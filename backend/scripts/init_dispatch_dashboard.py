#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化调度仪表盘菜单和权限
此脚本用于添加调度仪表盘菜单并绑定相应的权限
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Menu, Permission, MenuPermission
from app.extensions import db

def init_dispatch_dashboard():
    """初始化调度仪表盘菜单和权限"""
    app = create_app()
    
    with app.app_context():
        print("=== 开始初始化调度仪表盘菜单和权限 ===")
        
        # 1. 检查调度仪表盘菜单是否已存在
        dashboard_menu = Menu.query.filter_by(code='dispatch_dashboard').first()
        if dashboard_menu:
            print("调度仪表盘菜单已存在，跳过创建")
        else:
            # 获取调度管理父菜单
            dispatch_parent = Menu.query.filter_by(code='dispatch').first()
            if not dispatch_parent:
                print("错误: 未找到调度管理父菜单")
                return False
            
            # 创建调度仪表盘菜单
            dashboard_menu = Menu(
                name='调度仪表盘',
                code='dispatch_dashboard',
                path='/dispatch/dashboard',
                component='pages/dispatch/DispatchDashboard',
                icon='el-icon-data-analysis',
                parent_id=dispatch_parent.id,
                sort_order=3,
                is_active=True
            )
            db.session.add(dashboard_menu)
            db.session.commit()
            print("✓ 调度仪表盘菜单创建成功")
        
        # 2. 检查dispatch:read权限是否存在
        dispatch_read_permission = Permission.query.filter_by(code='dispatch:read').first()
        if not dispatch_read_permission:
            print("错误: 未找到dispatch:read权限")
            return False
        
        # 3. 检查菜单权限绑定是否已存在
        existing_binding = MenuPermission.query.filter_by(
            menu_id=dashboard_menu.id,
            permission_id=dispatch_read_permission.id
        ).first()
        
        if existing_binding:
            print("调度仪表盘菜单权限绑定已存在，跳过绑定")
        else:
            # 绑定菜单权限
            menu_permission = MenuPermission(
                menu_id=dashboard_menu.id,
                permission_id=dispatch_read_permission.id
            )
            db.session.add(menu_permission)
            db.session.commit()
            print("✓ 调度仪表盘菜单权限绑定成功")
        
        print("=== 调度仪表盘初始化完成 ===")
        return True

def check_dispatch_dashboard_status():
    """检查调度仪表盘状态"""
    app = create_app()
    
    with app.app_context():
        print("=== 检查调度仪表盘状态 ===")
        
        # 检查菜单
        dashboard_menu = Menu.query.filter_by(code='dispatch_dashboard').first()
        if dashboard_menu:
            print(f"✓ 调度仪表盘菜单存在: {dashboard_menu.name} ({dashboard_menu.code})")
            print(f"   路径: {dashboard_menu.path}")
            print(f"   组件: {dashboard_menu.component}")
            print(f"   图标: {dashboard_menu.icon}")
            print(f"   父菜单ID: {dashboard_menu.parent_id}")
            print(f"   排序: {dashboard_menu.sort_order}")
            print(f"   启用状态: {dashboard_menu.is_active}")
        else:
            print("✗ 调度仪表盘菜单不存在")
        
        # 检查权限绑定
        if dashboard_menu:
            permissions = MenuPermission.get_menu_permissions(dashboard_menu.id)
            if permissions:
                print("✓ 菜单权限绑定:")
                for perm in permissions:
                    print(f"   - {perm.name} ({perm.code})")
            else:
                print("✗ 菜单未绑定任何权限")
        
        print("=== 状态检查完成 ===")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_dispatch_dashboard_status()
    else:
        success = init_dispatch_dashboard()
        if success:
            check_dispatch_dashboard_status()
        else:
            print("初始化失败")
            sys.exit(1)