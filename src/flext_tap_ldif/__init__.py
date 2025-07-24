"""FLEXT TAP LDIF - Singer LDIF Data Extraction with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Singer LDIF Tap with simplified public API:
- All common imports available from root: from flext_tap_ldif import TapLDIF
- Built on flext-core foundation for robust LDIF integration
- Deprecation warnings for internal imports
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import warnings
from typing import Never

# Foundation patterns - ALWAYS from flext-core
# 🚨 ARCHITECTURAL COMPLIANCE: Using DI container
from flext_tap_ldif.infrastructure.di_container import get_service_result, get_domain_entity, get_field, get_domain_value_object, get_base_config
ServiceResult = get_service_result()
DomainEntity = get_domain_entity()
Field = get_field()
DomainValueObject = get_domain_value_object()
BaseConfig = get_base_config()
    BaseConfig as LDIFBaseConfig,  # Configuration base
    DomainBaseModel as BaseModel,  # Base for LDIF models
    DomainError as LDIFError,  # LDIF-specific errors
    ServiceResult,  # LDIF operation results
    ValidationError,  # Validation errors
)

try:
    __version__ = importlib.metadata.version("flext-tap-ldif")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.7.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())


class FlextTapLDIFDeprecationWarning(DeprecationWarning):
    """Custom deprecation warning for FLEXT TAP LDIF import changes."""


def _show_deprecation_warning(old_import: str, new_import: str) -> None:
    """Show deprecation warning for import paths."""
    message_parts = [
        f"⚠️  DEPRECATED IMPORT: {old_import}",
        f"✅ USE INSTEAD: {new_import}",
        "🔗 This will be removed in version 1.0.0",
        "📖 See FLEXT TAP LDIF docs for migration guide",
    ]
    warnings.warn(
        "\n".join(message_parts),
        FlextTapLDIFDeprecationWarning,
        stacklevel=3,
    )


# ================================
# SIMPLIFIED PUBLIC API EXPORTS
# ================================

# Foundation patterns - imported at top of file

# Singer Tap exports - direct import (ZERO TOLERANCE for fallbacks)
from flext_tap_ldif.tap import TapLDIF

# LDIF Client exports - simplified imports (client module doesn't exist yet)
# with contextlib.suppress(ImportError):
#     from flext_tap_ldif.client import LDIFTapClient

# LDIF Streams exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_ldif.streams import LDIFEntriesStream

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    "BaseModel",  # from flext_tap_ldif import BaseModel
    # Deprecation utilities
    "FlextTapLDIFDeprecationWarning",
    # Core Patterns (from flext-core)
    "LDIFBaseConfig",  # from flext_tap_ldif import LDIFBaseConfig
    # LDIF Streams (simplified access)
    "LDIFChangesStream",  # from flext_tap_ldif import LDIFChangesStream
    "LDIFEntriesStream",  # from flext_tap_ldif import LDIFEntriesStream
    "LDIFError",  # from flext_tap_ldif import LDIFError
    "LDIFTapClient",  # from flext_tap_ldif import LDIFTapClient
    "ServiceResult",  # from flext_tap_ldif import ServiceResult
    # Main Singer Tap (simplified access)
    "TapLDIF",  # from flext_tap_ldif import TapLDIF
    "ValidationError",  # from flext_tap_ldif import ValidationError
    # Version
    "__version__",
    "__version_info__",
]
