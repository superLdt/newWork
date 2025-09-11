#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
菜单权限系统初始化脚本
用于创建完整的菜单结构、权限配置和角色权限分配
"""

from app import create_app
from app.models import Menu, Permission, MenuPermission, Role, RolePermission
from app.extensions import db

def init_menu_permission_system():
    """初始化菜单权限系统"""
    app = create_app()
    with app.app_context():
        print("开始初始化菜单权限系统...")
        
        # 1. 确保菜单管理菜单项存在
        menu_mgmt = Menu.query.filter_by(code='menu_management').first()
        if not menu_mgmt:
            settings_menu = Menu.query.filter_by(code='settings').first()
            if settings_menu:
                menu_mgmt = Menu(
                    name='菜单管理',
                    code='menu_management',
                    path='/settings/menu',
                    component='pages/settings/MenuManagement',
                    icon='el-icon-menu',
                    parent_id=settings_menu.id,
                    sort_order=4,
                    is_active=True
                )
                db.session.add(menu_mgmt)
                print("✓ 创建菜单管理菜单项")
            else:
                print("✗ 系统设置菜单不存在，无法创建菜单管理项")
                return
        else:
            print("✓ 菜单管理菜单项已存在")
        
        # 2. 创建菜单相关权限
        menu_permissions = [
            {
                'name': '菜单管理权限',
                'code': 'menu:read',
                'description': '访问菜单管理页面',
                'resource_type': 'menu',
                'resource_id': '/settings/menu',
                'action': 'read'
            },
            {
                'name': '创建菜单权限',
                'code': 'menu:create',
                'description': '创建新菜单',
                'resource_type': 'api',
                'resource_id': '/api/v1/menus',
                'action': 'create'
            },
            {
                'name': '编辑菜单权限',
                'code': 'menu:update',
                'description': '编辑菜单信息',
                'resource_type': 'api',
                'resource_id': '/api/v1/menus',
                'action': 'update'
            },
            {
                'name': '删除菜单权限',
                'code': 'menu:delete',
                'description': '删除菜单',
                'resource_type': 'api',
                'resource_id': '/api/v1/menus',
                'action': 'delete'
            }
        ]
        
        created_permissions = []
        for perm_data in menu_permissions:
            existing_perm = Permission.query.filter_by(code=perm_data['code']).first()
            if not existing_perm:
                perm = Permission(**perm_data)
                db.session.add(perm)
                created_permissions.append(perm)
                print(f"✓ 创建权限: {perm_data['name']}")
            else:
                created_permissions.append(existing_perm)
                print(f"✓ 权限已存在: {perm_data['name']}")
        
        db.session.commit()
        
        # 3. 建立菜单与权限的关联
        menu_mgmt = Menu.query.filter_by(code='menu_management').first()
        if menu_mgmt:
            for perm in created_permissions:
                existing_mp = MenuPermission.query.filter_by(
                    menu_id=menu_mgmt.id,
                    permission_id=perm.id
                ).first()
                
                if not existing_mp:
                    mp = MenuPermission(
                        menu_id=menu_mgmt.id,
                        permission_id=perm.id
                    )
                    db.session.add(mp)
                    print(f"✓ 关联菜单与权限: {perm.code}")
        
        # 4. 为超级管理员分配所有菜单权限
        admin_role = Role.query.filter_by(name='超级管理员').first()
        if admin_role:
            for perm in created_permissions:
                existing_rp = RolePermission.query.filter_by(
                    role_id=admin_role.id,
                    permission_id=perm.id
                ).first()
                
                if not existing_rp:
                    rp = RolePermission(
                        role_id=admin_role.id,
                        permission_id=perm.id
                    )
                    db.session.add(rp)
                    print(f"✓ 为超级管理员分配权限: {perm.code}")
        else:
            print("✗ 超级管理员角色不存在")
        
        db.session.commit()
        
        print("\n菜单权限系统初始化完成！")
        print("\n系统功能说明:")
        print("1. 菜单管理: 系统设置 → 菜单管理")
        print("2. 权限管理: 系统设置 → 权限管理")
        print("3. 角色管理: 系统设置 → 角色管理")
        print("4. 用户管理: 系统设置 → 用户管理")
        print("\n使用流程:")
        print("1. 在菜单管理中创建系统菜单结构")
        print("2. 在权限管理中创建对应的访问权限")
        print("3. 通过菜单权限配置建立菜单与权限的关联")
        print("4. 在角色管理中为角色分配权限")
        print("5. 在用户管理中为用户分配角色")

def show_current_status():
    """显示当前系统状态"""
    app = create_app()
    with app.app_context():
        print("\n=== 当前系统状态 ===")
        
        # 菜单统计
        total_menus = Menu.query.count()
        active_menus = Menu.query.filter_by(is_active=True).count()
        print(f"菜单总数: {total_menus} (启用: {active_menus})")
        
        # 权限统计
        total_permissions = Permission.query.count()
        menu_permissions = Permission.query.filter_by(resource_type='menu').count()
        api_permissions = Permission.query.filter_by(resource_type='api').count()
        print(f"权限总数: {total_permissions} (菜单权限: {menu_permissions}, API权限: {api_permissions})")
        
        # 角色统计
        total_roles = Role.query.count()
        print(f"角色总数: {total_roles}")
        
        # 菜单权限关联统计
        total_menu_permissions = MenuPermission.query.count()
        print(f"菜单权限关联: {total_menu_permissions}")
        
        # 角色权限关联统计
        total_role_permissions = RolePermission.query.count()
        print(f"角色权限关联: {total_role_permissions}")
        
        print("\n=== 系统设置菜单 ===")
        settings_menu = Menu.query.filter_by(code='settings').first()
        if settings_menu:
            children = Menu.query.filter_by(parent_id=settings_menu.id, is_active=True).all()
            for child in children:
                print(f"- {child.name} ({child.code}) - {child.path}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_current_status()
    else:
        init_menu_permission_system()
        show_current_status()