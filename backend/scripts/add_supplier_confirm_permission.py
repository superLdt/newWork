#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加供应商确认权限的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

def add_supplier_confirm_permission():
    """添加供应商确认权限"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查权限是否已存在
            existing_permission = Permission.query.filter_by(code='supplier:confirm').first()
            if existing_permission:
                print("供应商确认权限已存在，跳过创建")
                return
            
            # 创建供应商确认权限
            permission = Permission(
                name='供应商确认',
                code='supplier:confirm',
                description='供应商确认调度任务',
                resource_type='api',
                resource_id='/dispatch/tasks/*/confirm',
                action='write'
            )
            
            db.session.add(permission)
            db.session.commit()
            
            print(f"成功创建权限: {permission.name} ({permission.code})")
            
            # 为供应商角色分配权限
            supplier_role = Role.query.filter_by(name='供应商').first()
            if supplier_role:
                # 检查角色权限关联是否已存在
                existing_role_permission = RolePermission.query.filter_by(
                    role_id=supplier_role.id,
                    permission_id=permission.id
                ).first()
                
                if not existing_role_permission:
                    role_permission = RolePermission(
                        role_id=supplier_role.id,
                        permission_id=permission.id
                    )
                    db.session.add(role_permission)
                    db.session.commit()
                    print(f"成功为角色 '{supplier_role.name}' 分配权限 '{permission.name}'")
                else:
                    print(f"角色 '{supplier_role.name}' 已拥有权限 '{permission.name}'")
            else:
                print("警告: 未找到供应商角色，请手动分配权限")
            
        except Exception as e:
            db.session.rollback()
            print(f"添加供应商确认权限失败: {str(e)}")
            raise

if __name__ == '__main__':
    add_supplier_confirm_permission()