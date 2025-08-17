"""Test configuration for flext-tap-ldif.

Provides pytest fixtures and configuration for testing LDIF tap functionality
using Singer protocol and real LDIF file processing.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from collections.abc import Generator
    from pathlib import Path


# Test environment setup
@pytest.fixture(autouse=True)
def set_test_environment() -> Generator[None]:
    """Set test environment variables."""
    os.environ["FLEXT_ENV"] = "test"
    os.environ["FLEXT_LOG_LEVEL"] = "debug"
    os.environ["SINGER_SDK_LOG_LEVEL"] = "debug"
    yield
    # Cleanup
    os.environ.pop("FLEXT_ENV", None)
    os.environ.pop("FLEXT_LOG_LEVEL", None)
    os.environ.pop("SINGER_SDK_LOG_LEVEL", None)


# LDIF test data fixtures
@pytest.fixture
def sample_ldif_content() -> str:
    """Sample LDIF content for testing."""
    return """version: 1

dn: cn=John Doe,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: person
cn: John Doe
sn: Doe
givenName: John
mail: john.doe@example.com
telephoneNumber: +1-555-123-4567
userPassword:: e1NTSEF9VGVzdFBhc3N3b3JkMTIz

dn: cn=Jane Smith,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: person
cn: Jane Smith
sn: Smith
givenName: Jane
mail: jane.smith@example.com
telephoneNumber: +1-555-987-6543

dn: cn=Administrators,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: Administrators
description: System administrators group
member: cn=John Doe,ou=users,dc=example,dc=com
member: cn=Jane Smith,ou=users,dc=example,dc=com

dn: cn=IT Department,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: IT Department
description: Information Technology department
member: cn=John Doe,ou=users,dc=example,dc=com
"""


@pytest.fixture
def sample_ldif_changes() -> str:
    """Sample LDIF changes content for testing."""
    return """version: 1

dn: cn=John Doe,ou=users,dc=example,dc=com
changetype: modify
replace: telephoneNumber
telephoneNumber: +1-555-111-2222
-
add: description
description: Senior System Administrator
-

dn: cn=New User,ou=users,dc=example,dc=com
changetype: add
objectClass: inetOrgPerson
objectClass: person
cn: New User
sn: User
givenName: New
mail: new.user@example.com

dn: cn=Old User,ou=users,dc=example,dc=com
changetype: delete
"""


@pytest.fixture
def sample_ldif_file(tmp_path: Path, sample_ldif_content: str) -> Path:
    """Create sample LDIF file for testing."""
    ldif_file = tmp_path / "test.ldif"
    ldif_file.write_text(sample_ldif_content, encoding="utf-8")
    return ldif_file


@pytest.fixture
def sample_ldif_changes_file(tmp_path: Path, sample_ldif_changes: str) -> Path:
    """Create sample LDIF changes file for testing."""
    ldif_file = tmp_path / "changes.ldif"
    ldif_file.write_text(sample_ldif_changes, encoding="utf-8")
    return ldif_file


@pytest.fixture
def ldif_directory(
    tmp_path: Path,
    sample_ldif_content: str,
    sample_ldif_changes: str,
) -> Path:
    """Create directory with multiple LDIF files."""
    ldif_dir = tmp_path / "ldif_files"
    ldif_dir.mkdir()

    # Create multiple LDIF files
    (ldif_dir / "users.ldif").write_text(sample_ldif_content, encoding="utf-8")
    (ldif_dir / "changes.ldif").write_text(sample_ldif_changes, encoding="utf-8")

    # Create additional test file
    additional_content = """version: 1

dn: cn=Test User,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: person
cn: Test User
sn: User
givenName: Test
mail: test.user@example.com
"""
    (ldif_dir / "additional.ldif").write_text(additional_content, encoding="utf-8")

    return ldif_dir


# Tap configuration fixtures
@pytest.fixture
def basic_tap_config(sample_ldif_file: Path) -> dict[str, object]:
    """Basic LDIF tap configuration."""
    return {
      "ldif_file_path": str(sample_ldif_file),
      "file_pattern": "*.ldif",
      "encoding": "utf-8",
      "processing_mode": "entries",
      "max_entries_per_batch": 100,
      "auto_discover_schema": True,
      "validate_entries": True,
      "enable_streaming": True,
    }


@pytest.fixture
def changes_tap_config(sample_ldif_changes_file: Path) -> dict[str, object]:
    """LDIF tap configuration for changes processing."""
    return {
      "ldif_file_path": str(sample_ldif_changes_file),
      "file_pattern": "*.ldif",
      "encoding": "utf-8",
      "processing_mode": "changes",
      "max_entries_per_batch": 50,
      "auto_discover_schema": True,
      "validate_entries": True,
      "enable_streaming": True,
    }


@pytest.fixture
def directory_tap_config(ldif_directory: Path) -> dict[str, object]:
    """LDIF tap configuration for directory processing."""
    return {
      "ldif_file_path": str(ldif_directory),
      "file_pattern": "*.ldif",
      "encoding": "utf-8",
      "processing_mode": "entries",
      "max_entries_per_batch": 100,
      "auto_discover_schema": True,
      "validate_entries": True,
      "enable_streaming": True,
      "enable_parallel_processing": True,
    }


@pytest.fixture
def filtered_tap_config(sample_ldif_file: Path) -> dict[str, object]:
    """LDIF tap configuration with filters."""
    return {
      "ldif_file_path": str(sample_ldif_file),
      "file_pattern": "*.ldif",
      "encoding": "utf-8",
      "processing_mode": "entries",
      "max_entries_per_batch": 100,
      "auto_discover_schema": True,
      "validate_entries": True,
      "include_object_classes": ["inetOrgPerson"],
      "exclude_dns": ["ou=groups"],
    }


# Large test data fixtures
@pytest.fixture
def large_ldif_file(tmp_path: Path) -> Path:
    """Create large LDIF file for performance testing."""
    ldif_file = tmp_path / "large.ldif"

    with ldif_file.open("w", encoding="utf-8") as f:
      f.write("version: 1\n\n")

      # Generate 1000 entries for performance testing
      for i in range(1000):
          f.write(f"dn: cn=user{i:04d},ou=users,dc=example,dc=com\n")
          f.write("objectClass: inetOrgPerson\n")
          f.write("objectClass: person\n")
          f.write(f"cn: user{i:04d}\n")
          f.write(f"sn: User{i:04d}\n")
          f.write("givenName: User\n")
          f.write(f"mail: user{i:04d}@example.com\n")
          f.write(f"employeeNumber: {i:04d}\n")
          f.write("\n")

    return ldif_file


@pytest.fixture
def performance_tap_config(large_ldif_file: Path) -> dict[str, object]:
    """LDIF tap configuration for performance testing."""
    return {
      "ldif_file_path": str(large_ldif_file),
      "file_pattern": "*.ldif",
      "encoding": "utf-8",
      "processing_mode": "entries",
      "max_entries_per_batch": 250,
      "auto_discover_schema": True,
      "validate_entries": True,
      "enable_streaming": True,
      "buffer_size": 16384,
      "max_memory_usage": 50 * 1024 * 1024,  # 50MB
    }


# Binary data fixtures
@pytest.fixture
def binary_ldif_content() -> str:
    """LDIF content with binary attributes."""
    return """version: 1

dn: cn=Binary User,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: person
cn: Binary User
sn: User
givenName: Binary
mail: binary.user@example.com
userCertificate;binary:: MIICXjCCAcegAwIBAgIJAODNcKgAQMRAMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMTgwNjA1MTI0ODM3WhcNMTkwNjA1MTI0ODM3WjBFMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDZFQZ1ZZ1Z
jpegPhoto:: /9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=
"""


@pytest.fixture
def binary_ldif_file(tmp_path: Path, binary_ldif_content: str) -> Path:
    """Create LDIF file with binary attributes."""
    ldif_file = tmp_path / "binary.ldif"
    ldif_file.write_text(binary_ldif_content, encoding="utf-8")
    return ldif_file


# Encoding test fixtures
@pytest.fixture
def utf16_ldif_file(tmp_path: Path) -> Path:
    """Create UTF-16 encoded LDIF file."""
    content = """version: 1

dn: cn=Unicode User,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: person
cn: Unicode User
sn: Üser
givenName: Ünicöde
mail: unicode.user@example.com
description: User with unicode characters: àáâãäåæç
"""

    ldif_file = tmp_path / "utf16.ldif"
    ldif_file.write_text(content, encoding="utf-16")
    return ldif_file


# Singer protocol fixtures
@pytest.fixture
def singer_catalog_config() -> dict[str, object]:
    """Singer catalog configuration."""
    return {
      "streams": [
          {
              "tap_stream_id": "ldif_entries",
              "schema": {
                  "type": "object",
                  "properties": {
                      "dn": {"type": "string"},
                      "source_file": {"type": "string"},
                      "source_file_mtime": {"type": "number"},
                      "objectClass": {"type": "array", "items": {"type": "string"}},
                      "cn": {"type": "array", "items": {"type": "string"}},
                      "mail": {"type": "array", "items": {"type": "string"}},
                  },
              },
              "metadata": [
                  {
                      "breadcrumb": [],
                      "metadata": {
                          "replication-method": "INCREMENTAL",
                          "replication-key": "source_file_mtime",
                          "selected": True,
                      },
                  },
              ],
          },
      ],
    }


@pytest.fixture
def singer_state() -> dict[str, object]:
    """Singer state for incremental sync."""
    return {
      "currently_syncing": None,
      "bookmarks": {
          "ldif_entries": {
              "replication_key_value": 1640995200.0,  # 2022-01-01 00:00:00
              "version": 1,
              "processed_files": [],
          },
      },
    }


# Error handling fixtures
@pytest.fixture
def invalid_ldif_content() -> str:
    """Invalid LDIF content for error testing."""
    return """version: 1

dn: cn=Invalid User,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: person
cn: Invalid User
sn: User
invalid_line_without_colon
mail: invalid.user@example.com
"""


@pytest.fixture
def invalid_ldif_file(tmp_path: Path, invalid_ldif_content: str) -> Path:
    """Create invalid LDIF file for error testing."""
    ldif_file = tmp_path / "invalid.ldif"
    ldif_file.write_text(invalid_ldif_content, encoding="utf-8")
    return ldif_file


# Performance benchmarking fixtures
@pytest.fixture
def benchmark_config() -> dict[str, object]:
    """Configuration for performance benchmarking."""
    return {
      "max_entries_to_process": 1000,
      "expected_processing_time": 30.0,  # seconds
      "memory_limit": 100 * 1024 * 1024,  # 100MB
      "batch_sizes": [50, 100, 250, 500, 1000],
    }


# Pytest markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "ldif: LDIF-specific tests")
    config.addinivalue_line("markers", "singer: Singer protocol tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "binary: Binary data tests")
    config.addinivalue_line("markers", "encoding: Encoding tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# Mock services
@pytest.fixture
def mock_ldif_tap() -> object:
    """Mock LDIF tap for testing."""

    class MockLDIFTap:
      def __init__(self, config: dict[str, object]) -> None:
          self.config = config
          self.discovered_streams: list[dict[str, object]] = []

      def discover_streams(self) -> list[dict[str, object]]:
          return self.discovered_streams

      async def sync_records(self) -> list[dict[str, object]]:
          return [
              {
                  "dn": "cn=test,ou=users,dc=example,dc=com",
                  "objectClass": ["inetOrgPerson", "person"],
                  "cn": ["test"],
                  "mail": ["test@example.com"],
                  "source_file": "test.ldif",
                  "source_file_mtime": 1640995200.0,
              },
          ]

    return MockLDIFTap


@pytest.fixture
def mock_ldif_parser() -> object:
    """Mock LDIF parser for testing."""

    class MockLDIFParser:
      def __init__(self, config: dict[str, object]) -> None:
          self.config = config
          self.parsed_entries: list[dict[str, object]] = []

      async def parse_file(self, file_path: str) -> dict[str, object]:  # noqa: ARG002
          return {
              "success": True,
              "entries": self.parsed_entries,
              "errors": [],
          }

      def add_mock_entry(self, entry: dict[str, object]) -> None:
          self.parsed_entries.append(entry)

    return MockLDIFParser
