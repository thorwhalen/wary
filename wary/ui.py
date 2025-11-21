"""Web UI for wary using Flask and my_uf.

This module provides a web dashboard for viewing dependency graphs,
test results, and statistics.
"""

from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

from wary.graph import DependencyGraph
from wary.ledger import ResultsLedger
from wary.watcher import VersionWatcher
from wary.my_uf import (
    Page,
    Component,
    ComponentType,
    make_table,
    make_stats,
    make_card,
    make_badge,
)


def create_ui_app(config=None):
    """Create Flask app for the web UI.

    Args:
        config: Optional configuration dict

    Returns:
        Flask app
    """
    app = Flask(__name__)

    if config:
        app.config.update(config)

    @app.route('/')
    def home():
        """Home page with dashboard."""
        graph = DependencyGraph()
        ledger = ResultsLedger()

        # Get stats
        all_edges = graph.get_all_edges()
        all_results = list(ledger.query_results())

        stats = [
            {'label': 'Registered Dependencies', 'value': len(all_edges)},
            {'label': 'Total Tests', 'value': len(all_results)},
        ]

        if all_results:
            passed = sum(1 for r in all_results if r['status'] == 'pass')
            stats.append({'label': 'Pass Rate', 'value': f"{passed/len(all_results)*100:.1f}%"})

        # Recent failures
        recent_failures = ledger.query_results(status='fail')
        recent_failures = sorted(
            recent_failures, key=lambda r: r.get('started_at', ''), reverse=True
        )[:10]

        # Build page
        components = [
            Component(type=ComponentType.HEADING, content='Wary Dashboard', props={'level': 1}),
            make_stats(stats),
            Component(type=ComponentType.HEADING, content='Recent Failures', props={'level': 2}),
        ]

        if recent_failures:
            failure_rows = []
            for r in recent_failures:
                status_badge = make_badge('FAIL', 'red')
                failure_rows.append(
                    [
                        r['upstream_package'],
                        r['downstream_package'],
                        r['upstream_version'],
                        status_badge.to_html(),
                        r.get('started_at', 'N/A')[:19],
                    ]
                )

            components.append(
                make_table(
                    columns=['Upstream', 'Downstream', 'Version', 'Status', 'Date'],
                    rows=failure_rows,
                )
            )
        else:
            components.append(Component(type=ComponentType.TEXT, content='No recent failures'))

        # Upstream packages
        upstream_packages = {}
        for edge in all_edges:
            upstream = edge['upstream']
            if upstream not in upstream_packages:
                upstream_packages[upstream] = 0
            upstream_packages[upstream] += 1

        if upstream_packages:
            components.append(
                Component(
                    type=ComponentType.HEADING, content='Top Upstream Packages', props={'level': 2}
                )
            )

            top_packages = sorted(
                upstream_packages.items(), key=lambda x: x[1], reverse=True
            )[:10]

            package_rows = [[pkg, count] for pkg, count in top_packages]
            components.append(make_table(columns=['Package', 'Dependents'], rows=package_rows))

        page = Page(title='Wary Dashboard', components=components)
        return page.to_html()

    @app.route('/package/<package_name>')
    def package_details(package_name):
        """Details for a specific package."""
        graph = DependencyGraph()
        ledger = ResultsLedger()

        # Get dependents
        dependents = graph.get_dependents(package_name)

        # Get test results
        results = ledger.query_results(upstream_package=package_name)

        # Calculate stats
        stats = [
            {'label': 'Dependents', 'value': len(dependents)},
            {'label': 'Total Tests', 'value': len(results)},
        ]

        if results:
            passed = sum(1 for r in results if r['status'] == 'pass')
            failed = sum(1 for r in results if r['status'] == 'fail')
            stats.append({'label': 'Passed', 'value': passed})
            stats.append({'label': 'Failed', 'value': failed})
            stats.append({'label': 'Pass Rate', 'value': f"{passed/len(results)*100:.1f}%"})

        # Build page
        components = [
            Component(
                type=ComponentType.HEADING,
                content=f'Package: {package_name}',
                props={'level': 1},
            ),
            make_stats(stats),
            Component(type=ComponentType.HEADING, content='Dependents', props={'level': 2}),
        ]

        if dependents:
            dependent_rows = []
            for d in dependents:
                dependent_rows.append(
                    [
                        d['downstream'],
                        d.get('constraint', ''),
                        d.get('metadata', {}).get('test_command', 'N/A'),
                    ]
                )

            components.append(
                make_table(
                    columns=['Package', 'Constraint', 'Test Command'], rows=dependent_rows
                )
            )
        else:
            components.append(
                Component(type=ComponentType.TEXT, content='No dependents registered')
            )

        # Recent test results
        components.append(Component(type=ComponentType.HEADING, content='Test History', props={'level': 2}))

        if results:
            # Sort by date
            results = sorted(results, key=lambda r: r.get('started_at', ''), reverse=True)[:20]

            result_rows = []
            for r in results:
                status_color = 'green' if r['status'] == 'pass' else 'red'
                status_badge = make_badge(r['status'].upper(), status_color)
                result_rows.append(
                    [
                        r['downstream_package'],
                        r['upstream_version'],
                        status_badge.to_html(),
                        r.get('started_at', 'N/A')[:19],
                    ]
                )

            components.append(
                make_table(
                    columns=['Downstream', 'Version', 'Status', 'Date'], rows=result_rows
                )
            )
        else:
            components.append(Component(type=ComponentType.TEXT, content='No test results yet'))

        page = Page(title=f'{package_name} - Wary', components=components)
        return page.to_html()

    @app.route('/results')
    def results_list():
        """List of all test results."""
        ledger = ResultsLedger()

        # Get filters from query params
        upstream = request.args.get('upstream')
        downstream = request.args.get('downstream')
        status = request.args.get('status')

        results = ledger.query_results(
            upstream_package=upstream, downstream_package=downstream, status=status
        )

        # Sort by date
        results = sorted(results, key=lambda r: r.get('started_at', ''), reverse=True)[:100]

        # Build page
        components = [
            Component(type=ComponentType.HEADING, content='Test Results', props={'level': 1}),
            Component(
                type=ComponentType.TEXT,
                content=f'Showing {len(results)} results (filtered)' if any([upstream, downstream, status]) else f'Showing {len(results)} most recent results',
            ),
        ]

        if results:
            result_rows = []
            for r in results:
                status_color = 'green' if r['status'] == 'pass' else 'red'
                status_badge = make_badge(r['status'].upper(), status_color)
                result_rows.append(
                    [
                        r['upstream_package'],
                        r['downstream_package'],
                        r['upstream_version'],
                        status_badge.to_html(),
                        r.get('started_at', 'N/A')[:19],
                        r['test_id'][:8] + '...',
                    ]
                )

            components.append(
                make_table(
                    columns=['Upstream', 'Downstream', 'Version', 'Status', 'Date', 'Test ID'],
                    rows=result_rows,
                )
            )
        else:
            components.append(Component(type=ComponentType.TEXT, content='No results found'))

        page = Page(title='Test Results - Wary', components=components)
        return page.to_html()

    @app.route('/result/<test_id>')
    def result_detail(test_id):
        """Detailed view of a test result."""
        ledger = ResultsLedger()

        try:
            result = ledger[test_id]
        except KeyError:
            return '<h1>Test result not found</h1>', 404

        # Build page
        status_color = 'green' if result['status'] == 'pass' else 'red'
        status_badge = make_badge(result['status'].upper(), status_color)

        components = [
            Component(
                type=ComponentType.HEADING, content='Test Result Details', props={'level': 1}
            ),
            make_card(
                'Test Information',
                f"""
                <p><strong>Test ID:</strong> {result['test_id']}</p>
                <p><strong>Upstream:</strong> {result['upstream_package']}@{result['upstream_version']}</p>
                <p><strong>Downstream:</strong> {result['downstream_package']}@{result['downstream_version']}</p>
                <p><strong>Status:</strong> {status_badge.to_html()}</p>
                <p><strong>Test Command:</strong> {result['test_command']}</p>
                <p><strong>Started:</strong> {result.get('started_at', 'N/A')}</p>
                <p><strong>Finished:</strong> {result.get('finished_at', 'N/A')}</p>
                <p><strong>Exit Code:</strong> {result['exit_code']}</p>
                """,
            ),
            make_card('Test Output', f'<pre>{result.get("output", "No output")}</pre>'),
        ]

        page = Page(title=f'Test {test_id[:8]} - Wary', components=components)
        return page.to_html()

    @app.route('/register')
    def register_form():
        """Form to register a new dependent."""
        components = [
            Component(
                type=ComponentType.HEADING,
                content='Register Dependent Package',
                props={'level': 1},
            ),
            Component(
                type=ComponentType.TEXT,
                content='Register your package as dependent of an upstream package.',
            ),
            Component(
                type=ComponentType.TEXT,
                content="""
                <form method="POST" action="/register">
                    <div style="margin: 10px 0;">
                        <label>Upstream Package:</label><br>
                        <input type="text" name="upstream" required style="width: 300px; padding: 8px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <label>Your Package (Downstream):</label><br>
                        <input type="text" name="downstream" required style="width: 300px; padding: 8px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <label>Version Constraint:</label><br>
                        <input type="text" name="constraint" placeholder=">=1.0.0" style="width: 300px; padding: 8px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <label>Test Command:</label><br>
                        <input type="text" name="test_command" value="pytest" style="width: 300px; padding: 8px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <label>Contact Email:</label><br>
                        <input type="email" name="contact" style="width: 300px; padding: 8px;">
                    </div>
                    <div style="margin: 20px 0;">
                        <button type="submit" style="padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Register
                        </button>
                    </div>
                </form>
                """,
            ),
        ]

        page = Page(title='Register - Wary', components=components)
        return page.to_html()

    @app.route('/register', methods=['POST'])
    def register_submit():
        """Handle registration form submission."""
        graph = DependencyGraph()

        upstream = request.form.get('upstream')
        downstream = request.form.get('downstream')
        constraint = request.form.get('constraint', '')
        test_command = request.form.get('test_command', 'pytest')
        contact = request.form.get('contact', '')

        if upstream and downstream:
            graph.register_dependent(
                upstream=upstream,
                downstream=downstream,
                constraint=constraint,
                test_command=test_command,
                contact=contact,
            )

            return redirect(f'/package/{upstream}')
        else:
            return '<h1>Error: upstream and downstream are required</h1>', 400

    return app


def run_ui_server(host='0.0.0.0', port=8000):
    """Run UI development server."""
    app = create_ui_app()
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_ui_server()
