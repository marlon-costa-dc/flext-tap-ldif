# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **flext-tap-ldif**, a Singer SDK tap for extracting data from LDIF (LDAP Data Interchange Format) files. It's part of the larger FLEXT ecosystem of enterprise data integration tools. The tap implements Clean Architecture and Domain-Driven Design patterns with strict type safety and 90% test coverage requirements.

## Architecture

### Core Components

- **TapLDIF** (`src/flext_tap_ldif/tap.py`): Main tap class implementing Singer SDK patterns
- **LDIFEntriesStream** (`src/flext_tap_ldif/streams.py`): Stream implementation for LDIF entry processing
- **TapLDIFConfig** (`src/flext_tap_ldif/config.py`): Pydantic-based configuration with validation
- **FlextLDIFProcessorWrapper** (`src/flext_tap_ldif/ldif_processor.py`): Wrapper around flext-ldif infrastructure
- **Exception Hierarchy** (`src/flext_tap_ldif/exceptions.py`): Domain-specific exceptions inheriting from flext-core

### Dependencies

The project follows FLEXT ecosystem patterns and depends on:

- **flext-core**: Base patterns, logging, result handling, dependency injection
- **flext-meltano**: Singer SDK integration and Meltano orchestration
- **flext-ldif**: LDIF parsing and processing infrastructure
- **flext-observability**: Monitoring and metrics

### Key Patterns

- **Singer SDK Integration**: Uses flext-meltano for centralized Singer SDK imports and patterns
- **Infrastructure Reuse**: Leverages flext-ldif for LDIF processing instead of reimplementing
- **Result Pattern**: Uses flext-core ServiceResult for error handling
- **Pydantic Configuration**: Type-safe configuration with field validation
- **Stream-based Processing**: Implements Singer stream interface for data extraction

## Development Commands

### Quality Gates (Always run before committing)

```bash
make validate          # Complete validation (lint + type + security + test)
make check            # Quick health check (lint + type-check)
```

### Individual Quality Checks

```bash
make lint             # Ruff linting with ALL rules enabled
make type-check       # MyPy strict type checking
make security         # Bandit security scan + pip-audit
make format           # Auto-format code with ruff
make test             # Run tests with 90% coverage requirement
```

### Testing

```bash
make test             # All tests with coverage
make test-unit        # Unit tests only (-m "not integration")
make test-integration # Integration tests only (-m integration)
make test-singer      # Singer protocol tests (-m singer)
make test-fast        # Tests without coverage report
make coverage-html    # Generate HTML coverage report
```

### Singer Tap Operations

```bash
make discover         # Run tap discovery mode (--discover)
make run              # Run tap extraction (--config --catalog --state)
make validate-config  # Validate tap configuration JSON
make catalog          # Alias for discover
make sync             # Alias for run
```

### LDIF-Specific Operations

```bash
make ldif-validate    # Validate LDIF file format
make ldif-parse       # Test LDIF parsing functionality
make ldif-test        # Run comprehensive LDIF tests
```

### Build & Distribution

```bash
make build            # Build distribution packages with Poetry
make build-clean      # Clean and build
make install          # Install dependencies
make setup            # Complete project setup (install-dev + pre-commit)
```

### Development Tools

```bash
make shell            # Python shell with project loaded
make pre-commit       # Run pre-commit hooks manually
make diagnose         # Project diagnostics and health info
make doctor           # Health check + diagnostics
make clean            # Clean build artifacts and cache
make clean-all        # Deep clean including venv
make reset            # Reset project (clean-all + setup)
```

### Dependencies

```bash
make deps-update      # Update dependencies
make deps-show        # Show dependency tree
make deps-audit       # Audit dependencies for vulnerabilities
```

## Configuration

The tap accepts configuration through JSON files or environment variables:

### Required Configuration

- **file_path**: Path to single LDIF file, OR
- **directory_path** + **file_pattern**: Directory with LDIF file pattern, OR
- **file_pattern**: Pattern in current directory

### Optional Configuration

- **base_dn_filter**: Filter entries by base DN pattern
- **object_class_filter**: Array of object classes to include
- **attribute_filter**: Array of attributes to include
- **exclude_attributes**: Array of attributes to exclude
- **encoding**: File encoding (default: utf-8)
- **batch_size**: Entries per batch (1-10000, default: 1000)
- **include_operational_attributes**: Include operational attributes (default: false)
- **strict_parsing**: Fail on parsing errors (default: true)
- **max_file_size_mb**: Maximum file size in MB (1-1000, default: 100)

## Testing Strategy

### Test Organization

- **Unit Tests**: Core functionality without external dependencies
- **Integration Tests**: File processing and Singer protocol integration
- **Singer Tests**: Singer SDK compliance and protocol validation

### Coverage Requirements

- Minimum 90% test coverage enforced
- pytest with comprehensive test configuration
- HTML and XML coverage reports generated

### Test Execution

```bash
# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m singer           # Singer protocol tests
pytest -m slow             # Slow tests only
pytest -m smoke            # Smoke tests only
pytest -m e2e              # End-to-end tests only
pytest -m "not slow"       # Fast tests only

# Run single test with verbose output
pytest tests/test_tap.py::test_discover_streams -v

# Debug failing tests
pytest tests/test_tap.py -vvs --pdb
```

## Code Quality Standards

### Linting & Formatting

- **Ruff**: ALL rules enabled with specific ignores in pyproject.toml
- **Black**: Code formatting (delegated to ruff format)
- **MyPy**: Strict type checking with no untyped code allowed
- **Bandit**: Security scanning with exclusions for test files

### Type Safety

- Python 3.13+ with strict type hints required
- Pydantic models for configuration validation
- TYPE_CHECKING imports for runtime optimization
- No `Any` types without justification

### Security

- pip-audit for dependency vulnerability scanning
- Bandit security linting with medium severity threshold
- detect-secrets for secret scanning (with baseline)
- No secrets or sensitive data in code
- Input validation on all configuration fields

### Pre-commit Hooks

The project uses comprehensive pre-commit hooks for quality enforcement:

```bash
make pre-commit       # Run all pre-commit hooks manually
pre-commit run --all-files  # Run specific hooks
```

**Enabled hooks**: Black formatting, Ruff linting/formatting, isort imports, MyPy type checking, Bandit security, Vulture dead code detection, Radon complexity analysis, YAML/TOML/JSON validation, and commit message validation.

## File Structure

```
src/flext_tap_ldif/
├── __init__.py           # Package initialization and exports
├── __version__.py        # Version information
├── tap.py               # Main TapLDIF class
├── streams.py           # LDIFEntriesStream implementation
├── config.py            # TapLDIFConfig with validation
├── ldif_processor.py    # Wrapper for flext-ldif integration
├── exceptions.py        # Domain-specific exception hierarchy
├── typings.py           # Type definitions
└── py.typed             # PEP 561 type information marker

tests/
├── test_tap.py         # Core tap functionality tests
└── conftest.py         # Pytest configuration and fixtures
```

## Common Issues & Solutions

### LDIF Processing Errors

- Check file encoding (default: utf-8)
- Verify LDIF file format compliance
- Use `strict_parsing=false` for lenient parsing
- Check file size limits (max_file_size_mb)

### Singer Protocol Issues

- Ensure configuration validation passes
- Run discovery mode before extraction
- Verify catalog and state file formats
- Check schema compatibility

### Type Check Failures

- All functions must have type hints
- Use `from __future__ import annotations` for forward references
- Import types under `TYPE_CHECKING` for runtime optimization
- No untyped function definitions allowed

### Dependency Issues

- Use Poetry for dependency management
- Dependencies are path-based within FLEXT ecosystem
- Run `poetry install --with dev,test,typings,security` for full development setup
- Check compatibility with flext-core patterns
- Use `make deps-audit` to check for vulnerabilities

### Environment Issues

- Requires Python 3.13+ (exactly, not 3.14+)
- Uses path-based dependencies to other FLEXT ecosystem projects
- Test environment is automatically configured via conftest.py
- All environment variables are prefixed with `FLEXT_` or `SINGER_SDK_`

## Integration Points

### FLEXT Ecosystem Integration

- Uses flext-core for logging, exceptions, and base patterns
- Integrates with flext-ldif for LDIF processing functionality
- Compatible with flext-meltano for Singer orchestration
- Follows flext-observability patterns for monitoring

### Singer Ecosystem

- Implements Singer SDK tap interface via flext-meltano
- Supports standard Singer discovery and extraction modes
- Compatible with Meltano orchestration platform
- Follows Singer JSON schema specifications
