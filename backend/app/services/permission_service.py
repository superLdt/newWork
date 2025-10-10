# -*- coding: utf-8 -*-
"""
权限管理服务模块
提供权限的CRUD操作和权限验证功能
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from ..extensions import db
from ..models import Permission, User, Role, RolePermission


class PermissionService:
    """
    权限管理服务类
    """
    
    @staticmethod
    def get_all_permissions(page: int = 1, per_page: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """
        获取权限列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            
        Returns:
            dict: 包含权限列表和分页信息的字典
        """
        query = Permission.query
        
        # 搜索过滤
        if search:
            search_filter = or_(
                Permission.name.contains(search),
                Permission.code.contains(search),
                Permission.description.contains(search)
            )
            query = query.filter(search_filter)
        
        # 分页查询
        pagination = query.order_by(Permission.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'items': [permission.to_dict() for permission in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_permission_by_id(permission_id: int) -> Optional[Permission]:
        """
        根据ID获取权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            Permission: 权限对象，如果不存在则返回None
        """
        return Permission.query.get(permission_id)
    
    @staticmethod
    def get_permission_by_code(code: str) -> Optional[Permission]:
        """
        根据权限代码获取权限
        
        Args:
            code: 权限代码
            
        Returns:
            Permission: 权限对象，如果不存在则返回None
        """
        return Permission.query.filter_by(code=code).first()
    
    @staticmethod
    def create_permission(data: Dict[str, Any]) -> Permission:
        """
        创建权限
        
        Args:
            data: 权限数据字典
            
        Returns:
            Permission: 创建的权限对象
            
        Raises:
            ValueError: 当权限代码已存在时
        """
        # 检查权限代码是否已存在
        existing = Permission.query.filter_by(code=data['code']).first()
        if existing:
            raise ValueError(f"权限代码 '{data['code']}' 已存在")
        
        permission = Permission(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            resource_type=data['resource_type'],
            resource_id=data.get('resource_id', ''),
            action=data['action']
        )
        
        db.session.add(permission)
        db.session.commit()
        
        return permission
    
    @staticmethod
    def update_permission(permission_id: int, data: Dict[str, Any]) -> Permission:
        """
        更新权限
        
        Args:
            permission_id: 权限ID
            data: 更新数据字典
            
        Returns:
            Permission: 更新后的权限对象
            
        Raises:
            ValueError: 当权限不存在或权限代码冲突时
        """
        permission = Permission.query.get(permission_id)
        if not permission:
            raise ValueError(f"权限ID {permission_id} 不存在")
        
        # 检查权限代码是否冲突
        if 'code' in data and data['code'] != permission.code:
            existing = Permission.query.filter_by(code=data['code']).first()
            if existing:
                raise ValueError(f"权限代码 '{data['code']}' 已存在")
        
        # 更新字段
        for field in ['name', 'code', 'description', 'resource_type', 'resource_id', 'action']:
            if field in data:
                setattr(permission, field, data[field])
        
        db.session.commit()
        
        return permission
    
    @staticmethod
    def delete_permission(permission_id: int) -> bool:
        """
        删除权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            ValueError: 当权限不存在或权限正在使用时
        """
        permission = Permission.query.get(permission_id)
        if not permission:
            raise ValueError(f"权限ID {permission_id} 不存在")
        
        # 检查权限是否正在使用
        role_count = RolePermission.query.filter_by(permission_id=permission_id).count()
        if role_count > 0:
            raise ValueError(f"权限 '{permission.name}' 正在被 {role_count} 个角色使用，无法删除")
        
        db.session.delete(permission)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_permissions_by_resource_type(resource_type: str) -> List[Permission]:
        """
        根据资源类型获取权限列表
        
        Args:
            resource_type: 资源类型（menu, api, button）
            
        Returns:
            list: 权限对象列表
        """
        return Permission.query.filter_by(resource_type=resource_type).all()
    
    @staticmethod
    def check_user_permission(user_id: int, permission_code: str) -> bool:
        """
        检查用户是否具有指定权限
        
        Args:
            user_id: 用户ID
            permission_code: 权限代码
            
        Returns:
            bool: 是否具有权限
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return False
        
        return user.has_permission(permission_code)
    
    @staticmethod
    def check_user_permissions(user_id: int, permission_codes: List[str], require_all: bool = False) -> bool:
        """
        检查用户是否具有指定权限列表
        
        Args:
            user_id: 用户ID
            permission_codes: 权限代码列表
            require_all: 是否需要全部权限（True）还是任一权限（False）
            
        Returns:
            bool: 是否具有权限
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return False
        
        if require_all:
            return user.has_all_permissions(permission_codes)
        else:
            return user.has_any_permission(permission_codes)
    
    @staticmethod
    def get_user_permissions(user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的所有权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 权限字典列表
        """
        user = User.query.get(user_id)
        if not user:
            return []
        
        permissions = user.get_permissions()
        return [permission.to_dict() for permission in permissions]
    
    @staticmethod
    def get_role_permissions(role_id: int) -> List[Dict[str, Any]]:
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            list: 权限字典列表
        """
        role = Role.query.get(role_id)
        if not role:
            return []
        
        permissions = role.get_permissions()
        return [permission.to_dict() for permission in permissions]
    
    @staticmethod
    def batch_create_permissions(permissions_data: List[Dict[str, Any]]) -> List[Permission]:
        """
        批量创建权限
        
        Args:
            permissions_data: 权限数据列表
            
        Returns:
            list: 创建的权限对象列表
        """
        created_permissions = []
        
        for data in permissions_data:
            # 检查权限代码是否已存在
            existing = Permission.query.filter_by(code=data['code']).first()
            if existing:
                continue  # 跳过已存在的权限
            
            permission = Permission(
                name=data['name'],
                code=data['code'],
                description=data.get('description', ''),
                resource_type=data['resource_type'],
                resource_id=data.get('resource_id', ''),
                action=data['action']
            )
            
            db.session.add(permission)
            created_permissions.append(permission)
        
        db.session.commit()
        
        return created_permissions
    
    @staticmethod
    def get_permission_statistics() -> Dict[str, Any]:
        """
        获取权限统计信息
        
        Returns:
            dict: 权限统计信息
        """
        total_permissions = Permission.query.count()
        
        # 按资源类型统计
        resource_type_stats = db.session.query(
            Permission.resource_type,
            db.func.count(Permission.id).label('count')
        ).group_by(Permission.resource_type).all()
        
        # 按操作类型统计
        action_stats = db.session.query(
            Permission.action,
            db.func.count(Permission.id).label('count')
        ).group_by(Permission.action).all()
        
        # 使用中的权限数量
        used_permissions = db.session.query(
            Permission.id
        ).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).distinct().count()
        
        return {
            'total_permissions': total_permissions,
            'used_permissions': used_permissions,
            'unused_permissions': total_permissions - used_permissions,
            'resource_type_stats': {
                item.resource_type: item.count for item in resource_type_stats
            },
            'action_stats': {
                item.action: item.count for item in action_stats
            }
        }
    
    @staticmethod
    def search_permissions(keyword: str, resource_type: Optional[str] = None, action: Optional[str] = None) -> List[Permission]:
        """
        搜索权限
        
        Args:
            keyword: 搜索关键词
            resource_type: 资源类型过滤
            action: 操作类型过滤
            
        Returns:
            list: 权限对象列表
        """
        query = Permission.query
        
        # 关键词搜索
        if keyword:
            search_filter = or_(
                Permission.name.contains(keyword),
                Permission.code.contains(keyword),
                Permission.description.contains(keyword)
            )
            query = query.filter(search_filter)
        
        # 资源类型过滤
        if resource_type:
            query = query.filter(Permission.resource_type == resource_type)
        
        # 操作类型过滤
        if action:
            query = query.filter(Permission.action == action)
        
        return query.order_by(Permission.name.asc()).all()
