"""LDIF tap exception hierarchy using flext-core patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for LDIF tap operations inheriting from flext-core.
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextConfigurationError,
    FlextError,
    FlextProcessingError,
    FlextValidationError,
)


class FlextTapLdifError(FlextError):
    """Base exception for LDIF tap operations."""

    def __init__(
        self,
        message: str = "LDIF tap error",
        file_path: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap error with context."""
        context = kwargs.copy()
        if file_path is not None:
            context["file_path"] = file_path

        super().__init__(message, error_code="LDIF_TAP_ERROR", context=context)


class FlextTapLdifValidationError(FlextValidationError):
    """LDIF tap validation errors."""

    def __init__(
        self,
        message: str = "LDIF tap validation failed",
        field: str | None = None,
        value: object = None,
        line_number: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap validation error with context."""
        validation_details = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        context = kwargs.copy()
        if line_number is not None:
            context["line_number"] = line_number

        super().__init__(
            f"LDIF tap validation: {message}",
            validation_details=validation_details,
            context=context,
        )


class FlextTapLdifConfigurationError(FlextConfigurationError):
    """LDIF tap configuration errors."""

    def __init__(
        self,
        message: str = "LDIF tap configuration error",
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap configuration error with context."""
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key

        super().__init__(f"LDIF tap config: {message}", **context)


class FlextTapLdifProcessingError(FlextProcessingError):
    """LDIF tap processing errors."""

    def __init__(
        self,
        message: str = "LDIF tap processing failed",
        file_path: str | None = None,
        line_number: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap processing error with context."""
        context = kwargs.copy()
        if file_path is not None:
            context["file_path"] = file_path
        if line_number is not None:
            context["line_number"] = line_number

        super().__init__(f"LDIF tap processing: {message}", **context)


class FlextTapLdifParseError(FlextProcessingError):
    """LDIF tap parsing errors."""

    def __init__(
        self,
        message: str = "LDIF tap parsing failed",
        file_path: str | None = None,
        line_number: int | None = None,
        entry_dn: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap parse error with context."""
        context = kwargs.copy()
        if file_path is not None:
            context["file_path"] = file_path
        if line_number is not None:
            context["line_number"] = line_number
        if entry_dn is not None:
            context["entry_dn"] = entry_dn

        super().__init__(f"LDIF tap parse: {message}", **context)


class FlextTapLdifFileError(FlextTapLdifError):
    """LDIF tap file operation errors."""

    def __init__(
        self,
        message: str = "LDIF tap file error",
        file_path: str | None = None,
        operation: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap file error with context."""
        context = kwargs.copy()
        if file_path is not None:
            context["file_path"] = file_path
        if operation is not None:
            context["operation"] = operation

        super().__init__(f"LDIF tap file: {message}", **context)


class FlextTapLdifStreamError(FlextTapLdifError):
    """LDIF tap stream processing errors."""

    def __init__(
        self,
        message: str = "LDIF tap stream error",
        stream_name: str | None = None,
        file_path: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap stream error with context."""
        context = kwargs.copy()
        if stream_name is not None:
            context["stream_name"] = stream_name
        if file_path is not None:
            context["file_path"] = file_path

        super().__init__(f"LDIF tap stream: {message}", **context)


__all__ = [
    "FlextTapLdifConfigurationError",
    "FlextTapLdifError",
    "FlextTapLdifFileError",
    "FlextTapLdifParseError",
    "FlextTapLdifProcessingError",
    "FlextTapLdifStreamError",
    "FlextTapLdifValidationError",
]
