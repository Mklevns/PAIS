from langchain.tools import tool
from hybrid_ai_assistant.utils.docker_utils import exec_in_container
import os

# We need a way to pass the container ID to these tools.
# In a real LangGraph, we might pass config or bind the tool to the state.
# For now, I'll rely on a global or context, or assume the LLM passes it?
# The user's code just says 'exec_in_container("ls " + path)'.
# 'exec_in_container' signature in user code: (container_id, cmd).
# The user's specific file_ops snippet missed the container_id argument or assumed a global/default.
# I will implement a helper that tries to get a container or uses a stored one.
# For this 'how-to' implementation, I will assume a single container context for simplicity 
# OR use a placeholder ID if not provided. 
# Better: Make these functions accept container_id if possible, or bind them.
# However, standard tools usually take a single input (str).
# I'll create a class or function builder.

# Actually, the user's snippet for file_ops.py:
# @tool
# def list_dir(path: str):
#    return exec_in_container("ls " + path)
# AND
# exec_in_container signature: (container_id, cmd)
# There is a mismatch. I will fix it by making a singleton or simple global for the active container 
# since we are running one flow.

_ACTIVE_CONTAINER_ID = None

def set_active_container(container_id):
    global _ACTIVE_CONTAINER_ID
    _ACTIVE_CONTAINER_ID = container_id

def get_active_container():
    return _ACTIVE_CONTAINER_ID

@tool
def list_dir(path: str):
    """List contents of a directory in the container."""
    cid = get_active_container()
    if not cid: return "Error: No active container"
    return exec_in_container(cid, "ls " + path)

@tool
def read_file(path: str):
    """Read a file from the container."""
    cid = get_active_container()
    if not cid: return "Error: No active container"
    return exec_in_container(cid, "cat " + path)

@tool
def write_file(path: str, content: str):
    """Write content to a file in the container."""
    cid = get_active_container()
    if not cid: return "Error: No active container"
    # Basic write - in prod use base64 or safe handling
    # Using echo for simplicity as per user snippet
    return exec_in_container(cid, f"echo '{content}' > {path}")

@tool
def mkdir(path: str):
    """Create a directory in the container."""
    cid = get_active_container()
    if not cid: return "Error: No active container"
    return exec_in_container(cid, "mkdir -p " + path)
