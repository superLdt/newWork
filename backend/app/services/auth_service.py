"""
认证服务层
处理用户认证相关业务逻辑
"""

from datetime import timedelta
from flask import current_app
from flask_jwt_extended import create_access_token
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
            
        # 使用 Flask-JWT-Extended 生成兼容 @jwt_required 的访问令牌
        # 获取用户角色、权限和菜单信息
        roles = [r.name for r in user.roles]
        permissions = user.get_permission_codes()
        accessible_menus = [menu.code for menu in user.get_accessible_menus()]
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'full_name': user.full_name,
                'roles': roles,
                'permissions': permissions,
                'accessible_menus': accessible_menus,
                'is_admin': user.is_admin()
            }
        )
        
        # 读取配置的过期时间（单位秒）
        expires_cfg = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        if isinstance(expires_cfg, timedelta):
            expires_in = int(expires_cfg.total_seconds())
        else:
            # 兼容直接配置为秒数或未配置的情况，默认1小时
            try:
                expires_in = int(expires_cfg) if expires_cfg is not None else 3600
            except Exception:
                expires_in = 3600
        
        return {
            'user': user.to_dict(),
            'token': access_token,
            'expires_in': expires_in
        }

# 说明：
# 1) 旧的基于 PyJWT 的 get_user_by_token 与 _generate_token 已移除，统一由 Flask-JWT-Extended 托管。
# 2) 解析 token 的职责交由路由层使用 @jwt_required 和 get_jwt_identity 完成，服务层只负责签发 token。