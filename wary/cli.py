"""Command-line interface for wary."""

import click
from wary.graph import DependencyGraph, build_graph_from_librariesio
from wary.watcher import VersionWatcher
from wary.orchestrator import TestOrchestrator
from wary.ledger import ResultsLedger


@click.group()
def cli():
    """Dependency Watch - Monitor package dependencies and test breakage."""
    pass


@cli.command()
@click.argument("upstream")
@click.argument("downstream")
@click.option("--test-cmd", default="pytest", help="Test command to run")
@click.option("--constraint", default="", help="Version constraint")
@click.option("--contact", default="", help="Contact email")
def register(upstream, downstream, test_cmd, constraint, contact):
    """Register a dependent package."""
    graph = DependencyGraph()
    graph.register_dependent(
        upstream=upstream,
        downstream=downstream,
        constraint=constraint,
        test_command=test_cmd,
        contact=contact,
    )
    click.echo(f"✓ Registered {downstream} as dependent of {upstream}")


@cli.command()
@click.argument("package")
def list_dependents(package):
    """List all registered dependents of a package."""
    graph = DependencyGraph()
    dependents = graph.get_dependents(package)

    if not dependents:
        click.echo(f"No dependents registered for {package}")
        return

    click.echo(f"Dependents of {package}:")
    for edge in dependents:
        click.echo(f"  - {edge['downstream']}")
        click.echo(f"    Constraint: {edge['constraint']}")
        click.echo(f"    Test command: {edge['metadata'].get('test_command', 'N/A')}")


@cli.command()
@click.argument("upstream")
@click.argument("version")
def test(upstream, version):
    """Test all dependents of a package at a specific version."""
    graph = DependencyGraph()
    orchestrator = TestOrchestrator()

    click.echo(f"Testing dependents of {upstream}@{version}...")
    results = orchestrator.test_all_dependents(upstream, version, graph)

    click.echo("\nResults:")
    for result in results:
        status_color = "green" if result["status"] == "pass" else "red"
        click.secho(f"  {result['downstream']}: {result['status']}", fg=status_color)


@cli.command()
@click.argument("packages", nargs=-1)
@click.option("--interval", default=300, help="Check interval in seconds")
def watch(packages, interval):
    """Watch packages for new versions and test dependents."""
    if not packages:
        click.echo("No packages specified")
        return

    watcher = VersionWatcher()
    graph = DependencyGraph()
    orchestrator = TestOrchestrator()

    def on_update(package, old_ver, new_ver):
        click.echo(f"\n🔔 {package}: {old_ver} → {new_ver}")
        click.echo("Testing dependents...")
        orchestrator.test_all_dependents(package, new_ver, graph)

    watcher.watch_continuously(
        packages=list(packages), callback=on_update, interval=interval
    )


@cli.command()
@click.argument("package")
@click.option(
    "--api-key", envvar="LIBRARIES_IO_API_KEY", help="Libraries.io API key"
)
@click.option("--depth", default=1, help="Graph depth")
def fetch_graph(package, api_key, depth):
    """Fetch dependency graph from Libraries.io."""
    if not api_key:
        click.echo("Error: LIBRARIES_IO_API_KEY not set")
        return

    click.echo(f"Fetching graph for {package} (depth={depth})...")
    graph = build_graph_from_librariesio(package, api_key, depth)

    edges = graph.get_all_edges()
    click.echo(f"✓ Fetched {len(edges)} dependency edges")


@cli.command()
@click.option("--upstream", help="Filter by upstream package")
@click.option("--downstream", help="Filter by downstream package")
@click.option("--status", help="Filter by status")
def results(upstream, downstream, status):
    """Query test results."""
    ledger = ResultsLedger()
    results = ledger.query_results(
        upstream_package=upstream, downstream_package=downstream, status=status
    )

    if not results:
        click.echo("No results found")
        return

    click.echo(f"Found {len(results)} results:\n")
    for result in results:
        click.echo(f"Test: {result['test_id']}")
        click.echo(f"  {result['upstream_package']}@{result['upstream_version']}")
        click.echo(f"  → {result['downstream_package']}")
        click.echo(f"  Status: {result['status']}")
        click.echo(f"  Started: {result['started_at']}")
        click.echo()


@cli.command()
@click.argument("test_id")
def show_result(test_id):
    """Show detailed test result."""
    ledger = ResultsLedger()

    try:
        result = ledger[test_id]
    except KeyError:
        click.echo(f"Test result not found: {test_id}")
        return

    click.echo(f"Test ID: {result['test_id']}")
    click.echo(f"Upstream: {result['upstream_package']}@{result['upstream_version']}")
    click.echo(f"Downstream: {result['downstream_package']}@{result['downstream_version']}")
    click.echo(f"Status: {result['status']}")
    click.echo(f"Test command: {result['test_command']}")
    click.echo(f"Started: {result['started_at']}")
    click.echo(f"Finished: {result['finished_at']}")
    click.echo(f"Exit code: {result['exit_code']}")
    click.echo(f"\nOutput:\n{result['output']}")


@cli.command()
@click.argument("package")
def check_version(package):
    """Check the latest version of a package on PyPI."""
    watcher = VersionWatcher()

    latest = watcher.get_latest_version(package)
    stored = watcher.get_stored_version(package)

    click.echo(f"Package: {package}")
    click.echo(f"Latest version: {latest}")
    click.echo(f"Stored version: {stored}")

    if stored and latest and stored != latest:
        click.echo(f"Update available: {stored} → {latest}")


if __name__ == "__main__":
    cli()
