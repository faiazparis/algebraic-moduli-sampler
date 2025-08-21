"""Geometry module for algebraic curves and line bundles.

This module implements the core mathematical objects:
- P1Curve: Line bundles O(d) on P^1
- EllipticCurve: y^2 = x^3 + ax + b
- HyperellipticCurve: y^2 = f(x)
- PlaneCurve: Homogeneous F(x,y,z) = 0
- LineBundle: Abstract line bundle with cohomology

All mathematics is grounded in trusted references with explicit citations.
"""

from .curves import P1Curve, EllipticCurve, HyperellipticCurve, PlaneCurve
from .line_bundles import LineBundle
from .cohomology import compute_h0, compute_h1, riemann_roch_check
from .invariants import compute_invariants

__all__ = [
    "P1Curve",
    "EllipticCurve", 
    "HyperellipticCurve",
    "PlaneCurve",
    "LineBundle",
    "compute_h0",
    "compute_h1", 
    "riemann_roch_check",
    "compute_invariants",
]
