"""
用户服务层
处理用户管理相关业务逻辑
"""

from sqlalchemy.exc import IntegrityError
from ..models.user import User
from ..extensions import db
from ..utils.exceptions import ValidationError, ResourceNotFoundError


class UserService:
    """用户业务服务类"""
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 用户信息
            
        Raises:
            ResourceNotFoundError: 用户不存在时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
        return user.to_dict()
    
    @staticmethod
    def get_user_by_username(username: str) -> dict:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            dict: 用户信息
            
        Raises:
            ResourceNotFoundError: 用户不存在时抛出
        """
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ResourceNotFoundError(f"用户名 {username} 不存在")
        return user.to_dict()
    
    @staticmethod
    def create_user(user_data: dict) -> dict:
        """
        创建新用户
        
        Args:
            user_data: 用户数据字典
            
        Returns:
            dict: 创建的用户信息
            
        Raises:
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证必填字段
            required_fields = ['username', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    raise ValidationError(f"缺少必填字段: {field}")
            
            # 检查用户名唯一性
            if User.query.filter_by(username=user_data['username']).first():
                raise ValidationError(f"用户名 {user_data['username']} 已存在")
            
            user = User(
                username=user_data['username'],
                full_name=user_data.get('full_name', ''),
                email=user_data.get('email', ''),
                phone=user_data.get('phone', ''),
                company_id=user_data.get('company_id')
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return user.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationError(f"创建用户失败: {str(e)}")
    
    @staticmethod
    def update_user(user_id: int, update_data: dict) -> dict:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            update_data: 更新数据字典
            
        Returns:
            dict: 更新后的用户信息
            
        Raises:
            ResourceNotFoundError: 用户不存在时抛出
            ValidationError: 数据验证失败时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
        
        try:
            # 不允许更新用户名
            update_data.pop('username', None)
            
            # 如果更新密码
            if 'password' in update_data:
                user.set_password(update_data.pop('password'))
            
            # 更新其他字段
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.session.commit()
            return user.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationError(f"更新用户失败: {str(e)}")
    
    @staticmethod
    def delete_user(user_id: int) -> None:
        """
        删除用户（软删除）
        
        Args:
            user_id: 用户ID
            
        Raises:
            ResourceNotFoundError: 用户不存在时抛出
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"用户ID {user_id} 不存在")
        
        user.is_active = False
        db.session.commit()
    
    @staticmethod
    def list_users(page: int = 1, per_page: int = 20) -> dict:
        """
        获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
            
        Returns:
            dict: 分页用户列表数据
        """
        pagination = User.query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'items': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }