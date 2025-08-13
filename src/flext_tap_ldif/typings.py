"""Centralized typings facade for flext-tap-ldif.

- Extends flext-core types
- Add Tap LDIF-specific type aliases and Protocols here
"""

from __future__ import annotations

from flext_core.typings import E, F, FlextTypes as CoreFlextTypes, P, R, T, U, V


class FlextTypes(CoreFlextTypes):
    """Tap LDIF domain-specific types can extend here."""


__all__ = [
    "E",
    "F",
    "FlextTypes",
    "P",
    "R",
    "T",
    "U",
    "V",
]
