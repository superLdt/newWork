#!/usr/bin/env python3
"""
用户管理API路由模块

处理用户管理相关的HTTP请求
调用UserService完成具体业务逻辑
"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from ...services.user_service import UserService
from ...utils.exceptions import SmartTransportException
from . import api_v1_bp


@api_v1_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """
    获取用户列表
    
    GET /api/v1/users
    
    查询参数:
    - page: 页码，默认1
    - per_page: 每页数量，默认20
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": [用户列表],
            "total": 总数,
            "page": 当前页,
            "per_page": 每页数量,
            "pages": 总页数
        }
    }
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        result = UserService.list_users(page, per_page)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500


@api_v1_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    获取用户详情
    
    GET /api/v1/users/<user_id>
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {用户信息}
    }
    """
    try:
        user = UserService.get_user_by_id(user_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user
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


@api_v1_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """
    创建用户
    
    POST /api/v1/users
    
    请求体:
    {
        "username": "用户名",
        "password": "密码",
        "full_name": "姓名",
        "email": "邮箱",
        "phone": "手机号",
        "company_id": 公司ID
    }
    
    响应:
    {
        "code": 200,
        "message": "创建成功",
        "data": {用户信息}
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        user = UserService.create_user(data)
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': user
        }), 201
        
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


@api_v1_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    更新用户信息
    
    PUT /api/v1/users/<user_id>
    
    请求体:
    {
        "full_name": "姓名",
        "email": "邮箱",
        "phone": "手机号",
        "company_id": 公司ID,
        "password": "新密码" (可选)
    }
    
    响应:
    {
        "code": 200,
        "message": "更新成功",
        "data": {用户信息}
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        user = UserService.update_user(user_id, data)
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user
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


@api_v1_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    删除用户（软删除）
    
    DELETE /api/v1/users/<user_id>
    
    响应:
    {
        "code": 200,
        "message": "删除成功",
        "data": null
    }
    """
    try:
        UserService.delete_user(user_id)
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
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