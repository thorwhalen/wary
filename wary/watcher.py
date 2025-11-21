"""Version watching and monitoring for wary."""

from typing import Callable, Optional
from datetime import datetime
from pathlib import Path
import time
import json

import requests


class VersionWatcher:
    """Watch packages for new releases.

    Stores last-seen versions using dol.
    """

    def __init__(self, store_path: str = None):
        if store_path is None:
            import appdirs

            store_path = Path(appdirs.user_data_dir("wary")) / "versions"

        from dol import Files

        self._store = Files(str(store_path))

    def get_latest_version(self, package: str) -> Optional[str]:
        """Fetch latest version from PyPI."""
        url = f"https://pypi.org/pypi/{package}/json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["info"]["version"]
        except Exception as e:
            print(f"Error fetching {package}: {e}")
            return None

    def get_stored_version(self, package: str) -> Optional[str]:
        """Get last-seen version from storage."""
        try:
            data_bytes = self._store[f"{package}.json"]
            data = json.loads(data_bytes.decode('utf-8'))
            return data["version"]
        except KeyError:
            return None

    def update_stored_version(self, package: str, version: str):
        """Store version."""
        data = {"version": version, "checked_at": datetime.now().isoformat()}
        self._store[f"{package}.json"] = json.dumps(data).encode('utf-8')

    def check_for_updates(
        self,
        packages: list[str],
        callback: Callable[[str, str, str], None] = None,
    ) -> dict[str, tuple[str, str]]:
        """Check packages for updates.

        Returns dict of {package: (old_version, new_version)}
        for packages with updates.

        Callback is called with (package, old_ver, new_ver).
        """
        updates = {}

        for package in packages:
            stored_version = self.get_stored_version(package)
            latest_version = self.get_latest_version(package)

            if latest_version is None:
                continue

            if stored_version != latest_version:
                updates[package] = (stored_version, latest_version)
                self.update_stored_version(package, latest_version)

                if callback:
                    callback(package, stored_version, latest_version)

        return updates

    def watch_continuously(
        self,
        packages: list[str],
        callback: Callable[[str, str, str], None],
        interval: int = 300,  # 5 minutes
    ):
        """Continuously poll for updates.

        Use for local daemon mode.
        """
        print(f"Watching {len(packages)} packages every {interval}s...")

        while True:
            self.check_for_updates(packages, callback)
            time.sleep(interval)
