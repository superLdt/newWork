#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新菜单和权限表脚本
将客户管理改为派车单位管理，并相应调整权限表
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Menu, Permission, MenuPermission, RolePermission, Role
from app.extensions import db
from sqlalchemy import text


def update_customer_to_dispatch_unit():
    """将客户管理更新为派车单位管理"""
    app = create_app()
    
    with app.app_context():
        print("=== 开始更新客户管理为派车单位管理 ===")
        
        try:
            # 1. 更新菜单表
            print("\n1. 更新菜单表...")
            customer_menu = Menu.query.filter_by(code='customer_management').first()
            dispatch_unit_menu = Menu.query.filter_by(code='dispatch_unit_management').first()
            
            if customer_menu:
                print(f"找到客户管理菜单: {customer_menu.name}")
                customer_menu.name = '派车单位管理'
                customer_menu.code = 'dispatch_unit_management'
                customer_menu.path = '/basic-data/dispatch-units'
                customer_menu.component = 'pages/basic-data/DispatchUnitManagement'
                customer_menu.icon = 'el-icon-office-building'
                print("✓ 菜单信息已更新")
            elif dispatch_unit_menu:
                print(f"派车单位管理菜单已存在: {dispatch_unit_menu.name}")
            else:
                # 如果不存在客户管理菜单，创建派车单位管理菜单
                print("未找到客户管理菜单，创建派车单位管理菜单")
                basic_data_parent = Menu.query.filter_by(code='basic_data').first()
                if not basic_data_parent:
                    print("错误: 未找到基础数据父菜单")
                    return False
                
                dispatch_unit_menu = Menu(
                    name='派车单位管理',
                    code='dispatch_unit_management',
                    path='/basic-data/dispatch-units',
                    component='pages/basic-data/DispatchUnitManagement',
                    icon='el-icon-office-building',
                    parent_id=basic_data_parent.id,
                    sort_order=3,
                    is_active=True
                )
                db.session.add(dispatch_unit_menu)
                print("✓ 派车单位管理菜单创建成功")
            
            # 2. 更新权限表
            print("\n2. 更新权限表...")
            
            # 查找并更新客户管理相关权限
            customer_permissions = Permission.query.filter(
                Permission.code.like('customer:%')
            ).all()
            
            permission_mapping = {
                'customer:read': 'dispatch_unit:read',
                'customer:create': 'dispatch_unit:create',
                'customer:update': 'dispatch_unit:update',
                'customer:delete': 'dispatch_unit:delete',
                'customer:manage': 'dispatch_unit:manage'
            }
            
            for perm in customer_permissions:
                old_code = perm.code
                if old_code in permission_mapping:
                    new_code = permission_mapping[old_code]
                    perm.code = new_code
                    perm.name = perm.name.replace('客户', '派车单位')
                    perm.description = perm.description.replace('客户', '派车单位') if perm.description else None
                    print(f"✓ 权限更新: {old_code} -> {new_code}")
            
            # 检查并创建缺失的派车单位权限
            required_permissions = [
                {
                    'code': 'dispatch_unit:read',
                    'name': '查看派车单位',
                    'description': '查看派车单位信息的权限',
                    'resource_type': 'api',
                    'action': 'read'
                },
                {
                    'code': 'dispatch_unit:create',
                    'name': '创建派车单位',
                    'description': '创建新派车单位的权限',
                    'resource_type': 'api',
                    'action': 'write'
                },
                {
                    'code': 'dispatch_unit:update',
                    'name': '更新派车单位',
                    'description': '更新派车单位信息的权限',
                    'resource_type': 'api',
                    'action': 'write'
                },
                {
                    'code': 'dispatch_unit:delete',
                    'name': '删除派车单位',
                    'description': '删除派车单位的权限',
                    'resource_type': 'api',
                    'action': 'delete'
                },
                {
                    'code': 'dispatch_unit:manage',
                    'name': '管理派车单位',
                    'description': '管理派车单位的权限',
                    'resource_type': 'api',
                    'action': 'execute'
                }
            ]
            
            for perm_data in required_permissions:
                existing_perm = Permission.query.filter_by(code=perm_data['code']).first()
                if not existing_perm:
                    permission = Permission(
                        code=perm_data['code'],
                        name=perm_data['name'],
                        description=perm_data['description'],
                        resource_type=perm_data['resource_type'],
                        action=perm_data['action']
                    )
                    db.session.add(permission)
                    print(f"✓ 权限创建: {perm_data['code']}")
                else:
                    print(f"权限已存在: {perm_data['code']}")
            
            # 3. 更新菜单权限关联
            print("\n3. 更新菜单权限关联...")
            dispatch_unit_menu = Menu.query.filter_by(code='dispatch_unit_management').first()
            if dispatch_unit_menu:
                # 删除旧的菜单权限关联
                old_menu_perms = MenuPermission.query.filter_by(menu_id=dispatch_unit_menu.id).all()
                for mp in old_menu_perms:
                    db.session.delete(mp)
                
                # 创建新的菜单权限关联
                dispatch_unit_read_perm = Permission.query.filter_by(code='dispatch_unit:read').first()
                if dispatch_unit_read_perm:
                    menu_permission = MenuPermission(
                        menu_id=dispatch_unit_menu.id,
                        permission_id=dispatch_unit_read_perm.id
                    )
                    db.session.add(menu_permission)
                    print("✓ 菜单权限关联已更新")
            
            # 4. 为管理员角色分配新权限
            print("\n4. 为管理员角色分配新权限...")
            admin_role = Role.query.filter_by(name='超级管理员').first()
            if admin_role:
                dispatch_unit_permissions = Permission.query.filter(
                    Permission.code.like('dispatch_unit:%')
                ).all()
                
                for perm in dispatch_unit_permissions:
                    # 检查是否已存在角色权限关联
                    existing_role_perm = RolePermission.query.filter_by(
                        role_id=admin_role.id,
                        permission_id=perm.id
                    ).first()
                    
                    if not existing_role_perm:
                        role_permission = RolePermission(
                            role_id=admin_role.id,
                            permission_id=perm.id
                        )
                        db.session.add(role_permission)
                        print(f"✓ 为超级管理员分配权限: {perm.code}")
            
            # 提交所有更改
            db.session.commit()
            print("\n=== 更新完成 ===")
            return True
            
        except Exception as e:
            print(f"错误: {str(e)}")
            db.session.rollback()
            return False


def check_current_status():
    """检查当前菜单和权限状态"""
    app = create_app()
    
    with app.app_context():
        print("=== 当前菜单和权限状态 ===")
        
        # 检查菜单
        print("\n菜单状态:")
        customer_menu = Menu.query.filter_by(code='customer_management').first()
        dispatch_unit_menu = Menu.query.filter_by(code='dispatch_unit_management').first()
        
        if customer_menu:
            print(f"- 客户管理菜单: {customer_menu.name} ({customer_menu.path})")
        if dispatch_unit_menu:
            print(f"- 派车单位管理菜单: {dispatch_unit_menu.name} ({dispatch_unit_menu.path})")
        
        if not customer_menu and not dispatch_unit_menu:
            print("- 未找到相关菜单")
        
        # 检查权限
        print("\n权限状态:")
        customer_perms = Permission.query.filter(
            Permission.code.like('customer:%')
        ).all()
        dispatch_unit_perms = Permission.query.filter(
            Permission.code.like('dispatch_unit:%')
        ).all()
        
        if customer_perms:
            print("客户管理权限:")
            for perm in customer_perms:
                print(f"  - {perm.code}: {perm.name}")
        
        if dispatch_unit_perms:
            print("派车单位管理权限:")
            for perm in dispatch_unit_perms:
                print(f"  - {perm.code}: {perm.name}")
        
        if not customer_perms and not dispatch_unit_perms:
            print("- 未找到相关权限")


def rollback_changes():
    """回滚更改（将派车单位管理改回客户管理）"""
    app = create_app()
    
    with app.app_context():
        print("=== 开始回滚更改 ===")
        
        try:
            # 1. 更新菜单表
            dispatch_unit_menu = Menu.query.filter_by(code='dispatch_unit_management').first()
            if dispatch_unit_menu:
                dispatch_unit_menu.name = '客户管理'
                dispatch_unit_menu.code = 'customer_management'
                dispatch_unit_menu.path = '/basic-data/customers'
                dispatch_unit_menu.component = 'pages/basic-data/CustomerManagement'
                dispatch_unit_menu.icon = 'el-icon-user'
                print("✓ 菜单已回滚")
            
            # 2. 更新权限表
            dispatch_unit_permissions = Permission.query.filter(
                Permission.code.like('dispatch_unit:%')
            ).all()
            
            permission_mapping = {
                'dispatch_unit:read': 'customer:read',
                'dispatch_unit:create': 'customer:create',
                'dispatch_unit:update': 'customer:update',
                'dispatch_unit:delete': 'customer:delete'
            }
            
            for perm in dispatch_unit_permissions:
                old_code = perm.code
                if old_code in permission_mapping:
                    new_code = permission_mapping[old_code]
                    perm.code = new_code
                    perm.name = perm.name.replace('派车单位', '客户')
                    perm.description = perm.description.replace('派车单位', '客户') if perm.description else None
                    print(f"✓ 权限回滚: {old_code} -> {new_code}")
            
            db.session.commit()
            print("\n=== 回滚完成 ===")
            return True
            
        except Exception as e:
            print(f"错误: {str(e)}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            check_current_status()
        elif sys.argv[1] == 'rollback':
            success = rollback_changes()
            if not success:
                sys.exit(1)
        else:
            print("用法:")
            print("  python update_menu_permissions.py        # 执行更新")
            print("  python update_menu_permissions.py check  # 检查当前状态")
            print("  python update_menu_permissions.py rollback # 回滚更改")
    else:
        success = update_customer_to_dispatch_unit()
        if success:
            print("\n检查更新后状态:")
            check_current_status()
        else:
            print("更新失败")
            sys.exit(1)