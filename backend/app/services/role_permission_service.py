# -*- coding: utf-8 -*-
"""
角色权限服务模块
提供角色权限分配和管理功能
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from ..extensions import db
from ..models import Role, Permission, RolePermission, User
from .permission_service import PermissionService


class RolePermissionService:
    """
    角色权限服务类
    """
    
    @staticmethod
    def assign_permission_to_role(role_id: int, permission_id: int, granted_by: Optional[int] = None) -> RolePermission:
        """
        为角色分配权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            granted_by: 授权人ID
            
        Returns:
            RolePermission: 角色权限关联对象
            
        Raises:
            ValueError: 当角色或权限不存在时
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 验证权限是否存在
        permission = Permission.query.get(permission_id)
        if not permission:
            raise ValueError(f"权限ID {permission_id} 不存在")
        
        # 分配权限
        role_permission = RolePermission.grant_permission(role_id, permission_id, granted_by)
        db.session.commit()
        
        return role_permission
    
    @staticmethod
    def revoke_permission_from_role(role_id: int, permission_id: int) -> bool:
        """
        撤销角色权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            
        Returns:
            bool: 是否撤销成功
            
        Raises:
            ValueError: 当角色不存在时
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 撤销权限
        success = RolePermission.revoke_permission(role_id, permission_id)
        if success:
            db.session.commit()
        
        return success
    
    @staticmethod
    def batch_assign_permissions_to_role(role_id: int, permission_ids: List[int], granted_by: Optional[int] = None) -> List[RolePermission]:
        """
        批量为角色分配权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            granted_by: 授权人ID
            
        Returns:
            list: 角色权限关联对象列表
            
        Raises:
            ValueError: 当角色不存在时
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 验证权限是否存在
        existing_permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        existing_permission_ids = [p.id for p in existing_permissions]
        
        invalid_ids = set(permission_ids) - set(existing_permission_ids)
        if invalid_ids:
            raise ValueError(f"权限ID {list(invalid_ids)} 不存在")
        
        # 批量分配权限
        role_permissions = RolePermission.batch_grant_permissions(role_id, permission_ids, granted_by)
        db.session.commit()
        
        return role_permissions
    
    @staticmethod
    def batch_revoke_permissions_from_role(role_id: int, permission_ids: Optional[List[int]] = None) -> int:
        """
        批量撤销角色权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表，如果为None则撤销所有权限
            
        Returns:
            int: 撤销的权限数量
            
        Raises:
            ValueError: 当角色不存在时
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 批量撤销权限
        count = RolePermission.batch_revoke_permissions(role_id, permission_ids)
        db.session.commit()
        
        return count
    
    @staticmethod
    def sync_role_permissions(role_id: int, permission_ids: List[int], granted_by: Optional[int] = None) -> List[RolePermission]:
        """
        同步角色权限（先清空再重新分配）
        
        Args:
            role_id: 角色ID
            permission_ids: 新的权限ID列表
            granted_by: 授权人ID
            
        Returns:
            list: 新创建的角色权限关联对象列表
            
        Raises:
            ValueError: 当角色不存在或权限不存在时
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 验证权限是否存在
        if permission_ids:
            existing_permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
            existing_permission_ids = [p.id for p in existing_permissions]
            
            invalid_ids = set(permission_ids) - set(existing_permission_ids)
            if invalid_ids:
                raise ValueError(f"权限ID {list(invalid_ids)} 不存在")
        
        # 同步权限
        role_permissions = RolePermission.sync_role_permissions(role_id, permission_ids, granted_by)
        db.session.commit()
        
        return role_permissions
    
    @staticmethod
    def get_role_permissions(role_id: int) -> List[Dict[str, Any]]:
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            list: 权限字典列表
        """
        return PermissionService.get_role_permissions(role_id)
    
    @staticmethod
    def get_role_permission_codes(role_id: int) -> List[str]:
        """
        获取角色的所有权限代码
        
        Args:
            role_id: 角色ID
            
        Returns:
            list: 权限代码列表
        """
        role = Role.query.get(role_id)
        if not role:
            return []
        
        return role.get_permission_codes()
    
    @staticmethod
    def check_role_permission(role_id: int, permission_code: str) -> bool:
        """
        检查角色是否具有指定权限
        
        Args:
            role_id: 角色ID
            permission_code: 权限代码
            
        Returns:
            bool: 是否具有权限
        """
        role = Role.query.get(role_id)
        if not role:
            return False
        
        return role.has_permission(permission_code)
    
    @staticmethod
    def get_permission_roles(permission_id: int) -> List[Dict[str, Any]]:
        """
        获取拥有指定权限的所有角色
        
        Args:
            permission_id: 权限ID
            
        Returns:
            list: 角色字典列表
        """
        roles = RolePermission.get_permission_roles(permission_id)
        return [role.to_dict() for role in roles]
    
    @staticmethod
    def copy_role_permissions(source_role_id: int, target_role_id: int, granted_by: Optional[int] = None) -> List[RolePermission]:
        """
        复制角色权限到另一个角色
        
        Args:
            source_role_id: 源角色ID
            target_role_id: 目标角色ID
            granted_by: 授权人ID
            
        Returns:
            list: 新创建的角色权限关联对象列表
            
        Raises:
            ValueError: 当角色不存在时
        """
        # 验证角色是否存在
        source_role = Role.query.get(source_role_id)
        if not source_role:
            raise ValueError(f"源角色ID {source_role_id} 不存在")
        
        target_role = Role.query.get(target_role_id)
        if not target_role:
            raise ValueError(f"目标角色ID {target_role_id} 不存在")
        
        # 获取源角色的权限
        source_permissions = source_role.get_permissions()
        permission_ids = [p.id for p in source_permissions]
        
        # 为目标角色分配权限
        role_permissions = RolePermissionService.batch_assign_permissions_to_role(
            target_role_id, permission_ids, granted_by
        )
        
        return role_permissions
    
    @staticmethod
    def get_role_permission_history(role_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        获取角色权限分配历史
        
        Args:
            role_id: 角色ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            dict: 包含权限分配历史和分页信息的字典
        """
        query = RolePermission.query.filter_by(role_id=role_id)
        
        pagination = query.order_by(RolePermission.granted_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'items': [rp.to_dict() for rp in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_user_roles_with_permissions(user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的角色及其权限信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 角色及权限信息列表
        """
        user = User.query.get(user_id)
        if not user:
            return []
        
        roles_with_permissions = []
        for role in user.roles:
            role_dict = role.to_dict()
            role_dict['permissions'] = [p.to_dict() for p in role.get_permissions()]
            role_dict['permission_codes'] = role.get_permission_codes()
            roles_with_permissions.append(role_dict)
        
        return roles_with_permissions
    
    @staticmethod
    def assign_role_to_user(user_id: int, role_id: int) -> bool:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            bool: 是否分配成功
            
        Raises:
            ValueError: 当用户或角色不存在时
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 检查用户是否已有此角色
        if role in user.roles:
            return True  # 已经有此角色，返回成功
        
        # 分配角色
        user.roles.append(role)
        db.session.commit()
        
        return True
    
    @staticmethod
    def revoke_role_from_user(user_id: int, role_id: int) -> bool:
        """
        撤销用户角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            bool: 是否撤销成功
            
        Raises:
            ValueError: 当用户或角色不存在时
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 检查用户是否有此角色
        if role not in user.roles:
            return True  # 没有此角色，返回成功
        
        # 撤销角色
        user.roles.remove(role)
        db.session.commit()
        
        return True
    
    @staticmethod
    def sync_user_roles(user_id: int, role_ids: List[int]) -> bool:
        """
        同步用户角色（先清空再重新分配）
        
        Args:
            user_id: 用户ID
            role_ids: 新的角色ID列表
            
        Returns:
            bool: 是否同步成功
            
        Raises:
            ValueError: 当用户不存在或角色不存在时
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        # 验证角色是否存在
        if role_ids:
            existing_roles = Role.query.filter(Role.id.in_(role_ids)).all()
            existing_role_ids = [r.id for r in existing_roles]
            
            invalid_ids = set(role_ids) - set(existing_role_ids)
            if invalid_ids:
                raise ValueError(f"角色ID {list(invalid_ids)} 不存在")
            
            # 同步角色
            user.roles = existing_roles
        else:
            # 清空所有角色
            user.roles = []
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_role_permission_statistics() -> Dict[str, Any]:
        """
        获取角色权限统计信息
        
        Returns:
            dict: 角色权限统计信息
        """
        # 总角色数
        total_roles = Role.query.count()
        
        # 有权限的角色数
        roles_with_permissions = db.session.query(RolePermission.role_id).distinct().count()
        
        # 权限分配总数
        total_assignments = RolePermission.query.count()
        
        # 每个角色的权限数量统计
        role_permission_counts = db.session.query(
            Role.name,
            db.func.count(RolePermission.permission_id).label('permission_count')
        ).outerjoin(
            RolePermission, Role.id == RolePermission.role_id
        ).group_by(Role.id, Role.name).all()
        
        # 最常分配的权限
        popular_permissions = db.session.query(
            Permission.name,
            Permission.code,
            db.func.count(RolePermission.role_id).label('role_count')
        ).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).group_by(
            Permission.id, Permission.name, Permission.code
        ).order_by(
            db.func.count(RolePermission.role_id).desc()
        ).limit(10).all()
        
        return {
            'total_roles': total_roles,
            'roles_with_permissions': roles_with_permissions,
            'roles_without_permissions': total_roles - roles_with_permissions,
            'total_assignments': total_assignments,
            'role_permission_counts': [
                {'role_name': item.name, 'permission_count': item.permission_count}
                for item in role_permission_counts
            ],
            'popular_permissions': [
                {
                    'permission_name': item.name,
                    'permission_code': item.code,
                    'role_count': item.role_count
                }
                for item in popular_permissions
            ]
        }
    
    @staticmethod
    def validate_role_permissions(role_id: int) -> Dict[str, Any]:
        """
        验证角色权限配置的合理性
        
        Args:
            role_id: 角色ID
            
        Returns:
            dict: 验证结果
        """
        role = Role.query.get(role_id)
        if not role:
            return {'valid': False, 'error': f'角色ID {role_id} 不存在'}
        
        permissions = role.get_permissions()
        
        # 检查权限配置
        issues = []
        warnings = []
        
        # 检查是否有基本的菜单访问权限
        menu_permissions = [p for p in permissions if p.resource_type == 'menu']
        if not menu_permissions:
            warnings.append('角色没有配置任何菜单访问权限')
        
        # 检查是否有API权限但没有对应的菜单权限
        api_permissions = [p for p in permissions if p.resource_type == 'api']
        menu_codes = [p.resource_id.split('/')[-1] for p in menu_permissions if p.resource_id]
        
        for api_perm in api_permissions:
            # 简单的启发式检查
            if 'user' in api_perm.code and 'menu:user_management' not in [p.code for p in permissions]:
                warnings.append(f'有用户相关API权限 {api_perm.code} 但缺少用户管理菜单权限')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'permission_count': len(permissions),
            'menu_permission_count': len(menu_permissions),
            'api_permission_count': len(api_permissions)
        }