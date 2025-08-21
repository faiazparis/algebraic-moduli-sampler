"""Algebraic Moduli Sampler: Sheaf Cohomology on Curves.

A zero-cost, local-first, reproducible, and test-driven Python library
for sampling algebraic curve families and computing sheaf-cohomology-based invariants.

All mathematics is grounded in trusted references with explicit citations.
"""

__version__ = "0.1.0"
__author__ = "faiazparis"
__email__ = "faiazparis@gmail.com"

# Core modules
from .sampling import Sampler, SamplingParams
from .geometry import (
    P1Curve,
    EllipticCurve,
    HyperellipticCurve,
    PlaneCurve,
    LineBundle,
    compute_invariants,
)
from .io import load_params, save_results, save_metadata, get_metadata
from .utils import setup_rng

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "Sampler",
    "SamplingParams",
    "P1Curve",
    "EllipticCurve",
    "HyperellipticCurve",
    "PlaneCurve",
    "LineBundle",
    "compute_invariants",
    "load_params",
    "save_results",
    "save_metadata",
    "setup_rng",
    "get_metadata",
]
