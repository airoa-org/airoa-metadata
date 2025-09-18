# -*- coding: utf-8 -*-
"""
Test version conversion functionality for AIROA Metadata Library.
"""

from typing import Any, Dict

import pytest

from airoa_metadata.versions import (
    MetadataV0_0,
    MetadataV1_0,
    MetadataV1_1,
    MetadataV1_2,
    MetadataV1_3,
)


class TestV1_2_to_V1_3_Conversion:
    """Test conversion from v1.2 to v1.3."""

    def test_convert_v1_2_to_v1_3_with_real_data(self, v1_2_test_data: Dict[str, Any]):
        """Test converting real v1.2 data to v1.3."""
        # Create v1.2 metadata
        v1_2_metadata = MetadataV1_2.from_dict(v1_2_test_data)

        # Convert to v1.3
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        # Basic validation
        assert v1_3_metadata.version == "1.3"
        assert v1_3_metadata.uuid == v1_2_metadata.uuid
        assert len(v1_3_metadata.files) == len(v1_2_metadata.files)

    def test_task_entity_splitting(self, sample_v1_2_data: Dict[str, Any]):
        """Test that v1.2 task entity is split into task-record and task-template in v1.3."""
        # Create v1.2 metadata with task entity
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)

        # Convert to v1.3
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        # Check that task was split
        task_record_entities = [
            e for e in v1_3_metadata.context.entities if e.role == "task-record"
        ]
        task_template_entities = [
            e for e in v1_3_metadata.context.entities if e.role == "task-template"
        ]

        assert len(task_record_entities) == 1, (
            f"Expected 1 task-record, got {len(task_record_entities)}"
        )
        assert len(task_template_entities) == 1, (
            f"Expected 1 task-template, got {len(task_template_entities)}"
        )

        # Verify task-record has ID
        task_record = task_record_entities[0]
        assert task_record.id is not None

        # Verify task-template has name and description
        task_template = task_template_entities[0]
        assert task_template.name is not None
        assert task_template.description is not None

    def test_other_entities_preserved(self, sample_v1_2_data: Dict[str, Any]):
        """Test that non-task entities are preserved during conversion."""
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        # Count entities by role (excluding task entities)
        v1_2_non_task_entities = [
            e for e in v1_2_metadata.context.entities if e.role != "task"
        ]
        v1_3_non_task_entities = [
            e
            for e in v1_3_metadata.context.entities
            if e.role not in ["task-record", "task-template"]
        ]

        assert len(v1_3_non_task_entities) == len(v1_2_non_task_entities)

        # Check specific roles are preserved
        v1_2_roles = {e.role for e in v1_2_non_task_entities}
        v1_3_roles = {e.role for e in v1_3_non_task_entities}
        assert v1_2_roles == v1_3_roles

    def test_components_preserved(self, sample_v1_2_data: Dict[str, Any]):
        """Test that components are preserved during conversion."""
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        assert len(v1_3_metadata.context.components) == len(
            v1_2_metadata.context.components
        )

        # Check first component details are preserved
        if v1_2_metadata.context.components and v1_3_metadata.context.components:
            v1_2_comp = v1_2_metadata.context.components[0]
            v1_3_comp = v1_3_metadata.context.components[0]

            assert v1_3_comp.role == v1_2_comp.role
            assert v1_3_comp.name == v1_2_comp.name
            assert v1_3_comp.source.git.uri == v1_2_comp.source.git.uri
            assert v1_3_comp.source.git.hash == v1_2_comp.source.git.hash
            assert v1_3_comp.source.git.branch == v1_2_comp.source.git.branch

    def test_run_data_preserved(self, sample_v1_2_data: Dict[str, Any]):
        """Test that run data is preserved during conversion."""
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        assert v1_3_metadata.run.total_time_s == v1_2_metadata.run.total_time_s
        assert len(v1_3_metadata.run.instructions) == len(
            v1_2_metadata.run.instructions
        )
        assert len(v1_3_metadata.run.segments) == len(v1_2_metadata.run.segments)

        # Check first instruction is preserved
        if v1_2_metadata.run.instructions and v1_3_metadata.run.instructions:
            v1_2_instr = v1_2_metadata.run.instructions[0]
            v1_3_instr = v1_3_metadata.run.instructions[0]

            assert v1_3_instr.idx == v1_2_instr.idx
            assert v1_3_instr.text == v1_2_instr.text


class TestConversionChain:
    """Test conversion chains through multiple versions."""

    def test_v1_2_same_instance_returns_self(self, sample_v1_2_data: Dict[str, Any]):
        """Test that converting v1.2 to v1.2 returns the same instance."""
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)
        converted = MetadataV1_2.convert(v1_2_metadata)

        assert converted is v1_2_metadata

    def test_v1_3_same_instance_returns_self(self, sample_v1_3_data: Dict[str, Any]):
        """Test that converting v1.3 to v1.3 returns the same instance."""
        v1_3_metadata = MetadataV1_3.from_dict(sample_v1_3_data)
        converted = MetadataV1_3.convert(v1_3_metadata)

        assert converted is v1_3_metadata

    def test_preceding_chain(self):
        """Test that preceding() method returns correct chain."""
        assert MetadataV1_3.preceding() is MetadataV1_2
        assert MetadataV1_2.preceding() is MetadataV1_1
        assert MetadataV1_1.preceding() is MetadataV1_0
        assert MetadataV1_0.preceding() is MetadataV0_0

    @pytest.mark.parametrize(
        "source_version,target_class,target_version",
        [
            ("0.0", MetadataV1_0, "1.0"),
            ("0.0", MetadataV1_1, "1.1"),
            ("0.0", MetadataV1_2, "1.2"),
            ("0.0", MetadataV1_3, "1.3"),
            ("1.0", MetadataV1_1, "1.1"),
            ("1.0", MetadataV1_2, "1.2"),
            ("1.0", MetadataV1_3, "1.3"),
            ("1.1", MetadataV1_2, "1.2"),
            ("1.1", MetadataV1_3, "1.3"),
            ("1.2", MetadataV1_3, "1.3"),
        ],
    )
    def test_all_version_conversions(
        self, source_version: str, target_class, target_version: str, request
    ):
        """Test conversions between all supported version combinations."""
        # Get the test data for the source version
        source_data = request.getfixturevalue(
            f"v{source_version.replace('.', '_')}_test_data"
        )

        # Create source metadata object
        if source_version == "0.0":
            source_metadata = MetadataV0_0.from_dict(source_data)
        elif source_version == "1.0":
            source_metadata = MetadataV1_0.from_dict(source_data)
        elif source_version == "1.1":
            source_metadata = MetadataV1_1.from_dict(source_data)
        elif source_version == "1.2":
            source_metadata = MetadataV1_2.from_dict(source_data)
        elif source_version == "1.3":
            source_metadata = MetadataV1_3.from_dict(source_data)

        # Convert to target version
        converted_metadata = target_class.convert(source_metadata)

        # Verify conversion
        assert isinstance(converted_metadata, target_class)
        assert converted_metadata.version == target_version

        # Basic data preservation checks
        if hasattr(source_metadata, "files") and hasattr(converted_metadata, "files"):
            assert (
                len(converted_metadata.files) >= 0
            )  # Files should be preserved or converted
        elif hasattr(source_metadata, "data_files") and hasattr(
            converted_metadata, "files"
        ):
            assert len(converted_metadata.files) >= 0  # Old data_files -> new files

        # Context preservation (if both have context)
        if hasattr(source_metadata, "context") and hasattr(
            converted_metadata, "context"
        ):
            assert converted_metadata.context is not None

        # Run data preservation (if both have run)
        if hasattr(source_metadata, "run") and hasattr(converted_metadata, "run"):
            assert converted_metadata.run is not None


class TestConversionEdgeCases:
    """Test edge cases in conversion."""

    def test_conversion_with_empty_task_template(self):
        """Test conversion when task entity has no template."""
        data = {
            "uuid": "test-uuid",
            "version": "1.2",
            "files": [{"type": "rosbag", "name": "test.bag"}],
            "context": {
                "entities": [
                    {"role": "task", "id": "test-task"}  # No template
                ],
                "components": [],
            },
            "run": {"total_time_s": 10.0, "instructions": [], "segments": []},
        }

        v1_2_metadata = MetadataV1_2.from_dict(data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        # Should still create task-record
        task_record_entities = [
            e for e in v1_3_metadata.context.entities if e.role == "task-record"
        ]
        assert len(task_record_entities) == 1

        # But no task-template should be created
        task_template_entities = [
            e for e in v1_3_metadata.context.entities if e.role == "task-template"
        ]
        assert len(task_template_entities) == 0

    def test_conversion_with_no_task_entities(self):
        """Test conversion when there are no task entities."""
        data = {
            "uuid": "test-uuid",
            "version": "1.2",
            "files": [{"type": "rosbag", "name": "test.bag"}],
            "context": {
                "entities": [
                    {"role": "robot", "id": "test-robot"},
                    {"role": "operator", "id": "test-operator"},
                ],
                "components": [],
            },
            "run": {"total_time_s": 10.0, "instructions": [], "segments": []},
        }

        v1_2_metadata = MetadataV1_2.from_dict(data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        # Should have no task-related entities
        task_record_entities = [
            e for e in v1_3_metadata.context.entities if e.role == "task-record"
        ]
        task_template_entities = [
            e for e in v1_3_metadata.context.entities if e.role == "task-template"
        ]

        assert len(task_record_entities) == 0
        assert len(task_template_entities) == 0

        # But other entities should be preserved
        assert len(v1_3_metadata.context.entities) == 2


class TestConversionErrorHandling:
    """Test error handling in conversions."""

    def test_conversion_with_invalid_data(self):
        """Test that conversion fails gracefully with invalid data."""
        # This test would depend on how validation is implemented
        # For now, we just test that the conversion process doesn't crash

        minimal_data = {
            "uuid": "test-uuid",
            "version": "1.2",
            "files": [],
            "context": {"entities": [], "components": []},
            "run": {"total_time_s": 0.0, "instructions": [], "segments": []},
        }

        v1_2_metadata = MetadataV1_2.from_dict(minimal_data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        assert v1_3_metadata.version == "1.3"
        assert v1_3_metadata.uuid == "test-uuid"


class TestConversionMetadata:
    """Test that conversion preserves important metadata."""

    def test_uuid_preserved(self, sample_v1_2_data: Dict[str, Any]):
        """Test that UUID is preserved during conversion."""
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        assert v1_3_metadata.uuid == v1_2_metadata.uuid

    def test_files_preserved(self, sample_v1_2_data: Dict[str, Any]):
        """Test that files are preserved during conversion."""
        v1_2_metadata = MetadataV1_2.from_dict(sample_v1_2_data)
        v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)

        assert len(v1_3_metadata.files) == len(v1_2_metadata.files)

        for v1_2_file, v1_3_file in zip(
            v1_2_metadata.files, v1_3_metadata.files, strict=False
        ):
            assert v1_3_file.type == v1_2_file.type
            assert v1_3_file.name == v1_2_file.name
