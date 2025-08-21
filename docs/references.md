# Mathematical References

This document provides the complete bibliography for the Algebraic Moduli Sampler, with all mathematical theorems, algorithms, and formulas grounded in trusted academic sources.

## Primary References

### Algebraic Geometry Fundamentals

**Hartshorne, Robin. Algebraic Geometry. Springer GTM 52, 1977.**
- **URL**: https://link.springer.com/book/10.1007/978-1-4757-3849-0
- **ISBN**: 978-1-4757-3849-0
- **Coverage**: Riemann-Roch theorem, Serre duality, canonical bundles, genus formulas
- **Key Theorems**: 
  - Riemann-Roch on curves: h⁰(L) - h¹(L) = deg(L) + 1 - g
  - Serre duality: h¹(L) ≅ h⁰(K ⊗ L⁻¹)*
  - Canonical bundle degree: deg(K) = 2g - 2

**Vakil, Ravi. The Rising Sea: Foundations of Algebraic Geometry. Stanford University, 2017.**
- **URL**: https://math.stanford.edu/~vakil/216blog/FOAGnov1817public.pdf
- **Coverage**: Modern treatment of cohomology, line bundles, and moduli spaces
- **Key Concepts**: Sheaf cohomology, Čech cohomology, line bundle operations

### Online References

**The Stacks Project.**
- **URL**: https://stacks.math.columbia.edu/
- **Coverage**: Comprehensive online reference for algebraic geometry
- **Key Tags**:
  - **01PZ**: Line bundles O(d) on Pⁿ and their cohomology
    - **URL**: https://stacks.math.columbia.edu/tag/01PZ
    - **Content**: h⁰(O(d)) = max(d+1, 0), h¹(O(d)) = max(-d-1, 0) on P¹
  - **01R5**: Genus formula for smooth plane curves
    - **URL**: https://stacks.math.columbia.edu/tag/01R5
    - **Content**: g = (d-1)(d-2)/2 for smooth plane curves of degree d
  - **01DW**: Čech cohomology basics
    - **URL**: https://stacks.math.columbia.edu/tag/01DW
    - **Content**: Čech cohomology with open covers
  - **0A1M**: Hyperelliptic curve basics
    - **URL**: https://stacks.math.columbia.edu/tag/0A1M
    - **Content**: Genus formulas and properties of hyperelliptic curves

### Elliptic Curves

**Silverman, Joseph H. The Arithmetic of Elliptic Curves. Springer GTM 106, 2009.**
- **URL**: https://link.springer.com/book/10.1007/978-0-387-09494-6
- **ISBN**: 978-0-387-09494-6
- **Coverage**: Elliptic curve theory, discriminant, smoothness conditions
- **Key Formulas**:
  - Discriminant: Δ = -16(4a³ + 27b²)
  - Smoothness: Δ ≠ 0 ensures smoothness
  - Genus: g = 1 for elliptic curves

**Wikipedia: Elliptic Curve.**
- **URL**: https://en.wikipedia.org/wiki/Elliptic_curve
- **Coverage**: Overview of elliptic curve theory and discriminant form
- **Key Content**: Standard form y² = x³ + ax + b and smoothness conditions

### Hyperelliptic Curves

**Stichtenoth, Henning. Algebraic Function Fields and Codes. Springer, 2009.**
- **URL**: https://link.springer.com/book/10.1007/978-3-662-06381-4
- **ISBN**: 978-3-662-06381-4
- **Coverage**: Function fields, hyperelliptic curves, genus formulas
- **Key Results**: Genus computation for y² = f(x) curves

## Mathematical Theorems and Formulas

### Riemann-Roch Theorem

**Statement**: For a line bundle L on a smooth projective curve C of genus g:
```
h⁰(L) - h¹(L) = deg(L) + 1 - g
```

**Reference**: Hartshorne GTM 52, Chapter IV, Section 1
**Proof**: Uses Čech cohomology and Serre duality

### Serre Duality

**Statement**: For a line bundle L on a smooth projective curve C:
```
h¹(L) ≅ h⁰(K ⊗ L⁻¹)*
```
where K is the canonical bundle.

**Reference**: Hartshorne GTM 52, Chapter III, Section 7
**Proof**: Uses derived category techniques and Grothendieck duality

### Genus Formulas

**Plane Curves**: For a smooth plane curve of degree d:
```
g = (d-1)(d-2)/2
```

**Reference**: Stacks Project tag 01R5
**Proof**: Uses adjunction formula and degree-genus formula

**Hyperelliptic Curves**: For y² = f(x) with deg(f) = 2g+1 or 2g+2:
```
g = ⌊(deg(f) - 1)/2⌋
```

**Reference**: Stacks Project tag 0A1M
**Proof**: Uses Riemann-Hurwitz formula

### Discriminant Formulas

**Elliptic Curves**: For y² = x³ + ax + b:
```
Δ = -16(4a³ + 27b²)
```

**Reference**: Silverman GTM 106, Chapter III
**Proof**: Uses elimination theory and resultant calculations

## Implementation Notes

### P¹ Line Bundles

The cohomology of O(d) on P¹ is implemented using the closed-form formulas from Stacks Project tag 01PZ:

- **h⁰(O(d))**: max(d+1, 0) for d ≥ -1, 0 otherwise
- **h¹(O(d))**: max(-d-1, 0) for d ≤ -1, 0 otherwise

These formulas are verified using Čech cohomology with the standard open cover U₀ = {z ≠ 0}, U₁ = {w ≠ 0}.

### Smoothness Checks

**Elliptic Curves**: Smoothness is verified by checking Δ ≠ 0
**Hyperelliptic Curves**: Basic smoothness check via squarefree polynomials
**Plane Curves**: Simplified smoothness check (placeholder for more sophisticated methods)

### Reproducibility

All random number generation uses numpy's RandomState with explicit seeds, ensuring:
- Deterministic output for given seed
- Cross-platform reproducibility
- Version-independent results

## Further Reading

### Advanced Topics

- **Moduli Spaces**: Mumford, GIT; Harris-Morrison, Moduli of Curves
- **Cohomology**: Grothendieck, ÉGA; Hartshorne, Residues and Duality
- **Computational Methods**: Decker-Schreyer, Varieties, Gröbner Bases and Algebraic Curves

### Online Resources

- **ArXiv**: https://arxiv.org/ (search for "algebraic geometry", "Riemann-Roch", "Serre duality")
- **MathSciNet**: https://mathscinet.ams.org/ (comprehensive mathematical literature database)
- **Zentralblatt**: https://zbmath.org/ (mathematical bibliography)

## Citation Guidelines

When using this software in academic work, please cite:

1. **Primary References**: Hartshorne GTM 52, Vakil FOAG, Stacks Project
2. **Software**: This Algebraic Moduli Sampler repository
3. **Mathematical Results**: Specific theorems and formulas with their references

## Contributing to References

If you find additional references that should be included, please:
1. Ensure they are from reputable academic sources
2. Provide complete bibliographic information
3. Include URLs when available
4. Specify which mathematical results they cover

---

*This bibliography is maintained as part of our commitment to mathematical soundness and thorough documentation.*
