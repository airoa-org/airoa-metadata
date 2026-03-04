# -*- coding: utf-8 -*-
"""
Test imports and package structure for AIROA Metadata Library.
"""

import pytest


class TestMainPackageImports:
    """Test imports from the main airoa_metadata package."""

    def test_main_package_imports(self):
        """Test that all expected classes can be imported from main package."""
        from airoa_metadata import (
            Metadata,
            MetadataBase,
            MetadataLatest,
            MetadataLoader,
            MetadataV0_0,
            MetadataV1_0,
            MetadataV1_1,
            MetadataV1_2,
            MetadataV1_3,
            MetadataV2_0,
            __version__,
        )

        # Verify classes are importable
        assert MetadataBase is not None
        assert MetadataLoader is not None
        assert MetadataV0_0 is not None
        assert MetadataV1_0 is not None
        assert MetadataV1_1 is not None
        assert MetadataV1_2 is not None
        assert MetadataV1_3 is not None
        assert MetadataV2_0 is not None
        assert MetadataLatest is not None
        assert Metadata is not None
        assert __version__ is not None

    def test_package_metadata(self):
        """Test package metadata is correctly set."""
        from airoa_metadata import __author__, __version__

        assert __version__ == "2.0.0"
        assert __author__ == "Petr Khrapchenkov"


class TestCoreImports:
    """Test imports from airoa_metadata.core module."""

    def test_core_imports(self):
        """Test that core classes can be imported."""
        from airoa_metadata.core import MetadataBase, MetadataLoader

        assert MetadataBase is not None
        assert MetadataLoader is not None

    def test_core_base_import(self):
        """Test importing base class directly."""
        from airoa_metadata.core.base import MetadataBase

        assert MetadataBase is not None

    def test_core_loader_import(self):
        """Test importing loader class directly."""
        from airoa_metadata.core.loader import MetadataLoader

        assert MetadataLoader is not None


class TestVersionImports:
    """Test imports from airoa_metadata.versions module."""

    def test_version_imports(self):
        """Test that all version classes can be imported."""
        from airoa_metadata.versions import (
            LATEST_VERSION,
            VERSIONS,
            MetadataLatest,
            MetadataV0_0,
            MetadataV1_0,
            MetadataV1_1,
            MetadataV1_2,
            MetadataV1_3,
            MetadataV2_0,
        )

        assert MetadataV0_0 is not None
        assert MetadataV1_0 is not None
        assert MetadataV1_1 is not None
        assert MetadataV1_2 is not None
        assert MetadataV1_3 is not None
        assert MetadataV2_0 is not None
        assert VERSIONS is not None
        assert LATEST_VERSION == "2.0"
        assert MetadataLatest is MetadataV2_0

    def test_versions_registry(self):
        """Test the versions registry contains all expected versions."""
        from airoa_metadata.versions import VERSIONS

        expected_versions = ["0.0", "1.0", "1.1", "1.2", "1.3", "2.0"]
        assert set(VERSIONS.keys()) == set(expected_versions)

        # Verify each version maps to the correct class
        from airoa_metadata.versions import (
            MetadataV0_0,
            MetadataV1_0,
            MetadataV1_1,
            MetadataV1_2,
            MetadataV1_3,
            MetadataV2_0,
        )

        assert VERSIONS["0.0"] is MetadataV0_0
        assert VERSIONS["1.0"] is MetadataV1_0
        assert VERSIONS["1.1"] is MetadataV1_1
        assert VERSIONS["1.2"] is MetadataV1_2
        assert VERSIONS["1.3"] is MetadataV1_3
        assert VERSIONS["2.0"] is MetadataV2_0

    @pytest.mark.parametrize(
        "version,expected_class",
        [
            ("0.0", "MetadataV0_0"),
            ("1.0", "MetadataV1_0"),
            ("1.1", "MetadataV1_1"),
            ("1.2", "MetadataV1_2"),
            ("1.3", "MetadataV1_3"),
            ("2.0", "MetadataV2_0"),
        ],
    )
    def test_individual_version_imports(self, version, expected_class):
        """Test importing individual version classes."""
        from airoa_metadata.versions import VERSIONS

        version_class = VERSIONS[version]
        assert version_class.__name__ == expected_class

    def test_direct_version_imports(self):
        """Test importing version classes directly from their modules."""
        from airoa_metadata.versions.v0_0 import MetadataV0_0
        from airoa_metadata.versions.v1_0 import MetadataV1_0
        from airoa_metadata.versions.v1_1 import MetadataV1_1
        from airoa_metadata.versions.v1_2 import MetadataV1_2
        from airoa_metadata.versions.v1_3 import MetadataV1_3
        from airoa_metadata.versions.v2_0 import MetadataV2_0

        assert MetadataV0_0 is not None
        assert MetadataV1_0 is not None
        assert MetadataV1_1 is not None
        assert MetadataV1_2 is not None
        assert MetadataV1_3 is not None
        assert MetadataV2_0 is not None


class TestSchemaImports:
    """Test imports from airoa_metadata.schemas module."""

    def test_schema_imports(self):
        """Test that schema utilities can be imported."""
        from airoa_metadata.schemas import (
            AVAILABLE_SCHEMAS,
            get_schema_path,
            load_schema,
        )

        assert get_schema_path is not None
        assert load_schema is not None
        assert AVAILABLE_SCHEMAS is not None

    def test_available_schemas(self):
        """Test that all expected schemas are available."""
        from airoa_metadata.schemas import AVAILABLE_SCHEMAS

        expected_schemas = ["0.0", "1.0", "1.1", "1.2", "1.3", "2.0"]
        assert set(AVAILABLE_SCHEMAS) == set(expected_schemas)


class TestConvenienceAliases:
    """Test convenience aliases work correctly."""

    def test_metadata_latest_alias(self):
        """Test MetadataLatest points to the latest version."""
        from airoa_metadata import MetadataLatest
        from airoa_metadata.versions import MetadataV2_0

        assert MetadataLatest is MetadataV2_0

    def test_metadata_alias(self):
        """Test Metadata points to the latest version."""
        from airoa_metadata import Metadata
        from airoa_metadata.versions import MetadataV2_0

        assert Metadata is MetadataV2_0

    def test_aliases_consistency(self):
        """Test that all aliases point to the same class."""
        from airoa_metadata import Metadata, MetadataLatest
        from airoa_metadata.versions import MetadataLatest as VersionsLatest

        assert MetadataLatest is Metadata
        assert MetadataLatest is VersionsLatest


class TestImportErrors:
    """Test that expected import errors occur for invalid imports."""

    def test_nonexistent_version_import_fails(self):
        """Test that importing a non-existent version fails."""
        with pytest.raises(ImportError):
            from airoa_metadata.versions.v9_9 import MetadataV9_9  # noqa: F401

    def test_nonexistent_module_import_fails(self):
        """Test that importing from non-existent module fails."""
        with pytest.raises(ImportError):
            from airoa_metadata.nonexistent import SomeClass  # noqa: F401
