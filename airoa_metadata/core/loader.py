# -*- coding: utf-8 -*-
# Copyright 2025-2026 AI Robot Association (AIRoA)
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
from typing import Any, Dict, Optional

import jsonschema

from ..versions import VERSION_REGISTRY
from .base import MetadataBase

logger = logging.getLogger(__name__)


class MetadataLoader:
    """
    Loader that validates the input dict using a JSON Schema and instantiates the correct metadata class.
    """

    @classmethod
    def get_version_map(cls):
        """Dynamic version map built from centralized registry."""
        return {
            version: (info["class"], f"../schemas/{info['schema']}")
            for version, info in VERSION_REGISTRY.items()
        }

    @classmethod
    def load_from_dict(
        cls,
        data: Dict[str, Any],
        extra_keys: Optional[Dict[str, Any]] = None,
        verify: bool = True,
        version_override: Optional[str] = None,
    ) -> MetadataBase:
        if data is None:
            raise TypeError("Data cannot be None")

        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")

        version = data.get("schema_version") or data.get("version")
        if version is None:
            raise KeyError("Version field not found in metadata")
        logger.info(f"Detected metadata version {version}")

        version_map = cls.get_version_map()
        if version not in version_map:
            raise ValueError(f"Unsupported metadata version: {version}")

        cls._validate_with_schema(data, version)
        meta_class, _ = version_map[version]
        meta_obj = meta_class.from_dict(data, extra_keys=extra_keys)

        return meta_obj

    @classmethod
    def _validate_with_schema(cls, data: Dict[str, Any], version: str) -> None:
        """
        Validate the given data dict against the JSON Schema found at the relative path.
        The path is relative to this file.
        """
        version_map = cls.get_version_map()
        if version not in version_map:
            raise ValueError(f"Unsupported metadata version: {version}")
        _, schema_relative_path = version_map[version]

        base_dir = os.path.dirname(__file__)
        schema_path = os.path.join(base_dir, schema_relative_path)
        with open(schema_path, "r") as f:
            schema = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        logger.info(
            f"[VALIDATION] Data validated against schema {schema_relative_path}."
        )

    @classmethod
    def validate_data(cls, data: Dict[str, Any], version_override: str = "0.0") -> None:
        """
        Validate the given data dict against the JSON Schema found at the relative path.
        The path is relative to this file.
        """
        version = data.get("schema_version") or data.get("version", "0.0")
        if version is None:
            raise ValueError("Version field not found in metadata.")
        cls._validate_with_schema(data, version)

    @classmethod
    def load_from_file(
        cls,
        file_path: str,
        extra_keys: Optional[Dict[str, Any]] = None,
        verify: bool = True,
    ) -> MetadataBase:
        """Load metadata from a JSON file."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}") from None
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in file {file_path}", e.doc, e.pos
            ) from e

        return cls.load_from_dict(data, extra_keys=extra_keys, verify=verify)
