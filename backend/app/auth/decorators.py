from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            from flask import g
            from ..models.user import User
            g.current_user = User.query.get(user_id)
            if not g.current_user:
                return jsonify({"msg": "User not found"}), 401
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"msg": "Missing or invalid token", "error": str(e)}), 401
    return wrapper