"""Wary - Dependency Monitoring and Testing Tool.

Monitor Python package dependencies, detect version changes, automatically
trigger tests in dependent packages, and maintain a ledger of test results.
"""

from wary.base import PackageVersion, DependencyEdge, TestResult
from wary.graph import DependencyGraph, build_graph_from_librariesio, build_graph_from_pipdeptree
from wary.watcher import VersionWatcher
from wary.orchestrator import TestOrchestrator
from wary.ledger import ResultsLedger
from wary.util import load_config, save_config, get_package_info, format_test_result

__version__ = "0.0.2"

__all__ = [
    # Core types
    "PackageVersion",
    "DependencyEdge",
    "TestResult",
    # Main classes
    "DependencyGraph",
    "VersionWatcher",
    "TestOrchestrator",
    "ResultsLedger",
    # Graph builders
    "build_graph_from_librariesio",
    "build_graph_from_pipdeptree",
    # Utilities
    "load_config",
    "save_config",
    "get_package_info",
    "format_test_result",
]
