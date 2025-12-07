"""
Sandboxed file operations tools.
Provides safe file system operations with path validation.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


# Default sandbox directory (can be configured)
SANDBOX_DIR = Path("/tmp/hybrid_ai_sandbox")
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


def validate_path(path: str) -> Path:
    """
    Validate that path is within sandbox directory.
    
    Args:
        path: File path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If path is outside sandbox
    """
    full_path = (SANDBOX_DIR / path).resolve()
    
    # Ensure path is within sandbox
    if not str(full_path).startswith(str(SANDBOX_DIR)):
        raise ValueError(f"Path outside sandbox: {path}")
    
    return full_path


def list_directory(path: str = ".") -> List[Dict[str, Any]]:
    """
    List contents of a directory within sandbox.
    
    Args:
        path: Directory path (relative to sandbox)
        
    Returns:
        List of files and directories with metadata
    """
    try:
        dir_path = validate_path(path)
        
        if not dir_path.exists():
            return []
        
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {path}")
        
        items = []
        for item in dir_path.iterdir():
            items.append({
                "name": item.name,
                "path": str(item.relative_to(SANDBOX_DIR)),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0
            })
        
        return sorted(items, key=lambda x: (x["type"], x["name"]))
        
    except Exception as e:
        return [{"error": str(e)}]


def read_file(path: str, max_size: int = 1024 * 1024) -> str:
    """
    Read contents of a file within sandbox.
    
    Args:
        path: File path (relative to sandbox)
        max_size: Maximum file size to read (bytes)
        
    Returns:
        File contents as string
    """
    try:
        file_path = validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        if file_path.stat().st_size > max_size:
            raise ValueError(f"File too large: {path} ({file_path.stat().st_size} bytes)")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file within sandbox.
    Creates parent directories if needed.
    
    Args:
        path: File path (relative to sandbox)
        content: Content to write
        
    Returns:
        Result dictionary with status
    """
    try:
        file_path = validate_path(path)
        
        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {
            "success": True,
            "path": str(file_path.relative_to(SANDBOX_DIR)),
            "size": len(content)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def mkdir(path: str) -> Dict[str, Any]:
    """
    Create a directory within sandbox.
    
    Args:
        path: Directory path (relative to sandbox)
        
    Returns:
        Result dictionary with status
    """
    try:
        dir_path = validate_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(dir_path.relative_to(SANDBOX_DIR))
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_file_tools():
    """
    Create LangChain tools for file operations.
    
    Returns:
        List of LangChain tool instances
    """
    from langchain.tools import Tool
    
    return [
        Tool(
            name="list_directory",
            description="List contents of a directory. Input should be a directory path.",
            func=list_directory
        ),
        Tool(
            name="read_file",
            description="Read contents of a file. Input should be a file path.",
            func=read_file
        ),
        Tool(
            name="write_file",
            description="Write content to a file. Input should be 'path|content' separated by pipe.",
            func=lambda input_str: write_file(*input_str.split("|", 1))
        ),
        Tool(
            name="create_directory",
            description="Create a directory. Input should be a directory path.",
            func=mkdir
        )
    ]
