"""
Docker container management utilities.
Handles container lifecycle for sandboxed execution.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from hybrid_ai_assistant.config.config import config


class DockerContainer:
    """
    Manages a Docker container for sandboxed execution.
    """
    
    def __init__(
        self,
        image: str = None,
        name: str = None,
        working_dir: str = "/workspace"
    ):
        """
        Initialize Docker container manager.
        
        Args:
            image: Docker image to use
            name: Container name
            working_dir: Working directory in container
        """
        self.image = image or config.DOCKER_IMAGE
        self.name = name
        self.working_dir = working_dir
        self.container = None
        self.client = None
        
    def start(self, volumes: Dict[str, Dict] = None) -> bool:
        """
        Start the Docker container.
        
        Args:
            volumes: Volume mounts for the container
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import docker
            self.client = docker.from_env()
            
            # Pull image if not available
            try:
                self.client.images.get(self.image)
            except:
                print(f"Pulling image {self.image}...")
                self.client.images.pull(self.image)
            
            # Create and start container
            self.container = self.client.containers.run(
                self.image,
                command="tail -f /dev/null",  # Keep container running
                name=self.name,
                volumes=volumes or {},
                working_dir=self.working_dir,
                detach=True,
                remove=False,  # Don't auto-remove so we can inspect
                network_disabled=False
            )
            
            return True
            
        except ImportError:
            print("Docker library not installed. Install with: pip install docker")
            return False
        except Exception as e:
            print(f"Error starting container: {e}")
            return False
    
    def exec_command(
        self,
        command: str,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Execute a command in the running container.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            
        Returns:
            Execution results
        """
        if not self.container:
            return {
                "success": False,
                "output": "",
                "error": "Container not started",
                "exit_code": -1
            }
        
        try:
            exec_result = self.container.exec_run(
                command,
                workdir=self.working_dir,
                demux=True
            )
            
            stdout, stderr = exec_result.output
            
            return {
                "success": exec_result.exit_code == 0,
                "output": stdout.decode("utf-8") if stdout else "",
                "error": stderr.decode("utf-8") if stderr else "",
                "exit_code": exec_result.exit_code
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
    
    def copy_to_container(self, src_path: str, dst_path: str) -> bool:
        """
        Copy a file or directory to the container.
        
        Args:
            src_path: Source path on host
            dst_path: Destination path in container
            
        Returns:
            True if successful, False otherwise
        """
        if not self.container:
            return False
        
        try:
            import tarfile
            import io
            
            # Create tar archive
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode="w") as tar:
                tar.add(src_path, arcname=Path(dst_path).name)
            
            tar_stream.seek(0)
            
            # Copy to container
            self.container.put_archive(
                path=str(Path(dst_path).parent),
                data=tar_stream
            )
            
            return True
            
        except Exception as e:
            print(f"Error copying to container: {e}")
            return False
    
    def copy_from_container(self, src_path: str, dst_path: str) -> bool:
        """
        Copy a file or directory from the container.
        
        Args:
            src_path: Source path in container
            dst_path: Destination path on host
            
        Returns:
            True if successful, False otherwise
        """
        if not self.container:
            return False
        
        try:
            import tarfile
            import io
            
            # Get archive from container
            bits, stat = self.container.get_archive(src_path)
            
            # Extract archive
            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)
            
            with tarfile.open(fileobj=tar_stream) as tar:
                tar.extractall(path=dst_path)
            
            return True
            
        except Exception as e:
            print(f"Error copying from container: {e}")
            return False
    
    def stop(self, remove: bool = True) -> bool:
        """
        Stop and optionally remove the container.
        
        Args:
            remove: Whether to remove container after stopping
            
        Returns:
            True if successful, False otherwise
        """
        if not self.container:
            return True
        
        try:
            self.container.stop()
            if remove:
                self.container.remove()
            return True
        except Exception as e:
            print(f"Error stopping container: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop(remove=True)


def get_container_for_execution(
    working_dir: str = None,
    name: str = None
) -> DockerContainer:
    """
    Get a Docker container configured for code execution.
    
    Args:
        working_dir: Working directory path on host
        name: Container name
        
    Returns:
        DockerContainer instance
    """
    volumes = {}
    
    if working_dir:
        volumes[working_dir] = {
            "bind": "/workspace",
            "mode": "rw"
        }
    
    container = DockerContainer(name=name)
    container.start(volumes=volumes)
    
    return container
