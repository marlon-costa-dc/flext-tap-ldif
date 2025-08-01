"""LDIF tap exception hierarchy using flext-core DRY patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions using factory pattern to eliminate duplication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.exceptions import FlextProcessingError, create_module_exception_classes

if TYPE_CHECKING:
    # For type checking, import the actual base types
    from flext_core.exceptions import (
        FlextAuthenticationError as FlextTapLdifAuthenticationError,
        FlextConfigurationError as FlextTapLdifConfigurationError,
        FlextConnectionError as FlextTapLdifConnectionError,
        FlextError as FlextTapLdifError,
        FlextProcessingError as FlextTapLdifProcessingError,
        FlextTimeoutError as FlextTapLdifTimeoutError,
        FlextValidationError as FlextTapLdifValidationError,
    )
else:
    # Create all standard exception classes using factory pattern - eliminates 120+ lines of duplication
    ldif_exceptions = create_module_exception_classes("flext_tap_ldif")

    # Import generated classes for clean usage
    FlextTapLdifError = ldif_exceptions["FlextTapLdifError"]
    FlextTapLdifValidationError = ldif_exceptions["FlextTapLdifValidationError"]
    FlextTapLdifConfigurationError = ldif_exceptions["FlextTapLdifConfigurationError"]
    FlextTapLdifConnectionError = ldif_exceptions["FlextTapLdifConnectionError"]
    FlextTapLdifProcessingError = ldif_exceptions["FlextTapLdifProcessingError"]
    FlextTapLdifAuthenticationError = ldif_exceptions["FlextTapLdifAuthenticationError"]
    FlextTapLdifTimeoutError = ldif_exceptions["FlextTapLdifTimeoutError"]


class FlextTapLdifParseError(FlextProcessingError):
    """LDIF tap parsing errors with LDIF-specific context."""

    def __init__(
        self,
        message: str = "LDIF tap parsing failed",
        file_path: str | None = None,
        line_number: int | None = None,
        entry_dn: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap parse error with LDIF-specific context."""
        context = kwargs.copy()
        if file_path is not None:
            context["file_path"] = file_path
        if line_number is not None:
            context["line_number"] = line_number
        if entry_dn is not None:
            context["entry_dn"] = entry_dn

        super().__init__(f"LDIF tap parse: {message}", **context)


class FlextTapLdifFileError(FlextTapLdifError):
    """LDIF tap file operation errors with file-specific context."""

    def __init__(
        self,
        message: str = "LDIF tap file error",
        file_path: str | None = None,
        operation: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap file error with file-specific context."""
        context = kwargs.copy()
        if file_path is not None:
            context["file_path"] = file_path
        if operation is not None:
            context["operation"] = operation

        super().__init__(f"LDIF tap file: {message}", context=context)


class FlextTapLdifStreamError(FlextTapLdifError):
    """LDIF tap stream processing errors with stream-specific context."""

    def __init__(
        self,
        message: str = "LDIF tap stream error",
        stream_name: str | None = None,
        file_path: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDIF tap stream error with stream-specific context."""
        context = kwargs.copy()
        if stream_name is not None:
            context["stream_name"] = stream_name
        if file_path is not None:
            context["file_path"] = file_path

        super().__init__(f"LDIF tap stream: {message}", context=context)


__all__ = [
    "FlextTapLdifConfigurationError",
    "FlextTapLdifError",
    "FlextTapLdifFileError",
    "FlextTapLdifParseError",
    "FlextTapLdifProcessingError",
    "FlextTapLdifStreamError",
    "FlextTapLdifValidationError",
]
