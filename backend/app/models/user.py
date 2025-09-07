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
    company_id = db.Column(db.Integer, db.ForeignKey('Company.id'), comment='所属公司ID')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    company = db.relationship('Company', backref=db.backref('users', lazy=True))
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
            'company_id': self.company_id,
            'company': self.company.to_dict() if self.company else None,
            'roles': [role.to_dict() for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        用户对象的字符串表示
        
        Returns:
            str: 用户信息字符串
        """
        return f'<User {self.username}>'