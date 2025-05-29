#!/usr/bin/env python3
"""
User view module
"""
from flask import abort, jsonify, request
from api.v1.views import app_views
from models.user import User


@app_views.route('/users', methods=['GET'], strict_slashes=False)
def get_users():
    """Retrieves the list of all User objects"""
    users = User.all()
    return jsonify([user.to_json() for user in users])


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def get_user(user_id):
    """Retrieves a specific User object"""
    if user_id == 'me':
        if request.current_user is None:
            abort(404)
        return jsonify(request.current_user.to_json())
    
    user = User.get(user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_json())


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user():
    """Creates a new User"""
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")
    if 'email' not in data:
        abort(400, description="Missing email")
    if 'password' not in data:
        abort(400, description="Missing password")
    
    user = User()
    user.email = data['email']
    user.password = data['password']
    user.save()
    return jsonify(user.to_json()), 201


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id):
    """Updates a User object"""
    if user_id == 'me':
        if request.current_user is None:
            abort(404)
        user = request.current_user
    else:
        user = User.get(user_id)
        if user is None:
            abort(404)
    
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")
    
    ignore_keys = ['id', 'email', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(user, key, value)
    user.save()
    return jsonify(user.to_json())


@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id):
    """Deletes a User object"""
    if user_id == 'me':
        if request.current_user is None:
            abort(404)
        user = request.current_user
    else:
        user = User.get(user_id)
        if user is None:
            abort(404)
    
    user.remove()
    return jsonify({}), 200
