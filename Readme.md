# AIROA Metadata Library

A Python library for handling versioned metadata for robotic data collection. This library provides dataclass-based representations of different metadata schema versions with automatic conversion between versions.

## Features

- **Multiple Schema Versions**: Support for metadata versions 0.0, 1.0, 1.1, 1.2, and 1.3
- **Automatic Conversion**: Convert between different metadata versions seamlessly
- **JSON Schema Validation**: Validate metadata against JSON schemas
- **Type Safety**: Full type hints and dataclass-based implementations
- **Python 3.8+ Compatible**: Works with modern Python versions

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/airoa-org/airoa-metadata.git
cd airoa-metadata

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e .[dev]
```

### Using pip (when published)

```bash
pip install airoa-metadata
```

## Quick Start

### Basic Usage

```python
from airoa_metadata import MetadataV1_3, MetadataLoader

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

# Convert between versions
from airoa_metadata.versions import MetadataV1_2
v1_2_metadata = MetadataV1_2.convert(metadata)
```

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
from airoa_metadata.core import MetadataLoader

# Automatic validation when loading
try:
    metadata = MetadataLoader.load_from_dict(data)
    print(f"Loaded valid {metadata.version} metadata")
except Exception as e:
    print(f"Validation failed: {e}")
```

## Supported Versions

| Version | Features |
|---------|----------|
| 0.0 | Basic metadata structure |
| 1.0 | Enhanced with task templates |
| 1.1 | Improved segment tracking |
| 1.2 | Unified entity structure with task templates |
| 1.3 | Split task entities into task-record and task-template |

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

## Development

### Setting up Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/airoa-org/airoa-metadata.git
cd airoa-metadata
pip install -e .[dev]

# Run tests
pytest

# Run linting
black airoa_metadata/
isort airoa_metadata/
flake8 airoa_metadata/
mypy airoa_metadata/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest airoa_metadata/tests/test_versions.py
```

## License

This software is provided "as-is", without any express or implied warranty.
See the source code for full license terms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/airoa-org/airoa-metadata/issues)
- **Documentation**: [Read the Docs](https://airoa-metadata.readthedocs.io/)
- **Email**: For questions about usage or development
