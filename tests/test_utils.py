"""Tests for utility modules."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

from moduli_sampler.utils import (
    setup_logging,
    get_logger,
    setup_rng,
    get_seed_info,
    generate_deterministic_sequence,
    verify_seed_reproducibility,
    validate_file_path,
    validate_output_dir,
    ensure_file_extension,
    validate_json_file,
)


class TestLogging:
    """Test logging utilities."""

    def test_setup_logging_default(self):
        """Test logging setup with default parameters."""
        logger = setup_logging()
        
        assert logger is not None
        assert logger.name == "moduli_sampler"
        assert logger.level == 20  # INFO level
        
        # Check that console handler is added
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0

    def test_setup_logging_with_file(self):
        """Test logging setup with file handler."""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            log_file = Path(f.name)
        
        try:
            logger = setup_logging(log_file=log_file)
            
            # Check that file handler is added
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) > 0
            
            # Test logging to file
            test_message = "Test log message"
            logger.info(test_message)
            
            # Check that message was written to file
            with open(log_file, 'r') as f:
                log_content = f.read()
                assert test_message in log_content
                
        finally:
            log_file.unlink(missing_ok=True)

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        logger = setup_logging(level=10)  # DEBUG level
        
        assert logger.level == 10
        
        logger = setup_logging(level=30)  # WARNING level
        assert logger.level == 30

    def test_setup_logging_no_console(self):
        """Test logging setup without console output."""
        logger = setup_logging(console_output=False)
        
        # Check that no console handlers are added
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) == 0

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test_module")
        
        assert logger is not None
        assert logger.name == "test_module"
        
        # Should return same logger for same name
        logger2 = get_logger("test_module")
        assert logger is logger2

    def test_logging_clear_handlers(self):
        """Test that logging setup clears existing handlers."""
        logger = setup_logging()
        initial_handler_count = len(logger.handlers)
        
        # Setup logging again
        logger = setup_logging()
        
        # Should have same number of handlers (cleared and re-added)
        assert len(logger.handlers) == initial_handler_count


class TestSeedManagement:
    """Test seed and RNG management utilities."""

    def test_setup_rng_with_seed(self):
        """Test RNG setup with specific seed."""
        rng = setup_rng(seed=42)
        
        assert rng is not None
        assert isinstance(rng, np.random.RandomState)
        
        # Check that seed was set correctly
        state = rng.get_state()
        assert state[1][0] == 42

    def test_setup_rng_without_seed(self):
        """Test RNG setup without seed."""
        rng = setup_rng()
        
        assert rng is not None
        assert isinstance(rng, np.random.RandomState)
        
        # Should use current time or default seed
        state = rng.get_state()
        assert len(state[1]) > 0

    def test_setup_rng_deterministic(self):
        """Test that RNG setup is deterministic with same seed."""
        rng1 = setup_rng(seed=123)
        rng2 = setup_rng(seed=123)
        
        # Both should produce same sequence
        values1 = [rng1.randint(0, 100) for _ in range(10)]
        values2 = [rng2.randint(0, 100) for _ in range(10)]
        
        assert values1 == values2

    def test_get_seed_info(self):
        """Test seed info collection."""
        seed_info = get_seed_info()
        
        assert "python_version" in seed_info
        assert "numpy_version" in seed_info
        assert "platform" in seed_info
        assert "python_hash_seed" in seed_info
        
        # Check that versions are strings
        assert isinstance(seed_info["python_version"], str)
        assert isinstance(seed_info["numpy_version"], str)
        assert isinstance(seed_info["platform"], str)

    def test_generate_deterministic_sequence(self):
        """Test deterministic sequence generation."""
        rng = setup_rng(seed=42)
        sequence = generate_deterministic_sequence(rng, 10, 0, 100)
        
        assert len(sequence) == 10
        assert all(0 <= x <= 100 for x in sequence)
        
        # Should be deterministic
        rng2 = setup_rng(seed=42)
        sequence2 = generate_deterministic_sequence(rng2, 10, 0, 100)
        assert sequence == sequence2

    def test_verify_seed_reproducibility(self):
        """Test seed reproducibility verification."""
        rng = setup_rng(seed=42)
        
        # Generate some random values
        values1 = [rng.randint(0, 100) for _ in range(5)]
        
        # Reset RNG with same seed
        rng2 = setup_rng(seed=42)
        values2 = [rng2.randint(0, 100) for _ in range(5)]
        
        # Verify reproducibility
        result = verify_seed_reproducibility(values1, values2)
        assert result["is_reproducible"] is True
        assert result["difference_count"] == 0

    def test_verify_seed_reproducibility_failure(self):
        """Test seed reproducibility verification with different values."""
        values1 = [1, 2, 3, 4, 5]
        values2 = [1, 2, 3, 4, 6]  # Different last value
        
        result = verify_seed_reproducibility(values1, values2)
        assert result["is_reproducible"] is False
        assert result["difference_count"] == 1
        assert result["differences"] == [4]  # Index of difference


class TestFileValidation:
    """Test file and directory validation utilities."""

    def test_validate_file_path_existing(self):
        """Test file path validation for existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = validate_file_path(temp_path)
            assert result["is_valid"] is True
            assert result["exists"] is True
            assert result["is_file"] is True
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_file_path_nonexistent(self):
        """Test file path validation for non-existent file."""
        temp_path = Path("/nonexistent/file.txt")
        
        result = validate_file_path(temp_path)
        assert result["is_valid"] is False
        assert result["exists"] is False
        assert result["is_file"] is False

    def test_validate_file_path_directory(self):
        """Test file path validation for directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            result = validate_file_path(temp_path)
            assert result["is_valid"] is False
            assert result["exists"] is True
            assert result["is_file"] is False

    def test_validate_output_dir_existing(self):
        """Test output directory validation for existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            result = validate_output_dir(temp_path)
            assert result["is_valid"] is True
            assert result["exists"] is True
            assert result["is_dir"] is True
            assert result["is_writable"] is True

    def test_validate_output_dir_nonexistent(self):
        """Test output directory validation for non-existent directory."""
        temp_path = Path("/nonexistent/directory")
        
        result = validate_output_dir(temp_path)
        assert result["is_valid"] is False
        assert result["exists"] is False
        assert result["is_dir"] is False

    def test_validate_output_dir_file(self):
        """Test output directory validation for file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = validate_output_dir(temp_path)
            assert result["is_valid"] is False
            assert result["exists"] is True
            assert result["is_dir"] is False
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_output_dir_unwritable(self):
        """Test output directory validation for unwritable directory."""
        # This test might not work on all systems, so we'll mock it
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('pathlib.Path.access', return_value=False):
            
            temp_path = Path("/unwritable/directory")
            result = validate_output_dir(temp_path)
            
            assert result["is_valid"] is False
            assert result["exists"] is True
            assert result["is_dir"] is True
            assert result["is_writable"] is False

    def test_ensure_file_extension(self):
        """Test file extension ensuring."""
        # Test with correct extension
        file_path = Path("test.json")
        result = ensure_file_extension(file_path, ".json")
        assert result == file_path
        
        # Test without extension
        file_path = Path("test")
        result = ensure_file_extension(file_path, ".json")
        assert result == Path("test.json")
        
        # Test with wrong extension
        file_path = Path("test.txt")
        result = ensure_file_extension(file_path, ".json")
        assert result == Path("test.txt.json")

    def test_validate_json_file_valid(self):
        """Test JSON file validation for valid file."""
        valid_json = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            json.dump(valid_json, f)
        
        try:
            result = validate_json_file(temp_path)
            assert result["is_valid"] is True
            assert result["is_json"] is True
            assert result["data"] == valid_json
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_json_file_invalid(self):
        """Test JSON file validation for invalid file."""
        invalid_json = "{ invalid json content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            f.write(invalid_json)
        
        try:
            result = validate_json_file(temp_path)
            assert result["is_valid"] is False
            assert result["is_json"] is False
            assert "error" in result
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_json_file_nonexistent(self):
        """Test JSON file validation for non-existent file."""
        temp_path = Path("/nonexistent/file.json")
        
        result = validate_json_file(temp_path)
        assert result["is_valid"] is False
        assert result["is_json"] is False
        assert "error" in result


class TestUtilityIntegration:
    """Test integration between utility functions."""

    def test_logging_and_validation_integration(self):
        """Test integration between logging and validation."""
        # Setup logging
        logger = setup_logging()
        
        # Test file validation with logging
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = validate_file_path(temp_path)
            
            # Log validation result
            if result["is_valid"]:
                logger.info(f"File {temp_path} is valid")
            else:
                logger.warning(f"File {temp_path} is invalid: {result}")
            
            assert result["is_valid"] is True
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_seed_and_validation_integration(self):
        """Test integration between seed management and validation."""
        # Setup RNG
        rng = setup_rng(seed=42)
        
        # Generate deterministic sequence
        sequence = generate_deterministic_sequence(rng, 5, 0, 10)
        
        # Validate that sequence is within bounds
        assert all(0 <= x <= 10 for x in sequence)
        
        # Verify reproducibility
        rng2 = setup_rng(seed=42)
        sequence2 = generate_deterministic_sequence(rng2, 5, 0, 10)
        
        result = verify_seed_reproducibility(sequence, sequence2)
        assert result["is_reproducible"] is True

    def test_file_validation_chain(self):
        """Test chain of file validation operations."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Validate output directory
            dir_result = validate_output_dir(temp_path)
            assert dir_result["is_valid"] is True
            
            # Create a file in the directory
            test_file = temp_path / "test.json"
            test_data = {"test": "data"}
            
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            
            # Validate the file
            file_result = validate_file_path(test_file)
            assert file_result["is_valid"] is True
            
            # Validate JSON content
            json_result = validate_json_file(test_file)
            assert json_result["is_valid"] is True
            assert json_result["data"] == test_data


class TestUtilityEdgeCases:
    """Test edge cases in utility functions."""

    def test_setup_rng_extreme_seeds(self):
        """Test RNG setup with extreme seed values."""
        # Test with very large seed
        rng = setup_rng(seed=2**63 - 1)
        assert rng is not None
        
        # Test with negative seed
        rng = setup_rng(seed=-42)
        assert rng is not None
        
        # Test with zero seed
        rng = setup_rng(seed=0)
        assert rng is not None

    def test_validate_file_path_special_characters(self):
        """Test file path validation with special characters."""
        # Test with spaces
        temp_path = Path("test file with spaces.txt")
        
        # This should not raise an error
        result = validate_file_path(temp_path)
        assert result["is_valid"] is False  # File doesn't exist
        assert result["exists"] is False

    def test_validate_output_dir_permissions(self):
        """Test output directory validation with permission issues."""
        # This test might not work on all systems
        # We'll test the logic with mocked permissions
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('pathlib.Path.access', side_effect=OSError("Permission denied")):
            
            temp_path = Path("/restricted/directory")
            result = validate_output_dir(temp_path)
            
            assert result["is_valid"] is False
            assert result["is_writable"] is False

    def test_generate_deterministic_sequence_edge_cases(self):
        """Test deterministic sequence generation with edge cases."""
        rng = setup_rng(seed=42)
        
        # Test with zero length
        sequence = generate_deterministic_sequence(rng, 0, 0, 100)
        assert len(sequence) == 0
        
        # Test with single element
        sequence = generate_deterministic_sequence(rng, 1, 0, 100)
        assert len(sequence) == 1
        assert 0 <= sequence[0] <= 100
        
        # Test with equal min and max
        sequence = generate_deterministic_sequence(rng, 5, 42, 42)
        assert len(sequence) == 5
        assert all(x == 42 for x in sequence)

    def test_verify_seed_reproducibility_empty_sequences(self):
        """Test seed reproducibility verification with empty sequences."""
        # Test with empty sequences
        result = verify_seed_reproducibility([], [])
        assert result["is_reproducible"] is True
        assert result["difference_count"] == 0
        
        # Test with one empty sequence
        result = verify_seed_reproducibility([1, 2, 3], [])
        assert result["is_reproducible"] is False
        assert result["difference_count"] == 3

    def test_logging_with_extreme_levels(self):
        """Test logging setup with extreme levels."""
        # Test with very low level
        logger = setup_logging(level=0)  # NOTSET
        assert logger.level == 0
        
        # Test with very high level
        logger = setup_logging(level=50)  # CRITICAL
        assert logger.level == 50
        
        # Test with invalid level (should handle gracefully)
        logger = setup_logging(level=999)
        assert logger.level == 999  # Should accept any level


# Import logging at the top for the tests
import logging
