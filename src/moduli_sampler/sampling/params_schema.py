"""Parameter schema and validation for algebraic curve sampling.

This module defines the JSON schema for input parameters and provides
validation functions. All constraints are mathematically grounded in
trusted references.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import jsonschema
from pydantic import BaseModel, Field, field_validator


class CoefficientRanges(BaseModel):
    """Coefficient ranges for polynomial parameters.
    
    Each coefficient is constrained to lie within [min, max].
    """
    model_config = {
        "extra": "allow"  # Allow arbitrary coefficient names
    }
    
    # Define common coefficient fields with defaults
    a: Optional[List[int]] = Field(None, description="Coefficient a range [min, max]")
    b: Optional[List[int]] = Field(None, description="Coefficient b range [min, max]")
    a0: Optional[List[int]] = Field(None, description="Coefficient a0 range [min, max]")
    a1: Optional[List[int]] = Field(None, description="Coefficient a1 range [min, max]")
    a2: Optional[List[int]] = Field(None, description="Coefficient a2 range [min, max]")
    a3: Optional[List[int]] = Field(None, description="Coefficient a3 range [min, max]")
    a4: Optional[List[int]] = Field(None, description="Coefficient a4 range [min, max]")
    a5: Optional[List[int]] = Field(None, description="Coefficient a5 range [min, max]")
    a6: Optional[List[int]] = Field(None, description="Coefficient a6 range [min, max]")
    a7: Optional[List[int]] = Field(None, description="Coefficient a7 range [min, max]")
    x3: Optional[List[int]] = Field(None, description="Coefficient x^3 range [min, max]")
    y3: Optional[List[int]] = Field(None, description="Coefficient y^3 range [min, max]")
    z3: Optional[List[int]] = Field(None, description="Coefficient z^3 range [min, max]")
    x4: Optional[List[int]] = Field(None, description="Coefficient x^4 range [min, max]")
    y4: Optional[List[int]] = Field(None, description="Coefficient y^4 range [min, max]")
    z4: Optional[List[int]] = Field(None, description="Coefficient z^4 range [min, max]")
    
    def __getitem__(self, key: str) -> Optional[List[int]]:
        return getattr(self, key, None)
    
    def __iter__(self):
        # Return only non-None coefficients
        return iter({k: v for k, v in self.model_dump().items() if v is not None})
    
    def items(self):
        # Return only non-None coefficients
        return {k: v for k, v in self.model_dump().items() if v is not None}.items()
    
    def keys(self):
        # Return only non-None coefficients
        return {k: v for k, v in self.model_dump().items() if v is not None}.keys()
    
    def values(self):
        # Return only non-None coefficients
        return {k: v for k, v in self.model_dump().items() if v is not None}.values()
    
    def __len__(self):
        # Return count of non-None coefficients
        return len({k: v for k, v in self.model_dump().items() if v is not None})


class Constraints(BaseModel):
    """Mathematical constraints for curve families.
    
    All constraints are mathematically grounded in trusted references:
    - Hartshorne, Algebraic Geometry (GTM 52)
    - Vakil, FOAG
    - Stacks Project
    """
    genus: Optional[int] = Field(
        None,
        ge=0,
        description="Genus constraint (optional for some families)",
        json_schema_extra={"example": 2},
    )
    degree: Optional[int] = Field(
        None,
        description="Degree constraint (line bundle or plane curve degree)",
        json_schema_extra={"example": 3},
    )
    coefficient_ranges: Optional[CoefficientRanges] = Field(
        None,
        description="Ranges for polynomial coefficients",
    )
    field: Literal["Q", "R", "C", "Fp"] = Field(
        "Q",
        description="Base field for computations",
        json_schema_extra={"example": "Q"},
    )
    smoothness_check: bool = Field(
        True,
        description="Whether to check smoothness conditions",
        json_schema_extra={"example": True},
    )

    @field_validator("genus")
    @classmethod
    def validate_genus(cls, v):
        if v is not None and v < 0:
            raise ValueError("Genus must be non-negative")
        return v

    @field_validator("degree")
    @classmethod
    def validate_degree(cls, v):
        if v is not None and v < 0:
            raise ValueError("Degree must be non-negative")
        return v


class Sampling(BaseModel):
    """Sampling strategy and parameters.
    
    Ensures deterministic, reproducible sampling through seeded RNG.
    """
    n_samples_default: int = Field(
        ...,
        gt=0,
        le=10000,
        description="Default number of samples to generate",
        json_schema_extra={"example": 25},
    )
    seed: int = Field(
        ...,
        description="Random seed for reproducible sampling",
        json_schema_extra={"example": 42},
    )
    strategy: Literal["grid", "random", "lhs"] = Field(
        "random",
        description="Sampling strategy: grid, random, or Latin hypercube",
        json_schema_extra={"example": "random"},
    )


class Invariants(BaseModel):
    """Invariants to compute for each curve.
    
    All invariants are mathematically well-defined and computable:
    - genus: topological invariant
    - degK: canonical degree
    - h0, h1: sheaf cohomology dimensions
    - canonical_deg: degree of canonical bundle
    """
    compute: List[Literal["genus", "degK", "h0", "h1", "canonical_deg"]] = Field(
        ...,
        description="List of invariants to compute",
        min_length=1,
        json_schema_extra={"example": ["genus", "h0", "h1"]},
    )


class SamplingParams(BaseModel):
    """Complete parameter specification for algebraic curve sampling.
    
    This schema supports four main curve families:
    1. P1: Line bundles O(d) on P^1 with closed-form cohomology
    2. Elliptic: y^2 = x^3 + ax + b with discriminant Δ ≠ 0
    3. Hyperelliptic: y^2 = f(x) with squarefree f(x)
    4. PlaneCurve: Homogeneous F(x,y,z) = 0 with smoothness checks
    
    Mathematical grounding:
    - P1: Stacks Project tag 01PZ for O(d) cohomology
    - Elliptic: Silverman GTM 106 for discriminant and smoothness
    - Hyperelliptic: Stacks tag 0A1M for genus formulas
    - Plane curves: Stacks tag 01R5 for genus formula
    """
    family_type: Literal["P1", "Elliptic", "Hyperelliptic", "PlaneCurve"] = Field(
        ...,
        description="Type of algebraic curve family to sample",
        json_schema_extra={"example": "Elliptic"},
    )
    constraints: Constraints = Field(
        ...,
        description="Mathematical constraints for the curve family",
    )
    sampling: Sampling = Field(
        ...,
        description="Sampling strategy and parameters",
    )
    invariants: Invariants = Field(
        ...,
        description="Invariants to compute for each curve",
    )

    @field_validator("constraints")
    @classmethod
    def validate_family_constraints(cls, v, info):
        """Validate family-specific constraints."""
        family_type = info.data.get("family_type")
        if not family_type:
            return v
        
        if family_type == "P1":
            if not hasattr(v, 'degree') or v.degree is None:
                raise ValueError("P1 family requires degree constraint")
            if hasattr(v, 'genus') and v.genus is not None:
                raise ValueError("P1 family has fixed genus 0, cannot specify genus")
        
        elif family_type == "Elliptic":
            if hasattr(v, 'genus') and v.genus is not None and v.genus != 1:
                raise ValueError("Elliptic curves have genus 1")
            if not hasattr(v, 'coefficient_ranges') or v.coefficient_ranges is None:
                raise ValueError("Elliptic family requires coefficient_ranges")
        
        elif family_type == "Hyperelliptic":
            if not hasattr(v, 'genus') or v.genus is None:
                raise ValueError("Hyperelliptic family requires genus constraint")
            if not hasattr(v, 'coefficient_ranges') or v.coefficient_ranges is None:
                raise ValueError("Hyperelliptic family requires coefficient_ranges")
        
        elif family_type == "PlaneCurve":
            if not hasattr(v, 'degree') or v.degree is None:
                raise ValueError("PlaneCurve family requires degree constraint")
            if hasattr(v, 'degree') and v.degree is not None and v.degree < 1:
                raise ValueError("Plane curve degree must be at least 1")
        
        return v

    model_config = {
        "extra": "forbid",  # Reject unknown fields
        "validate_assignment": True
    }


# JSON Schema for validation
SAMPLING_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Algebraic Moduli Sampler Parameters",
    "description": "Parameters for sampling algebraic curve families and computing invariants",
    "type": "object",
    "additionalProperties": False,
    "required": ["family_type", "constraints", "sampling", "invariants"],
    "properties": {
        "family_type": {
            "type": "string",
            "enum": ["P1", "Elliptic", "Hyperelliptic", "PlaneCurve"],
            "description": "Type of algebraic curve family"
        },
        "constraints": {
            "type": "object",
            "additionalProperties": False,
            "required": ["field", "smoothness_check"],
            "properties": {
                "genus": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Genus constraint (optional for some families)"
                },
                "degree": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Degree constraint"
                },
                "coefficient_ranges": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "description": "Coefficient ranges [min, max]"
                },
                "field": {
                    "type": "string",
                    "enum": ["Q", "R", "C", "Fp"],
                    "default": "Q",
                    "description": "Base field"
                },
                "smoothness_check": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to check smoothness"
                }
            }
        },
        "sampling": {
            "type": "object",
            "additionalProperties": False,
            "required": ["n_samples_default", "seed"],
            "properties": {
                "n_samples_default": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10000,
                    "description": "Default number of samples"
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility"
                },
                "strategy": {
                    "type": "string",
                    "enum": ["grid", "random", "lhs"],
                    "default": "random",
                    "description": "Sampling strategy"
                }
            }
        },
        "invariants": {
            "type": "object",
            "additionalProperties": False,
            "required": ["compute"],
            "properties": {
                "compute": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["genus", "degK", "h0", "h1", "canonical_deg"]
                    },
                    "minLength": 1,
                    "description": "Invariants to compute"
                }
            }
        }
    }
}


def validate_params(params_dict: Dict[str, Any]) -> SamplingParams:
    """Validate parameters against JSON schema and return validated object.
    
    Args:
        params_dict: Dictionary of parameters to validate
        
    Returns:
        Validated SamplingParams object
        
    Raises:
        jsonschema.ValidationError: If parameters don't match schema
        ValueError: If family-specific constraints are violated
    """
    # First validate against JSON schema
    try:
        jsonschema.validate(instance=params_dict, schema=SAMPLING_SCHEMA)
    except jsonschema.ValidationError as e:
        # Provide more helpful error messages
        path = " -> ".join(str(p) for p in e.path)
        raise jsonschema.ValidationError(
            f"Parameter validation failed at {path}: {e.message}",
            path=e.path,
            instance=e.instance,
            schema=e.schema,
        )
    
    # Then validate with Pydantic (includes family-specific logic)
    return SamplingParams(**params_dict)


def load_params_from_file(file_path: Union[str, Path]) -> SamplingParams:
    """Load and validate parameters from a JSON file.
    
    Args:
        file_path: Path to JSON parameter file
        
    Returns:
        Validated SamplingParams object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
        jsonschema.ValidationError: If parameters don't match schema
        ValueError: If family-specific constraints are violated
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Parameter file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            params_dict = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in parameter file {file_path}: {e.msg}",
            e.doc,
            e.pos,
        )
    
    return validate_params(params_dict)
