# -*- coding: utf-8 -*-
"""
Test version-specific functionality for AIROA Metadata Library.
"""

import json
import pytest
from typing import Dict, Any

from airoa_metadata.versions import (
    MetadataV0_0,
    MetadataV1_0,
    MetadataV1_1,
    MetadataV1_2,
    MetadataV1_3,
)


class TestMetadataV1_3:
    """Test MetadataV1_3 functionality."""

    def test_from_dict_with_real_data(self, v1_3_test_data: Dict[str, Any]):
        """Test creating MetadataV1_3 from real test data."""
        metadata = MetadataV1_3.from_dict(v1_3_test_data)

        assert metadata.uuid == v1_3_test_data["uuid"]
        assert metadata.version == "1.3"
        assert len(metadata.files) == len(v1_3_test_data["files"])
        assert len(metadata.context.entities) == len(
            v1_3_test_data["context"]["entities"]
        )
        assert len(metadata.context.components) == len(
            v1_3_test_data["context"]["components"]
        )
        assert len(metadata.run.instructions) == len(
            v1_3_test_data["run"]["instructions"]
        )
        assert len(metadata.run.segments) == len(v1_3_test_data["run"]["segments"])

    def test_from_dict_with_sample_data(self, sample_v1_3_data: Dict[str, Any]):
        """Test creating MetadataV1_3 from sample data."""
        metadata = MetadataV1_3.from_dict(sample_v1_3_data)

        assert metadata.uuid == sample_v1_3_data["uuid"]
        assert metadata.version == "1.3"
        assert len(metadata.files) == 1
        assert metadata.files[0].type == "rosbag"
        assert metadata.files[0].name == "test.bag"

    def test_to_json_serialization(self, v1_3_test_data: Dict[str, Any]):
        """Test JSON serialization."""
        metadata = MetadataV1_3.from_dict(v1_3_test_data)
        json_str = metadata.to_json()

        assert json_str is not None
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_entities_structure(self, v1_3_test_data: Dict[str, Any]):
        """Test that entities are correctly parsed."""
        metadata = MetadataV1_3.from_dict(v1_3_test_data)

        # Check different entity roles
        entity_roles = [entity.role for entity in metadata.context.entities]
        assert "robot" in entity_roles
        assert "operator" in entity_roles
        assert "task-record" in entity_roles
        assert "task-template" in entity_roles

    def test_components_structure(self, v1_3_test_data: Dict[str, Any]):
        """Test that components are correctly parsed."""
        metadata = MetadataV1_3.from_dict(v1_3_test_data)

        assert len(metadata.context.components) > 0

        for component in metadata.context.components:
            assert component.role is not None
            assert component.name is not None
            assert component.source is not None
            assert component.source.git is not None
            assert component.source.git.uri is not None
            assert component.source.git.hash is not None
            assert component.source.git.branch is not None

    def test_segments_structure(self, v1_3_test_data: Dict[str, Any]):
        """Test that segments are correctly parsed."""
        metadata = MetadataV1_3.from_dict(v1_3_test_data)

        assert len(metadata.run.segments) > 0

        for segment in metadata.run.segments:
            assert segment.start_time is not None
            assert segment.end_time is not None
            assert segment.instruction_idx is not None
            assert segment.success is not None
            assert segment.controlled_by is not None


class TestMetadataV1_2:
    """Test MetadataV1_2 functionality."""

    def test_from_dict_with_real_data(self, v1_2_test_data: Dict[str, Any]):
        """Test creating MetadataV1_2 from real test data."""
        metadata = MetadataV1_2.from_dict(v1_2_test_data)

        assert metadata.uuid == v1_2_test_data["uuid"]
        assert metadata.version == "1.2"
        assert len(metadata.files) == len(v1_2_test_data["files"])
        assert len(metadata.context.entities) == len(
            v1_2_test_data["context"]["entities"]
        )
        assert len(metadata.context.components) == len(
            v1_2_test_data["context"]["components"]
        )

    def test_from_dict_with_sample_data(self, sample_v1_2_data: Dict[str, Any]):
        """Test creating MetadataV1_2 from sample data."""
        metadata = MetadataV1_2.from_dict(sample_v1_2_data)

        assert metadata.uuid == sample_v1_2_data["uuid"]
        assert metadata.version == "1.2"
        assert len(metadata.files) == 1

    def test_task_entity_with_template(self, v1_2_test_data: Dict[str, Any]):
        """Test that task entity with template is correctly parsed."""
        metadata = MetadataV1_2.from_dict(v1_2_test_data)

        # Find task entity
        task_entities = [e for e in metadata.context.entities if e.role == "task"]
        assert len(task_entities) == 1

        task_entity = task_entities[0]
        assert task_entity.id is not None
        assert task_entity.template is not None
        assert task_entity.template.name is not None
        assert task_entity.template.description is not None

    def test_to_json_serialization(self, v1_2_test_data: Dict[str, Any]):
        """Test JSON serialization."""
        metadata = MetadataV1_2.from_dict(v1_2_test_data)
        json_str = metadata.to_json()

        assert json_str is not None
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)


class TestMetadataV1_1:
    """Test MetadataV1_1 functionality."""

    def test_from_dict_with_real_data(self, v1_1_test_data: Dict[str, Any]):
        """Test creating MetadataV1_1 from real test data."""
        metadata = MetadataV1_1.from_dict(v1_1_test_data)

        assert metadata.version == "1.1"
        assert len(metadata.files) > 0
        assert metadata.context is not None
        assert metadata.run is not None

    def test_to_json_serialization(self, v1_1_test_data: Dict[str, Any]):
        """Test JSON serialization."""
        metadata = MetadataV1_1.from_dict(v1_1_test_data)
        json_str = metadata.to_json()

        assert json_str is not None
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)


class TestMetadataV1_0:
    """Test MetadataV1_0 functionality."""

    def test_from_dict_with_real_data(self, v1_0_test_data: Dict[str, Any]):
        """Test creating MetadataV1_0 from real test data."""
        metadata = MetadataV1_0.from_dict(v1_0_test_data)

        assert metadata.version == "1.0"
        assert metadata.hsr_id is not None
        assert len(metadata.instructions) > 0
        assert metadata.bag_path is not None

    def test_to_json_serialization(self, v1_0_test_data: Dict[str, Any]):
        """Test JSON serialization."""
        metadata = MetadataV1_0.from_dict(v1_0_test_data)
        json_str = metadata.to_json()

        assert json_str is not None
        assert isinstance(json_str, str)


class TestMetadataV0_0:
    """Test MetadataV0_0 functionality."""

    def test_from_dict_with_real_data(self, v0_0_test_data: Dict[str, Any]):
        """Test creating MetadataV0_0 from real test data."""
        metadata = MetadataV0_0.from_dict(v0_0_test_data)

        assert metadata.version == "0.0"
        assert metadata.bag_path is not None
        assert metadata.data is not None

    def test_to_json_serialization(self, v0_0_test_data: Dict[str, Any]):
        """Test JSON serialization."""
        metadata = MetadataV0_0.from_dict(v0_0_test_data)
        json_str = metadata.to_json()

        assert json_str is not None
        assert isinstance(json_str, str)


class TestVersionValidation:
    """Test validation across all versions."""

    @pytest.mark.parametrize(
        "version_class,test_data_fixture",
        [
            (MetadataV1_3, "v1_3_test_data"),
            (MetadataV1_2, "v1_2_test_data"),
        ],
    )
    def test_version_validation(self, version_class, test_data_fixture, request):
        """Test that version validation works correctly."""
        test_data = request.getfixturevalue(test_data_fixture)
        metadata = version_class.from_dict(test_data)

        # Verify should not raise exception
        metadata.verify()

    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        invalid_data = {
            "version": "1.3", 
            "files": "not_a_list",  # Should be a list
            "context": {"entities": "not_a_list"}  # Should be a list
        }

        with pytest.raises(Exception):
            MetadataV1_3.from_dict(invalid_data)


class TestVersionProperties:
    """Test version-specific properties."""

    def test_v1_3_has_hierarchical_entities(self, sample_v1_3_data: Dict[str, Any]):
        """Test that v1.3 supports hierarchical entity structure."""
        metadata = MetadataV1_3.from_dict(sample_v1_3_data)

        # Should have separate context structure
        assert hasattr(metadata, "context")
        assert hasattr(metadata.context, "entities")
        assert hasattr(metadata.context, "components")

    def test_v1_2_has_task_templates(self, sample_v1_2_data: Dict[str, Any]):
        """Test that v1.2 supports task templates."""
        metadata = MetadataV1_2.from_dict(sample_v1_2_data)

        task_entities = [e for e in metadata.context.entities if e.role == "task"]
        if task_entities:
            task_entity = task_entities[0]
            assert hasattr(task_entity, "template")
            if task_entity.template:
                assert hasattr(task_entity.template, "name")
                assert hasattr(task_entity.template, "description")

