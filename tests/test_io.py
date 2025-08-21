"""Tests for the IO module."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import datetime

from moduli_sampler.io import (
    load_json,
    save_json,
    load_params,
    save_results,
    load_family_data,
    get_git_info,
    get_environment_info,
    get_timestamp,
    compute_params_hash,
    get_metadata,
    save_metadata,
)


class TestJSONIO:
    """Test JSON I/O functions."""

    def test_load_json_valid(self):
        """Test loading valid JSON."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(test_data, f)
        
        try:
            loaded_data = load_json(temp_path)
            assert loaded_data == test_data
        finally:
            temp_path.unlink(missing_ok=True)

    def test_load_json_invalid(self):
        """Test loading invalid JSON."""
        invalid_json = "{ invalid json content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            f.write(invalid_json)
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_json(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_load_json_file_not_found(self):
        """Test loading JSON from non-existent file."""
        temp_path = Path("/nonexistent/file.json")
        
        with pytest.raises(FileNotFoundError):
            load_json(temp_path)

    def test_save_json_valid(self):
        """Test saving valid JSON."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            save_json(test_data, temp_path)
            
            # Check that file was created and contains correct data
            assert temp_path.exists()
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == test_data
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_json_with_indent(self):
        """Test saving JSON with indentation."""
        test_data = {"key": "value", "nested": {"inner": "data"}}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            save_json(test_data, temp_path, indent=2)
            
            # Check that file was created
            assert temp_path.exists()
            
            # Check that content is properly formatted
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Should have proper indentation
            assert "  " in content  # 2-space indentation
            assert content.count('"key"') == 1
            assert content.count('"nested"') == 1
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_json_to_directory(self):
        """Test saving JSON to directory path."""
        test_data = {"key": "value"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test.json"
            
            save_json(test_data, temp_path)
            
            # Check that file was created
            assert temp_path.exists()
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == test_data

    def test_load_params(self):
        """Test loading parameters."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(test_params, f)
        
        try:
            loaded_params = load_params(temp_path)
            assert loaded_params == test_params
            assert isinstance(loaded_params, dict)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_results(self):
        """Test saving results."""
        test_results = [
            {"curve": {"type": "P1Curve", "genus": 0}, "line_bundle": {"degree": 1}},
            {"curve": {"type": "P1Curve", "genus": 0}, "line_bundle": {"degree": 2}}
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            save_results(test_results, temp_path)
            
            # Check that file was created
            assert temp_path.exists()
            
            with open(temp_path, 'r') as f:
                saved_results = json.load(f)
            
            assert saved_results == test_results
            assert isinstance(saved_results, list)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_load_family_data(self):
        """Test loading family data."""
        test_family = [
            {"curve": {"type": "P1Curve", "genus": 0}, "line_bundle": {"degree": 1}},
            {"curve": {"type": "P1Curve", "genus": 0}, "line_bundle": {"degree": 2}}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(test_family, f)
        
        try:
            loaded_family = load_family_data(temp_path)
            assert loaded_family == test_family
            assert isinstance(loaded_family, list)
        finally:
            temp_path.unlink(missing_ok=True)


class TestMetadata:
    """Test metadata functions."""

    def test_get_git_info(self):
        """Test git info collection."""
        git_info = get_git_info()
        
        # Check that all expected fields are present
        assert "commit_hash" in git_info
        assert "branch" in git_info
        assert "is_dirty" in git_info
        assert "remote_url" in git_info
        
        # Check that values are of expected types
        assert isinstance(git_info["commit_hash"], str)
        assert isinstance(git_info["branch"], str)
        assert isinstance(git_info["is_dirty"], bool)
        assert isinstance(git_info["remote_url"], str)

    def test_get_environment_info(self):
        """Test environment info collection."""
        env_info = get_environment_info()
        
        # Check that all expected fields are present
        assert "python_version" in env_info
        assert "numpy_version" in env_info
        assert "sympy_version" in env_info
        assert "platform" in env_info
        assert "architecture" in env_info
        
        # Check that values are of expected types
        assert isinstance(env_info["python_version"], str)
        assert isinstance(env_info["numpy_version"], str)
        assert isinstance(env_info["sympy_version"], str)
        assert isinstance(env_info["platform"], str)
        assert isinstance(env_info["architecture"], str)

    def test_get_timestamp(self):
        """Test timestamp generation."""
        timestamp = get_timestamp()
        
        # Check that timestamp is a string
        assert isinstance(timestamp, str)
        
        # Check that it's in ISO format
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp
        
        # Check that it's recent (within last minute)
        dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        time_diff = abs((now - dt).total_seconds())
        assert time_diff < 60

    def test_compute_params_hash(self):
        """Test parameter hash computation."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        hash1 = compute_params_hash(test_params)
        hash2 = compute_params_hash(test_params)
        
        # Same params should produce same hash
        assert hash1 == hash2
        
        # Hash should be a string
        assert isinstance(hash1, str)
        assert len(hash1) > 0
        
        # Different params should produce different hashes
        different_params = test_params.copy()
        different_params["sampling"]["seed"] = 43
        
        hash3 = compute_params_hash(different_params)
        assert hash3 != hash1

    def test_compute_params_hash_deterministic(self):
        """Test that parameter hash is deterministic."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        # Compute hash multiple times
        hashes = [compute_params_hash(test_params) for _ in range(10)]
        
        # All hashes should be identical
        assert len(set(hashes)) == 1
        assert hashes[0] == hashes[1]

    def test_get_metadata(self):
        """Test metadata generation."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        metadata = get_metadata(test_params)
        
        # Check that all expected fields are present
        assert "timestamp" in metadata
        assert "git_info" in metadata
        assert "environment_info" in metadata
        assert "parameters_hash" in metadata
        assert "parameters" in metadata
        
        # Check that values are of expected types
        assert isinstance(metadata["timestamp"], str)
        assert isinstance(metadata["git_info"], dict)
        assert isinstance(metadata["environment_info"], dict)
        assert isinstance(metadata["parameters_hash"], str)
        assert isinstance(metadata["parameters"], dict)
        
        # Check that parameters are included
        assert metadata["parameters"] == test_params

    def test_save_metadata(self):
        """Test metadata saving."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        metadata = get_metadata(test_params)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            save_metadata(metadata, output_dir)
            
            # Check that metadata.json was created
            metadata_file = output_dir / "metadata.json"
            assert metadata_file.exists()
            
            # Check that metadata_summary.txt was created
            summary_file = output_dir / "metadata_summary.txt"
            assert summary_file.exists()
            
            # Check JSON content
            with open(metadata_file, 'r') as f:
                saved_metadata = json.load(f)
            
            assert saved_metadata == metadata
            
            # Check summary content
            with open(summary_file, 'r') as f:
                summary_content = f.read()
            
            # Summary should contain key information
            assert "Timestamp" in summary_content
            assert "Git Commit" in summary_content
            assert "Python Version" in summary_content
            assert "Parameters Hash" in summary_content

    def test_save_metadata_custom_filename(self):
        """Test metadata saving with custom filename."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        metadata = get_metadata(test_params)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            save_metadata(metadata, output_dir, filename="custom_metadata.json")
            
            # Check that custom filename was used
            metadata_file = output_dir / "custom_metadata.json"
            assert metadata_file.exists()
            
            # Check that default summary filename was still used
            summary_file = output_dir / "metadata_summary.txt"
            assert summary_file.exists()


class TestIOIntegration:
    """Test integration between IO functions."""

    def test_full_workflow(self):
        """Test complete IO workflow."""
        # Create test data
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        test_family = [
            {"curve": {"type": "P1Curve", "genus": 0}, "line_bundle": {"degree": 1}},
            {"curve": {"type": "P1Curve", "genus": 0}, "line_bundle": {"degree": 2}}
        ]
        
        test_invariants = [
            {"genus": 0, "h0": 2, "h1": 0, "euler_characteristic": 2},
            {"genus": 0, "h0": 3, "h1": 0, "euler_characteristic": 3}
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # Save parameters
            params_file = output_dir / "params.json"
            save_json(test_params, params_file)
            
            # Save family data
            family_file = output_dir / "family.json"
            save_results(test_family, family_file)
            
            # Save invariants
            invariants_file = output_dir / "invariants.json"
            save_results(test_invariants, invariants_file)
            
            # Generate and save metadata
            metadata = get_metadata(test_params)
            save_metadata(metadata, output_dir)
            
            # Verify all files were created
            assert params_file.exists()
            assert family_file.exists()
            assert invariants_file.exists()
            assert (output_dir / "metadata.json").exists()
            assert (output_dir / "metadata_summary.txt").exists()
            
            # Load and verify data
            loaded_params = load_params(params_file)
            loaded_family = load_family_data(family_file)
            loaded_invariants = load_json(invariants_file)
            loaded_metadata = load_json(output_dir / "metadata.json")
            
            assert loaded_params == test_params
            assert loaded_family == test_family
            assert loaded_invariants == test_invariants
            assert loaded_metadata == metadata

    def test_metadata_consistency(self):
        """Test that metadata is consistent across saves."""
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": 42},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # Generate metadata twice
            metadata1 = get_metadata(test_params)
            metadata2 = get_metadata(test_params)
            
            # Should be identical
            assert metadata1 == metadata2
            
            # Save both
            save_metadata(metadata1, output_dir, filename="metadata1.json")
            save_metadata(metadata2, output_dir, filename="metadata2.json")
            
            # Load and compare
            loaded1 = load_json(output_dir / "metadata1.json")
            loaded2 = load_json(output_dir / "metadata2.json")
            
            assert loaded1 == loaded2
            assert loaded1 == metadata1


class TestIOErrorHandling:
    """Test IO error handling."""

    def test_save_json_permission_error(self):
        """Test saving JSON with permission error."""
        test_data = {"key": "value"}
        
        # Try to save to a location that might not be writable
        # This test might not work on all systems
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                save_json(test_data, Path("/restricted/file.json"))

    def test_load_json_encoding_error(self):
        """Test loading JSON with encoding error."""
        # Create a file with invalid encoding
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        
        try:
            with pytest.raises((UnicodeDecodeError, json.JSONDecodeError)):
                load_json(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_metadata_invalid_directory(self):
        """Test saving metadata to invalid directory."""
        test_params = {"family_type": "P1"}
        metadata = get_metadata(test_params)
        
        # Try to save to a non-existent directory
        invalid_dir = Path("/nonexistent/directory")
        
        with pytest.raises(FileNotFoundError):
            save_metadata(metadata, invalid_dir)

    def test_compute_params_hash_with_numpy_types(self):
        """Test parameter hash computation with numpy types."""
        import numpy as np
        
        test_params = {
            "family_type": "P1",
            "constraints": {"degree": [-2, 2]},
            "sampling": {"strategy": "grid", "seed": np.int64(42)},
            "invariants": {"compute": ["h0", "h1"]}
        }
        
        # Should not raise an error
        hash1 = compute_params_hash(test_params)
        assert isinstance(hash1, str)
        assert len(hash1) > 0


class TestIOEdgeCases:
    """Test edge cases in IO functions."""

    def test_save_json_empty_data(self):
        """Test saving empty JSON data."""
        empty_data = {}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            save_json(empty_data, temp_path)
            
            # Check that file was created
            assert temp_path.exists()
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == empty_data
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_json_none_data(self):
        """Test saving None as JSON data."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            save_json(None, temp_path)
            
            # Check that file was created
            assert temp_path.exists()
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data is None
        finally:
            temp_path.unlink(missing_ok=True)

    def test_compute_params_hash_nested_structure(self):
        """Test parameter hash computation with deeply nested structure."""
        nested_params = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "deep_value"
                        }
                    }
                }
            },
            "array": [1, 2, [3, 4, [5, 6]]],
            "mixed": {"str": "value", "int": 42, "float": 3.14, "bool": True}
        }
        
        # Should not raise an error
        hash1 = compute_params_hash(nested_params)
        hash2 = compute_params_hash(nested_params)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)

    def test_get_metadata_with_missing_git(self):
        """Test metadata generation when git is not available."""
        test_params = {"family_type": "P1"}
        
        # Mock git info to simulate missing git
        with patch('moduli_sampler.io.get_git_info', return_value={
            "commit_hash": "unknown",
            "branch": "unknown",
            "is_dirty": False,
            "remote_url": "unknown"
        }):
            metadata = get_metadata(test_params)
            
            assert metadata["git_info"]["commit_hash"] == "unknown"
            assert metadata["git_info"]["branch"] == "unknown"
            assert metadata["git_info"]["is_dirty"] is False
            assert metadata["git_info"]["remote_url"] == "unknown"
