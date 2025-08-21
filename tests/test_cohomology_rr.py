"""Tests for cohomology computation and Riemann-Roch verification."""

import pytest
import numpy as np

from moduli_sampler.geometry.curves import (
    P1Curve,
    EllipticCurve,
    HyperellipticCurve,
    PlaneCurve,
)
from moduli_sampler.geometry.line_bundles import (
    P1LineBundle,
    EllipticLineBundle,
    HyperellipticLineBundle,
    PlaneCurveLineBundle,
)
from moduli_sampler.geometry.cohomology import (
    compute_h0,
    compute_h1,
    riemann_roch_check,
    serre_duality_check,
    compute_cohomology_table,
    p1_cech_verification,
)


class TestCohomologyComputation:
    """Test cohomology computation functions."""

    def test_compute_h0_p1(self):
        """Test h0 computation for P1 line bundles."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        
        h0 = compute_h0(line_bundle)
        assert h0 == 4  # max(3+1, 0) = 4

    def test_compute_h0_elliptic(self):
        """Test h0 computation for elliptic line bundles."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=2)
        
        h0 = compute_h0(line_bundle)
        assert h0 == 2  # deg + 1 - g = 2 + 1 - 1 = 2

    def test_compute_h0_hyperelliptic(self):
        """Test h0 computation for hyperelliptic line bundles."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        line_bundle = HyperellipticLineBundle(curve, degree=1)
        
        h0 = compute_h0(line_bundle)
        assert h0 >= 0  # Should be non-negative

    def test_compute_h0_plane_curve(self):
        """Test h0 computation for plane curve line bundles."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        line_bundle = PlaneCurveLineBundle(curve, degree=1)
        
        h0 = compute_h0(line_bundle)
        assert h0 >= 0  # Should be non-negative

    def test_compute_h1_p1(self):
        """Test h1 computation for P1 line bundles."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=-3)
        
        h1 = compute_h1(line_bundle)
        assert h1 == 2  # max(-(-3)-1, 0) = 2

    def test_compute_h1_elliptic(self):
        """Test h1 computation for elliptic line bundles."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=-2)
        
        h1 = compute_h1(line_bundle)
        assert h1 == 2  # deg + 1 - g = -2 + 1 - 1 = -2, so h1 = 2

    def test_compute_h1_hyperelliptic(self):
        """Test h1 computation for hyperelliptic line bundles."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        line_bundle = HyperellipticLineBundle(curve, degree=-1)
        
        h1 = compute_h1(line_bundle)
        assert h1 >= 0  # Should be non-negative

    def test_compute_h1_plane_curve(self):
        """Test h1 computation for plane curve line bundles."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        line_bundle = PlaneCurveLineBundle(curve, degree=-1)
        
        h1 = compute_h1(line_bundle)
        assert h1 >= 0  # Should be non-negative

    def test_compute_h0_h1_consistency(self):
        """Test that h0 and h1 are consistent for various degrees."""
        # P1 case
        for deg in range(-5, 6):
            line_bundle = P1LineBundle(degree=deg)
            h0 = compute_h0(line_bundle)
            h1 = compute_h1(line_bundle)
            
            # Both should be non-negative
            assert h0 >= 0
            assert h1 >= 0
            
            # For P1, h0 and h1 can't both be positive
            if deg >= 0:
                assert h1 == 0
            else:
                assert h0 == 0

        # Elliptic case
        curve = EllipticCurve(a=1, b=2)
        for deg in range(-3, 4):
            line_bundle = EllipticLineBundle(curve, degree=deg)
            h0 = compute_h0(line_bundle)
            h1 = compute_h1(line_bundle)
            
            # Both should be non-negative
            assert h0 >= 0
            assert h1 >= 0


class TestRiemannRochVerification:
    """Test Riemann-Roch theorem verification."""

    def test_riemann_roch_p1(self):
        """Test Riemann-Roch for P1 curves."""
        curve = P1Curve(degree=0)
        
        for deg in range(-5, 6):
            line_bundle = P1LineBundle(degree=deg)
            result = riemann_roch_check(line_bundle)
            
            assert result["satisfied"] is True
            assert result["left_side"] == result["right_side"]
            assert result["difference"] == 0

    def test_riemann_roch_elliptic(self):
        """Test Riemann-Roch for elliptic curves."""
        curve = EllipticCurve(a=1, b=2)
        
        for deg in range(-3, 4):
            line_bundle = EllipticLineBundle(curve, degree=deg)
            result = riemann_roch_check(line_bundle)
            
            assert result["satisfied"] is True
            assert result["left_side"] == result["right_side"]
            assert result["difference"] == 0

    def test_riemann_roch_hyperelliptic(self):
        """Test Riemann-Roch for hyperelliptic curves."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        
        for deg in range(-2, 3):
            line_bundle = HyperellipticLineBundle(curve, degree=deg)
            result = riemann_roch_check(line_bundle)
            
            # For hyperelliptic curves, Riemann-Roch should still hold
            # Both sides can be negative for negative degree line bundles
            assert result["left_side"] == result["right_side"]
            assert result["difference"] == 0

    def test_riemann_roch_plane_curve(self):
        """Test Riemann-Roch for plane curves."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        
        for deg in range(-2, 3):
            line_bundle = PlaneCurveLineBundle(curve, degree=deg)
            result = riemann_roch_check(line_bundle)
            
            # For plane curves, Riemann-Roch should still hold
            # Both sides can be negative for negative degree line bundles
            assert result["left_side"] == result["right_side"]
            assert result["difference"] == 0

    def test_riemann_roch_formula_components(self):
        """Test individual components of Riemann-Roch formula."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        
        result = riemann_roch_check(line_bundle)
        
        # Check formula components
        assert result["h0"] == 4
        assert result["h1"] == 0
        assert result["degree"] == 3
        assert result["genus"] == 0
        
        # Check left side: h0 - h1
        assert result["left_side"] == 4 - 0 == 4
        
        # Check right side: deg + 1 - g
        assert result["right_side"] == 3 + 1 - 0 == 4


class TestSerreDuality:
    """Test Serre duality verification."""

    def test_serre_duality_p1(self):
        """Test Serre duality for P1 curves."""
        curve = P1Curve(degree=0)
        
        for deg in range(-5, 6):
            line_bundle = P1LineBundle(degree=deg)
            result = serre_duality_check(line_bundle)
            
            # For P1, Serre duality should hold
            assert result["satisfied"] is True
            assert result["h1_L"] == result["h0_K_minus_L"]

    def test_serre_duality_elliptic(self):
        """Test Serre duality for elliptic curves."""
        curve = EllipticCurve(a=1, b=2)
        
        for deg in range(-3, 4):
            line_bundle = EllipticLineBundle(curve, degree=deg)
            result = serre_duality_check(line_bundle)
            
            # For elliptic curves, Serre duality should hold
            assert result["satisfied"] is True
            assert result["h1_L"] == result["h0_K_minus_L"]

    def test_serre_duality_formula_components(self):
        """Test individual components of Serre duality formula."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        
        result = serre_duality_check(line_bundle)
        
        # Check formula components
        assert result["h1_L"] == 0  # h1(O(3)) = 0 on P1
        assert result["h0_K_minus_L"] == 0  # h0(K ⊗ O(-3)) = h0(O(-5)) = 0
        
        # Check that duality holds
        assert result["h1_L"] == result["h0_K_minus_L"]


class TestCohomologyTable:
    """Test cohomology table computation."""

    def test_compute_cohomology_table_p1(self):
        """Test cohomology table for P1."""
        curve = P1Curve(degree=0)
        degrees = [-2, -1, 0, 1, 2]
        
        table = compute_cohomology_table(curve, degrees)
        
        assert len(table) == len(degrees)
        
        for i, deg in enumerate(degrees):
            entry = table[i]
            assert entry["degree"] == deg
            assert entry["h0"] >= 0
            assert entry["h1"] >= 0
            assert entry["euler_characteristic"] == deg + 1 - curve.genus()

    def test_compute_cohomology_table_elliptic(self):
        """Test cohomology table for elliptic curves."""
        curve = EllipticCurve(a=1, b=2)
        degrees = [-2, -1, 0, 1, 2]
        
        table = compute_cohomology_table(curve, degrees)
        
        assert len(table) == len(degrees)
        
        for i, deg in enumerate(degrees):
            entry = table[i]
            assert entry["degree"] == deg
            assert entry["h0"] >= 0
            assert entry["h1"] >= 0
            assert entry["euler_characteristic"] == deg + 1 - curve.genus()

    def test_compute_cohomology_table_empty_degrees(self):
        """Test cohomology table with empty degrees list."""
        curve = P1Curve(degree=0)
        table = compute_cohomology_table(curve, [])
        
        assert table == []

    def test_compute_cohomology_table_single_degree(self):
        """Test cohomology table with single degree."""
        curve = P1Curve(degree=0)
        table = compute_cohomology_table(curve, [3])
        
        assert len(table) == 1
        entry = table[0]
        assert entry["degree"] == 3
        assert entry["h0"] == 4
        assert entry["h1"] == 0


class TestP1CechVerification:
    """Test P1 Čech cohomology verification."""

    def test_p1_cech_verification_positive_degree(self):
        """Test Čech verification for positive degree on P1."""
        result = p1_cech_verification(degree=3)
        
        assert result["degree"] == 3
        assert result["h0_cech"] == 4  # max(3+1, 0) = 4
        assert result["h1_cech"] == 0  # max(-3-1, 0) = 0
        assert result["h0_closed_form"] == 4
        assert result["h1_closed_form"] == 0
        assert result["h0_match"] is True
        assert result["h1_match"] is True

    def test_p1_cech_verification_zero_degree(self):
        """Test Čech verification for zero degree on P1."""
        result = p1_cech_verification(degree=0)
        
        assert result["degree"] == 0
        assert result["h0_cech"] == 1  # max(0+1, 0) = 1
        assert result["h1_cech"] == 0  # max(-0-1, 0) = 0
        assert result["h0_closed_form"] == 1
        assert result["h1_closed_form"] == 0
        assert result["h0_match"] is True
        assert result["h1_match"] is True

    def test_p1_cech_verification_negative_degree(self):
        """Test Čech verification for negative degree on P1."""
        result = p1_cech_verification(degree=-3)
        
        assert result["degree"] == -3
        assert result["h0_cech"] == 0  # max(-3+1, 0) = 0
        assert result["h1_cech"] == 2  # max(-(-3)-1, 0) = 2
        assert result["h0_closed_form"] == 0
        assert result["h1_closed_form"] == 2
        assert result["h0_match"] is True
        assert result["h1_match"] is True

    def test_p1_cech_verification_edge_cases(self):
        """Test Čech verification for edge cases."""
        # Test degree -1 (boundary case)
        result = p1_cech_verification(degree=-1)
        assert result["h0_cech"] == 0
        assert result["h1_cech"] == 0
        
        # Test degree 1 (boundary case)
        result = p1_cech_verification(degree=1)
        assert result["h0_cech"] == 2
        assert result["h1_cech"] == 0

    def test_p1_cech_verification_consistency(self):
        """Test that Čech verification is consistent with closed forms."""
        for deg in range(-5, 6):
            result = p1_cech_verification(degree=deg)
            
            # Both methods should agree
            assert result["h0_match"] is True
            assert result["h1_match"] is True
            
            # Values should be non-negative
            assert result["h0_cech"] >= 0
            assert result["h1_cech"] >= 0
            assert result["h0_closed_form"] >= 0
            assert result["h1_closed_form"] >= 0


class TestMathematicalConsistency:
    """Test mathematical consistency across different computation methods."""

    def test_riemann_roch_serre_duality_consistency(self):
        """Test that Riemann-Roch and Serre duality are consistent."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=2)
        
        # Check Riemann-Roch
        rr_result = riemann_roch_check(line_bundle)
        assert rr_result["satisfied"] is True
        
        # Check Serre duality
        sd_result = serre_duality_check(line_bundle)
        assert sd_result["satisfied"] is True
        
        # The two should be mathematically consistent
        h0 = rr_result["h0"]
        h1 = rr_result["h1"]
        deg = rr_result["degree"]
        g = rr_result["genus"]
        
        # Riemann-Roch: h0 - h1 = deg + 1 - g
        assert h0 - h1 == deg + 1 - g
        
        # Serre duality: h1(L) = h0(K ⊗ L^(-1))
        # For P1, K = O(-2), so K ⊗ L^(-1) = O(-2 - 2) = O(-4)
        # h0(O(-4)) = 0, which should equal h1(O(2)) = 0
        assert h1 == sd_result["h0_K_minus_L"]

    def test_cohomology_bounds(self):
        """Test that cohomology values respect mathematical bounds."""
        curve = EllipticCurve(a=1, b=2)
        
        for deg in range(-5, 6):
            line_bundle = EllipticLineBundle(curve, degree=deg)
            
            h0 = compute_h0(line_bundle)
            h1 = compute_h1(line_bundle)
            
            # Both should be non-negative
            assert h0 >= 0
            assert h1 >= 0
            
            # For elliptic curves, h0 and h1 can't both be large
            # This is a basic bound from Riemann-Roch
            if deg < 0:
                assert h0 == 0
            if deg > 1:
                assert h1 == 0

    def test_genus_consistency(self):
        """Test that genus is consistent across different curve types."""
        # P1 should always have genus 0
        p1_curve = P1Curve(degree=0)
        assert p1_curve.genus() == 0
        
        # Elliptic curves should always have genus 1
        elliptic_curve = EllipticCurve(a=1, b=2)
        assert elliptic_curve.genus() == 1
        
        # Hyperelliptic curves should have genus ≥ 1
        coeffs = [1, 0, -2, 0, 1]
        hyperelliptic_curve = HyperellipticCurve(coeffs)
        assert hyperelliptic_curve.genus() >= 1
        
        # Plane curves should have genus ≥ 0
        plane_coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        plane_curve = PlaneCurve(degree=3, coefficients=plane_coeffs)
        assert plane_curve.genus() >= 0
