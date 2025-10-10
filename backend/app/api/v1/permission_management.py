# -*- coding: utf-8 -*-
"""
权限管理API接口
提供权限的CRUD操作和权限验证功能
"""

from flask import Blueprint, request, jsonify, g
from ...services.permission_service import PermissionService
from ...common.response import success_response, error_response
from ...auth.decorators import token_required
from typing import Optional

# 创建蓝图
bp = Blueprint('permission_management', __name__, url_prefix='/permissions')


@bp.route('', methods=['GET'])
@token_required
def get_permissions():
    """
    获取权限列表（分页）
    
    Query Parameters:
        page (int): 页码，默认1
        per_page (int): 每页数量，默认20
        search (str): 搜索关键词
        resource_type (str): 资源类型过滤
        action (str): 操作类型过滤
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        resource_type = request.args.get('resource_type', '')
        action = request.args.get('action', '')
        
        # 限制每页数量
        per_page = min(per_page, 100)
        
        if search or resource_type or action:
            # 使用搜索功能
            # 处理可选参数，空字符串转换为None
            resource_type_param: Optional[str] = resource_type if resource_type else None
            action_param: Optional[str] = action if action else None
            
            permissions = PermissionService.search_permissions(
                keyword=search,
                resource_type=resource_type_param,
                action=action_param
            )
            
            # 手动分页
            total = len(permissions)
            start = (page - 1) * per_page
            end = start + per_page
            items = permissions[start:end]
            
            result = {
                'items': [p.to_dict() for p in items],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        else:
            # 使用分页查询
            result = PermissionService.get_all_permissions(page, per_page, search)
        
        return success_response(data=result, message='获取权限列表成功')
        
    except Exception as e:
        return error_response(message=f'获取权限列表失败: {str(e)}')


@bp.route('/<int:permission_id>', methods=['GET'])
@token_required
def get_permission(permission_id):
    """
    获取权限详情
    
    Args:
        permission_id: 权限ID
    """
    try:
        permission = PermissionService.get_permission_by_id(permission_id)
        if not permission:
            return error_response(message='权限不存在', code=404)
        
        return success_response(data=permission.to_dict(), message='获取权限详情成功')
        
    except Exception as e:
        return error_response(message=f'获取权限详情失败: {str(e)}')


@bp.route('', methods=['POST'])
@token_required
def create_permission():
    """
    创建权限
    
    Request Body:
        name (str): 权限名称
        code (str): 权限代码
        description (str): 权限描述
        resource_type (str): 资源类型
        resource_id (str): 资源标识
        action (str): 操作类型
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'code', 'resource_type', 'action']
        for field in required_fields:
            if not data.get(field):
                return error_response(message=f'缺少必填字段: {field}', code=400)
        
        # 创建权限
        permission = PermissionService.create_permission(data)
        
        return success_response(
            data=permission.to_dict(),
            message='权限创建成功',
            code=201
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'权限创建失败: {str(e)}')


@bp.route('/<int:permission_id>', methods=['PUT'])
@token_required
def update_permission(permission_id):
    """
    更新权限
    
    Args:
        permission_id: 权限ID
        
    Request Body:
        name (str): 权限名称
        code (str): 权限代码
        description (str): 权限描述
        resource_type (str): 资源类型
        resource_id (str): 资源标识
        action (str): 操作类型
    """
    try:
        data = request.get_json()
        
        # 更新权限
        permission = PermissionService.update_permission(permission_id, data)
        
        return success_response(
            data=permission.to_dict(),
            message='权限更新成功'
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'权限更新失败: {str(e)}')


@bp.route('/<int:permission_id>', methods=['DELETE'])
@token_required
def delete_permission(permission_id):
    """
    删除权限
    
    Args:
        permission_id: 权限ID
    """
    try:
        success = PermissionService.delete_permission(permission_id)
        
        if success:
            return success_response(message='权限删除成功')
        else:
            return error_response(message='权限删除失败')
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'权限删除失败: {str(e)}')


@bp.route('/batch', methods=['POST'])
@token_required
def batch_create_permissions():
    """
    批量创建权限
    
    Request Body:
        permissions (list): 权限数据列表
    """
    try:
        data = request.get_json()
        permissions_data = data.get('permissions', [])
        
        if not permissions_data:
            return error_response(message='权限数据不能为空', code=400)
        
        # 批量创建权限
        created_permissions = PermissionService.batch_create_permissions(permissions_data)
        
        return success_response(
            data={
                'created_count': len(created_permissions),
                'permissions': [p.to_dict() for p in created_permissions]
            },
            message=f'批量创建权限成功，共创建 {len(created_permissions)} 个权限',
            code=201
        )
        
    except Exception as e:
        return error_response(message=f'批量创建权限失败: {str(e)}')


@bp.route('/statistics', methods=['GET'])
@token_required
def get_permission_statistics():
    """
    获取权限统计信息
    """
    try:
        stats = PermissionService.get_permission_statistics()
        
        return success_response(
            data=stats,
            message='获取权限统计信息成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取权限统计信息失败: {str(e)}')


@bp.route('/resource-types', methods=['GET'])
@token_required
def get_resource_types():
    """
    获取资源类型列表
    """
    try:
        resource_types = [
            {'value': 'menu', 'label': '菜单'},
            {'value': 'api', 'label': 'API接口'},
            {'value': 'button', 'label': '按钮'}
        ]
        
        return success_response(
            data=resource_types,
            message='获取资源类型列表成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取资源类型列表失败: {str(e)}')


@bp.route('/actions', methods=['GET'])
@token_required
def get_actions():
    """
    获取操作类型列表
    """
    try:
        actions = [
            {'value': 'read', 'label': '查看'},
            {'value': 'write', 'label': '编辑'},
            {'value': 'delete', 'label': '删除'},
            {'value': 'execute', 'label': '执行'}
        ]
        
        return success_response(
            data=actions,
            message='获取操作类型列表成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取操作类型列表失败: {str(e)}')


@bp.route('/check', methods=['POST'])
@token_required
def check_permission():
    """
    检查用户权限
    
    Request Body:
        user_id (int): 用户ID，可选，默认为当前用户
        permission_code (str): 权限代码
        permission_codes (list): 权限代码列表
        require_all (bool): 是否需要全部权限，默认False
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', g.current_user.id)
        permission_code = data.get('permission_code')
        permission_codes = data.get('permission_codes', [])
        require_all = data.get('require_all', False)
        
        if permission_code:
            # 检查单个权限
            has_permission = PermissionService.check_user_permission(user_id, permission_code)
            result = {
                'user_id': user_id,
                'permission_code': permission_code,
                'has_permission': has_permission
            }
        elif permission_codes:
            # 检查多个权限
            has_permission = PermissionService.check_user_permissions(
                user_id, permission_codes, require_all
            )
            result = {
                'user_id': user_id,
                'permission_codes': permission_codes,
                'require_all': require_all,
                'has_permission': has_permission
            }
        else:
            return error_response(message='请提供权限代码', code=400)
        
        return success_response(
            data=result,
            message='权限检查完成'
        )
        
    except Exception as e:
        return error_response(message=f'权限检查失败: {str(e)}')


@bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_permissions(user_id):
    """
    获取用户的所有权限
    
    Args:
        user_id: 用户ID
    """
    try:
        permissions = PermissionService.get_user_permissions(user_id)
        
        return success_response(
            data={
                'user_id': user_id,
                'permissions': permissions
            },
            message='获取用户权限成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取用户权限失败: {str(e)}')


@bp.route('/role/<int:role_id>', methods=['GET'])
@token_required
def get_role_permissions(role_id):
    """
    获取角色的所有权限
    
    Args:
        role_id: 角色ID
    """
    try:
        permissions = PermissionService.get_role_permissions(role_id)
        
        return success_response(
            data={
                'role_id': role_id,
                'permissions': permissions
            },
            message='获取角色权限成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取角色权限失败: {str(e)}')