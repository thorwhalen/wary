"""Example of watching packages for updates and auto-testing.

This example shows how to set up continuous monitoring
of upstream packages and automatically test dependents
when new versions are released.
"""

from wary import DependencyGraph, VersionWatcher, TestOrchestrator

# Set up the dependency graph
graph = DependencyGraph()

# Register dependencies
packages_to_monitor = ["dol", "i2", "qh"]

for pkg in packages_to_monitor:
    graph.register_dependent(
        upstream=pkg,
        downstream="my-package",
        test_command="pytest",
    )

# Set up watcher and orchestrator
watcher = VersionWatcher()
orchestrator = TestOrchestrator()


def on_version_update(package, old_version, new_version):
    """Callback when a package version changes."""
    print(f"\n🔔 New version detected!")
    print(f"   Package: {package}")
    print(f"   Version: {old_version} → {new_version}")
    print(f"\n   Testing dependents...")

    # Test all dependents with the new version
    results = orchestrator.test_all_dependents(package, new_version, graph)

    # Report results
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")

    print(f"\n   Results: {passed} passed, {failed} failed")


# Watch packages (checks every 5 minutes)
print(f"Watching {len(packages_to_monitor)} packages for updates...")
print("Press Ctrl+C to stop")

try:
    watcher.watch_continuously(
        packages=packages_to_monitor, callback=on_version_update, interval=300
    )
except KeyboardInterrupt:
    print("\nStopped watching")
