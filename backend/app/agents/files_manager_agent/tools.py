# 文件根目录（可修改）
import shutil
from pathlib import Path
from typing import Dict

from langchain.tools import ToolRuntime
from langchain_core.tools import tool
import os
import subprocess
import platform

from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState

from backend.app.agents.files_manager_agent.state import FileAgentState, ToolState


def safe_path(base_dir: str, rel_path: str) -> Path:
    """
    确保访问路径安全（限制在 base_dir 内）。

    Args:
        base_dir (str): 基准目录。
        rel_path (str): 相对路径。

    Raises:
        ValueError: 当路径超出 base_dir 时。
        FileNotFoundError: 当 base_dir 不存在且无法创建时。

    Returns:
        Path: 安全的绝对路径对象。
    """
    base_path = Path(base_dir).resolve()

    # 检查 base_dir 是否存在，如果不存在尝试创建
    try:
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
        elif not base_path.is_dir():
            raise ValueError(f"Base directory '{base_dir}' 不是一个合法目录。")
    except Exception as e:
        raise FileNotFoundError(f"无法访问或创建目录 '{base_dir}'：{e}")

    # 构造目标路径并解析为绝对路径
    target_path = (base_path / rel_path).resolve()

    # 检查路径是否超出 base_dir 边界
    if base_path not in target_path.parents and target_path != base_path:
        raise ValueError(f"非法访问：'{target_path}' 不在 '{base_path}' 目录下。")

    return target_path


@tool
def show_tree(runtime: ToolRuntime,path: str="",include_dirs:bool=True, recursive:bool=True, limit:int=60):
    """
    以树形结构显示目录内容，超过阈值自动停止。
    Args:
        path (str): 相对目录路径，默认当前目录 。
        include_dirs (bool): 是否显示目录，默认 True。
        recursive (bool): 是否递归，默认 True。
        limit (int): 最大节点数量阈值，默认 60。
    """
    base_dir = runtime.state.get("base_file_path")
    path = safe_path(base_dir,path)
    print(path)
    base = Path(path).resolve()
    if not base.exists():
        return {"error": "Source path not found."}

    tree_lines = []
    count = 0

    def _tree(p: Path, prefix=""):
        nonlocal count
        if count >= limit:
            return

        children = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for idx, child in enumerate(children):
            if count >= limit:
                break

            connector = "└── " if idx == len(children) - 1 else "├── "
            line = f"{prefix}{connector}{child.name}/" if child.is_dir() else f"{prefix}{connector}{child.name}"
            if child.is_dir() or include_dirs:
                tree_lines.append(line)
                count += 1

            if child.is_dir() and recursive:
                extension = "    " if idx == len(children) - 1 else "│   "
                _tree(child, prefix + extension)

    _tree(base)

    result = {
        "base path": base.name,  # 当前展示的目录名
        "file tree": "\n".join(tree_lines)
    }
    if count >= limit:
        result["warning"] = f"文件过多（>{limit}），已提前停止显示。"

    return result


@tool
def read_file(runtime: ToolRuntime,filename: str, max_length: int = 1000):
    """
    读取文件内容，非文本文件或过大内容会有提示。
    Args:
        filename (str): 文件名（相对 BASE_DIR）。
        max_length (int): 最大返回字符数，默认1000。
    """
    base_dir = runtime.state.get("base_file_path")
    path = safe_path(base_dir,filename)
    if not path.exists():
        return {"error": "Source path not found."}
    if not path.is_file():
        return {"error": "指定路径不是文件。"}

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return {"error": "无法读取，可能不是文本文件。"}

    result = {"filename": filename}
    if len(content) > max_length:
        result["content"] = content[:max_length]
        result["warning"] = f"文件内容过长（>{max_length}字符），已截断显示。"
    else:
        result["content"] = content

    return result


@tool
def write_file(runtime: ToolRuntime,filename: str, content: str):
    """
    写入内容到文件（覆盖）。
    Args:
        filename (str): 文件名（相对 BASE_DIR）。
        content (str): 内容。
    Returns:
        dict: {"message": "File written."}
    """
    base_dir = runtime.state.get("base_file_path")
    path = safe_path(base_dir,filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"message": f"File '{filename}' written."}


@tool
def delete_file(runtime: ToolRuntime,filename: str):
    """
    删除文件。
    Args:
        filename (str): 文件名（相对 BASE_DIR）。
    Raises:
        FileNotFoundError: 文件不存在。
    Returns:
        dict: {"message": "File deleted."}
    """
    base_dir = runtime.state.get("base_file_path")
    path = safe_path(base_dir,filename)
    if not path.exists():
        return {"error": f"Source path not found."}
    path.unlink()
    return {"message": f"File '{filename}' deleted."}


@tool
def create_dir(runtime: ToolRuntime,dirname: str):
    """
    创建新目录（递归）。
    Args:
        dirname (str): 目录名（相对 BASE_DIR）。
    Returns:
        dict: {"message": "Directory created."}
    """
    base_dir = runtime.state.get("base_file_path")
    path = safe_path(base_dir,dirname)

    path.mkdir(parents=True, exist_ok=True)
    return {"message": f"Directory '{dirname}' created."}


@tool
def rename_path(runtime: ToolRuntime,old_name: str, new_name: str):
    """
    重命名文件或目录。
    Args:
        old_name (str): 原名（相对 BASE_DIR）。
        new_name (str): 新名（相对 BASE_DIR）。
    Returns:
        dict: {"message": "Renamed 'a' -> 'b'."}
    """
    base_dir = runtime.state.get("base_file_path")

    old = safe_path(base_dir,old_name)
    new = safe_path(base_dir,new_name)
    if not old.exists():
        return {"error": f"Source path not found."}
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
    return {"message": f"Renamed '{old_name}' -> '{new_name}'."}


@tool
def copy_path(runtime: ToolRuntime,src: str, dest: str):
    """
    复制文件或目录。
    Args:
        src (str): 源路径（相对 BASE_DIR）。
        dest (str): 目标路径（相对 BASE_DIR）。
    Raises:
        FileNotFoundError: 源不存在。
    Returns:
        dict: {"message": "Copied 'src' -> 'dest'."}
    """
    base_dir = runtime.state.get("base_file_path")
    s = safe_path(base_dir,src)
    d = safe_path(base_dir,dest)
    if not s.exists():
        raise FileNotFoundError("Source path not found.")
    d.parent.mkdir(parents=True, exist_ok=True)
    if s.is_dir():
        shutil.copytree(s, d, dirs_exist_ok=True)
    else:
        shutil.copy2(s, d)
    return {"message": f"Copied '{src}' -> '{dest}'."}


@tool
def move_path(runtime: ToolRuntime,src: str, dest: str):
    """
    移动（剪切）文件或目录。
    Args:
        src (str): 源路径（相对 BASE_DIR）。
        dest (str): 目标路径（相对 BASE_DIR）。
    Raises:
        FileNotFoundError: 源不存在。
    Returns:
        dict: {"message": "Moved 'src' -> 'dest'."}
    """
    base_dir = runtime.state.get("base_file_path")
    s = safe_path(base_dir,src)
    d = safe_path(base_dir,dest)
    if not s.exists():
        raise FileNotFoundError("Source path not found.")
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))
    return {"message": f"Moved '{src}' -> '{dest}'."}


@tool
def open_file(runtime: ToolRuntime,filepath: str):
    """
    使用系统默认程序打开文件或目录。
    Args:
        filepath (str): 相对 BASE_DIR 的路径。
    Returns:
        dict: {"message": "✅ Opened: path"} 或错误信息。
    """
    base_dir = runtime.state.get("base_file_path")
    path = safe_path(base_dir,filepath)
    if not path.exists():
        return {"message": f"❌ File not found: {filepath}"}
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.run(["open", path])
        elif system == "Linux":
            subprocess.run(["xdg-open", path])
        else:
            return {"message": f"⚠️ Unsupported OS: {system}"}
        return {"message": f"✅ Opened: {filepath}"}
    except Exception as e:
        return {"message": f"⚠️ Error: {e}"}
@tool
def run_command(runtime: ToolRuntime,command: str, shell_type: str = None, max_output: int = 1000):
    """
    执行系统命令（cmd / powershell / shell）。
    Args:
        command (str): 要执行的命令。
        shell_type (str): 可选，Windows: "cmd" 或 "powershell"，其他系统忽略。
        max_output (int): 输出截断长度，默认1000字符。
    """
    import subprocess, platform, os
    base_dir = runtime.state.get("base_file_path")

    import subprocess, platform

    system = platform.system()
    shell_cmd = command

    if system == "Windows":
        if shell_type == "powershell":
            # ✅ PowerShell 默认支持 UTF-8，可强制使用 UTF-8 输出
            shell_cmd = ["powershell", "-NoProfile", "-Command",
                         f"$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}"]
        else:  # 默认 cmd
            # ✅ CMD 强制以 UTF-8 执行命令
            shell_cmd = ["cmd", "/c", f"chcp 65001 >nul && {command}"]

    try:
        result = subprocess.run(
            shell_cmd,
            cwd=base_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",  # ✅ 强制解码为 UTF-8
            errors="replace",  # ✅ 避免乱码崩溃，用 � 替代非法字符
            shell=(system != "Windows"),
            timeout=60
        )

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        warning = None

        if len(stdout) > max_output:
            stdout = stdout[:max_output]
            warning = f"输出过长（>{max_output}字符），已截断显示。"
        if len(stderr) > max_output:
            stderr = stderr[:max_output]
            warning = (warning + " " if warning else "") + f"错误输出过长（>{max_output}字符），已截断显示。"

        res = {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode
        }
        if warning:
            res["warning"] = warning
        return res

    except subprocess.TimeoutExpired:
        return {"error": "命令执行超时。"}
    except Exception as e:
        return {"error": f"命令执行失败: {e}"}




tools_list = [write_file, read_file, show_tree, delete_file,open_file,rename_path,copy_path,move_path,run_command,create_dir]