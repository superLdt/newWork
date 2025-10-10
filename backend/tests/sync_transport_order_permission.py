#!/usr/bin/env python3
"""
同步运输订单菜单权限脚本
为超级管理员角色添加运输订单菜单权限
"""
import os
import sys
from app import create_app, db
from app.models.permission import Permission
from app.models.role import Role
from app.models.menu import Menu

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = create_app()

# 运输订单权限配置
TRANSPORT_ORDER_PERMISSION = {
    'name': '运输订单菜单',
    'code': 'menu:transport_orders',
    'description': '访问运输订单菜单',
    'resource_type': 'menu',
    'resource_id': '/dispatch/orders',
    'action': 'read'
}

def sync_transport_order_permission():
    """创建运输订单菜单权限并分配给超级管理员角色。"""
    with app.app_context():
        print("开始同步运输订单菜单权限...")
        
        # 创建或获取运输订单权限
        permission = Permission.query.filter_by(code='menu:transport_orders').first()
        if not permission:
            permission = Permission(
                name=TRANSPORT_ORDER_PERMISSION['name'],
                code=TRANSPORT_ORDER_PERMISSION['code'],
                description=TRANSPORT_ORDER_PERMISSION['description'],
                resource_type=TRANSPORT_ORDER_PERMISSION['resource_type'],
                resource_id=TRANSPORT_ORDER_PERMISSION['resource_id'],
                action=TRANSPORT_ORDER_PERMISSION['action']
            )
            db.session.add(permission)
            db.session.commit()
            print(f"✓ 创建权限: {permission.name} ({permission.code})")
        else:
            print(f"✓ 权限已存在: {permission.name} ({permission.code})")
        
        # 获取运输订单菜单
        transport_menu = Menu.query.filter_by(code='transport_orders').first()
        if transport_menu:
            print(f"✓ 找到运输订单菜单: {transport_menu.name} (ID: {transport_menu.id})")
        else:
            print("⚠ 未找到运输订单菜单")
        
        # 为超级管理员角色分配权限
        admin_role = Role.query.filter_by(name='供应商').first()
        if admin_role:
            # 检查权限是否已存在
            from app.models.role_permission import RolePermission
            existing = RolePermission.query.filter_by(
                role_id=admin_role.id,
                permission_id=permission.id
            ).first()
            
            if not existing:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id
                )
                db.session.add(role_permission)
                db.session.commit()
                print(f"✓ 为角色 '{admin_role.name}' 分配权限: {permission.name}")
            else:
                print(f"✓ 角色 '{admin_role.name}' 已拥有权限: {permission.name}")
        else:
            print("⚠ 未找到供应商角色")
        
        print("运输订单菜单权限同步完成！")

if __name__ == '__main__':
    sync_transport_order_permission()