#!/usr/bin/env python3
"""
Main Flask application
"""
from flask import Flask, jsonify, abort, request
from api.v1.views import app_views
import os

app = Flask(__name__)
app.register_blueprint(app_views)

# Authentication instance initialization
auth = None
AUTH_TYPE = os.getenv('AUTH_TYPE')

if AUTH_TYPE == 'basic_auth':
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
elif AUTH_TYPE == 'auth':
    from api.v1.auth.auth import Auth
    auth = Auth()

# Error handlers
@app.errorhandler(401)
def unauthorized(error):
    """Handles 401 Unauthorized errors"""
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(error):
    """Handles 403 Forbidden errors"""
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(error):
    """Handles 404 Not Found errors"""
    return jsonify({"error": "Not found"}), 404

# before_request handler
@app.before_request
def before_request():
    """Handles authentication before each request"""
    if auth is None:
        return

    excluded_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'
    ]

    if not auth.require_auth(request.path, excluded_paths):
        return

    # First check authorization header exists
    if auth.authorization_header(request) is None:
        abort(401)

    # THEN set current user on request object
    request.current_user = auth.current_user(request)
    
    # FINALLY check if current user exists
    if request.current_user is None:
        abort(403)

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = os.getenv("API_PORT", "5000")
    app.run(host=host, port=port, debug=True)
