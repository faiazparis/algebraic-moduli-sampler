# API Reference

This document provides the complete API reference for the Algebraic Moduli Sampler, including all public functions, classes, and their usage.

## Package Overview

```python
import moduli_sampler
from moduli_sampler import Sampler, SamplingParams
from moduli_sampler.geometry import P1Curve, EllipticCurve, HyperellipticCurve, PlaneCurve
from moduli_sampler.geometry import compute_invariants
from moduli_sampler.io import load_params, save_results, save_metadata
from moduli_sampler.utils import setup_rng, get_metadata
```

## Core Classes

### SamplingParams

**Location**: `moduli_sampler.sampling.params_schema`

**Description**: Main parameter container for sampling configuration.

**Attributes**:
- `family_type`: Type of curve family ("P1", "Elliptic", "Hyperelliptic", "PlaneCurve")
- `constraints`: Mathematical constraints for the family
- `sampling`: Sampling strategy and parameters
- `invariants`: List of invariants to compute

**Example**:
```python
from moduli_sampler.sampling import SamplingParams

params = SamplingParams(
    family_type="P1",
    constraints={"degree": [-3, 5], "field": "Q"},
    sampling={"strategy": "grid", "n_samples_default": 9, "seed": 42},
    invariants={"compute": ["h0", "h1", "canonical_deg"]}
)
```

### Sampler

**Location**: `moduli_sampler.sampling.sampler`

**Description**: Main class for sampling curve families.

**Methods**:
- `__init__(params: SamplingParams)`: Initialize with parameters
- `sample_family(n_samples: Optional[int] = None)`: Sample curve family
- `save_family(family_data, output_dir)`: Save results to directory

**Example**:
```python
from moduli_sampler.sampling import Sampler

sampler = Sampler(params)
family = sampler.sample_family(n_samples=25)
sampler.save_family(family, "./output")
```

## Geometry Classes

### AlgebraicCurve (Abstract Base)

**Location**: `moduli_sampler.geometry.curves`

**Description**: Abstract base class for all algebraic curves.

**Abstract Methods**:
- `genus() -> int`: Compute genus
- `is_smooth() -> bool`: Check smoothness
- `canonical_degree() -> int`: Compute canonical bundle degree

**Concrete Methods**:
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

### P1Curve

**Location**: `moduli_sampler.geometry.curves`

**Description**: Line bundles O(d) on P¹.

**Constructor**: `P1Curve(degree: int)`

**Methods**:
- `genus() -> int`: Always returns 0
- `is_smooth() -> bool`: Always returns True
- `canonical_degree() -> int`: Always returns -2
- `h0() -> int`: Compute h⁰(O(d)) = max(d+1, 0)
- `h1() -> int`: Compute h¹(O(d)) = max(-d-1, 0)

**Example**:
```python
from moduli_sampler.geometry.curves import P1Curve

curve = P1Curve(degree=3)
print(f"Genus: {curve.genus()}")  # 0
print(f"h0: {curve.h0()}")        # 4
print(f"h1: {curve.h1()}")        # 0
```

### EllipticCurve

**Location**: `moduli_sampler.geometry.curves`

**Description**: Elliptic curves y² = x³ + ax + b.

**Constructor**: `EllipticCurve(a: int, b: int)`

**Methods**:
- `genus() -> int`: Always returns 1
- `is_smooth() -> bool`: Check via discriminant Δ ≠ 0
- `canonical_degree() -> int`: Always returns 0
- `discriminant() -> int`: Compute Δ = -16(4a³ + 27b²)

**Example**:
```python
from moduli_sampler.geometry.curves import EllipticCurve

curve = EllipticCurve(a=1, b=2)
print(f"Genus: {curve.genus()}")           # 1
print(f"Smooth: {curve.is_smooth()}")      # True (if Δ ≠ 0)
print(f"Discriminant: {curve.discriminant()}")
```

### HyperellipticCurve

**Location**: `moduli_sampler.geometry.curves`

**Description**: Hyperelliptic curves y² = f(x).

**Constructor**: `HyperellipticCurve(coefficients: List[int])`

**Methods**:
- `genus() -> int`: Compute from polynomial degree
- `is_smooth() -> bool`: Check if f(x) is squarefree
- `canonical_degree() -> int`: Compute 2g - 2
- `f_polynomial() -> sp.Poly`: Get SymPy polynomial

**Example**:
```python
from moduli_sampler.geometry.curves import HyperellipticCurve

# y² = x⁵ + 2x³ - x + 1 (genus 2)
curve = HyperellipticCurve([1, -1, 0, 2, 0, 1])
print(f"Genus: {curve.genus()}")           # 2
print(f"Canonical degree: {curve.canonical_degree()}")  # 2
```

### PlaneCurve

**Location**: `moduli_sampler.geometry.curves`

**Description**: Plane curves F(x,y,z) = 0.

**Constructor**: `PlaneCurve(degree: int, coefficients: Dict[str, int])`

**Methods**:
- `genus() -> int`: Compute (d-1)(d-2)/2
- `is_smooth() -> bool`: Simplified smoothness check
- `canonical_degree() -> int`: Compute 2g - 2
- `f_polynomial() -> sp.Expr`: Get SymPy expression

**Example**:
```python
from moduli_sampler.geometry.curves import PlaneCurve

# F(x,y,z) = x³ + y³ - 2z³
curve = PlaneCurve(3, {"x^3": 1, "y^3": 1, "z^3": -2})
print(f"Genus: {curve.genus()}")           # 1
print(f"Canonical degree: {curve.canonical_degree()}")  # 0
```

## Line Bundle Classes

### LineBundle (Abstract Base)

**Location**: `moduli_sampler.geometry.line_bundles`

**Description**: Abstract base class for line bundles.

**Abstract Methods**:
- `degree() -> int`: Compute line bundle degree

**Concrete Methods**:
- `euler_characteristic() -> int`: Compute χ(L) = deg(L) + 1 - g
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

### P1LineBundle

**Location**: `moduli_sampler.geometry.line_bundles`

**Description**: Line bundle O(d) on P¹.

**Constructor**: `P1LineBundle(degree: int)`

**Methods**:
- `degree() -> int`: Return degree d
- `h0() -> int`: Compute h⁰(O(d))
- `h1() -> int`: Compute h¹(O(d))

### EllipticLineBundle

**Location**: `moduli_sampler.geometry.line_bundles`

**Description**: Line bundle on elliptic curve.

**Constructor**: `EllipticLineBundle(curve: EllipticCurve, degree: int)`

**Methods**:
- `degree() -> int`: Return line bundle degree
- `h0() -> int`: Compute h⁰(L) using Riemann-Roch
- `h1() -> int`: Compute h¹(L) using Serre duality

## Cohomology Functions

### Core Functions

**Location**: `moduli_sampler.geometry.cohomology`

#### `compute_h0(curve: AlgebraicCurve, line_bundle_degree: int) -> int`

Compute h⁰(L) for line bundle L of given degree on curve.

**Parameters**:
- `curve`: Algebraic curve instance
- `line_bundle_degree`: Degree of the line bundle

**Returns**: Dimension of global sections

**Example**:
```python
from moduli_sampler.geometry.cohomology import compute_h0
from moduli_sampler.geometry.curves import P1Curve

curve = P1Curve(degree=0)
h0 = compute_h0(curve, line_bundle_degree=3)
print(f"h0(O(3)) on P1: {h0}")  # 4
```

#### `compute_h1(curve: AlgebraicCurve, line_bundle_degree: int) -> int`

Compute h¹(L) for line bundle L of given degree on curve.

**Parameters**:
- `curve`: Algebraic curve instance
- `line_bundle_degree`: Degree of the line bundle

**Returns**: First cohomology dimension

**Example**:
```python
from moduli_sampler.geometry.cohomology import compute_h1

h1 = compute_h1(curve, line_bundle_degree=-2)
print(f"h1(O(-2)) on P1: {h1}")  # 1
```

### Verification Functions

#### `riemann_roch_check(curve: AlgebraicCurve, line_bundle_degree: int) -> Dict[str, Union[int, bool]]`

Verify Riemann-Roch theorem for a line bundle.

**Returns**: Dictionary with verification results

**Example**:
```python
from moduli_sampler.geometry.cohomology import riemann_roch_check

result = riemann_roch_check(curve, line_bundle_degree=2)
print(f"Riemann-Roch satisfied: {result['riemann_roch_satisfied']}")
print(f"Left side: {result['left_side']}")
print(f"Right side: {result['right_side']}")
```

#### `serre_duality_check(curve: AlgebraicCurve, line_bundle_degree: int) -> Dict[str, Union[int, bool]]`

Verify Serre duality for a line bundle.

**Returns**: Dictionary with verification results

**Example**:
```python
from moduli_sampler.geometry.cohomology import serre_duality_check

result = serre_duality_check(curve, line_bundle_degree=1)
print(f"Serre duality satisfied: {result['serre_duality_satisfied']}")
```

#### `p1_cech_verification(degree: int) -> Dict[str, Union[int, bool]]`

Verify P¹ cohomology using Čech cohomology.

**Parameters**:
- `degree`: Degree of the line bundle O(d)

**Returns**: Dictionary with Čech computation results

**Example**:
```python
from moduli_sampler.geometry.cohomology import p1_cech_verification

result = p1_cech_verification(degree=-3)
print(f"Čech verification passed: {result['cech_verification_passed']}")
```

## Invariant Functions

### Core Functions

**Location**: `moduli_sampler.geometry.invariants`

#### `compute_invariants(curve: AlgebraicCurve, requested_invariants: List[str], line_bundle_degree: int = 0) -> Dict[str, Union[int, bool, str]]`

Compute requested invariants for an algebraic curve.

**Parameters**:
- `curve`: Algebraic curve instance
- `requested_invariants`: List of invariant names to compute
- `line_bundle_degree`: Degree of line bundle for h0/h1 computations

**Returns**: Dictionary mapping invariant names to computed values

**Example**:
```python
from moduli_sampler.geometry.invariants import compute_invariants

invariants = compute_invariants(
    curve, 
    ["genus", "h0", "h1"], 
    line_bundle_degree=2
)
print(f"Genus: {invariants['genus']}")
print(f"h0: {invariants['h0']}")
print(f"h1: {invariants['h1']}")
```

### Family Functions

#### `compute_p1_family_invariants(degree_range: tuple[int, int], requested_invariants: List[str]) -> List[Dict[str, Union[int, bool, str]]]`

Compute invariants for P¹ family with line bundles O(d).

**Parameters**:
- `degree_range`: Tuple (min_degree, max_degree)
- `requested_invariants`: List of invariant names to compute

**Returns**: List of dictionaries with invariants for each degree

**Example**:
```python
from moduli_sampler.geometry.invariants import compute_p1_family_invariants

family = compute_p1_family_invariants(
    degree_range=(-2, 2),
    requested_invariants=["h0", "h1", "canonical_deg"]
)

for curve_data in family:
    print(f"Degree {curve_data['degree']}: h0={curve_data['h0']}, h1={curve_data['h1']}")
```

#### `compute_elliptic_family_invariants(coefficient_pairs: List[tuple[int, int]], requested_invariants: List[str], line_bundle_degree: int = 0) -> List[Dict[str, Union[int, bool, str]]]`

Compute invariants for elliptic curve family.

**Parameters**:
- `coefficient_pairs`: List of (a, b) pairs for y² = x³ + ax + b
- `requested_invariants`: List of invariant names to compute
- `line_bundle_degree`: Degree of line bundle for h0/h1 computations

**Returns**: List of dictionaries with invariants for each curve

**Example**:
```python
from moduli_sampler.geometry.invariants import compute_elliptic_family_invariants

coefficients = [(1, 2), (2, 3), (3, 1)]
family = compute_elliptic_family_invariants(
    coefficients,
    ["genus", "h0", "h1"],
    line_bundle_degree=2
)

for curve_data in family:
    print(f"a={curve_data['a']}, b={curve_data['b']}: genus={curve_data['genus']}")
```

### Summary Functions

#### `summarize_family_invariants(family_invariants: List[Dict[str, Union[int, bool, str]]]) -> Dict[str, Any]`

Compute summary statistics for a family of curves.

**Returns**: Dictionary with summary statistics

**Example**:
```python
from moduli_sampler.geometry.invariants import summarize_family_invariants

summary = summarize_family_invariants(family)
print(f"Total curves: {summary['total_curves']}")
print(f"Smooth curves: {summary['smooth_curves']}")
print(f"Genus range: {summary['genus_min']} to {summary['genus_max']}")
```

#### `validate_invariants_consistency(family_invariants: List[Dict[str, Union[int, bool, str]]]) -> Dict[str, Any]`

Validate consistency of computed invariants.

**Returns**: Dictionary with validation results

**Example**:
```python
from moduli_sampler.geometry.invariants import validate_invariants_consistency

consistency = validate_invariants_consistency(family)
if consistency['validation_errors']:
    print(f"Found {len(consistency['validation_errors'])} validation errors")
else:
    print("All consistency checks passed")
```

## I/O Functions

### JSON I/O

**Location**: `moduli_sampler.io.json_io`

#### `load_json(file_path: Union[str, Path]) -> Union[Dict[str, Any], List[Any]]`

Load JSON data from a file.

**Parameters**:
- `file_path`: Path to JSON file

**Returns**: Loaded JSON data

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `json.JSONDecodeError`: If file contains invalid JSON

**Example**:
```python
from moduli_sampler.io.json_io import load_json

data = load_json("params.json")
print(f"Family type: {data['family_type']}")
```

#### `save_json(data: Union[Dict[str, Any], List[Any]], file_path: Union[str, Path], indent: int = 2, ensure_ascii: bool = False) -> None`

Save data to a JSON file.

**Parameters**:
- `data`: Data to save
- `file_path`: Path to output file
- `indent`: JSON indentation
- `ensure_ascii`: Whether to escape non-ASCII characters

**Example**:
```python
from moduli_sampler.io.json_io import save_json

results = {"status": "success", "count": 42}
save_json(results, "results.json")
```

### Metadata Functions

**Location**: `moduli_sampler.io.metadata`

#### `get_metadata(command: str, **kwargs) -> Dict[str, Any]`

Generate comprehensive metadata for a run.

**Parameters**:
- `command`: CLI command that was run
- `**kwargs`: Additional metadata to include

**Returns**: Dictionary with complete metadata

**Example**:
```python
from moduli_sampler.io.metadata import get_metadata

metadata = get_metadata(
    command="sample",
    params_file="params.json",
    seed=42,
    n_samples=25,
    family_type="P1"
)
```

#### `save_metadata(metadata: Dict[str, Any], output_file: Path) -> None`

Save metadata to a JSON file with human-readable summary.

**Parameters**:
- `metadata`: Metadata dictionary to save
- `output_file`: Path to output file

**Example**:
```python
from moduli_sampler.io.metadata import save_metadata
from pathlib import Path

save_metadata(metadata, Path("./output/metadata.json"))
```

## Utility Functions

### RNG Management

**Location**: `moduli_sampler.utils.seed`

#### `setup_rng(seed: int) -> np.random.RandomState`

Setup deterministic random number generator.

**Parameters**:
- `seed`: Integer seed for the RNG

**Returns**: Configured numpy RandomState object

**Example**:
```python
from moduli_sampler.utils.seed import setup_rng

rng = setup_rng(seed=42)
random_numbers = rng.randint(0, 100, size=10)
```

#### `get_seed_info(seed: int) -> dict`

Get information about the current seed and environment.

**Returns**: Dictionary with seed and environment information

**Example**:
```python
from moduli_sampler.utils.seed import get_seed_info

info = get_seed_info(seed=42)
print(f"Platform: {info['platform']}")
print(f"Python: {info['python_version']}")
```

### Validation Functions

**Location**: `moduli_sampler.utils.validation`

#### `validate_file_path(file_path: Union[str, Path]) -> Path`

Validate that a file path exists and is a file.

**Parameters**:
- `file_path`: Path to validate

**Returns**: Validated Path object

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If path is not a file

**Example**:
```python
from moduli_sampler.utils.validation import validate_file_path

path = validate_file_path("params.json")
print(f"Valid file: {path}")
```

#### `validate_output_dir(output_dir: Union[str, Path], create: bool = True) -> Path`

Validate and optionally create an output directory.

**Parameters**:
- `output_dir`: Directory path to validate
- `create`: Whether to create the directory if it doesn't exist

**Returns**: Validated Path object

**Example**:
```python
from moduli_sampler.utils.validation import validate_output_dir

output_path = validate_output_dir("./results", create=True)
print(f"Output directory: {output_path}")
```

### Logging Functions

**Location**: `moduli_sampler.utils.logging`

#### `setup_logging(level: int = logging.INFO, log_file: Optional[Path] = None, console_output: bool = True) -> logging.Logger`

Setup logging configuration for the moduli sampler.

**Parameters**:
- `level`: Logging level
- `log_file`: Optional file path for logging output
- `console_output`: Whether to output to console

**Returns**: Configured logger instance

**Example**:
```python
from moduli_sampler.utils.logging import setup_logging
from pathlib import Path

logger = setup_logging(
    level=logging.DEBUG,
    log_file=Path("./debug.log"),
    console_output=True
)
logger.info("Logging setup complete")
```

## Error Handling

### Common Exceptions

**ValidationError**: Raised when parameter validation fails
**FileNotFoundError**: Raised when input files don't exist
**ValueError**: Raised for mathematical inconsistencies
**RuntimeError**: Raised for sampling failures

### Error Recovery

```python
try:
    sampler = Sampler(params)
    family = sampler.sample_family(n_samples=25)
except ValidationError as e:
    print(f"Parameter validation failed: {e}")
    # Fix parameter file and retry
except FileNotFoundError as e:
    print(f"File not found: {e}")
    # Check file paths and permissions
except ValueError as e:
    print(f"Mathematical error: {e}")
    # Review mathematical constraints
```

## Performance Considerations

### Memory Usage

- **Large Families**: Use streaming for very large families
- **Coefficient Ranges**: Keep ranges reasonable to avoid excessive memory
- **Invariant Computation**: Compute only needed invariants

### Computation Time

- **P¹ Curves**: O(1) per curve (closed-form formulas)
- **Elliptic Curves**: O(1) per curve (discriminant check)
- **Hyperelliptic Curves**: O(deg(f)) per curve (polynomial operations)
- **Plane Curves**: O(d²) per curve (genus computation)

### Optimization Tips

- **Batch Processing**: Process multiple families together
- **Caching**: Reuse computed values when possible
- **Parallel Processing**: Use multiprocessing for independent curves

## Extension Points

### Adding New Curve Families

1. Inherit from `AlgebraicCurve`
2. Implement required methods
3. Add family-specific line bundle class
4. Update parameter schema validation
5. Add tests and documentation

### Adding New Invariants

1. Add to invariant schema
2. Implement computation function
3. Update consistency validation
4. Add property-based tests

### Adding New Sampling Strategies

1. Implement strategy interface
2. Add to strategy selection logic
3. Update parameter schema
4. Add strategy-specific tests

---

*This API reference covers all public functions and classes. For implementation details and internal APIs, see the source code.*
