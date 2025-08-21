"""Tests for invariants computation module."""

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
from moduli_sampler.geometry.invariants import (
    compute_invariants,
    compute_family_invariants,
    compute_p1_family_invariants,
    compute_elliptic_family_invariants,
    compute_hyperelliptic_family_invariants,
    compute_plane_curve_family_invariants,
    summarize_family_invariants,
    validate_invariants_consistency,
)


class TestSingleCurveInvariants:
    """Test invariants computation for single curves."""

    def test_compute_invariants_p1(self):
        """Test invariants computation for P1 curve."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["genus"] == 0
        assert invariants["canonical_degree"] == -2
        assert invariants["line_bundle_degree"] == 3
        assert invariants["h0"] == 4
        assert invariants["h1"] == 0
        assert invariants["euler_characteristic"] == 4
        assert invariants["h0_canonical"] == 0  # h0(K) = h0(O(-2)) = 0

    def test_compute_invariants_elliptic(self):
        """Test invariants computation for elliptic curve."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=2)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["genus"] == 1
        assert invariants["canonical_degree"] == 0
        assert invariants["line_bundle_degree"] == 2
        assert invariants["h0"] == 2
        assert invariants["h1"] == 0
        assert invariants["euler_characteristic"] == 2
        assert invariants["h0_canonical"] == 1  # h0(K) = h0(O(0)) = 1

    def test_compute_invariants_hyperelliptic(self):
        """Test invariants computation for hyperelliptic curve."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        line_bundle = HyperellipticLineBundle(curve, degree=1)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["genus"] == 1
        assert invariants["canonical_degree"] == 0
        assert invariants["line_bundle_degree"] == 1
        assert invariants["h0"] >= 0
        assert invariants["h1"] >= 0
        assert invariants["euler_characteristic"] == invariants["h0"] - invariants["h1"]
        assert invariants["h0_canonical"] == 1  # h0(K) = g = 1

    def test_compute_invariants_plane_curve(self):
        """Test invariants computation for plane curve."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        line_bundle = PlaneCurveLineBundle(curve, degree=1)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["genus"] == 1
        assert invariants["canonical_degree"] == 0
        assert invariants["line_bundle_degree"] == 1
        assert invariants["h0"] >= 0
        assert invariants["h1"] >= 0
        assert invariants["euler_characteristic"] == invariants["h0"] - invariants["h1"]
        assert invariants["h0_canonical"] == 1  # h0(K) = g = 1

    def test_compute_invariants_required_fields(self):
        """Test that all required fields are present in invariants."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=2)
        
        invariants = compute_invariants(curve, line_bundle)
        
        required_fields = [
            "genus", "canonical_degree", "line_bundle_degree",
            "h0", "h1", "euler_characteristic", "h0_canonical"
        ]
        
        for field in required_fields:
            assert field in invariants
            assert invariants[field] is not None

    def test_compute_invariants_mathematical_consistency(self):
        """Test mathematical consistency of computed invariants."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        
        invariants = compute_invariants(curve, line_bundle)
        
        # Check Euler characteristic formula
        assert invariants["euler_characteristic"] == invariants["h0"] - invariants["h1"]
        
        # Check canonical degree formula
        assert invariants["canonical_degree"] == 2 * invariants["genus"] - 2
        
        # Check that h0 and h1 are non-negative
        assert invariants["h0"] >= 0
        assert invariants["h1"] >= 0


class TestFamilyInvariants:
    """Test invariants computation for families of curves."""

    def test_compute_family_invariants_p1(self):
        """Test family invariants computation for P1 curves."""
        curves = [P1Curve(degree=0) for _ in range(3)]
        line_bundles = [P1LineBundle(degree=d) for d in [1, 2, 3]]
        
        family_invariants = compute_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 3
        for i, inv in enumerate(family_invariants):
            assert inv["genus"] == 0
            assert inv["line_bundle_degree"] == i + 1
            assert inv["h0"] == i + 2  # max(deg+1, 0)
            assert inv["h1"] == 0

    def test_compute_family_invariants_elliptic(self):
        """Test family invariants computation for elliptic curves."""
        curves = [EllipticCurve(a=1, b=2) for _ in range(3)]
        line_bundles = [EllipticLineBundle(curve, degree=d) for curve, d in zip(curves, [1, 2, 3])]
        
        family_invariants = compute_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 3
        for i, inv in enumerate(family_invariants):
            assert inv["genus"] == 1
            assert inv["line_bundle_degree"] == i + 1
            assert inv["h0"] >= 0
            assert inv["h1"] >= 0

    def test_compute_family_invariants_mixed_types(self):
        """Test family invariants computation with mixed curve types."""
        curves = [
            P1Curve(degree=0),
            EllipticCurve(a=1, b=2),
            HyperellipticCurve([1, 0, -2, 0, 1])
        ]
        line_bundles = [
            P1LineBundle(degree=2),
            EllipticLineBundle(curves[1], degree=1),
            HyperellipticLineBundle(curves[2], degree=1)
        ]
        
        family_invariants = compute_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 3
        assert family_invariants[0]["genus"] == 0  # P1
        assert family_invariants[1]["genus"] == 1  # Elliptic
        assert family_invariants[2]["genus"] == 1  # Hyperelliptic

    def test_compute_family_invariants_empty_family(self):
        """Test family invariants computation with empty family."""
        family_invariants = compute_family_invariants([], [])
        
        assert family_invariants == []

    def test_compute_family_invariants_mismatched_lengths(self):
        """Test that family invariants handles mismatched curve and line bundle counts."""
        curves = [P1Curve(degree=0), P1Curve(degree=0)]
        line_bundles = [P1LineBundle(degree=1)]
        
        # This should raise an error or handle gracefully
        with pytest.raises(ValueError):
            compute_family_invariants(curves, line_bundles)


class TestFamilySpecificInvariants:
    """Test family-specific invariants computation."""

    def test_compute_p1_family_invariants(self):
        """Test P1 family-specific invariants computation."""
        curves = [P1Curve(degree=0) for _ in range(3)]
        line_bundles = [P1LineBundle(degree=d) for d in [1, 2, 3]]
        
        family_invariants = compute_p1_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 3
        for i, inv in enumerate(family_invariants):
            assert inv["genus"] == 0
            assert inv["canonical_degree"] == -2
            assert inv["line_bundle_degree"] == i + 1
            assert inv["h0"] == i + 2
            assert inv["h1"] == 0

    def test_compute_elliptic_family_invariants(self):
        """Test elliptic family-specific invariants computation."""
        curves = [EllipticCurve(a=1, b=2) for _ in range(3)]
        line_bundles = [EllipticLineBundle(curve, degree=d) for curve, d in zip(curves, [1, 2, 3])]
        
        family_invariants = compute_elliptic_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 3
        for i, inv in enumerate(family_invariants):
            assert inv["genus"] == 1
            assert inv["canonical_degree"] == 0
            assert inv["line_bundle_degree"] == i + 1
            assert inv["h0"] >= 0
            assert inv["h1"] >= 0

    def test_compute_hyperelliptic_family_invariants(self):
        """Test hyperelliptic family-specific invariants computation."""
        coeffs_list = [
            [1, 0, -2, 0, 1],  # degree 4, genus 1
            [1, 0, 0, 0, 0, 1],  # degree 5, genus 2
            [1, 0, 0, 0, 0, 0, 1]  # degree 6, genus 2
        ]
        curves = [HyperellipticCurve(coeffs) for coeffs in coeffs_list]
        line_bundles = [HyperellipticLineBundle(curve, degree=1) for curve in curves]
        
        family_invariants = compute_hyperelliptic_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 3
        assert family_invariants[0]["genus"] == 1  # degree 4
        assert family_invariants[1]["genus"] == 2  # degree 5
        assert family_invariants[2]["genus"] == 2  # degree 6

    def test_compute_plane_curve_family_invariants(self):
        """Test plane curve family-specific invariants computation."""
        coeffs_list = [
            {"x^3": 1, "y^3": 1, "z^3": -2},  # degree 3, genus 1
            {"x^4": 1, "y^4": 1, "z^4": -2},  # degree 4, genus 3
        ]
        curves = [PlaneCurve(degree=deg, coefficients=coeffs) for deg, coeffs in zip([3, 4], coeffs_list)]
        line_bundles = [PlaneCurveLineBundle(curve, degree=1) for curve in curves]
        
        family_invariants = compute_plane_curve_family_invariants(curves, line_bundles)
        
        assert len(family_invariants) == 2
        assert family_invariants[0]["genus"] == 1  # degree 3
        assert family_invariants[1]["genus"] == 3  # degree 4


class TestFamilySummarization:
    """Test family invariants summarization."""

    def test_summarize_family_invariants_p1(self):
        """Test summarization of P1 family invariants."""
        curves = [P1Curve(degree=0) for _ in range(3)]
        line_bundles = [P1LineBundle(degree=d) for d in [1, 2, 3]]
        family_invariants = compute_p1_family_invariants(curves, line_bundles)
        
        summary = summarize_family_invariants(family_invariants)
        
        assert summary["family_size"] == 3
        assert summary["genus_range"] == [0, 0]  # All P1 curves have genus 0
        assert summary["degree_range"] == [1, 3]
        assert summary["h0_range"] == [2, 4]
        assert summary["h1_range"] == [0, 0]
        assert summary["euler_characteristic_range"] == [2, 4]

    def test_summarize_family_invariants_elliptic(self):
        """Test summarization of elliptic family invariants."""
        curves = [EllipticCurve(a=1, b=2) for _ in range(3)]
        line_bundles = [EllipticLineBundle(curve, degree=d) for curve, d in zip(curves, [1, 2, 3])]
        family_invariants = compute_elliptic_family_invariants(curves, line_bundles)
        
        summary = summarize_family_invariants(family_invariants)
        
        assert summary["family_size"] == 3
        assert summary["genus_range"] == [1, 1]  # All elliptic curves have genus 1
        assert summary["degree_range"] == [1, 3]
        assert summary["h0_range"][0] >= 0  # h0 should be non-negative
        assert summary["h1_range"][0] >= 0  # h1 should be non-negative

    def test_summarize_family_invariants_empty(self):
        """Test summarization of empty family."""
        summary = summarize_family_invariants([])
        
        assert summary["family_size"] == 0
        assert summary["genus_range"] == [None, None]
        assert summary["degree_range"] == [None, None]
        assert summary["h0_range"] == [None, None]
        assert summary["h1_range"] == [None, None]

    def test_summarize_family_invariants_single_curve(self):
        """Test summarization of single curve family."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=2)
        family_invariants = [compute_invariants(curve, line_bundle)]
        
        summary = summarize_family_invariants(family_invariants)
        
        assert summary["family_size"] == 1
        assert summary["genus_range"] == [0, 0]
        assert summary["degree_range"] == [2, 2]
        assert summary["h0_range"] == [3, 3]
        assert summary["h1_range"] == [0, 0]


class TestInvariantsConsistency:
    """Test invariants consistency validation."""

    def test_validate_invariants_consistency_valid(self):
        """Test consistency validation for valid invariants."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        invariants = compute_invariants(curve, line_bundle)
        
        validation_result = validate_invariants_consistency([invariants])
        
        assert validation_result["is_consistent"] is True
        assert len(validation_result["errors"]) == 0

    def test_validate_invariants_consistency_invalid_genus(self):
        """Test consistency validation for invalid genus."""
        # Create invalid invariants with wrong genus
        invalid_invariants = {
            "genus": 5,  # Wrong genus for P1
            "canonical_degree": -2,
            "line_bundle_degree": 3,
            "h0": 4,
            "h1": 0,
            "euler_characteristic": 4,
            "h0_canonical": 0
        }
        
        validation_result = validate_invariants_consistency([invalid_invariants])
        
        assert validation_result["is_consistent"] is False
        assert len(validation_result["errors"]) > 0

    def test_validate_invariants_consistency_invalid_canonical_degree(self):
        """Test consistency validation for invalid canonical degree."""
        # Create invalid invariants with wrong canonical degree
        invalid_invariants = {
            "genus": 0,
            "canonical_degree": 0,  # Wrong: should be -2 for genus 0
            "line_bundle_degree": 3,
            "h0": 4,
            "h1": 0,
            "euler_characteristic": 4,
            "h0_canonical": 0
        }
        
        validation_result = validate_invariants_consistency([invalid_invariants])
        
        assert validation_result["is_consistent"] is False
        assert len(validation_result["errors"]) > 0

    def test_validate_invariants_consistency_invalid_euler_characteristic(self):
        """Test consistency validation for invalid Euler characteristic."""
        # Create invalid invariants with wrong Euler characteristic
        invalid_invariants = {
            "genus": 0,
            "canonical_degree": -2,
            "line_bundle_degree": 3,
            "h0": 4,
            "h1": 0,
            "euler_characteristic": 5,  # Wrong: should be 4
            "h0_canonical": 0
        }
        
        validation_result = validate_invariants_consistency([invalid_invariants])
        
        assert validation_result["is_consistent"] is False
        assert len(validation_result["errors"]) > 0

    def test_validate_invariants_consistency_family(self):
        """Test consistency validation for family of invariants."""
        curves = [P1Curve(degree=0) for _ in range(3)]
        line_bundles = [P1LineBundle(degree=d) for d in [1, 2, 3]]
        family_invariants = compute_p1_family_invariants(curves, line_bundles)
        
        validation_result = validate_invariants_consistency(family_invariants)
        
        assert validation_result["is_consistent"] is True
        assert len(validation_result["errors"]) == 0

    def test_validate_invariants_consistency_mixed_validity(self):
        """Test consistency validation with mix of valid and invalid invariants."""
        # Valid invariants
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        valid_invariants = compute_invariants(curve, line_bundle)
        
        # Invalid invariants
        invalid_invariants = {
            "genus": 5,  # Wrong genus
            "canonical_degree": -2,
            "line_bundle_degree": 3,
            "h0": 4,
            "h1": 0,
            "euler_characteristic": 4,
            "h0_canonical": 0
        }
        
        mixed_invariants = [valid_invariants, invalid_invariants]
        validation_result = validate_invariants_consistency(mixed_invariants)
        
        assert validation_result["is_consistent"] is False
        assert len(validation_result["errors"]) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_compute_invariants_zero_degree_line_bundle(self):
        """Test invariants computation for zero degree line bundle."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=0)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["line_bundle_degree"] == 0
        assert invariants["h0"] == 1  # h0(O(0)) = 1
        assert invariants["h1"] == 0  # h1(O(0)) = 0
        assert invariants["euler_characteristic"] == 1

    def test_compute_invariants_negative_degree_line_bundle(self):
        """Test invariants computation for negative degree line bundle."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=-2)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["line_bundle_degree"] == -2
        assert invariants["h0"] == 0  # h0(O(-2)) = 0
        assert invariants["h1"] == 1  # h1(O(-2)) = 1
        assert invariants["euler_characteristic"] == -1

    def test_compute_invariants_large_degree_line_bundle(self):
        """Test invariants computation for large degree line bundle."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=100)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["line_bundle_degree"] == 100
        assert invariants["h0"] == 101  # max(100+1, 0) = 101
        assert invariants["h1"] == 0  # max(-100-1, 0) = 0
        assert invariants["euler_characteristic"] == 101

    def test_compute_invariants_large_negative_degree_line_bundle(self):
        """Test invariants computation for large negative degree line bundle."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=-100)
        
        invariants = compute_invariants(curve, line_bundle)
        
        assert invariants["line_bundle_degree"] == -100
        assert invariants["h0"] == 0  # max(-100+1, 0) = 0
        assert invariants["h1"] == 99  # max(-(-100)-1, 0) = 99
        assert invariants["euler_characteristic"] == -99
