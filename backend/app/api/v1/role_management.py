#!/usr/bin/env python3
"""
角色管理API路由模块

处理角色管理相关的HTTP请求
调用RoleService完成具体业务逻辑
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ...services.role_service import RoleService
from ...utils.exceptions import SmartTransportException
from . import api_v1_bp

role_bp = Blueprint('role', __name__, url_prefix='/roles')


@role_bp.route('/', methods=['GET'])
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
        # 使用服务层方法获取带用户数统计的角色列表
        roles = RoleService.list_roles_with_user_count()
        
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


@role_bp.route('/<int:role_id>/menus', methods=['PUT'])
@jwt_required()
def update_role_menus(role_id):
    """
    更新角色的菜单权限
    
    PUT /api/v1/roles/<role_id>/menus
    
    请求体:
    {
        "menu_ids": [菜单ID列表]
    }
    
    响应:
    {
        "code": 200,
        "message": "更新成功",
        "data": null
    }
    """
    try:
        # 验证角色是否存在
        role = RoleService.get_role_by_id(role_id)
        if not role:
            return jsonify({
                'code': 404,
                'message': '角色不存在',
                'data': None
            }), 404
        
        data = request.get_json()
        if not data or 'menu_ids' not in data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空或缺少menu_ids',
                'data': None
            }), 400
        
        menu_ids = data['menu_ids']
        
        # 验证菜单是否存在
        if menu_ids:
            existing_menus = db.session.query(Menu).filter(
                Menu.id.in_(menu_ids)
            ).all()
            existing_menu_ids = [m.id for m in existing_menus]
            
            invalid_ids = set(menu_ids) - set(existing_menu_ids)
            if invalid_ids:
                return jsonify({
                    'code': 400,
                    'message': f'菜单ID {list(invalid_ids)} 不存在',
                    'data': None
                }), 400
        
        # 获取菜单对应的权限
        permission_ids = []
        if menu_ids:
            menu_permissions = db.session.query(MenuPermission).filter(
                MenuPermission.menu_id.in_(menu_ids)
            ).all()
            permission_ids = list(set([mp.permission_id for mp in menu_permissions]))
        
        # 同步角色权限
        RolePermissionService.sync_role_permissions(role_id, permission_ids)
        
        return jsonify({
            'code': 200,
            'message': '菜单权限更新成功',
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


@role_bp.route('/<int:role_id>/menus', methods=['GET'])
@jwt_required()
def get_role_menus(role_id):
    """
    获取角色的菜单配置
    
    GET /api/v1/roles/<role_id>/menus
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {菜单树}
    }
    """
    try:
        # 获取角色拥有的权限
        role_permissions = RolePermissionService.get_role_permissions(role_id)
        permission_codes = [p['code'] for p in role_permissions]
        
        # 获取所有菜单
        menu_tree = MenuService.get_menu_tree()
        
        # 根据角色权限过滤菜单树
        filtered_menus = MenuService.get_menu_tree_by_role_permissions(menu_tree, permission_codes)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': filtered_menus
        })
        
    except SmartTransportException as e:
        print(f"SmartTransportException: {str(e)}")
        return jsonify({
            'code': e.status_code,
            'message': str(e),
            'data': None
        }), e.status_code
    except Exception as e:
        print(f"Exception in get_role_menus: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印错误堆栈信息
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500


@role_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@jwt_required()
def get_user_roles_api(user_id):
    """
    获取指定用户的所有角色

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


@role_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@jwt_required()
def assign_role_to_user_api(user_id):
    """
    为指定用户分配角色

    POST /api/v1/users/<user_id>/roles

    请求体:
    {
        "role_id": 角色ID
    }

    响应:
    {
        "code": 200,
        "message": "角色分配成功",
        "data": null
    }
    """
    try:
        data = request.get_json()
        if not data or 'role_id' not in data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空或缺少role_id',
                'data': None
            }), 400
        role_id = data['role_id']
        RoleService.assign_role_to_user(user_id, role_id)
        return jsonify({
            'code': 200,
            'message': '角色分配成功',
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


@role_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def remove_role_from_user_api(user_id, role_id):
    """
    移除指定用户的某个角色

    DELETE /api/v1/users/<user_id>/roles/<role_id>

    响应:
    {
        "code": 200,
        "message": "角色移除成功",
        "data": null
    }
    """
    try:
        RoleService.remove_role_from_user(user_id, role_id)
        return jsonify({
            'code': 200,
            'message': '角色移除成功',
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


@role_bp.route('/<int:role_id>', methods=['GET'])
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
        
        # 添加用户数统计
        user_count = RoleService.get_role_user_count(role_id)
        role['user_count'] = user_count
        
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


@role_bp.route('/', methods=['POST'])
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
        # 添加用户数字段
        role['user_count'] = 0
        
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


@role_bp.route('/<int:role_id>', methods=['PUT'])
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
        # 添加用户数统计
        user_count = RoleService.get_role_user_count(role_id)
        role['user_count'] = user_count
        
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


@role_bp.route('/<int:role_id>', methods=['DELETE'])
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
