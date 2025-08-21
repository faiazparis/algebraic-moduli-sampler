# Algebraic Moduli Sampler Documentation

Welcome to the **Algebraic Moduli Sampler**: A zero-cost, local-first, reproducible, and test-driven Python library for sampling algebraic curve families and computing sheaf-cohomology-based invariants.

## 🎯 Mission

**Build advanced math models for everyone**: A documented and reproducible pipeline to sample algebraic curve families and compute cohomological invariants.

## 🚀 Quick Start

```bash
# Install in development mode
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Validate parameters
moduli-sampler validate examples/small_params/p1_degree_linebundles.json

# Sample P^1 line bundles
moduli-sampler sample examples/small_params/p1_degree_linebundles.json --seed 42 --n 5 --out ./output

# Run complete pipeline
moduli-sampler pipeline examples/small_params/elliptic_small.json --seed 7 --n 10 --out ./pipeline_output
```

## 📚 Documentation Sections

### [Theory](theory.md)
Mathematical background and theorems with explicit citations to trusted references:
- Riemann-Roch theorem on curves
- Serre duality and cohomology
- Genus formulas for different curve families
- Discriminant conditions for smoothness

### [Design](design.md)
Architecture and reproducibility guarantees:
- Module boundaries and interfaces
- Deterministic random number generation
- Metadata capture and validation
- Mathematical consistency checks

### [Usage](usage.md)
End-to-end examples and workflows:
- Parameter file specifications
- CLI command reference
- Expected outputs and verification
- Troubleshooting guide

### [API](api.md)
Complete function and class documentation:
- Core geometry classes
- Sampling algorithms
- Invariant computations
- Utility functions

### [References](references.md)
Academic sources and URLs:
- Hartshorne, Algebraic Geometry (GTM 52)
- Vakil, FOAG (Stanford notes)
- Stacks Project (online reference)
- Silverman, The Arithmetic of Elliptic Curves (GTM 106)

## 🔬 Supported Curve Families

- **P¹**: Line bundles O(d) with closed-form cohomology
- **Elliptic Curves**: y² = x³ + ax + b with discriminant Δ ≠ 0
- **Hyperelliptic Curves**: y² = f(x) with squarefree f(x)
- **Plane Curves**: Homogeneous F(x,y,z) = 0 with smoothness checks

## 🧮 Mathematical Foundation

All algorithms are grounded in trusted references:

- **Riemann-Roch**: h⁰(L) - h¹(L) = deg(L) + 1 - g
- **Serre Duality**: h¹(L) ≅ h⁰(K ⊗ L⁻¹)*
- **Genus Formulas**: g = (d-1)(d-2)/2 for smooth plane curves of degree d
- **Discriminant**: Δ = -16(4a³ + 27b²) for elliptic curves

## 🛠️ Development

### Local Development Setup

```bash
# Install all dependencies
make setup

# Run all checks
make all

# Individual targets
make lint      # ruff + black + isort
make format    # black + isort
make typecheck # mypy
make test      # pytest with coverage
make docs      # mkdocs serve
```

### Test Coverage

We maintain **≥95% test coverage** across all modules:
- Unit tests for mathematical functions
- Property-based tests with Hypothesis
- Integration tests for CLI workflows
- Deterministic test outputs

## 🤝 Contributing

We welcome contributions! This project aims to build **advanced math models for everyone**.

**Areas for improvement:**
- Additional curve families (K3 surfaces, Calabi-Yau manifolds)
- More sophisticated sampling strategies (Latin hypercube, Sobol sequences)
- Performance optimizations for large parameter spaces
- Integration with computer algebra systems
- Educational examples and tutorials

**How to contribute:**
1. Fork the repository
2. Create a feature branch
3. Ensure `make all` passes locally
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

---

**Built with ❤️ for the algebraic geometry community**
