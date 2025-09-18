# -*- coding: utf-8 -*-
"""
Shared test fixtures and configuration for AIROA Metadata Library tests.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Get the path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def good_fixtures_dir(fixtures_dir: Path) -> Path:
    """Get the path to good test fixtures directory."""
    return fixtures_dir / "good"


@pytest.fixture
def bad_fixtures_dir(fixtures_dir: Path) -> Path:
    """Get the path to bad test fixtures directory."""
    return fixtures_dir / "bad"


@pytest.fixture
def v1_3_test_data(good_fixtures_dir: Path) -> Dict[str, Any]:
    """Load v1.3 test data."""
    test_file = good_fixtures_dir / "v1.3_001.json"
    with open(test_file, "r") as f:
        return json.load(f)


@pytest.fixture
def v1_2_test_data(good_fixtures_dir: Path) -> Dict[str, Any]:
    """Load v1.2 test data."""
    test_file = good_fixtures_dir / "v1.2_001.json"
    with open(test_file, "r") as f:
        return json.load(f)


@pytest.fixture
def v1_1_test_data(good_fixtures_dir: Path) -> Dict[str, Any]:
    """Load v1.1 test data."""
    test_file = good_fixtures_dir / "v1.1_005.json"
    with open(test_file, "r") as f:
        return json.load(f)


@pytest.fixture
def v1_0_test_data(good_fixtures_dir: Path) -> Dict[str, Any]:
    """Load v1.0 test data."""
    test_file = good_fixtures_dir / "v1.0_001.json"
    with open(test_file, "r") as f:
        return json.load(f)


@pytest.fixture
def v0_0_test_data(good_fixtures_dir: Path) -> Dict[str, Any]:
    """Load v0.0 test data."""
    test_file = good_fixtures_dir / "v0.0_001.json"
    with open(test_file, "r") as f:
        return json.load(f)


@pytest.fixture
def sample_v1_3_data() -> Dict[str, Any]:
    """Create minimal valid v1.3 data for testing."""
    return {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "version": "1.3",
        "files": [{"type": "rosbag", "name": "test.bag"}],
        "context": {
            "entities": [
                {"role": "robot", "id": "test-robot"},
                {"role": "operator", "id": "test-operator"},
            ],
            "components": [
                {
                    "role": "interface",
                    "name": "test-interface",
                    "source": {
                        "git": {
                            "uri": "https://github.com/test/repo.git",
                            "hash": "abc123",
                            "branch": "main",
                        }
                    },
                }
            ],
        },
        "run": {
            "total_time_s": 10.0,
            "instructions": [{"idx": 0, "text": ["Test instruction"]}],
            "segments": [
                {
                    "start_time": 1000.0,
                    "end_time": 1010.0,
                    "instruction_idx": 0,
                    "success": True,
                    "controlled_by": "operator",
                }
            ],
        },
    }


@pytest.fixture
def sample_v1_2_data() -> Dict[str, Any]:
    """Create minimal valid v1.2 data for testing."""
    return {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "version": "1.2",
        "files": [{"type": "rosbag", "name": "test.bag"}],
        "context": {
            "entities": [
                {"role": "robot", "id": "test-robot"},
                {"role": "operator", "id": "test-operator"},
                {
                    "role": "task",
                    "id": "test-task",
                    "template": {"name": "Test Task", "description": "A test task"},
                },
            ],
            "components": [
                {
                    "role": "interface",
                    "name": "test-interface",
                    "source": {
                        "git": {
                            "uri": "https://github.com/test/repo.git",
                            "hash": "abc123",
                            "branch": "main",
                        }
                    },
                }
            ],
        },
        "run": {
            "total_time_s": 10.0,
            "instructions": [{"idx": 0, "text": ["Test instruction"]}],
            "segments": [
                {
                    "start_time": 1000.0,
                    "end_time": 1010.0,
                    "instruction_idx": 0,
                    "success": True,
                    "controlled_by": "operator",
                }
            ],
        },
    }


@pytest.fixture(params=["0.0", "1.0", "1.1", "1.2", "1.3"])
def version_string(request) -> str:
    """Parametrized fixture for all supported version strings."""
    return request.param


@pytest.fixture
def all_test_data_files(good_fixtures_dir: Path) -> Dict[str, Path]:
    """Get all test data files by version."""
    files = {}
    for json_file in good_fixtures_dir.glob("*.json"):
        # Extract version from filename like "v1.3_001.json"
        version = json_file.stem.split("_")[0].replace("v", "").replace("_", ".")
        if version not in files:
            files[version] = []
        if not isinstance(files[version], list):
            files[version] = [files[version]]
        files[version].append(json_file)

    # Return first file for each version
    return {
        v: files_list[0] if isinstance(files_list, list) else files_list
        for v, files_list in files.items()
    }
