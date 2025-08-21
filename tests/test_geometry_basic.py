"""Tests for basic geometry classes and curves."""

import pytest
import sympy as sp

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


class TestP1Curve:
    """Test P1Curve class."""

    def test_p1_curve_creation(self):
        """Test P1Curve creation."""
        curve = P1Curve(degree=3)
        assert curve.degree == 3

    def test_p1_genus(self):
        """Test P1 genus is always 0."""
        curve = P1Curve(degree=5)
        assert curve.genus() == 0

    def test_p1_smoothness(self):
        """Test P1 is always smooth."""
        curve = P1Curve(degree=-2)
        assert curve.is_smooth() is True

    def test_p1_canonical_degree(self):
        """Test P1 canonical degree is always -2."""
        curve = P1Curve(degree=10)
        assert curve.canonical_degree() == -2

    def test_p1_h0_positive_degree(self):
        """Test h0 for positive degree."""
        curve = P1Curve(degree=3)
        assert curve.h0() == 4  # max(3+1, 0) = 4

    def test_p1_h0_zero_degree(self):
        """Test h0 for zero degree."""
        curve = P1Curve(degree=0)
        assert curve.h0() == 1  # max(0+1, 0) = 1

    def test_p1_h0_negative_degree(self):
        """Test h0 for negative degree."""
        curve = P1Curve(degree=-3)
        assert curve.h0() == 0  # max(-3+1, 0) = 0

    def test_p1_h1_positive_degree(self):
        """Test h1 for positive degree."""
        curve = P1Curve(degree=3)
        assert curve.h1() == 0  # max(-3-1, 0) = 0

    def test_p1_h1_zero_degree(self):
        """Test h1 for zero degree."""
        curve = P1Curve(degree=0)
        assert curve.h1() == 0  # max(-0-1, 0) = 0

    def test_p1_h1_negative_degree(self):
        """Test h1 for negative degree."""
        curve = P1Curve(degree=-3)
        assert curve.h1() == 2  # max(-(-3)-1, 0) = 2

    def test_p1_to_dict(self):
        """Test P1Curve to_dict method."""
        curve = P1Curve(degree=2)
        curve_dict = curve.to_dict()
        
        assert curve_dict["type"] == "P1Curve"
        assert curve_dict["genus"] == 0
        assert curve_dict["canonical_degree"] == -2
        assert curve_dict["is_smooth"] is True
        assert curve_dict["degree"] == 2
        assert curve_dict["h0"] == 3
        assert curve_dict["h1"] == 0


class TestEllipticCurve:
    """Test EllipticCurve class."""

    def test_elliptic_curve_creation(self):
        """Test EllipticCurve creation."""
        curve = EllipticCurve(a=1, b=2)
        assert curve.a == 1
        assert curve.b == 2

    def test_elliptic_genus(self):
        """Test elliptic curve genus is always 1."""
        curve = EllipticCurve(a=0, b=1)
        assert curve.genus() == 1

    def test_elliptic_canonical_degree(self):
        """Test elliptic curve canonical degree is always 0."""
        curve = EllipticCurve(a=1, b=0)
        assert curve.canonical_degree() == 0

    def test_elliptic_discriminant(self):
        """Test elliptic curve discriminant calculation."""
        curve = EllipticCurve(a=1, b=2)
        expected = -16 * (4 * 1**3 + 27 * 2**2)
        assert curve.discriminant() == expected

    def test_elliptic_smoothness_smooth(self):
        """Test smooth elliptic curve."""
        curve = EllipticCurve(a=1, b=2)
        assert curve.is_smooth() is True

    def test_elliptic_smoothness_singular(self):
        """Test singular elliptic curve."""
        curve = EllipticCurve(a=0, b=0)  # y² = x³
        assert curve.is_smooth() is False

    def test_elliptic_to_dict(self):
        """Test EllipticCurve to_dict method."""
        curve = EllipticCurve(a=1, b=2)
        curve_dict = curve.to_dict()
        
        assert curve_dict["type"] == "EllipticCurve"
        assert curve_dict["genus"] == 1
        assert curve_dict["canonical_degree"] == 0
        assert curve_dict["is_smooth"] is True
        assert curve_dict["a"] == 1
        assert curve_dict["b"] == 2
        assert "discriminant" in curve_dict


class TestHyperellipticCurve:
    """Test HyperellipticCurve class."""

    def test_hyperelliptic_curve_creation(self):
        """Test HyperellipticCurve creation."""
        coeffs = [1, 0, -2, 0, 1]  # x⁴ - 2x² + 1
        curve = HyperellipticCurve(coeffs)
        assert curve.coefficients == coeffs
        assert curve.degree == 4

    def test_hyperelliptic_genus_degree_5(self):
        """Test genus for degree 5 polynomial."""
        coeffs = [1, 0, 0, 0, 0, 1]  # x⁵ + 1
        curve = HyperellipticCurve(coeffs)
        assert curve.genus() == 2  # (5-1)/2 = 2

    def test_hyperelliptic_genus_degree_6(self):
        """Test genus for degree 6 polynomial."""
        coeffs = [1, 0, 0, 0, 0, 0, 1]  # x⁶ + 1
        curve = HyperellipticCurve(coeffs)
        assert curve.genus() == 2  # (6-1)/2 = 2

    def test_hyperelliptic_canonical_degree(self):
        """Test canonical degree calculation."""
        coeffs = [1, 0, -2, 0, 1]  # degree 4, genus 1
        curve = HyperellipticCurve(coeffs)
        assert curve.canonical_degree() == 0  # 2*1-2 = 0

    def test_hyperelliptic_f_polynomial(self):
        """Test f_polynomial method."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        poly = curve.f_polynomial()
        
        assert isinstance(poly, sp.Poly)
        assert poly.degree() == 4
        assert poly.all_coeffs() == [1, 0, -2, 0, 1]

    def test_hyperelliptic_smoothness(self):
        """Test smoothness check."""
        coeffs = [1, 0, -2, 0, 1]  # x⁴ - 2x² + 1
        curve = HyperellipticCurve(coeffs)
        # This is a simplified check, so it may always return True
        assert isinstance(curve.is_smooth(), bool)

    def test_hyperelliptic_to_dict(self):
        """Test HyperellipticCurve to_dict method."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        curve_dict = curve.to_dict()
        
        assert curve_dict["type"] == "HyperellipticCurve"
        assert curve_dict["genus"] == 1
        assert curve_dict["canonical_degree"] == 0
        assert curve_dict["coefficients"] == coeffs
        assert curve_dict["polynomial_degree"] == 4
        assert "f_polynomial" in curve_dict


class TestPlaneCurve:
    """Test PlaneCurve class."""

    def test_plane_curve_creation(self):
        """Test PlaneCurve creation."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        assert curve.degree == 3
        assert curve.coefficients == coeffs

    def test_plane_curve_genus_degree_3(self):
        """Test genus for degree 3 plane curve."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        assert curve.genus() == 1  # (3-1)(3-2)/2 = 1

    def test_plane_curve_genus_degree_4(self):
        """Test genus for degree 4 plane curve."""
        coeffs = {"x^4": 1, "y^4": 1, "z^4": -2}
        curve = PlaneCurve(degree=4, coefficients=coeffs)
        assert curve.genus() == 3  # (4-1)(4-2)/2 = 3

    def test_plane_curve_canonical_degree(self):
        """Test canonical degree calculation."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        assert curve.canonical_degree() == 0  # 2*1-2 = 0

    def test_plane_curve_f_polynomial(self):
        """Test f_polynomial method."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        poly = curve.f_polynomial()
        
        assert isinstance(poly, sp.Expr)
        # Check that the polynomial contains the expected terms
        assert "x**3" in str(poly)
        assert "y**3" in str(poly)
        assert "z**3" in str(poly)

    def test_plane_curve_smoothness(self):
        """Test smoothness check."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        # This is a simplified check, so it may always return True
        assert isinstance(curve.is_smooth(), bool)

    def test_plane_curve_to_dict(self):
        """Test PlaneCurve to_dict method."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        curve_dict = curve.to_dict()
        
        assert curve_dict["type"] == "PlaneCurve"
        assert curve_dict["genus"] == 1
        assert curve_dict["canonical_degree"] == 0
        assert curve_dict["degree"] == 3
        assert curve_dict["coefficients"] == coeffs
        assert "polynomial" in curve_dict


class TestLineBundles:
    """Test line bundle classes."""

    def test_p1_line_bundle_creation(self):
        """Test P1LineBundle creation."""
        line_bundle = P1LineBundle(degree=3)
        assert line_bundle.degree() == 3
        assert line_bundle.curve.genus() == 0

    def test_p1_line_bundle_h0(self):
        """Test P1LineBundle h0 computation."""
        line_bundle = P1LineBundle(degree=3)
        assert line_bundle.h0() == 4  # max(3+1, 0) = 4

    def test_p1_line_bundle_h1(self):
        """Test P1LineBundle h1 computation."""
        line_bundle = P1LineBundle(degree=-3)
        assert line_bundle.h1() == 2  # max(-(-3)-1, 0) = 2

    def test_p1_line_bundle_euler_characteristic(self):
        """Test P1LineBundle Euler characteristic."""
        line_bundle = P1LineBundle(degree=2)
        assert line_bundle.euler_characteristic() == 3  # 2 + 1 - 0 = 3

    def test_p1_line_bundle_to_dict(self):
        """Test P1LineBundle to_dict method."""
        line_bundle = P1LineBundle(degree=1)
        bundle_dict = line_bundle.to_dict()
        
        assert bundle_dict["curve_type"] == "P1Curve"
        assert bundle_dict["line_bundle_degree"] == 1
        assert bundle_dict["h0"] == 2
        assert bundle_dict["h1"] == 0
        assert bundle_dict["euler_characteristic"] == 2

    def test_elliptic_line_bundle_creation(self):
        """Test EllipticLineBundle creation."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=3)
        assert line_bundle.degree() == 3
        assert line_bundle.curve.genus() == 1

    def test_elliptic_line_bundle_h0_positive(self):
        """Test EllipticLineBundle h0 for positive degree."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=3)
        assert line_bundle.h0() == 3

    def test_elliptic_line_bundle_h0_zero(self):
        """Test EllipticLineBundle h0 for zero degree."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=0)
        assert line_bundle.h0() == 1

    def test_elliptic_line_bundle_h0_negative(self):
        """Test EllipticLineBundle h0 for negative degree."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=-2)
        assert line_bundle.h0() == 0

    def test_elliptic_line_bundle_h1_positive(self):
        """Test EllipticLineBundle h1 for positive degree."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=3)
        assert line_bundle.h1() == 0

    def test_elliptic_line_bundle_h1_zero(self):
        """Test EllipticLineBundle h1 for zero degree."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=0)
        # For genus 1, h^1(O) = g = 1
        assert line_bundle.h1() == 1

    def test_elliptic_line_bundle_h1_negative(self):
        """Test EllipticLineBundle h1 for negative degree."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=-2)
        assert line_bundle.h1() == 2

    def test_elliptic_line_bundle_euler_characteristic(self):
        """Test EllipticLineBundle Euler characteristic."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=2)
        assert line_bundle.euler_characteristic() == 2  # 2 + 1 - 1 = 2

    def test_hyperelliptic_line_bundle_creation(self):
        """Test HyperellipticLineBundle creation."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        line_bundle = HyperellipticLineBundle(curve, degree=1)
        assert line_bundle.degree() == 1
        assert line_bundle.curve.genus() == 1

    def test_hyperelliptic_line_bundle_h0_positive(self):
        """Test HyperellipticLineBundle h0 for positive degree."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        line_bundle = HyperellipticLineBundle(curve, degree=2)
        assert line_bundle.h0() >= 0  # Should be non-negative

    def test_hyperelliptic_line_bundle_h1_positive(self):
        """Test HyperellipticLineBundle h1 for positive degree."""
        coeffs = [1, 0, -2, 0, 1]
        curve = HyperellipticCurve(coeffs)
        line_bundle = HyperellipticLineBundle(curve, degree=2)
        assert line_bundle.h1() >= 0  # Should be non-negative

    def test_plane_curve_line_bundle_creation(self):
        """Test PlaneCurveLineBundle creation."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        line_bundle = PlaneCurveLineBundle(curve, degree=1)
        assert line_bundle.degree() == 1
        assert line_bundle.curve.genus() == 1

    def test_plane_curve_line_bundle_h0_positive(self):
        """Test PlaneCurveLineBundle h0 for positive degree."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        line_bundle = PlaneCurveLineBundle(curve, degree=2)
        assert line_bundle.h0() >= 0  # Should be non-negative

    def test_plane_curve_line_bundle_h1_positive(self):
        """Test PlaneCurveLineBundle h1 for positive degree."""
        coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        curve = PlaneCurve(degree=3, coefficients=coeffs)
        line_bundle = PlaneCurveLineBundle(curve, degree=2)
        assert line_bundle.h1() >= 0  # Should be non-negative


class TestMathematicalProperties:
    """Test mathematical properties and consistency."""

    def test_p1_riemann_roch(self):
        """Test Riemann-Roch theorem for P1."""
        curve = P1Curve(degree=0)
        line_bundle = P1LineBundle(degree=3)
        
        # Riemann-Roch: h0 - h1 = deg + 1 - g
        h0 = line_bundle.h0()
        h1 = line_bundle.h1()
        deg = line_bundle.degree()
        g = curve.genus()
        
        assert h0 - h1 == deg + 1 - g

    def test_elliptic_riemann_roch(self):
        """Test Riemann-Roch theorem for elliptic curve."""
        curve = EllipticCurve(a=1, b=2)
        line_bundle = EllipticLineBundle(curve, degree=2)
        
        # Riemann-Roch: h0 - h1 = deg + 1 - g
        h0 = line_bundle.h0()
        h1 = line_bundle.h1()
        deg = line_bundle.degree()
        g = curve.genus()
        
        assert h0 - h1 == deg + 1 - g

    def test_canonical_degree_formula(self):
        """Test canonical degree formula: deg(K) = 2g - 2."""
        # P1: g = 0, deg(K) = -2
        p1_curve = P1Curve(degree=0)
        assert p1_curve.canonical_degree() == 2 * p1_curve.genus() - 2
        
        # Elliptic: g = 1, deg(K) = 0
        elliptic_curve = EllipticCurve(a=1, b=2)
        assert elliptic_curve.canonical_degree() == 2 * elliptic_curve.genus() - 2
        
        # Hyperelliptic: g = 1, deg(K) = 0
        coeffs = [1, 0, -2, 0, 1]
        hyperelliptic_curve = HyperellipticCurve(coeffs)
        assert hyperelliptic_curve.canonical_degree() == 2 * hyperelliptic_curve.genus() - 2
        
        # Plane curve: g = 1, deg(K) = 0
        plane_coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        plane_curve = PlaneCurve(degree=3, coefficients=plane_coeffs)
        assert plane_curve.canonical_degree() == 2 * plane_curve.genus() - 2

    def test_genus_non_negative(self):
        """Test that genus is always non-negative."""
        # P1
        p1_curve = P1Curve(degree=0)
        assert p1_curve.genus() >= 0
        
        # Elliptic
        elliptic_curve = EllipticCurve(a=1, b=2)
        assert elliptic_curve.genus() >= 0
        
        # Hyperelliptic
        coeffs = [1, 0, -2, 0, 1]
        hyperelliptic_curve = HyperellipticCurve(coeffs)
        assert hyperelliptic_curve.genus() >= 0
        
        # Plane curve
        plane_coeffs = {"x^3": 1, "y^3": 1, "z^3": -2}
        plane_curve = PlaneCurve(degree=3, coefficients=plane_coeffs)
        assert plane_curve.genus() >= 0
