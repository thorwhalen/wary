"""Example of querying test results.

This example shows how to query and analyze historical
test results from the ledger.
"""

from wary import ResultsLedger
from datetime import datetime, timedelta

# Create ledger instance
ledger = ResultsLedger()

# Query all results for a specific upstream package
print("All results for 'dol':")
dol_results = ledger.query_results(upstream_package="dol")
print(f"Found {len(dol_results)} test results\n")

# Query only failures
print("Failed tests:")
failures = ledger.query_results(status="fail")
for result in failures:
    print(f"  - {result['downstream_package']}")
    print(f"    Version: {result['upstream_package']}@{result['upstream_version']}")
    print(f"    Date: {result['started_at']}")
    print()

# Query recent results (last 7 days)
week_ago = datetime.now() - timedelta(days=7)
recent_results = ledger.query_results(after=week_ago)
print(f"Results from last 7 days: {len(recent_results)}")

# Get latest result for a specific package pair
latest = ledger.get_latest_result(
    upstream_package="dol", downstream_package="my-package"
)

if latest:
    print(f"\nLatest test result for dol → my-package:")
    print(f"  Status: {latest['status']}")
    print(f"  Version: {latest['upstream_version']}")
    print(f"  Date: {latest['started_at']}")
else:
    print("\nNo test results found for this package pair")

# Calculate statistics
all_results = list(ledger.query_results())
if all_results:
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "pass")
    failed = sum(1 for r in all_results if r["status"] == "fail")

    print(f"\nOverall statistics:")
    print(f"  Total tests: {total}")
    print(f"  Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"  Failed: {failed} ({failed/total*100:.1f}%)")
