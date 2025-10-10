#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化吨位容积对应管理菜单和权限
此脚本用于添加吨位容积对应管理菜单并绑定相应的权限
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Menu, Permission, MenuPermission, Role, RolePermission
from app.extensions import db

def init_tonnage_volume_menu_permission():
    """初始化吨位容积对应管理菜单和权限"""
    app = create_app()
    with app.app_context():
        print("开始初始化吨位容积对应管理菜单和权限...")
        
        # 1. 确保吨位容积对应管理菜单项存在
        tonnage_volume_menu = Menu.query.filter_by(code='tonnage_volume_mapping').first()
        if not tonnage_volume_menu:
            basic_data_menu = Menu.query.filter_by(code='basic_data').first()
            if basic_data_menu:
                tonnage_volume_menu = Menu(
                    name='吨位容积对应管理',
                    code='tonnage_volume_mapping',
                    path='/basic-data/tonnage-volume-mapping',
                    component='pages/basic-data/TonnageVolumeMapping',
                    icon='el-icon-data-board',
                    parent_id=basic_data_menu.id,
                    sort_order=4,
                    is_active=True
                )
                db.session.add(tonnage_volume_menu)
                print("✓ 创建吨位容积对应管理菜单项")
            else:
                print("✗ 基础数据菜单不存在，无法创建吨位容积对应管理菜单项")
                return
        else:
            print("✓ 吨位容积对应管理菜单项已存在")
        
        # 2. 获取吨位容积相关权限
        tonnage_volume_permissions = Permission.query.filter(
            Permission.code.like('tonnage_volume:%')
        ).all()
        
        if not tonnage_volume_permissions:
            print("✗ 吨位容积相关权限不存在，请先运行权限初始化脚本")
            return
        
        print(f"✓ 找到 {len(tonnage_volume_permissions)} 个吨位容积相关权限")
        
        # 3. 建立菜单与权限的关联
        tonnage_volume_menu = Menu.query.filter_by(code='tonnage_volume_mapping').first()
        if tonnage_volume_menu:
            for perm in tonnage_volume_permissions:
                existing_mp = MenuPermission.query.filter_by(
                    menu_id=tonnage_volume_menu.id,
                    permission_id=perm.id
                ).first()
                
                if not existing_mp:
                    mp = MenuPermission(
                        menu_id=tonnage_volume_menu.id,
                        permission_id=perm.id
                    )
                    db.session.add(mp)
                    print(f"✓ 关联菜单与权限: {perm.code}")
                else:
                    print(f"✓ 菜单权限关联已存在: {perm.code}")
        
        # 4. 为超级管理员分配所有吨位容积权限
        admin_role = Role.query.filter_by(name='超级管理员').first()
        if admin_role:
            for perm in tonnage_volume_permissions:
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
                    print(f"✓ 超级管理员权限已存在: {perm.code}")
        else:
            print("✗ 超级管理员角色不存在")
        
        db.session.commit()
        
        print("\n吨位容积对应管理菜单权限初始化完成！")
        print("\n系统功能说明:")
        print("1. 已创建吨位容积对应管理菜单项")
        print("2. 已关联相关权限到菜单")
        print("3. 已为超级管理员分配所有权限")
        print("4. 用户可以通过角色管理为其他角色分配相应权限")

if __name__ == '__main__':
    init_tonnage_volume_menu_permission()