"""LDIF file processing module for FLEXT Tap LDIF using flext-ldif infrastructure.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module eliminates code duplication by using the FLEXT LDIF infrastructure
implementation from flext-ldif project.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import get_logger
from flext_ldif import FlextLdifProcessor, parse_ldif

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

logger = get_logger(__name__)

# Use flext-ldif processor instead of reimplementing LDIF functionality
LDIFProcessor = FlextLdifProcessor

# Backward compatibility alias removed (causes self-assignment warning)


class FlextLDIFProcessorWrapper:
    """Wrapper for FlextLDIFProcessor to maintain API compatibility."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the LDIF processor using flext-ldif infrastructure.

        Args:
            config: Configuration dictionary from the tap.

        """
        self.config = config
        self._processor = FlextLdifProcessor()

    def process_file(self, file_path: Path) -> Generator[dict[str, Any]]:
        """Process a single LDIF file and yield records using flext-ldif.

        Args:
            file_path: Path to the LDIF file.

        Yields:
            Dictionary records representing LDIF entries.

        """
        logger.info(f"Processing LDIF file: {file_path}")
        try:
            with file_path.open(
                "r", encoding=self.config.get("encoding", "utf-8"),
            ) as file:
                content = file.read()
                entries = parse_ldif(content)

                for entry in entries:
                    # Convert FlextLdifEntry to expected dictionary format
                    yield {
                        "dn": str(entry.dn),
                        "attributes": entry.attributes.attributes,
                        "object_class": entry.attributes.attributes.get(
                            "objectClass", [],
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

__all__ = [
    "FlextLDIFProcessor",
    "LDIFProcessor",
]
