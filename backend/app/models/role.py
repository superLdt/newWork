from datetime import datetime
from app.extensions import db
from app.models.user_role import user_role


class Role(db.Model):
    """
    角色模型类
    对应数据库设计文档中的Role表
    """
    __tablename__ = 'Role'
    
    id = db.Column(db.Integer, primary_key=True, comment='角色唯一ID')
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    description = db.Column(db.Text, comment='角色描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        """
        将角色对象转换为字典格式
        Returns:
            dict: 包含角色信息的字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_permissions(self):
        """
        获取角色的所有权限
        
        Returns:
            list: 权限对象列表
        """
        from .permission import Permission
        from .role_permission import RolePermission
        
        permissions = db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.role_id == self.id
        ).all()
        
        return permissions
    
    def get_permission_codes(self):
        """
        获取角色的所有权限代码
        
        Returns:
            list: 权限代码列表
        """
        permissions = self.get_permissions()
        return [p.code for p in permissions]
    
    def has_permission(self, permission_code):
        """
        检查角色是否具有指定权限
        
        Args:
            permission_code: 权限代码
            
        Returns:
            bool: 是否具有权限
        """
        permission_codes = self.get_permission_codes()
        return permission_code in permission_codes
    
    def grant_permission(self, permission_id, granted_by=None):
        """
        为角色授予权限
        
        Args:
            permission_id: 权限ID
            granted_by: 授权人ID
            
        Returns:
            RolePermission: 角色权限关联对象
        """
        from .role_permission import RolePermission
        
        return RolePermission.grant_permission(self.id, permission_id, granted_by)
    
    def revoke_permission(self, permission_id):
        """
        撤销角色权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            bool: 是否成功撤销
        """
        from .role_permission import RolePermission
        
        return RolePermission.revoke_permission(self.id, permission_id)
    
    def grant_permissions(self, permission_ids, granted_by=None):
        """
        批量为角色授予权限
        
        Args:
            permission_ids: 权限ID列表
            granted_by: 授权人ID
            
        Returns:
            list: 角色权限关联对象列表
        """
        from .role_permission import RolePermission
        
        return RolePermission.batch_grant_permissions(self.id, permission_ids, granted_by)
    
    def revoke_permissions(self, permission_ids=None):
        """
        批量撤销角色权限
        
        Args:
            permission_ids: 权限ID列表，如果为None则撤销所有权限
            
        Returns:
            int: 撤销的权限数量
        """
        from .role_permission import RolePermission
        
        return RolePermission.batch_revoke_permissions(self.id, permission_ids)
    
    def sync_permissions(self, permission_ids, granted_by=None):
        """
        同步角色权限（先清空再重新分配）
        
        Args:
            permission_ids: 新的权限ID列表
            granted_by: 授权人ID
            
        Returns:
            list: 新创建的角色权限关联对象列表
        """
        from .role_permission import RolePermission
        
        return RolePermission.sync_role_permissions(self.id, permission_ids, granted_by)
    
    def get_user_count(self):
        """
        获取拥有此角色的用户数量
        
        Returns:
            int: 用户数量
        """
        return len(self.users)
    
    def to_dict_with_permissions(self):
        """
        将角色对象转换为包含权限信息的字典格式
        
        Returns:
            dict: 包含权限信息的角色字典
        """
        role_dict = self.to_dict()
        role_dict['permissions'] = [p.to_dict() for p in self.get_permissions()]
        role_dict['permission_codes'] = self.get_permission_codes()
        role_dict['user_count'] = self.get_user_count()
        return role_dict
    
    @classmethod
    def get_default_roles(cls):
        """
        获取系统默认角色列表
        Returns:
            list: 默认角色列表
        """
        return [
            {'name': '超级管理员', 'description': '系统最高权限，可管理所有功能'},
            {'name': '区域调度员', 'description': '负责任务审核、派车管理'},
            {'name': '车间地调', 'description': '负责提交车辆需求、查看已分配的任务'},
            {'name': '供应商', 'description': '负责响应任务、填写车辆信息'},
            {'name': '财务人员', 'description': '负责财务对账，结算单生成等任务'}
        ]


# 关联表定义已移至 user_role.py