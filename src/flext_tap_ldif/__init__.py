"""FLEXT Tap LDIF - Singer Tap for LDIF file format data extraction.

This project implements a Singer tap for extracting data from LDIF (LDAP Data
Interchange Format) files, using flext-meltano interfaces and flext-ldif for
processing logic.

Architecture:
- Uses generic Tap/Stream interfaces from flext-meltano
- Uses real LDIF processing logic from flext-ldif
- Follows flext-core patterns for error handling and logging

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import local implementations
from flext_tap_ldif.config import TapLDIFConfig
from flext_tap_ldif.tap import TapLDIF

# Backward compatibility aliases
FlextTapLDIF = TapLDIF
FlextTapLDIFConfig = TapLDIFConfig
LDIFTap = TapLDIF
TapConfig = TapLDIFConfig

__version__ = "0.9.0-wrapper"

__all__: list[str] = [
    # Backward compatibility
    "FlextTapLDIF",
    "FlextTapLDIFConfig",
    "LDIFTap",
    "TapConfig",
    "TapLDIF",
    "TapLDIFConfig",
    "__version__",
]
