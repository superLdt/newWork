# -*- coding: utf-8 -*-
"""
菜单权限关联模型模块
定义菜单与权限的关联关系
"""

from ..extensions import db


class MenuPermission(db.Model):
    """
    菜单权限关联模型类
    定义菜单项需要哪些权限才能访问
    """
    __tablename__ = 'MenuPermission'
    
    id = db.Column(db.Integer, primary_key=True, comment='关联记录唯一ID')
    menu_id = db.Column(db.Integer, db.ForeignKey('Menu.id', ondelete='CASCADE'), nullable=False, comment='菜单ID')
    permission_id = db.Column(db.Integer, db.ForeignKey('Permission.id', ondelete='CASCADE'), nullable=False, comment='权限ID')
    
    # 关系定义
    menu = db.relationship('Menu', backref=db.backref('menu_permissions', lazy=True, cascade='all, delete-orphan'))
    permission = db.relationship('Permission', backref=db.backref('menu_permissions', lazy=True))
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('menu_id', 'permission_id', name='uk_menu_permission'),
    )
    
    def __repr__(self):
        return f'<MenuPermission menu_id={self.menu_id} permission_id={self.permission_id}>'
    
    def to_dict(self):
        """
        将菜单权限关联对象转换为字典格式
        
        Returns:
            dict: 包含关联信息的字典
        """
        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'permission_id': self.permission_id,
            'menu': self.menu.to_dict() if self.menu else None,
            'permission': self.permission.to_dict() if self.permission else None
        }
    
    @classmethod
    def bind_permission(cls, menu_id, permission_id):
        """
        为菜单绑定权限
        
        Args:
            menu_id: 菜单ID
            permission_id: 权限ID
            
        Returns:
            MenuPermission: 创建的菜单权限关联对象
        """
        # 检查是否已存在
        existing = cls.query.filter_by(
            menu_id=menu_id,
            permission_id=permission_id
        ).first()
        
        if existing:
            return existing
        
        menu_permission = cls(
            menu_id=menu_id,
            permission_id=permission_id
        )
        
        db.session.add(menu_permission)
        return menu_permission
    
    @classmethod
    def unbind_permission(cls, menu_id, permission_id):
        """
        解除菜单权限绑定
        
        Args:
            menu_id: 菜单ID
            permission_id: 权限ID
            
        Returns:
            bool: 是否成功解除绑定
        """
        menu_permission = cls.query.filter_by(
            menu_id=menu_id,
            permission_id=permission_id
        ).first()
        
        if menu_permission:
            db.session.delete(menu_permission)
            return True
        return False
    
    @classmethod
    def get_menu_permissions(cls, menu_id):
        """
        获取菜单需要的所有权限
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            list: 权限列表
        """
        from .permission import Permission
        
        permissions = db.session.query(Permission).join(
            cls, Permission.id == cls.permission_id
        ).filter(
            cls.menu_id == menu_id
        ).all()
        
        return permissions
    
    @classmethod
    def get_permission_menus(cls, permission_id):
        """
        获取需要指定权限的所有菜单
        
        Args:
            permission_id: 权限ID
            
        Returns:
            list: 菜单列表
        """
        from .menu import Menu
        
        menus = db.session.query(Menu).join(
            cls, Menu.id == cls.menu_id
        ).filter(
            cls.permission_id == permission_id
        ).all()
        
        return menus
    
    @classmethod
    def batch_bind_permissions(cls, menu_id, permission_ids):
        """
        批量为菜单绑定权限
        
        Args:
            menu_id: 菜单ID
            permission_ids: 权限ID列表
            
        Returns:
            list: 创建的菜单权限关联对象列表
        """
        menu_permissions = []
        
        for permission_id in permission_ids:
            menu_permission = cls.bind_permission(menu_id, permission_id)
            menu_permissions.append(menu_permission)
        
        return menu_permissions
    
    @classmethod
    def batch_unbind_permissions(cls, menu_id, permission_ids=None):
        """
        批量解除菜单权限绑定
        
        Args:
            menu_id: 菜单ID
            permission_ids: 权限ID列表，如果为None则解除所有权限绑定
            
        Returns:
            int: 解除绑定的权限数量
        """
        query = cls.query.filter_by(menu_id=menu_id)
        
        if permission_ids is not None:
            query = query.filter(cls.permission_id.in_(permission_ids))
        
        count = query.count()
        query.delete(synchronize_session=False)
        
        return count
    
    @classmethod
    def sync_menu_permissions(cls, menu_id, permission_ids):
        """
        同步菜单权限（先清空再重新绑定）
        
        Args:
            menu_id: 菜单ID
            permission_ids: 新的权限ID列表
            
        Returns:
            list: 新创建的菜单权限关联对象列表
        """
        # 先清空现有权限绑定
        cls.batch_unbind_permissions(menu_id)
        
        # 重新绑定权限
        return cls.batch_bind_permissions(menu_id, permission_ids)
    
    @classmethod
    def get_user_accessible_menus(cls, user_id):
        """
        获取用户可访问的菜单列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 用户可访问的菜单列表
        """
        from .menu import Menu
        from .role_permission import RolePermission
        from .user_role import user_role
        
        # 查询用户通过角色获得的所有权限
        user_permissions = db.session.query(cls.permission_id).join(
            RolePermission, cls.permission_id == RolePermission.permission_id
        ).join(
            user_role, RolePermission.role_id == user_role.c.role_id
        ).filter(
            user_role.c.user_id == user_id
        ).subquery()
        
        # 查询用户可访问的菜单
        accessible_menus = db.session.query(Menu).join(
            cls, Menu.id == cls.menu_id
        ).filter(
            cls.permission_id.in_(user_permissions),
            Menu.is_active == True
        ).distinct().all()
        
        return accessible_menus
    
    @classmethod
    def check_menu_access(cls, user_id, menu_code):
        """
        检查用户是否可以访问指定菜单
        
        Args:
            user_id: 用户ID
            menu_code: 菜单代码
            
        Returns:
            bool: 是否可以访问
        """
        from .menu import Menu
        from .role_permission import RolePermission
        from .user_role import user_role
        
        # 查询菜单
        menu = Menu.query.filter_by(code=menu_code, is_active=True).first()
        if not menu:
            return False
        
        # 查询菜单需要的权限
        required_permissions = cls.get_menu_permissions(menu.id)
        if not required_permissions:
            # 如果菜单没有绑定权限，则默认允许访问
            return True
        
        # 查询用户拥有的权限
        user_permission_ids = db.session.query(RolePermission.permission_id).join(
            user_role, RolePermission.role_id == user_role.c.role_id
        ).filter(
            user_role.c.user_id == user_id
        ).all()
        
        user_permission_ids = [p[0] for p in user_permission_ids]
        
        # 检查是否拥有任一所需权限
        for permission in required_permissions:
            if permission.id in user_permission_ids:
                return True
        
        return False