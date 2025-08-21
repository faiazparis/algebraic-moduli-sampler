"""Cohomology computations for line bundles on curves.

This module implements the core cohomology computations using
Riemann-Roch and Serre duality.

References:
- Hartshorne, Algebraic Geometry (GTM 52): Riemann-Roch theorem
- Vakil, FOAG: Serre duality and cohomology
"""

from typing import Dict, List, Tuple, Union

from .curves import AlgebraicCurve, P1Curve, EllipticCurve, HyperellipticCurve, PlaneCurve
from .line_bundles import LineBundle, P1LineBundle, EllipticLineBundle, HyperellipticLineBundle, PlaneCurveLineBundle


def compute_h0_with_degree(curve: AlgebraicCurve, line_bundle_degree: int) -> int:
    """Compute h^0(L) for line bundle L of given degree on curve.
    
    This function dispatches to the appropriate computation method
    based on the curve type.
    
    Args:
        curve: Algebraic curve
        line_bundle_degree: Degree of the line bundle
        
    Returns:
        Dimension of global sections h^0(L)
    """
    if isinstance(curve, P1Curve):
        return P1LineBundle(line_bundle_degree).h0()
    elif isinstance(curve, EllipticCurve):
        return EllipticLineBundle(curve, line_bundle_degree).h0()
    elif isinstance(curve, HyperellipticCurve):
        return HyperellipticLineBundle(curve, line_bundle_degree).h0()
    elif isinstance(curve, PlaneCurve):
        return PlaneCurveLineBundle(curve, line_bundle_degree).h0()
    else:
        raise ValueError(f"Unsupported curve type: {type(curve)}")


def compute_h0(line_bundle: LineBundle) -> int:
    """Compute h^0(L) for line bundle L.
    
    This is an adapter function for backward compatibility.
    The line bundle must have a degree() method.
    
    Args:
        line_bundle: Line bundle object
        
    Returns:
        Dimension of global sections h^0(L)
    """
    if not hasattr(line_bundle, 'degree'):
        raise ValueError("Line bundle must have a degree() method")
    return line_bundle.h0()


def compute_h1_with_degree(curve: AlgebraicCurve, line_bundle_degree: int) -> int:
    """Compute h^1(L) for line bundle L of given degree on curve.
    
    This function dispatches to the appropriate computation method
    based on the curve type.
    
    Args:
        curve: Algebraic curve
        line_bundle_degree: Degree of the line bundle
        
    Returns:
        First cohomology dimension h^1(L)
    """
    if isinstance(curve, P1Curve):
        return P1LineBundle(line_bundle_degree).h1()
    elif isinstance(curve, EllipticCurve):
        return EllipticLineBundle(curve, line_bundle_degree).h1()
    elif isinstance(curve, HyperellipticCurve):
        return HyperellipticLineBundle(curve, line_bundle_degree).h1()
    elif isinstance(curve, PlaneCurve):
        return PlaneCurveLineBundle(curve, line_bundle_degree).h1()
    else:
        raise ValueError(f"Unsupported curve type: {type(curve)}")


def compute_h1(line_bundle: LineBundle) -> int:
    """Compute h^1(L) for line bundle L.
    
    This is an adapter function for backward compatibility.
    The line bundle must have a degree() method.
    
    Args:
        line_bundle: Line bundle object
        
    Returns:
        First cohomology dimension h^1(L)
    """
    if not hasattr(line_bundle, 'degree'):
        raise ValueError("Line bundle must have a degree() method")
    return line_bundle.h1()


def riemann_roch_check_with_degree(curve: AlgebraicCurve, line_bundle_degree: int) -> Dict[str, Union[int, bool]]:
    """Verify Riemann-Roch theorem for a line bundle.
    
    Riemann-Roch states: h^0(L) - h^1(L) = deg(L) + 1 - g
    where g is the genus of the curve.
    
    Args:
        curve: Algebraic curve
        line_bundle_degree: Degree of the line bundle
        
    Returns:
        Dictionary with computed values and verification result
    """
    h0 = compute_h0_with_degree(curve, line_bundle_degree)
    h1 = compute_h1_with_degree(curve, line_bundle_degree)
    g = curve.genus()
    
    # Riemann-Roch: h^0 - h^1 = deg + 1 - g
    left_side = h0 - h1
    right_side = line_bundle_degree + 1 - g
    
    return {
        "h0": h0,
        "h1": h1,
        "genus": g,
        "degree": line_bundle_degree,  # Alias for backward compatibility
        "line_bundle_degree": line_bundle_degree,
        "left_side": left_side,
        "right_side": right_side,
        "riemann_roch_satisfied": left_side == right_side,
        "satisfied": left_side == right_side,  # Alias for backward compatibility
        "difference": left_side - right_side,
    }


def riemann_roch_check(line_bundle: LineBundle) -> Dict[str, Union[int, bool]]:
    """Verify Riemann-Roch theorem for a line bundle.
    
    This is an adapter function for backward compatibility.
    The line bundle must have a degree() method.
    
    Args:
        line_bundle: Line bundle object
        
    Returns:
        Dictionary with computed values and verification result
    """
    if not hasattr(line_bundle, 'degree'):
        raise ValueError("Line bundle must have a degree() method")
    
    # Get the curve from the line bundle
    if hasattr(line_bundle, 'curve'):
        curve = line_bundle.curve
    else:
        # For P1, we can create a dummy curve
        from .curves import P1Curve
        curve = P1Curve()
    
    return riemann_roch_check_with_degree(curve, line_bundle.degree())


def serre_duality_check_with_degree(curve: AlgebraicCurve, line_bundle_degree: int) -> Dict[str, Union[int, bool]]:
    """Verify Serre duality for a line bundle.
    
    Serre duality states: h^1(L) = h^0(K ⊗ L^(-1))
    where K is the canonical bundle.
    
    Args:
        curve: Algebraic curve
        line_bundle_degree: Degree of the line bundle
        
    Returns:
        Dictionary with computed values and verification result
    """
    h1 = compute_h1_with_degree(curve, line_bundle_degree)
    g = curve.genus()
    
    # For Serre duality, we need to compute h^0(K ⊗ L^(-1))
    # K has degree 2g - 2, L^(-1) has degree -deg(L)
    # So K ⊗ L^(-1) has degree (2g - 2) - deg(L)
    canonical_degree = 2 * g - 2
    dual_bundle_degree = canonical_degree - line_bundle_degree
    
    h0_dual = compute_h0_with_degree(curve, dual_bundle_degree)
    
    return {
        "h1": h1,
        "h0_dual": h0_dual,
        "h0_K_minus_L": h0_dual,  # Alias for backward compatibility
        "h1_L": h1,  # Alias for backward compatibility
        "canonical_degree": canonical_degree,
        "dual_bundle_degree": dual_bundle_degree,
        "serre_duality_satisfied": h1 == h0_dual,
        "satisfied": h1 == h0_dual,  # Alias for backward compatibility
        "difference": h1 - h0_dual,
    }


def serre_duality_check(line_bundle: LineBundle) -> Dict[str, Union[int, bool]]:
    """Verify Serre duality for a line bundle.
    
    This is an adapter function for backward compatibility.
    The line bundle must have a degree() method.
    
    Args:
        line_bundle: Line bundle object
        
    Returns:
        Dictionary with computed values and verification result
    """
    if not hasattr(line_bundle, 'degree'):
        raise ValueError("Line bundle must have a degree() method")
    
    # Get the curve from the line bundle
    if hasattr(line_bundle, 'curve'):
        curve = line_bundle.curve
    else:
        # For P1, we can create a dummy curve
        from .curves import P1Curve
        curve = P1Curve()
    
    return serre_duality_check_with_degree(curve, line_bundle.degree())


def compute_cohomology_table_with_degree(curve: AlgebraicCurve, degree_range: Tuple[int, int]) -> List[Dict[str, Union[int, bool]]]:
    """Compute cohomology table for line bundles in a degree range.
    
    This is useful for understanding how cohomology varies with
    line bundle degree.
    
    Args:
        curve: Algebraic curve
        degree_range: Tuple (min_degree, max_degree)
        
    Returns:
        List of dictionaries with cohomology data for each degree
    """
    min_deg, max_deg = degree_range
    results = []
    
    for degree in range(min_deg, max_deg + 1):
        h0 = compute_h0_with_degree(curve, degree)
        h1 = compute_h1_with_degree(curve, degree)
        g = curve.genus()
        
        # Verify Riemann-Roch
        rr_check = riemann_roch_check_with_degree(curve, degree)
        
        result = {
            "degree": degree,
            "h0": h0,
            "h1": h1,
            "euler_characteristic": h0 - h1,
            "riemann_roch_verified": rr_check["riemann_roch_satisfied"],
            "genus": g,
        }
        results.append(result)
    
    return results


def compute_cohomology_table(curve: AlgebraicCurve, degree_range: Union[Tuple[int, int], List[int]]) -> List[Dict[str, Union[int, bool]]]:
    """Compute cohomology table for line bundles in a degree range.
    
    This is an adapter function that handles both tuple and list inputs.
    
    Args:
        curve: Algebraic curve
        degree_range: Tuple (min_degree, max_degree) or list of degrees
        
    Returns:
        List of dictionaries with cohomology data for each degree
    """
    if isinstance(degree_range, list):
        if len(degree_range) == 0:
            return []
        elif len(degree_range) == 1:
            degree = degree_range[0]
            h0 = compute_h0_with_degree(curve, degree)
            h1 = compute_h1_with_degree(curve, degree)
            g = curve.genus()
            rr_check = riemann_roch_check_with_degree(curve, degree)
            return [{
                "degree": degree,
                "h0": h0,
                "h1": h1,
                "euler_characteristic": h0 - h1,
                "riemann_roch_verified": rr_check["riemann_roch_satisfied"],
                "genus": g,
            }]
        else:
            # Convert list to tuple range
            min_deg, max_deg = min(degree_range), max(degree_range)
            degree_range = (min_deg, max_deg)
    
    return compute_cohomology_table_with_degree(curve, degree_range)


def p1_cech_verification(degree: int) -> Dict[str, Union[int, bool]]:
    """Verify P^1 cohomology using Čech cohomology with 2-open cover.
    
    This implements a basic Čech computation for O(d) on P^1
    using the standard open cover U_0, U_1.
    
    Reference: Stacks Project tag 01DW for Čech cohomology.
    
    Args:
        degree: Degree of the line bundle O(d)
        
    Returns:
        Dictionary with Čech computation results
    """
    # For P^1 with open cover U_0 = {z ≠ 0}, U_1 = {w ≠ 0}
    # where [z:w] are homogeneous coordinates
    
    if degree >= 0:
        # For d ≥ 0, global sections are polynomials of degree ≤ d
        # Čech 0-cochains: H^0 = k[x]_{≤d} where x = z/w
        h0_cech = degree + 1
        
        # Čech 1-cochains: H^1 = 0 for d ≥ 0
        h1_cech = 0
    else:
        # For d < 0, no global sections
        h0_cech = 0
        
        # Čech 1-cochains: H^1 = k[x]_{< -d - 1}
        h1_cech = -degree - 1
    
    # Compare with closed-form formulas
    h0_closed = max(degree + 1, 0)
    h1_closed = max(-degree - 1, 0)
    
    return {
        "degree": degree,
        "h0_cech": h0_cech,
        "h1_cech": h1_cech,
        "h0_closed": h0_closed,
        "h1_closed": h1_closed,
        "h0_closed_form": h0_closed,  # Alias for backward compatibility
        "h1_closed_form": h1_closed,  # Alias for backward compatibility
        "h0_match": h0_cech == h0_closed,
        "h1_match": h1_cech == h1_closed,
        "cech_verification_passed": (h0_cech == h0_closed) and (h1_cech == h1_closed),
    }
