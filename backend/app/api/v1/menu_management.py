# -*- coding: utf-8 -*-
"""
菜单管理API接口
提供菜单管理和权限菜单查询功能
"""

from flask import Blueprint, request, jsonify, g
from ...services.menu_service import MenuService
from ...services.permission_cache_service import PermissionCacheService
from ...common.response import success_response, error_response
from ...auth.decorators import token_required

# 创建蓝图
bp = Blueprint('menu_management', __name__, url_prefix='/menus')


@bp.route('', methods=['GET'])
@token_required
def get_menus():
    """
    获取菜单列表
    
    Query Parameters:
        include_inactive (bool): 是否包含未启用的菜单，默认False
        tree (bool): 是否返回树形结构，默认True
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        tree = request.args.get('tree', 'true').lower() == 'true'
        
        if tree:
            # 返回树形结构
            menu_tree = MenuService.get_menu_tree(include_inactive)
            return success_response(
                data=menu_tree,
                message='获取菜单树成功'
            )
        else:
            # 返回平铺列表
            menus = MenuService.get_all_menus(include_inactive)
            return success_response(
                data=[menu.to_dict() for menu in menus],
                message='获取菜单列表成功'
            )
        
    except Exception as e:
        return error_response(message=f'获取菜单列表失败: {str(e)}')


@bp.route('/<int:menu_id>', methods=['GET'])
@token_required
def get_menu(menu_id):
    """
    获取菜单详情
    
    Args:
        menu_id: 菜单ID
    """
    try:
        menu = MenuService.get_menu_by_id(menu_id)
        if not menu:
            return error_response(message='菜单不存在', code=404)
        
        return success_response(
            data=menu.to_dict(include_children=True),
            message='获取菜单详情成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取菜单详情失败: {str(e)}')


@bp.route('', methods=['POST'])
@token_required
def create_menu():
    """
    创建菜单
    
    Request Body:
        name (str): 菜单名称
        code (str): 菜单代码
        path (str): 路由路径
        component (str): 组件路径
        icon (str): 图标
        parent_id (int): 父菜单ID
        sort_order (int): 排序
        is_active (bool): 是否启用
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return error_response(message=f'缺少必填字段: {field}', code=400)
        
        # 创建菜单
        menu = MenuService.create_menu(data)
        
        # 清除菜单缓存
        PermissionCacheService.invalidate_menu_cache()
        
        return success_response(
            data=menu.to_dict(),
            message='菜单创建成功',
            code=201
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'菜单创建失败: {str(e)}')


@bp.route('/<int:menu_id>', methods=['PUT'])
@token_required
def update_menu(menu_id):
    """
    更新菜单
    
    Args:
        menu_id: 菜单ID
        
    Request Body:
        name (str): 菜单名称
        code (str): 菜单代码
        path (str): 路由路径
        component (str): 组件路径
        icon (str): 图标
        parent_id (int): 父菜单ID
        sort_order (int): 排序
        is_active (bool): 是否启用
    """
    try:
        data = request.get_json()
        
        # 更新菜单
        menu = MenuService.update_menu(menu_id, data)
        
        # 清除菜单缓存
        PermissionCacheService.invalidate_menu_cache()
        
        return success_response(
            data=menu.to_dict(),
            message='菜单更新成功'
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'菜单更新失败: {str(e)}')


@bp.route('/<int:menu_id>', methods=['DELETE'])
@token_required
def delete_menu(menu_id):
    """
    删除菜单
    
    Args:
        menu_id: 菜单ID
        
    Query Parameters:
        force (bool): 是否强制删除（包括子菜单），默认False
    """
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        
        success = MenuService.delete_menu(menu_id, force)
        
        if success:
            # 清除菜单缓存
            PermissionCacheService.invalidate_menu_cache()
            return success_response(message='菜单删除成功')
        else:
            return error_response(message='菜单删除失败')
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'菜单删除失败: {str(e)}')


@bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_menus(user_id):
    """
    获取用户可访问的菜单树
    
    Args:
        user_id: 用户ID
        
    Query Parameters:
        include_inactive (bool): 是否包含未启用的菜单，默认False
        use_cache (bool): 是否使用缓存，默认True
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        use_cache = request.args.get('use_cache', 'true').lower() == 'true'
        
        if use_cache:
            # 使用缓存服务
            menus = PermissionCacheService.get_user_menus(user_id, use_cache=True)
        else:
            # 直接查询
            menus = MenuService.get_user_menus(user_id, include_inactive)
        
        return success_response(
            data={
                'user_id': user_id,
                'menus': menus
            },
            message='获取用户菜单成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取用户菜单失败: {str(e)}')


@bp.route('/current-user', methods=['GET'])
@token_required
def get_current_user_menus():
    """
    获取当前用户可访问的菜单树
    
    Query Parameters:
        include_inactive (bool): 是否包含未启用的菜单，默认False
        use_cache (bool): 是否使用缓存，默认True
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        use_cache = request.args.get('use_cache', 'true').lower() == 'true'
        
        user_id = g.current_user.id
        
        if use_cache:
            # 使用缓存服务
            menus = PermissionCacheService.get_user_menus(user_id, use_cache=True)
        else:
            # 直接查询
            menus = MenuService.get_user_menus(user_id, include_inactive)
        
        return success_response(
            data=menus,
            message='获取当前用户菜单成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取当前用户菜单失败: {str(e)}')


@bp.route('/<int:menu_id>/permissions', methods=['GET'])
@token_required
def get_menu_permissions(menu_id):
    """
    获取菜单需要的权限列表
    
    Args:
        menu_id: 菜单ID
    """
    try:
        permissions = MenuService.get_menu_permissions(menu_id)
        
        return success_response(
            data={
                'menu_id': menu_id,
                'permissions': permissions
            },
            message='获取菜单权限成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取菜单权限失败: {str(e)}')


@bp.route('/<int:menu_id>/permissions', methods=['POST'])
@token_required
def bind_menu_permissions(menu_id):
    """
    为菜单绑定权限
    
    Args:
        menu_id: 菜单ID
        
    Request Body:
        permission_ids (list): 权限ID列表
    """
    try:
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        
        # 绑定菜单权限
        menu_permissions = MenuService.bind_menu_permissions(menu_id, permission_ids)
        
        # 清除菜单缓存
        PermissionCacheService.invalidate_menu_cache()
        
        return success_response(
            data={
                'menu_id': menu_id,
                'bound_permissions': len(menu_permissions)
            },
            message='菜单权限绑定成功'
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'菜单权限绑定失败: {str(e)}')


@bp.route('/roots', methods=['GET'])
@token_required
def get_root_menus():
    """
    获取根菜单列表
    
    Query Parameters:
        include_inactive (bool): 是否包含未启用的菜单，默认False
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        root_menus = MenuService.get_root_menus(include_inactive)
        
        return success_response(
            data=[menu.to_dict() for menu in root_menus],
            message='获取根菜单列表成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取根菜单列表失败: {str(e)}')


@bp.route('/<int:menu_id>/children', methods=['GET'])
@token_required
def get_menu_children(menu_id):
    """
    获取菜单的子菜单列表
    
    Args:
        menu_id: 菜单ID
        
    Query Parameters:
        include_inactive (bool): 是否包含未启用的菜单，默认False
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        children = MenuService.get_menu_children(menu_id, include_inactive)
        
        return success_response(
            data={
                'menu_id': menu_id,
                'children': [menu.to_dict() for menu in children]
            },
            message='获取子菜单列表成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取子菜单列表失败: {str(e)}')


@bp.route('/<int:menu_id>/move', methods=['POST'])
@token_required
def move_menu(menu_id):
    """
    移动菜单到新的父菜单下
    
    Args:
        menu_id: 菜单ID
        
    Request Body:
        new_parent_id (int): 新的父菜单ID，null表示移动到根级别
        new_sort_order (int): 新的排序值，可选
    """
    try:
        data = request.get_json()
        new_parent_id = data.get('new_parent_id')
        new_sort_order = data.get('new_sort_order')
        
        # 移动菜单
        menu = MenuService.move_menu(menu_id, new_parent_id, new_sort_order)
        
        # 清除菜单缓存
        PermissionCacheService.invalidate_menu_cache()
        
        return success_response(
            data=menu.to_dict(),
            message='菜单移动成功'
        )
        
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f'菜单移动失败: {str(e)}')


@bp.route('/batch-order', methods=['POST'])
@token_required
def batch_update_menu_order():
    """
    批量更新菜单排序
    
    Request Body:
        menu_orders (list): 菜单排序数据列表，格式：[{'id': menu_id, 'sort_order': order}, ...]
    """
    try:
        data = request.get_json()
        menu_orders = data.get('menu_orders', [])
        
        if not menu_orders:
            return error_response(message='菜单排序数据不能为空', code=400)
        
        # 批量更新排序
        success = MenuService.batch_update_menu_order(menu_orders)
        
        if success:
            # 清除菜单缓存
            PermissionCacheService.invalidate_menu_cache()
            return success_response(message='菜单排序更新成功')
        else:
            return error_response(message='菜单排序更新失败')
        
    except Exception as e:
        return error_response(message=f'菜单排序更新失败: {str(e)}')


@bp.route('/search', methods=['GET'])
@token_required
def search_menus():
    """
    搜索菜单
    
    Query Parameters:
        keyword (str): 搜索关键词
        include_inactive (bool): 是否包含未启用的菜单，默认False
    """
    try:
        keyword = request.args.get('keyword', '')
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        if not keyword:
            return error_response(message='搜索关键词不能为空', code=400)
        
        menus = MenuService.search_menus(keyword, include_inactive)
        
        return success_response(
            data=[menu.to_dict() for menu in menus],
            message='菜单搜索成功'
        )
        
    except Exception as e:
        return error_response(message=f'菜单搜索失败: {str(e)}')


@bp.route('/statistics', methods=['GET'])
@token_required
def get_menu_statistics():
    """
    获取菜单统计信息
    """
    try:
        stats = MenuService.get_menu_statistics()
        
        return success_response(
            data=stats,
            message='获取菜单统计信息成功'
        )
        
    except Exception as e:
        return error_response(message=f'获取菜单统计信息失败: {str(e)}')


@bp.route('/check-access', methods=['POST'])
@token_required
def check_menu_access():
    """
    检查用户菜单访问权限
    
    Request Body:
        user_id (int): 用户ID，可选，默认为当前用户
        menu_code (str): 菜单代码
        menu_codes (list): 菜单代码列表
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', g.current_user.id)
        menu_code = data.get('menu_code')
        menu_codes = data.get('menu_codes', [])
        
        if menu_code:
            # 检查单个菜单访问权限
            has_access = PermissionCacheService.check_user_menu_access(
                user_id, menu_code, use_cache=True
            )
            result = {
                'user_id': user_id,
                'menu_code': menu_code,
                'has_access': has_access
            }
        elif menu_codes:
            # 检查多个菜单访问权限
            access_results = {}
            for code in menu_codes:
                access_results[code] = PermissionCacheService.check_user_menu_access(
                    user_id, code, use_cache=True
                )
            
            result = {
                'user_id': user_id,
                'menu_codes': menu_codes,
                'access_results': access_results
            }
        else:
            return error_response(message='请提供菜单代码', code=400)
        
        return success_response(
            data=result,
            message='菜单访问权限检查完成'
        )
        
    except Exception as e:
        return error_response(message=f'菜单访问权限检查失败: {str(e)}')