"""Configuration for FLEXT Tap LDIF."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TapLDIFConfig(BaseModel):
    """Configuration for the LDIF tap."""

    # File Input Configuration
    file_path: str | None = Field(
        default=None,
        description="Path to the LDIF file to extract data from",
    )

    file_pattern: str | None = Field(
        default=None,
        description="Pattern for multiple LDIF files (e.g., '*.ldif')",
    )

    directory_path: str | None = Field(
        default=None,
        description="Directory containing LDIF files",
    )

    # Filtering Configuration
    base_dn_filter: str | None = Field(
        default=None,
        description="Filter entries by base DN pattern",
    )

    object_class_filter: list[str] | None = Field(
        default=None,
        description="Filter entries by object class",
    )

    attribute_filter: list[str] | None = Field(
        default=None,
        description="Include only specified attributes",
    )

    exclude_attributes: list[str] | None = Field(
        default=None,
        description="Exclude specified attributes",
    )

    # Processing Configuration
    encoding: str = Field(
        default="utf-8",
        description="File encoding (default: utf-8)",
    )

    batch_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Number of entries to process in each batch",
    )

    include_operational_attributes: bool = Field(
        default=False,
        description="Include operational attributes in output",
    )

    strict_parsing: bool = Field(
        default=True,
        description="Enable strict LDIF parsing (fail on errors)",
    )

    max_file_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum file size in MB to process",
    )

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str | None) -> str | None:
        """Validate that file_path exists if provided."""
        if v is not None:
            path = Path(v)
            if not path.exists():
                msg = f"File path does not exist: {v}"
                raise ValueError(msg)
            if not path.is_file():
                msg = f"Path is not a file: {v}"
                raise ValueError(msg)
        return v

    @field_validator("directory_path")
    @classmethod
    def validate_directory_path(cls, v: str | None) -> str | None:
        """Validate that directory_path exists if provided."""
        if v is not None:
            path = Path(v)
            if not path.exists():
                msg = f"Directory path does not exist: {v}"
                raise ValueError(msg)
            if not path.is_dir():
                msg = f"Path is not a directory: {v}"
                raise ValueError(msg)
        return v

    def model_post_init(self, __context: Any, /) -> None:
        """Validate configuration after initialization."""
        super().model_post_init(__context)

        # Ensure at least one input source is specified
        if not any([self.file_path, self.file_pattern, self.directory_path]):
            msg = "At least one input source must be specified: file_path, file_pattern, or directory_path"
            raise ValueError(msg)

    @property
    def ldif_config(self) -> dict[str, Any]:
        """Get LDIF-specific configuration as a dictionary."""
        return {
            "file_path": self.file_path,
            "file_pattern": self.file_pattern,
            "directory_path": self.directory_path,
            "base_dn_filter": self.base_dn_filter,
            "object_class_filter": self.object_class_filter,
            "attribute_filter": self.attribute_filter,
            "exclude_attributes": self.exclude_attributes,
            "encoding": self.encoding,
            "batch_size": self.batch_size,
            "include_operational_attributes": self.include_operational_attributes,
            "strict_parsing": self.strict_parsing,
            "max_file_size_mb": self.max_file_size_mb,
        }
