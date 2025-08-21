"""Tests for the sampling module."""

import pytest
import numpy as np
import tempfile
import json
from pathlib import Path

from moduli_sampler.sampling import (
    SamplingParams,
    validate_params,
    Sampler,
)
from moduli_sampler.sampling.params_schema import (
    CoefficientRanges,
    Constraints,
    Sampling,
    Invariants,
)


class TestSamplingParams:
    """Test SamplingParams class."""

    def test_sampling_params_creation_p1(self):
        """Test creating SamplingParams for P1 family."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(
                degree=[-3, 5],
                field="Q",
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="grid",
                n_samples_default=9,
                seed=42
            ),
            invariants=Invariants(
                compute=["h0", "h1", "canonical_deg"]
            )
        )
        
        assert params.family_type == "P1"
        assert params.constraints.degree == [-3, 5]
        assert params.constraints.field == "Q"
        assert params.constraints.smoothness_check is True
        assert params.sampling.strategy == "grid"
        assert params.sampling.n_samples_default == 9
        assert params.sampling.seed == 42
        assert params.invariants.compute == ["h0", "h1", "canonical_deg"]

    def test_sampling_params_creation_elliptic(self):
        """Test creating SamplingParams for elliptic family."""
        params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(
                    a=[-3, 3],
                    b=[-3, 3]
                ),
                field="Q",
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="random",
                n_samples_default=25,
                seed=7
            ),
            invariants=Invariants(
                compute=["genus", "h0", "h1", "degK"]
            )
        )
        
        assert params.family_type == "Elliptic"
        assert params.constraints.coefficient_ranges.a == [-3, 3]
        assert params.constraints.coefficient_ranges.b == [-3, 3]
        assert params.sampling.strategy == "random"
        assert params.sampling.n_samples_default == 25

    def test_sampling_params_creation_hyperelliptic(self):
        """Test creating SamplingParams for hyperelliptic family."""
        params = SamplingParams(
            family_type="Hyperelliptic",
            constraints=Constraints(
                genus=2,
                coefficient_ranges=CoefficientRanges(
                    a0=[-2, 2],
                    a1=[-2, 2],
                    a2=[-2, 2],
                    a3=[-2, 2],
                    a4=[-2, 2],
                    a5=[-2, 2],
                    a6=[-2, 2]
                ),
                field="Q",
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="random",
                n_samples_default=20,
                seed=11
            ),
            invariants=Invariants(
                compute=["genus", "degK", "h0", "h1"]
            )
        )
        
        assert params.family_type == "Hyperelliptic"
        assert params.constraints.genus == 2
        assert params.constraints.coefficient_ranges.a0 == [-2, 2]
        assert params.constraints.coefficient_ranges.a6 == [-2, 2]

    def test_sampling_params_creation_plane_curve(self):
        """Test creating SamplingParams for plane curve family."""
        params = SamplingParams(
            family_type="PlaneCurve",
            constraints=Constraints(
                degree=3,
                coefficient_ranges=CoefficientRanges(
                    x3=[-2, 2],
                    y3=[-2, 2],
                    z3=[-2, 2]
                ),
                field="Q",
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="grid",
                n_samples_default=15,
                seed=123
            ),
            invariants=Invariants(
                compute=["genus", "degK", "h0", "h1"]
            )
        )
        
        assert params.family_type == "PlaneCurve"
        assert params.constraints.degree == 3
        assert params.constraints.coefficient_ranges.x3 == [-2, 2]

    def test_sampling_params_defaults(self):
        """Test SamplingParams default values."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(),
            sampling=Sampling(),
            invariants=Invariants()
        )
        
        assert params.constraints.field == "Q"
        assert params.constraints.smoothness_check is True
        assert params.sampling.strategy == "random"
        assert params.sampling.n_samples_default == 10
        assert params.sampling.seed == 0
        assert params.invariants.compute == ["genus", "h0", "h1"]

    def test_sampling_params_validation(self):
        """Test SamplingParams validation."""
        # Valid params
        valid_params = SamplingParams(
            family_type="P1",
            constraints=Constraints(),
            sampling=Sampling(),
            invariants=Invariants()
        )
        assert valid_params is not None
        
        # Invalid family type
        with pytest.raises(ValueError):
            SamplingParams(
                family_type="InvalidType",
                constraints=Constraints(),
                sampling=Sampling(),
                invariants=Invariants()
            )


class TestSampler:
    """Test Sampler class."""

    def test_sampler_creation(self):
        """Test Sampler creation."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(),
            sampling=Sampling(seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        assert sampler.params == params
        assert sampler.rng is not None
        assert sampler.rng.get_state()[1][0] == 42  # Check seed

    def test_sampler_p1_family(self):
        """Test sampling P1 family."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(
                degree=[-2, 3]
            ),
            sampling=Sampling(
                strategy="grid",
                n_samples_default=6,
                seed=42
            ),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_p1_family()
        
        assert len(family) == 6
        for curve_data in family:
            assert "curve" in curve_data
            assert "line_bundle" in curve_data
            assert curve_data["curve"]["type"] == "P1Curve"
            assert curve_data["curve"]["genus"] == 0

    def test_sampler_elliptic_family(self):
        """Test sampling elliptic family."""
        params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(
                    a=[-2, 2],
                    b=[-2, 2]
                ),
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="random",
                n_samples_default=10,
                seed=42
            ),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_elliptic_family()
        
        assert len(family) == 10
        for curve_data in family:
            assert "curve" in curve_data
            assert "line_bundle" in curve_data
            assert curve_data["curve"]["type"] == "EllipticCurve"
            assert curve_data["curve"]["genus"] == 1

    def test_sampler_hyperelliptic_family(self):
        """Test sampling hyperelliptic family."""
        params = SamplingParams(
            family_type="Hyperelliptic",
            constraints=Constraints(
                genus=2,
                coefficient_ranges=CoefficientRanges(
                    a0=[-1, 1],
                    a1=[-1, 1],
                    a2=[-1, 1],
                    a3=[-1, 1],
                    a4=[-1, 1],
                    a5=[-1, 1]
                ),
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="random",
                n_samples_default=8,
                seed=42
            ),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_hyperelliptic_family()
        
        assert len(family) == 8
        for curve_data in family:
            assert "curve" in curve_data
            assert "line_bundle" in curve_data
            assert curve_data["curve"]["type"] == "HyperellipticCurve"
            assert curve_data["curve"]["genus"] == 2

    def test_sampler_plane_curve_family(self):
        """Test sampling plane curve family."""
        params = SamplingParams(
            family_type="PlaneCurve",
            constraints=Constraints(
                degree=3,
                coefficient_ranges=CoefficientRanges(
                    x3=[-1, 1],
                    y3=[-1, 1],
                    z3=[-1, 1]
                ),
                smoothness_check=True
            ),
            sampling=Sampling(
                strategy="grid",
                n_samples_default=5,
                seed=42
            ),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_plane_curve_family()
        
        assert len(family) == 5
        for curve_data in family:
            assert "curve" in curve_data
            assert "line_bundle" in curve_data
            assert curve_data["curve"]["type"] == "PlaneCurve"
            assert curve_data["curve"]["degree"] == 3

    def test_sampler_family_dispatch(self):
        """Test that sampler dispatches to correct family method."""
        # P1
        p1_params = SamplingParams(
            family_type="P1",
            constraints=Constraints(),
            sampling=Sampling(seed=42),
            invariants=Invariants()
        )
        p1_sampler = Sampler(p1_params)
        p1_family = p1_sampler.sample_family()
        assert all(curve["curve"]["type"] == "P1Curve" for curve in p1_family)
        
        # Elliptic
        elliptic_params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(a=[-1, 1], b=[-1, 1])
            ),
            sampling=Sampling(seed=42),
            invariants=Invariants()
        )
        elliptic_sampler = Sampler(elliptic_params)
        elliptic_family = elliptic_sampler.sample_family()
        assert all(curve["curve"]["type"] == "EllipticCurve" for curve in elliptic_family)

    def test_sampler_invalid_family_type(self):
        """Test that sampler handles invalid family type."""
        params = SamplingParams(
            family_type="InvalidType",
            constraints=Constraints(),
            sampling=Sampling(seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        with pytest.raises(ValueError):
            sampler.sample_family()

    def test_sampler_deterministic(self):
        """Test that sampler produces deterministic results with same seed."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(degree=[-2, 2]),
            sampling=Sampling(strategy="grid", n_samples_default=5, seed=42),
            invariants=Invariants()
        )
        
        sampler1 = Sampler(params)
        family1 = sampler1.sample_p1_family()
        
        sampler2 = Sampler(params)
        family2 = sampler2.sample_p1_family()
        
        # Results should be identical
        assert family1 == family2

    def test_sampler_save_family(self):
        """Test saving family to file."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(degree=[-1, 1]),
            sampling=Sampling(strategy="grid", n_samples_default=3, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_p1_family()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            sampler.save_family(family, temp_path)
            
            # Check that file was created and contains valid JSON
            assert temp_path.exists()
            with open(temp_path, 'r') as f:
                saved_family = json.load(f)
            
            assert len(saved_family) == 3
            assert saved_family[0]["curve"]["type"] == "P1Curve"
            
        finally:
            temp_path.unlink(missing_ok=True)


class TestSamplingStrategies:
    """Test different sampling strategies."""

    def test_grid_sampling_p1(self):
        """Test grid sampling for P1 curves."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(degree=[-2, 2]),
            sampling=Sampling(strategy="grid", n_samples_default=5, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_p1_family()
        
        # Grid sampling should produce predictable degrees
        degrees = [curve["line_bundle"]["line_bundle_degree"] for curve in family]
        expected_degrees = [-2, -1, 0, 1, 2]
        assert degrees == expected_degrees

    def test_random_sampling_elliptic(self):
        """Test random sampling for elliptic curves."""
        params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(a=[-1, 1], b=[-1, 1])
            ),
            sampling=Sampling(strategy="random", n_samples_default=10, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_elliptic_family()
        
        # Random sampling should produce different coefficients
        a_values = [curve["curve"]["a"] for curve in family]
        b_values = [curve["curve"]["b"] for curve in family]
        
        # With seed 42, we should get deterministic but varied results
        assert len(set(a_values)) > 1 or len(set(b_values)) > 1

    def test_lhs_sampling_hyperelliptic(self):
        """Test Latin Hypercube sampling for hyperelliptic curves."""
        params = SamplingParams(
            family_type="Hyperelliptic",
            constraints=Constraints(
                genus=2,
                coefficient_ranges=CoefficientRanges(
                    a0=[-1, 1], a1=[-1, 1], a2=[-1, 1],
                    a3=[-1, 1], a4=[-1, 1], a5=[-1, 1]
                )
            ),
            sampling=Sampling(strategy="lhs", n_samples_default=6, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_hyperelliptic_family()
        
        assert len(family) == 6
        # LHS should provide good coverage of the parameter space
        for curve_data in family:
            assert "curve" in curve_data
            assert curve_data["curve"]["type"] == "HyperellipticCurve"


class TestSamplingConstraints:
    """Test sampling with various constraints."""

    def test_sampling_with_genus_constraint(self):
        """Test sampling with genus constraint."""
        params = SamplingParams(
            family_type="Hyperelliptic",
            constraints=Constraints(
                genus=3,
                coefficient_ranges=CoefficientRanges(
                    a0=[-1, 1], a1=[-1, 1], a2=[-1, 1],
                    a3=[-1, 1], a4=[-1, 1], a5=[-1, 1],
                    a6=[-1, 1], a7=[-1, 1]
                )
            ),
            sampling=Sampling(strategy="random", n_samples_default=5, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_hyperelliptic_family()
        
        for curve_data in family:
            assert curve_data["curve"]["genus"] == 3

    def test_sampling_with_degree_constraint(self):
        """Test sampling with degree constraint."""
        params = SamplingParams(
            family_type="PlaneCurve",
            constraints=Constraints(
                degree=4,
                coefficient_ranges=CoefficientRanges(
                    x4=[-1, 1], y4=[-1, 1], z4=[-1, 1]
                )
            ),
            sampling=Sampling(strategy="grid", n_samples_default=3, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_plane_curve_family()
        
        for curve_data in family:
            assert curve_data["curve"]["degree"] == 4

    def test_sampling_with_coefficient_ranges(self):
        """Test sampling with coefficient range constraints."""
        params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(
                    a=[-5, 5],
                    b=[-10, 10]
                )
            ),
            sampling=Sampling(strategy="random", n_samples_default=20, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_elliptic_family()
        
        for curve_data in family:
            a = curve_data["curve"]["a"]
            b = curve_data["curve"]["b"]
            assert -5 <= a <= 5
            assert -10 <= b <= 10

    def test_sampling_with_smoothness_check(self):
        """Test sampling with smoothness check enabled."""
        params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(a=[-2, 2], b=[-2, 2]),
                smoothness_check=True
            ),
            sampling=Sampling(strategy="random", n_samples_default=15, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_elliptic_family()
        
        # All curves should be smooth
        for curve_data in family:
            assert curve_data["curve"]["is_smooth"] is True


class TestSamplingEdgeCases:
    """Test edge cases in sampling."""

    def test_sampling_zero_samples(self):
        """Test sampling with zero samples."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(),
            sampling=Sampling(n_samples_default=0, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_p1_family()
        
        assert len(family) == 0

    def test_sampling_single_sample(self):
        """Test sampling with single sample."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(),
            sampling=Sampling(n_samples_default=1, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_p1_family()
        
        assert len(family) == 1
        assert family[0]["curve"]["type"] == "P1Curve"

    def test_sampling_large_number_samples(self):
        """Test sampling with large number of samples."""
        params = SamplingParams(
            family_type="P1",
            constraints=Constraints(degree=[-1, 1]),
            sampling=Sampling(strategy="grid", n_samples_default=100, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_p1_family()
        
        assert len(family) == 100
        # Should handle large numbers without issues

    def test_sampling_extreme_coefficient_ranges(self):
        """Test sampling with extreme coefficient ranges."""
        params = SamplingParams(
            family_type="Elliptic",
            constraints=Constraints(
                coefficient_ranges=CoefficientRanges(
                    a=[-1000, 1000],
                    b=[-1000, 1000]
                )
            ),
            sampling=Sampling(strategy="random", n_samples_default=10, seed=42),
            invariants=Invariants()
        )
        
        sampler = Sampler(params)
        family = sampler.sample_elliptic_family()
        
        assert len(family) == 10
        for curve_data in family:
            a = curve_data["curve"]["a"]
            b = curve_data["curve"]["b"]
            assert -1000 <= a <= 1000
            assert -1000 <= b <= 1000
