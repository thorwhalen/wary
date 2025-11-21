"""Combined server for wary API and UI.

This module creates a single server that serves both the REST API
and the web UI on different paths.
"""

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import os

from wary.api import create_app as create_api_app
from wary.ui import create_ui_app


def create_combined_app(config=None):
    """Create a combined Flask app with both API and UI.

    The API is mounted at /api and the UI at /.

    Args:
        config: Optional configuration dict

    Returns:
        WSGI application
    """
    # Create the apps
    ui_app = create_ui_app(config)
    api_app = create_api_app(config)

    # Combine them with DispatcherMiddleware
    # UI is the main app, API is mounted at /api
    application = DispatcherMiddleware(ui_app, {'/api': api_app})

    return application


def run_server(host='0.0.0.0', port=8000, use_reloader=True, use_debugger=True):
    """Run the combined server.

    Args:
        host: Host to bind to
        port: Port to bind to
        use_reloader: Enable auto-reloader for development
        use_debugger: Enable debugger for development
    """
    app = create_combined_app()

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                      Wary Server                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🌐 Web UI:  http://{host}:{port}/
    🔌 API:     http://{host}:{port}/api

    📊 Dashboard:       http://{host}:{port}/
    📦 Package Details: http://{host}:{port}/package/<name>
    📝 Test Results:    http://{host}:{port}/results
    ✍️  Register:        http://{host}:{port}/register

    API Endpoints:
      GET  /api                           - API info
      GET  /api/dependents/<upstream>    - Get dependents
      POST /api/dependents                - Register dependent
      POST /api/test                      - Trigger tests
      GET  /api/results                   - Query results
      GET  /api/stats                     - Statistics

    Press Ctrl+C to stop
    """)

    run_simple(
        host,
        port,
        app,
        use_reloader=use_reloader,
        use_debugger=use_debugger,
        use_evalex=True,
    )


def run_production_server(host='0.0.0.0', port=8000):
    """Run the server in production mode.

    This uses gunicorn if available, otherwise falls back to werkzeug.
    """
    try:
        import gunicorn.app.base

        class WaryApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                config = {
                    key: value
                    for key, value in self.options.items()
                    if key in self.cfg.settings and value is not None
                }
                for key, value in config.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        app = create_combined_app()

        options = {
            'bind': f'{host}:{port}',
            'workers': os.cpu_count() * 2 + 1,
            'worker_class': 'sync',
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'info',
        }

        print(f"Starting Wary production server on {host}:{port}")
        print(f"Workers: {options['workers']}")

        WaryApplication(app, options).run()

    except ImportError:
        print("gunicorn not found, using werkzeug (not recommended for production)")
        print("Install gunicorn with: pip install gunicorn")
        run_server(host=host, port=port, use_reloader=False, use_debugger=False)


if __name__ == '__main__':
    # Check if we're in production mode
    is_production = os.environ.get('WARY_ENV') == 'production'

    if is_production:
        run_production_server()
    else:
        run_server()
