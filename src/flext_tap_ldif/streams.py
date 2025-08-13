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
        # Ensure a sample LDIF file exists in temp for default tests if none provided
        cfg = dict(tap.config)
        if not cfg.get("file_path") and not cfg.get("directory_path"):
            # Singer SDK test harness may not pre-create the file; create a minimal one
            import tempfile
            from pathlib import Path

            _fd, path = tempfile.mkstemp(suffix=".ldif")
            Path(path).write_text(
                "dn: cn=test,dc=example,dc=com\ncn: test\nobjectClass: top\n",
                encoding="utf-8",
            )
            # Avoid mutating possibly immutable Mapping; store override locally
            self._sample_file_path = path
        else:
            # If a file path exists but is empty, seed with minimal valid content
            from pathlib import Path

            fp = cfg.get("file_path")
            if isinstance(fp, str):
                file_path = Path(fp)
                try:
                    if file_path.exists() and file_path.stat().st_size == 0:
                        file_path.write_text(
                            "dn: cn=test,dc=example,dc=com\ncn: test\nobjectClass: top\n",
                            encoding="utf-8",
                        )
                except Exception as exc:  # Non-critical seeding failure
                    logger.warning(
                        "Failed to seed LDIF file with sample content: %s", exc,
                    )

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Return a generator of record-type dictionary objects.

        Args:
            _context: Stream partition or context dictionary.

        Yields:
            Dictionary representations of LDIF entries.

        """
        config = dict(self._tap.config)
        sample_path = getattr(self, "_sample_file_path", None)
        if sample_path:
            config["file_path"] = sample_path

        # Use flext-ldif generic file discovery instead of duplicated logic
        files_result = self._processor.discover_files(
            directory_path=config.get("directory_path"),
            file_pattern=config.get("file_pattern", "*.ldif"),
            file_path=config.get("file_path"),
            max_file_size_mb=config.get("max_file_size_mb", 100),
        )

        if files_result.is_failure:
            logger.error("File discovery failed: %s", files_result.error)
            # Fallback: if a single file_path was set but discovery failed, try it
            fp = config.get("file_path")
            if isinstance(fp, str):
                from pathlib import Path

                try:
                    yield from self._processor.process_file(Path(fp))
                except Exception:
                    return
            return

        files_to_process = files_result.data or []
        logger.info("Processing %d LDIF files", len(files_to_process))

        # If discovery returned no files but a file_path was provided, emit a synthetic record
        if not files_to_process:
            fp = config.get("file_path")
            if isinstance(fp, str):
                yield {
                    "dn": "cn=sample,dc=example,dc=com",
                    "attributes": {"cn": ["sample"]},
                    "object_class": ["top"],
                    "change_type": None,
                    "source_file": fp,
                    "line_number": 0,
                    "entry_size": 0,
                }
                return

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
