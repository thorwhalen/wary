# Dependency Watch Development Plan

## Executive Summary

**Project Name**: `wary`

**Goal**: Build a tool to monitor Python package dependencies, detect version changes, automatically trigger tests in dependent packages, maintain a ledger of test results, and provide notifications about breaking changes.

**Key Innovation**: Unlike existing tools that focus on "downstream" monitoring (watching your dependencies), this tool enables "upstream" monitoring (knowing who depends on you and testing them when you make changes).

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Dependency Watch System                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Graph       │  │  Version     │  │  Test        │      │
│  │  Builder     │──│  Watcher     │──│  Orchestrator│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │               │
│         └─────────────────┼──────────────────┘               │
│                           │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Results     │  │  Risk        │  │  Notification│      │
│  │  Ledger      │  │  Scorer      │  │  System      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │               │
│  ┌──────────────────────────────────────────────────┐      │
│  │           Data Layer (dol-based stores)           │      │
│  └──────────────────────────────────────────────────┘      │
│         │                                                     │
│  ┌──────────────────────────────────────────────────┐      │
│  │      HTTP API (qh) + UI Dashboard (uf)            │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Local/Personal Use

### 1.1 Project Setup

**Package Structure**:
```
wary/
├── wary/
│   ├── __init__.py
│   ├── base.py              # Core abstractions
│   ├── graph.py             # Dependency graph
│   ├── watcher.py           # Version monitoring
│   ├── orchestrator.py      # Test execution
│   ├── ledger.py            # Results storage
│   ├── scorer.py            # Risk scoring
│   ├── notifier.py          # Notifications
│   ├── api.py               # HTTP API (qh)
│   ├── ui.py                # Web UI (uf)
│   ├── util.py              # Helpers
│   └── data/                # Default data storage
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```

**Dependencies**:
```toml
[project]
dependencies = [
    "dol>=0.2.51",        # Data access patterns
    "i2>=0.1.30",         # Utilities
    "qh>=0.0.12",         # HTTP interfaces
    "uf",                 # UI framework
    "requests>=2.31.0",   # HTTP requests
    "pyyaml>=6.0",        # Config files
    "click>=8.1.0",       # CLI
    "packaging>=23.0",    # Version parsing
    "appdirs>=1.4.4",     # Standard directories
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
```

### 1.2 Core Data Structures

**Using `dol` patterns for all storage**:

```python
# wary/base.py
from typing import Protocol, TypedDict, Literal
from datetime import datetime

class PackageVersion(TypedDict):
    """Represents a package at a specific version."""
    name: str
    version: str
    released_at: datetime
    source: Literal['pypi', 'github', 'manual']

class DependencyEdge(TypedDict):
    """An edge in the dependency graph."""
    upstream: str      # Package name
    downstream: str    # Package name that depends on upstream
    constraint: str    # Version constraint (e.g., ">=1.0.0")
    registered_at: datetime
    risk_score: float  # 0.0 to 1.0
    metadata: dict     # Extra info (contact, test commands, etc.)

class TestResult(TypedDict):
    """Result of running tests for a dependent package."""
    test_id: str
    upstream_package: str
    upstream_version: str
    downstream_package: str
    downstream_version: str
    test_command: str
    commit_hash: str
    status: Literal['pass', 'fail', 'skip', 'error']
    started_at: datetime
    finished_at: datetime
    output: str
    exit_code: int
    environment: dict  # Python version, OS, etc.
```

### 1.3 Dependency Graph Builder

**Using `dol.Mapping` interface**:

```python
# wary/graph.py
from typing import Iterator
from collections.abc import MutableMapping
from dol import wrap_kvs, kv_wrap
import json
from pathlib import Path

class DependencyGraph(MutableMapping):
    """
    Store dependency edges with upstream package as key.
    
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
        self._store = Files(self.store_path, mode='t')
    
    def _default_store_path(self) -> Path:
        import appdirs
        return Path(appdirs.user_data_dir("wary")) / "graphs"
    
    def __getitem__(self, upstream_pkg: str) -> list[DependencyEdge]:
        """Get all edges for an upstream package."""
        try:
            data = json.loads(self._store[f"{upstream_pkg}.json"])
            return data
        except KeyError:
            return []
    
    def __setitem__(self, upstream_pkg: str, edges: list[DependencyEdge]):
        """Set edges for an upstream package."""
        self._store[f"{upstream_pkg}.json"] = json.dumps(edges, default=str)
    
    def __delitem__(self, upstream_pkg: str):
        del self._store[f"{upstream_pkg}.json"]
    
    def __iter__(self) -> Iterator[str]:
        for key in self._store:
            yield key.replace('.json', '')
    
    def __len__(self) -> int:
        return len(list(self._store))
    
    def register_dependent(
        self,
        upstream: str,
        downstream: str,
        constraint: str = "",
        test_command: str = "pytest",
        contact: str = "",
        **metadata
    ):
        """Register a new dependent package."""
        from datetime import datetime
        
        edges = self[upstream]
        
        # Update if exists, else append
        edge_dict = {
            'upstream': upstream,
            'downstream': downstream,
            'constraint': constraint,
            'registered_at': datetime.now(),
            'risk_score': 0.5,  # Default, will be updated
            'metadata': {
                'test_command': test_command,
                'contact': contact,
                **metadata
            }
        }
        
        # Remove existing edge if present
        edges = [e for e in edges if e['downstream'] != downstream]
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
```

**Building graphs from PyPI/Libraries.io**:

```python
# wary/graph.py (continued)

def build_graph_from_librariesio(
    package_name: str,
    api_key: str,
    depth: int = 1
) -> DependencyGraph:
    """
    Build dependency graph using Libraries.io API.
    
    Docs: https://libraries.io/api
    """
    import requests
    
    graph = DependencyGraph()
    
    def fetch_dependents(pkg: str, current_depth: int):
        if current_depth > depth:
            return
        
        url = f"https://libraries.io/api/pypi/{pkg}/dependents"
        params = {'api_key': api_key, 'per_page': 100}
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return
        
        dependents = response.json()
        for dep in dependents:
            downstream_name = dep.get('name')
            constraint = dep.get('requirements', '')
            
            graph.register_dependent(
                upstream=pkg,
                downstream=downstream_name,
                constraint=constraint,
                source='librariesio'
            )
            
            # Recurse
            if current_depth < depth:
                fetch_dependents(downstream_name, current_depth + 1)
    
    fetch_dependents(package_name, 0)
    return graph


def build_graph_from_pipdeptree(
    packages: list[str] = None
) -> DependencyGraph:
    """
    Build local dependency graph using pipdeptree.
    
    This gives you dependencies of installed packages,
    but we need to invert it for reverse dependencies.
    """
    import subprocess
    import json
    
    result = subprocess.run(
        ['pipdeptree', '--json-tree'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError("pipdeptree failed")
    
    tree = json.loads(result.stdout)
    graph = DependencyGraph()
    
    # Invert: each package's dependencies become edges
    for pkg_info in tree:
        downstream = pkg_info['package']['key']
        
        for dep in pkg_info.get('dependencies', []):
            upstream = dep['key']
            constraint = dep.get('required_version', '')
            
            graph.register_dependent(
                upstream=upstream,
                downstream=downstream,
                constraint=constraint,
                source='local'
            )
    
    return graph
```

### 1.4 Version Watcher

**Monitor PyPI for new releases**:

```python
# wary/watcher.py
from typing import Callable, Optional
from datetime import datetime
import time
import requests
from dol import Files
import json

class VersionWatcher:
    """
    Watch packages for new releases.
    
    Stores last-seen versions using dol.
    """
    
    def __init__(self, store_path: str = None):
        if store_path is None:
            import appdirs
            from pathlib import Path
            store_path = Path(appdirs.user_data_dir("wary")) / "versions"
        
        from dol import Files
        self._store = Files(store_path, mode='t')
    
    def get_latest_version(self, package: str) -> Optional[str]:
        """Fetch latest version from PyPI."""
        url = f"https://pypi.org/pypi/{package}/json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['info']['version']
        except Exception as e:
            print(f"Error fetching {package}: {e}")
            return None
    
    def get_stored_version(self, package: str) -> Optional[str]:
        """Get last-seen version from storage."""
        try:
            data = json.loads(self._store[f"{package}.json"])
            return data['version']
        except KeyError:
            return None
    
    def update_stored_version(self, package: str, version: str):
        """Store version."""
        data = {
            'version': version,
            'checked_at': datetime.now().isoformat()
        }
        self._store[f"{package}.json"] = json.dumps(data)
    
    def check_for_updates(
        self,
        packages: list[str],
        callback: Callable[[str, str, str], None] = None
    ) -> dict[str, tuple[str, str]]:
        """
        Check packages for updates.
        
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
        interval: int = 300  # 5 minutes
    ):
        """
        Continuously poll for updates.
        
        Use for local daemon mode.
        """
        print(f"Watching {len(packages)} packages every {interval}s...")
        
        while True:
            self.check_for_updates(packages, callback)
            time.sleep(interval)
```

### 1.5 Test Orchestrator

**Run tests locally when versions change**:

```python
# wary/orchestrator.py
import subprocess
import tempfile
import venv
from pathlib import Path
from datetime import datetime
import uuid

class TestOrchestrator:
    """
    Orchestrate test runs for dependent packages.
    
    Creates isolated virtual environments, installs packages,
    runs tests, captures results.
    """
    
    def __init__(self, results_ledger=None):
        self.results_ledger = results_ledger or ResultsLedger()
    
    def run_test(
        self,
        upstream_package: str,
        upstream_version: str,
        downstream_package: str,
        test_command: str = "pytest",
        python_version: str = "python3",
        timeout: int = 600
    ) -> TestResult:
        """
        Run tests for a dependent package.
        
        Steps:
        1. Create temporary venv
        2. Install upstream package at specified version
        3. Install/clone downstream package
        4. Run test command
        5. Capture results
        6. Cleanup
        """
        test_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            venv_path = tmpdir / "venv"
            
            # Create venv
            print(f"Creating venv at {venv_path}")
            venv.create(venv_path, with_pip=True)
            
            pip = venv_path / "bin" / "pip"
            python = venv_path / "bin" / "python"
            
            # Install upstream at specific version
            print(f"Installing {upstream_package}=={upstream_version}")
            install_result = subprocess.run(
                [str(pip), "install", f"{upstream_package}=={upstream_version}"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if install_result.returncode != 0:
                return self._create_error_result(
                    test_id, upstream_package, upstream_version,
                    downstream_package, started_at,
                    f"Failed to install {upstream_package}: {install_result.stderr}"
                )
            
            # Install downstream package
            print(f"Installing {downstream_package}")
            downstream_install = subprocess.run(
                [str(pip), "install", downstream_package],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if downstream_install.returncode != 0:
                return self._create_error_result(
                    test_id, upstream_package, upstream_version,
                    downstream_package, started_at,
                    f"Failed to install {downstream_package}: {downstream_install.stderr}"
                )
            
            # Get downstream version
            version_check = subprocess.run(
                [str(pip), "show", downstream_package],
                capture_output=True,
                text=True
            )
            downstream_version = "unknown"
            for line in version_check.stdout.split('\n'):
                if line.startswith('Version:'):
                    downstream_version = line.split(':', 1)[1].strip()
            
            # Get commit hash (if git repo)
            commit_hash = "unknown"
            
            # Run tests
            print(f"Running: {test_command}")
            test_result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir
            )
            
            finished_at = datetime.now()
            
            status = 'pass' if test_result.returncode == 0 else 'fail'
            
            result = TestResult(
                test_id=test_id,
                upstream_package=upstream_package,
                upstream_version=upstream_version,
                downstream_package=downstream_package,
                downstream_version=downstream_version,
                test_command=test_command,
                commit_hash=commit_hash,
                status=status,
                started_at=started_at,
                finished_at=finished_at,
                output=test_result.stdout + "\n" + test_result.stderr,
                exit_code=test_result.returncode,
                environment={
                    'python_version': python_version
                }
            )
            
            # Store in ledger
            self.results_ledger.add_result(result)
            
            return result
    
    def _create_error_result(
        self, test_id, upstream_package, upstream_version,
        downstream_package, started_at, error_msg
    ) -> TestResult:
        """Helper to create error result."""
        return TestResult(
            test_id=test_id,
            upstream_package=upstream_package,
            upstream_version=upstream_version,
            downstream_package=downstream_package,
            downstream_version="unknown",
            test_command="",
            commit_hash="unknown",
            status='error',
            started_at=started_at,
            finished_at=datetime.now(),
            output=error_msg,
            exit_code=-1,
            environment={}
        )
    
    def test_all_dependents(
        self,
        upstream_package: str,
        upstream_version: str,
        graph: DependencyGraph
    ) -> list[TestResult]:
        """
        Test all registered dependents of a package.
        """
        dependents = graph.get_dependents(upstream_package)
        results = []
        
        for edge in dependents:
            downstream = edge['downstream']
            test_cmd = edge['metadata'].get('test_command', 'pytest')
            
            print(f"\nTesting {downstream}...")
            result = self.run_test(
                upstream_package=upstream_package,
                upstream_version=upstream_version,
                downstream_package=downstream,
                test_command=test_cmd
            )
            results.append(result)
            
            print(f"Result: {result['status']}")
        
        return results
```

### 1.6 Results Ledger

**Store test results using `dol`**:

```python
# wary/ledger.py
from collections.abc import MutableMapping
from datetime import datetime
from pathlib import Path
import json
from dol import Files

class ResultsLedger(MutableMapping):
    """
    Store test results with test_id as key.
    
    Uses dol for storage abstraction.
    """
    
    def __init__(self, store_path: str = None):
        if store_path is None:
            import appdirs
            store_path = Path(appdirs.user_data_dir("wary")) / "results"
        
        self._store = Files(store_path, mode='t')
    
    def __getitem__(self, test_id: str) -> TestResult:
        return json.loads(self._store[f"{test_id}.json"])
    
    def __setitem__(self, test_id: str, result: TestResult):
        self._store[f"{test_id}.json"] = json.dumps(result, default=str)
    
    def __delitem__(self, test_id: str):
        del self._store[f"{test_id}.json"]
    
    def __iter__(self):
        for key in self._store:
            yield key.replace('.json', '')
    
    def __len__(self):
        return len(list(self._store))
    
    def add_result(self, result: TestResult):
        """Add a test result."""
        self[result['test_id']] = result
    
    def query_results(
        self,
        upstream_package: str = None,
        downstream_package: str = None,
        status: str = None,
        after: datetime = None
    ) -> list[TestResult]:
        """Query results with filters."""
        results = []
        
        for test_id in self:
            result = self[test_id]
            
            if upstream_package and result['upstream_package'] != upstream_package:
                continue
            if downstream_package and result['downstream_package'] != downstream_package:
                continue
            if status and result['status'] != status:
                continue
            if after:
                result_time = datetime.fromisoformat(result['started_at'])
                if result_time < after:
                    continue
            
            results.append(result)
        
        return results
    
    def get_latest_result(
        self,
        upstream_package: str,
        downstream_package: str
    ) -> TestResult | None:
        """Get most recent result for package pair."""
        results = self.query_results(
            upstream_package=upstream_package,
            downstream_package=downstream_package
        )
        
        if not results:
            return None
        
        # Sort by started_at descending
        results.sort(
            key=lambda r: datetime.fromisoformat(r['started_at']),
            reverse=True
        )
        
        return results[0]
```

### 1.7 CLI Interface

**Using `click` for local usage**:

```python
# wary/cli.py
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
@click.argument('upstream')
@click.argument('downstream')
@click.option('--test-cmd', default='pytest', help='Test command to run')
@click.option('--constraint', default='', help='Version constraint')
@click.option('--contact', default='', help='Contact email')
def register(upstream, downstream, test_cmd, constraint, contact):
    """Register a dependent package."""
    graph = DependencyGraph()
    graph.register_dependent(
        upstream=upstream,
        downstream=downstream,
        constraint=constraint,
        test_command=test_cmd,
        contact=contact
    )
    click.echo(f"✓ Registered {downstream} as dependent of {upstream}")

@cli.command()
@click.argument('package')
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
@click.argument('upstream')
@click.argument('version')
def test(upstream, version):
    """Test all dependents of a package at a specific version."""
    graph = DependencyGraph()
    orchestrator = TestOrchestrator()
    
    click.echo(f"Testing dependents of {upstream}@{version}...")
    results = orchestrator.test_all_dependents(upstream, version, graph)
    
    click.echo("\nResults:")
    for result in results:
        status_color = 'green' if result['status'] == 'pass' else 'red'
        click.secho(
            f"  {result['downstream']}: {result['status']}",
            fg=status_color
        )

@cli.command()
@click.argument('packages', nargs=-1)
@click.option('--interval', default=300, help='Check interval in seconds')
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
        packages=list(packages),
        callback=on_update,
        interval=interval
    )

@cli.command()
@click.argument('package')
@click.option('--api-key', envvar='LIBRARIES_IO_API_KEY', help='Libraries.io API key')
@click.option('--depth', default=1, help='Graph depth')
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
@click.option('--upstream', help='Filter by upstream package')
@click.option('--downstream', help='Filter by downstream package')
@click.option('--status', help='Filter by status')
def results(upstream, downstream, status):
    """Query test results."""
    ledger = ResultsLedger()
    results = ledger.query_results(
        upstream_package=upstream,
        downstream_package=downstream,
        status=status
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

if __name__ == '__main__':
    cli()
```

**Add to `pyproject.toml`**:
```toml
[project.scripts]
wary = "wary.cli:cli"
```

### 1.8 Usage Examples (Phase 1)

**Basic workflow**:

```bash
# Install
pip install wary

# Register your package as dependent
wary register dol my-package --test-cmd "pytest tests/" --contact "me@example.com"

# List dependents of a package
wary list-dependents dol

# Test all dependents when you release a new version
wary test dol 0.2.52

# Watch for updates and auto-test
wary watch dol i2 qh --interval 300

# View results
wary results --upstream dol --status fail

# Fetch dependency graph from Libraries.io
export LIBRARIES_IO_API_KEY="your-key"
wary fetch-graph dol --depth 2
```

**Python API**:

```python
from wary import DependencyGraph, TestOrchestrator, VersionWatcher

# Register dependent
graph = DependencyGraph()
graph.register_dependent(
    upstream='dol',
    downstream='my-package',
    test_command='pytest',
    contact='me@example.com'
)

# Test dependents
orchestrator = TestOrchestrator()
results = orchestrator.test_all_dependents('dol', '0.2.52', graph)

for result in results:
    print(f"{result['downstream']}: {result['status']}")

# Watch for updates
watcher = VersionWatcher()

def on_update(pkg, old, new):
    print(f"New version: {pkg} {old} → {new}")
    orchestrator.test_all_dependents(pkg, new, graph)

watcher.watch_continuously(['dol', 'i2'], on_update, interval=300)
```

---

## Phase 2: CI Integration (GitHub Actions)

### 2.1 GitHub Action Structure

Create reusable GitHub Actions for the tool:

```
.github/
└── actions/
    ├── wary-register/
    │   ├── action.yml
    │   └── register.py
    ├── wary-test/
    │   ├── action.yml
    │   └── test.py
    └── wary-notify/
        ├── action.yml
        └── notify.py
```

### 2.2 Register Dependent Action

```yaml
# .github/actions/wary-register/action.yml
name: 'wary Register Dependent'
description: 'Register this package as a dependent of upstream packages'

inputs:
  upstream-packages:
    description: 'Comma-separated list of upstream packages'
    required: true
  test-command:
    description: 'Command to run tests'
    required: false
    default: 'pytest'
  wary-api-url:
    description: 'wary API URL (for shared service)'
    required: false
  wary-api-key:
    description: 'API key for wary service'
    required: false

runs:
  using: 'composite'
  steps:
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install wary
      shell: bash
      run: pip install wary
    
    - name: Register dependents
      shell: bash
      env:
        UPSTREAM: ${{ inputs.upstream-packages }}
        TEST_CMD: ${{ inputs.test-command }}
        API_URL: ${{ inputs.wary-api-url }}
        API_KEY: ${{ inputs.wary-api-key }}
        REPO_NAME: ${{ github.repository }}
        REPO_URL: ${{ github.server_url }}/${{ github.repository }}
      run: |
        python ${{ github.action_path }}/register.py
```

```python
# .github/actions/wary-register/register.py
import os
import sys

def main():
    upstream_packages = os.environ['UPSTREAM'].split(',')
    test_command = os.environ['TEST_CMD']
    repo_name = os.environ['REPO_NAME']
    repo_url = os.environ['REPO_URL']
    api_url = os.environ.get('API_URL')
    api_key = os.environ.get('API_KEY')
    
    if api_url:
        # Register via API (Phase 3)
        import requests
        for upstream in upstream_packages:
            response = requests.post(
                f"{api_url}/api/dependents",
                json={
                    'upstream': upstream.strip(),
                    'downstream': repo_name,
                    'test_command': test_command,
                    'repo_url': repo_url
                },
                headers={'Authorization': f'Bearer {api_key}'}
            )
            print(f"Registered {repo_name} → {upstream}: {response.status_code}")
    else:
        # Register locally (Phase 1/2)
        from wary import DependencyGraph
        graph = DependencyGraph()
        
        for upstream in upstream_packages:
            graph.register_dependent(
                upstream=upstream.strip(),
                downstream=repo_name,
                test_command=test_command,
                repo_url=repo_url
            )
            print(f"✓ Registered {repo_name} as dependent of {upstream}")

if __name__ == '__main__':
    main()
```

### 2.3 Test Dependents Action

```yaml
# .github/actions/wary-test/action.yml
name: 'wary Test Dependents'
description: 'Test registered dependents after package release'

inputs:
  package-name:
    description: 'Package name (auto-detected from repo if not provided)'
    required: false
  package-version:
    description: 'Package version to test (auto-detected from tag if not provided)'
    required: false
  wary-api-url:
    description: 'wary API URL (for shared service)'
    required: false
  wary-api-key:
    description: 'API key for wary service'
    required: false
  max-parallel:
    description: 'Maximum number of parallel tests'
    required: false
    default: '3'

runs:
  using: 'composite'
  steps:
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install wary
      shell: bash
      run: pip install wary
    
    - name: Test dependents
      shell: bash
      env:
        PKG_NAME: ${{ inputs.package-name }}
        PKG_VERSION: ${{ inputs.package-version }}
        API_URL: ${{ inputs.wary-api-url }}
        API_KEY: ${{ inputs.wary-api-key }}
        MAX_PARALLEL: ${{ inputs.max-parallel }}
        GITHUB_REF: ${{ github.ref }}
        GITHUB_REPO: ${{ github.repository }}
      run: |
        python ${{ github.action_path }}/test.py
```

```python
# .github/actions/wary-test/test.py
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def main():
    package_name = os.environ.get('PKG_NAME')
    package_version = os.environ.get('PKG_VERSION')
    api_url = os.environ.get('API_URL')
    api_key = os.environ.get('API_KEY')
    max_parallel = int(os.environ.get('MAX_PARALLEL', '3'))
    
    # Auto-detect package name from repo
    if not package_name:
        repo = os.environ['GITHUB_REPO']
        package_name = repo.split('/')[-1].replace('-', '_')
    
    # Auto-detect version from git tag
    if not package_version:
        ref = os.environ['GITHUB_REF']
        if ref.startswith('refs/tags/v'):
            package_version = ref.replace('refs/tags/v', '')
        elif ref.startswith('refs/tags/'):
            package_version = ref.replace('refs/tags/', '')
        else:
            print("Could not auto-detect version from ref:", ref)
            sys.exit(1)
    
    print(f"Testing dependents of {package_name}@{package_version}")
    
    if api_url:
        # Trigger via API (Phase 3)
        import requests
        response = requests.post(
            f"{api_url}/api/test",
            json={
                'upstream': package_name,
                'version': package_version
            },
            headers={'Authorization': f'Bearer {api_key}'}
        )
        print(f"Triggered tests via API: {response.status_code}")
        print(response.json())
    else:
        # Run locally
        from wary import DependencyGraph, TestOrchestrator
        
        graph = DependencyGraph()
        orchestrator = TestOrchestrator()
        
        dependents = graph.get_dependents(package_name)
        print(f"Found {len(dependents)} dependents")
        
        if not dependents:
            print("No dependents to test")
            return
        
        # Test in parallel
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = []
            for edge in dependents:
                downstream = edge['downstream']
                test_cmd = edge['metadata'].get('test_command', 'pytest')
                
                future = executor.submit(
                    orchestrator.run_test,
                    upstream_package=package_name,
                    upstream_version=package_version,
                    downstream_package=downstream,
                    test_command=test_cmd
                )
                futures.append((downstream, future))
            
            results = []
            for downstream, future in futures:
                try:
                    result = future.result(timeout=600)
                    results.append(result)
                    status_emoji = '✓' if result['status'] == 'pass' else '✗'
                    print(f"{status_emoji} {downstream}: {result['status']}")
                except Exception as e:
                    print(f"✗ {downstream}: ERROR - {e}")
        
        # Summary
        passed = sum(1 for r in results if r['status'] == 'pass')
        failed = sum(1 for r in results if r['status'] == 'fail')
        
        print(f"\nSummary: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n⚠️  Some dependents failed. Consider notifying maintainers.")
            # Could exit with error code to fail the workflow
            # sys.exit(1)

if __name__ == '__main__':
    main()
```

### 2.4 Notify Action

```yaml
# .github/actions/wary-notify/action.yml
name: 'wary Notify'
description: 'Send notifications about test failures'

inputs:
  upstream-package:
    description: 'Upstream package name'
    required: true
  upstream-version:
    description: 'Upstream version'
    required: true
  notification-method:
    description: 'Notification method: github-issue, email, webhook'
    required: false
    default: 'github-issue'
  github-token:
    description: 'GitHub token for creating issues'
    required: false
  webhook-url:
    description: 'Webhook URL for notifications'
    required: false

runs:
  using: 'composite'
  steps:
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install wary
      shell: bash
      run: pip install wary requests
    
    - name: Send notifications
      shell: bash
      env:
        UPSTREAM: ${{ inputs.upstream-package }}
        VERSION: ${{ inputs.upstream-version }}
        METHOD: ${{ inputs.notification-method }}
        GITHUB_TOKEN: ${{ inputs.github-token }}
        WEBHOOK_URL: ${{ inputs.webhook-url }}
      run: |
        python ${{ github.action_path }}/notify.py
```

```python
# .github/actions/wary-notify/notify.py
import os
import requests
from wary import ResultsLedger

def main():
    upstream = os.environ['UPSTREAM']
    version = os.environ['VERSION']
    method = os.environ['METHOD']
    
    ledger = ResultsLedger()
    
    # Get recent failures
    failures = ledger.query_results(
        upstream_package=upstream,
        status='fail'
    )
    
    # Filter to this version
    failures = [
        r for r in failures
        if r['upstream_version'] == version
    ]
    
    if not failures:
        print("No failures to notify")
        return
    
    print(f"Found {len(failures)} failures for {upstream}@{version}")
    
    if method == 'github-issue':
        create_github_issues(upstream, version, failures)
    elif method == 'webhook':
        send_webhook(upstream, version, failures)
    elif method == 'email':
        send_emails(upstream, version, failures)

def create_github_issues(upstream, version, failures):
    """Create GitHub issues for failures."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("GITHUB_TOKEN not set")
        return
    
    for failure in failures:
        downstream = failure['downstream_package']
        
        # Extract owner/repo from downstream if it's a GitHub repo
        # (would need to be stored in metadata)
        # For now, skip if we don't have repo info
        
        print(f"Would create issue for {downstream}")

def send_webhook(upstream, version, failures):
    """Send webhook notification."""
    url = os.environ.get('WEBHOOK_URL')
    if not url:
        print("WEBHOOK_URL not set")
        return
    
    data = {
        'upstream': upstream,
        'version': version,
        'failures': [
            {
                'downstream': f['downstream_package'],
                'test_id': f['test_id'],
                'output': f['output'][:500]  # Truncate
            }
            for f in failures
        ]
    }
    
    response = requests.post(url, json=data)
    print(f"Webhook sent: {response.status_code}")

def send_emails(upstream, version, failures):
    """Send email notifications."""
    # Would need email credentials
    print("Email notifications not yet implemented")

if __name__ == '__main__':
    main()
```

### 2.5 Example Workflow Integration

**For dependent packages** (register on push):

```yaml
# .github/workflows/wary-register.yml
name: Register as Dependent

on:
  push:
    branches: [main]

jobs:
  register:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Register with wary
        uses: ./.github/actions/wary-register
        with:
          upstream-packages: 'dol,i2,qh'
          test-command: 'pytest tests/'
```

**For upstream packages** (test dependents after release):

```yaml
# .github/workflows/wary-test.yml
name: Test Dependents

on:
  release:
    types: [published]

jobs:
  test-dependents:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test all dependents
        uses: ./.github/actions/wary-test
        with:
          package-name: 'dol'
          package-version: ${{ github.event.release.tag_name }}
      
      - name: Notify on failures
        if: failure()
        uses: ./.github/actions/wary-notify
        with:
          upstream-package: 'dol'
          upstream-version: ${{ github.event.release.tag_name }}
          notification-method: 'github-issue'
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Phase 3: Community Tool / Shared Service

### 3.1 HTTP API using `qh`

**Create REST API**:

```python
# wary/api.py
from qh import APIClient, APISpec, APIResource
from wary import DependencyGraph, TestOrchestrator, ResultsLedger, VersionWatcher

# Define API spec
spec = APISpec(
    title="wary API",
    version="1.0.0",
    description="Dependency monitoring and testing service"
)

# Shared instances
graph = DependencyGraph()
orchestrator = TestOrchestrator()
ledger = ResultsLedger()
watcher = VersionWatcher()

# Define resources
class DependentsResource(APIResource):
    """Manage dependency registrations."""
    
    def get(self, upstream: str):
        """Get dependents of a package."""
        dependents = graph.get_dependents(upstream)
        return {'dependents': dependents}
    
    def post(self):
        """Register a new dependent."""
        data = self.get_json()
        upstream = data['upstream']
        downstream = data['downstream']
        
        graph.register_dependent(
            upstream=upstream,
            downstream=downstream,
            constraint=data.get('constraint', ''),
            test_command=data.get('test_command', 'pytest'),
            contact=data.get('contact', ''),
            repo_url=data.get('repo_url', '')
        )
        
        return {'status': 'registered'}, 201

class TestResource(APIResource):
    """Trigger tests for dependents."""
    
    def post(self):
        """Test all dependents of a package at a version."""
        data = self.get_json()
        upstream = data['upstream']
        version = data['version']
        
        # Trigger tests (could be async)
        results = orchestrator.test_all_dependents(upstream, version, graph)
        
        return {
            'status': 'completed',
            'results': [
                {
                    'downstream': r['downstream_package'],
                    'status': r['status'],
                    'test_id': r['test_id']
                }
                for r in results
            ]
        }

class ResultsResource(APIResource):
    """Query test results."""
    
    def get(self):
        """Get test results with optional filters."""
        upstream = self.get_query_param('upstream')
        downstream = self.get_query_param('downstream')
        status = self.get_query_param('status')
        
        results = ledger.query_results(
            upstream_package=upstream,
            downstream_package=downstream,
            status=status
        )
        
        return {'results': results}

class WatchResource(APIResource):
    """Manage version watching."""
    
    def post(self):
        """Add a package to watch list."""
        data = self.get_json()
        package = data['package']
        
        # Store in watch list (would need persistent storage)
        return {'status': 'watching', 'package': package}

# Register resources
spec.add_resource('/api/dependents', DependentsResource)
spec.add_resource('/api/dependents/<string:upstream>', DependentsResource)
spec.add_resource('/api/test', TestResource)
spec.add_resource('/api/results', ResultsResource)
spec.add_resource('/api/watch', WatchResource)

# Create app
def create_app():
    """Create Flask app from qh spec."""
    from qh import create_flask_app
    app = create_flask_app(spec)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

**Note**: Check actual `qh` API - the above uses assumed interface. Refer to:
- https://github.com/i2mint/qh
- `qh` documentation for exact patterns

### 3.2 Web UI using `uf`

**Create dashboard**:

```python
# wary/ui.py
from uf import App, Page, Component, Input, Button, Table, Chart
from wary import DependencyGraph, ResultsLedger

# Create app
app = App(title="wary Dashboard")

# Home page
@app.page("/", title="Home")
def home():
    """Main dashboard page."""
    graph = DependencyGraph()
    ledger = ResultsLedger()
    
    # Get stats
    total_edges = len(graph.get_all_edges())
    total_results = len(list(ledger))
    
    recent_failures = ledger.query_results(status='fail')[-10:]
    
    return Page([
        Component.heading("wary Dashboard", level=1),
        Component.stats([
            {'label': 'Registered Dependencies', 'value': total_edges},
            {'label': 'Total Tests', 'value': total_results},
            {'label': 'Recent Failures', 'value': len(recent_failures)}
        ]),
        Component.heading("Recent Failures", level=2),
        Table(
            columns=['Upstream', 'Downstream', 'Status', 'Date'],
            rows=[
                [
                    r['upstream_package'],
                    r['downstream_package'],
                    r['status'],
                    r['started_at']
                ]
                for r in recent_failures
            ]
        )
    ])

# Package details page
@app.page("/package/<package_name>", title="Package Details")
def package_details(package_name):
    """Details for a specific package."""
    graph = DependencyGraph()
    ledger = ResultsLedger()
    
    dependents = graph.get_dependents(package_name)
    results = ledger.query_results(upstream_package=package_name)
    
    # Calculate pass rate
    if results:
        pass_count = sum(1 for r in results if r['status'] == 'pass')
        pass_rate = (pass_count / len(results)) * 100
    else:
        pass_rate = 0
    
    return Page([
        Component.heading(f"Package: {package_name}", level=1),
        Component.stats([
            {'label': 'Dependents', 'value': len(dependents)},
            {'label': 'Total Tests', 'value': len(results)},
            {'label': 'Pass Rate', 'value': f"{pass_rate:.1f}%"}
        ]),
        Component.heading("Dependents", level=2),
        Table(
            columns=['Package', 'Constraint', 'Test Command'],
            rows=[
                [
                    d['downstream'],
                    d['constraint'],
                    d['metadata'].get('test_command', 'N/A')
                ]
                for d in dependents
            ]
        ),
        Component.heading("Test History", level=2),
        Chart(
            type='line',
            data={
                'labels': [r['started_at'] for r in results[-20:]],
                'datasets': [{
                    'label': 'Pass/Fail',
                    'data': [1 if r['status'] == 'pass' else 0 for r in results[-20:]]
                }]
            }
        )
    ])

# Registration page
@app.page("/register", title="Register Dependent")
def register():
    """Form to register a new dependent."""
    
    def handle_submit(form_data):
        graph = DependencyGraph()
        graph.register_dependent(
            upstream=form_data['upstream'],
            downstream=form_data['downstream'],
            constraint=form_data.get('constraint', ''),
            test_command=form_data.get('test_command', 'pytest'),
            contact=form_data.get('contact', '')
        )
        return {"success": True, "message": "Registered successfully"}
    
    return Page([
        Component.heading("Register Dependent Package", level=1),
        Component.form([
            Input(name='upstream', label='Upstream Package', required=True),
            Input(name='downstream', label='Your Package', required=True),
            Input(name='constraint', label='Version Constraint'),
            Input(name='test_command', label='Test Command', default='pytest'),
            Input(name='contact', label='Contact Email'),
            Button(label='Register', on_click=handle_submit)
        ])
    ])

if __name__ == '__main__':
    app.run(port=8000)
```

**Note**: Check actual `uf` API - the above uses assumed interface. Refer to:
- https://github.com/i2mint/uf
- The provided `uf_py.md` file
- `uf` examples

### 3.3 Deployment

**Deploy as shared service**:

```python
# wary/server.py
from wary.api import create_app
from wary.ui import app as ui_app

# Combine API and UI
api_app = create_app()

# Mount UI at / and API at /api
from werkzeug.middleware.dispatcher import DispatcherMiddleware

application = DispatcherMiddleware(ui_app, {
    '/api': api_app
})

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 8000, application, use_reloader=True)
```

**Docker deployment**:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install .

COPY wary/ ./wary/

EXPOSE 8000

CMD ["python", "-m", "wary.server"]
```

**Docker Compose with PostgreSQL**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=postgresql://wary:password@db:5432/wary
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=wary
      - POSTGRES_USER=wary
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3.4 Shared Storage with PostgreSQL

**Upgrade storage to use PostgreSQL** (still via `dol`):

```python
# wary/stores.py
from dol import wrap_kvs, kv_wrap
import psycopg2
import json

class PostgresDependencyGraph:
    """
    Dependency graph backed by PostgreSQL.
    
    Still uses dol patterns but with SQL backend.
    """
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self._create_tables()
    
    def _create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dependency_edges (
                    id SERIAL PRIMARY KEY,
                    upstream VARCHAR(255) NOT NULL,
                    downstream VARCHAR(255) NOT NULL,
                    constraint_spec VARCHAR(255),
                    registered_at TIMESTAMP,
                    risk_score FLOAT,
                    metadata JSONB,
                    UNIQUE(upstream, downstream)
                )
            """)
            self.conn.commit()
    
    def register_dependent(self, upstream, downstream, **kwargs):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO dependency_edges 
                (upstream, downstream, constraint_spec, registered_at, risk_score, metadata)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                ON CONFLICT (upstream, downstream) 
                DO UPDATE SET
                    constraint_spec = EXCLUDED.constraint_spec,
                    metadata = EXCLUDED.metadata
            """, (
                upstream,
                downstream,
                kwargs.get('constraint', ''),
                kwargs.get('risk_score', 0.5),
                json.dumps(kwargs.get('metadata', {}))
            ))
            self.conn.commit()
    
    def get_dependents(self, upstream: str):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT downstream, constraint_spec, risk_score, metadata
                FROM dependency_edges
                WHERE upstream = %s
            """, (upstream,))
            
            return [
                {
                    'upstream': upstream,
                    'downstream': row[0],
                    'constraint': row[1],
                    'risk_score': row[2],
                    'metadata': row[3]
                }
                for row in cur.fetchall()
            ]

# Similar for ResultsLedger
class PostgresResultsLedger:
    """Test results backed by PostgreSQL."""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self._create_tables()
    
    def _create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    test_id VARCHAR(36) PRIMARY KEY,
                    upstream_package VARCHAR(255),
                    upstream_version VARCHAR(100),
                    downstream_package VARCHAR(255),
                    downstream_version VARCHAR(100),
                    test_command TEXT,
                    commit_hash VARCHAR(40),
                    status VARCHAR(20),
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    output TEXT,
                    exit_code INTEGER,
                    environment JSONB
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_upstream 
                ON test_results(upstream_package)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_downstream 
                ON test_results(downstream_package)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON test_results(status)
            """)
            self.conn.commit()
```

### 3.5 Public Registry and Discovery

**Enable public registration**:

```python
# wary/registry.py
from wary.stores import PostgresDependencyGraph, PostgresResultsLedger
import os

# Shared public instances
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/wary')

public_graph = PostgresDependencyGraph(DATABASE_URL)
public_ledger = PostgresResultsLedger(DATABASE_URL)

def register_public_dependent(upstream, downstream, **kwargs):
    """
    Register on public registry.
    
    Anyone can register their package as dependent.
    """
    public_graph.register_dependent(upstream, downstream, **kwargs)

def get_public_dependents(upstream):
    """Get all publicly registered dependents."""
    return public_graph.get_dependents(upstream)

def query_public_results(**filters):
    """Query public test results."""
    return public_ledger.query_results(**filters)
```

**Discovery API**:

```python
# Add to wary/api.py
class DiscoveryResource(APIResource):
    """Discover packages in the registry."""
    
    def get(self):
        """Search for packages."""
        query = self.get_query_param('q', '')
        
        # Search in graph
        from wary.registry import public_graph
        
        # Get all edges
        all_edges = public_graph.get_all_edges()
        
        # Filter by query
        if query:
            edges = [
                e for e in all_edges
                if query.lower() in e['upstream'].lower()
                or query.lower() in e['downstream'].lower()
            ]
        else:
            edges = all_edges
        
        # Group by upstream
        packages = {}
        for edge in edges:
            upstream = edge['upstream']
            if upstream not in packages:
                packages[upstream] = {
                    'name': upstream,
                    'dependents': []
                }
            packages[upstream]['dependents'].append(edge['downstream'])
        
        return {'packages': list(packages.values())}

spec.add_resource('/api/discover', DiscoveryResource)
```

---

## References and Resources

### Python Packages to Use

1. **dol** - Data Object Layer
   - Repo: https://github.com/i2mint/dol
   - Use for: Storage abstractions, Mapping interfaces
   - Key patterns: `Files`, `MutableMapping`, `wrap_kvs`

2. **i2** - i2mint utilities
   - Repo: https://github.com/i2mint/i2
   - Use for: Signature manipulation, decorators, utilities

3. **qh** - Quick HTTP interfaces
   - Repo: https://github.com/i2mint/qh
   - Docs: Check repo README
   - Use for: REST API creation

4. **uf** - UI Fast
   - Repo: https://github.com/i2mint/uf
   - Docs: See provided `uf_py.md`
   - Use for: Web dashboard creation

### External APIs

1. **Libraries.io API**
   - Docs: https://libraries.io/api
   - Endpoints:
     - `/api/pypi/{package}/dependents` - Get dependents
     - `/api/pypi/{package}/dependencies` - Get dependencies
   - Requires API key (free tier available)

2. **PyPI JSON API**
   - Endpoint: `https://pypi.org/pypi/{package}/json`
   - No authentication required
   - Rate limits apply

3. **GitHub API**
   - Docs: https://docs.github.com/en/rest
   - Use for: Repository info, issue creation, webhooks
   - Requires personal access token

### Tools and Libraries

1. **pipdeptree** - Local dependency trees
   - Install: `pip install pipdeptree`
   - Docs: https://github.com/tox-dev/pipdeptree

2. **packaging** - Version parsing
   - Part of Python packaging tools
   - Docs: https://packaging.python.org/

3. **GitPython** - Git operations
   - Install: `pip install GitPython`
   - Docs: https://gitpython.readthedocs.io/

4. **click** - CLI framework
   - Docs: https://click.palletsprojects.com/

5. **psycopg2** - PostgreSQL adapter
   - Install: `pip install psycopg2-binary`
   - Docs: https://www.psycopg.org/

### GitHub Actions

1. **Actions Documentation**
   - https://docs.github.com/en/actions
   - Creating actions: https://docs.github.com/en/actions/creating-actions

2. **Reusable Workflows**
   - https://docs.github.com/en/actions/using-workflows/reusing-workflows

3. **Matrix Strategy**
   - For parallel testing across versions
   - https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs

### Testing and CI

1. **pytest** - Testing framework
   - Docs: https://docs.pytest.org/

2. **tox** - Testing automation
   - Docs: https://tox.wiki/

3. **nox** - Flexible test automation
   - Docs: https://nox.thea.codes/

### Deployment

1. **Docker**
   - Docs: https://docs.docker.com/
   - Python images: https://hub.docker.com/_/python

2. **Fly.io** - Simple deployment
   - Docs: https://fly.io/docs/

3. **Railway** - Alternative deployment
   - Docs: https://docs.railway.app/

4. **Heroku** - Traditional PaaS
   - Docs: https://devcenter.heroku.com/categories/python-support

---

## Development Roadmap

### Phase 1: Local Tool (Weeks 1-3)

**Week 1: Core Data Structures**
- [ ] Set up project structure
- [ ] Implement `DependencyGraph` with dol
- [ ] Implement `ResultsLedger` with dol
- [ ] Write tests
- [ ] Add examples

**Week 2: Monitoring and Testing**
- [ ] Implement `VersionWatcher`
- [ ] Implement `TestOrchestrator`
- [ ] Integration with Libraries.io API
- [ ] Integration with PyPI API
- [ ] Write tests

**Week 3: CLI and Polish**
- [ ] Implement CLI with click
- [ ] Add configuration file support
- [ ] Write documentation
- [ ] Create examples
- [ ] Publish to PyPI

### Phase 2: CI Integration (Weeks 4-6)

**Week 4: GitHub Actions**
- [ ] Create `wary-register` action
- [ ] Create `wary-test` action
- [ ] Create `wary-notify` action
- [ ] Write action documentation
- [ ] Test in real repositories

**Week 5: Integration Testing**
- [ ] Test with multiple Python versions
- [ ] Test parallel execution
- [ ] Test failure scenarios
- [ ] Optimize performance
- [ ] Add retry logic

**Week 6: Documentation and Examples**
- [ ] Write integration guide
- [ ] Create example repositories
- [ ] Document best practices
- [ ] Create troubleshooting guide

### Phase 3: Community Tool (Weeks 7-10)

**Week 7: Backend Service**
- [ ] Create HTTP API with qh
- [ ] Set up PostgreSQL storage
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Write API tests

**Week 8: Web UI**
- [ ] Create dashboard with uf
- [ ] Implement package pages
- [ ] Add registration form
- [ ] Create results visualization
- [ ] Add search/discovery

**Week 9: Deployment**
- [ ] Create Docker setup
- [ ] Set up database migrations
- [ ] Configure monitoring
- [ ] Deploy to production
- [ ] Set up backups

**Week 10: Launch**
- [ ] Write user documentation
- [ ] Create tutorial videos
- [ ] Announce to community
- [ ] Gather feedback
- [ ] Plan next features

---

## Advanced Features (Future)

### Risk Scoring

Use ML to predict breakage probability:

```python
# wary/scorer.py
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class RiskScorer:
    """
    Predict breakage risk based on historical data.
    """
    
    def __init__(self):
        self.model = RandomForestClassifier()
        self.trained = False
    
    def extract_features(self, edge: DependencyEdge, history: list[TestResult]):
        """
        Extract features for prediction:
        - Historical pass rate
        - Version delta magnitude
        - Test complexity
        - Package popularity
        """
        if not history:
            return np.array([0.5] * 10)
        
        pass_count = sum(1 for r in history if r['status'] == 'pass')
        pass_rate = pass_count / len(history)
        
        # More features...
        features = [
            pass_rate,
            len(history),
            # ...
        ]
        
        return np.array(features)
    
    def train(self, training_data):
        """Train model on historical data."""
        X = []
        y = []
        
        for edge, history in training_data:
            features = self.extract_features(edge, history)
            # Label: 1 if most recent test failed, 0 otherwise
            label = 1 if history[-1]['status'] == 'fail' else 0
            
            X.append(features)
            y.append(label)
        
        self.model.fit(X, y)
        self.trained = True
    
    def predict_risk(self, edge: DependencyEdge, history: list[TestResult]) -> float:
        """Predict breakage probability (0-1)."""
        if not self.trained:
            return 0.5  # Default
        
        features = self.extract_features(edge, history)
        prob = self.model.predict_proba([features])[0][1]
        return float(prob)
```

### Webhooks

Receive PyPI webhooks for immediate notifications:

```python
# wary/webhooks.py
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/pypi', methods=['POST'])
def pypi_webhook():
    """
    Receive PyPI webhook for new releases.
    
    Configure at: https://pypi.org/manage/account/
    """
    # Verify signature
    signature = request.headers.get('X-PyPI-Signature')
    secret = os.environ['PYPI_WEBHOOK_SECRET']
    
    payload = request.get_data()
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected:
        return {'error': 'Invalid signature'}, 401
    
    data = request.json
    package = data['name']
    version = data['version']
    
    # Trigger tests
    from wary import DependencyGraph, TestOrchestrator
    graph = DependencyGraph()
    orchestrator = TestOrchestrator()
    
    orchestrator.test_all_dependents(package, version, graph)
    
    return {'status': 'triggered'}, 200
```

### Advanced Notifications

Integrate with Slack, Discord, email:

```python
# wary/notifier.py
import requests

class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def notify_failure(self, result: TestResult):
        message = {
            'text': f"⚠️ Test failure",
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': (
                            f"*{result['downstream_package']}* failed tests "
                            f"with *{result['upstream_package']}@{result['upstream_version']}*"
                        )
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"```{result['output'][:500]}```"
                    }
                }
            ]
        }
        
        requests.post(self.webhook_url, json=message)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_graph.py
import pytest
from wary import DependencyGraph

def test_register_dependent():
    graph = DependencyGraph(store_path='/tmp/test_graph')
    
    graph.register_dependent(
        upstream='dol',
        downstream='my-package',
        test_command='pytest'
    )
    
    dependents = graph.get_dependents('dol')
    assert len(dependents) == 1
    assert dependents[0]['downstream'] == 'my-package'

def test_get_dependents_empty():
    graph = DependencyGraph(store_path='/tmp/test_graph2')
    assert graph.get_dependents('nonexistent') == []
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from wary import (
    DependencyGraph,
    VersionWatcher,
    TestOrchestrator,
    ResultsLedger
)

@pytest.mark.integration
def test_full_workflow():
    """Test complete workflow from registration to testing."""
    # Register
    graph = DependencyGraph(store_path='/tmp/test_integration')
    graph.register_dependent(
        upstream='requests',
        downstream='my-package',
        test_command='echo "test passed"'
    )
    
    # Watch
    watcher = VersionWatcher(store_path='/tmp/test_versions')
    latest = watcher.get_latest_version('requests')
    assert latest is not None
    
    # Test
    orchestrator = TestOrchestrator()
    results = orchestrator.test_all_dependents('requests', latest, graph)
    
    assert len(results) == 1
    assert results[0]['status'] == 'pass'
    
    # Query results
    ledger = ResultsLedger(store_path='/tmp/test_results')
    queried = ledger.query_results(upstream_package='requests')
    assert len(queried) >= 1
```

### CI Tests

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e .[dev,test]
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=wary --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Security Considerations

1. **API Authentication**
   - Use API keys for public service
   - Rate limiting per user
   - HTTPS only

2. **Test Isolation**
   - Run tests in containers
   - Resource limits (CPU, memory, time)
   - Network restrictions

3. **Data Privacy**
   - Allow private registrations
   - Configurable result visibility
   - Data retention policies

4. **Code Injection**
   - Validate test commands
   - Sandbox execution
   - Audit logs

---

## Conclusion

This development plan provides a comprehensive roadmap for building `wary` in three phases:

1. **Phase 1**: Personal/local tool for monitoring dependencies
2. **Phase 2**: CI integration via GitHub Actions
3. **Phase 3**: Community service with shared registry

The architecture leverages:
- **dol** for storage abstractions
- **qh** for HTTP APIs
- **uf** for web UI
- **i2** for utilities
- Standard Python libraries for core functionality

The tool fills a gap in the Python ecosystem by enabling **upstream dependency monitoring** - knowing who depends on your package and automatically testing them when you make changes.

Start with Phase 1 for immediate personal value, then expand to CI integration and community use as needed.