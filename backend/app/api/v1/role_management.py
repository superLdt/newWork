#!/usr/bin/env python3
"""
角色管理API路由模块

处理角色管理相关的HTTP请求
调用RoleService完成具体业务逻辑
"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from ...services.role_service import RoleService
from ...utils.exceptions import SmartTransportException
from . import api_v1_bp


@api_v1_bp.route('/roles', methods=['GET'])
@jwt_required()
def list_roles():
    """
    获取角色列表
    
    GET /api/v1/roles
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": [角色列表]
    }
    """
    try:
        roles = RoleService.list_roles()
        
        # 为每个角色添加用户数统计
        for role in roles:
            role_id = role['id']
            # 这里简化处理，实际应该通过RoleService提供方法
            role['user_count'] = 0  # 简化处理，实际需要查询关联表
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': roles
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500


@api_v1_bp.route('/roles/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """
    获取角色详情
    
    GET /api/v1/roles/<role_id>
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {角色信息}
    }
    """
    try:
        role = RoleService.get_role_by_id(role_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': role
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


@api_v1_bp.route('/roles', methods=['POST'])
@jwt_required()
def create_role():
    """
    创建角色
    
    POST /api/v1/roles
    
    请求体:
    {
        "name": "角色名称",
        "description": "角色描述"
    }
    
    响应:
    {
        "code": 200,
        "message": "创建成功",
        "data": {角色信息}
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
        
        role = RoleService.create_role(data)
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': role
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


@api_v1_bp.route('/roles/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """
    更新角色信息
    
    PUT /api/v1/roles/<role_id>
    
    请求体:
    {
        "description": "角色描述"
    }
    
    响应:
    {
        "code": 200,
        "message": "更新成功",
        "data": {角色信息}
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
        
        role = RoleService.update_role(role_id, data)
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': role
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


@api_v1_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """
    删除角色
    
    DELETE /api/v1/roles/<role_id>
    
    响应:
    {
        "code": 200,
        "message": "删除成功",
        "data": null
    }
    """
    try:
        RoleService.delete_role(role_id)
        
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


@api_v1_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@jwt_required()
def get_user_roles(user_id):
    """
    获取用户的所有角色
    
    GET /api/v1/users/<user_id>/roles
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": [角色列表]
    }
    """
    try:
        roles = RoleService.get_user_roles(user_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': roles
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


@api_v1_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['POST'])
@jwt_required()
def assign_role_to_user(user_id, role_id):
    """
    为用户分配角色
    
    POST /api/v1/users/<user_id>/roles/<role_id>
    
    响应:
    {
        "code": 200,
        "message": "分配成功",
        "data": null
    }
    """
    try:
        RoleService.assign_role_to_user(user_id, role_id)
        
        return jsonify({
            'code': 200,
            'message': '分配成功',
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


@api_v1_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def remove_role_from_user(user_id, role_id):
    """
    移除用户的角色
    
    DELETE /api/v1/users/<user_id>/roles/<role_id>
    
    响应:
    {
        "code": 200,
        "message": "移除成功",
        "data": null
    }
    """
    try:
        RoleService.remove_role_from_user(user_id, role_id)
        
        return jsonify({
            'code': 200,
            'message': '移除成功',
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