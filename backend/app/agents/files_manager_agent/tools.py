# 文件根目录（可修改）
import shutil
from pathlib import Path

from langchain_core.tools import tool
import os
import subprocess
import platform
BASE_DIR = Path("E:\\music_test")
BASE_DIR.mkdir(exist_ok=True)

# 获取文件列表
def safe_path(rel_path: str) -> Path:
    """
    确保访问路径安全（限制在 BASE_DIR 内）。
    Args:
        rel_path (str): 相对路径。
    Raises:
        ValueError: 当路径超出 BASE_DIR 时。
    Returns:
        Path: 安全的绝对路径对象。
    """
    p = (BASE_DIR / rel_path).resolve()
    if not str(p).startswith(str(BASE_DIR)):
        raise ValueError("Unsafe path access detected.")
    return p


@tool
def show_tree(path: str = ".", include_dirs: bool = True, recursive: bool = True, limit: int = 60):
    """
    以树形结构显示目录内容，超过阈值自动停止。
    Args:
        path (str): 相对目录路径，默认当前目录。
        include_dirs (bool): 是否显示目录，默认 True。
        recursive (bool): 是否递归，默认 True。
        limit (int): 最大节点数量阈值，默认 60。
    """
    base = safe_path(path)
    if not base.exists():
        return {"error": "Source path not found."}

    tree_lines = []
    count = 0

    def _tree(p: Path, prefix=""):
        nonlocal count
        if count >= limit:
            return
        tree_lines.append(f"{prefix}{p.name}/" if p.is_dir() else f"{prefix}{p.name}")
        count += 1
        if count >= limit:
            return
        if p.is_dir() and recursive:
            children = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for idx, child in enumerate(children):
                if count >= limit:
                    break
                branch = "└── " if idx == len(children) - 1 else "├── "
                extension = "    " if idx == len(children) - 1 else "│   "
                _tree(child, prefix + extension if child.is_dir() else prefix + branch)

    _tree(base, "")
    result = {"file tree": "\n".join(tree_lines)}
    if count >= limit:
        result["warning"] = f"文件过多（>{limit}），已提前停止显示。"
    return result


@tool
def read_file(filename: str, max_length: int = 1000):
    """
    读取文件内容，非文本文件或过大内容会有提示。
    Args:
        filename (str): 文件名（相对 BASE_DIR）。
        max_length (int): 最大返回字符数，默认1000。
    """
    path = safe_path(filename)
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
def write_file(filename: str, content: str):
    """
    写入内容到文件（覆盖）。
    Args:
        filename (str): 文件名（相对 BASE_DIR）。
        content (str): 内容。
    Returns:
        dict: {"message": "File written."}
    """
    path = safe_path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"message": f"File '{filename}' written."}


@tool
def delete_file(filename: str):
    """
    删除文件。
    Args:
        filename (str): 文件名（相对 BASE_DIR）。
    Raises:
        FileNotFoundError: 文件不存在。
    Returns:
        dict: {"message": "File deleted."}
    """
    path = safe_path(filename)
    if not path.exists():
        return {"error": f"Source path not found."}
    path.unlink()
    return {"message": f"File '{filename}' deleted."}


@tool
def create_dir(dirname: str):
    """
    创建新目录（递归）。
    Args:
        dirname (str): 目录名（相对 BASE_DIR）。
    Returns:
        dict: {"message": "Directory created."}
    """
    path = safe_path(dirname)
    path.mkdir(parents=True, exist_ok=True)
    return {"message": f"Directory '{dirname}' created."}


@tool
def rename_path(old_name: str, new_name: str):
    """
    重命名文件或目录。
    Args:
        old_name (str): 原名（相对 BASE_DIR）。
        new_name (str): 新名（相对 BASE_DIR）。
    Returns:
        dict: {"message": "Renamed 'a' -> 'b'."}
    """
    old = safe_path(old_name)
    new = safe_path(new_name)
    if not old.exists():
        return {"error": f"Source path not found."}
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
    return {"message": f"Renamed '{old_name}' -> '{new_name}'."}


@tool
def copy_path(src: str, dest: str):
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
    s = safe_path(src)
    d = safe_path(dest)
    if not s.exists():
        raise FileNotFoundError("Source path not found.")
    d.parent.mkdir(parents=True, exist_ok=True)
    if s.is_dir():
        shutil.copytree(s, d, dirs_exist_ok=True)
    else:
        shutil.copy2(s, d)
    return {"message": f"Copied '{src}' -> '{dest}'."}


@tool
def move_path(src: str, dest: str):
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
    s = safe_path(src)
    d = safe_path(dest)
    if not s.exists():
        raise FileNotFoundError("Source path not found.")
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))
    return {"message": f"Moved '{src}' -> '{dest}'."}


@tool
def open_file(filepath: str):
    """
    使用系统默认程序打开文件或目录。
    Args:
        filepath (str): 相对 BASE_DIR 的路径。
    Returns:
        dict: {"message": "✅ Opened: path"} 或错误信息。
    """
    path = safe_path(filepath)
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
def run_command(command: str, shell_type: str = None, max_output: int = 1000):
    """
    执行系统命令（cmd / powershell / shell）。
    Args:
        command (str): 要执行的命令。
        shell_type (str): 可选，Windows: "cmd" 或 "powershell"，其他系统忽略。
        max_output (int): 输出截断长度，默认1000字符。
    """
    system = platform.system()
    shell_cmd = command

    if system == "Windows":
        if shell_type == "powershell":
            shell_cmd = ["powershell", "-Command", command]
        else:  # 默认 cmd
            shell_cmd = ["cmd", "/c", command]
    # macOS/Linux 使用默认 shell，不需要修改

    try:
        result = subprocess.run(
            shell_cmd,
            capture_output=True,
            text=True,
            shell=(system != "Windows"),  # Windows 已经用 list
            timeout=60  # 防止无限阻塞
        )
        stdout = result.stdout
        stderr = result.stderr
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