# Wary Examples

This directory contains examples demonstrating how to use wary.

## Examples

### `basic_usage.py`
Demonstrates the core functionality:
- Creating a dependency graph
- Registering dependent packages
- Checking for version updates
- Testing dependents

```bash
python examples/basic_usage.py
```

### `watch_and_test.py`
Shows how to set up continuous monitoring:
- Watch multiple packages for updates
- Automatically test dependents when versions change
- Report results

```bash
python examples/watch_and_test.py
```

### `query_results.py`
Demonstrates querying test results:
- Query historical test results
- Filter by package, status, date
- Calculate statistics

```bash
python examples/query_results.py
```

## CLI Examples

You can also use the CLI tool:

```bash
# Register a dependent package
wary register dol my-package --test-cmd "pytest tests/"

# List dependents of a package
wary list-dependents dol

# Check for version updates
wary check-version dol

# Test all dependents
wary test dol 0.2.51

# Watch packages for updates
wary watch dol i2 qh --interval 300

# Query test results
wary results --upstream dol --status fail

# Show detailed result
wary show-result <test-id>
```

## Configuration

You can create a `.wary.yml` file to configure default settings:

```yaml
packages:
  - dol
  - i2
  - qh

test_command: pytest tests/

contact: me@example.com

interval: 300  # Check every 5 minutes
```
