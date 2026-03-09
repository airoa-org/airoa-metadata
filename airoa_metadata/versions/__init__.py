# -*- coding: utf-8 -*-
"""
Version-specific implementations for the AIROA Metadata Library.

Each module in this package provides dataclass implementations for a specific
metadata schema version, along with conversion utilities.
"""

from .v0_0 import MetadataV0_0
from .v1_0 import MetadataV1_0
from .v1_1 import MetadataV1_1
from .v1_2 import MetadataV1_2
from .v1_3 import MetadataV1_3
from .v2_0 import MetadataV2_0

# Enhanced version registry with schema paths
VERSION_REGISTRY = {
    "0.0": {
        "class": MetadataV0_0,
        "schema": "v0_0.json",
    },
    "1.0": {
        "class": MetadataV1_0,
        "schema": "v1_0.json",
    },
    "1.1": {
        "class": MetadataV1_1,
        "schema": "v1_1.json",
    },
    "1.2": {
        "class": MetadataV1_2,
        "schema": "v1_2.json",
    },
    "1.3": {
        "class": MetadataV1_3,
        "schema": "v1_3.json",
    },
    "2.0": {
        "class": MetadataV2_0,
        "schema": "v2_0.json",
    },
}

# Backward compatibility - class-only mapping
VERSIONS = {version: info["class"] for version, info in VERSION_REGISTRY.items()}

# Latest version alias
LATEST_VERSION = "2.0"
MetadataLatest = MetadataV2_0

__all__ = [
    "MetadataV0_0",
    "MetadataV1_0",
    "MetadataV1_1",
    "MetadataV1_2",
    "MetadataV1_3",
    "MetadataV2_0",
    "MetadataLatest",
    "VERSIONS",
    "VERSION_REGISTRY",
    "LATEST_VERSION",
]
