"""Tests for wary.graph module."""

import tempfile
from pathlib import Path
import pytest

from wary import DependencyGraph


def test_register_dependent():
    """Test registering a dependent package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = DependencyGraph(store_path=tmpdir)

        graph.register_dependent(
            upstream="dol", downstream="my-package", test_command="pytest"
        )

        dependents = graph.get_dependents("dol")
        assert len(dependents) == 1
        assert dependents[0]["downstream"] == "my-package"
        assert dependents[0]["metadata"]["test_command"] == "pytest"


def test_get_dependents_empty():
    """Test getting dependents for non-existent package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = DependencyGraph(store_path=tmpdir)
        assert graph.get_dependents("nonexistent") == []


def test_multiple_dependents():
    """Test registering multiple dependents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = DependencyGraph(store_path=tmpdir)

        graph.register_dependent(upstream="dol", downstream="package1")
        graph.register_dependent(upstream="dol", downstream="package2")
        graph.register_dependent(upstream="dol", downstream="package3")

        dependents = graph.get_dependents("dol")
        assert len(dependents) == 3


def test_update_dependent():
    """Test updating an existing dependent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = DependencyGraph(store_path=tmpdir)

        graph.register_dependent(
            upstream="dol", downstream="my-package", test_command="pytest"
        )
        graph.register_dependent(
            upstream="dol", downstream="my-package", test_command="pytest -v"
        )

        dependents = graph.get_dependents("dol")
        assert len(dependents) == 1
        assert dependents[0]["metadata"]["test_command"] == "pytest -v"


def test_get_all_edges():
    """Test getting all edges from graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = DependencyGraph(store_path=tmpdir)

        graph.register_dependent(upstream="dol", downstream="package1")
        graph.register_dependent(upstream="i2", downstream="package2")
        graph.register_dependent(upstream="qh", downstream="package3")

        edges = graph.get_all_edges()
        assert len(edges) == 3


def test_graph_persistence():
    """Test that graph data persists across instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create first instance and add data
        graph1 = DependencyGraph(store_path=tmpdir)
        graph1.register_dependent(upstream="dol", downstream="my-package")

        # Create second instance and verify data persists
        graph2 = DependencyGraph(store_path=tmpdir)
        dependents = graph2.get_dependents("dol")
        assert len(dependents) == 1
        assert dependents[0]["downstream"] == "my-package"
