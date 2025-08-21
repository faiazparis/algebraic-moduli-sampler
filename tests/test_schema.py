"""Tests for parameter schema and validation."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
import jsonschema

from moduli_sampler.sampling.params_schema import (
    SamplingParams,
    validate_params,
    load_params_from_file,
    SAMPLING_SCHEMA,
)


class TestSamplingParams:
    """Test SamplingParams model creation and validation."""

    def test_p1_params_valid(self):
        """Test valid P1 parameters."""
        params_dict = {
            "family_type": "P1",
            "constraints": {
                "degree": 3,
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 9,
                "seed": 42,
            },
            "invariants": {
                "compute": ["h0", "h1", "canonical_deg"],
            },
        }
        
        params = SamplingParams(**params_dict)
        assert params.family_type == "P1"
        assert params.constraints.degree == 3
        assert params.sampling.strategy == "grid"
        assert params.sampling.seed == 42
        assert "h0" in params.invariants.compute

    def test_elliptic_params_valid(self):
        """Test valid elliptic curve parameters."""
        params_dict = {
            "family_type": "Elliptic",
            "constraints": {
                "coefficient_ranges": {
                    "a": [-3, 3],
                    "b": [-3, 3],
                },
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {
                "strategy": "random",
                "n_samples_default": 25,
                "seed": 7,
            },
            "invariants": {
                "compute": ["genus", "h0", "h1", "degK"],
            },
        }
        
        params = SamplingParams(**params_dict)
        assert params.family_type == "Elliptic"
        assert "a" in params.constraints.coefficient_ranges
        assert "b" in params.constraints.coefficient_ranges

    def test_hyperelliptic_params_valid(self):
        """Test valid hyperelliptic curve parameters."""
        params_dict = {
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
                },
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {
                "strategy": "random",
                "n_samples_default": 20,
                "seed": 11,
            },
            "invariants": {
                "compute": ["genus", "degK", "h0", "h1"],
            },
        }
        
        params = SamplingParams(**params_dict)
        assert params.family_type == "Hyperelliptic"
        assert params.constraints.genus == 2
        assert len(params.constraints.coefficient_ranges) == 6

    def test_plane_curve_params_valid(self):
        """Test valid plane curve parameters."""
        params_dict = {
            "family_type": "PlaneCurve",
            "constraints": {
                "degree": 3,
                "coefficient_ranges": {
                    "x^3": [-2, 2],
                    "y^3": [-2, 2],
                    "z^3": [-2, 2],
                },
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {
                "strategy": "random",
                "n_samples_default": 15,
                "seed": 23,
            },
            "invariants": {
                "compute": ["genus", "degK", "h0", "h1"],
            },
        }
        
        params = SamplingParams(**params_dict)
        assert params.family_type == "PlaneCurve"
        assert params.constraints.degree == 3

    def test_invalid_family_type(self):
        """Test invalid family type."""
        params_dict = {
            "family_type": "InvalidType",
            "constraints": {"field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "random", "n_samples_default": 10, "seed": 42},
            "invariants": {"compute": ["genus"]},
        }
        
        with pytest.raises(ValueError, match="InvalidType"):
            SamplingParams(**params_dict)

    def test_missing_required_fields(self):
        """Test missing required fields."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"field": "Q", "smoothness_check": True},
            # Missing sampling and invariants
        }
        
        with pytest.raises(ValueError):
            SamplingParams(**params_dict)

    def test_p1_missing_degree(self):
        """Test P1 family missing degree constraint."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="P1 family requires degree constraint"):
            SamplingParams(**params_dict)

    def test_p1_invalid_genus(self):
        """Test P1 family with invalid genus constraint."""
        params_dict = {
            "family_type": "P1",
            "constraints": {
                "degree": 3,
                "genus": 1,  # P1 has fixed genus 0
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="P1 family has fixed genus 0"):
            SamplingParams(**params_dict)

    def test_elliptic_missing_coefficients(self):
        """Test elliptic family missing coefficient ranges."""
        params_dict = {
            "family_type": "Elliptic",
            "constraints": {"field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "random", "n_samples_default": 25, "seed": 7},
            "invariants": {"compute": ["genus", "h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="Elliptic family requires coefficient_ranges"):
            SamplingParams(**params_dict)

    def test_elliptic_invalid_genus(self):
        """Test elliptic family with invalid genus."""
        params_dict = {
            "family_type": "Elliptic",
            "constraints": {
                "genus": 2,  # Elliptic curves have genus 1
                "coefficient_ranges": {"a": [-3, 3], "b": [-3, 3]},
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 25, "seed": 7},
            "invariants": {"compute": ["genus", "h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="Elliptic curves have genus 1"):
            SamplingParams(**params_dict)

    def test_hyperelliptic_missing_genus(self):
        """Test hyperelliptic family missing genus."""
        params_dict = {
            "family_type": "Hyperelliptic",
            "constraints": {
                "coefficient_ranges": {"a0": [-2, 2], "a1": [-2, 2]},
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 20, "seed": 11},
            "invariants": {"compute": ["genus", "degK"]},
        }
        
        with pytest.raises(ValueError, match="Hyperelliptic family requires genus constraint"):
            SamplingParams(**params_dict)

    def test_hyperelliptic_missing_coefficients(self):
        """Test hyperelliptic family missing coefficient ranges."""
        params_dict = {
            "family_type": "Hyperelliptic",
            "constraints": {
                "genus": 2,
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 20, "seed": 11},
            "invariants": {"compute": ["genus", "degK"]},
        }
        
        with pytest.raises(ValueError, match="Hyperelliptic family requires coefficient_ranges"):
            SamplingParams(**params_dict)

    def test_plane_curve_missing_degree(self):
        """Test plane curve family missing degree."""
        params_dict = {
            "family_type": "PlaneCurve",
            "constraints": {
                "coefficient_ranges": {"x^3": [-2, 2]},
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 15, "seed": 23},
            "invariants": {"compute": ["genus", "degK"]},
        }
        
        with pytest.raises(ValueError, match="PlaneCurve family requires degree constraint"):
            SamplingParams(**params_dict)

    def test_plane_curve_invalid_degree(self):
        """Test plane curve family with invalid degree."""
        params_dict = {
            "family_type": "PlaneCurve",
            "constraints": {
                "degree": 0,  # Must be at least 1
                "coefficient_ranges": {"x^1": [-2, 2]},
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 15, "seed": 23},
            "invariants": {"compute": ["genus", "degK"]},
        }
        
        with pytest.raises(ValueError, match="Plane curve degree must be at least 1"):
            SamplingParams(**params_dict)

    def test_invalid_genus_negative(self):
        """Test negative genus constraint."""
        params_dict = {
            "family_type": "Hyperelliptic",
            "constraints": {
                "genus": -1,  # Must be non-negative
                "coefficient_ranges": {"a0": [-2, 2]},
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 20, "seed": 11},
            "invariants": {"compute": ["genus"]},
        }
        
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            SamplingParams(**params_dict)

    def test_invalid_degree_negative(self):
        """Test negative degree constraint."""
        params_dict = {
            "family_type": "P1",
            "constraints": {
                "degree": -5,  # Must be non-negative for P1
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="Degree must be non-negative"):
            SamplingParams(**params_dict)

    def test_invalid_n_samples_too_large(self):
        """Test n_samples_default too large."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 15000,  # Exceeds maximum
                "seed": 42,
            },
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="Input should be less than or equal to 10000"):
            SamplingParams(**params_dict)

    def test_invalid_n_samples_zero(self):
        """Test n_samples_default zero."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 0,  # Must be positive
                "seed": 42,
            },
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="Input should be greater than 0"):
            SamplingParams(**params_dict)

    def test_empty_invariants_list(self):
        """Test empty invariants compute list."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": []},  # Must have at least one
        }
        
        with pytest.raises(ValueError, match="List should have at least 1 item after validation"):
            SamplingParams(**params_dict)

    def test_default_values(self):
        """Test default values are set correctly."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3},  # Missing field and smoothness_check
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        params = SamplingParams(**params_dict)
        assert params.constraints.field == "Q"  # Default
        assert params.constraints.smoothness_check is True  # Default
        assert params.sampling.strategy == "grid"  # Explicit
        assert params.sampling.seed == 42  # Explicit

    def test_coefficient_ranges_access(self):
        """Test CoefficientRanges access methods."""
        params_dict = {
            "family_type": "Elliptic",
            "constraints": {
                "coefficient_ranges": {"a": [-3, 3], "b": [-3, 3]},
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "random", "n_samples_default": 25, "seed": 7},
            "invariants": {"compute": ["genus", "h0", "h1"]},
        }
        
        params = SamplingParams(**params_dict)
        coeff_ranges = params.constraints.coefficient_ranges
        
        # Test access methods
        assert coeff_ranges["a"] == [-3, 3]
        assert "a" in coeff_ranges
        assert list(coeff_ranges.keys()) == ["a", "b"]
        assert list(coeff_ranges.values()) == [[-3, 3], [-3, 3]]


class TestValidateParams:
    """Test validate_params function."""

    def test_valid_params(self):
        """Test validation of valid parameters."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1", "canonical_deg"]},
        }
        
        params = validate_params(params_dict)
        assert isinstance(params, SamplingParams)
        assert params.family_type == "P1"

    def test_invalid_json_schema(self):
        """Test validation failure due to JSON schema violation."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1", "canonical_deg"]},
            "extra_field": "should_not_be_here",  # Violates schema
        }
        
        with pytest.raises(jsonschema.ValidationError):
            validate_params(params_dict)

    def test_family_specific_validation(self):
        """Test family-specific constraint validation."""
        params_dict = {
            "family_type": "P1",
            "constraints": {
                "degree": 3,
                "genus": 1,  # Invalid for P1
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with pytest.raises(ValueError, match="P1 family has fixed genus 0"):
            validate_params(params_dict)


class TestLoadParamsFromFile:
    """Test load_params_from_file function."""

    def test_load_valid_file(self):
        """Test loading valid parameters from file."""
        params_dict = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1", "canonical_deg"]},
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(params_dict, f)
            temp_file = f.name
        
        try:
            params = load_params_from_file(temp_file)
            assert isinstance(params, SamplingParams)
            assert params.family_type == "P1"
        finally:
            Path(temp_file).unlink()

    def test_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_params_from_file("nonexistent_file.json")

    def test_invalid_json(self):
        """Test loading file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_params_from_file(temp_file)
        finally:
            Path(temp_file).unlink()

    def test_validation_error_in_file(self):
        """Test loading file with validation errors."""
        params_dict = {
            "family_type": "P1",
            "constraints": {
                "degree": 3,
                "genus": 1,  # Invalid for P1
                "field": "Q",
                "smoothness_check": True,
            },
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(params_dict, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="P1 family has fixed genus 0"):
                load_params_from_file(temp_file)
        finally:
            Path(temp_file).unlink()


class TestJSONSchema:
    """Test JSON schema validation."""

    def test_schema_structure(self):
        """Test that the JSON schema is well-formed."""
        # Basic schema validation
        assert "$schema" in SAMPLING_SCHEMA
        assert "type" in SAMPLING_SCHEMA
        assert SAMPLING_SCHEMA["type"] == "object"
        
        # Required fields
        assert "required" in SAMPLING_SCHEMA
        required_fields = SAMPLING_SCHEMA["required"]
        assert "family_type" in required_fields
        assert "constraints" in required_fields
        assert "sampling" in required_fields
        assert "invariants" in required_fields

    def test_schema_validation(self):
        """Test that the schema validates correctly."""
        valid_params = {
            "family_type": "P1",
            "constraints": {"degree": 3, "field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "grid", "n_samples_default": 9, "seed": 42},
            "invariants": {"compute": ["h0", "h1"]},
        }
        
        # Should not raise any exception
        jsonschema.validate(instance=valid_params, schema=SAMPLING_SCHEMA)

    def test_schema_invalid_family_type(self):
        """Test schema validation with invalid family type."""
        invalid_params = {
            "family_type": "InvalidType",
            "constraints": {"field": "Q", "smoothness_check": True},
            "sampling": {"strategy": "random", "n_samples_default": 10, "seed": 42},
            "invariants": {"compute": ["genus"]},
        }
        
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_params, schema=SAMPLING_SCHEMA)

    def test_schema_missing_required(self):
        """Test schema validation with missing required fields."""
        incomplete_params = {
            "family_type": "P1",
            # Missing constraints, sampling, invariants
        }
        
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=incomplete_params, schema=SAMPLING_SCHEMA)
