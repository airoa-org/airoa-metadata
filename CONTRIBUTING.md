# Contributing to AIROA Metadata

Thank you for your interest in contributing to AIROA Metadata! This document provides guidelines and instructions for contributing to the project.


## Quick Start for Contributors

### Development Setup

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/your-username/airoa-metadata.git
   cd airoa-metadata
   ```

2. Initialize submodules and install dependencies:
   ```bash
   git submodule update --init --recursive
   GIT_LFS_SKIP_SMUDGE=1 uv sync
   ```

3. Run pre-commit checks to ensure everything works:
   ```bash
   make format && make lint && make test
   ```

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and add tests**
   - Add unit tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**
   ```bash
   make format    # Format code with ruff
   make lint      # Check linting and types with ruff + mypy
   make test      # Run test suite
   ```

4. **Commit your changes:**
   ```bash
   git commit -m "Add your descriptive commit message"
   ```
   - Use clear, descriptive commit messages
   - Reference issue numbers when applicable

5. **Push and create a Pull Request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what changes you made and why
- **Tests**: Include tests for new functionality
- **Quality**: All checks must pass (formatting, linting, tests)
- **Documentation**: Update documentation if needed
- **Reference**: Link any related issues

## Reporting Issues

### Bug Reports
- Use clear, descriptive titles
- Include steps to reproduce
- Provide environment details (OS, Python version, etc.)
- Include relevant error messages and stack traces

### Feature Requests
- Describe the feature and its use case
- Explain how it would benefit the community
- Consider implementation complexity

## Types of Contributions

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Code refactoring

### Metadata Support
- New metadata version support
- Improvements to existing conversions
- Validation enhancements
- Configuration examples

### Documentation
- README improvements
- Code documentation
- Usage examples

## Code Standards

- **Python 3.10+** compatible
- **Type hints** required for new code
- **Tests** required for new functionality
- **Format**: Code must pass `make format`
- **Linting**: Code must pass `make lint`

## Questions & Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion

## License

By contributing to AIROA Metadata, you agree that your contributions will be licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

Thank you for contributing to AIROA Metadata! 🤖