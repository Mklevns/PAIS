"""
Repository skeleton generator for context management.
Creates compressed representations of codebases for AI context.
"""
from pathlib import Path
from typing import List, Dict, Any, Set
import os


# Common directories and files to ignore
DEFAULT_IGNORE = {
    ".git", ".gitignore", "__pycache__", "node_modules", "venv", ".venv",
    "env", ".env", "dist", "build", ".pytest_cache", ".mypy_cache",
    ".coverage", "*.pyc", "*.pyo", "*.egg-info", ".DS_Store"
}


class RepoMap:
    """
    Generates a compressed skeleton representation of a repository.
    Useful for providing codebase context to AI models.
    """
    
    def __init__(
        self,
        root_path: str,
        ignore_patterns: Set[str] = None,
        max_depth: int = 5
    ):
        """
        Initialize repository mapper.
        
        Args:
            root_path: Root directory of the repository
            ignore_patterns: Additional patterns to ignore
            max_depth: Maximum directory depth to traverse
        """
        self.root_path = Path(root_path)
        self.ignore_patterns = DEFAULT_IGNORE | (ignore_patterns or set())
        self.max_depth = max_depth
    
    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored.
        
        Args:
            path: Path to check
            
        Returns:
            True if should be ignored, False otherwise
        """
        name = path.name
        
        # Check exact matches
        if name in self.ignore_patterns:
            return True
        
        # Check pattern matches (simple wildcard)
        for pattern in self.ignore_patterns:
            if "*" in pattern:
                # Simple wildcard matching
                prefix = pattern.split("*")[0]
                suffix = pattern.split("*")[-1]
                if name.startswith(prefix) and name.endswith(suffix):
                    return True
        
        return False
    
    def generate_tree(self, include_files: bool = True) -> str:
        """
        Generate a tree-style representation of the repository.
        
        Args:
            include_files: Whether to include files in the tree
            
        Returns:
            Tree representation as string
        """
        lines = [str(self.root_path.name) + "/"]
        
        def walk_dir(path: Path, prefix: str = "", depth: int = 0):
            if depth >= self.max_depth:
                return
            
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                items = [item for item in items if not self.should_ignore(item)]
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    
                    if item.is_dir():
                        connector = "└── " if is_last else "├── "
                        lines.append(f"{prefix}{connector}{item.name}/")
                        
                        extension = "    " if is_last else "│   "
                        walk_dir(item, prefix + extension, depth + 1)
                    
                    elif include_files:
                        connector = "└── " if is_last else "├── "
                        lines.append(f"{prefix}{connector}{item.name}")
            
            except PermissionError:
                pass
        
        walk_dir(self.root_path)
        return "\n".join(lines)
    
    def generate_file_list(
        self,
        extensions: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a list of files with metadata.
        
        Args:
            extensions: Filter by file extensions (e.g., ['.py', '.js'])
            
        Returns:
            List of file information dictionaries
        """
        files = []
        
        def walk_dir(path: Path, depth: int = 0):
            if depth >= self.max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if self.should_ignore(item):
                        continue
                    
                    if item.is_dir():
                        walk_dir(item, depth + 1)
                    
                    elif item.is_file():
                        # Filter by extension if specified
                        if extensions and item.suffix not in extensions:
                            continue
                        
                        try:
                            size = item.stat().st_size
                            relative_path = item.relative_to(self.root_path)
                            
                            files.append({
                                "path": str(relative_path),
                                "name": item.name,
                                "size": size,
                                "extension": item.suffix
                            })
                        except:
                            pass
            
            except PermissionError:
                pass
        
        walk_dir(self.root_path)
        return sorted(files, key=lambda x: x["path"])
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the repository structure.
        
        Returns:
            Summary dictionary with statistics
        """
        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "file_types": {},
            "total_size": 0
        }
        
        def walk_dir(path: Path):
            try:
                for item in path.iterdir():
                    if self.should_ignore(item):
                        continue
                    
                    if item.is_dir():
                        stats["total_dirs"] += 1
                        walk_dir(item)
                    
                    elif item.is_file():
                        stats["total_files"] += 1
                        ext = item.suffix or "no_extension"
                        stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                        
                        try:
                            stats["total_size"] += item.stat().st_size
                        except:
                            pass
            
            except PermissionError:
                pass
        
        walk_dir(self.root_path)
        return stats
    
    def generate_skeleton(
        self,
        include_tree: bool = True,
        include_summary: bool = True
    ) -> str:
        """
        Generate a complete skeleton representation.
        
        Args:
            include_tree: Include directory tree
            include_summary: Include repository summary
            
        Returns:
            Skeleton representation as string
        """
        parts = []
        
        if include_summary:
            summary = self.generate_summary()
            parts.append("Repository Summary:")
            parts.append(f"  Total Files: {summary['total_files']}")
            parts.append(f"  Total Directories: {summary['total_dirs']}")
            parts.append(f"  Total Size: {summary['total_size']:,} bytes")
            parts.append("\n  File Types:")
            for ext, count in sorted(summary["file_types"].items(), key=lambda x: -x[1]):
                parts.append(f"    {ext}: {count}")
            parts.append("")
        
        if include_tree:
            parts.append("Directory Tree:")
            parts.append(self.generate_tree())
        
        return "\n".join(parts)


def generate_repo_skeleton(
    repo_path: str,
    output_file: str = None
) -> str:
    """
    Generate a repository skeleton.
    
    Args:
        repo_path: Path to repository
        output_file: Optional file to write skeleton to
        
    Returns:
        Skeleton representation as string
    """
    mapper = RepoMap(repo_path)
    skeleton = mapper.generate_skeleton()
    
    if output_file:
        with open(output_file, "w") as f:
            f.write(skeleton)
    
    return skeleton
