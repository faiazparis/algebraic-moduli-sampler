"""Tests for the CLI module."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from moduli_sampler.cli import main


class TestCLICommands:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "Algebraic Moduli Sampler" in result.output
        assert "validate" in result.output
        assert "sample" in result.output
        assert "invariants" in result.output
        assert "pipeline" in result.output

    def test_cli_validate_valid_params(self):
        """Test validate command with valid parameters."""
        # Create valid parameter file
        params = {
            "family_type": "P1",
            "constraints": {
                "degree": [-3, 5],
                "field": "Q",
                "smoothness_check": True
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, ['validate', str(temp_path)])
            assert result.exit_code == 0
            assert "Parameters are valid" in result.output
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_validate_invalid_params(self):
        """Test validate command with invalid parameters."""
        # Create invalid parameter file
        params = {
            "family_type": "InvalidType",  # Invalid family type
            "constraints": {},
            "sampling": {},
            "invariants": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, ['validate', str(temp_path)])
            assert result.exit_code != 0  # Should fail
            assert "error" in result.output.lower() or "invalid" in result.output.lower()
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_validate_file_not_found(self):
        """Test validate command with non-existent file."""
        result = self.runner.invoke(main, ['validate', 'nonexistent.json'])
        assert result.exit_code != 0
        assert "error" in result.output.lower() or "not found" in result.output.lower()

    def test_cli_sample_p1(self):
        """Test sample command for P1 family."""
        # Create valid parameter file
        params = {
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '5',
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Sampling completed successfully" in result.output
            
            # Check that output files were created
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            
            # Check family file content
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            assert len(family_data) == 5
            assert family_data[0]["curve"]["type"] == "P1Curve"
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_sample_elliptic(self):
        """Test sample command for elliptic family."""
        # Create valid parameter file
        params = {
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '10',
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Sampling completed successfully" in result.output
            
            # Check that output files were created
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            
            # Check family file content
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            assert len(family_data) == 10
            assert family_data[0]["curve"]["type"] == "EllipticCurve"
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_sample_hyperelliptic(self):
        """Test sample command for hyperelliptic family."""
        # Create valid parameter file
        params = {
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '8',
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Sampling completed successfully" in result.output
            
            # Check that output files were created
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            
            # Check family file content
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            assert len(family_data) == 8
            assert family_data[0]["curve"]["type"] == "HyperellipticCurve"
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_sample_plane_curve(self):
        """Test sample command for plane curve family."""
        # Create valid parameter file
        params = {
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '5',
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Sampling completed successfully" in result.output
            
            # Check that output files were created
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            
            # Check family file content
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            assert len(family_data) == 5
            assert family_data[0]["curve"]["type"] == "PlaneCurve"
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_sample_without_optional_args(self):
        """Test sample command without optional arguments."""
        # Create valid parameter file
        params = {
            "family_type": "P1",
            "constraints": {
                "degree": [-1, 1],
                "field": "Q",
                "smoothness_check": True
            },
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 3,
                "seed": 42
            },
            "invariants": {
                "compute": ["h0", "h1"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Sampling completed successfully" in result.output
            
            # Should use default values from params
            family_file = self.output_dir / "family.json"
            assert family_file.exists()
            
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            assert len(family_data) == 3  # Default from params
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_invariants(self):
        """Test invariants command."""
        # First create a family file
        family_data = [
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
        
        family_file = self.output_dir / "family.json"
        with open(family_file, 'w') as f:
            json.dump(family_data, f)
        
        # Test invariants command
        result = self.runner.invoke(main, [
            'invariants', str(family_file),
            '--out', str(self.output_dir / "invariants.json")
        ])
        
        assert result.exit_code == 0
        assert "Invariants computation completed successfully" in result.output
        
        # Check that invariants file was created
        invariants_file = self.output_dir / "invariants.json"
        assert invariants_file.exists()
        
        with open(invariants_file, 'r') as f:
            invariants_data = json.load(f)
        
        assert len(invariants_data) == 1
        assert "genus" in invariants_data[0]
        assert "h0" in invariants_data[0]
        assert "h1" in invariants_data[0]

    def test_cli_pipeline(self):
        """Test pipeline command."""
        # Create valid parameter file
        params = {
            "family_type": "P1",
            "constraints": {
                "degree": [-1, 1],
                "field": "Q",
                "smoothness_check": True
            },
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 3,
                "seed": 42
            },
            "invariants": {
                "compute": ["h0", "h1", "canonical_deg"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'pipeline', str(temp_path),
                '--seed', '42',
                '--n', '3',
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Pipeline completed successfully" in result.output
            
            # Check that all output files were created
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            invariants_file = self.output_dir / "invariants.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            assert invariants_file.exists()
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_pipeline_without_optional_args(self):
        """Test pipeline command without optional arguments."""
        # Create valid parameter file
        params = {
            "family_type": "P1",
            "constraints": {
                "degree": [-1, 1],
                "field": "Q",
                "smoothness_check": True
            },
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 3,
                "seed": 42
            },
            "invariants": {
                "compute": ["h0", "h1", "canonical_deg"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'pipeline', str(temp_path),
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            assert "Pipeline completed successfully" in result.output
            
            # Should use default values from params
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            invariants_file = self.output_dir / "invariants.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            assert invariants_file.exists()
            
        finally:
            temp_path.unlink(missing_ok=True)


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_sample_invalid_params(self):
        """Test sample command with invalid parameters."""
        # Create invalid parameter file
        params = {
            "family_type": "InvalidType",
            "constraints": {},
            "sampling": {},
            "invariants": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code != 0
            assert "error" in result.output.lower() or "invalid" in result.output.lower()
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_sample_invalid_output_dir(self):
        """Test sample command with invalid output directory."""
        # Create valid parameter file
        params = {
            "family_type": "P1",
            "constraints": {},
            "sampling": {},
            "invariants": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            # Try to write to a non-existent directory
            invalid_output = "/nonexistent/directory"
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--out', invalid_output
            ])
            
            assert result.exit_code != 0
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_invariants_file_not_found(self):
        """Test invariants command with non-existent family file."""
        result = self.runner.invoke(main, [
            'invariants', 'nonexistent.json',
            '--out', str(self.output_dir / "invariants.json")
        ])
        
        assert result.exit_code != 0
        assert "error" in result.output.lower() or "not found" in result.output.lower()

    def test_cli_pipeline_invalid_params(self):
        """Test pipeline command with invalid parameters."""
        # Create invalid parameter file
        params = {
            "family_type": "InvalidType",
            "constraints": {},
            "sampling": {},
            "invariants": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'pipeline', str(temp_path),
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code != 0
            assert "error" in result.output.lower() or "invalid" in result.output.lower()
            
        finally:
            temp_path.unlink(missing_ok=True)


class TestCLIDeterministicOutput:
    """Test that CLI produces deterministic output."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_deterministic_p1_sampling(self):
        """Test that P1 sampling produces deterministic output."""
        # Create parameter file
        params = {
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            # Run sampling twice with same seed
            output_dir1 = self.output_dir / "run1"
            output_dir1.mkdir(exist_ok=True)
            
            result1 = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '5',
                '--out', str(output_dir1)
            ])
            
            assert result1.exit_code == 0
            
            output_dir2 = self.output_dir / "run2"
            output_dir2.mkdir(exist_ok=True)
            
            result2 = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '5',
                '--out', str(output_dir2)
            ])
            
            assert result2.exit_code == 0
            
            # Check that outputs are identical
            family_file1 = output_dir1 / "family.json"
            family_file2 = output_dir2 / "family.json"
            
            with open(family_file1, 'r') as f:
                family1 = json.load(f)
            
            with open(family_file2, 'r') as f:
                family2 = json.load(f)
            
            assert family1 == family2
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_deterministic_elliptic_sampling(self):
        """Test that elliptic sampling produces deterministic output."""
        # Create parameter file
        params = {
            "family_type": "Elliptic",
            "constraints": {
                "coefficient_ranges": {
                    "a": [-1, 1],
                    "b": [-1, 1]
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            # Run sampling twice with same seed
            output_dir1 = self.output_dir / "run1"
            output_dir1.mkdir(exist_ok=True)
            
            result1 = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '10',
                '--out', str(output_dir1)
            ])
            
            assert result1.exit_code == 0
            
            output_dir2 = self.output_dir / "run2"
            output_dir2.mkdir(exist_ok=True)
            
            result2 = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--seed', '42',
                '--n', '10',
                '--out', str(output_dir2)
            ])
            
            assert result2.exit_code == 0
            
            # Check that outputs are identical
            family_file1 = output_dir1 / "family.json"
            family_file2 = output_dir2 / "family.json"
            
            with open(family_file1, 'r') as f:
                family1 = json.load(f)
            
            with open(family_file2, 'r') as f:
                family2 = json.load(f)
            
            assert family1 == family2
            
        finally:
            temp_path.unlink(missing_ok=True)


class TestCLIOutputStructure:
    """Test CLI output structure and content."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_output_files_structure(self):
        """Test that CLI creates all required output files."""
        # Create parameter file
        params = {
            "family_type": "P1",
            "constraints": {
                "degree": [-1, 1],
                "field": "Q",
                "smoothness_check": True
            },
            "sampling": {
                "strategy": "grid",
                "n_samples_default": 3,
                "seed": 42
            },
            "invariants": {
                "compute": ["h0", "h1", "canonical_deg"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'pipeline', str(temp_path),
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            
            # Check that all required files exist
            family_file = self.output_dir / "family.json"
            metadata_file = self.output_dir / "metadata.json"
            invariants_file = self.output_dir / "invariants.json"
            
            assert family_file.exists()
            assert metadata_file.exists()
            assert invariants_file.exists()
            
            # Check family file structure
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            assert isinstance(family_data, list)
            assert len(family_data) == 3
            
            for curve_data in family_data:
                assert "curve" in curve_data
                assert "line_bundle" in curve_data
                assert "type" in curve_data["curve"]
                assert "genus" in curve_data["curve"]
                assert "line_bundle_degree" in curve_data["line_bundle"]
            
            # Check metadata file structure
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            assert "timestamp" in metadata
            assert "git_info" in metadata
            assert "environment_info" in metadata
            assert "parameters_hash" in metadata
            
            # Check invariants file structure
            with open(invariants_file, 'r') as f:
                invariants = json.load(f)
            
            assert isinstance(invariants, list)
            assert len(invariants) == 3
            
            for inv in invariants:
                assert "genus" in inv
                assert "h0" in inv
                assert "h1" in inv
                assert "euler_characteristic" in inv
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cli_metadata_content(self):
        """Test that metadata file contains expected information."""
        # Create parameter file
        params = {
            "family_type": "P1",
            "constraints": {},
            "sampling": {"seed": 42},
            "invariants": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(params, f)
        
        try:
            result = self.runner.invoke(main, [
                'sample', str(temp_path),
                '--out', str(self.output_dir)
            ])
            
            assert result.exit_code == 0
            
            metadata_file = self.output_dir / "metadata.json"
            assert metadata_file.exists()
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check metadata content
            assert "timestamp" in metadata
            assert "git_info" in metadata
            assert "environment_info" in metadata
            assert "parameters_hash" in metadata
            
            # Check that timestamp is recent
            import datetime
            timestamp = datetime.datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            time_diff = abs((now - timestamp).total_seconds())
            assert time_diff < 60  # Should be within 1 minute
            
        finally:
            temp_path.unlink(missing_ok=True)
