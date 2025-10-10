# -*- coding: utf-8 -*-
"""
角色权限关联模型模块
定义角色与权限的多对多关系
"""

from datetime import datetime
from ..extensions import db


class RolePermission(db.Model):
    """
    角色权限关联模型类
    记录角色权限分配的详细信息，包括授权人和授权时间
    """
    __tablename__ = 'RolePermission'
    
    id = db.Column(db.Integer, primary_key=True, comment='关联记录唯一ID')
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id', ondelete='CASCADE'), nullable=False, comment='角色ID')
    permission_id = db.Column(db.Integer, db.ForeignKey('Permission.id', ondelete='CASCADE'), nullable=False, comment='权限ID')
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, comment='授权时间')
    granted_by = db.Column(db.Integer, db.ForeignKey('User.id'), comment='授权人ID')
    
    # 关系定义
    role = db.relationship('Role', backref=db.backref('role_permissions', lazy=True, cascade='all, delete-orphan'))
    permission = db.relationship('Permission', backref=db.backref('role_permissions', lazy=True))
    granted_by_user = db.relationship('User', foreign_keys=[granted_by])
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
    )
    
    def __repr__(self):
        return f'<RolePermission role_id={self.role_id} permission_id={self.permission_id}>'
    
    def to_dict(self):
        """
        将角色权限关联对象转换为字典格式
        
        Returns:
            dict: 包含关联信息的字典
        """
        return {
            'id': self.id,
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'granted_by': self.granted_by,
            'role': self.role.to_dict() if self.role else None,
            'permission': self.permission.to_dict() if self.permission else None,
            'granted_by_user': {
                'id': self.granted_by_user.id,
                'username': self.granted_by_user.username,
                'full_name': self.granted_by_user.full_name
            } if self.granted_by_user else None
        }
    
    @classmethod
    def grant_permission(cls, role_id, permission_id, granted_by=None):
        """
        为角色授予权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            granted_by: 授权人ID
            
        Returns:
            RolePermission: 创建的角色权限关联对象
        """
        # 检查是否已存在
        existing = cls.query.filter_by(
            role_id=role_id,
            permission_id=permission_id
        ).first()
        
        if existing:
            return existing
        
        role_permission = cls(
            role_id=role_id,
            permission_id=permission_id,
            granted_by=granted_by
        )
        
        db.session.add(role_permission)
        return role_permission
    
    @classmethod
    def revoke_permission(cls, role_id, permission_id):
        """
        撤销角色权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            
        Returns:
            bool: 是否成功撤销
        """
        role_permission = cls.query.filter_by(
            role_id=role_id,
            permission_id=permission_id
        ).first()
        
        if role_permission:
            db.session.delete(role_permission)
            return True
        return False
    
    @classmethod
    def get_role_permissions(cls, role_id):
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            list: 权限列表
        """
        from .permission import Permission
        
        permissions = db.session.query(Permission).join(
            cls, Permission.id == cls.permission_id
        ).filter(
            cls.role_id == role_id
        ).all()
        
        return permissions
    
    @classmethod
    def get_permission_roles(cls, permission_id):
        """
        获取拥有指定权限的所有角色
        
        Args:
            permission_id: 权限ID
            
        Returns:
            list: 角色列表
        """
        from .role import Role
        
        roles = db.session.query(Role).join(
            cls, Role.id == cls.role_id
        ).filter(
            cls.permission_id == permission_id
        ).all()
        
        return roles
    
    @classmethod
    def batch_grant_permissions(cls, role_id, permission_ids, granted_by=None):
        """
        批量为角色授予权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            granted_by: 授权人ID
            
        Returns:
            list: 创建的角色权限关联对象列表
        """
        role_permissions = []
        
        for permission_id in permission_ids:
            role_permission = cls.grant_permission(role_id, permission_id, granted_by)
            role_permissions.append(role_permission)
        
        return role_permissions
    
    @classmethod
    def batch_revoke_permissions(cls, role_id, permission_ids=None):
        """
        批量撤销角色权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表，如果为None则撤销所有权限
            
        Returns:
            int: 撤销的权限数量
        """
        query = cls.query.filter_by(role_id=role_id)
        
        if permission_ids is not None:
            query = query.filter(cls.permission_id.in_(permission_ids))
        
        count = query.count()
        query.delete(synchronize_session=False)
        
        return count
    
    @classmethod
    def sync_role_permissions(cls, role_id, permission_ids, granted_by=None):
        """
        同步角色权限（先清空再重新分配）
        
        Args:
            role_id: 角色ID
            permission_ids: 新的权限ID列表
            granted_by: 授权人ID
            
        Returns:
            list: 新创建的角色权限关联对象列表
        """
        # 先清空现有权限
        cls.batch_revoke_permissions(role_id)
        
        # 重新分配权限
        return cls.batch_grant_permissions(role_id, permission_ids, granted_by)