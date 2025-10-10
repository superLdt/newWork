# -*- coding: utf-8 -*-
"""
角色权限配置API接口
提供角色权限分配和管理功能
"""

from flask import Blueprint, request, jsonify, g
from ...services.role_permission_service import RolePermissionService
from ...services.permission_cache_service import PermissionCacheService
from ...common.response import success_response, error_response
from ...auth.decorators import token_required

# 创建蓝图
bp = Blueprint('role_permission_management', __name__, url_prefix='/role-permissions')


@bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
@token_required
def get_role_permissions(role_id):
    """
    获取角色的所有权限
    
    Args:
        role_id: 角色ID
    """
    try:
        permissions = RolePermissionService.get_role_permissions(role_id)
        permission_codes = RolePermissionService.get_role_permission_codes(role_id)
        
        return success_response(
            data={
                'role_id': role_id,
                'permissions': permissions,
                'permission_codes': permission_codes
            },
            message='获取角色权限成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取角色权限失败: {str(e)}')


@bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
@token_required
def assign_permission_to_role(role_id):
    """
    为角色分配权限
    
    Args:
        role_id: 角色ID
        
    Request Body:
        permission_id (int): 权限ID
        permission_ids (list): 权限ID列表（批量分配）
    """
    try:
        data = request.get_json()
        permission_id = data.get('permission_id')
        permission_ids = data.get('permission_ids', [])
        granted_by = g.current_user.id
        
        if permission_id:
            # 单个权限分配
            role_permission = RolePermissionService.assign_permission_to_role(
                role_id, permission_id, granted_by
            )
            
            result = {
                'role_id': role_id,
                'permission_id': permission_id,
                'assigned': True
            }
            message = '权限分配成功'
            
        elif permission_ids:
            # 批量权限分配
            role_permissions = RolePermissionService.batch_assign_permissions_to_role(
                role_id, permission_ids, granted_by
            )
            
            result = {
                'role_id': role_id,
                'permission_ids': permission_ids,
                'assigned_count': len(role_permissions)
            }
            message = f'批量权限分配成功，共分配 {len(role_permissions)} 个权限'
            
        else:
            return error_response(message='请提供权限ID', code=400)
        
        # 清除角色缓存
        PermissionCacheService.invalidate_role_cache(role_id)
        
        return success_response(
            data=result,
            message=message,
            code=201
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'权限分配失败: {str(e)}')


@bp.route('/roles/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@token_required
def revoke_permission_from_role(role_id, permission_id):
    """
    撤销角色权限
    
    Args:
        role_id: 角色ID
        permission_id: 权限ID
    """
    try:
        success = RolePermissionService.revoke_permission_from_role(role_id, permission_id)
        
        if success:
            # 清除角色缓存
            PermissionCacheService.invalidate_role_cache(role_id)
            
            return success_response(
                data={
                    'role_id': role_id,
                    'permission_id': permission_id,
                    'revoked': True
                },
                message='权限撤销成功'
            )
        else:
            return error_response(message='权限撤销失败')
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'权限撤销失败: {str(e)}')


@bp.route('/roles/<int:role_id>/permissions/batch-revoke', methods=['POST'])
@token_required
def batch_revoke_permissions_from_role(role_id):
    """
    批量撤销角色权限
    
    Args:
        role_id: 角色ID
        
    Request Body:
        permission_ids (list): 权限ID列表，如果为空则撤销所有权限
    """
    try:
        data = request.get_json()
        permission_ids = data.get('permission_ids')
        
        count = RolePermissionService.batch_revoke_permissions_from_role(
            role_id, permission_ids
        )
        
        # 清除角色缓存
        PermissionCacheService.invalidate_role_cache(role_id)
        
        return success_response(
            data={
                'role_id': role_id,
                'revoked_count': count
            },
            message=f'批量权限撤销成功，共撤销 {count} 个权限'
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'批量权限撤销失败: {str(e)}')


@bp.route('/roles/<int:role_id>/permissions', methods=['PUT'])
@token_required
def update_role_permissions(role_id):
    """
    更新（同步）角色权限
    - 该接口与前端 PUT /role-permissions/roles/:role_id/permissions 对齐
    - 行为等同于“同步”：先清空再按传入的 permission_ids 重新分配，确保幂等

    Request Body:
        permission_ids (list[int]): 新的权限ID列表
    """
    try:
        data = request.get_json() or {}
        permission_ids = data.get('permission_ids', [])
        granted_by = g.current_user.id

        role_permissions = RolePermissionService.sync_role_permissions(
            role_id, permission_ids, granted_by
        )

        # 清除角色缓存
        PermissionCacheService.invalidate_role_cache(role_id)

        return success_response(
            data={
                'role_id': role_id,
                'synced_count': len(role_permissions),
                'permission_ids': permission_ids
            },
            message=f'角色权限更新成功，共配置 {len(role_permissions)} 个权限'
        )

    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'角色权限更新失败: {str(e)}')


@bp.route('/permissions/<int:permission_id>/roles', methods=['GET'])
@token_required
def get_permission_roles(permission_id):
    """
    获取拥有指定权限的所有角色
    
    Args:
        permission_id: 权限ID
    """
    try:
        roles = RolePermissionService.get_permission_roles(permission_id)
        
        return success_response(
            data={
                'permission_id': permission_id,
                'roles': roles
            },
            message='获取权限角色成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取权限角色失败: {str(e)}')


@bp.route('/roles/<int:source_role_id>/copy-to/<int:target_role_id>', methods=['POST'])
@token_required
def copy_role_permissions(source_role_id, target_role_id):
    """
    复制角色权限到另一个角色
    
    Args:
        source_role_id: 源角色ID
        target_role_id: 目标角色ID
    """
    try:
        granted_by = g.current_user.id
        
        role_permissions = RolePermissionService.copy_role_permissions(
            source_role_id, target_role_id, granted_by
        )
        
        # 清除目标角色缓存
        PermissionCacheService.invalidate_role_cache(target_role_id)
        
        return success_response(
            data={
                'source_role_id': source_role_id,
                'target_role_id': target_role_id,
                'copied_count': len(role_permissions)
            },
            message=f'角色权限复制成功，共复制 {len(role_permissions)} 个权限'
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'角色权限复制失败: {str(e)}')


@bp.route('/roles/<int:role_id>/permissions/history', methods=['GET'])
@token_required
def get_role_permission_history(role_id):
    """
    获取角色权限分配历史
    
    Args:
        role_id: 角色ID
        
    Query Parameters:
        page (int): 页码，默认1
        per_page (int): 每页数量，默认20
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 限制每页数量
        per_page = min(per_page, 100)
        
        result = RolePermissionService.get_role_permission_history(
            role_id, page, per_page
        )
        
        return success_response(
            data=result,
            message='获取角色权限历史成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取角色权限历史失败: {str(e)}')


@bp.route('/users/<int:user_id>/roles', methods=['GET'])
@token_required
def get_user_roles_with_permissions(user_id):
    """
    获取用户的角色及其权限信息
    
    Args:
        user_id: 用户ID
    """
    try:
        roles_with_permissions = RolePermissionService.get_user_roles_with_permissions(user_id)
        
        return success_response(
            data={
                'user_id': user_id,
                'roles': roles_with_permissions
            },
            message='获取用户角色权限成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取用户角色权限失败: {str(e)}')


@bp.route('/users/<int:user_id>/roles', methods=['POST'])
@token_required
def assign_role_to_user(user_id):
    """
    为用户分配角色
    
    Args:
        user_id: 用户ID
        
    Request Body:
        role_id (int): 角色ID
        role_ids (list): 角色ID列表（批量分配或同步）
        sync (bool): 是否同步模式（先清空再分配），默认False
    """
    try:
        data = request.get_json()
        role_id = data.get('role_id')
        role_ids = data.get('role_ids', [])
        sync = data.get('sync', False)
        
        if sync and role_ids is not None:
            # 同步用户角色
            success = RolePermissionService.sync_user_roles(user_id, role_ids)
            
            # 清除用户缓存
            PermissionCacheService.invalidate_user_cache(user_id)
            
            return success_response(
                data={
                    'user_id': user_id,
                    'role_ids': role_ids,
                    'synced': success
                },
                message=f'用户角色同步成功，共配置 {len(role_ids)} 个角色'
            )
            
        elif role_id:
            # 单个角色分配
            success = RolePermissionService.assign_role_to_user(user_id, role_id)
            
            # 清除用户缓存
            PermissionCacheService.invalidate_user_cache(user_id)
            
            return success_response(
                data={
                    'user_id': user_id,
                    'role_id': role_id,
                    'assigned': success
                },
                message='用户角色分配成功',
                code=201
            )
            
        else:
            return error_response(message='请提供角色ID', code=400)
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'用户角色分配失败: {str(e)}')


@bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@token_required
def revoke_role_from_user(user_id, role_id):
    """
    撤销用户角色
    
    Args:
        user_id: 用户ID
        role_id: 角色ID
    """
    try:
        success = RolePermissionService.revoke_role_from_user(user_id, role_id)
        
        if success:
            # 清除用户缓存
            PermissionCacheService.invalidate_user_cache(user_id)
            
            return success_response(
                data={
                    'user_id': user_id,
                    'role_id': role_id,
                    'revoked': True
                },
                message='用户角色撤销成功'
            )
        else:
            return error_response(message='用户角色撤销失败')
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'用户角色撤销失败: {str(e)}')


@bp.route('/roles/<int:role_id>/check', methods=['POST'])
@token_required
def check_role_permission(role_id):
    """
    检查角色是否具有指定权限
    
    Args:
        role_id: 角色ID
        
    Request Body:
        permission_code (str): 权限代码
    """
    try:
        data = request.get_json()
        permission_code = data.get('permission_code')
        
        if not permission_code:
            return error_response(message='请提供权限代码', code=400)
        
        has_permission = RolePermissionService.check_role_permission(role_id, permission_code)
        
        return success_response(
            data={
                'role_id': role_id,
                'permission_code': permission_code,
                'has_permission': has_permission
            },
            message='角色权限检查完成'
        )
        
    except Exception as e:
        return error_response(message=f'角色权限检查失败: {str(e)}')


@bp.route('/statistics', methods=['GET'])
@token_required
def get_role_permission_statistics():
    """
    获取角色权限统计信息
    """
    try:
        stats = RolePermissionService.get_role_permission_statistics()
        
        return success_response(
            data=stats,
            message='获取角色权限统计信息成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取角色权限统计信息失败: {str(e)}')


@bp.route('/roles/<int:role_id>/validate', methods=['GET'])
@token_required
def validate_role_permissions(role_id):
    """
    验证角色权限配置的合理性
    
    Args:
        role_id: 角色ID
    """
    try:
        validation_result = RolePermissionService.validate_role_permissions(role_id)
        
        return success_response(
            data=validation_result,
            message='角色权限验证完成'
        )
        
    except Exception as e:
        return error_response(message=f'角色权限验证失败: {str(e)}')