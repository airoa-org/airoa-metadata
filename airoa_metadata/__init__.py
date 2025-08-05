# -*- coding: utf-8 -*-
"""
AIROA Metadata Library

A Python library for handling versioned metadata for robotic data collection.
Supports multiple metadata schema versions with automatic conversion between versions.

Copyright (c) Tokyo University Matsuo Iwasawa Laboratory, Petr Khrapchenkov
"""

__version__ = "1.3.0"
__author__ = "Petr Khrapchenkov"

# Core functionality
from .core.base import MetadataBase
from .core.loader import MetadataLoader

# Version-specific implementations
from .versions.v0_0 import MetadataV0_0
from .versions.v1_0 import MetadataV1_0
from .versions.v1_1 import MetadataV1_1
from .versions.v1_2 import MetadataV1_2
from .versions.v1_3 import MetadataV1_3

# Convenience aliases
MetadataLatest = MetadataV1_3
Metadata = MetadataLatest  # Alias for the latest stable version

# Public API
__all__ = [
    # Core classes
    "MetadataBase",
    "MetadataLoader",
    # Version-specific classes
    "MetadataV0_0",
    "MetadataV1_0",
    "MetadataV1_1",
    "MetadataV1_2",
    "MetadataV1_3",
    # Convenience aliases
    "MetadataLatest",
    "Metadata",
    # Package info
    "__version__",
    "__author__",
]
