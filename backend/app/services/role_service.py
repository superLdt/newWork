"""
角色服务层
处理角色管理相关业务逻辑
"""

from sqlalchemy.exc import IntegrityError
from ..models.role import Role
from ..models.user import User
from ..models.user_role import user_role
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
        获取用户的所有角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 用户角色列表
            
        Raises:
            ResourceNotFoundError: 用户不存在时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
        
        return [role.to_dict() for role in user.roles]