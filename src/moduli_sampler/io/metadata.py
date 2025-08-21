"""Metadata capture and saving utilities.

This module handles capturing and saving metadata about runs,
    including environment information, git status, and parameters.
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def get_git_info() -> Dict[str, str]:
    """Get git repository information.
    
    Returns:
        Dictionary with git information or empty dict if not in git repo
    """
    try:
        # Get git root directory
        git_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        # Get current commit hash
        commit_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        # Get current branch
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        # Check if working directory is clean
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        is_clean = len(status) == 0
        
        return {
            "git_root": git_root,
            "commit_hash": commit_hash,
            "branch": branch,
            "working_directory_clean": is_clean,
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in git repo or git not available
        return {}


def get_environment_info() -> Dict[str, str]:
    """Get environment information.
    
    Returns:
        Dictionary with environment information
    """
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "machine": platform.machine(),
        "processor": platform.processor(),
        "numpy_version": np.__version__,
        "working_directory": str(Path.cwd()),
        "environment_variables": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", ""),
        }
    }


def get_timestamp() -> str:
    """Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def compute_params_hash(params: Dict[str, Any]) -> str:
    """Compute a hash of parameters for reproducibility.
    
    Args:
        params: Parameter dictionary
        
    Returns:
        SHA256 hash of parameters
    """
    # Convert to sorted JSON string for consistent hashing
    params_str = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(params_str.encode()).hexdigest()


def get_metadata(
    command: str,
    params_file: Optional[str] = None,
    seed: Optional[int] = None,
    n_samples: Optional[int] = None,
    family_type: Optional[str] = None,
    sampling_strategy: Optional[str] = None,
    invariants_computed: Optional[list] = None,
    **additional_info: Any,
) -> Dict[str, Any]:
    """Generate comprehensive metadata for a run.
    
    Args:
        command: CLI command that was run
        params_file: Path to parameter file
        seed: Random seed used
        n_samples: Number of samples generated
        family_type: Type of curve family
        sampling_strategy: Sampling strategy used
        invariants_computed: List of computed invariants
        **additional_info: Additional metadata to include
        
    Returns:
        Dictionary with complete metadata
    """
    metadata = {
        "timestamp": get_timestamp(),
        "command": command,
        "environment": get_environment_info(),
        "git_info": get_git_info(),
    }
    
    # Add command-specific information
    if params_file:
        metadata["params_file"] = params_file
        # Try to load and hash parameters
        try:
            with open(params_file, "r", encoding="utf-8") as f:
                params = json.load(f)
            metadata["params_hash"] = compute_params_hash(params)
        except Exception:
            metadata["params_hash"] = "error_loading_params"
    
    if seed is not None:
        metadata["seed"] = seed
    
    if n_samples is not None:
        metadata["n_samples"] = n_samples
    
    if family_type:
        metadata["family_type"] = family_type
    
    if sampling_strategy:
        metadata["sampling_strategy"] = sampling_strategy
    
    if invariants_computed:
        metadata["invariants_computed"] = invariants_computed
    
    # Add any additional information
    metadata.update(additional_info)
    
    return metadata


def save_metadata(metadata: Dict[str, Any], output_file: Path) -> None:
    """Save metadata to a JSON file.
    
    Args:
        metadata: Metadata dictionary to save
        output_file: Path to output file
    """
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save metadata
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Also save a summary file
    summary_file = output_file.parent / "metadata_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("Algebraic Moduli Sampler - Run Metadata\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Timestamp: {metadata.get('timestamp', 'Unknown')}\n")
        f.write(f"Command: {metadata.get('command', 'Unknown')}\n")
        
        if "family_type" in metadata:
            f.write(f"Family Type: {metadata['family_type']}\n")
        
        if "seed" in metadata:
            f.write(f"Seed: {metadata['seed']}\n")
        
        if "n_samples" in metadata:
            f.write(f"Samples: {metadata['n_samples']}\n")
        
        if "sampling_strategy" in metadata:
            f.write(f"Strategy: {metadata['sampling_strategy']}\n")
        
        if "git_info" in metadata and metadata["git_info"]:
            f.write(f"Git Commit: {metadata['git_info'].get('commit_hash', 'Unknown')[:8]}\n")
            f.write(f"Git Branch: {metadata['git_info'].get('branch', 'Unknown')}\n")
            f.write(f"Working Directory Clean: {metadata['git_info'].get('working_directory_clean', 'Unknown')}\n")
        
        f.write(f"\nEnvironment:\n")
        env = metadata.get("environment", {})
        f.write(f"  Python: {env.get('python_version', 'Unknown')}\n")
        f.write(f"  Platform: {env.get('platform', 'Unknown')}\n")
        f.write(f"  NumPy: {env.get('numpy_version', 'Unknown')}\n")
        
        if "params_hash" in metadata:
            f.write(f"\nParameters Hash: {metadata['params_hash']}\n")
