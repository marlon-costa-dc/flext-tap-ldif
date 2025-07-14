# FLEXT Tap LDIF

A Singer tap for extracting data from LDIF (LDAP Data Interchange Format) files, built using the Singer SDK and integrated with the FLEXT framework.

## Features

- **LDIF File Processing**: Extract data from single or multiple LDIF files
- **Flexible Input**: Support for file paths, directory scanning, and file patterns
- **Advanced Filtering**: Filter by base DN, object class, and attributes
- **Batch Processing**: Configurable batch sizes for memory efficiency
- **Error Handling**: Strict or lenient parsing modes
- **Singer Protocol**: Full compliance with Singer specification
- **FLEXT Integration**: Leverages FLEXT core libraries for enterprise features

## Installation

```bash
# Install from source
pip install flext-tap-ldif

# Install in development mode
poetry install
```

## Configuration

### Required Settings

- `file_path` OR `directory_path` OR `file_pattern`: Specify input source

### Optional Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `file_path` | string | - | Path to single LDIF file |
| `directory_path` | string | - | Directory containing LDIF files |
| `file_pattern` | string | `*.ldif` | File pattern for multiple files |
| `base_dn_filter` | string | - | Filter entries by base DN |
| `object_class_filter` | array | - | Filter by object classes |
| `attribute_filter` | array | - | Include only specified attributes |
| `exclude_attributes` | array | - | Exclude specified attributes |
| `encoding` | string | `utf-8` | File encoding |
| `batch_size` | integer | 1000 | Batch size for processing |
| `include_operational_attributes` | boolean | false | Include operational attributes |
| `strict_parsing` | boolean | true | Enable strict parsing |
| `max_file_size_mb` | integer | 100 | Maximum file size limit (MB) |

## Usage

### Basic Usage

```bash
# Discover available streams
tap-ldif --discover

# Extract data from a single file
tap-ldif --config config.json --discover > catalog.json
tap-ldif --config config.json --catalog catalog.json
```

### Configuration Examples

#### Single File
```json
{
  "file_path": "/path/to/directory.ldif"
}
```

#### Directory Processing
```json
{
  "directory_path": "/path/to/ldif/files",
  "file_pattern": "*.ldif",
  "batch_size": 500
}
```

#### Filtered Extraction
```json
{
  "file_path": "/path/to/directory.ldif",
  "base_dn_filter": "dc=example,dc=com",
  "object_class_filter": ["person", "organizationalPerson"],
  "exclude_attributes": ["userPassword", "authPassword"]
}
```

## Output Schema

The tap produces records with the following schema:

```json
{
  "dn": "cn=John Doe,ou=people,dc=example,dc=com",
  "object_class": ["person", "organizationalPerson"],
  "attributes": {
    "cn": "John Doe",
    "sn": "Doe",
    "mail": "john.doe@example.com"
  },
  "change_type": null,
  "source_file": "/path/to/file.ldif",
  "line_number": 42,
  "entry_size": 256
}
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/marlon-costa-dc/flext-tap-ldif.git
cd flext-tap-ldif

# Install dependencies
make dev-install

# Run tests
make test

# Run quality checks
make check
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test types
make test-unit
make test-integration
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Type checking
make type-check

# Security checks
make security

# All quality checks
make check
```

## LDIF Format Support

This tap supports standard LDIF format as defined in RFC 2849:

- **Entry Records**: Standard LDAP entries
- **Change Records**: Add, delete, modify, and moddn operations
- **Base64 Encoding**: Automatic detection and decoding
- **Line Continuation**: Multi-line attribute values
- **Comments**: Lines starting with `#`

### Supported LDIF Features

- ✅ Entry records with DN and attributes
- ✅ Base64 encoded values (using `::` syntax)
- ✅ Multi-line attribute values
- ✅ Comments and empty lines
- ✅ Change records (changetype attribute)
- ✅ UTF-8 and other encodings
- ✅ Large file processing with batching

## Integration with FLEXT

This tap integrates with the FLEXT framework:

- **Observability**: Automatic metrics and logging
- **Configuration**: Pydantic-based configuration management
- **Error Handling**: Consistent error patterns
- **Type Safety**: Full type hints and validation

## Singer Specification Compliance

This tap fully complies with the Singer specification:

- **Discovery**: Automatic schema discovery
- **Catalog**: Stream and field selection
- **State**: Incremental extraction support
- **Messages**: RECORD, SCHEMA, and STATE messages
- **Types**: JSON Schema type definitions

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

For issues and questions:
- GitHub Issues: [flext-tap-ldif/issues](https://github.com/marlon-costa-dc/flext-tap-ldif/issues)
- FLEXT Documentation: [FLEXT Framework](https://github.com/flext-sh/flext)