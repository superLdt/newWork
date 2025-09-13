# -*- coding: utf-8 -*-
"""
菜单管理服务模块
提供菜单结构管理和权限菜单生成功能
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from flask import current_app
from ..extensions import db
from ..models import Menu, Permission, MenuPermission, User


class MenuService:
    """
    菜单管理服务类
    """
    
    @staticmethod
    def get_all_menus(include_inactive: bool = False) -> List[Menu]:
        """
        获取所有菜单
        
        Args:
            include_inactive: 是否包含未启用的菜单
            
        Returns:
            list: 菜单对象列表
        """
        query = Menu.query
        
        if not include_inactive:
            query = query.filter(Menu.is_active == True)
        
        return query.order_by(Menu.sort_order.asc()).all()
    
    @staticmethod
    def get_menu_tree(include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        获取菜单树结构
        
        Args:
            include_inactive: 是否包含未启用的菜单
            
        Returns:
            list: 菜单树结构
        """
        menus = MenuService.get_all_menus(include_inactive)
        return Menu.build_menu_tree(menus)
    
    @staticmethod
    def get_menu_by_id(menu_id: int) -> Optional[Menu]:
        """
        根据ID获取菜单
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            Menu: 菜单对象，如果不存在则返回None
        """
        return Menu.query.get(menu_id)
    
    @staticmethod
    def get_menu_by_code(code: str) -> Optional[Menu]:
        """
        根据菜单代码获取菜单
        
        Args:
            code: 菜单代码
            
        Returns:
            Menu: 菜单对象，如果不存在则返回None
        """
        return Menu.query.filter_by(code=code).first()
    
    @staticmethod
    def create_menu(data: Dict[str, Any]) -> Menu:
        """
        创建菜单
        
        Args:
            data: 菜单数据字典
            
        Returns:
            Menu: 创建的菜单对象
            
        Raises:
            ValueError: 当菜单代码已存在或父菜单不存在时
        """
        # 检查菜单代码是否已存在
        existing = Menu.query.filter_by(code=data['code']).first()
        if existing:
            raise ValueError(f"菜单代码 '{data['code']}' 已存在")
        
        # 检查父菜单是否存在
        parent_id = data.get('parent_id')
        if parent_id:
            parent = Menu.query.get(parent_id)
            if not parent:
                raise ValueError(f"父菜单ID {parent_id} 不存在")
        
        menu = Menu(
            name=data['name'],
            code=data['code'],
            path=data.get('path'),
            component=data.get('component'),
            icon=data.get('icon'),
            parent_id=parent_id,
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(menu)
        db.session.commit()
        
        return menu
    
    @staticmethod
    def update_menu(menu_id: int, data: Dict[str, Any]) -> Menu:
        """
        更新菜单
        
        Args:
            menu_id: 菜单ID
            data: 更新数据字典
            
        Returns:
            Menu: 更新后的菜单对象
            
        Raises:
            ValueError: 当菜单不存在、菜单代码冲突或父菜单不存在时
        """
        menu = Menu.query.get(menu_id)
        if not menu:
            raise ValueError(f"菜单ID {menu_id} 不存在")
        
        # 检查菜单代码是否冲突
        if 'code' in data and data['code'] != menu.code:
            existing = Menu.query.filter_by(code=data['code']).first()
            if existing:
                raise ValueError(f"菜单代码 '{data['code']}' 已存在")
        
        # 检查父菜单是否存在（不能设置自己为父菜单）
        if 'parent_id' in data:
            parent_id = data['parent_id']
            if parent_id:
                if parent_id == menu_id:
                    raise ValueError("不能将菜单设置为自己的父菜单")
                parent = Menu.query.get(parent_id)
                if not parent:
                    raise ValueError(f"父菜单ID {parent_id} 不存在")
                
                # 检查是否会形成循环引用
                if MenuService._would_create_cycle(menu_id, parent_id):
                    raise ValueError("设置此父菜单会形成循环引用")
        
        # 更新字段
        for field in ['name', 'code', 'path', 'component', 'icon', 'parent_id', 'sort_order', 'is_active']:
            if field in data:
                setattr(menu, field, data[field])
        
        db.session.commit()
        
        return menu
    
    @staticmethod
    def delete_menu(menu_id: int, force: bool = False) -> bool:
        """
        删除菜单
        
        Args:
            menu_id: 菜单ID
            force: 是否强制删除（包括子菜单）
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            ValueError: 当菜单不存在或有子菜单时
        """
        menu = Menu.query.get(menu_id)
        if not menu:
            raise ValueError(f"菜单ID {menu_id} 不存在")
        
        # 检查是否有子菜单
        children = menu.get_active_children()
        if children and not force:
            raise ValueError(f"菜单 '{menu.name}' 有 {len(children)} 个子菜单，无法删除")
        
        # 如果强制删除，先删除所有子菜单
        if force:
            MenuService._delete_menu_recursive(menu)
        else:
            db.session.delete(menu)
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def _delete_menu_recursive(menu: Menu):
        """
        递归删除菜单及其子菜单
        
        Args:
            menu: 要删除的菜单对象
        """
        # 先删除所有子菜单
        for child in menu.children:
            MenuService._delete_menu_recursive(child)
        
        # 删除菜单
        db.session.delete(menu)
    
    @staticmethod
    def _would_create_cycle(menu_id: int, parent_id: int) -> bool:
        """
        检查设置父菜单是否会形成循环引用
        
        Args:
            menu_id: 菜单ID
            parent_id: 父菜单ID
            
        Returns:
            bool: 是否会形成循环引用
        """
        current_id = parent_id
        visited = set()
        
        while current_id:
            if current_id == menu_id:
                return True
            
            if current_id in visited:
                # 已经访问过，说明存在循环，但不涉及目标菜单
                break
            
            visited.add(current_id)
            parent = Menu.query.get(current_id)
            current_id = parent.parent_id if parent else None
        
        return False
    
    @staticmethod
    def get_user_menus(user_id: int, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        获取用户可访问的菜单树
        
        Args:
            user_id: 用户ID
            include_inactive: 是否包含未启用的菜单
            
        Returns:
            list: 用户可访问的菜单树结构
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return []
        
        # 管理员返回全量菜单树
        if hasattr(user, 'is_admin') and callable(getattr(user, 'is_admin')) and user.is_admin():
            return MenuService.get_menu_tree(include_inactive)
        
        # 获取用户可访问的菜单
        accessible_menus = user.get_accessible_menus()
        
        if not include_inactive:
            accessible_menus = [menu for menu in accessible_menus if menu.is_active]
        
        # 构建菜单树（需要包含父菜单路径）
        menu_tree = MenuService._build_user_menu_tree(accessible_menus)
        
        return menu_tree
    
    @staticmethod
    def _build_user_menu_tree(accessible_menus: List[Menu]) -> List[Dict[str, Any]]:
        """
        为用户构建菜单树，包含必要的父菜单路径
        
        Args:
            accessible_menus: 用户可访问的菜单列表
            
        Returns:
            list: 菜单树结构
        """
        # 获取所有需要的菜单（包括父菜单路径）
        all_needed_menus = set()
        
        for menu in accessible_menus:
            # 添加菜单本身
            all_needed_menus.add(menu)
            
            # 添加所有祖先菜单
            ancestors = menu.get_ancestors()
            all_needed_menus.update(ancestors)
        
        # 构建菜单树
        return Menu.build_menu_tree(list(all_needed_menus))
    
    @staticmethod
    def get_menu_permissions(menu_id: int) -> List[Dict[str, Any]]:
        """
        获取菜单需要的权限列表
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            list: 权限字典列表
        """
        permissions = MenuPermission.get_menu_permissions(menu_id)
        return [permission.to_dict() for permission in permissions]
    
    
    @staticmethod
    def validate_menu_ids(menu_ids: List[int]) -> List[int]:
        """
        验证菜单ID列表是否存在

        Args:
            menu_ids: 菜单ID列表

        Returns:
            list: 存在的菜单ID列表
        """
        if not menu_ids:
            return []
        existing_menus = db.session.query(Menu).filter(
            Menu.id.in_(menu_ids)
        ).all()
        return [m.id for m in existing_menus]

    @staticmethod
    def get_permissions_by_menu_ids(menu_ids: List[int]) -> List[int]:
        """
        根据菜单ID列表获取所有相关的权限ID

        Args:
            menu_ids: 菜单ID列表

        Returns:
            list: 权限ID列表
        """
        if not menu_ids:
            return []
        menu_permissions = db.session.query(MenuPermission).filter(
            MenuPermission.menu_id.in_(menu_ids)
        ).all()
        return list(set([mp.permission_id for mp in menu_permissions]))

    @staticmethod
    def bind_menu_permissions(menu_id: int, permission_ids: List[int]) -> List[MenuPermission]:
        """
        为菜单绑定权限
        
        Args:
            menu_id: 菜单ID
            permission_ids: 权限ID列表
            
        Returns:
            list: 菜单权限关联对象列表
            
        Raises:
            ValueError: 当菜单不存在时
        """
        menu = Menu.query.get(menu_id)
        if not menu:
            raise ValueError(f"菜单ID {menu_id} 不存在")
        
        # 同步菜单权限
        menu_permissions = MenuPermission.sync_menu_permissions(menu_id, permission_ids)
        db.session.commit()
        
        return menu_permissions
    
    @staticmethod
    def get_root_menus(include_inactive: bool = False) -> List[Menu]:
        """
        获取根菜单列表
        
        Args:
            include_inactive: 是否包含未启用的菜单
            
        Returns:
            list: 根菜单对象列表
        """
        query = Menu.query.filter(Menu.parent_id.is_(None))
        
        if not include_inactive:
            query = query.filter(Menu.is_active == True)
        
        return query.order_by(Menu.sort_order.asc()).all()
    
    @staticmethod
    def get_menu_children(menu_id: int, include_inactive: bool = False) -> List[Menu]:
        """
        获取菜单的子菜单列表
        
        Args:
            menu_id: 菜单ID
            include_inactive: 是否包含未启用的菜单
            
        Returns:
            list: 子菜单对象列表
        """
        query = Menu.query.filter(Menu.parent_id == menu_id)
        
        if not include_inactive:
            query = query.filter(Menu.is_active == True)
        
        return query.order_by(Menu.sort_order.asc()).all()
    
    @staticmethod
    def move_menu(menu_id: int, new_parent_id: Optional[int], new_sort_order: Optional[int] = None) -> Menu:
        """
        移动菜单到新的父菜单下
        
        Args:
            menu_id: 菜单ID
            new_parent_id: 新的父菜单ID，None表示移动到根级别
            new_sort_order: 新的排序值
            
        Returns:
            Menu: 更新后的菜单对象
            
        Raises:
            ValueError: 当菜单不存在、父菜单不存在或会形成循环引用时
        """
        menu = Menu.query.get(menu_id)
        if not menu:
            raise ValueError(f"菜单ID {menu_id} 不存在")
        
        # 检查新父菜单是否存在
        if new_parent_id:
            if new_parent_id == menu_id:
                raise ValueError("不能将菜单移动到自己下面")
            
            new_parent = Menu.query.get(new_parent_id)
            if not new_parent:
                raise ValueError(f"父菜单ID {new_parent_id} 不存在")
            
            # 检查是否会形成循环引用
            if MenuService._would_create_cycle(menu_id, new_parent_id):
                raise ValueError("移动到此父菜单会形成循环引用")
        
        # 更新菜单
        menu.parent_id = new_parent_id
        if new_sort_order is not None:
            menu.sort_order = new_sort_order
        
        db.session.commit()
        
        return menu
    
    @staticmethod
    def batch_update_menu_order(menu_orders: List[Dict[str, Any]]) -> bool:
        """
        批量更新菜单排序
        
        Args:
            menu_orders: 菜单排序数据列表，格式：[{'id': menu_id, 'sort_order': order}, ...]
            
        Returns:
            bool: 是否更新成功
        """
        for item in menu_orders:
            menu = Menu.query.get(item['id'])
            if menu:
                menu.sort_order = item['sort_order']
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def search_menus(keyword: str, include_inactive: bool = False) -> List[Menu]:
        """
        搜索菜单
        
        Args:
            keyword: 搜索关键词
            include_inactive: 是否包含未启用的菜单
            
        Returns:
            list: 菜单对象列表
        """
        query = Menu.query
        
        if keyword:
            search_filter = or_(
                Menu.name.contains(keyword),
                Menu.code.contains(keyword),
                Menu.path.contains(keyword)
            )
            query = query.filter(search_filter)
        
        if not include_inactive:
            query = query.filter(Menu.is_active == True)
        
        return query.order_by(Menu.name.asc()).all()

    @staticmethod
    def get_menu_tree_by_role_permissions(role_id: int, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        根据角色权限获取菜单树

        Args:
            role_id: 角色ID
            include_inactive: 是否包含未启用的菜单

        Returns:
            list: 完整的菜单树结构，包含所有菜单
        """
        from ..models import Role, RolePermission

        current_app.logger.debug(f"get_menu_tree_by_role_permissions called with role_id: {role_id}")
        role = Role.query.get(role_id)
        if not role:
            current_app.logger.debug(f"Role with ID {role_id} not found. Returning empty list.")
            return []

        # 获取角色拥有的所有权限ID（从 RolePermission 关联表查询）
        role_permission_ids = [rp.permission_id for rp in RolePermission.query.filter_by(role_id=role_id).all()]
        current_app.logger.debug(f"Role permission IDs: {role_permission_ids}")

        # 获取所有菜单权限关联
        menu_permissions = MenuPermission.query.filter(
            MenuPermission.permission_id.in_(role_permission_ids)
        ).all()

        # 获取所有与角色权限关联的菜单ID
        accessible_menu_ids = list(set([mp.menu_id for mp in menu_permissions]))
        current_app.logger.debug(f"Accessible menu IDs: {accessible_menu_ids}")

        # 获取所有菜单（返回完整菜单树，不过滤）
        all_menus = MenuService.get_all_menus(include_inactive)
        current_app.logger.debug(f"Total menus fetched: {len(all_menus)}")

        # 构建完整菜单树
        menu_tree = Menu.build_menu_tree(all_menus)
        
        # 在返回的树中标记有权限的菜单ID
        def mark_permissions_in_tree(menus, accessible_ids):
            """递归标记菜单权限状态"""
            for menu in menus:
                menu['has_permission'] = menu['id'] in accessible_ids
                if menu.get('children'):
                    mark_permissions_in_tree(menu['children'], accessible_ids)
        
        mark_permissions_in_tree(menu_tree, accessible_menu_ids)
        current_app.logger.debug(f"Menu tree built with permissions. Root nodes count: {len(menu_tree)}")
        return menu_tree

    @staticmethod
    def get_menu_statistics() -> Dict[str, Any]:
        """
        获取菜单统计信息
        
        Returns:
            dict: 菜单统计信息
        """
        total_menus = Menu.query.count()
        active_menus = Menu.query.filter(Menu.is_active == True).count()
        root_menus = Menu.query.filter(Menu.parent_id.is_(None)).count()
        
        # 计算菜单层级分布
        level_stats = {}
        root_menus_list = Menu.get_root_menus()
        
        def count_levels(menus, level):
            if level not in level_stats:
                level_stats[level] = 0
            level_stats[level] += len(menus)
            
            for menu in menus:
                children = menu.get_active_children()
                if children:
                    count_levels(children, level + 1)
        
        count_levels(root_menus_list, 1)
        
        return {
            'total_menus': total_menus,
            'active_menus': active_menus,
            'inactive_menus': total_menus - active_menus,
            'root_menus': root_menus,
            'level_stats': level_stats
        }