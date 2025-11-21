"""Register action script for GitHub Actions."""

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
                    'repo_url': repo_url,
                },
                headers={'Authorization': f'Bearer {api_key}'},
            )
            print(f"Registered {repo_name} → {upstream}: {response.status_code}")
            if response.status_code >= 400:
                print(f"Error: {response.text}")
    else:
        # Register locally (Phase 1/2)
        from wary import DependencyGraph

        graph = DependencyGraph()

        for upstream in upstream_packages:
            graph.register_dependent(
                upstream=upstream.strip(),
                downstream=repo_name,
                test_command=test_command,
                repo_url=repo_url,
            )
            print(f"✓ Registered {repo_name} as dependent of {upstream}")


if __name__ == '__main__':
    main()
