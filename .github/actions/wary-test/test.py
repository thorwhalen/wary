"""Test action script for GitHub Actions."""

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
            print(f"Could not auto-detect version from ref: {ref}")
            sys.exit(1)

    print(f"Testing dependents of {package_name}@{package_version}")

    if api_url:
        # Trigger via API (Phase 3)
        import requests

        response = requests.post(
            f"{api_url}/api/test",
            json={'upstream': package_name, 'version': package_version},
            headers={'Authorization': f'Bearer {api_key}'},
        )
        print(f"Triggered tests via API: {response.status_code}")
        if response.ok:
            print(response.json())
        else:
            print(f"Error: {response.text}")
            sys.exit(1)
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
                    test_command=test_cmd,
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
