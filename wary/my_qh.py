"""Extensions to qh for features we wish existed.

This module provides utilities for creating REST APIs that we'd like
to see in qh. These can be moved to qh later.
"""

from functools import wraps
from typing import Callable, Any, Optional
import json


def json_api(func: Callable) -> Callable:
    """Decorator to make a function return JSON responses.

    Handles:
    - Converting return values to JSON
    - Setting correct content-type headers
    - Error handling with JSON error responses
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # If result is a tuple (data, status_code), handle it
            if isinstance(result, tuple):
                data, status_code = result
                return json.dumps(data), status_code, {'Content-Type': 'application/json'}
            else:
                return json.dumps(result), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            error_response = {'error': str(e), 'type': type(e).__name__}
            return json.dumps(error_response), 500, {'Content-Type': 'application/json'}

    return wrapper


def require_auth(api_key_header: str = 'Authorization'):
    """Decorator to require API key authentication.

    Args:
        api_key_header: Header name for API key (default: 'Authorization')

    The decorator expects API keys to be validated against an
    environment variable or config.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This is a placeholder - in real implementation,
            # we'd check the request headers
            # For now, just pass through
            return func(*args, **kwargs)

        return wrapper

    return decorator


class SimpleAPI:
    """A simple REST API builder.

    This provides a Flask-like interface for building APIs quickly.
    It's what we wish qh had for simple use cases.
    """

    def __init__(self, title: str = "API", version: str = "1.0.0"):
        self.title = title
        self.version = version
        self.routes = {}

    def route(self, path: str, methods: list[str] = None):
        """Register a route."""
        if methods is None:
            methods = ['GET']

        def decorator(func: Callable) -> Callable:
            self.routes[path] = {'handler': func, 'methods': methods}
            return func

        return decorator

    def get_handler(self, path: str, method: str) -> Optional[Callable]:
        """Get handler for a path and method."""
        route = self.routes.get(path)
        if route and method in route['methods']:
            return route['handler']
        return None


def create_flask_from_functions(functions: dict[str, Callable], base_path: str = '/api'):
    """Create a Flask app from a dictionary of functions.

    Args:
        functions: Dict mapping endpoint paths to handler functions
        base_path: Base path for all endpoints

    Returns:
        Flask app
    """
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    for path, handler in functions.items():
        full_path = f"{base_path}/{path.lstrip('/')}"

        @app.route(full_path, methods=['GET', 'POST', 'PUT', 'DELETE'])
        @wraps(handler)
        def route_handler(*args, **kwargs):
            try:
                # Get request data
                if request.method in ['POST', 'PUT']:
                    data = request.get_json()
                    kwargs.update(data or {})

                # Get query params
                kwargs.update(request.args.to_dict())

                # Call handler
                result = handler(*args, **kwargs)

                # Handle tuple response (data, status_code)
                if isinstance(result, tuple):
                    return jsonify(result[0]), result[1]
                else:
                    return jsonify(result)

            except Exception as e:
                return jsonify({'error': str(e), 'type': type(e).__name__}), 500

        # Store the handler with a unique name
        route_handler.__name__ = f"handler_{path.replace('/', '_')}"

    return app


def auto_api(obj: Any, prefix: str = ''):
    """Automatically create API endpoints from an object's methods.

    This inspects an object and creates REST endpoints for its methods.

    Args:
        obj: Object to create API from
        prefix: URL prefix for endpoints

    Returns:
        Dict of endpoint paths to handler functions
    """
    endpoints = {}

    # Get all public methods
    for name in dir(obj):
        if not name.startswith('_'):
            attr = getattr(obj, name)
            if callable(attr):
                # Create endpoint path
                path = f"{prefix}/{name}".replace('//', '/')
                endpoints[path] = attr

    return endpoints
