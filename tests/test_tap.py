"""Tests for TapLDIF."""

from __future__ import annotations

import tempfile
from pathlib import Path

# MIGRATED: from singer_sdk.testing import get_tap_test_class -> use flext_meltano
from flext_meltano import get_tap_test_class

from flext_tap_ldif.tap import TapLDIF


def test_discover_streams() -> None:
    """Test stream discovery."""
    with tempfile.NamedTemporaryFile(suffix=".ldif", delete=False) as tmp_file:
        config = {"file_path": tmp_file.name}
        tap = TapLDIF(config=config)
        streams = tap.discover_streams()
        assert len(streams) == 1
        assert streams[0].name == "ldif_entries"
        # Clean up
        Path(tmp_file.name).unlink(missing_ok=True)


# Create test class for Singer testing framework
with tempfile.NamedTemporaryFile(suffix=".ldif", delete=False) as _tmp_file:
    TestTapLDIF = get_tap_test_class(
        tap_class=TapLDIF,
        config={
            "file_path": _tmp_file.name,  # This will be mocked in actual tests
        },
    )
    # Note: File cleanup handled by test framework
