"""Pytest configuration for Algebraic Moduli Sampler tests."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_file():
    """Create a temporary file for tests."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def sample_params():
    """Sample parameters for testing."""
    return {
        "family_type": "P1",
        "constraints": {
            "degree": [-2, 2],
            "field": "Q",
            "smoothness_check": True
        },
        "sampling": {
            "strategy": "grid",
            "n_samples_default": 5,
            "seed": 42
        },
        "invariants": {
            "compute": ["h0", "h1", "canonical_deg"]
        }
    }


@pytest.fixture(scope="function")
def sample_elliptic_params():
    """Sample elliptic curve parameters for testing."""
    return {
        "family_type": "Elliptic",
        "constraints": {
            "coefficient_ranges": {
                "a": [-2, 2],
                "b": [-2, 2]
            },
            "field": "Q",
            "smoothness_check": True
        },
        "sampling": {
            "strategy": "random",
            "n_samples_default": 10,
            "seed": 42
        },
        "invariants": {
            "compute": ["genus", "h0", "h1", "degK"]
        }
    }


@pytest.fixture(scope="function")
def sample_hyperelliptic_params():
    """Sample hyperelliptic curve parameters for testing."""
    return {
        "family_type": "Hyperelliptic",
        "constraints": {
            "genus": 2,
            "coefficient_ranges": {
                "a0": [-1, 1],
                "a1": [-1, 1],
                "a2": [-1, 1],
                "a3": [-1, 1],
                "a4": [-1, 1],
                "a5": [-1, 1]
            },
            "field": "Q",
            "smoothness_check": True
        },
        "sampling": {
            "strategy": "random",
            "n_samples_default": 8,
            "seed": 42
        },
        "invariants": {
            "compute": ["genus", "degK", "h0", "h1"]
        }
    }


@pytest.fixture(scope="function")
def sample_plane_curve_params():
    """Sample plane curve parameters for testing."""
    return {
        "family_type": "PlaneCurve",
        "constraints": {
            "degree": 3,
            "coefficient_ranges": {
                "x3": [-1, 1],
                "y3": [-1, 1],
                "z3": [-1, 1]
            },
            "field": "Q",
            "smoothness_check": True
        },
        "sampling": {
            "strategy": "grid",
            "n_samples_default": 5,
            "seed": 42
        },
        "invariants": {
            "compute": ["genus", "degK", "h0", "h1"]
        }
    }


@pytest.fixture(scope="function")
def sample_family_data():
    """Sample family data for testing."""
    return [
        {
            "curve": {
                "type": "P1Curve",
                "genus": 0,
                "canonical_degree": -2,
                "is_smooth": True,
                "degree": 1,
                "h0": 2,
                "h1": 0
            },
            "line_bundle": {
                "curve_type": "P1Curve",
                "line_bundle_degree": 1,
                "h0": 2,
                "h1": 0,
                "euler_characteristic": 2
            }
        },
        {
            "curve": {
                "type": "P1Curve",
                "genus": 0,
                "canonical_degree": -2,
                "is_smooth": True,
                "degree": 2,
                "h0": 3,
                "h1": 0
            },
            "line_bundle": {
                "curve_type": "P1Curve",
                "line_bundle_degree": 2,
                "h0": 3,
                "h1": 0,
                "euler_characteristic": 3
            }
        }
    ]


@pytest.fixture(scope="function")
def sample_invariants():
    """Sample invariants for testing."""
    return [
        {
            "genus": 0,
            "canonical_degree": -2,
            "line_bundle_degree": 1,
            "h0": 2,
            "h1": 0,
            "euler_characteristic": 2,
            "h0_canonical": 0
        },
        {
            "genus": 0,
            "canonical_degree": -2,
            "line_bundle_degree": 2,
            "h0": 3,
            "h1": 0,
            "euler_characteristic": 3,
            "h0_canonical": 0
        }
    ]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark CLI tests as integration tests
        if "test_cli" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Mark utility tests as unit tests
        elif "test_utils" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark geometry tests as unit tests
        elif "test_geometry" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark cohomology tests as unit tests
        elif "test_cohomology" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark invariants tests as unit tests
        elif "test_invariants" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark sampling tests as unit tests
        elif "test_sampling" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark IO tests as unit tests
        elif "test_io" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark schema tests as unit tests
        elif "test_schema" in item.nodeid:
            item.add_marker(pytest.mark.unit)
