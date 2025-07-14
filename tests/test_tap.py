"""Test the main tap functionality."""

from __future__ import annotations

import pytest
from singer_sdk.testing import get_tap_test_class

from flext_tap_ldif.tap import TapLDIF


def test_tap_ldif_creation():
    """Test creating TapLDIF instance."""
    tap = TapLDIF()
    assert tap.name == "tap-ldif"


def test_tap_ldif_config_schema():
    """Test the configuration schema."""
    tap = TapLDIF()
    assert "file_path" in tap.config_jsonschema["properties"]
    assert "directory_path" in tap.config_jsonschema["properties"]
    assert "batch_size" in tap.config_jsonschema["properties"]


def test_discover_streams():
    """Test stream discovery."""
    config = {"file_path": "/tmp/test.ldif"}
    tap = TapLDIF(config=config)
    streams = tap.discover_streams()
    assert len(streams) == 1
    assert streams[0].name == "ldif_entries"


# Create test class for Singer testing framework
TestTapLDIF = get_tap_test_class(
    tap_class=TapLDIF,
    config={
        "file_path": "/tmp/test.ldif",  # This will be mocked in actual tests
    }
)