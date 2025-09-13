# -*- coding: utf-8 -*-
"""
菜单模型模块
定义Menu数据模型及相关功能
"""

from datetime import datetime
from ..extensions import db


class Menu(db.Model):
    """
    菜单模型类
    支持多级菜单结构的权限控制
    """
    __tablename__ = 'Menu'
    
    id = db.Column(db.Integer, primary_key=True, comment='菜单唯一ID')
    name = db.Column(db.String(100), nullable=False, comment='菜单名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='菜单代码')
    path = db.Column(db.String(200), comment='路由路径')
    component = db.Column(db.String(200), comment='组件路径')
    icon = db.Column(db.String(50), comment='图标')
    parent_id = db.Column(db.Integer, db.ForeignKey('Menu.id'), comment='父菜单ID')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 自引用关系
    parent = db.relationship('Menu', remote_side=[id], backref='children')
    
    def __repr__(self):
        return f'<Menu {self.code}>'
    
    def to_dict(self, include_children=False):
        """
        将菜单对象转换为字典格式
        
        Args:
            include_children: 是否包含子菜单
            
        Returns:
            dict: 包含菜单信息的字典
        """
        result = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'path': self.path,
            'component': self.component,
            'icon': self.icon,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_children:
            result['children'] = [child.to_dict(include_children=True) for child in self.get_active_children()]
            
        return result
    
    def get_active_children(self):
        """
        获取启用的子菜单
        
        Returns:
            list: 启用的子菜单列表，按sort_order排序
        """
        return Menu.query.filter_by(
            parent_id=self.id,
            is_active=True
        ).order_by(Menu.sort_order.asc()).all()
    
    def get_all_descendants(self):
        """
        获取所有后代菜单（递归）
        
        Returns:
            list: 所有后代菜单列表
        """
        descendants = []
        for child in self.get_active_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def get_ancestors(self):
        """
        获取所有祖先菜单
        
        Returns:
            list: 祖先菜单列表，从根菜单到直接父菜单
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors
    
    def get_breadcrumb(self):
        """
        获取面包屑导航
        
        Returns:
            list: 面包屑路径，包含从根菜单到当前菜单的完整路径
        """
        breadcrumb = self.get_ancestors()
        breadcrumb.append(self)
        return breadcrumb
    
    @classmethod
    def get_root_menus(cls):
        """
        获取所有根菜单（顶级菜单）
        
        Returns:
            list: 根菜单列表，按sort_order排序
        """
        return cls.query.filter_by(
            parent_id=None,
            is_active=True
        ).order_by(cls.sort_order.asc()).all()
    
    @classmethod
    def build_menu_tree(cls, menus=None):
        """
        构建菜单树结构
        
        Args:
            menus: 菜单列表，如果为None则获取所有启用的菜单
            
        Returns:
            list: 菜单树结构
        """
        if menus is None:
            menus = cls.query.filter_by(is_active=True).all()
        
        # 创建菜单字典，以id为键
        menu_dict = {menu.id: menu.to_dict() for menu in menus}
        
        # 构建树结构
        tree = []
        for menu in menus:
            menu_data = menu_dict[menu.id]
            if menu.parent_id is None:
                # 根菜单
                tree.append(menu_data)
            else:
                # 子菜单
                parent = menu_dict.get(menu.parent_id)
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(menu_data)
        
        # 对每个层级的菜单按sort_order排序
        def sort_menu_tree(menu_list):
            menu_list.sort(key=lambda x: x['sort_order'])
            for menu in menu_list:
                if 'children' in menu:
                    sort_menu_tree(menu['children'])
        
        sort_menu_tree(tree)
        return tree
    
    @classmethod
    def get_default_menus(cls):
        """
        获取系统默认菜单结构
        
        Returns:
            list: 默认菜单列表
        """
        return [
            # 一级菜单
            {'name': '基础数据', 'code': 'basic_data', 'path': '/basic-data', 'component': 'Layout', 'icon': 'el-icon-data-board', 'parent_id': None, 'sort_order': 1},
            {'name': '调度管理', 'code': 'dispatch', 'path': '/dispatch', 'component': 'Layout', 'icon': 'el-icon-truck', 'parent_id': None, 'sort_order': 2},
            {'name': '系统设置', 'code': 'settings', 'path': '/settings', 'component': 'Layout', 'icon': 'el-icon-setting', 'parent_id': None, 'sort_order': 3},
            
            # 基础数据子菜单
            {'name': '车辆管理', 'code': 'vehicle_management', 'path': '/basic-data/vehicles', 'component': 'pages/basic-data/VehicleManagement', 'icon': 'el-icon-truck', 'parent_code': 'basic_data', 'sort_order': 1},
            {'name': '司机管理', 'code': 'driver_management', 'path': '/basic-data/drivers', 'component': 'pages/basic-data/DriverManagement', 'icon': 'el-icon-user', 'parent_code': 'basic_data', 'sort_order': 2},
            {'name': '客户管理', 'code': 'customer_management', 'path': '/basic-data/customers', 'component': 'pages/basic-data/CustomerManagement', 'icon': 'el-icon-office-building', 'parent_code': 'basic_data', 'sort_order': 3},
            
            # 调度管理子菜单
            {'name': '运输订单', 'code': 'transport_orders', 'path': '/dispatch/orders', 'component': 'pages/dispatch/TransportOrders', 'icon': 'el-icon-document', 'parent_code': 'dispatch', 'sort_order': 1},
            {'name': '调度任务', 'code': 'dispatch_tasks', 'path': '/dispatch/tasks', 'component': 'pages/dispatch/DispatchTasks', 'icon': 'el-icon-coordinate', 'parent_code': 'dispatch', 'sort_order': 2},
            {'name': '调度仪表盘', 'code': 'dispatch_dashboard', 'path': '/dispatch/dashboard', 'component': 'pages/dispatch/DispatchDashboard', 'icon': 'el-icon-data-analysis', 'parent_code': 'dispatch', 'sort_order': 3},
            {'name': '运输跟踪', 'code': 'transport_tracking', 'path': '/dispatch/tracking', 'component': 'pages/dispatch/TransportTracking', 'icon': 'el-icon-location', 'parent_code': 'dispatch', 'sort_order': 4},
            
            # 系统设置子菜单
            {'name': '用户管理', 'code': 'user_management', 'path': '/settings/users', 'component': 'pages/settings/UserManagement', 'icon': 'el-icon-user', 'parent_code': 'settings', 'sort_order': 1},
            {'name': '角色管理', 'code': 'role_management', 'path': '/settings/roles', 'component': 'pages/settings/RoleManagement', 'icon': 'el-icon-user-solid', 'parent_code': 'settings', 'sort_order': 2},
            {'name': '权限管理', 'code': 'permission_management', 'path': '/settings/permissions', 'component': 'pages/settings/PermissionManagement', 'icon': 'el-icon-key', 'parent_code': 'settings', 'sort_order': 3}
        ]
    
    @staticmethod
    def create_menu(name, code, path=None, component=None, icon=None, parent_id=None, sort_order=0):
        """
        创建菜单的便捷方法
        
        Args:
            name: 菜单名称
            code: 菜单代码
            path: 路由路径
            component: 组件路径
            icon: 图标
            parent_id: 父菜单ID
            sort_order: 排序
            
        Returns:
            Menu: 创建的菜单对象
        """
        menu = Menu(
            name=name,
            code=code,
            path=path,
            component=component,
            icon=icon,
            parent_id=parent_id,
            sort_order=sort_order
        )
        return menu