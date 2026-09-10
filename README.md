# AIROA Metadata

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/airoa-metadata.svg)](https://badge.fury.io/py/airoa-metadata)

> A Python library for handling versioned metadata schemas for robotic data collection, providing seamless conversion between versions and robust validation.

## Overview

**Currently under active development. Expect changes in API and command line arguments.**  
AIROA Metadata provides a **unified and versioned metadata schema system** for robotic data collection. It enables researchers and developers to manage metadata across different versions with automatic conversion capabilities, ensuring backward compatibility and data consistency throughout the robot learning pipeline.

## Key Features

- 🔄 **Version Management** - Support for multiple schema versions (0.0, 1.0, 1.1, 1.2, 1.3, 2.0)
- 🔀 **Automatic Conversion** - Seamless conversion between different metadata versions
- ✅ **JSON Schema Validation** - Robust validation against defined JSON schemas
- 🔒 **Type Safety** - Full type hints and dataclass-based implementations
- 🐍 **Python 3.8+ Compatible** - Works with modern Python versions
- 📦 **Extensible Architecture** - Easy to add new versions and features

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Installation

#### Using pip

```bash
pip install airoa-metadata
```

#### From Source

```bash
# Clone the repository
git clone https://github.com/airoa-org/airoa-metadata.git
cd airoa-metadata

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Basic Usage

```python
from airoa_metadata import MetadataV1_2, MetadataV1_3, MetadataLoader

# Load metadata from a JSON file
metadata = MetadataLoader.load_from_file("metadata.json")

# Or create from a dictionary
data = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "version": "1.3",
    "files": [{"type": "rosbag", "name": "data.bag"}],
    "context": {"entities": [], "components": []},
    "run": {"total_time_s": 10.0, "instructions": [], "segments": []}
}
metadata = MetadataV1_3.from_dict(data)

# Convert from older to newer version
v1_2_data = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "version": "1.2",
    "files": [{"type": "rosbag", "name": "data.bag"}],
    "context": {"entities": [], "components": []},
    "run": {"total_time_s": 10.0, "instructions": [], "segments": []}
}
v1_2_metadata = MetadataV1_2.from_dict(v1_2_data)
v1_3_metadata = MetadataV1_3.convert(v1_2_metadata)  # Convert to v1.3
```

## Supported Versions

| Version | Features | Status |
|---------|----------|---------|
| 0.0 | Basic metadata structure | ✅ Stable |
| 1.0 | Enhanced with task templates | ✅ Stable |
| 1.1 | Improved segment tracking | ✅ Stable |
| 1.2 | Unified entity structure with task templates | ✅ Stable |
| 1.3 | Split task entities into task-record and task-template | ✅ Stable |
| 2.0 | Restructured schema: promotes `robot`, `environment`, `runner`, `devices`, `programs`, `episode`, `labels` and `segments` to top-level fields (replacing v1.x `context`/`run`); renames `version` to `schema_version` | ✅ Stable (latest) |

> **What's new in v2.0 (latest):** Version 2.0 restructures the metadata layout to describe a run more directly. The nested `context`/`run` objects of v1.x are replaced by first-class top-level fields — `robot` (identity: URI, type, id), `environment` (site/location and a type such as `real_world` or `simulation`), `runner` (operator or model), `devices` (teleoperation devices), `programs` (teleoperation / data-logging services), `episode` (start/end timestamps, success flag, label), `labels` (high-level instructions) and `segments` (execution segments aligned with `labels`). The `version` field is renamed to `schema_version`, and `MetadataV2_0` becomes the new `MetadataLatest`.

## Usage Examples

### Working with Specific Versions

```python
# Import specific versions
from airoa_metadata.versions import (
    MetadataV0_0, MetadataV1_0, MetadataV1_1, 
    MetadataV1_2, MetadataV1_3
)

# Use the latest version
from airoa_metadata import MetadataLatest, Metadata

# Create metadata with specific version
metadata = MetadataV1_3.from_dict(data)
```

### Schema Validation

```python
from airoa_metadata import MetadataLoader

# Automatic validation when loading
data = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "version": "1.3",
    "files": [{"type": "rosbag", "name": "data.bag"}],
    "context": {"entities": [], "components": []},
    "run": {"total_time_s": 10.0, "instructions": [], "segments": []}
}
try:
    metadata = MetadataLoader.load_from_dict(data)
    print(f"Loaded valid {metadata.version} metadata")
except Exception as e:
    print(f"Validation failed: {e}")
```

## Development

### Development Setup

```bash
# Clone the repository
git clone https://github.com/airoa-org/airoa-metadata.git
cd airoa-metadata

# Initialize submodules and install dependencies
git submodule update --init --recursive
GIT_LFS_SKIP_SMUDGE=1 uv sync
```

### Code Quality

```bash
# Format code
make format

# Run linting (ruff + mypy)
make lint

# Run tests
make test

# Run tests with coverage
make test-coverage
```

### Available Make Commands

- `make format` - Format code with ruff
- `make lint` - Run linting checks (ruff + mypy)
- `make test` - Run all unit tests
- `make test-coverage` - Run tests with coverage report

### Testing

```bash
# Run specific test
uv run pytest airoa_metadata/tests/test_versions.py -v

# Run with coverage
make test-coverage
```

## Library Structure

```
airoa_metadata/
├── __init__.py              # Main package exports
├── core/                    # Core functionality
│   ├── base.py             # MetadataBase class
│   └── loader.py           # MetadataLoader class
├── versions/               # Version-specific implementations
│   ├── v0_0.py            # MetadataV0_0
│   ├── v1_0.py            # MetadataV1_0
│   ├── v1_1.py            # MetadataV1_1
│   ├── v1_2.py            # MetadataV1_2
│   └── v1_3.py            # MetadataV1_3
├── schemas/               # JSON schema files
└── tests/                 # Test suite
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you've installed the package correctly with `uv sync` or `pip install -e .`
2. **Validation errors**: Check that your metadata follows the correct schema for the version
3. **Version conversion errors**: Some conversions may lose data when going to older versions

### Getting Help

- 🐛 Report issues on [GitHub Issues](https://github.com/airoa-org/airoa-metadata/issues)

## Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

**Quick start:**

1. Fork the repository
2. Create a feature branch
3. Make your changes and add tests
4. Run quality checks: `make format && make lint && make test`
5. Open a Pull Request

📋 **For detailed instructions, development setup, and guidelines, please see our [Contributing Guide](CONTRIBUTING.md).**

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by the [AIRoA Team](https://github.com/airoa-org)
