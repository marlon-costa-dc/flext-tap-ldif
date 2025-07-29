"""Stream classes for FLEXT Tap LDIF."""

# MIGRATED: Singer SDK imports centralized via flext-meltano
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from flext_core import get_logger

if TYPE_CHECKING:
    from collections.abc import Mapping

from flext_meltano import Stream, th

from flext_tap_ldif.ldif_processor import FlextLDIFProcessorWrapper

if TYPE_CHECKING:
    from collections.abc import Iterable

    from flext_meltano.singer import FlextMeltanoTap as Tap

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

    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the LDIF entries stream.

        Args:
            tap: The parent tap instance.
            name: The stream name.
            schema: The stream schema.

        """
        super().__init__(tap, schema, name)
        self._processor = FlextLDIFProcessorWrapper(dict(tap.config))

    def get_records(
        self,
        context: Mapping[str, Any] | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Return a generator of record-type dictionary objects.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            Dictionary representations of LDIF entries.

        """
        config = self._tap.config

        # Determine input files to process
        files_to_process = self._get_input_files()

        logger.info(f"Processing {len(files_to_process)} LDIF files")

        for file_path in files_to_process:
            logger.info(f"Processing file: {file_path}")
            try:
                # Process the LDIF file and yield records
                yield from self._processor.process_file(file_path)
            except (RuntimeError, ValueError, TypeError) as e:
                if config.get("strict_parsing", True):
                    logger.exception(f"Error processing file {file_path}")
                    raise
                else:
                    logger.warning(f"Skipping file {file_path} due to error: {e}")
                    continue

    def _get_input_files(self) -> list[Path]:
        """Get list of LDIF files to process based on configuration.

        Returns:
            List of Path objects for files to process.

        """
        config = self._tap.config
        files_to_process = []

        # Single file
        if config.get("file_path"):
            file_path = Path(config["file_path"])
            if file_path.exists() and file_path.is_file():
                files_to_process.append(file_path)

        # Directory with pattern
        if config.get("directory_path"):
            directory = Path(config["directory_path"])
            if directory.exists() and directory.is_dir():
                pattern = config.get("file_pattern", "*.ldif")
                files_to_process.extend(directory.glob(pattern))

        # Pattern in current directory
        elif config.get("file_pattern"):
            current_dir = Path()
            pattern = config["file_pattern"]
            files_to_process.extend(current_dir.glob(pattern))

        # Filter by file size limit
        max_size_bytes = config.get("max_file_size_mb", 100) * 1024 * 1024
        filtered_files = []
        for file_path in files_to_process:
            try:
                if file_path.stat().st_size <= max_size_bytes:
                    filtered_files.append(file_path)
                else:
                    logger.warning(
                        f"Skipping file {file_path} - size {file_path.stat().st_size} bytes "
                        f"exceeds limit of {max_size_bytes} bytes",
                    )
            except OSError as e:
                logger.warning(f"Could not check size for file {file_path}: {e}")

        return sorted(filtered_files)
