# -*- coding: utf-8 -*-
"""
Test schema functionality for AIROA Metadata Library.
"""

import json
from pathlib import Path

import pytest

from airoa_metadata.schemas import AVAILABLE_SCHEMAS, get_schema_path, load_schema


class TestSchemaUtilities:
    """Test schema utility functions."""

    def test_available_schemas_list(self):
        """Test that AVAILABLE_SCHEMAS contains expected versions."""
        expected_schemas = ["0.0", "1.0", "1.1", "1.2", "1.3"]
        assert set(AVAILABLE_SCHEMAS) == set(expected_schemas)

    @pytest.mark.parametrize("version", ["0.0", "1.0", "1.1", "1.2", "1.3"])
    def test_get_schema_path(self, version):
        """Test getting schema path for each version."""
        path = get_schema_path(version)

        assert isinstance(path, Path)
        assert path.name == f"v{version.replace('.', '_')}.json"
        assert path.exists(), f"Schema file not found: {path}"

    @pytest.mark.parametrize("version", ["0.0", "1.0", "1.1", "1.2", "1.3"])
    def test_load_schema(self, version):
        """Test loading schema for each version."""
        schema = load_schema(version)

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "type" in schema
        assert schema["type"] == "object"

    def test_load_schema_invalid_version(self):
        """Test loading schema with invalid version."""
        with pytest.raises(FileNotFoundError):
            load_schema("99.0")

    def test_schema_file_format(self):
        """Test that schema files are valid JSON."""
        for version in AVAILABLE_SCHEMAS:
            schema_path = get_schema_path(version)

            with open(schema_path, "r") as f:
                schema_content = f.read()

            # Should be valid JSON
            schema = json.loads(schema_content)
            assert isinstance(schema, dict)

    def test_schema_structure(self):
        """Test that schemas have expected structure."""
        for version in AVAILABLE_SCHEMAS:
            schema = load_schema(version)

            # All schemas should have these basic fields
            assert "$schema" in schema
            assert "type" in schema
            assert "properties" in schema

            # Should be a JSON Schema draft-07
            assert "http://json-schema.org/draft-07/schema#" in schema["$schema"]


class TestSchemaContent:
    """Test schema content for specific versions."""

    def test_v1_3_schema_structure(self):
        """Test v1.3 schema has expected structure."""
        schema = load_schema("1.3")

        required_props = ["uuid", "version", "files", "context", "run"]
        assert "required" in schema
        assert set(schema["required"]) == set(required_props)

        # Check that it has the hierarchical structure
        properties = schema["properties"]
        assert "context" in properties
        assert "run" in properties

        # Context should have entities and components
        if "context" in properties:
            context_props = properties["context"].get("properties", {})
            assert "entities" in context_props
            assert "components" in context_props

    def test_v1_2_schema_structure(self):
        """Test v1.2 schema has expected structure."""
        schema = load_schema("1.2")

        required_props = ["uuid", "version", "files", "context", "run"]
        assert "required" in schema
        assert set(schema["required"]) == set(required_props)

        # Should be similar to v1.3 but with task entity structure
        properties = schema["properties"]
        assert "context" in properties
        assert "run" in properties

    def test_schema_definitions(self):
        """Test that schemas have proper definitions section."""
        for version in ["1.2", "1.3"]:  # Newer versions have definitions
            schema = load_schema(version)

            if "definitions" in schema:
                definitions = schema["definitions"]

                # Should have common definitions
                expected_definitions = [
                    "file",
                    "entity",
                    "component",
                    "instruction",
                    "segment",
                ]
                for definition in expected_definitions:
                    assert definition in definitions, (
                        f"Missing {definition} in {version} schema"
                    )

                    # Each definition should be an object
                    assert definitions[definition]["type"] == "object"
                    assert "properties" in definitions[definition]


class TestSchemaVersionDifferences:
    """Test differences between schema versions."""

    def test_v1_2_vs_v1_3_entity_roles(self):
        """Test entity role differences between v1.2 and v1.3."""
        v1_2_schema = load_schema("1.2")
        v1_3_schema = load_schema("1.3")

        # Get entity role enums
        v1_2_entity_roles = set()
        v1_3_entity_roles = set()

        if "definitions" in v1_2_schema and "entity" in v1_2_schema["definitions"]:
            entity_def = v1_2_schema["definitions"]["entity"]
            if "properties" in entity_def and "role" in entity_def["properties"]:
                role_def = entity_def["properties"]["role"]
                if "enum" in role_def:
                    v1_2_entity_roles = set(role_def["enum"])

        if "definitions" in v1_3_schema and "entity" in v1_3_schema["definitions"]:
            entity_def = v1_3_schema["definitions"]["entity"]
            if "properties" in entity_def and "role" in entity_def["properties"]:
                role_def = entity_def["properties"]["role"]
                if "enum" in role_def:
                    v1_3_entity_roles = set(role_def["enum"])

        # v1.2 should have "task" role, v1.3 should have "task-record" and "task-template"
        if v1_2_entity_roles and v1_3_entity_roles:
            assert "task" in v1_2_entity_roles
            assert "task" not in v1_3_entity_roles
            assert "task-record" in v1_3_entity_roles
            assert "task-template" in v1_3_entity_roles

    def test_schema_evolution_consistency(self):
        """Test that newer schemas maintain backward compatibility concepts."""
        # All modern schemas should have files, context, run structure
        for version in ["1.2", "1.3"]:
            schema = load_schema(version)
            properties = schema.get("properties", {})

            # Core structure should be consistent
            assert "files" in properties
            assert "context" in properties
            assert "run" in properties

            # Context should have entities and components
            context_props = properties["context"].get("properties", {})
            assert "entities" in context_props
            assert "components" in context_props
