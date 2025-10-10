#!/usr/bin/env python3
"""
为车间地调角色添加 dispatch_unit:read 权限的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.extensions import db

def add_dispatch_unit_read_permission():
    app = create_app()
    with app.app_context():
        # 查找车间地调角色
        workshop_role = Role.query.filter_by(name='车间地调').first()
        if not workshop_role:
            print("错误: 未找到车间地调角色")
            return False
        
        # 查找 dispatch_unit:read 权限
        permission = Permission.query.filter_by(code='dispatch_unit:read').first()
        if not permission:
            print("错误: 未找到 dispatch_unit:read 权限")
            return False
        
        # 检查角色是否已经拥有该权限
        existing_role_permission = RolePermission.query.filter_by(
            role_id=workshop_role.id,
            permission_id=permission.id
        ).first()
        
        if existing_role_permission:
            print("车间地调角色已经拥有 dispatch_unit:read 权限")
            return True
        
        # 为车间地调角色添加权限
        role_permission = RolePermission(
            role_id=workshop_role.id,
            permission_id=permission.id
        )
        try:
            db.session.add(role_permission)
            db.session.commit()
            print(f"✓ 成功为车间地调角色添加 dispatch_unit:read 权限")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"✗ 添加权限失败: {str(e)}")
            return False

if __name__ == '__main__':
    print("=== 为车间地调角色添加 dispatch_unit:read 权限 ===")
    success = add_dispatch_unit_read_permission()
    if success:
        print("=== 完成 ===")
    else:
        print("=== 失败 ===")