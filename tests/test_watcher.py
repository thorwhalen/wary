"""Tests for wary.watcher module."""

import tempfile
import pytest

from wary import VersionWatcher


def test_get_latest_version():
    """Test fetching latest version from PyPI."""
    watcher = VersionWatcher()

    # Test with a well-known package
    version = watcher.get_latest_version("requests")
    assert version is not None
    assert isinstance(version, str)
    assert len(version) > 0


def test_store_and_retrieve_version():
    """Test storing and retrieving versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        watcher = VersionWatcher(store_path=tmpdir)

        # Initially should be None
        assert watcher.get_stored_version("test-package") is None

        # Store a version
        watcher.update_stored_version("test-package", "1.0.0")

        # Should now retrieve it
        stored = watcher.get_stored_version("test-package")
        assert stored == "1.0.0"


def test_check_for_updates_no_change():
    """Test checking for updates when version hasn't changed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        watcher = VersionWatcher(store_path=tmpdir)

        # Get current version of requests
        current = watcher.get_latest_version("requests")
        watcher.update_stored_version("requests", current)

        # Check for updates - should be empty
        updates = watcher.check_for_updates(["requests"])
        assert "requests" not in updates


def test_check_for_updates_with_change():
    """Test checking for updates when version has changed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        watcher = VersionWatcher(store_path=tmpdir)

        # Store an old version
        watcher.update_stored_version("requests", "0.0.1")

        # Check for updates - should find the new version
        updates = watcher.check_for_updates(["requests"])
        assert "requests" in updates
        old_ver, new_ver = updates["requests"]
        assert old_ver == "0.0.1"
        assert new_ver is not None
