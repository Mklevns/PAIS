from langchain.tools import tool
from hybrid_ai_assistant.utils.docker_utils import exec_in_container

@tool
def list_dir(path: str, container_id: str):
    """List contents of a directory in the specific container."""
    if not container_id: return "Error: No container ID"
    return exec_in_container(container_id, "ls " + path)

@tool
def read_file(path: str, container_id: str):
    """Read a file in the specific container."""
    if not container_id: return "Error: No container ID"
    return exec_in_container(container_id, "cat " + path)

@tool
def write_file(path: str, content: str, container_id: str):
    """Write to a file in the specific container."""
    if not container_id: return "Error: No container ID"
    # Gate for overwrite
    # if file_exists(path, container_id):
    #     pass
    return exec_in_container(container_id, f"echo '{content}' > {path}")

@tool
def mkdir(path: str, container_id: str):
    """Create a directory in the specific container."""
    if not container_id: return "Error: No container ID"
    return exec_in_container(container_id, "mkdir -p " + path)
