#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app
from app.models import Role, Permission, RolePermission
from app.extensions import db

def assign_menu_permission():
    app = create_app()
    with app.app_context():
        # 获取超级管理员角色
        admin_role = Role.query.filter_by(name='超级管理员').first()
        if not admin_role:
            print('超级管理员角色不存在')
            return
        
        # 获取菜单管理权限
        menu_perm = Permission.query.filter_by(code='menu:read').first()
        if not menu_perm:
            print('菜单管理权限不存在')
            return
        
        # 检查是否已经分配
        existing = RolePermission.query.filter_by(
            role_id=admin_role.id, 
            permission_id=menu_perm.id
        ).first()
        
        if existing:
            print('权限已存在')
            return
        
        # 分配权限
        rp = RolePermission(
            role_id=admin_role.id,
            permission_id=menu_perm.id
        )
        
        db.session.add(rp)
        db.session.commit()
        
        print(f'成功为角色 "{admin_role.name}" 分配菜单管理权限')

if __name__ == '__main__':
    assign_menu_permission()