"""Notify action script for GitHub Actions."""

import os
import requests
from wary import ResultsLedger


def main():
    upstream = os.environ['UPSTREAM']
    version = os.environ['VERSION']
    method = os.environ['METHOD']

    ledger = ResultsLedger()

    # Get recent failures
    failures = ledger.query_results(upstream_package=upstream, status='fail')

    # Filter to this version
    failures = [r for r in failures if r['upstream_version'] == version]

    if not failures:
        print("No failures to notify")
        return

    print(f"Found {len(failures)} failures for {upstream}@{version}")

    if method == 'github-issue':
        create_github_issues(upstream, version, failures)
    elif method == 'webhook':
        send_webhook(upstream, version, failures)
    elif method == 'slack':
        send_slack(upstream, version, failures)


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
        repo_url = failure.get('metadata', {}).get('repo_url', '')
        if not repo_url or 'github.com' not in repo_url:
            print(f"No GitHub repo URL for {downstream}, skipping")
            continue

        # Parse repo from URL
        # e.g., https://github.com/owner/repo -> owner/repo
        parts = repo_url.rstrip('/').split('/')
        if len(parts) >= 2:
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            print(f"Could not parse repo from {repo_url}")
            continue

        # Create issue
        issue_data = {
            'title': f"Test failure with {upstream}@{version}",
            'body': f"""
## Test Failure Report

Your package **{downstream}** failed tests with **{upstream}@{version}**.

### Details
- Test ID: `{failure['test_id']}`
- Status: {failure['status']}
- Started: {failure['started_at']}
- Duration: {failure['finished_at']}

### Output
```
{failure['output'][:1000]}
```

This issue was automatically created by [wary](https://github.com/thorwhalen/wary).
            """,
            'labels': ['dependency-test-failure', 'wary'],
        }

        url = f"https://api.github.com/repos/{owner_repo}/issues"
        response = requests.post(
            url, json=issue_data, headers={'Authorization': f'token {token}'}
        )

        if response.ok:
            print(f"✓ Created issue for {downstream}: {response.json()['html_url']}")
        else:
            print(f"✗ Failed to create issue for {downstream}: {response.text}")


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
                'output': f['output'][:500],  # Truncate
            }
            for f in failures
        ],
    }

    response = requests.post(url, json=data)
    print(f"Webhook sent: {response.status_code}")


def send_slack(upstream, version, failures):
    """Send Slack notification."""
    webhook_url = os.environ.get('SLACK_WEBHOOK')
    if not webhook_url:
        print("SLACK_WEBHOOK not set")
        return

    # Format message
    blocks = [
        {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': f'⚠️ Test Failures: {upstream}@{version}',
            },
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*{len(failures)}* dependent packages failed tests:',
            },
        },
    ]

    for failure in failures[:5]:  # Limit to 5
        blocks.append(
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"• *{failure['downstream_package']}*\n  Status: {failure['status']}\n  Test ID: `{failure['test_id']}`",
                },
            }
        )

    message = {'blocks': blocks}

    response = requests.post(webhook_url, json=message)
    if response.ok:
        print(f"✓ Slack notification sent")
    else:
        print(f"✗ Failed to send Slack notification: {response.text}")


if __name__ == '__main__':
    main()
