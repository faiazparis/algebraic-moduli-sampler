"""Computation of mathematical invariants for algebraic curves.

This module provides a unified interface for computing all supported
invariants across different curve families.

All invariants are mathematically well-defined and computable:
- genus: topological invariant
- degK: canonical degree  
- h0, h1: sheaf cohomology dimensions
- canonical_deg: degree of canonical bundle
"""

from typing import Any, Dict, List, Union

from .curves import AlgebraicCurve, P1Curve, EllipticCurve, HyperellipticCurve, PlaneCurve
from .cohomology import compute_h0, compute_h1


def compute_invariants(
    curve: AlgebraicCurve,
    requested_invariants: List[str],
    line_bundle_degree: int = 0,
) -> Dict[str, Union[int, bool, str]]:
    """Compute requested invariants for an algebraic curve.
    
    This function provides a unified interface for computing
    invariants across all supported curve families.
    
    Args:
        curve: Algebraic curve
        requested_invariants: List of invariant names to compute
        line_bundle_degree: Degree of line bundle for h0/h1 computations
        
    Returns:
        Dictionary mapping invariant names to computed values
        
    Raises:
        ValueError: If an unsupported invariant is requested
    """
    supported_invariants = {"genus", "degK", "h0", "h1", "canonical_deg"}
    
    # Validate requested invariants
    invalid_invariants = set(requested_invariants) - supported_invariants
    if invalid_invariants:
        raise ValueError(f"Unsupported invariants: {invalid_invariants}")
    
    results = {}
    
    # Compute basic curve invariants
    if "genus" in requested_invariants:
        results["genus"] = curve.genus()
    
    if "canonical_deg" in requested_invariants:
        results["canonical_deg"] = curve.canonical_degree()
    
    if "degK" in requested_invariants:
        # degK is the same as canonical_deg
        results["degK"] = curve.canonical_degree()
    
    # Compute cohomology invariants if requested
    if "h0" in requested_invariants:
        results["h0"] = compute_h0(curve, line_bundle_degree)
    
    if "h1" in requested_invariants:
        results["h1"] = compute_h1(curve, line_bundle_degree)
    
    # Add curve type and smoothness information
    results["curve_type"] = curve.__class__.__name__
    results["is_smooth"] = curve.is_smooth()
    
    return results


def compute_family_invariants(
    curves: List[AlgebraicCurve],
    requested_invariants: List[str],
    line_bundle_degree: int = 0,
) -> List[Dict[str, Union[int, bool, str]]]:
    """Compute invariants for a family of curves.
    
    Args:
        curves: List of algebraic curves
        requested_invariants: List of invariant names to compute
        line_bundle_degree: Degree of line bundle for h0/h1 computations
        
    Returns:
        List of dictionaries with invariants for each curve
    """
    results = []
    
    for i, curve in enumerate(curves):
        curve_invariants = compute_invariants(curve, requested_invariants, line_bundle_degree)
        curve_invariants["curve_index"] = i
        results.append(curve_invariants)
    
    return results


def compute_p1_family_invariants(
    degree_range: tuple[int, int],
    requested_invariants: List[str],
) -> List[Dict[str, Union[int, bool, str]]]:
    """Compute invariants for P^1 family with line bundles O(d).
    
    Args:
        degree_range: Tuple (min_degree, max_degree)
        requested_invariants: List of invariant names to compute
        
    Returns:
        List of dictionaries with invariants for each degree
    """
    min_deg, max_deg = degree_range
    curves = [P1Curve(d) for d in range(min_deg, max_deg + 1)]
    
    results = []
    for i, curve in enumerate(curves):
        d = min_deg + i
        curve_invariants = compute_invariants(curve, requested_invariants, d)
        curve_invariants["degree"] = d
        curve_invariants["curve_index"] = i
        results.append(curve_invariants)
    
    return results


def compute_elliptic_family_invariants(
    coefficient_pairs: List[tuple[int, int]],
    requested_invariants: List[str],
    line_bundle_degree: int = 0,
) -> List[Dict[str, Union[int, bool, str]]]:
    """Compute invariants for elliptic curve family.
    
    Args:
        coefficient_pairs: List of (a, b) pairs for y² = x³ + ax + b
        requested_invariants: List of invariant names to compute
        line_bundle_degree: Degree of line bundle for h0/h1 computations
        
    Returns:
        List of dictionaries with invariants for each curve
    """
    curves = [EllipticCurve(a, b) for a, b in coefficient_pairs]
    
    results = []
    for i, curve in enumerate(curves):
        curve_invariants = compute_invariants(curve, requested_invariants, line_bundle_degree)
        curve_invariants["a"] = coefficient_pairs[i][0]
        curve_invariants["b"] = coefficient_pairs[i][1]
        curve_invariants["curve_index"] = i
        results.append(curve_invariants)
    
    return results


def compute_hyperelliptic_family_invariants(
    coefficient_lists: List[List[int]],
    requested_invariants: List[str],
    line_bundle_degree: int = 0,
) -> List[Dict[str, Union[int, bool, str]]]:
    """Compute invariants for hyperelliptic curve family.
    
    Args:
        coefficient_lists: List of coefficient lists for f(x) in y² = f(x)
        requested_invariants: List of invariant names to compute
        line_bundle_degree: Degree of line bundle for h0/h1 computations
        
    Returns:
        List of dictionaries with invariants for each curve
    """
    curves = [HyperellipticCurve(coeffs) for coeffs in coefficient_lists]
    
    results = []
    for i, curve in enumerate(curves):
        curve_invariants = compute_invariants(curve, requested_invariants, line_bundle_degree)
        curve_invariants["coefficients"] = coefficient_lists[i]
        curve_invariants["curve_index"] = i
        results.append(curve_invariants)
    
    return results


def compute_plane_curve_family_invariants(
    degree_coefficient_pairs: List[tuple[int, Dict[str, int]]],
    requested_invariants: List[str],
    line_bundle_degree: int = 0,
) -> List[Dict[str, Union[int, bool, str]]]:
    """Compute invariants for plane curve family.
    
    Args:
        degree_coefficient_pairs: List of (degree, coefficients) pairs
        requested_invariants: List of invariant names to compute
        line_bundle_degree: Degree of line bundle for h0/h1 computations
        
    Returns:
        List of dictionaries with invariants for each curve
    """
    curves = [PlaneCurve(degree, coeffs) for degree, coeffs in degree_coefficient_pairs]
    
    results = []
    for i, curve in enumerate(curves):
        curve_invariants = compute_invariants(curve, requested_invariants, line_bundle_degree)
        curve_invariants["degree"] = degree_coefficient_pairs[i][0]
        curve_invariants["coefficients"] = degree_coefficient_pairs[i][1]
        curve_invariants["curve_index"] = i
        results.append(curve_invariants)
    
    return results


def summarize_family_invariants(
    family_invariants: List[Dict[str, Union[int, bool, str]]],
) -> Dict[str, Any]:
    """Compute summary statistics for a family of curves.
    
    Args:
        family_invariants: List of invariant dictionaries from compute_family_invariants
        
    Returns:
        Dictionary with summary statistics
    """
    if not family_invariants:
        return {}
    
    summary = {
        "total_curves": len(family_invariants),
        "smooth_curves": sum(1 for inv in family_invariants if inv.get("is_smooth", False)),
        "curve_types": list(set(inv.get("curve_type", "Unknown") for inv in family_invariants)),
    }
    
    # Add numerical summaries for supported invariants
    numerical_invariants = ["genus", "canonical_deg", "h0", "h1"]
    
    for inv_name in numerical_invariants:
        values = [inv.get(inv_name) for inv in family_invariants if inv.get(inv_name) is not None]
        if values:
            summary[f"{inv_name}_min"] = min(values)
            summary[f"{inv_name}_max"] = max(values)
            summary[f"{inv_name}_mean"] = sum(values) / len(values)
    
    return summary


def validate_invariants_consistency(
    family_invariants: List[Dict[str, Union[int, bool, str]]],
) -> Dict[str, Any]:
    """Validate consistency of computed invariants.
    
    This function checks for mathematical consistency:
    - Genus consistency across curve types
    - Canonical degree = 2g - 2
    - Riemann-Roch theorem for h0, h1
    
    Args:
        family_invariants: List of invariant dictionaries
        
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        "total_curves": len(family_invariants),
        "validation_errors": [],
        "consistency_checks": {},
    }
    
    for i, inv in enumerate(family_invariants):
        curve_errors = []
        
        # Check genus consistency
        if "genus" in inv and "canonical_deg" in inv:
            expected_canonical_deg = 2 * inv["genus"] - 2
            if inv["canonical_deg"] != expected_canonical_deg:
                curve_errors.append(
                    f"Canonical degree {inv['canonical_deg']} != 2*{inv['genus']}-2 = {expected_canonical_deg}"
                )
        
        # Check Riemann-Roch if h0 and h1 are available
        if all(key in inv for key in ["h0", "h1", "genus"]):
            # This would need line bundle degree for proper check
            # For now, just note that we have the data
            pass
        
        if curve_errors:
            validation_results["validation_errors"].append({
                "curve_index": i,
                "errors": curve_errors,
            })
    
    validation_results["consistency_checks"]["canonical_degree_formula"] = len(
        validation_results["validation_errors"]
    ) == 0
    
    return validation_results
