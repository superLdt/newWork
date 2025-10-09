#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
供应商申诉任务菜单初始化脚本
为供应商角色创建申诉任务查看菜单和相关权限
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Menu, Permission, MenuPermission, Role, RolePermission
from app.extensions import db

def init_supplier_appeal_menu():
    """初始化供应商申诉任务菜单"""
    app = create_app()
    with app.app_context():
        print("开始初始化供应商申诉任务菜单...")
        
        try:
            # 1. 查找调度管理父菜单
            dispatch_parent = Menu.query.filter_by(code='dispatch').first()
            if not dispatch_parent:
                print("✗ 调度管理菜单不存在，请先创建调度管理菜单")
                return
            else:
                print("✓ 调度管理菜单已存在")
            
            # 2. 创建或更新申诉任务查看菜单（统一使用 code='appeal_tasks'）
            appeal_menu = Menu.query.filter_by(code='appeal_tasks').first()
            legacy_menu = None
            if not appeal_menu:
                # 兼容旧code
                legacy_menu = Menu.query.filter_by(code='supplier_appeal_tasks').first()
            
            if not appeal_menu and not legacy_menu:
                appeal_menu = Menu(
                    name='申诉任务管理',
                    code='appeal_tasks',
                    path='/dispatch/appeal-tasks',
                    component='pages/supplier/SupplierAppealTasks',
                    icon='el-icon-warning',
                    parent_id=dispatch_parent.id,
                    sort_order=1,
                    is_active=True
                )
                db.session.add(appeal_menu)
                db.session.flush()
                print("✓ 创建申诉任务管理菜单 (code=appeal_tasks)")
            elif legacy_menu and not appeal_menu:
                # 将旧菜单更新为新code并修正父级与路径
                legacy_menu.code = 'appeal_tasks'
                legacy_menu.parent_id = dispatch_parent.id
                legacy_menu.path = '/dispatch/appeal-tasks'
                legacy_menu.name = legacy_menu.name or '申诉任务管理'
                legacy_menu.component = legacy_menu.component or 'pages/supplier/SupplierAppealTasks'
                appeal_menu = legacy_menu
                db.session.flush()
                print("✓ 已将旧菜单 supplier_appeal_tasks 更新为 appeal_tasks 并迁移到调度管理下")
            else:
                # 确保现有菜单在调度管理下与路径正确
                updated = False
                if appeal_menu.parent_id != dispatch_parent.id:
                    appeal_menu.parent_id = dispatch_parent.id
                    updated = True
                if appeal_menu.path != '/dispatch/appeal-tasks':
                    appeal_menu.path = '/dispatch/appeal-tasks'
                    updated = True
                if updated:
                    db.session.flush()
                    print("✓ 修正申诉任务管理菜单的父级与路径")
                else:
                    print("✓ 申诉任务管理菜单已存在且配置正确")
            
            # 3. 创建相关权限
            permissions_data = [
                {
                    'name': '供应商申诉任务查看',
                    'code': 'supplier:appeal:read',
                    'description': '查看供应商申诉任务列表',
                    'resource_type': 'menu',
                    'resource_id': '/dispatch/appeal-tasks',
                    'action': 'read'
                },
                {
                    'name': '申诉任务菜单',
                    'code': 'menu:appeal_tasks',
                    'description': '访问申诉任务管理菜单',
                    'resource_type': 'menu',
                    'resource_id': '/dispatch/appeal-tasks',
                    'action': 'read'
                },
                {
                    'name': '供应商申诉任务详情',
                    'code': 'supplier:appeal:detail',
                    'description': '查看申诉任务详情',
                    'resource_type': 'api',
                    'resource_id': '/api/v1/dispatch/tasks/*/appeal',
                    'action': 'read'
                },
                {
                    'name': '供应商申诉任务列表',
                    'code': 'supplier:appeal:list',
                    'description': '获取申诉任务列表',
                    'resource_type': 'api',
                    'resource_id': '/api/v1/dispatch/supplier/appeal-tasks',
                    'action': 'read'
                }
            ]
            
            created_permissions = []
            for perm_data in permissions_data:
                existing_perm = Permission.query.filter_by(code=perm_data['code']).first()
                if not existing_perm:
                    perm = Permission(**perm_data)
                    db.session.add(perm)
                    created_permissions.append(perm)
                    print(f"✓ 创建权限: {perm_data['name']}")
                else:
                    created_permissions.append(existing_perm)
                    print(f"✓ 权限已存在: {perm_data['name']}")
            
            db.session.flush()
            
            # 4. 建立菜单与权限的关联
            for perm in created_permissions:
                existing_mp = MenuPermission.query.filter_by(
                    menu_id=appeal_menu.id,
                    permission_id=perm.id
                ).first()
                
                if not existing_mp:
                    mp = MenuPermission(
                        menu_id=appeal_menu.id,
                        permission_id=perm.id
                    )
                    db.session.add(mp)
                    print(f"✓ 关联菜单与权限: {perm.code}")

            # 4.1 限制菜单权限仅供应商可见：删除非供应商角色的 menu:appeal_tasks 绑定
            menu_perm = Permission.query.filter_by(code='menu:appeal_tasks').first()
            if menu_perm:
                non_supplier_roles = Role.query.filter(Role.name.in_(['超级管理员', '区域调度员'])).all()
                for role in non_supplier_roles:
                    rp = RolePermission.query.filter_by(role_id=role.id, permission_id=menu_perm.id).first()
                    if rp:
                        db.session.delete(rp)
                        print(f"✓ 移除 {role.name} 的申诉菜单权限绑定")
            
            # 5. 为供应商角色分配权限
            supplier_role = Role.query.filter_by(name='供应商').first()
            if supplier_role:
                for perm in created_permissions:
                    existing_rp = RolePermission.query.filter_by(
                        role_id=supplier_role.id,
                        permission_id=perm.id
                    ).first()
                    
                    if not existing_rp:
                        rp = RolePermission(
                            role_id=supplier_role.id,
                            permission_id=perm.id
                        )
                        db.session.add(rp)
                        print(f"✓ 为供应商角色分配权限: {perm.code}")
                print("✓ 供应商角色权限分配完成")
            else:
                print("✗ 供应商角色不存在，请先创建供应商角色")
            
            # 6. 为超级管理员分配权限（不分配菜单权限，仅分配API/业务权限）
            admin_role = Role.query.filter_by(name='超级管理员').first()
            if admin_role:
                for perm in created_permissions:
                    # 跳过菜单权限绑定
                    if perm.code == 'menu:appeal_tasks':
                        # 如果已存在绑定则移除，确保菜单仅供应商可见
                        existing_rp = RolePermission.query.filter_by(
                            role_id=admin_role.id,
                            permission_id=perm.id
                        ).first()
                        if existing_rp:
                            db.session.delete(existing_rp)
                            print("✓ 已移除超级管理员的申诉菜单权限绑定")
                        continue
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

            # 7. 为区域调度员分配权限（不分配菜单权限，仅分配API/业务权限）
            dispatcher_role = Role.query.filter_by(name='区域调度员').first()
            if dispatcher_role:
                for perm in created_permissions:
                    if perm.code == 'menu:appeal_tasks':
                        existing_rp = RolePermission.query.filter_by(
                            role_id=dispatcher_role.id,
                            permission_id=perm.id
                        ).first()
                        if existing_rp:
                            db.session.delete(existing_rp)
                            print("✓ 已移除区域调度员的申诉菜单权限绑定")
                        continue
                    existing_rp = RolePermission.query.filter_by(
                        role_id=dispatcher_role.id,
                        permission_id=perm.id
                    ).first()
                    if not existing_rp:
                        rp = RolePermission(
                            role_id=dispatcher_role.id,
                            permission_id=perm.id
                        )
                        db.session.add(rp)
                        print(f"✓ 为区域调度员分配权限: {perm.code}")
            
            db.session.commit()
            print("\n✅ 供应商申诉任务菜单初始化完成！")
            print("\n菜单结构:")
            print("调度管理")
            print("  └── 申诉任务管理 (/dispatch/appeal-tasks, code=appeal_tasks)")
            print("\n权限配置:")
            for perm in created_permissions:
                print(f"  - {perm.name} ({perm.code})")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 初始化失败: {str(e)}")
            raise

def show_menu_status():
    """显示菜单状态"""
    app = create_app()
    with app.app_context():
        print("\n=== 菜单状态检查 ===")
        
        # 检查菜单
        supplier_parent = Menu.query.filter_by(code='supplier_management').first()
        appeal_menu = Menu.query.filter_by(code='supplier_appeal_tasks').first()
        
        print(f"供应商管理菜单: {'✓ 存在' if supplier_parent else '✗ 不存在'}")
        print(f"申诉任务管理菜单: {'✓ 存在' if appeal_menu else '✗ 不存在'}")
        
        # 检查权限
        permissions = Permission.query.filter(
            Permission.code.like('supplier:appeal:%')
        ).all()
        print(f"申诉相关权限数量: {len(permissions)}")
        
        # 检查角色权限
        supplier_role = Role.query.filter_by(name='供应商').first()
        if supplier_role:
            role_perms = RolePermission.query.filter_by(role_id=supplier_role.id).count()
            print(f"供应商角色权限数量: {role_perms}")
        else:
            print("供应商角色: ✗ 不存在")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_menu_status()
    else:
        init_supplier_appeal_menu()