"""Wary - Dependency Monitoring and Testing Tool.

Monitor Python package dependencies, detect version changes, automatically
trigger tests in dependent packages, and maintain a ledger of test results.

Phases:
- Phase 1: Core functionality (CLI, local storage)
- Phase 2: CI Integration (GitHub Actions)
- Phase 3: Community Tool (API + Web UI)
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

# Optional imports for Phase 3 (API/UI)
try:
    from wary.api import create_app as create_api_app
    from wary.ui import create_ui_app
    from wary.server import create_combined_app, run_server
    __all__.extend(["create_api_app", "create_ui_app", "create_combined_app", "run_server"])
except ImportError:
    # Flask not installed, API/UI not available
    pass

# Optional imports for PostgreSQL storage
try:
    from wary.stores import PostgresDependencyGraph, PostgresResultsLedger
    __all__.extend(["PostgresDependencyGraph", "PostgresResultsLedger"])
except ImportError:
    # psycopg2 not installed
    pass
