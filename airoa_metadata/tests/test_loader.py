# -*- coding: utf-8 -*-
"""
Test MetadataLoader functionality for AIROA Metadata Library.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import mock_open, patch

from airoa_metadata.core.loader import MetadataLoader
from airoa_metadata.versions import (
    MetadataV0_0,
    MetadataV1_0,
    MetadataV1_1,
    MetadataV1_2,
    MetadataV1_3,
)


class TestMetadataLoaderVersionMapping:
    """Test MetadataLoader version mapping."""

    def test_version_map_contains_all_versions(self):
        """Test that version_map contains all expected versions."""
        expected_versions = {"0.0", "1.0", "1.1", "1.2", "1.3"}
        actual_versions = set(MetadataLoader.get_version_map().keys())

        assert expected_versions == actual_versions

    def test_version_map_classes(self):
        """Test that version_map maps to correct classes."""
        expected_mapping = {
            "0.0": MetadataV0_0,
            "1.0": MetadataV1_0,
            "1.1": MetadataV1_1,
            "1.2": MetadataV1_2,
            "1.3": MetadataV1_3,
        }

        version_map = MetadataLoader.get_version_map()
        for version, expected_class in expected_mapping.items():
            actual_class, _ = version_map[version]
            assert actual_class is expected_class


class TestMetadataLoaderFromDict:
    """Test MetadataLoader.load_from_dict functionality."""

    def test_load_from_dict_v1_3(self, v1_3_test_data: Dict[str, Any]):
        """Test loading v1.3 data from dict."""
        metadata = MetadataLoader.load_from_dict(v1_3_test_data)

        assert isinstance(metadata, MetadataV1_3)
        assert metadata.version == "1.3"
        assert metadata.uuid == v1_3_test_data["uuid"]

    def test_load_from_dict_v1_2(self, v1_2_test_data: Dict[str, Any]):
        """Test loading v1.2 data from dict."""
        metadata = MetadataLoader.load_from_dict(v1_2_test_data)

        assert isinstance(metadata, MetadataV1_2)
        assert metadata.version == "1.2"
        assert metadata.uuid == v1_2_test_data["uuid"]

    @pytest.mark.parametrize(
        "version,expected_class",
        [
            ("1.3", MetadataV1_3),
            ("1.2", MetadataV1_2),
            ("1.1", MetadataV1_1),
            ("1.0", MetadataV1_0),
            ("0.0", MetadataV0_0),
        ],
    )
    def test_load_from_dict_version_detection(
        self, version, expected_class, sample_v1_3_data
    ):
        """Test that loader correctly detects and uses appropriate class for each version."""
        # Modify sample data to have the desired version
        test_data = sample_v1_3_data.copy()
        test_data["version"] = version

        # For older versions, we might need to adjust the data structure
        if version in ["0.0", "1.0", "1.1"]:
            # These versions have different structure, so we'll just test with minimal data
            test_data = {
                "version": version,
                "data_files": ["test.bag"],
                "instructions": ["test instruction"],
                "segments": [],
            }
            # Add version-specific required fields
            if version in ["1.0", "1.1"]:
                test_data.update(
                    {
                        "robot": {"model": "test"},
                        "task": {"template": {"name": "test", "instructions": []}},
                    }
                )
                if version == "1.1":
                    test_data["data"] = {"segments": []}

        # Skip validation for this test by mocking it
        with patch.object(MetadataLoader, "_validate_with_schema"):
            metadata = MetadataLoader.load_from_dict(test_data)
            assert isinstance(metadata, expected_class)
            assert metadata.version == version

    def test_load_from_dict_missing_version(self):
        """Test that loader handles missing version field."""
        data_without_version = {"uuid": "test-uuid", "files": []}

        with pytest.raises(KeyError):
            MetadataLoader.load_from_dict(data_without_version)

    def test_load_from_dict_unsupported_version(self):
        """Test that loader handles unsupported version."""
        data_with_unsupported_version = {
            "version": "99.0",
            "uuid": "test-uuid",
            "files": [],
        }

        with pytest.raises(ValueError, match="Unsupported metadata version"):
            MetadataLoader.load_from_dict(data_with_unsupported_version)


class TestMetadataLoaderFromFile:
    """Test MetadataLoader.load_from_file functionality."""

    def test_load_from_file_success(self, v1_3_test_data: Dict[str, Any]):
        """Test successfully loading from file."""
        json_content = json.dumps(v1_3_test_data)

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch.object(MetadataLoader, "_validate_with_schema"):
                metadata = MetadataLoader.load_from_file("test.json")

                assert isinstance(metadata, MetadataV1_3)
                assert metadata.version == "1.3"
                assert metadata.uuid == v1_3_test_data["uuid"]

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            MetadataLoader.load_from_file("nonexistent.json")

    def test_load_from_file_invalid_json(self):
        """Test loading file with invalid JSON."""
        invalid_json = '{"version": "1.3", "invalid": json}'

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with pytest.raises(json.JSONDecodeError):
                MetadataLoader.load_from_file("invalid.json")

    def test_load_from_file_with_extra_keys(self, v1_3_test_data: Dict[str, Any]):
        """Test loading from file with extra keys."""
        json_content = json.dumps(v1_3_test_data)
        extra_keys = {"test_key": "test_value"}

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch.object(MetadataLoader, "_validate_with_schema"):
                metadata = MetadataLoader.load_from_file(
                    "test.json", extra_keys=extra_keys
                )

                assert isinstance(metadata, MetadataV1_3)
                assert metadata.version == "1.3"


class TestMetadataLoaderValidation:
    """Test MetadataLoader validation functionality."""

    @pytest.mark.skip(reason="Schema validation implementation details may vary")
    def test_validation_with_valid_data(self, v1_3_test_data: Dict[str, Any]):
        """Test validation with valid data."""
        # This test would depend on the actual schema validation implementation
        # Skip for now as it requires schema files to be properly set up
        pass

    @pytest.mark.skip(reason="Schema validation implementation details may vary")
    def test_validation_with_invalid_data(self):
        """Test validation with invalid data."""
        # This test would depend on the actual schema validation implementation
        # Skip for now as it requires schema files to be properly set up
        pass


class TestMetadataLoaderErrorHandling:
    """Test MetadataLoader error handling."""

    def test_load_with_malformed_data(self):
        """Test loading with malformed data structure."""
        malformed_data = {
            "version": "1.3",
            "files": "this should be a list",  # Wrong type
            "context": "this should be an object",  # Wrong type
        }

        # The exact error depends on validation implementation
        # At minimum, it should not crash silently
        with pytest.raises(Exception):
            MetadataLoader.load_from_dict(malformed_data)

    def test_load_with_none_data(self):
        """Test loading with None data."""
        with pytest.raises((TypeError, AttributeError)):
            MetadataLoader.load_from_dict(None)

    def test_load_with_empty_data(self):
        """Test loading with empty data."""
        with pytest.raises(KeyError):
            MetadataLoader.load_from_dict({})


class TestMetadataLoaderIntegration:
    """Integration tests for MetadataLoader."""

    def test_load_and_convert_workflow(self, v1_2_test_data: Dict[str, Any]):
        """Test complete workflow: load v1.2 and convert to v1.3."""
        # Load v1.2 data
        with patch.object(MetadataLoader, "_validate_with_schema"):
            v1_2_metadata = MetadataLoader.load_from_dict(v1_2_test_data)

            assert isinstance(v1_2_metadata, MetadataV1_2)
            assert v1_2_metadata.version == "1.2"

            # Convert to v1.3
            v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

            assert isinstance(v1_3_metadata, MetadataV1_3)
            assert v1_3_metadata.version == "1.3"
            assert v1_3_metadata.uuid == v1_2_metadata.uuid

    def test_round_trip_serialization(self, v1_3_test_data: Dict[str, Any]):
        """Test loading data, serializing it, and loading again."""
        with patch.object(MetadataLoader, "_validate_with_schema"):
            # Load original data
            metadata1 = MetadataLoader.load_from_dict(v1_3_test_data)

            # Serialize to JSON
            json_str = metadata1.to_json()

            # Parse back to dict
            parsed_data = json.loads(json_str)

            # Load again
            metadata2 = MetadataLoader.load_from_dict(parsed_data)

            # Verify they're equivalent
            assert metadata2.version == metadata1.version
            assert metadata2.uuid == metadata1.uuid
            assert len(metadata2.files) == len(metadata1.files)

