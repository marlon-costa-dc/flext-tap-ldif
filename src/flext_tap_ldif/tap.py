"""tap-ldif main tap class.

This module implements the main tap class for LDIF file format data extraction.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

"""
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


# MIGRATED: Singer SDK imports centralized via flext-meltano
from typing import ClassVar

from flext_core import FlextLogger
from flext_meltano import Stream, Tap, singer_typing as th

from flext_tap_ldif.config import TapLDIFConfig
from flext_tap_ldif.streams import LDIFEntriesStream

logger = FlextLogger(__name__)


class TapLDIF(Tap):
    """Singer tap for LDIF file format data extraction."""

    name: str = "tap-ldif"
    config_class = TapLDIFConfig
    # Schema combining file-based configuration with LDIF-specific properties
    config_jsonschema: ClassVar[FlextTypes.Core.Dict] = th.PropertiesList(
        # File-based properties
        th.Property(
            "file_path",
            th.StringType,
            description="Path to single LDIF file",
        ),
        th.Property(
            "directory_path",
            th.StringType,
            description="Directory containing LDIF files",
        ),
        th.Property(
            "file_pattern",
            th.StringType,
            default="*.ldif",
            description="File pattern for matching LDIF files in directory",
        ),
        th.Property(
            "encoding",
            th.StringType,
            default="utf-8",
            description="Text encoding for LDIF files",
        ),
        # LDIF-specific additional properties
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
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.

        """
        return [
            LDIFEntriesStream(tap=self),
        ]

    def _get_ldif_entries_schema(self) -> FlextTypes.Core.Dict:
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
