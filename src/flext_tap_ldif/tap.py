"""tap-ldif main tap class.

This module implements the main tap class for LDIF file format data extraction.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from singer_sdk import Tap
from singer_sdk import singer_typing as th

from flext_tap_ldif.config import TapLDIFConfig
from flext_tap_ldif.streams import LDIFEntriesStream

if TYPE_CHECKING:
    from singer_sdk.streams import Stream


logger = logging.getLogger(__name__)


class TapLDIF(Tap):
    """Singer tap for LDIF file format data extraction."""

    name = "tap-ldif"
    config_class = TapLDIFConfig

    # Keep the jsonschema for backward compatibility
    config_jsonschema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "file_path",
            th.StringType,
            required=True,
            description="Path to the LDIF file to extract data from",
        ),
        th.Property(
            "file_pattern",
            th.StringType,
            description="Pattern for multiple LDIF files (e.g., '*.ldif')",
        ),
        th.Property(
            "directory_path",
            th.StringType,
            description="Directory containing LDIF files",
        ),
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
            "encoding",
            th.StringType,
            default="utf-8",
            description="File encoding (default: utf-8)",
        ),
        th.Property(
            "batch_size",
            th.IntegerType,
            default=1000,
            description="Number of entries to process in each batch",
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
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            LDIFEntriesStream(
                tap=self,
                name="ldif_entries",
                schema=self._get_ldif_entries_schema(),
            ),
        ]

    def _get_ldif_entries_schema(self) -> dict[str, Any]:
        """Get the schema for LDIF entries stream.

        Returns:
            Schema definition for LDIF entries.
        """
        return th.PropertiesList(
            th.Property("dn", th.StringType, required=True, description="Distinguished Name"),
            th.Property("object_class", th.ArrayType(th.StringType), description="Object classes"),
            th.Property("attributes", th.ObjectType(), description="LDAP attributes"),
            th.Property("change_type", th.StringType, description="LDIF change type"),
            th.Property("source_file", th.StringType, description="Source LDIF file"),
            th.Property("line_number", th.IntegerType, description="Line number in source file"),
            th.Property("entry_size", th.IntegerType, description="Size of entry in bytes"),
        ).to_dict()


def main() -> None:
    """Main function for the tap."""
    TapLDIF.cli()


if __name__ == "__main__":
    main()