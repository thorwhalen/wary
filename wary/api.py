"""HTTP API for wary using qh and Flask.

This module provides a REST API for the wary dependency monitoring service.
It allows remote registration of dependents, triggering tests, and querying results.
"""

from flask import Flask, request, jsonify
from functools import wraps
import os

from wary.graph import DependencyGraph
from wary.watcher import VersionWatcher
from wary.orchestrator import TestOrchestrator
from wary.ledger import ResultsLedger


# Shared instances (can be configured to use PostgreSQL)
def get_graph():
    """Get dependency graph instance."""
    # Could be configured to use PostgreSQL via env var
    return DependencyGraph()


def get_orchestrator():
    """Get test orchestrator instance."""
    return TestOrchestrator()


def get_ledger():
    """Get results ledger instance."""
    return ResultsLedger()


def get_watcher():
    """Get version watcher instance."""
    return VersionWatcher()


# Simple auth decorator
def require_api_key(f):
    """Require API key for protected endpoints."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization', '')
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]

        # In production, validate against database
        # For now, check against environment variable
        expected_key = os.environ.get('WARY_API_KEY', '')
        if expected_key and api_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)

    return decorated_function


def create_app(config=None):
    """Create Flask app with wary API endpoints.

    Args:
        config: Optional configuration dict

    Returns:
        Flask app
    """
    app = Flask(__name__)

    if config:
        app.config.update(config)

    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'ok', 'service': 'wary'})

    # API info
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information."""
        return jsonify(
            {
                'name': 'Wary API',
                'version': '1.0.0',
                'description': 'Dependency monitoring and testing service',
                'endpoints': {
                    'GET /health': 'Health check',
                    'GET /api': 'API information',
                    'GET /api/dependents/<upstream>': 'Get dependents of a package',
                    'POST /api/dependents': 'Register a new dependent',
                    'POST /api/test': 'Test all dependents',
                    'GET /api/results': 'Query test results',
                    'GET /api/results/<test_id>': 'Get specific test result',
                    'GET /api/packages/<package>/version': 'Get latest version',
                    'POST /api/watch': 'Add package to watch list',
                },
            }
        )

    # Dependents endpoints
    @app.route('/api/dependents/<upstream>', methods=['GET'])
    def get_dependents(upstream):
        """Get all dependents of a package."""
        try:
            graph = get_graph()
            dependents = graph.get_dependents(upstream)
            return jsonify({'upstream': upstream, 'dependents': dependents})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/dependents', methods=['POST'])
    @require_api_key
    def register_dependent():
        """Register a new dependent package."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            upstream = data.get('upstream')
            downstream = data.get('downstream')

            if not upstream or not downstream:
                return jsonify({'error': 'upstream and downstream are required'}), 400

            graph = get_graph()
            graph.register_dependent(
                upstream=upstream,
                downstream=downstream,
                constraint=data.get('constraint', ''),
                test_command=data.get('test_command', 'pytest'),
                contact=data.get('contact', ''),
                repo_url=data.get('repo_url', ''),
            )

            return jsonify({'status': 'registered', 'upstream': upstream, 'downstream': downstream}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Test endpoint
    @app.route('/api/test', methods=['POST'])
    @require_api_key
    def trigger_test():
        """Test all dependents of a package at a specific version."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            upstream = data.get('upstream')
            version = data.get('version')

            if not upstream or not version:
                return jsonify({'error': 'upstream and version are required'}), 400

            graph = get_graph()
            orchestrator = get_orchestrator()

            # This could be async/background job in production
            results = orchestrator.test_all_dependents(upstream, version, graph)

            summary = {
                'upstream': upstream,
                'version': version,
                'total': len(results),
                'passed': sum(1 for r in results if r['status'] == 'pass'),
                'failed': sum(1 for r in results if r['status'] == 'fail'),
                'results': [
                    {'downstream': r['downstream_package'], 'status': r['status'], 'test_id': r['test_id']}
                    for r in results
                ],
            }

            return jsonify(summary)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Results endpoints
    @app.route('/api/results', methods=['GET'])
    def query_results():
        """Query test results with filters."""
        try:
            ledger = get_ledger()

            # Get query parameters
            upstream = request.args.get('upstream')
            downstream = request.args.get('downstream')
            status = request.args.get('status')
            limit = int(request.args.get('limit', 100))

            results = ledger.query_results(
                upstream_package=upstream, downstream_package=downstream, status=status
            )

            # Limit results
            results = results[:limit]

            return jsonify({'count': len(results), 'results': results})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/results/<test_id>', methods=['GET'])
    def get_result(test_id):
        """Get a specific test result."""
        try:
            ledger = get_ledger()
            result = ledger[test_id]
            return jsonify(result)
        except KeyError:
            return jsonify({'error': 'Test result not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Package version endpoint
    @app.route('/api/packages/<package>/version', methods=['GET'])
    def get_package_version(package):
        """Get latest version of a package from PyPI."""
        try:
            watcher = get_watcher()
            latest = watcher.get_latest_version(package)
            stored = watcher.get_stored_version(package)

            return jsonify({'package': package, 'latest': latest, 'stored': stored})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Watch endpoint
    @app.route('/api/watch', methods=['POST'])
    @require_api_key
    def add_watch():
        """Add a package to the watch list."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            package = data.get('package')

            if not package:
                return jsonify({'error': 'package is required'}), 400

            # In production, this would add to a persistent watch list
            # For now, just acknowledge
            return jsonify({'status': 'watching', 'package': package})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Statistics endpoint
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get overall statistics."""
        try:
            graph = get_graph()
            ledger = get_ledger()

            all_edges = graph.get_all_edges()
            all_results = list(ledger.query_results())

            stats = {
                'total_edges': len(all_edges),
                'total_tests': len(all_results),
                'unique_upstream': len(set(e['upstream'] for e in all_edges)),
                'unique_downstream': len(set(e['downstream'] for e in all_edges)),
            }

            if all_results:
                stats['passed'] = sum(1 for r in all_results if r['status'] == 'pass')
                stats['failed'] = sum(1 for r in all_results if r['status'] == 'fail')
                stats['pass_rate'] = stats['passed'] / len(all_results) * 100

            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


def run_dev_server(host='0.0.0.0', port=5000):
    """Run development server."""
    app = create_app()
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_dev_server()
