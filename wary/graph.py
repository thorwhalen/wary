"""Dependency graph management for wary."""

from typing import Iterator
from collections.abc import MutableMapping
from pathlib import Path
import json
from datetime import datetime

from wary.base import DependencyEdge


class DependencyGraph(MutableMapping):
    """Store dependency edges with upstream package as key.

    Uses dol for storage abstraction - can back with JSON files,
    SQLite, or remote storage.

    Key: upstream_package_name (str)
    Value: List of DependencyEdge dicts
    """

    def __init__(self, store_path: str = None):
        if store_path is None:
            store_path = self._default_store_path()
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

        # Use dol to wrap filesystem as dict
        from dol import Files

        self._store = Files(str(self.store_path))

    def _default_store_path(self) -> Path:
        import appdirs

        return Path(appdirs.user_data_dir("wary")) / "graphs"

    def __getitem__(self, upstream_pkg: str) -> list[DependencyEdge]:
        """Get all edges for an upstream package."""
        try:
            # Files stores bytes, so decode
            data_bytes = self._store[f"{upstream_pkg}.json"]
            data = json.loads(data_bytes.decode('utf-8'))
            return data
        except KeyError:
            return []

    def __setitem__(self, upstream_pkg: str, edges: list[DependencyEdge]):
        """Set edges for an upstream package."""
        # Files stores bytes, so encode
        data_str = json.dumps(edges, default=str)
        self._store[f"{upstream_pkg}.json"] = data_str.encode('utf-8')

    def __delitem__(self, upstream_pkg: str):
        del self._store[f"{upstream_pkg}.json"]

    def __iter__(self) -> Iterator[str]:
        for key in self._store:
            yield key.replace(".json", "")

    def __len__(self) -> int:
        return len(list(self._store))

    def register_dependent(
        self,
        upstream: str,
        downstream: str,
        constraint: str = "",
        test_command: str = "pytest",
        contact: str = "",
        **metadata,
    ):
        """Register a new dependent package."""
        edges = self[upstream]

        # Update if exists, else append
        edge_dict = {
            "upstream": upstream,
            "downstream": downstream,
            "constraint": constraint,
            "registered_at": datetime.now(),
            "risk_score": 0.5,  # Default, will be updated
            "metadata": {"test_command": test_command, "contact": contact, **metadata},
        }

        # Remove existing edge if present
        edges = [e for e in edges if e["downstream"] != downstream]
        edges.append(edge_dict)

        self[upstream] = edges

    def get_dependents(self, upstream: str) -> list[DependencyEdge]:
        """Get all packages that depend on upstream."""
        return self[upstream]

    def get_all_edges(self) -> list[DependencyEdge]:
        """Flatten all edges."""
        all_edges = []
        for upstream in self:
            all_edges.extend(self[upstream])
        return all_edges


def build_graph_from_librariesio(
    package_name: str, api_key: str, depth: int = 1
) -> DependencyGraph:
    """Build dependency graph using Libraries.io API.

    Docs: https://libraries.io/api
    """
    import requests

    graph = DependencyGraph()

    def fetch_dependents(pkg: str, current_depth: int):
        if current_depth > depth:
            return

        url = f"https://libraries.io/api/pypi/{pkg}/dependents"
        params = {"api_key": api_key, "per_page": 100}

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return

        dependents = response.json()
        for dep in dependents:
            downstream_name = dep.get("name")
            constraint = dep.get("requirements", "")

            graph.register_dependent(
                upstream=pkg, downstream=downstream_name, constraint=constraint, source="librariesio"
            )

            # Recurse
            if current_depth < depth:
                fetch_dependents(downstream_name, current_depth + 1)

    fetch_dependents(package_name, 0)
    return graph


def build_graph_from_pipdeptree(packages: list[str] = None) -> DependencyGraph:
    """Build local dependency graph using pipdeptree.

    This gives you dependencies of installed packages,
    but we need to invert it for reverse dependencies.
    """
    import subprocess
    import json

    result = subprocess.run(
        ["pipdeptree", "--json-tree"], capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError("pipdeptree failed")

    tree = json.loads(result.stdout)
    graph = DependencyGraph()

    # Invert: each package's dependencies become edges
    for pkg_info in tree:
        downstream = pkg_info["package"]["key"]

        for dep in pkg_info.get("dependencies", []):
            upstream = dep["key"]
            constraint = dep.get("required_version", "")

            graph.register_dependent(
                upstream=upstream, downstream=downstream, constraint=constraint, source="local"
            )

    return graph
