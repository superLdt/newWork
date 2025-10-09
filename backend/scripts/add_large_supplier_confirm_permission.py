#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为大容积供应商角色添加supplier:confirm权限
解决大容积供应商确认任务时403权限错误的问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Role, Permission, RolePermission
from app.extensions import db

def add_large_supplier_confirm_permission():
    """为大容积供应商角色添加supplier:confirm权限"""
    app = create_app()
    with app.app_context():
        print("开始为大容积供应商角色添加supplier:confirm权限...")
        
        # 查找大容积供应商角色
        large_supplier_role = Role.query.filter_by(name='大容积供应商').first()
        if not large_supplier_role:
            print("✗ 未找到大容积供应商角色")
            return False
        
        print(f"✓ 找到大容积供应商角色: {large_supplier_role.name} (ID: {large_supplier_role.id})")
        
        # 查找supplier:confirm权限
        supplier_confirm_perm = Permission.query.filter_by(code='supplier:confirm').first()
        if not supplier_confirm_perm:
            print("✗ 未找到supplier:confirm权限")
            return False
        
        print(f"✓ 找到supplier:confirm权限: {supplier_confirm_perm.name} (ID: {supplier_confirm_perm.id})")
        
        # 检查是否已经有这个权限
        existing_role_permission = RolePermission.query.filter_by(
            role_id=large_supplier_role.id,
            permission_id=supplier_confirm_perm.id
        ).first()
        
        if existing_role_permission:
            print("✓ 大容积供应商角色已有supplier:confirm权限，无需重复添加")
            return True
        
        # 添加权限
        try:
            role_permission = RolePermission(
                role_id=large_supplier_role.id,
                permission_id=supplier_confirm_perm.id
            )
            db.session.add(role_permission)
            db.session.commit()
            
            print("✓ 成功为大容积供应商角色添加supplier:confirm权限")
            
            # 验证添加结果
            verification = RolePermission.query.filter_by(
                role_id=large_supplier_role.id,
                permission_id=supplier_confirm_perm.id
            ).first()
            
            if verification:
                print("✓ 权限添加验证成功")
                return True
            else:
                print("✗ 权限添加验证失败")
                return False
                
        except Exception as e:
            print(f"✗ 添加权限时发生错误: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = add_large_supplier_confirm_permission()
    if success:
        print("\n权限配置完成！大容积供应商现在可以进行任务确认操作。")
    else:
        print("\n权限配置失败！请检查错误信息。")
        sys.exit(1)