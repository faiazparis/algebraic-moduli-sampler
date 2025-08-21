"""Seed management and RNG setup utilities.

This module provides deterministic random number generation
for reproducible sampling across different platforms.
"""

import os
import platform
import sys
from typing import Optional

import numpy as np


def setup_rng(seed: int) -> np.random.RandomState:
    """Setup deterministic random number generator.
    
    This function ensures reproducible random number generation
    across different platforms and Python versions.
    
    Args:
        seed: Integer seed for the RNG
        
    Returns:
        Configured numpy RandomState object
    """
    # Set numpy seed for global numpy functions
    np.random.seed(seed)
    
    # Create and return a RandomState object for local use
    rng = np.random.RandomState(seed)
    
    # Set environment variables for additional reproducibility
    os.environ["PYTHONHASHSEED"] = str(seed)
    
    return rng


def get_seed_info(seed: int) -> dict:
    """Get information about the current seed and environment.
    
    Args:
        seed: The seed value being used
        
    Returns:
        Dictionary with seed and environment information
    """
    return {
        "seed": seed,
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def generate_deterministic_sequence(seed: int, length: int, min_val: int = 0, max_val: int = 100) -> list:
    """Generate a deterministic sequence of integers.
    
    This function is useful for testing and ensuring reproducible
    behavior across different runs.
    
    Args:
        seed: Seed for the RNG
        length: Length of the sequence to generate
        min_val: Minimum value (inclusive)
        max_val: Maximum value (exclusive)
        
    Returns:
        List of deterministic integers
    """
    rng = setup_rng(seed)
    return rng.randint(min_val, max_val, size=length).tolist()


def verify_seed_reproducibility(seed: int, n_samples: int = 10) -> bool:
    """Verify that a seed produces reproducible results.
    
    This function runs a simple test to ensure that the same
    seed produces the same sequence of random numbers.
    
    Args:
        seed: Seed to test
        n_samples: Number of samples to generate for testing
        
    Returns:
        True if reproducible, False otherwise
    """
    # Generate sequence twice with the same seed
    seq1 = generate_deterministic_sequence(seed, n_samples)
    seq2 = generate_deterministic_sequence(seed, n_samples)
    
    return seq1 == seq2
