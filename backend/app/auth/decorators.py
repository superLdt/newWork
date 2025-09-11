from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # 预检请求直接放行
            if request.method == 'OPTIONS':
                return fn(*args, **kwargs)
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            from ..models.user import User
            g.current_user = User.query.get(user_id)
            if not g.current_user:
                return jsonify({"msg": "User not found"}), 401
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"msg": "Missing or invalid token", "error": str(e)}), 401
    return wrapper


def permission_required(permission_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 预检请求直接放行
            if request.method == 'OPTIONS':
                return fn(*args, **kwargs)
            try:
                # 确保已完成JWT校验并注入当前用户
                if not hasattr(g, 'current_user') or g.current_user is None:
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                    from ..models.user import User
                    g.current_user = User.query.get(user_id)
                    if not g.current_user:
                        return jsonify({"msg": "User not found"}), 401
                # 权限校验
                if not g.current_user.has_permission(permission_name):
                    return jsonify({"msg": "Permission denied"}), 403
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"msg": "Missing or invalid token", "error": str(e)}), 401
        return wrapper
    return decorator