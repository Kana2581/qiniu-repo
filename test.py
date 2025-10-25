def run_command(command: str, shell_type: str = None, max_output: int = 1000, base_dir=r"E:\music_test"):
    """
    执行系统命令（cmd / powershell / shell）。
    Args:
        command (str): 要执行的命令。
        shell_type (str): Windows: "cmd" 或 "powershell"。
        max_output (int): 输出截断长度。
    """
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


# ✅ 示例
print(run_command("docker ps", "cmd"))


# ✅ 示例



print(run_command("dir","cmd"))