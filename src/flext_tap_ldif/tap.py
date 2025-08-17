"""tap-ldif main tap class.

This module implements the main tap class for LDIF file format data extraction.
"""

# MIGRATED: Singer SDK imports centralized via flext-meltano
from __future__ import annotations

from typing import ClassVar

from flext_core import get_logger
from flext_meltano import Stream, Tap, singer_typing as th
from flext_meltano.config import create_file_tap_schema

from flext_tap_ldif.config import TapLDIFConfig
from flext_tap_ldif.streams import LDIFEntriesStream

logger = get_logger(__name__)


class TapLDIF(Tap):
    """Singer tap for LDIF file format data extraction."""

    name: str = "tap-ldif"
    config_class = TapLDIFConfig
    # REAL DRY: Use centralized file-based schema from flext-meltano instead of duplicating
    config_jsonschema: ClassVar[dict[str, object]] = create_file_tap_schema(
      # LDIF-specific additional properties for tap-ldif
      additional_properties=th.PropertiesList(
          th.Property(
              "base_dn_filter",
              th.StringType,
              description="Filter entries by base DN pattern",
          ),
          th.Property(
              "object_class_filter",
              th.ArrayType(th.StringType),
              description="Filter entries by object class",
          ),
          th.Property(
              "attribute_filter",
              th.ArrayType(th.StringType),
              description="Include only specified attributes",
          ),
          th.Property(
              "exclude_attributes",
              th.ArrayType(th.StringType),
              description="Exclude specified attributes",
          ),
          th.Property(
              "include_operational_attributes",
              th.BooleanType,
              default=False,
              description="Include operational attributes in output",
          ),
          th.Property(
              "strict_parsing",
              th.BooleanType,
              default=True,
              description="Enable strict LDIF parsing (fail on errors)",
          ),
          th.Property(
              "max_file_size_mb",
              th.IntegerType,
              default=100,
              description="Maximum file size in MB to process",
          ),
      ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
      """Return a list of discovered streams.

      Returns:
          A list of discovered streams.

      """
      return [
          LDIFEntriesStream(tap=self),
      ]

    def _get_ldif_entries_schema(self) -> dict[str, object]:
      """Get the schema for LDIF entries stream.

      Returns:
          Schema definition for LDIF entries.

      """
      return th.PropertiesList(
          th.Property(
              "dn",
              th.StringType,
              required=True,
              description="Distinguished Name",
          ),
          th.Property(
              "object_class",
              th.ArrayType(th.StringType),
              description="Object classes",
          ),
          th.Property("attributes", th.ObjectType(), description="LDAP attributes"),
          th.Property("change_type", th.StringType, description="LDIF change type"),
          th.Property("source_file", th.StringType, description="Source LDIF file"),
          th.Property(
              "line_number",
              th.IntegerType,
              description="Line number in source file",
          ),
          th.Property(
              "entry_size",
              th.IntegerType,
              description="Size of entry in bytes",
          ),
      ).to_dict()


def main() -> None:
    """Run the tap entry point."""
    TapLDIF.cli()


if __name__ == "__main__":
    main()
