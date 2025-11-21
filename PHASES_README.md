# Wary - Multi-Phase Implementation Guide

This document describes the three phases of Wary implementation and how to use each one.

## Overview

Wary is a dependency monitoring and testing tool that helps you:
- Track which packages depend on your code
- Automatically test dependents when you release new versions
- Maintain a history of test results
- Get notified about breaking changes

## Phase 1: Local/Personal Use

**Status:** ✅ Complete

Phase 1 provides core functionality for local use via CLI and Python API.

### Installation

```bash
pip install wary
```

### CLI Usage

```bash
# Register a dependent package
wary register dol my-package --test-cmd "pytest tests/"

# List dependents
wary list-dependents dol

# Test all dependents
wary test dol 0.2.51

# Watch for updates
wary watch dol i2 qh --interval 300

# Query results
wary results --upstream dol --status fail

# Show detailed result
wary show-result <test-id>

# Check version
wary check-version dol
```

### Python API

```python
from wary import DependencyGraph, VersionWatcher, TestOrchestrator

# Register dependencies
graph = DependencyGraph()
graph.register_dependent(
    upstream='dol',
    downstream='my-package',
    test_command='pytest'
)

# Check for updates
watcher = VersionWatcher()
latest = watcher.get_latest_version('dol')

# Test dependents
orchestrator = TestOrchestrator()
results = orchestrator.test_all_dependents('dol', latest, graph)
```

### Storage

Phase 1 uses local file storage (JSON files) via `dol`:
- Graph data: `~/.local/share/wary/graphs/`
- Version data: `~/.local/share/wary/versions/`
- Test results: `~/.local/share/wary/results/`

---

## Phase 2: CI Integration (GitHub Actions)

**Status:** ✅ Complete

Phase 2 adds GitHub Actions for automatic registration and testing in CI/CD pipelines.

### GitHub Actions

Three reusable actions are provided:

#### 1. wary-register

Register your package as dependent of upstream packages.

```yaml
# .github/workflows/register.yml
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
        uses: thorwhalen/wary/.github/actions/wary-register@main
        with:
          upstream-packages: 'dol,i2,qh'
          test-command: 'pytest tests/'
```

#### 2. wary-test

Test all dependents when you release a new version.

```yaml
# .github/workflows/test-dependents.yml
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
        uses: thorwhalen/wary/.github/actions/wary-test@main
        with:
          package-name: 'dol'
          package-version: ${{ github.event.release.tag_name }}
```

#### 3. wary-notify

Send notifications about test failures.

```yaml
# .github/workflows/test-dependents.yml (continued)
      - name: Notify on failures
        if: failure()
        uses: thorwhalen/wary/.github/actions/wary-notify@main
        with:
          upstream-package: 'dol'
          upstream-version: ${{ github.event.release.tag_name }}
          notification-method: 'slack'
          slack-webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Notification Methods

- `github-issue`: Create issues in dependent repositories
- `slack`: Send Slack messages
- `webhook`: Send to custom webhook

---

## Phase 3: Community Tool / Shared Service

**Status:** ✅ Complete

Phase 3 provides a hosted service with REST API and web UI for community use.

### Installation

```bash
# Install with server dependencies
pip install wary[server]
```

### Running the Server

#### Development Mode

```bash
# Start combined API + UI server
python -m wary.server

# Or directly:
python -c "from wary.server import run_server; run_server()"
```

Server will start on http://localhost:8000:
- Web UI: http://localhost:8000/
- API: http://localhost:8000/api

#### Production Mode

```bash
# Using Docker Compose
docker-compose up -d

# Using environment variable
WARY_ENV=production python -m wary.server
```

### REST API

#### Endpoints

```bash
# Get API info
GET /api

# Get dependents
GET /api/dependents/<upstream>

# Register dependent
POST /api/dependents
{
  "upstream": "dol",
  "downstream": "my-package",
  "test_command": "pytest",
  "repo_url": "https://github.com/user/my-package"
}

# Trigger tests
POST /api/test
{
  "upstream": "dol",
  "version": "0.2.51"
}

# Query results
GET /api/results?upstream=dol&status=fail

# Get specific result
GET /api/results/<test-id>

# Get package version
GET /api/packages/<package>/version

# Get statistics
GET /api/stats
```

#### Authentication

For write operations, set API key:

```bash
# In environment
export WARY_API_KEY=your-secret-key

# In request headers
Authorization: Bearer your-secret-key
```

#### Example Usage

```python
import requests

API_URL = "http://localhost:8000/api"
API_KEY = "your-secret-key"

# Register dependent
response = requests.post(
    f"{API_URL}/dependents",
    json={
        "upstream": "dol",
        "downstream": "my-package",
        "test_command": "pytest"
    },
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# Trigger tests
response = requests.post(
    f"{API_URL}/test",
    json={"upstream": "dol", "version": "0.2.51"},
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# Query results
response = requests.get(f"{API_URL}/results?upstream=dol")
results = response.json()
```

### Web UI

The web UI provides:
- **Dashboard**: Overview with statistics and recent failures
- **Package Details**: View dependents and test history for a package
- **Test Results**: Browse and filter all test results
- **Result Details**: Detailed view of individual test runs
- **Registration Form**: Web form to register dependencies

#### Pages

- `/` - Dashboard
- `/package/<name>` - Package details
- `/results` - Test results list
- `/result/<test-id>` - Result details
- `/register` - Registration form

### PostgreSQL Storage

For production deployments, use PostgreSQL instead of file storage:

```python
from wary.stores import PostgresDependencyGraph, PostgresResultsLedger

# Configure with connection string
DATABASE_URL = "postgresql://user:password@localhost:5432/wary"

graph = PostgresDependencyGraph(DATABASE_URL)
ledger = PostgresResultsLedger(DATABASE_URL)
```

Or set environment variable:

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/wary
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Services:
# - Web: http://localhost:8000
# - PostgreSQL: localhost:5432
# - pgAdmin: http://localhost:5050
```

See `deployment/README.md` for detailed deployment instructions.

### GitHub Actions with Shared Service

Use the shared service instead of local storage:

```yaml
- name: Register with wary
  uses: thorwhalen/wary/.github/actions/wary-register@main
  with:
    upstream-packages: 'dol,i2,qh'
    test-command: 'pytest tests/'
    wary-api-url: 'https://wary.example.com'
    wary-api-key: ${{ secrets.WARY_API_KEY }}
```

---

## Architecture

### Core Components

```
┌─────────────────────────────────────────┐
│         Dependency Watch System         │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐│
│  │  Graph   │  │ Watcher  │  │ Orch. ││
│  └──────────┘  └──────────┘  └───────┘│
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │  Ledger  │  │  API/UI  │           │
│  └──────────┘  └──────────┘           │
│         │              │               │
│  ┌─────────────────────────────┐      │
│  │  Storage (Files/PostgreSQL) │      │
│  └─────────────────────────────┘      │
└─────────────────────────────────────────┘
```

### Extensions (my_qh and my_uf)

We created `my_qh.py` and `my_uf.py` modules with utilities we wish existed in qh and uf:

**my_qh.py** (API utilities):
- `json_api`: Decorator for JSON responses
- `require_auth`: Authentication decorator
- `SimpleAPI`: Flask-like API builder
- `create_flask_from_functions`: Auto-generate Flask app
- `auto_api`: Create endpoints from object methods

**my_uf.py** (UI utilities):
- `Component`: UI component abstraction
- `Page`: Full page builder
- `make_table`, `make_stats`, `make_card`: Helper functions
- HTML generation with default styling

These can be moved to qh/uf later for broader use.

---

## Migration Path

### From Phase 1 to Phase 2

No migration needed - just add GitHub Actions to your repositories.

### From Phase 1 to Phase 3

#### Using File Storage

Phase 3 can use the same file storage, so existing data is preserved.

#### Migrating to PostgreSQL

```python
from wary import DependencyGraph, ResultsLedger
from wary.stores import PostgresDependencyGraph, PostgresResultsLedger

# Load from files
file_graph = DependencyGraph()
file_ledger = ResultsLedger()

# Create PostgreSQL instances
pg_graph = PostgresDependencyGraph("postgresql://...")
pg_ledger = PostgresResultsLedger("postgresql://...")

# Migrate edges
for edge in file_graph.get_all_edges():
    pg_graph.register_dependent(
        upstream=edge['upstream'],
        downstream=edge['downstream'],
        **edge['metadata']
    )

# Migrate results
for test_id in file_ledger:
    result = file_ledger[test_id]
    pg_ledger.add_result(result)
```

---

## Roadmap

### Implemented ✅

- [x] Phase 1: Core functionality
  - [x] Dependency graph storage
  - [x] Version monitoring
  - [x] Test orchestration
  - [x] Results ledger
  - [x] CLI interface

- [x] Phase 2: CI Integration
  - [x] wary-register action
  - [x] wary-test action
  - [x] wary-notify action
  - [x] Example workflows

- [x] Phase 3: Community Tool
  - [x] REST API (Flask)
  - [x] Web UI
  - [x] PostgreSQL storage
  - [x] Docker deployment
  - [x] Combined server

### Future Enhancements

- [ ] Risk scoring with ML
- [ ] PyPI webhooks integration
- [ ] Advanced notifications (email, Discord)
- [ ] Matrix testing (multiple Python versions)
- [ ] Caching and performance optimization
- [ ] Kubernetes deployment examples
- [ ] Public hosted service

---

## Support

- Documentation: https://thorwhalen.github.io/wary
- Issues: https://github.com/thorwhalen/wary/issues
- Discussions: https://github.com/thorwhalen/wary/discussions

## License

MIT
