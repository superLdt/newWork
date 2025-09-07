"""
认证服务层
处理用户认证相关业务逻辑
"""

from datetime import datetime, timedelta
import jwt
from flask import current_app
from ..models.user import User
from ..extensions import db
from ..utils.exceptions import AuthenticationError, ValidationError


class AuthService:
    """认证业务服务类"""
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """
        用户登录认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            dict: 包含用户信息和token的字典
            
        Raises:
            AuthenticationError: 认证失败时抛出
        """
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            raise AuthenticationError("用户名或密码错误")
            
        if not user.is_active:
            raise AuthenticationError("用户已被禁用")
            
        # 生成JWT token
        token = AuthService._generate_token(user)
        
        return {
            'user': user.to_dict(),
            'token': token,
            'expires_in': 3600  # 1小时有效期
        }
    
    @staticmethod
    def get_user_by_token(token: str) -> User:
        """
        通过token获取用户信息
        
        Args:
            token: JWT token
            
        Returns:
            User: 用户对象
            
        Raises:
            AuthenticationError: token无效时抛出
        """
        try:
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            
            if not user_id:
                raise AuthenticationError("无效的token")
                
            user = User.query.get(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("用户不存在或已被禁用")
                
            return user
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("token已过期")
        except jwt.InvalidTokenError:
            raise AuthenticationError("无效的token")
    
    @staticmethod
    def _generate_token(user: User) -> str:
        """生成JWT token"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(
            payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )