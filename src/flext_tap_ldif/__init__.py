"""FLEXT Tap LDIF - Singer Tap for LDIF file format data extraction."""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "FLEXT Team"
__email__ = "team@flext.sh"

from flext_tap_ldif.tap import TapLDIF

__all__ = [
    "TapLDIF",
    "__version__",
]
