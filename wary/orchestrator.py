"""Test orchestration for wary."""

import subprocess
import tempfile
import venv
from pathlib import Path
from datetime import datetime
import uuid

from wary.base import TestResult
from wary.ledger import ResultsLedger
from wary.graph import DependencyGraph


class TestOrchestrator:
    """Orchestrate test runs for dependent packages.

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
        timeout: int = 600,
    ) -> TestResult:
        """Run tests for a dependent package.

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
                timeout=timeout,
            )

            if install_result.returncode != 0:
                return self._create_error_result(
                    test_id,
                    upstream_package,
                    upstream_version,
                    downstream_package,
                    started_at,
                    f"Failed to install {upstream_package}: {install_result.stderr}",
                )

            # Install downstream package
            print(f"Installing {downstream_package}")
            downstream_install = subprocess.run(
                [str(pip), "install", downstream_package],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if downstream_install.returncode != 0:
                return self._create_error_result(
                    test_id,
                    upstream_package,
                    upstream_version,
                    downstream_package,
                    started_at,
                    f"Failed to install {downstream_package}: {downstream_install.stderr}",
                )

            # Get downstream version
            version_check = subprocess.run(
                [str(pip), "show", downstream_package], capture_output=True, text=True
            )
            downstream_version = "unknown"
            for line in version_check.stdout.split("\n"):
                if line.startswith("Version:"):
                    downstream_version = line.split(":", 1)[1].strip()

            # Get commit hash (if git repo)
            commit_hash = "unknown"

            # Run tests
            print(f"Running: {test_command}")
            test_result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
            )

            finished_at = datetime.now()

            status = "pass" if test_result.returncode == 0 else "fail"

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
                environment={"python_version": python_version},
            )

            # Store in ledger
            self.results_ledger.add_result(result)

            return result

    def _create_error_result(
        self,
        test_id,
        upstream_package,
        upstream_version,
        downstream_package,
        started_at,
        error_msg,
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
            status="error",
            started_at=started_at,
            finished_at=datetime.now(),
            output=error_msg,
            exit_code=-1,
            environment={},
        )

    def test_all_dependents(
        self, upstream_package: str, upstream_version: str, graph: DependencyGraph
    ) -> list[TestResult]:
        """Test all registered dependents of a package."""
        dependents = graph.get_dependents(upstream_package)
        results = []

        for edge in dependents:
            downstream = edge["downstream"]
            test_cmd = edge["metadata"].get("test_command", "pytest")

            print(f"\nTesting {downstream}...")
            result = self.run_test(
                upstream_package=upstream_package,
                upstream_version=upstream_version,
                downstream_package=downstream,
                test_command=test_cmd,
            )
            results.append(result)

            print(f"Result: {result['status']}")

        return results
