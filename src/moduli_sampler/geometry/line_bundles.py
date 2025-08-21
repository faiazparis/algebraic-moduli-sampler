"""Line bundles and cohomology computations.

This module implements line bundles on algebraic curves and their
cohomology computations using Riemann-Roch and Serre duality.

References:
- Hartshorne, Algebraic Geometry (GTM 52): Riemann-Roch theorem
- Vakil, FOAG: Serre duality and cohomology
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .curves import AlgebraicCurve


class LineBundle(ABC):
    """Abstract line bundle on an algebraic curve.
    
    All line bundles implement cohomology computations through
    Riemann-Roch and Serre duality.
    """
    
    def __init__(self, curve: AlgebraicCurve):
        """Initialize line bundle on a curve.
        
        Args:
            curve: The algebraic curve
        """
        self.curve = curve
    
    @abstractmethod
    def degree(self) -> int:
        """Compute the degree of the line bundle.
        
        Returns:
            Degree as an integer
        """
        pass
    
    def h0(self) -> int:
        """Compute h^0(L) using Riemann-Roch and Serre duality.
        
        For a line bundle L on a curve of genus g:
        h^0(L) - h^1(L) = deg(L) + 1 - g (Riemann-Roch)
        h^1(L) = h^0(K ⊗ L^(-1)) (Serre duality)
        
        Returns:
            Dimension of global sections
        """
        # This is a placeholder - subclasses should implement
        # specific cohomology computations
        raise NotImplementedError("Subclasses must implement h0()")
    
    def h1(self) -> int:
        """Compute h^1(L) using Serre duality.
        
        h^1(L) = h^0(K ⊗ L^(-1)) where K is the canonical bundle.
        
        Returns:
            First cohomology dimension
        """
        # This is a placeholder - subclasses should implement
        # specific cohomology computations
        raise NotImplementedError("Subclasses must implement h1()")
    
    def euler_characteristic(self) -> int:
        """Compute Euler characteristic χ(L) = h^0(L) - h^1(L).
        
        By Riemann-Roch: χ(L) = deg(L) + 1 - g
        
        Returns:
            Euler characteristic
        """
        return self.degree() + 1 - self.curve.genus()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert line bundle to dictionary representation.
        
        Returns:
            Dictionary with line bundle data and cohomology
        """
        return {
            "curve_type": self.curve.__class__.__name__,
            "curve_data": self.curve.to_dict(),
            "line_bundle_degree": self.degree(),
            "h0": self.h0(),
            "h1": self.h1(),
            "euler_characteristic": self.euler_characteristic(),
        }


class P1LineBundle(LineBundle):
    """Line bundle O(d) on P^1.
    
    This is the simplest case with closed-form cohomology.
    Reference: Stacks Project tag 01PZ for O(d) on P^n.
    """
    
    def __init__(self, degree: int):
        """Initialize O(d) on P^1.
        
        Args:
            degree: Degree of the line bundle
        """
        from .curves import P1Curve
        curve = P1Curve(degree)
        super().__init__(curve)
        self._degree = degree
    
    def degree(self) -> int:
        """Degree of O(d).
        
        Returns:
            Degree d
        """
        return self._degree
    
    def h0(self) -> int:
        """h^0(O(d)) = max(d + 1, 0) on P^1.
        
        Returns:
            Dimension of global sections
        """
        return max(self._degree + 1, 0)
    
    def h1(self) -> int:
        """h^1(O(d)) = max(-d - 1, 0) on P^1.
        
        This follows from Serre duality: h^1(O(d)) = h^0(K ⊗ O(d)^(-1))
        where K = O(-2) is the canonical bundle.
        
        Returns:
            First cohomology dimension
        """
        return max(-self._degree - 1, 0)


class EllipticLineBundle(LineBundle):
    """Line bundle on an elliptic curve.
    
    For elliptic curves (genus 1), we use Riemann-Roch:
    h^0(L) - h^1(L) = deg(L)
    """
    
    def __init__(self, curve: 'EllipticCurve', degree: int):
        """Initialize line bundle on elliptic curve.
        
        Args:
            curve: Elliptic curve
            degree: Degree of the line bundle
        """
        super().__init__(curve)
        self._degree = degree
    
    def degree(self) -> int:
        """Degree of the line bundle.
        
        Returns:
            Degree
        """
        return self._degree
    
    def h0(self) -> int:
        """Compute h^0(L) for line bundle L on elliptic curve.
        
        For genus 1, Riemann-Roch gives: h^0(L) - h^1(L) = deg(L)
        We use Serre duality to determine which is non-zero.
        
        Returns:
            Dimension of global sections
        """
        if self._degree < 0:
            return 0
        elif self._degree == 0:
            # O(0) = O, so h^0 = 1, h^1 = 0
            return 1
        else:
            # deg(L) > 0, so h^0(L) = deg(L) and h^1(L) = 0
            return self._degree
    
    def h1(self) -> int:
        """Compute h^1(L) for line bundle L on elliptic curve.
        
        For genus 1, Riemann-Roch gives: h^0(L) - h^1(L) = deg(L)
        We use Serre duality to determine which is non-zero.
        
        Returns:
            First cohomology dimension
        """
        if self._degree < 0:
            # For negative degree, h^0 = 0, so h^1 = -deg(L)
            return -self._degree
        elif self._degree == 0:
            # O(0) = O, so h^0 = 1, h^1 = g = 1 for genus 1
            return 1
        else:
            # deg(L) > 0, so h^0(L) = deg(L) and h^1(L) = 0
            return 0


class HyperellipticLineBundle(LineBundle):
    """Line bundle on a hyperelliptic curve.
    
    For hyperelliptic curves, we use Riemann-Roch and may need
    to compute more sophisticated cohomology.
    """
    
    def __init__(self, curve: 'HyperellipticCurve', degree: int):
        """Initialize line bundle on hyperelliptic curve.
        
        Args:
            curve: Hyperelliptic curve
            degree: Degree of the line bundle
        """
        super().__init__(curve)
        self._degree = degree
    
    def degree(self) -> int:
        """Degree of the line bundle.
        
        Returns:
            Degree
        """
        return self._degree
    
    def h0(self) -> int:
        """Compute h^0(L) for line bundle L on hyperelliptic curve.
        
        This is a simplified implementation. For a proper computation,
        one would need more sophisticated methods.
        
        Returns:
            Dimension of global sections
        """
        # Simplified: use Riemann-Roch bounds
        g = self.curve.genus()
        if self._degree < 0:
            return 0
        elif self._degree == 0:
            return 1
        else:
            # Upper bound from Riemann-Roch
            return max(0, self._degree + 1 - g)
    
    def h1(self) -> int:
        """Compute h^1(L) for line bundle L on hyperelliptic curve.
        
        This is a simplified implementation. For a proper computation,
        one would need more sophisticated methods.
        
        Returns:
            First cohomology dimension
        """
        # Simplified: use Riemann-Roch
        g = self.curve.genus()
        if self._degree < 0:
            return -self._degree
        elif self._degree == 0:
            return g
        else:
            # Use Riemann-Roch: h^0 - h^1 = deg + 1 - g
            h0 = self.h0()
            return max(0, h0 - (self._degree + 1 - g))


class PlaneCurveLineBundle(LineBundle):
    """Line bundle on a plane curve.
    
    For plane curves, we use Riemann-Roch and may need to check
    smoothness conditions.
    """
    
    def __init__(self, curve: 'PlaneCurve', degree: int):
        """Initialize line bundle on plane curve.
        
        Args:
            curve: Plane curve
            degree: Degree of the line bundle
        """
        super().__init__(curve)
        self._degree = degree
    
    def degree(self) -> int:
        """Degree of the line bundle.
        
        Returns:
            Degree
        """
        return self._degree
    
    def h0(self) -> int:
        """Compute h^0(L) for line bundle L on plane curve.
        
        This is a simplified implementation. For a proper computation,
        one would need more sophisticated methods.
        
        Returns:
            Dimension of global sections
        """
        # Simplified: use Riemann-Roch bounds
        g = self.curve.genus()
        if self._degree < 0:
            return 0
        elif self._degree == 0:
            return 1
        else:
            # Upper bound from Riemann-Roch
            return max(0, self._degree + 1 - g)
    
    def h1(self) -> int:
        """Compute h^1(L) for line bundle L on plane curve.
        
        This is a simplified implementation. For a proper computation,
        one would need more sophisticated methods.
        
        Returns:
            First cohomology dimension
        """
        # Simplified: use Riemann-Roch
        g = self.curve.genus()
        if self._degree < 0:
            return -self._degree
        elif self._degree == 0:
            return g
        else:
            # Use Riemann-Roch: h^0 - h^1 = deg + 1 - g
            h0 = self.h0()
            return max(0, h0 - (self._degree + 1 - g))
