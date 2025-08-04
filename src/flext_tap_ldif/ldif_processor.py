"""LDIF file processing module for FLEXT Tap LDIF using flext-ldif infrastructure.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module eliminates code duplication by using the FLEXT LDIF infrastructure
implementation from flext-ldif project.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from flext_core import FlextResult, get_logger
from flext_ldif import FlextLdifAPI, flext_ldif_get_api

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from flext_ldif import FlextLdifEntry

logger = get_logger(__name__)

# Use flext-ldif processor instead of reimplementing LDIF functionality
LDIFProcessor = FlextLdifAPI

# Backward compatibility alias removed (causes self-assignment warning)


class FlextLDIFProcessorWrapper:
    """Wrapper for FlextLDIFProcessor to maintain API compatibility."""

    def __init__(self, config: dict[str, object]) -> None:
        """Initialize the LDIF processor using flext-ldif infrastructure.

        Args:
            config: Configuration dictionary from the tap.

        """
        self.config = config
        self._api = flext_ldif_get_api()

    def process_file(self, file_path: Path) -> Generator[dict[str, object]]:
        """Process a single LDIF file and yield records using flext-ldif.

        Args:
            file_path: Path to the LDIF file.

        Yields:
            Dictionary records representing LDIF entries.

        """
        logger.info(f"Processing LDIF file: {file_path}")
        try:
            # Ensure encoding is properly typed
            encoding = self.config.get("encoding", "utf-8")
            if not isinstance(encoding, str):
                encoding = "utf-8"

            with file_path.open("r", encoding=encoding) as file:
                content = file.read()
                parse_result = cast(
                    "FlextResult[list[FlextLdifEntry]]",
                    self._api.parse(content),
                )
                if not parse_result.success:
                    msg: str = f"Failed to parse LDIF: {parse_result.error}"
                    raise ValueError(msg)
                entries = parse_result.data

                if entries is None:
                    logger.warning(f"No entries found in file: {file_path}")
                    return

                for entry in entries:
                    # Convert FlextLdifEntry to expected dictionary format
                    yield {
                        "dn": str(entry.dn),
                        "attributes": entry.attributes.attributes,
                        "object_class": entry.attributes.attributes.get(
                            "objectClass",
                            [],
                        ),
                        "change_type": None,  # Change records not supported in simple parse
                        "source_file": str(file_path),
                        "line_number": 0,  # Line numbers not available in simplified parse
                        "entry_size": len(str(entry).encode("utf-8")),
                    }
        except (RuntimeError, ValueError, TypeError):
            logger.exception(f"Failed to process LDIF file: {file_path}")
            if self.config.get("strict_parsing", True):
                raise


# Create the original class name for backward compatibility
FlextLDIFProcessor: type[FlextLDIFProcessorWrapper] = FlextLDIFProcessorWrapper

__all__: list[str] = [
    "FlextLDIFProcessor",
    "LDIFProcessor",
]
