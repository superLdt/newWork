#!/usr/bin/env python3
"""
认证模块路由文件

表现层 - 处理HTTP请求响应
调用服务层完成具体业务逻辑
"""

from flask import jsonify, request
from . import auth_bp
from ..services.auth_service import AuthService
from ..utils.exceptions import SmartTransportException
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.user import User


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    
    POST /api/auth/login
    
    请求体:
    {
        "username": "用户名",
        "password": "密码"
    }
    
    响应:
    {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": "jwt_token",
            "user": {用户详细信息},
            "expires_in": 3600
        }
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空',
                'data': None
            }), 400
        
        # 先通过服务层校验用户名和密码（返回用户信息等）
        result = AuthService.authenticate_user(
            data.get('username'), 
            data.get('password')
        )
        # 从结果中提取用户信息和token
        user_dict = result.get('user')
        # 从结果中提取token
        access_token = result.get('token')
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': access_token,
                'user': user_dict,
                'expires_in': result.get('expires_in')
            }
        })
        
    except SmartTransportException as e:
        return jsonify({
            'code': e.status_code,
            'message': str(e),
            'data': None
        }), e.status_code
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    用户登出接口
    
    POST /api/auth/logout
    
    注意：前端需清除本地存储的token
    """
    return jsonify({
        'code': 200,
        'message': '登出成功',
        'data': None
    })


@auth_bp.route('/userinfo', methods=['GET'])
@jwt_required()
def get_user_info():
    """
    获取当前用户信息接口
    
    GET /api/auth/userinfo
    
    请求头:
    Authorization: Bearer <token>
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {用户详细信息}
    }
    """
    try:
        # 从JWT中获取用户ID
        identity = get_jwt_identity()
        if not identity:
            return jsonify({
                'code': 401,
                'message': '缺少认证token',
                'data': None
            }), 401
        
        user = User.query.get(int(identity))
        if not user or not user.is_active:
            return jsonify({
                'code': 401,
                'message': '用户不存在或已被禁用',
                'data': None
            }), 401
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user.to_dict()
        })
        
    except SmartTransportException as e:
        return jsonify({
            'code': e.status_code,
            'message': str(e),
            'data': None
        }), e.status_code
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500