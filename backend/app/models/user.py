#!/usr/bin/env python3
"""
用户模型模块
定义User数据模型及相关功能
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from .user_role import user_role


class User(db.Model):
    """
    用户模型类
    对应数据库设计文档中的User表
    """
    __tablename__ = 'User'
    
    id = db.Column(db.Integer, primary_key=True, comment='用户唯一ID')
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(128), nullable=False, comment='密码（加密存储）')
    full_name = db.Column(db.String(100), comment='姓名')
    email = db.Column(db.String(120), comment='邮箱')
    phone = db.Column(db.String(20), comment='手机号')
    dispatch_unit_id = db.Column(db.Integer, db.ForeignKey('dispatch_units.id'), comment='所属派车单位ID')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    dispatch_unit = db.relationship('DispatchUnit', backref=db.backref('users', lazy=True))
    roles = db.relationship('Role', secondary=user_role, backref=db.backref('users', lazy=True))

    def set_password(self, password):
        """
        设置用户密码
        
        Args:
            password: 明文密码
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        验证用户密码
        
        Args:
            password: 明文密码
            
        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password, password)

    def to_dict(self):
        """
        将用户对象转换为字典格式
        
        Returns:
            dict: 用户信息字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name or self.username,  # 确保始终有显示名称
            'fullname': self.full_name or self.username,   # 兼容前端字段
            'email': self.email,
            'phone': self.phone,
            'dispatch_unit_id': self.dispatch_unit_id,
            'dispatch_unit': self.dispatch_unit.to_dict() if self.dispatch_unit else None,
            'is_active': self.is_active,
            'roles': [role.to_dict() for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_permissions(self):
        """
        获取用户的所有权限
        
        Returns:
            list: 权限对象列表
        """
        from .permission import Permission
        from .role_permission import RolePermission
        
        permissions = db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            user_role, RolePermission.role_id == user_role.c.role_id
        ).filter(
            user_role.c.user_id == self.id
        ).distinct().all()
        
        return permissions
    
    def get_permission_codes(self):
        """
        获取用户的所有权限代码
        
        Returns:
            list: 权限代码列表
        """
        permissions = self.get_permissions()
        return [p.code for p in permissions]
    
    def has_permission(self, permission_code):
        """
        检查用户是否具有指定权限
        
        Args:
            permission_code: 权限代码
            
        Returns:
            bool: 是否具有权限
        """
        permission_codes = self.get_permission_codes()
        return permission_code in permission_codes
    
    def has_any_permission(self, permission_codes):
        """
        检查用户是否具有任一指定权限
        
        Args:
            permission_codes: 权限代码列表
            
        Returns:
            bool: 是否具有任一权限
        """
        user_permissions = self.get_permission_codes()
        return any(code in user_permissions for code in permission_codes)
    
    def has_all_permissions(self, permission_codes):
        """
        检查用户是否具有所有指定权限
        
        Args:
            permission_codes: 权限代码列表
            
        Returns:
            bool: 是否具有所有权限
        """
        user_permissions = self.get_permission_codes()
        return all(code in user_permissions for code in permission_codes)
    
    def get_accessible_menus(self):
        """
        获取用户可访问的菜单列表
        
        Returns:
            list: 菜单对象列表
        """
        from .menu_permission import MenuPermission
        
        menus = MenuPermission.get_user_accessible_menus(self.id)
        return menus
    
    def can_access_menu(self, menu_code):
        """
        检查用户是否可以访问指定菜单
        
        Args:
            menu_code: 菜单代码
            
        Returns:
            bool: 是否可以访问
        """
        from .menu_permission import MenuPermission
        
        return MenuPermission.check_menu_access(self.id, menu_code)
    
    def has_role(self, role_name):
        """
        检查用户是否具有指定角色
        
        Args:
            role_name: 角色名称
            
        Returns:
            bool: 是否具有角色
        """
        return any(role.name == role_name for role in self.roles)
    
    def get_role_names(self):
        """
        获取用户的所有角色名称
        
        Returns:
            list: 角色名称列表
        """
        return [role.name for role in self.roles]
    
    def is_admin(self):
        """
        检查用户是否为管理员
        
        Returns:
            bool: 是否为管理员
        """
        return self.has_role('超级管理员')
    
    def to_dict_with_permissions(self):
        """
        将用户对象转换为包含权限信息的字典格式
        
        Returns:
            dict: 包含权限信息的用户字典
        """
        user_dict = self.to_dict()
        user_dict['permissions'] = self.get_permission_codes()
        user_dict['accessible_menus'] = [menu.code for menu in self.get_accessible_menus()]
        return user_dict
    
    def __repr__(self):
        """
        用户对象的字符串表示
        
        Returns:
            str: 用户信息字符串
        """
        return f'<User {self.username}>'