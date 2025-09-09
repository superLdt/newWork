"""
角色服务层
处理角色管理相关业务逻辑
"""

from sqlalchemy.exc import IntegrityError
from ..models.role import Role
from ..models.user import User
from ..models.user_role import user_role
from ..models.menu import Menu
from ..models.permission import Permission
from ..models.role_permission import RolePermission
from ..models.menu_permission import MenuPermission
from ..extensions import db
from ..utils.exceptions import ValidationError, ResourceNotFoundError


class RoleService:
    """角色业务服务类"""
    
    @staticmethod
    def get_role_by_id(role_id: int) -> dict:
        """
        根据ID获取角色信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            dict: 角色信息
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
        """
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        return role.to_dict()
    
    @staticmethod
    def get_role_by_name(name: str) -> dict:
        """
        根据名称获取角色信息
        
        Args:
            name: 角色名称
            
        Returns:
            dict: 角色信息
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
        """
        role = Role.query.filter_by(name=name).first()
        if not role:
            raise ResourceNotFoundError(f"角色名称 {name} 不存在")
        return role.to_dict()
    
    @staticmethod
    def create_role(role_data: dict) -> dict:
        """
        创建新角色
        
        Args:
            role_data: 角色数据字典
            
        Returns:
            dict: 创建的角色信息
            
        Raises:
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证必填字段
            required_fields = ['name']
            for field in required_fields:
                if not role_data.get(field):
                    raise ValidationError(f"缺少必填字段: {field}")
            
            # 检查角色名称唯一性
            if Role.query.filter_by(name=role_data['name']).first():
                raise ValidationError(f"角色名称 {role_data['name']} 已存在")
            
            role = Role(
                name=role_data['name'],
                description=role_data.get('description', '')
            )
            
            db.session.add(role)
            db.session.commit()
            
            return role.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationError(f"创建角色失败: {str(e)}")
    
    @staticmethod
    def update_role(role_id: int, update_data: dict) -> dict:
        """
        更新角色信息
        
        Args:
            role_id: 角色ID
            update_data: 更新数据字典
            
        Returns:
            dict: 更新后的角色信息
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
            ValidationError: 数据验证失败时抛出
        """
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        try:
            # 不允许更新角色名称（唯一性约束）
            update_data.pop('name', None)
            
            # 更新其他字段
            for key, value in update_data.items():
                if hasattr(role, key):
                    setattr(role, key, value)
            
            db.session.commit()
            return role.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationError(f"更新角色失败: {str(e)}")
    
    @staticmethod
    def delete_role(role_id: int) -> None:
        """
        删除角色
        
        Args:
            role_id: 角色ID
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
            ValidationError: 角色有关联用户时抛出
        """
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        # 检查是否有关联的用户
        user_count = db.session.query(user_role).filter_by(role_id=role_id).count()
        if user_count > 0:
            raise ValidationError(f"角色 {role.name} 下有关联用户，无法删除")
        
        db.session.delete(role)
        db.session.commit()
    
    @staticmethod
    def list_roles() -> list:
        """
        获取角色列表
        
        Returns:
            list: 角色列表
        """
        roles = Role.query.all()
        return [role.to_dict() for role in roles]
    
    @staticmethod
    def assign_role_to_user(user_id: int, role_id: int) -> None:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Raises:
            ResourceNotFoundError: 用户或角色不存在时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
            
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        # 检查是否已分配该角色
        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()
    
    @staticmethod
    def remove_role_from_user(user_id: int, role_id: int) -> None:
        """
        移除用户的角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Raises:
            ResourceNotFoundError: 用户或角色不存在时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
            
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        # 检查是否已分配该角色
        if role in user.roles:
            user.roles.remove(role)
            db.session.commit()
    
    @staticmethod
    def get_user_roles(user_id: int) -> list:
        """
        获取指定用户的所有角色

        Args:
            user_id: 用户ID

        Returns:
            list: 角色列表

        Raises:
            ResourceNotFoundError: 用户不存在时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
        return [role.to_dict() for role in user.roles]
    
    @staticmethod
    def get_role_user_count(role_id: int) -> int:
        """
        获取角色的用户数
        
        Args:
            role_id: 角色ID
            
        Returns:
            int: 用户数
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
        """
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        return len(role.users)

    @staticmethod
    def list_roles_with_user_count() -> list:
        """
        获取角色列表，并为每个角色添加用户数统计
        
        Returns:
            list: 包含用户数统计的角色列表
        """
        roles = Role.query.all()
        roles_with_count = []
        
        for role in roles:
            role_dict = role.to_dict()
            # 获取角色的用户数
            role_dict['user_count'] = len(role.users)
            roles_with_count.append(role_dict)
        
        return roles_with_count

    @staticmethod
    def get_role_menus(role_id: int) -> list:
        """
        获取角色的菜单权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            list: 角色可访问的菜单列表
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        # 获取角色的权限
        role_permissions = db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.role_id == role_id
        ).all()
        
        permission_ids = [p.id for p in role_permissions]
        
        # 获取这些权限对应的菜单
        accessible_menus = []
        if permission_ids:
            # 查询菜单权限关联表，找到权限对应的菜单
            menu_permissions = db.session.query(MenuPermission).filter(
                MenuPermission.permission_id.in_(permission_ids)
            ).all()
            
            menu_ids = list(set([mp.menu_id for mp in menu_permissions]))
            
            if menu_ids:
                menus = db.session.query(Menu).filter(
                    Menu.id.in_(menu_ids),
                    Menu.is_active == True
                ).all()
                accessible_menus = [menu.to_dict() for menu in menus]
        
        return accessible_menus
    
    @staticmethod
    def update_role_menus(role_id: int, menu_ids: list) -> None:
        """
        更新角色的菜单权限
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            
        Raises:
            ResourceNotFoundError: 角色不存在时抛出
            ValidationError: 菜单ID无效时抛出
        """
        # 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFoundError(f"角色ID {role_id} 不存在")
        
        # 验证菜单是否存在
        if menu_ids:
            existing_menus = db.session.query(Menu).filter(
                Menu.id.in_(menu_ids)
            ).all()
            existing_menu_ids = [m.id for m in existing_menus]
            
            invalid_ids = set(menu_ids) - set(existing_menu_ids)
            if invalid_ids:
                raise ValidationError(f"菜单ID {list(invalid_ids)} 不存在")
        
        # 获取菜单对应的权限
        permission_ids = []
        if menu_ids:
            menu_permissions = db.session.query(MenuPermission).filter(
                MenuPermission.menu_id.in_(menu_ids)
            ).all()
            permission_ids = list(set([mp.permission_id for mp in menu_permissions]))
        
        # 同步角色权限
        from .role_permission_service import RolePermissionService
        RolePermissionService.sync_role_permissions(role_id, permission_ids)
        
        return None
