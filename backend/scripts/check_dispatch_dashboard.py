#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调度仪表盘菜单和权限配置检查脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from app.models import Menu, Permission, MenuPermission

def check_dispatch_dashboard():
    """检查调度仪表盘菜单和权限配置"""
    print("=== 调度仪表盘配置检查 ===")
    
    # 检查菜单是否存在
    menu = Menu.query.filter_by(code='dispatch_dashboard').first()
    if not menu:
        print("❌ 错误: 调度仪表盘菜单不存在")
        return False
    
    print(f"✅ 菜单存在: {menu.name} (代码: {menu.code})")
    print(f"   路径: {menu.path}")
    print(f"   组件: {menu.component}")
    print(f"   图标: {menu.icon}")
    print(f"   排序: {menu.sort_order}")
    
    # 检查权限是否存在
    permission = Permission.query.filter_by(code='dispatch:read').first()
    if not permission:
        print("❌ 错误: dispatch:read 权限不存在")
        return False
    
    print(f"✅ 权限存在: {permission.name} (代码: {permission.code})")
    
    # 检查菜单权限绑定
    menu_permission = MenuPermission.query.filter_by(
        menu_id=menu.id, permission_id=permission.id
    ).first()
    
    if not menu_permission:
        print("❌ 错误: 菜单权限绑定不存在")
        return False
    
    print("✅ 菜单权限绑定存在")
    
    # 检查父菜单
    parent_menu = Menu.query.filter_by(code='dispatch').first()
    if not parent_menu:
        print("❌ 错误: 调度管理父菜单不存在")
        return False
    
    print(f"✅ 父菜单存在: {parent_menu.name} (代码: {parent_menu.code})")
    
    # 检查菜单在父菜单中的位置
    children = Menu.query.filter_by(parent_id=parent_menu.id).order_by(Menu.sort_order).all()
    print(f"📋 调度管理子菜单列表 (按排序顺序):")
    for i, child in enumerate(children, 1):
        status = "✅" if child.id == menu.id else "  "
        print(f"   {i}. {status} {child.name} (排序: {child.sort_order})")
    
    print("\n=== 检查完成 ===")
    return True

if __name__ == '__main__':
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            success = check_dispatch_dashboard()
            
            if success:
                print("🎉 所有检查通过！调度仪表盘配置正确。")
                sys.exit(0)
            else:
                print("❌ 检查未通过，请检查配置。")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)