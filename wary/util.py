"""Utility functions for wary."""

from pathlib import Path
from typing import Optional
import yaml


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file.

    If config_path is None, looks for .wary.yml in current directory
    or home directory.
    """
    if config_path is None:
        # Try current directory first
        config_path = Path(".wary.yml")
        if not config_path.exists():
            # Try home directory
            config_path = Path.home() / ".wary.yml"
            if not config_path.exists():
                return {}

    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict, config_path: Optional[str] = None):
    """Save configuration to YAML file."""
    if config_path is None:
        config_path = Path(".wary.yml")

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def get_package_info(package_name: str) -> Optional[dict]:
    """Get package information from PyPI.

    Returns dict with keys: name, version, summary, home_page, etc.
    """
    import requests

    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["info"]
    except Exception as e:
        print(f"Error fetching package info for {package_name}: {e}")
        return None


def parse_version_constraint(constraint: str) -> tuple[str, str]:
    """Parse a version constraint like '>=1.0.0' into operator and version.

    Returns: (operator, version)
    """
    from packaging.specifiers import SpecifierSet

    if not constraint:
        return ("", "")

    try:
        spec = SpecifierSet(constraint)
        # Get the first specifier
        if spec:
            first = list(spec)[0]
            return (first.operator, first.version)
    except Exception:
        pass

    return ("", "")


def format_test_result(result: dict) -> str:
    """Format a test result for display."""
    status_emoji = {
        "pass": "✓",
        "fail": "✗",
        "error": "⚠",
        "skip": "○",
    }

    emoji = status_emoji.get(result["status"], "?")
    return (
        f"{emoji} {result['downstream_package']} "
        f"(tested with {result['upstream_package']}@{result['upstream_version']})\n"
        f"   Status: {result['status']}\n"
        f"   Started: {result['started_at']}\n"
        f"   Test ID: {result['test_id']}"
    )
