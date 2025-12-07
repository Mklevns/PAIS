import subprocess

def run_shell_command(command: str, cwd: str = None) -> str:
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)
