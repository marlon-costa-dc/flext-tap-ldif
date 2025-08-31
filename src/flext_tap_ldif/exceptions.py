"""LDIF tap exception hierarchy using flext-core DRY patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions using factory pattern to eliminate duplication.
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextExceptions, create_module_exception_classes
from flext_core.exceptions import FlextExceptions

type FlextExceptionType = type[FlextExceptions.Base.FlextExceptionsMixin]

# Create all standard exception classes using factory pattern - avoids heavy
# conditional imports and ensures runtime availability without TYPE_CHECKING.
ldif_exceptions = create_module_exception_classes("flext_tap_ldif")
_prefix = "FLEXT_TAP_LDIF"
_mapping = {
    "FlextTapLdifError": f"{_prefix}Error",
    "FlextTapLdifValidationError": f"{_prefix}ValidationError",
    "FlextTapLdifConfigurationError": f"{_prefix}ConfigurationError",
    "FlextTapLdifConnectionError": f"{_prefix}ConnectionError",
    "FlextTapLdifProcessingError": f"{_prefix}ProcessingError",
    "FlextTapLdifAuthenticationError": f"{_prefix}AuthenticationError",
    "FlextTapLdifTimeoutError": f"{_prefix}TimeoutError",
}

# Type cast to help MyPy understand these are class types, not variables
FlextTapLdifError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifError"]]
)
FlextTapLdifValidationError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifValidationError"]]
)
FlextTapLdifConfigurationError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifConfigurationError"]]
)
FlextTapLdifConnectionError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifConnectionError"]]
)
FlextTapLdifProcessingError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifProcessingError"]]
)
FlextTapLdifAuthenticationError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifAuthenticationError"]]
)
FlextTapLdifTimeoutError = cast(
    "FlextExceptionType", ldif_exceptions[_mapping["FlextTapLdifTimeoutError"]]
)


class FlextTapLdifParseError(FlextExceptions.ProcessingError):
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

        super().__init__(f"LDIF tap parse: {message}")
        # Store context information as instance attributes
        for key, value in context.items():
            setattr(self, key, value)


class FlextTapLdifFileError(FlextTapLdifError):  # type: ignore[valid-type,misc]
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


class FlextTapLdifStreamError(FlextTapLdifError):  # type: ignore[valid-type,misc]
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


__all__: list[str] = [
    "FlextTapLdifConfigurationError",
    "FlextTapLdifError",
    "FlextTapLdifFileError",
    "FlextTapLdifParseError",
    "FlextTapLdifProcessingError",
    "FlextTapLdifStreamError",
    "FlextTapLdifValidationError",
]
