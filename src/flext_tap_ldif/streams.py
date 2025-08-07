"""Stream classes for FLEXT Tap LDIF."""

# MIGRATED: Singer SDK imports centralized via flext-meltano
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from flext_core import get_logger

if TYPE_CHECKING:
    from collections.abc import Mapping

from flext_meltano import Stream, Tap, singer_typing as th

from flext_tap_ldif.ldif_processor import FlextLDIFProcessorWrapper

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = get_logger(__name__)


class LDIFEntriesStream(Stream):
    """Stream for LDIF entries."""

    name = "ldif_entries"
    primary_keys: ClassVar[list[str]] = ["dn"]  # Distinguished Name is the primary key
    replication_key = None  # LDIF files are typically snapshot data

    schema = th.PropertiesList(
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
        th.Property("entry_size", th.IntegerType, description="Size of entry in bytes"),
    ).to_dict()

    def __init__(self, tap: Tap) -> None:
        """Initialize the LDIF entries stream.

        Args:
            tap: The parent tap instance.

        """
        super().__init__(tap, name=self.name, schema=self.schema)
        self._processor = FlextLDIFProcessorWrapper(dict(tap.config))

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Return a generator of record-type dictionary objects.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            Dictionary representations of LDIF entries.

        """
        config = self._tap.config

        # Use flext-ldif generic file discovery instead of duplicated logic
        files_result = self._processor.discover_files(
            directory_path=config.get("directory_path"),
            file_pattern=config.get("file_pattern", "*.ldif"),
            file_path=config.get("file_path"),
            max_file_size_mb=config.get("max_file_size_mb", 100),
        )

        if files_result.is_failure:
            logger.error("File discovery failed: %s", files_result.error)
            return

        files_to_process = files_result.data or []
        logger.info("Processing %d LDIF files", len(files_to_process))

        for file_path in files_to_process:
            logger.info("Processing file: %s", file_path)
            try:
                # Process the LDIF file and yield records
                yield from self._processor.process_file(file_path)
            except (RuntimeError, ValueError, TypeError) as e:
                if config.get("strict_parsing", True):
                    logger.exception("Error processing file %s", file_path)
                    raise
                else:
                    logger.warning("Skipping file %s due to error: %s", file_path, e)
                    continue
