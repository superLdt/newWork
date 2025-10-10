#!/usr/bin/env python3
"""
检查权限分配情况的脚本
"""

from app import create_app
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission

def check_permissions():
    app = create_app()
    with app.app_context():
        print("=== 角色和权限检查 ===")
        
        # 获取所有角色及其权限
        roles = Role.query.all()
        print("\n角色及其权限:")
        for role in roles:
            permissions = role.get_permissions()
            permission_codes = [p.code for p in permissions]
            print(f"  {role.name}: {permission_codes}")
        
        # 检查特定权限
        print("\n检查 dispatch:create 权限:")
        perm = Permission.query.filter_by(code='dispatch:create').first()
        print(f"  权限存在: {perm is not None}")
        if perm:
            print(f"  权限详情: {perm.code} - {perm.name}")
            
            # 检查哪些角色拥有此权限
            print("  拥有此权限的角色:")
            role_perms = RolePermission.query.filter_by(permission_id=perm.id).all()
            for rp in role_perms:
                print(f"    {rp.role.name}")
        
        # 检查车间地调角色
        print("\n检查车间地调角色:")
        workshop_role = Role.query.filter_by(name='车间地调').first()
        if workshop_role:
            permissions = workshop_role.get_permissions()
            permission_codes = [p.code for p in permissions]
            has_create_permission = 'dispatch:create' in permission_codes
            print(f"  角色存在: True")
            print(f"  拥有 dispatch:create 权限: {has_create_permission}")
            print(f"  所有权限: {permission_codes}")
        else:
            print("  角色存在: False")

if __name__ == '__main__':
    check_permissions()