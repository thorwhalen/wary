"""Core data structures for wary dependency monitoring."""

from typing import TypedDict, Literal
from datetime import datetime


class PackageVersion(TypedDict):
    """Represents a package at a specific version."""

    name: str
    version: str
    released_at: datetime
    source: Literal["pypi", "github", "manual"]


class DependencyEdge(TypedDict):
    """An edge in the dependency graph."""

    upstream: str  # Package name
    downstream: str  # Package name that depends on upstream
    constraint: str  # Version constraint (e.g., ">=1.0.0")
    registered_at: datetime
    risk_score: float  # 0.0 to 1.0
    metadata: dict  # Extra info (contact, test commands, etc.)


class TestResult(TypedDict):
    """Result of running tests for a dependent package."""

    test_id: str
    upstream_package: str
    upstream_version: str
    downstream_package: str
    downstream_version: str
    test_command: str
    commit_hash: str
    status: Literal["pass", "fail", "skip", "error"]
    started_at: datetime
    finished_at: datetime
    output: str
    exit_code: int
    environment: dict  # Python version, OS, etc.
