# -*- coding: utf-8 -*-
"""
JSON schema files and utilities for the AIROA Metadata Library.

This module provides access to JSON schema files for validation
and schema-related utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict


def get_schema_path(version: str) -> Path:
    """Get the path to a schema file for a specific version."""
    schema_file = f"v{version.replace('.', '_')}.json"
    return Path(__file__).parent / schema_file


def load_schema(version: str) -> Dict[str, Any]:
    """Load a JSON schema for a specific version."""
    schema_path = get_schema_path(version)
    with open(schema_path, "r") as f:
        return json.load(f)


# Available schema versions
AVAILABLE_SCHEMAS = ["0.0", "1.0", "1.1", "1.2", "1.3"]

__all__ = [
    "get_schema_path",
    "load_schema",
    "AVAILABLE_SCHEMAS",
]
