#!/usr/bin/env python3
"""
Main Flask application
"""
from flask import Flask, jsonify, abort, request
from api.v1.views import app_views
import os

app = Flask(__name__)
app.register_blueprint(app_views)

# --- CORS configuration (optional, remove if not strictly needed) ---
# from flask_cors import CORS
# CORS(app, resources={r"/api/v1/*": {"origins": "*"}})


# --- Authentication instance initialization ---
auth = None
AUTH_TYPE = os.getenv('AUTH_TYPE')

if AUTH_TYPE == 'basic_auth':  # Check for basic_auth first
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
elif AUTH_TYPE == 'auth':  # Fallback to general Auth if not basic_auth
    from api.v1.auth.auth import Auth
    auth = Auth()


# --- Error handlers ---

@app.errorhandler(401)
def unauthorized(error):
    """
    Handler for 401 Unauthorized errors.
    Returns a JSON response with status code 401.
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error):
    """
    Handler for 403 Forbidden errors.
    Returns a JSON response with status code 403.
    """
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(error):
    """
    Handler for 404 Not Found errors.
    Returns a JSON response with status code 404.
    """
    return jsonify({"error": "Not found"}), 404


# --- before_request handler for authentication/authorization ---

@app.before_request
def handle_before_request():
    """
    Handles operations before each request is processed,
    for authentication and authorization checks.
    """
    if auth is None:
        return

    excluded_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/'
    ]

    if auth.require_auth(request.path, excluded_paths):
        if auth.authorization_header(request) is None:
            abort(401)
        if auth.current_user(request) is None:
            abort(403)


# --- Main execution block for running the Flask development server ---

if __name__ == "__main__":
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))

    app.run(host=API_HOST, port=API_PORT, debug=True)
