# Mathematical Theory

This document provides the mathematical background for the Algebraic Moduli Sampler, with explicit citations to trusted references.

## Algebraic Curves and Line Bundles

### Basic Definitions

An **algebraic curve** over a field k is a one-dimensional algebraic variety. In this sampler, we focus on smooth projective curves, which can be embedded in projective space.

A **line bundle** L on a curve C is a rank-1 locally free sheaf. Line bundles are classified by their degree, which measures how "twisted" the bundle is.

### Genus and Topology

The **genus** g of a curve is a fundamental topological invariant that counts the number of "holes" in the surface. For smooth projective curves:

- **g = 0**: Rational curves (e.g., P¹)
- **g = 1**: Elliptic curves
- **g ≥ 2**: Higher genus curves

## Riemann-Roch Theorem

### Statement

For a line bundle L on a smooth projective curve C of genus g:

$$
h^0(L) - h^1(L) = \deg(L) + 1 - g
$$

**Reference**: Hartshorne GTM 52, Chapter IV, Section 1

### Interpretation

- **h⁰(L)**: Dimension of global sections (solutions to L = 0)
- **h¹(L)**: First cohomology dimension (obstructions)
- **deg(L)**: Degree of the line bundle
- **g**: Genus of the curve

### Examples

**P¹ (g = 0)**: For O(d) on P¹:
- If d ≥ 0: h⁰ = d + 1, h¹ = 0
- If d < 0: h⁰ = 0, h¹ = -d - 1

**Elliptic Curve (g = 1)**: For line bundle L of degree d:
- If d > 0: h⁰ = d, h¹ = 0
- If d = 0: h⁰ = 1, h¹ = 0
- If d < 0: h⁰ = 0, h¹ = -d

## Serre Duality

### Statement

For a line bundle L on a smooth projective curve C:

$$
h^1(L) \cong h^0(K \otimes L^{-1})^*
$$

where K is the canonical bundle and * denotes dual.

**Reference**: Hartshorne GTM 52, Chapter III, Section 7

### Canonical Bundle

The **canonical bundle** K is the bundle of differential 1-forms on C. Its degree is:

$$
\deg(K) = 2g - 2
$$

This formula is fundamental and used throughout the sampler for consistency checks.

## Curve Families

### P¹: Projective Line

**Definition**: P¹ is the simplest curve, isomorphic to the Riemann sphere.

**Properties**:
- Genus g = 0
- Canonical bundle K = O(-2)
- Line bundles O(d) have closed-form cohomology

**Cohomology**: For O(d) on P¹:
- h⁰(O(d)) = max(d + 1, 0)
- h¹(O(d)) = max(-d - 1, 0)

**Reference**: Stacks Project tag 01PZ

**Čech Verification**: The cohomology can be verified using Čech cohomology with the standard open cover U₀ = {z ≠ 0}, U₁ = {w ≠ 0}.

### Elliptic Curves

**Definition**: Elliptic curves are curves of genus 1 with a marked point.

**Standard Form**: y² = x³ + ax + b

**Discriminant**: Δ = -16(4a³ + 27b²)

**Smoothness**: The curve is smooth if and only if Δ ≠ 0

**Properties**:
- Genus g = 1 (fixed)
- Canonical bundle degree = 0
- Line bundle cohomology determined by degree

**Reference**: Silverman GTM 106, Chapter III

### Hyperelliptic Curves

**Definition**: Hyperelliptic curves are curves with a degree-2 map to P¹.

**Standard Form**: y² = f(x) where f(x) is a polynomial

**Genus Formula**: g = ⌊(deg(f) - 1)/2⌋

**Properties**:
- Genus determined by degree of f(x)
- Canonical bundle degree = 2g - 2
- Smoothness requires f(x) to be squarefree

**Reference**: Stacks Project tag 0A1M

### Plane Curves

**Definition**: Plane curves are defined by homogeneous polynomials F(x,y,z) = 0

**Genus Formula**: For smooth plane curves of degree d:
$$
g = \frac{(d-1)(d-2)}{2}
$$

**Properties**:
- Genus grows quadratically with degree
- Canonical bundle degree = 2g - 2
- Smoothness checked via Jacobian criterion

**Reference**: Stacks Project tag 01R5

## Sampling and Invariants

### Sampling Strategies

**Grid Sampling**: Systematic exploration of parameter space
- **Use case**: Small parameter ranges, complete coverage
- **Advantage**: Deterministic, reproducible
- **Disadvantage**: Exponential growth with dimensions

**Random Sampling**: Probabilistic exploration
- **Use case**: Large parameter spaces, statistical analysis
- **Advantage**: Scalable, good coverage
- **Disadvantage**: May miss specific regions

**Latin Hypercube Sampling (LHS)**: Quasi-random sampling
- **Use case**: Balanced exploration of parameter space
- **Advantage**: Better coverage than random, scalable
- **Disadvantage**: More complex implementation

### Computed Invariants

**Topological**:
- **genus**: Topological invariant of the curve
- **canonical_deg**: Degree of canonical bundle (2g - 2)

**Cohomological**:
- **h0**: Dimension of global sections
- **h1**: First cohomology dimension
- **degK**: Canonical bundle degree (alias for canonical_deg)

### Consistency Checks

The sampler automatically verifies mathematical consistency:

1. **Genus Consistency**: Canonical degree = 2g - 2
2. **Riemann-Roch**: h⁰(L) - h¹(L) = deg(L) + 1 - g
3. **Serre Duality**: h¹(L) = h⁰(K ⊗ L^(-1))

## Mathematical Foundation

### References and Citations

All mathematical statements in this sampler are grounded in trusted references:

- **Hartshorne GTM 52**: Classical algebraic geometry
- **Vakil FOAG**: Modern foundations and cohomology
- **Stacks Project**: Online reference with specific tags
- **Silverman GTM 106**: Elliptic curve theory

### Implementation Notes

- **Deterministic**: All random number generation uses explicit seeds
- **Reproducible**: Same parameters + seed = identical output
- **Validated**: Mathematical consistency automatically checked
- **Documented**: All algorithms documented with sources

### Limitations and Future Work

**Current Limitations**:
- Simplified smoothness checks for some curve types
- Basic sampling strategies (LHS implementation incomplete)
- Limited to characteristic 0 fields

**Future Improvements**:
- Advanced smoothness algorithms
- More sophisticated sampling strategies
- Support for finite fields
- Integration with computer algebra systems

## Examples and Verification

### P¹ Verification

For O(d) on P¹, we can verify the closed-form formulas using Čech cohomology:

**Open Cover**: U₀ = {z ≠ 0}, U₁ = {w ≠ 0}
**Transition Functions**: g₀₁ = (w/z)^d

**Cohomology Computation**:
- **H⁰**: Global sections that extend across both opens
- **H¹**: Cocycles modulo coboundaries

**Result**: Matches the closed-form formulas exactly.

### Elliptic Curve Verification

For elliptic curves, we verify:

1. **Discriminant**: Δ = -16(4a³ + 27b²) ≠ 0
2. **Genus**: Always g = 1
3. **Canonical Degree**: Always 0
4. **Riemann-Roch**: Verified for line bundles of various degrees

### Consistency Verification

The sampler automatically runs consistency checks:

```python
# Example consistency check
def verify_consistency(curve, line_bundle_degree):
    g = curve.genus()
    h0 = compute_h0(curve, line_bundle_degree)
    h1 = compute_h1(curve, line_bundle_degree)
    
    # Riemann-Roch
    left = h0 - h1
    right = line_bundle_degree + 1 - g
    assert left == right, f"Riemann-Roch failed: {left} != {right}"
    
    # Canonical degree
    canonical_deg = curve.canonical_degree()
    expected = 2 * g - 2
    assert canonical_deg == expected, f"Canonical degree failed: {canonical_deg} != {expected}"
```

## Conclusion

The Algebraic Moduli Sampler provides a mathematically sound, reproducible framework for exploring algebraic curve families. All algorithms are grounded in trusted references, with automatic consistency verification ensuring mathematical correctness.

The combination of deterministic sampling, thorough invariant computation, and thorough validation makes this tool suitable for both research and educational purposes in algebraic geometry.
