"""Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from flext_core import FlextTypes

"""FLEXT Tap LDIF - Enterprise Singer Tap for LDIF Data Extraction."""
"""
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


import importlib.metadata

# flext-core imports
from flext_core import FlextLogger, FlextModels, FlextResult

# === FLEXT-MELTANO COMPLETE INTEGRATION ===
# Re-export ALL flext-meltano facilities for full ecosystem integration
from flext_meltano import (
    BatchSink,
    # Bridge integration
    FlextMeltanoBridge,
    # Configuration and validation
    FlextMeltanoConfig,
    # Enterprise services
    FlextMeltanoTapService,
    # Authentication patterns
    OAuthAuthenticator,
    # Typing definitions
    PropertiesList,
    Property,
    Sink,
    SQLSink,
    # Core Singer SDK classes (centralized from flext-meltano)
    Stream,
    Tap,
    Target,
    # Testing utilities
    get_tap_test_class,
    # Singer typing utilities (centralized)
    singer_typing,
)

# Legacy imports for backward compatibility - maintain ALL existing imports
from flext_tap_ldif.config import TapLDIFConfig, TapLDIFConfig as LegacyTapLDIFConfig
from flext_tap_ldif.exceptions import (
    FlextTapLdifConfigurationError,
    FlextTapLdifError,
    FlextTapLdifFileError,
    FlextTapLdifParseError,
    FlextTapLdifProcessingError,
    FlextTapLdifStreamError,
    FlextTapLdifValidationError,
)
from flext_tap_ldif.ldif_processor import (
    FlextLDIFProcessor,
    FlextLDIFProcessorWrapper,
    LDIFProcessor,
)
from flext_tap_ldif.streams import LDIFEntriesStream

# === PEP8 REORGANIZATION: Import from new structure ===
from flext_tap_ldif.tap import TapLDIF, TapLDIF as LegacyTapLDIF

# Enterprise-grade aliases for backward compatibility
FlextTapLDIF = TapLDIF
FlextTapLDIFConfig = TapLDIFConfig
LDIFTap = TapLDIF
TapConfig = TapLDIFConfig

# Version following semantic versioning
try:
    __version__ = importlib.metadata.version("flext-tap-ldif")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0-enterprise"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Complete public API exports
__all__: FlextTypes.Core.StringList = [
    "BatchSink",
    # Legacy processor classes
    "FlextLDIFProcessor",
    "FlextLDIFProcessorWrapper",
    "FlextLogger",
    # Bridge integration
    "FlextMeltanoBridge",
    # Configuration patterns
    "FlextMeltanoConfig",
    # Enterprise services
    "FlextMeltanoTapService",
    "FlextModels",
    # === FLEXT-CORE RE-EXPORTS ===
    "FlextResult",
    # === BACKWARD COMPATIBILITY ===
    "FlextTapLDIF",
    "FlextTapLDIFConfig",
    # Legacy exception classes
    "FlextTapLdifConfigurationError",
    "FlextTapLdifError",
    "FlextTapLdifFileError",
    "FlextTapLdifParseError",
    "FlextTapLdifProcessingError",
    "FlextTapLdifStreamError",
    "FlextTapLdifValidationError",
    # Legacy stream classes
    "LDIFEntriesStream",
    "LDIFProcessor",
    "LDIFTap",
    # Legacy config classes
    "LegacyTapLDIF",
    "LegacyTapLDIFConfig",
    # Authentication
    "OAuthAuthenticator",
    "PropertiesList",
    "Property",
    "SQLSink",
    "Sink",
    # === FLEXT-MELTANO COMPLETE RE-EXPORTS ===
    # Singer SDK core classes
    "Stream",
    "Tap",
    "TapConfig",
    # === PRIMARY TAP CLASSES ===
    "TapLDIF",
    "TapLDIFConfig",
    "Target",
    # === METADATA ===
    "__version__",
    "__version_info__",
    # Testing
    "get_tap_test_class",
    # Singer typing
    "singer_typing",
]
