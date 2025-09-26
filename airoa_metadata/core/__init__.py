# -*- coding: utf-8 -*-
"""
Core functionality for the AIROA Metadata Library.

This module contains the base classes and utilities used across all metadata versions.
"""

from .base import MetadataBase
from .loader import MetadataLoader

__all__ = [
    "MetadataBase",
    "MetadataLoader",
]
