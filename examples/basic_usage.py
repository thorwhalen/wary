"""Basic usage examples for wary.

This example demonstrates the core functionality of wary:
- Registering dependent packages
- Checking for version updates
- Testing dependents when versions change
"""

from wary import DependencyGraph, VersionWatcher, TestOrchestrator

# Create a dependency graph
graph = DependencyGraph()

# Register your package as dependent on dol
graph.register_dependent(
    upstream="dol",
    downstream="my-awesome-package",
    test_command="pytest tests/",
    contact="me@example.com",
    constraint=">=0.2.0",
)

# List all packages that depend on dol
dependents = graph.get_dependents("dol")
print(f"Found {len(dependents)} packages that depend on dol:")
for edge in dependents:
    print(f"  - {edge['downstream']}")

# Check for version updates
watcher = VersionWatcher()
latest_version = watcher.get_latest_version("dol")
print(f"\nLatest version of dol: {latest_version}")

# Test all dependents with a specific version
# (This would create virtual environments and run tests)
orchestrator = TestOrchestrator()

# Note: This will actually run tests, so use with caution
# results = orchestrator.test_all_dependents("dol", latest_version, graph)
#
# for result in results:
#     print(f"{result['downstream']}: {result['status']}")
