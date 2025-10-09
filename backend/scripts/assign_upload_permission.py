#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为超级管理员角色分配上传图片权限
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Role, Permission, RolePermission
from app.extensions import db

def assign_upload_permission():
    """为超级管理员角色分配上传图片权限"""
    app = create_app()
    with app.app_context():
        print("开始为超级管理员分配上传图片权限...")
        
        # 查找超级管理员角色
        admin_role = Role.query.filter_by(name='超级管理员').first()
        if not admin_role:
            print("✗ 超级管理员角色不存在")
            return
        
        # 查找上传图片权限
        upload_permission = Permission.query.filter_by(code='upload:image').first()
        if not upload_permission:
            print("✗ upload:image权限不存在")
            return
        
        # 检查是否已经分配了该权限
        existing_role_permission = RolePermission.query.filter_by(
            role_id=admin_role.id,
            permission_id=upload_permission.id
        ).first()
        
        if existing_role_permission:
            print(f"✓ 超级管理员已拥有权限: {upload_permission.name} ({upload_permission.code})")
        else:
            # 分配权限
            role_permission = RolePermission(
                role_id=admin_role.id,
                permission_id=upload_permission.id
            )
            db.session.add(role_permission)
            db.session.commit()
            print(f"✓ 为超级管理员分配权限: {upload_permission.name} ({upload_permission.code})")
        
        print("权限分配完成！")

if __name__ == '__main__':
    assign_upload_permission()