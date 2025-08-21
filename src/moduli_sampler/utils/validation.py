"""File and directory validation utilities."""

from pathlib import Path
from typing import Union


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """Validate that a file path exists and is a file.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    return path


def validate_output_dir(output_dir: Union[str, Path], create: bool = True) -> Path:
    """Validate and optionally create an output directory.
    
    Args:
        output_dir: Directory path to validate
        create: Whether to create the directory if it doesn't exist
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If path exists but is not a directory
        PermissionError: If directory cannot be created
    """
    path = Path(output_dir)
    
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"Path exists but is not a directory: {path}")
    elif create:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot create directory {path}: {e}")
    
    return path


def ensure_file_extension(file_path: Union[str, Path], extension: str) -> Path:
    """Ensure a file path has the specified extension.
    
    Args:
        file_path: File path to check
        extension: Required extension (with or without dot)
        
    Returns:
        Path with correct extension
    """
    path = Path(file_path)
    
    # Normalize extension
    if not extension.startswith("."):
        extension = "." + extension
    
    # Add extension if not present
    if path.suffix != extension:
        path = path.with_suffix(extension)
    
    return path


def validate_json_file(file_path: Union[str, Path]) -> Path:
    """Validate that a file path exists and has .json extension.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file doesn't have .json extension
    """
    path = validate_file_path(file_path)
    
    if path.suffix.lower() != ".json":
        raise ValueError(f"File must have .json extension: {path}")
    
    return path
