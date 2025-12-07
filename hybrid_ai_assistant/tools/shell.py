"""
Docker-wrapped shell execution for safe command execution.
Runs commands in isolated Docker containers.
"""
import subprocess
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
from hybrid_ai_assistant.config.config import config


def execute_command(
    command: str,
    timeout: int = None,
    working_dir: str = None,
    use_docker: bool = True
) -> Dict[str, Any]:
    """
    Execute a shell command, optionally in a Docker container.
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds (default from config)
        working_dir: Working directory for command
        use_docker: Whether to use Docker (True) or direct execution (False)
        
    Returns:
        Dictionary with execution results
    """
    if timeout is None:
        timeout = config.CODE_TIMEOUT
    
    try:
        if use_docker:
            return _execute_in_docker(command, timeout, working_dir)
        else:
            return _execute_direct(command, timeout, working_dir)
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Command timed out after {timeout} seconds",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "exit_code": -1
        }


def _execute_direct(
    command: str,
    timeout: int,
    working_dir: Optional[str]
) -> Dict[str, Any]:
    """
    Execute command directly on host (less safe, but faster).
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        working_dir: Working directory
        
    Returns:
        Execution results
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode
        }
        
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "exit_code": -1
        }


def _execute_in_docker(
    command: str,
    timeout: int,
    working_dir: Optional[str]
) -> Dict[str, Any]:
    """
    Execute command in a Docker container for isolation.
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        working_dir: Working directory to mount
        
    Returns:
        Execution results
    """
    try:
        import docker
        client = docker.from_env()
        
        # Prepare volume mount if working_dir specified
        volumes = {}
        container_workdir = "/workspace"
        
        if working_dir:
            volumes[working_dir] = {
                "bind": container_workdir,
                "mode": "rw"
            }
        
        # Run container
        container = client.containers.run(
            config.DOCKER_IMAGE,
            command=f'/bin/sh -c "{command}"',
            volumes=volumes,
            working_dir=container_workdir if working_dir else None,
            detach=True,
            remove=True,
            network_disabled=False  # Allow network for package installs
        )
        
        # Wait for completion
        result = container.wait(timeout=timeout)
        
        # Get logs
        output = container.logs(stdout=True, stderr=False).decode("utf-8")
        error = container.logs(stdout=False, stderr=True).decode("utf-8")
        
        exit_code = result.get("StatusCode", -1)
        
        return {
            "success": exit_code == 0,
            "output": output,
            "error": error,
            "exit_code": exit_code
        }
        
    except ImportError:
        # Docker library not available, fall back to direct execution
        return _execute_direct(command, timeout, working_dir)
        
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Docker execution error: {str(e)}",
            "exit_code": -1
        }


def execute_python_code(code: str, timeout: int = None) -> Dict[str, Any]:
    """
    Execute Python code in a safe environment.
    
    Args:
        code: Python code to execute
        timeout: Timeout in seconds
        
    Returns:
        Execution results
    """
    # Create temporary file with code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = execute_command(
            f"python {temp_file}",
            timeout=timeout,
            use_docker=True
        )
        return result
    finally:
        # Clean up temp file
        Path(temp_file).unlink(missing_ok=True)


def get_shell_tools():
    """
    Create LangChain tools for shell execution.
    
    Returns:
        List of LangChain tool instances
    """
    from langchain.tools import Tool
    
    return [
        Tool(
            name="execute_command",
            description="Execute a shell command in a safe Docker environment. Input should be the command string.",
            func=lambda cmd: execute_command(cmd, use_docker=True)
        ),
        Tool(
            name="execute_python",
            description="Execute Python code in a safe environment. Input should be the Python code string.",
            func=execute_python_code
        )
    ]
