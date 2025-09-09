# CLAUDE.md - FLEXT Tap LDIF Quality Refactoring Guide

**Project**: FLEXT Tap LDIF - Enterprise LDIF Data Extraction  
**Status**: Quality Refactoring Required | **Architecture**: Clean Architecture + DDD  
**Dependencies**: Python 3.13+, flext-core, flext-ldif, flext-meltano, singer-sdk  
**Coverage Target**: 90% | **Current Type Status**: Requires Assessment  
**Authority**: FLEXT-TAP-LDIF | **Last Updated**: 2025-01-08

---

## 🎯 PROJECT MISSION STATEMENT

Transform FLEXT Tap LDIF into a **production-ready, enterprise-grade LDIF file processing tap** implementing Singer protocol with zero tolerance quality standards. This tap provides specialized LDIF (LDAP Data Interchange Format) file extraction capabilities leveraging the proven flext-ldif infrastructure while maintaining Clean Architecture and Domain-Driven Design principles.

### 🏆 SUCCESS CRITERIA (EVIDENCE-BASED VALIDATION)

- **✅ 90% Test Coverage**: Real functional tests with comprehensive LDIF processing scenarios (measured via `pytest --cov=src --cov-report=term`)
- **✅ Zero Tolerance Quality**: MyPy strict + Ruff ALL rules + Bandit security (measured via `make validate`)
- **✅ Singer Protocol Compliance**: Full catalog discovery + data extraction working (verified via `make discover && make run`)
- **✅ LDIF Processing Excellence**: Robust LDIF parsing with error handling (verified via `make ldif-test`)
- **✅ Infrastructure Integration**: Seamless flext-ldif infrastructure reuse (verified via integration tests)

---

## 🚫 PROJECT PROHIBITIONS (ZERO TOLERANCE ENFORCEMENT)

### ⛔ ABSOLUTELY FORBIDDEN ACTIONS:

1. **Quality Degradation**:
   - NEVER reduce test coverage below 90%
   - NEVER suppress MyPy/Ruff errors without proper resolution
   - NEVER disable security scanning (Bandit/pip-audit)
   - NEVER compromise Singer protocol compliance

2. **Architectural Violations**:
   - NEVER bypass Clean Architecture layer boundaries
   - NEVER duplicate functionality available in flext-ldif
   - NEVER create circular dependencies between layers
   - NEVER ignore FlextResult pattern for error handling

3. **LDIF Processing Violations**:
   - NEVER implement LDIF parsing from scratch (use flext-ldif)
   - NEVER ignore LDIF format validation
   - NEVER process files without proper encoding detection
   - NEVER skip error recovery mechanisms

4. **Singer Protocol Violations**:
   - NEVER return data without proper Singer RECORD messages
   - NEVER skip catalog discovery implementation
   - NEVER ignore file-based replication patterns
   - NEVER create non-compliant stream schemas

---

## 🏗️ PROJECT ARCHITECTURE (CURRENT STATE ANALYSIS REQUIRED)

### Core Architecture Layers

```python
# FLEXT Tap LDIF follows Clean Architecture with infrastructure reuse
src/flext_tap_ldif/
   domain/                    # Core business logic (minimal - leverage flext-ldif)
      entities.py             # Domain entities: LDIFFile, ProcessingBatch, ExtractedEntry
   application/               # Application services (orchestration layer)
      services.py             # Business logic with FlextResult pattern
   infrastructure/            # External integrations (file system, flext-ldif)
   tap.py                     # Main TapLDIF class (Singer SDK implementation)
   streams.py                 # LDIFEntriesStream implementation
   config.py                  # Pydantic configuration models
   ldif_processor.py          # FlextLDIFProcessorWrapper (infrastructure integration)
   exceptions.py              # Domain-specific exception hierarchy
```

### Service Architecture Pattern (MANDATORY)

```python
class FlextTapLdifService(FlextDomainService):
    """Single unified service class following flext-core patterns.
    
    This class consolidates all LDIF tap-related operations,
    leveraging flext-ldif infrastructure while maintaining
    a unified interface for file processing and data extraction.
    """
    
    def __init__(self, **data) -> None:
        """Initialize service with proper dependency injection."""
        super().__init__(**data)
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        self._ldif_processor = self._container.get(LdifProcessor)
    
    def process_ldif_file(self, file_path: str, config: dict) -> FlextResult[list[dict]]:
        """Process LDIF file with comprehensive error handling."""
        if not file_path or not config:
            return FlextResult[list[dict]].fail("File path and config are required")
        
        try:
            # Validate file accessibility and size
            if not Path(file_path).exists():
                return FlextResult[list[dict]].fail(f"LDIF file not found: {file_path}")
            
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            max_size = config.get("max_file_size_mb", 100)
            if file_size_mb > max_size:
                return FlextResult[list[dict]].fail(f"File size {file_size_mb:.1f}MB exceeds limit {max_size}MB")
            
            # Use flext-ldif for processing
            processing_result = self._ldif_processor.process_file(
                file_path=file_path,
                batch_size=config.get("batch_size", 1000),
                encoding=config.get("encoding", "utf-8"),
                strict_parsing=config.get("strict_parsing", True),
                include_operational_attributes=config.get("include_operational_attributes", False)
            )
            
            if processing_result.is_success:
                # Apply configuration-based filtering
                filtered_entries = self._apply_filters(processing_result.value, config)
                return FlextResult[list[dict]].ok(filtered_entries)
            else:
                return FlextResult[list[dict]].fail(f"LDIF processing failed: {processing_result.error}")
                
        except Exception as e:
            self._logger.error(f"LDIF processing error: {e}")
            return FlextResult[list[dict]].fail(f"LDIF processing error: {str(e)}")
    
    def _apply_filters(self, entries: list[dict], config: dict) -> list[dict]:
        """Apply configuration-based filtering to LDIF entries."""
        filtered_entries = entries
        
        # Base DN filtering
        if base_dn_filter := config.get("base_dn_filter"):
            filtered_entries = [
                entry for entry in filtered_entries
                if entry.get("dn", "").lower().endswith(base_dn_filter.lower())
            ]
        
        # Object class filtering
        if object_class_filter := config.get("object_class_filter"):
            filtered_entries = [
                entry for entry in filtered_entries
                if any(oc in entry.get("objectClass", []) for oc in object_class_filter)
            ]
        
        # Attribute filtering
        if attribute_filter := config.get("attribute_filter"):
            for entry in filtered_entries:
                filtered_attrs = {k: v for k, v in entry.items() 
                                if k in attribute_filter or k in ["dn", "objectClass"]}
                entry.clear()
                entry.update(filtered_attrs)
        
        # Attribute exclusion
        if exclude_attributes := config.get("exclude_attributes"):
            for entry in filtered_entries:
                for attr in exclude_attributes:
                    entry.pop(attr, None)
        
        return filtered_entries
    
    def validate_configuration(self, config: dict) -> FlextResult[bool]:
        """Validate tap configuration with business rules."""
        # Implementation with comprehensive validation
        return FlextResult[bool].ok(True)
    
    def discover_schema(self, file_paths: list[str]) -> FlextResult[dict]:
        """Discover schema from LDIF files for Singer catalog generation."""
        try:
            schema_result = self._ldif_processor.analyze_schema(file_paths)
            if schema_result.is_success:
                return FlextResult[dict].ok(schema_result.value)
            else:
                return FlextResult[dict].fail(f"Schema discovery failed: {schema_result.error}")
        except Exception as e:
            return FlextResult[dict].fail(f"Schema discovery error: {str(e)}")
```

---

## ⚡ IMPLEMENTATION STRATEGY (PRIORITY-BASED EXECUTION)

### Phase 1: Foundation Assessment & Repair (MANDATORY FIRST)

#### 1.1 Current State Discovery (INVESTIGATE FIRST)
```bash
# MANDATORY: Complete ecosystem understanding
find flext-core/src -name "*.py" -exec grep -l "FlextDomainService\|FlextResult\|FlextContainer" {} \;
# Read EVERY file that shows up - understand what's available

# Map flext-ldif integration capabilities
grep -r "from flext_ldif" src/ --include="*.py" | cut -d: -f2 | sort | uniq
# Understand current flext-ldif usage patterns

# Check current Singer SDK integration
python -c "from flext_tap_ldif import TapLDIF; help(TapLDIF.discover_streams)"
# Verify current API compatibility

# Count current test coverage
pytest --cov=src --cov-report=term | grep "TOTAL"
# Get baseline coverage before improvements

# Map current failure patterns
pytest --tb=no -q | tail -1 | grep -oE "[0-9]+ failed"
# Understand current test landscape
```

#### 1.2 Quality Gate Assessment
```bash
# Type checking status
mypy src/ --strict --show-error-codes 2>&1 | wc -l
# Count current type errors (target: 0)

# Linting status
ruff check src/ --statistics | grep "errors"
# Count current linting errors (target: 0)

# Security scan
bandit -r src/ -f json 2>/dev/null | jq '.metrics._totals' || echo "Security scan needed"
# Assess security status

# Singer protocol compliance
make discover 2>&1 | grep -E "ERROR|FAILED" | wc -l
# Test current Singer compliance
```

### Phase 2: Service Architecture Optimization (LEVERAGE INFRASTRUCTURE)

#### 2.1 FlextLDIFProcessorWrapper Enhancement
```python
# Enhanced wrapper for flext-ldif integration
class FlextLDIFProcessorWrapper:
    """Enhanced wrapper for flext-ldif infrastructure integration."""
    
    def __init__(self, container: FlextContainer):
        self._container = container
        self._ldif_processor = container.get(LdifProcessor)
        self._logger = FlextLogger(__name__)
    
    def process_file_streamed(self, file_path: str, config: TapLDIFConfig) -> Iterator[dict]:
        """Stream LDIF entries with configuration-based filtering."""
        # Implementation leveraging flext-ldif streaming capabilities
        pass
    
    def validate_ldif_format(self, file_path: str) -> FlextResult[bool]:
        """Validate LDIF file format using flext-ldif validation."""
        # Implementation using flext-ldif validation
        pass
    
    def discover_schema_from_file(self, file_path: str) -> FlextResult[dict]:
        """Discover schema from LDIF file for Singer catalog."""
        # Implementation using flext-ldif schema analysis
        pass
```

#### 2.2 Configuration Enhancement
```python
class TapLDIFConfig(FlextModel):
    """Enhanced LDIF tap configuration with comprehensive validation."""
    
    # File location (choose one approach)
    file_path: Optional[str] = Field(None, description="Path to single LDIF file")
    directory_path: Optional[str] = Field(None, description="Directory containing LDIF files")
    file_pattern: Optional[str] = Field(None, description="File pattern for LDIF files")
    
    # Processing configuration
    encoding: str = Field(default="utf-8", description="File encoding")
    batch_size: int = Field(default=1000, ge=1, le=10000, description="Processing batch size")
    max_file_size_mb: int = Field(default=100, ge=1, le=1000, description="Maximum file size in MB")
    strict_parsing: bool = Field(default=True, description="Fail on parsing errors")
    include_operational_attributes: bool = Field(default=False, description="Include operational attributes")
    
    # Filtering configuration
    base_dn_filter: Optional[str] = Field(None, description="Filter entries by base DN pattern")
    object_class_filter: list[str] = Field(default_factory=list, description="Object classes to include")
    attribute_filter: list[str] = Field(default_factory=list, description="Attributes to include")
    exclude_attributes: list[str] = Field(default_factory=list, description="Attributes to exclude")
    
    @model_validator(mode='after')
    def validate_file_configuration(self) -> 'TapLDIFConfig':
        """Validate that exactly one file location method is specified."""
        file_configs = [self.file_path, self.directory_path, self.file_pattern]
        specified_configs = sum(1 for config in file_configs if config is not None)
        
        if specified_configs != 1:
            raise ValueError("Exactly one of file_path, directory_path+file_pattern, or file_pattern must be specified")
        
        return self
```

### Phase 3: Singer Protocol Excellence (PROTOCOL COMPLIANCE)

#### 3.1 Stream Implementation Enhancement
```python
class LDIFEntriesStream(Stream):
    """Enhanced LDIF entries stream with flext-ldif integration."""
    
    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Extract LDIF records with comprehensive error handling."""
        service = self._container.get(FlextTapLdifService)
        config = self.config.model_dump()
        
        # Determine file paths to process
        file_paths = self._resolve_file_paths(config)
        
        for file_path in file_paths:
            self.logger.info(f"Processing LDIF file: {file_path}")
            result = service.process_ldif_file(file_path, config)
            
            if result.is_success:
                for entry in result.value:
                    # Add metadata
                    entry["_ldif_file_path"] = file_path
                    entry["_ldif_processing_timestamp"] = datetime.utcnow().isoformat()
                    yield entry
            else:
                if config.get("strict_parsing", True):
                    raise RuntimeError(f"LDIF processing error: {result.error}")
                else:
                    self.logger.warning(f"Skipping file {file_path}: {result.error}")
    
    def _resolve_file_paths(self, config: dict) -> list[str]:
        """Resolve file paths based on configuration."""
        if config.get("file_path"):
            return [config["file_path"]]
        elif config.get("directory_path") and config.get("file_pattern"):
            directory = Path(config["directory_path"])
            pattern = config["file_pattern"]
            return [str(f) for f in directory.glob(pattern) if f.is_file()]
        elif config.get("file_pattern"):
            return [str(f) for f in Path.cwd().glob(config["file_pattern"]) if f.is_file()]
        else:
            raise ValueError("No valid file configuration found")
```

#### 3.2 Schema Discovery Implementation
```python
def discover_schema(self) -> dict:
    """Discover schema from LDIF files for catalog generation."""
    service = self._container.get(FlextTapLdifService)
    config = self.config.model_dump()
    
    # Get file paths for schema discovery
    file_paths = self._resolve_file_paths(config)
    
    # Use service for schema discovery
    schema_result = service.discover_schema(file_paths[:5])  # Sample first 5 files
    
    if schema_result.is_success:
        return schema_result.value
    else:
        # Fallback to basic schema
        return self._get_default_schema()

def _get_default_schema(self) -> dict:
    """Get default LDIF entry schema."""
    return {
        "type": "object",
        "properties": {
            "dn": {"type": "string", "description": "Distinguished Name"},
            "objectClass": {
                "type": "array",
                "items": {"type": "string"},
                "description": "LDAP object classes"
            },
            "_ldif_file_path": {"type": "string", "description": "Source LDIF file path"},
            "_ldif_processing_timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["dn"],
        "additionalProperties": True
    }
```

### Phase 4: Integration Testing Excellence (REAL TESTING)

#### 4.1 Comprehensive Test Suite
```python
@pytest.mark.integration
def test_ldif_file_processing_comprehensive():
    """Test comprehensive LDIF file processing scenarios."""
    # Test various LDIF formats
    # Test large files (within limits)
    # Test encoding variations
    # Test malformed entries
    # Test filtering capabilities
    
@pytest.mark.performance
def test_large_ldif_file_performance():
    """Test performance with large LDIF files."""
    # Generate large test LDIF file
    # Measure processing time and memory usage
    # Verify streaming behavior
    # Validate memory efficiency

@pytest.mark.error_handling
def test_error_recovery_scenarios():
    """Test error handling and recovery."""
    # Test file not found scenarios
    # Test permission denied scenarios  
    # Test malformed LDIF content
    # Test encoding errors
    # Test size limit violations
```

#### 4.2 Sample Test Data Organization
```
tests/
   test_data/
      ldif_samples/
         ├── valid_small.ldif           # Small valid LDIF for unit tests
         ├── valid_large.ldif           # Large valid LDIF for performance tests
         ├── malformed_entries.ldif     # LDIF with malformed entries
         ├── encoding_utf16.ldif        # Different encoding test
         ├── operational_attrs.ldif     # LDIF with operational attributes
         └── complex_schema.ldif        # Complex schema for discovery tests
```

---

## 🔧 ESSENTIAL COMMANDS (DAILY DEVELOPMENT)

### Quality Gates (MANDATORY BEFORE ANY COMMIT)
```bash
# NEVER SKIP: Complete validation pipeline
make validate                # lint + type + security + test (90% coverage)

# Quick validation during development
make check                   # lint + type-check + test

# Individual quality components
make lint                    # Ruff linting (ALL rules enabled)
make type-check              # MyPy strict mode validation
make security                # Bandit + pip-audit security scanning
make format                  # Auto-format code with Ruff
```

### Singer Tap Operations
```bash
# Essential Singer protocol operations
make discover                # Generate catalog.json schema (test Singer compliance)
make run                     # Run data extraction (validate full pipeline)  
make validate-config         # Validate tap configuration JSON

# LDIF-specific testing
make ldif-validate           # Validate LDIF file format using flext-ldif
make ldif-parse              # Test LDIF parsing functionality
make ldif-test               # Comprehensive LDIF processing tests
```

### Testing Strategy (90% COVERAGE TARGET)
```bash
# Comprehensive testing approach
make test                    # All tests with 90% coverage requirement
make test-unit               # Unit tests only (-m "not integration")
make test-integration        # Integration tests with real LDIF files
make test-singer             # Singer protocol compliance tests
make coverage-html           # Generate HTML coverage report for analysis

# Performance and specific tests
pytest -m slow               # Performance tests with large files
pytest -m "not slow"         # Fast tests for quick feedback loop
pytest -m error_handling     # Error handling and recovery tests
```

### Development Environment
```bash
# File-based development testing
echo "dn: dc=test,dc=com" > test.ldif
echo "objectClass: organization" >> test.ldif  
echo "dc: test" >> test.ldif

# Test with sample file
poetry run tap-ldif --config '{"file_path": "test.ldif"}' --discover
poetry run tap-ldif --config '{"file_path": "test.ldif"}' --catalog catalog.json
```

---

## 📊 SUCCESS METRICS (EVIDENCE-BASED MEASUREMENT)

### Code Quality Metrics (AUTOMATED VALIDATION)
```bash
# Coverage measurement (TARGET: 90%)
pytest --cov=src --cov-report=term | grep "TOTAL" | awk '{print $4}'

# Type safety assessment (TARGET: 0 errors)
mypy src/ --strict --show-error-codes 2>&1 | wc -l

# Linting compliance (TARGET: 0 errors)
ruff check src/ --statistics | grep -o "[0-9]\+ errors"

# Security assessment (TARGET: 0 critical vulnerabilities)  
bandit -r src/ -f json 2>/dev/null | jq '.metrics._totals.SEVERITY_RISK_HIGH' || echo 0
```

### Singer Protocol Compliance (FUNCTIONAL VALIDATION)
```bash
# Catalog discovery success
make discover >/dev/null 2>&1 && echo "✅ Discovery OK" || echo "❌ Discovery FAILED"

# Data extraction success  
make run >/dev/null 2>&1 && echo "✅ Extraction OK" || echo "❌ Extraction FAILED"

# Schema validation
singer-check-tap --catalog catalog.json < /dev/null && echo "✅ Schema OK" || echo "❌ Schema FAILED"
```

### LDIF Processing Functionality (DOMAIN-SPECIFIC VALIDATION)
```bash
# LDIF processing test
make ldif-test >/dev/null 2>&1 && echo "✅ LDIF OK" || echo "❌ LDIF FAILED"

# flext-ldif integration test
python -c "
from flext_tap_ldif.ldif_processor import FlextLDIFProcessorWrapper
from flext_core import FlextContainer
wrapper = FlextLDIFProcessorWrapper(FlextContainer.get_global())
print('✅ flext-ldif integration OK')
" && echo "Integration test OK"

# File processing test
python -c "
from flext_tap_ldif import TapLDIF
tap = TapLDIF()
streams = list(tap.discover_streams())  
print(f'✅ {len(streams)} streams discovered')
" && echo "Stream discovery OK"
```

---

## 🔍 PROJECT-SPECIFIC CONTEXT (LDIF PROCESSING DOMAIN EXPERTISE)

### LDIF Format Processing Excellence

#### File Format Support
- **LDIF v1 Specification**: Complete compliance with RFC 2849
- **Encoding Support**: UTF-8 (default), UTF-16, Latin-1, with automatic detection
- **Content Types**: Base64 encoded values, binary data, multi-line values
- **Change Records**: Add, delete, modify, moddn operations (if applicable)
- **Validation**: Schema compliance, syntax validation, referential integrity

#### Performance Optimization
- **Streaming Processing**: Memory-efficient processing without loading entire files
- **Configurable Batching**: Adjustable batch sizes (1-10,000 entries) for memory management
- **File Size Limits**: Configurable maximum file sizes (1-1,000 MB) for resource protection
- **Error Recovery**: Lenient parsing mode with error counting and reporting

### Configuration Excellence

#### File Location Strategies
```python
# Single file processing
{
    "file_path": "/data/exports/users.ldif",
    "batch_size": 500,
    "strict_parsing": true
}

# Directory processing with pattern
{
    "directory_path": "/data/exports/",
    "file_pattern": "*.ldif",
    "batch_size": 2000,
    "max_file_size_mb": 200
}

# Current directory pattern
{
    "file_pattern": "export_*.ldif",
    "encoding": "utf-16",
    "include_operational_attributes": true
}
```

#### Advanced Filtering Configuration
```python
# Comprehensive filtering example
{
    "file_path": "/data/migration.ldif",
    "base_dn_filter": "ou=people,dc=company,dc=com",
    "object_class_filter": ["person", "inetOrgPerson"],
    "attribute_filter": ["cn", "sn", "mail", "uid"],
    "exclude_attributes": ["userPassword", "jpegPhoto"],
    "strict_parsing": false,
    "batch_size": 1000
}
```

### flext-ldif Integration Patterns

#### Infrastructure Reuse Excellence
```python
# Leverage flext-ldif capabilities (NEVER reimplement)
from flext_ldif import (
    LdifProcessor,        # Core LDIF processing engine
    LdifValidator,        # LDIF format validation
    LdifSchemaAnalyzer,   # Schema discovery from LDIF content
    LdifEntryFilter,      # Entry filtering capabilities
    LdifErrorHandler      # Error handling and recovery
)

class FlextTapLdifService(FlextDomainService):
    """Service leveraging flext-ldif infrastructure."""
    
    def __init__(self, **data) -> None:
        super().__init__(**data)
        # Get flext-ldif services from container
        self._ldif_processor = self._container.get(LdifProcessor)
        self._ldif_validator = self._container.get(LdifValidator)
        self._schema_analyzer = self._container.get(LdifSchemaAnalyzer)
```

#### Processing Pipeline Integration
```python
def process_with_pipeline(self, file_path: str, config: dict) -> FlextResult[Iterator[dict]]:
    """Process LDIF using flext-ldif pipeline capabilities."""
    
    # Step 1: Validate file format using flext-ldif
    validation_result = self._ldif_validator.validate_file(file_path)
    if validation_result.is_failure:
        return FlextResult[Iterator[dict]].fail(f"Validation failed: {validation_result.error}")
    
    # Step 2: Create processing pipeline
    pipeline_result = self._ldif_processor.create_processing_pipeline(
        file_path=file_path,
        batch_size=config.get("batch_size", 1000),
        encoding=config.get("encoding", "utf-8"),
        strict_mode=config.get("strict_parsing", True)
    )
    
    if pipeline_result.is_success:
        return FlextResult[Iterator[dict]].ok(pipeline_result.value)
    else:
        return FlextResult[Iterator[dict]].fail(f"Pipeline creation failed: {pipeline_result.error}")
```

### Singer Protocol Implementation Details

#### Stream Schema Generation
```python
def generate_stream_schema(self, sample_entries: list[dict]) -> dict:
    """Generate Singer schema from LDIF entries."""
    
    schema = {
        "type": "object",
        "properties": {
            "dn": {
                "type": "string",
                "description": "Distinguished Name (primary key)"
            },
            "objectClass": {
                "type": "array",
                "items": {"type": "string"},
                "description": "LDAP object classes"
            }
        },
        "required": ["dn"],
        "additionalProperties": True
    }
    
    # Analyze sample entries for additional properties
    for entry in sample_entries:
        for attr_name, attr_value in entry.items():
            if attr_name not in schema["properties"]:
                schema["properties"][attr_name] = self._infer_attribute_schema(attr_value)
    
    return schema

def _infer_attribute_schema(self, value: Any) -> dict:
    """Infer Singer schema for LDIF attribute value."""
    if isinstance(value, list):
        return {
            "type": "array", 
            "items": {"type": "string"},
            "description": "Multi-value LDAP attribute"
        }
    elif isinstance(value, str):
        return {
            "type": "string",
            "description": "String LDAP attribute"
        }
    else:
        return {
            "type": "string", 
            "description": "LDAP attribute (converted to string)"
        }
```

---

## 🎯 QUALITY ACHIEVEMENT ROADMAP (PHASE-BY-PHASE SUCCESS)

### Week 1: Foundation & Infrastructure Integration (PREREQUISITE SUCCESS)
- [ ] **Quality Gate Repair**: Achieve `make validate` success (0 errors)
- [ ] **flext-ldif Integration Assessment**: Document current integration patterns and capabilities
- [ ] **Test Coverage Assessment**: Document current coverage and identify gaps
- [ ] **Singer Compliance**: Ensure basic discover/extract functionality works

### Week 2: Service Architecture Enhancement (INFRASTRUCTURE LEVERAGE)
- [ ] **Enhanced FlextLDIFProcessorWrapper**: Comprehensive wrapper for flext-ldif integration
- [ ] **Unified Service Implementation**: `FlextTapLdifService` with all functionality consolidated
- [ ] **Configuration Enhancement**: Advanced filtering and validation capabilities
- [ ] **FlextResult Migration**: Replace all exception handling with FlextResult pattern

### Week 3: Protocol & Processing Excellence (SINGER + LDIF MASTERY)
- [ ] **Stream Implementation Enhancement**: Advanced LDIF entries stream with error handling
- [ ] **Schema Discovery**: Dynamic schema generation from LDIF content analysis
- [ ] **Performance Optimization**: Streaming processing with memory efficiency
- [ ] **Error Handling Excellence**: Comprehensive error recovery and reporting

### Week 4: Testing & Validation Excellence (90% COVERAGE TARGET)
- [ ] **Integration Tests**: Real LDIF file processing tests with diverse formats
- [ ] **Performance Tests**: Large file processing with memory and time validation
- [ ] **Error Scenario Tests**: File access errors, malformed content, encoding issues
- [ ] **Coverage Validation**: Achieve and maintain 90% test coverage

### Success Validation (EVIDENCE-BASED CONFIRMATION)
```bash
# Final success confirmation (ALL must pass)
make validate                    # ✅ Zero errors
pytest --cov=src --cov-report=term | grep "90%"  # ✅ Coverage target
make discover && make run        # ✅ Singer compliance
make ldif-test                   # ✅ LDIF processing excellence
python -c "from flext_ldif import LdifProcessor; print('✅ Infrastructure integration')"
```

---

**PROJECT AUTHORITY**: FLEXT-TAP-LDIF  
**REFACTORING AUTHORITY**: Evidence-based validation required for all success claims  
**QUALITY AUTHORITY**: Zero tolerance - 90% coverage, zero type errors, full Singer compliance  
**INTEGRATION AUTHORITY**: Must leverage flext-ldif infrastructure efficiently while maintaining FLEXT ecosystem integration