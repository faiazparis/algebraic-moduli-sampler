"""JSON input/output utilities for the moduli sampler."""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


def load_json(file_path: Union[str, Path]) -> Union[Dict[str, Any], List[Any]]:
    """Load JSON data from a file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in file {file_path}: {e.msg}",
            e.doc,
            e.pos,
        )


def save_json(
    data: Union[Dict[str, Any], List[Any]],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to output file
        indent: JSON indentation
        ensure_ascii: Whether to escape non-ASCII characters
        
    Raises:
        PermissionError: If file cannot be written
    """
    file_path = Path(file_path)
    
    # Ensure output directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
    except PermissionError as e:
        raise PermissionError(f"Cannot write to file {file_path}: {e}")


def load_params(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load and validate parameter file.
    
    This is a convenience function that loads JSON and ensures
    it's a dictionary (parameters should be objects, not arrays).
    
    Args:
        file_path: Path to parameter file
        
    Returns:
        Parameter dictionary
        
    Raises:
        ValueError: If loaded data is not a dictionary
    """
    data = load_json(file_path)
    
    if not isinstance(data, dict):
        raise ValueError(f"Parameter file must contain a JSON object, got {type(data)}")
    
    return data


def save_results(
    results: Dict[str, Any],
    output_dir: Union[str, Path],
    base_name: str = "results",
) -> Path:
    """Save results to output directory with timestamp.
    
    Args:
        results: Results dictionary to save
        output_dir: Output directory
        base_name: Base name for output files
        
    Returns:
        Path to saved results file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create results file
    results_file = output_dir / f"{base_name}.json"
    save_json(results, results_file)
    
    return results_file


def load_family_data(family_file: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load family data from a file.
    
    This is a convenience function that loads JSON and ensures
    it's a list of curve data dictionaries.
    
    Args:
        family_file: Path to family data file
        
    Returns:
        List of curve data dictionaries
        
    Raises:
        ValueError: If loaded data is not a list
    """
    data = load_json(family_file)
    
    if not isinstance(data, list):
        raise ValueError(f"Family file must contain a JSON array, got {type(data)}")
    
    return data
