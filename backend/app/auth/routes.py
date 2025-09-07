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
        
        result = AuthService.authenticate_user(
            data.get('username'), 
            data.get('password')
        )
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': result
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
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'code': 401,
                'message': '缺少认证token',
                'data': None
            }), 401
        
        token = auth_header.split(' ')[1]
        user = AuthService.get_user_by_token(token)
        
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