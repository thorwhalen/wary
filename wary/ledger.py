"""Test results ledger for wary."""

from collections.abc import MutableMapping
from datetime import datetime
from pathlib import Path
import json

from wary.base import TestResult


class ResultsLedger(MutableMapping):
    """Store test results with test_id as key.

    Uses dol for storage abstraction.
    """

    def __init__(self, store_path: str = None):
        if store_path is None:
            import appdirs

            store_path = Path(appdirs.user_data_dir("wary")) / "results"

        from dol import Files

        self._store = Files(str(store_path))

    def __getitem__(self, test_id: str) -> TestResult:
        data_bytes = self._store[f"{test_id}.json"]
        return json.loads(data_bytes.decode('utf-8'))

    def __setitem__(self, test_id: str, result: TestResult):
        self._store[f"{test_id}.json"] = json.dumps(result, default=str).encode('utf-8')

    def __delitem__(self, test_id: str):
        del self._store[f"{test_id}.json"]

    def __iter__(self):
        for key in self._store:
            yield key.replace(".json", "")

    def __len__(self):
        return len(list(self._store))

    def add_result(self, result: TestResult):
        """Add a test result."""
        self[result["test_id"]] = result

    def query_results(
        self,
        upstream_package: str = None,
        downstream_package: str = None,
        status: str = None,
        after: datetime = None,
    ) -> list[TestResult]:
        """Query results with filters."""
        results = []

        for test_id in self:
            result = self[test_id]

            if upstream_package and result["upstream_package"] != upstream_package:
                continue
            if downstream_package and result["downstream_package"] != downstream_package:
                continue
            if status and result["status"] != status:
                continue
            if after:
                result_time = datetime.fromisoformat(result["started_at"])
                if result_time < after:
                    continue

            results.append(result)

        return results

    def get_latest_result(
        self, upstream_package: str, downstream_package: str
    ) -> TestResult | None:
        """Get most recent result for package pair."""
        results = self.query_results(
            upstream_package=upstream_package, downstream_package=downstream_package
        )

        if not results:
            return None

        # Sort by started_at descending
        results.sort(
            key=lambda r: datetime.fromisoformat(r["started_at"]), reverse=True
        )

        return results[0]
