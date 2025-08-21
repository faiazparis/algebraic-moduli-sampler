# Usage Guide

This document provides detailed usage instructions for the Algebraic Moduli Sampler, including examples, workflows, and troubleshooting.

## Installation

### Development Installation

```bash
# Clone the repository
git clone https://github.com/faiazparis/algebraic-moduli-sampler.git
cd algebraic-moduli-sampler

# Install in development mode
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### Production Installation

```bash
# Install from PyPI (when available)
pip install moduli-sampler

# Or install from source
pip install .
```

## Quick Start

### 1. Validate Parameters

First, validate your parameter file:

```bash
moduli-sampler validate examples/small_params/p1_degree_linebundles.json
```

**Current Status**: CLI validation working for core schemas
**Mathematical Foundation**: All parameter validation grounded in [theory.md](theory.md)
```
✓ Parameters valid! (when implemented)
Family type: P1  
Sampling strategy: grid
Default samples: 9
Seed: 42
Invariants: h0, h1, canonical_deg
```

### 2. Sample a Curve Family

Generate a family of curves:

```bash
moduli-sampler sample examples/small_params/p1_degree_linebundles.json --seed 42 --n 5 --out ./output
```

**Current Status**: Mathematical core implemented, CLI integration in progress
**Mathematical Verification**: All cohomology computations verified per [references.md](references.md)
```
✓ Sampling complete! (when implemented)
Generated 5 curves
Family data: ./output/family.json  
Metadata: ./output/metadata.json
```

### 3. Run Complete Pipeline

For convenience, run sampling and invariant computation together:

```bash
moduli-sampler pipeline examples/small_params/elliptic_small.json --seed 7 --n 10 --out ./pipeline_output
```

## Parameter File Format

### Basic Structure

All parameter files follow this JSON structure:

```json
{
  "family_type": "CurveFamily",
  "constraints": {
    "field": "Q",
    "smoothness_check": true
  },
  "sampling": {
    "strategy": "random",
    "n_samples_default": 25,
    "seed": 42
  },
  "invariants": {
    "compute": ["genus", "h0", "h1", "degK"]
  }
}
```

### Supported Curve Families

#### P¹ Line Bundles

```json
{
  "family_type": "P1",
  "constraints": {
    "degree": [-3, 5],
    "field": "Q",
    "smoothness_check": true
  },
  "sampling": {
    "strategy": "grid",
    "n_samples_default": 9,
    "seed": 42
  },
  "invariants": {
    "compute": ["h0", "h1", "canonical_deg"]
  }
}
```

**Notes**:
- `degree` can be a single integer or range [min, max]
- P¹ always has genus 0 and canonical degree -2
- Smoothness check is always true for P¹

#### Elliptic Curves

```json
{
  "family_type": "Elliptic",
  "constraints": {
    "coefficient_ranges": {
      "a": [-3, 3],
      "b": [-3, 3]
    },
    "field": "Q",
    "smoothness_check": true
  },
  "sampling": {
    "strategy": "random",
    "n_samples_default": 25,
    "seed": 7
  },
  "invariants": {
    "compute": ["genus", "h0", "h1", "degK"]
  }
}
```

**Notes**:
- `coefficient_ranges` must specify ranges for `a` and `b`
- Genus is always 1 for elliptic curves
- Canonical degree is always 0
- Smoothness checked via discriminant Δ ≠ 0

#### Hyperelliptic Curves

```json
{
  "family_type": "Hyperelliptic",
  "constraints": {
    "genus": 2,
    "coefficient_ranges": {
      "a0": [-2, 2],
      "a1": [-2, 2],
      "a2": [-2, 2],
      "a3": [-2, 2],
      "a4": [-2, 2],
      "a5": [-2, 2],
      "a6": [-2, 2]
    },
    "field": "Q",
    "smoothness_check": true
  },
  "sampling": {
    "strategy": "random",
    "n_samples_default": 20,
    "seed": 11
  },
  "invariants": {
    "compute": ["genus", "degK", "h0", "h1"]
  }
}
```

**Notes**:
- `genus` must be specified
- Polynomial degree will be 2g+1 or 2g+2
- Coefficient ranges should cover all polynomial terms
- Smoothness checked via squarefree polynomials

#### Plane Curves

```json
{
  "family_type": "PlaneCurve",
  "constraints": {
    "degree": 3,
    "coefficient_ranges": {
      "x^3": [-2, 2],
      "y^3": [-2, 2],
      "z^3": [-2, 2]
    },
    "field": "Q",
    "smoothness_check": true
  },
  "sampling": {
    "strategy": "random",
    "n_samples_default": 15,
    "seed": 23
  },
  "invariants": {
    "compute": ["genus", "degK", "h0", "h1"]
  }
}
```

**Notes**:
- `degree` must be specified
- Genus computed as (d-1)(d-2)/2
- Coefficient ranges for monomials
- Smoothness check is simplified (placeholder)

### Sampling Strategies

#### Grid Sampling

```json
{
  "sampling": {
    "strategy": "grid",
    "n_samples_default": 16,
    "seed": 42
  }
}
```

**Use Case**: Small parameter ranges, complete coverage
**Behavior**: Systematic exploration of parameter space
**Limitation**: Exponential growth with dimensions

#### Random Sampling

```json
{
  "sampling": {
    "strategy": "random",
    "n_samples_default": 100,
    "seed": 42
  }
}
```

**Use Case**: Large parameter spaces, statistical analysis
**Behavior**: Probabilistic exploration with seed control
**Advantage**: Scalable, good coverage

#### Latin Hypercube Sampling (LHS)

```json
{
  "sampling": {
    "strategy": "lhs",
    "n_samples_default": 50,
    "seed": 42
  }
}
```

**Use Case**: Balanced exploration of parameter space
**Behavior**: Quasi-random sampling for better coverage
**Status**: Currently simplified implementation

### Available Invariants

**Topological**:
- `genus`: Topological invariant of the curve
- `canonical_deg`: Degree of canonical bundle (2g - 2)

**Cohomological**:
- `h0`: Dimension of global sections
- `h1`: First cohomology dimension
- `degK`: Canonical bundle degree (alias for canonical_deg)

## CLI Commands

### validate

Validate a parameter file against the schema:

```bash
moduli-sampler validate <params.json>
```

**Options**:
- No additional options
- Exits with error code 1 if validation fails

**Use Cases**:
- Pre-flight parameter checking
- CI/CD validation
- Debugging parameter files

### sample

Sample a curve family based on parameters:

```bash
moduli-sampler sample <params.json> [OPTIONS]
```

**Options**:
- `--seed <int>`: Override random seed
- `--n <int>`: Number of samples to generate
- `--out <dir>`: Output directory (default: ./output)

**Examples**:
```bash
# Basic sampling
moduli-sampler sample params.json

# Override seed and sample count
moduli-sampler sample params.json --seed 123 --n 50

# Specify output directory
moduli-sampler sample params.json --out ./my_results
```

### invariants

Compute invariants for an existing family:

```bash
moduli-sampler invariants <family.json> [OPTIONS]
```

**Options**:
- `--out <file>`: Output file (default: ./invariants.json)

**Use Cases**:
- Recompute invariants with different parameters
- Validate existing results
- Extract specific invariant subsets

### pipeline

Run complete sampling and invariant computation:

```bash
moduli-sampler pipeline <params.json> [OPTIONS]
```

**Options**:
- `--seed <int>`: Override random seed
- `--n <int>`: Number of samples to generate
- `--out <dir>`: Output directory (default: ./pipeline_output)

**Advantages**:
- Single command for complete workflow
- Automatic consistency validation
- Complete metadata capture

## Output Structure

### Family Data (`family.json`)

```json
[
  {
    "type": "P1Curve",
    "genus": 0,
    "canonical_degree": -2,
    "is_smooth": true,
    "degree": -3,
    "h0": 0,
    "h1": 2,
    "sampling_strategy": "grid",
    "seed": 42
  },
  {
    "type": "P1Curve",
    "genus": 0,
    "canonical_degree": -2,
    "is_smooth": true,
    "degree": -2,
    "h0": 0,
    "h1": 1,
    "sampling_strategy": "grid",
    "seed": 42
  }
]
```

### Metadata (`metadata.json`)

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "command": "sample",
  "params_file": "examples/small_params/p1_degree_linebundles.json",
  "seed": 42,
  "n_samples": 5,
  "family_type": "P1",
  "sampling_strategy": "grid",
  "invariants_computed": ["h0", "h1", "canonical_deg"],
  "environment": {
    "python_version": "3.11.0",
    "platform": "macOS-14.2.0-x86_64",
    "numpy_version": "1.24.0"
  },
  "git_info": {
    "commit_hash": "a1b2c3d4e5f6",
    "branch": "main",
    "working_directory_clean": true
  }
}
```

### Metadata Summary (`metadata_summary.txt`)

```
Algebraic Moduli Sampler - Run Metadata
==================================================

Timestamp: 2024-01-15T10:30:00.123456
Command: sample
Family Type: P1
Seed: 42
Samples: 5
Strategy: grid

Git Commit: a1b2c3d
Git Branch: main
Working Directory Clean: true

Environment:
  Python: 3.11.0
  Platform: macOS-14.2.0-x86_64
  NumPy: 1.24.0

Parameters Hash: abc123def456...
```

## Expected Outputs

### P¹ Line Bundles

**Input**: Degree range [-3, 5]
**Expected Output**:
- 9 curves with degrees -3, -2, -1, 0, 1, 2, 3, 4, 5
- h⁰(O(d)) = max(d+1, 0)
- h¹(O(d)) = max(-d-1, 0)
- Canonical degree = -2 (fixed)

**Mathematical Verification**:
- Riemann-Roch: h⁰ - h¹ = d + 1 - 0 = d + 1 ✓
- Serre duality: h¹ = h⁰(K ⊗ O(d)^(-1)) ✓

### Elliptic Curves

**Input**: a ∈ [-3, 3], b ∈ [-3, 3]
**Expected Output**:
- Up to 25 smooth elliptic curves
- Genus = 1 (fixed)
- Canonical degree = 0 (fixed)
- Smoothness via Δ ≠ 0

**Mathematical Verification**:
- Discriminant Δ = -16(4a³ + 27b²) ≠ 0 ✓
- Genus consistency: g = 1 ✓
- Canonical degree: 2g - 2 = 0 ✓

### Hyperelliptic Curves (Genus 2)

**Input**: Genus 2, coefficients in [-2, 2]
**Expected Output**:
- Up to 20 curves with deg(f) = 5
- Genus = 2 (as specified)
- Canonical degree = 2
- Smoothness via squarefree f(x)

**Mathematical Verification**:
- Genus formula: g = ⌊(5-1)/2⌋ = 2 ✓
- Canonical degree: 2g - 2 = 2 ✓
- Polynomial smoothness ✓

## Troubleshooting

### Common Issues

#### Validation Errors

**Problem**: Parameter file validation fails
**Solutions**:
- Check JSON syntax
- Verify required fields are present
- Ensure family-specific constraints are met
- Check coefficient range formats

**Example Error**:
```
Parameter validation failed at constraints.degree: -5 is less than the minimum of 0
```

**Fix**: Ensure degree is non-negative for plane curves.

#### Sampling Failures

**Problem**: Sampling produces fewer curves than expected
**Solutions**:
- Check smoothness constraints
- Verify coefficient ranges are reasonable
- Increase max_attempts for complex families
- Use grid sampling for small ranges

**Example**: Elliptic curves with very small coefficient ranges may have limited smooth options.

#### Mathematical Inconsistencies

**Problem**: Consistency checks fail
**Solutions**:
- Verify parameter file is correct
- Check for edge cases in constraints
- Ensure smoothness conditions are appropriate
- Review mathematical assumptions

### Debug Mode

Enable verbose output for debugging:

```bash
# Set environment variable
export MODULI_SAMPLER_DEBUG=1

# Run command
moduli-sampler sample params.json --seed 42 --n 5 --out ./debug_output
```

### Log Files

Check generated log files for detailed information:
- `metadata.json`: Complete run information
- `metadata_summary.txt`: Human-readable summary
- Console output: Real-time progress and errors

## Advanced Usage

### Custom Parameter Files

Create your own parameter files:

```json
{
  "family_type": "Elliptic",
  "constraints": {
    "coefficient_ranges": {
      "a": [-10, 10],
      "b": [-10, 10]
    },
    "field": "Q",
    "smoothness_check": true
  },
  "sampling": {
    "strategy": "random",
    "n_samples_default": 100,
    "seed": 12345
  },
  "invariants": {
    "compute": ["genus", "h0", "h1", "degK"]
  }
}
```

### Batch Processing

Process multiple parameter files:

```bash
#!/bin/bash
for params in params/*.json; do
    echo "Processing $params"
    moduli-sampler pipeline "$params" --seed 42 --n 50 --out "./output/$(basename "$params" .json)"
done
```

### Integration with Other Tools

**Jupyter Notebooks**:
```python
from moduli_sampler import Sampler, load_params_from_file

# Load parameters
params = load_params_from_file("params.json")

# Create sampler
sampler = Sampler(params)

# Sample family
family = sampler.sample_family(n_samples=25)

# Analyze results
for curve in family:
    print(f"Genus: {curve['genus']}, h0: {curve['h0']}, h1: {curve['h1']}")
```

**Python Scripts**:
```python
from moduli_sampler.geometry import compute_invariants
from moduli_sampler.geometry.curves import EllipticCurve

# Create curve
curve = EllipticCurve(a=1, b=2)

# Compute invariants
invariants = compute_invariants(curve, ["genus", "h0", "h1"], line_bundle_degree=3)
print(invariants)
```

## Performance Tips

### Sampling Strategy Selection

- **Grid**: Use for small ranges (≤ 3 dimensions, ≤ 100 total points)
- **Random**: Use for large ranges or statistical analysis
- **LHS**: Use for balanced exploration (when implemented)

### Parameter Optimization

- **Coefficient Ranges**: Keep ranges reasonable to avoid excessive smoothness failures
- **Sample Counts**: Start small and increase as needed
- **Smoothness Checks**: Disable for faster sampling if not needed

### Output Management

- **Output Directories**: Use descriptive names for different runs
- **Metadata**: Always save metadata for reproducibility
- **File Organization**: Group related runs in subdirectories

## Next Steps

### Explore Examples

1. **Start Simple**: Begin with P¹ line bundles
2. **Progress Gradually**: Move to elliptic curves, then hyperelliptic
3. **Experiment**: Try different sampling strategies and parameters
4. **Validate**: Use consistency checks to verify results

### Extend Functionality

1. **New Curve Families**: Implement additional curve types
2. **Custom Invariants**: Add new mathematical invariants
3. **Sampling Strategies**: Implement LHS or other advanced methods
4. **Integration**: Connect with computer algebra systems

### Contribute

1. **Report Issues**: Use GitHub issues for bugs and feature requests
2. **Submit PRs**: Contribute improvements and new features
3. **Documentation**: Help improve guides and examples
4. **Testing**: Add tests for edge cases and new functionality

---

*This usage guide covers the essential functionality. For advanced features and API details, see the [API Documentation](api.md).*
