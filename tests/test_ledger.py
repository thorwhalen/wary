"""Tests for wary.ledger module."""

import tempfile
from datetime import datetime
import pytest

from wary import ResultsLedger
from wary.base import TestResult


def create_test_result(test_id="test-123", status="pass"):
    """Helper to create a test result."""
    return TestResult(
        test_id=test_id,
        upstream_package="dol",
        upstream_version="0.2.51",
        downstream_package="my-package",
        downstream_version="1.0.0",
        test_command="pytest",
        commit_hash="abc123",
        status=status,
        started_at=datetime.now(),
        finished_at=datetime.now(),
        output="All tests passed",
        exit_code=0,
        environment={"python_version": "3.10"},
    )


def test_add_and_retrieve_result():
    """Test adding and retrieving a test result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = ResultsLedger(store_path=tmpdir)

        result = create_test_result()
        ledger.add_result(result)

        # Retrieve it
        retrieved = ledger[result["test_id"]]
        assert retrieved["test_id"] == result["test_id"]
        assert retrieved["status"] == "pass"


def test_query_results_by_upstream():
    """Test querying results by upstream package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = ResultsLedger(store_path=tmpdir)

        result1 = create_test_result("test-1")
        result2 = create_test_result("test-2")

        ledger.add_result(result1)
        ledger.add_result(result2)

        results = ledger.query_results(upstream_package="dol")
        assert len(results) == 2


def test_query_results_by_status():
    """Test querying results by status."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = ResultsLedger(store_path=tmpdir)

        pass_result = create_test_result("test-pass", status="pass")
        fail_result = create_test_result("test-fail", status="fail")

        ledger.add_result(pass_result)
        ledger.add_result(fail_result)

        pass_results = ledger.query_results(status="pass")
        assert len(pass_results) == 1
        assert pass_results[0]["status"] == "pass"

        fail_results = ledger.query_results(status="fail")
        assert len(fail_results) == 1
        assert fail_results[0]["status"] == "fail"


def test_get_latest_result():
    """Test getting the latest result for a package pair."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = ResultsLedger(store_path=tmpdir)

        result1 = create_test_result("test-1")
        result2 = create_test_result("test-2")

        ledger.add_result(result1)
        ledger.add_result(result2)

        latest = ledger.get_latest_result(
            upstream_package="dol", downstream_package="my-package"
        )
        assert latest is not None
        # Should be one of the results
        assert latest["test_id"] in ["test-1", "test-2"]


def test_ledger_persistence():
    """Test that ledger data persists across instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create first instance and add data
        ledger1 = ResultsLedger(store_path=tmpdir)
        result = create_test_result()
        ledger1.add_result(result)

        # Create second instance and verify data persists
        ledger2 = ResultsLedger(store_path=tmpdir)
        retrieved = ledger2[result["test_id"]]
        assert retrieved["test_id"] == result["test_id"]
