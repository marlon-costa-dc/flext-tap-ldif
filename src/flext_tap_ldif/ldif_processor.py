"""LDIF file processing module for FLEXT Tap LDIF."""

from __future__ import annotations

import base64
import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

logger = logging.getLogger(__name__)


class LDIFProcessor:
    """Processor for LDIF (LDAP Data Interchange Format) files."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the LDIF processor.

        Args:
            config: Configuration dictionary from the tap.

        """
        self.config = config
        self.encoding = config.get("encoding", "utf-8")
        self.batch_size = config.get("batch_size", 1000)
        self.base_dn_filter = config.get("base_dn_filter")
        self.object_class_filter = config.get("object_class_filter", [])
        self.attribute_filter = config.get("attribute_filter")
        self.exclude_attributes = config.get("exclude_attributes", [])
        self.include_operational = config.get("include_operational_attributes", False)
        self.strict_parsing = config.get("strict_parsing", True)

        # Compile regex patterns for performance
        self._dn_pattern = re.compile(r"^dn:\s*(.+)$", re.IGNORECASE)
        self._attr_pattern = re.compile(r"^([a-zA-Z][a-zA-Z0-9-]*)(::?)?\s*(.*)$")
        self._base64_pattern = re.compile(r"^([a-zA-Z][a-zA-Z0-9-]*)::\s*(.*)$")

    def process_file(self, file_path: Path) -> Generator[dict[str, Any]]:
        """Process a single LDIF file and yield records.

        Args:
            file_path: Path to the LDIF file.

        Yields:
            Dictionary records representing LDIF entries.

        """
        logger.info("Processing LDIF file: %s", file_path)
        try:
            with file_path.open("r", encoding=self.encoding) as file:
                yield from self._parse_ldif_content(file, str(file_path))
        except UnicodeDecodeError as e:
            error_msg = f"Unicode decode error in file {file_path}: {e}"
            if self.strict_parsing:
                raise ValueError(error_msg) from e
            else:
                logger.warning(error_msg)
                return

    def _parse_ldif_content(
        self,
        file: Iterator[str],
        source_file: str,
    ) -> Generator[dict[str, Any]]:
        """Parse LDIF content from file iterator.

        Args:
            file: File iterator yielding lines.
            source_file: Source file name for metadata.

        Yields:
            Dictionary records representing LDIF entries.

        """
        current_entry: dict[str, Any] = {}
        line_number = 0
        entry_start_line = 0
        entry_size = 0

        for raw_line in file:
            line_number += 1
            original_line = raw_line
            line = raw_line.rstrip("\r\n")
            entry_size += len(original_line.encode(self.encoding))

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Handle line continuations (lines starting with space)
            if line.startswith(" ") and current_entry:
                if current_entry.get("attributes"):
                    # Get the last attribute and append continuation
                    last_attr = list(current_entry["attributes"].keys())[-1]
                    if isinstance(current_entry["attributes"][last_attr], list):
                        current_entry["attributes"][last_attr][-1] += line[1:]
                    else:
                        current_entry["attributes"][last_attr] += line[1:]
                continue

            # Check for DN line (start of new entry)
            dn_match = self._dn_pattern.match(line)
            if dn_match:
                # Yield previous entry if exists
                if current_entry and self._should_include_entry(current_entry):
                    current_entry["source_file"] = source_file
                    current_entry["line_number"] = entry_start_line
                    current_entry["entry_size"] = entry_size
                    yield self._finalize_entry(current_entry)

                # Start new entry
                current_entry = {
                    "dn": dn_match.group(1).strip(),
                    "attributes": {},
                    "object_class": [],
                    "change_type": None,
                }
                entry_start_line = line_number
                entry_size = len(original_line.encode(self.encoding))
                continue

            # Parse attribute lines
            if current_entry:
                self._parse_attribute_line(line, current_entry, line_number)

        # Yield last entry if exists
        if current_entry and self._should_include_entry(current_entry):
            current_entry["source_file"] = source_file
            current_entry["line_number"] = entry_start_line
            current_entry["entry_size"] = entry_size
            yield self._finalize_entry(current_entry)

    def _parse_attribute_line(
        self,
        line: str,
        entry: dict[str, Any],
        line_number: int,
    ) -> None:
        """Parse an attribute line and add to entry.

        Args:
            line: The attribute line to parse.
            entry: The current entry being built.
            line_number: Current line number for error reporting.

        """
        # Handle base64 encoded values
        base64_match = self._base64_pattern.match(line)
        if base64_match:
            attr_name = base64_match.group(1).lower()
            encoded_value = base64_match.group(2)
            try:
                base64.b64decode(encoded_value).decode(self.encoding)
            except Exception as e:
                if self.strict_parsing:
                    msg = f"Failed to decode base64 value at line {line_number}: {e}"
                    raise ValueError(msg) from e
                logger.warning(
                    "Skipping invalid base64 value at line %s: %s",
                    line_number,
                    e,
                )
            return

        # Handle regular attribute lines
        attr_match = self._attr_pattern.match(line)
        if attr_match:
            attr_name = attr_match.group(1).lower()
            value = attr_match.group(3)
            self._add_attribute_value(entry, attr_name, value)
        elif self.strict_parsing and not line.startswith(
            "-",
        ):  # Skip change record separators
            raise ValueError(msg)
            raise ValueError(
                msg,
            )

    def _add_attribute_value(
        self,
        entry: dict[str, Any],
        attr_name: str,
        value: str,
    ) -> None:
        """Add an attribute value to the entry.

        Args:
            entry: The entry to add the attribute to.
            attr_name: The attribute name.
            value: The attribute value.

        """
        # Handle special attributes
        if attr_name == "objectclass":
            entry["object_class"].append(value)
        elif attr_name == "changetype":
            entry["change_type"] = value

        # Apply attribute filtering
        if self.attribute_filter and attr_name not in self.attribute_filter:
            return
        if attr_name in self.exclude_attributes:
            return
        if not self.include_operational and self._is_operational_attribute(attr_name):
            return

        # Add to attributes dictionary
        if attr_name in entry["attributes"]:
            # Convert to list if multiple values
            if not isinstance(entry["attributes"][attr_name], list):
                entry["attributes"][attr_name] = [entry["attributes"][attr_name]]
            entry["attributes"][attr_name].append(value)
        else:
            entry["attributes"][attr_name] = value

    def _should_include_entry(self, entry: dict[str, Any]) -> bool:
        """Determine if an entry should be included based on filters.

        Args:
            entry: The entry to check.

        Returns:
            True if the entry should be included, False otherwise.

        """
        # Check base DN filter
        if self.base_dn_filter:
            dn = entry.get("dn", "").lower()
            base_dn = self.base_dn_filter.lower()
            if not dn.endswith(base_dn):
                return False

        # Check object class filter
        if self.object_class_filter:
            entry_object_classes = [oc.lower() for oc in entry.get("object_class", [])]
            filter_object_classes = [oc.lower() for oc in self.object_class_filter]
            if not any(oc in entry_object_classes for oc in filter_object_classes):
                return False

        return True

    def _is_operational_attribute(self, attr_name: str) -> bool:
        """Check if an attribute is operational.

        Args:
            attr_name: The attribute name to check.

        Returns:
            True if the attribute is operational, False otherwise.

        """
        operational_attrs = {
            "createtimestamp",
            "creatorsname",
            "modifytimestamp",
            "modifiersname",
            "structuralobjectclass",
            "governingstructurerule",
            "entrydn",
            "entryuuid",
            "entrycsn",
            "contextcsn",
            "pwdchangedtime",
            "pwdaccountlockedtime",
            "pwdfailuretime",
            "pwdhistory",
            "pwdgraceusetime",
        }
        return attr_name.lower() in operational_attrs

    def _finalize_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Finalize an entry before yielding.

        Args:
            entry: The entry to finalize.

        Returns:
            The finalized entry.

        """
        # Ensure object_class is always a list
        if not entry["object_class"]:
            entry["object_class"] = []

        # Convert single-value lists back to strings for consistency
        for attr_name, attr_value in entry["attributes"].items():
            if isinstance(attr_value, list) and len(attr_value) == 1:
                entry["attributes"][attr_name] = attr_value[0]

        return entry
