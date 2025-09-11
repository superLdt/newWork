#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
同步并授予调度（dispatch:*) 权限的脚本
- 将 app.models.permission.Permission.get_default_permissions() 中的 dispatch 权限同步到数据库
- 将这些权限授予『超级管理员』『区域调度员』角色（如不存在则创建）

用法：
  python tests/sync_dispatch_permissions.py
"""

import os
import sys
# 将后端项目根目录加入到模块搜索路径，确保可以导入 app 包
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User

DISPATCH_CODES = [
    'dispatch:read',
    'dispatch:create',
    'dispatch:update',
    'dispatch:approve',
    'dispatch:assign',
    'dispatch:complete'
]

TARGET_ROLES = [
    {'name': '超级管理员', 'description': '系统最高权限，可管理所有功能'},
    {'name': '区域调度员', 'description': '负责任务审核、派车管理'}
]

DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'admin123',  # 开发环境默认密码，生产请修改
    'full_name': '系统管理员',
    'email': 'admin@example.com'
}

def ensure_roles():
    """确保目标角色存在，不存在则创建。"""
    created = []
    for role_def in TARGET_ROLES:
        role = Role.query.filter_by(name=role_def['name']).first()
        if not role:
            role = Role(name=role_def['name'], description=role_def.get('description', ''))
            db.session.add(role)
            created.append(role_def['name'])
    if created:
        db.session.commit()
        print('✓ 创建角色: ' + ', '.join(created))


def ensure_admin_user():
    """确保存在一个可登录的管理员账号，并分配『超级管理员』角色。"""
    user = User.query.filter_by(username=DEFAULT_ADMIN['username']).first()
    created = False
    if not user:
        user = User(
            username=DEFAULT_ADMIN['username'],
            full_name=DEFAULT_ADMIN['full_name'],
            email=DEFAULT_ADMIN['email'],
            is_active=True
        )
        user.set_password(DEFAULT_ADMIN['password'])
        db.session.add(user)
        db.session.commit()
        created = True
        print(f"✓ 创建管理员用户: {user.username}")

    # 分配『超级管理员』角色
    admin_role = Role.query.filter_by(name='超级管理员').first()
    if not admin_role:
        # 兜底：若角色仍不存在，先创建
        admin_role = Role(name='超级管理员', description='系统最高权限，可管理所有功能')
        db.session.add(admin_role)
        db.session.commit()

    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.session.commit()
        print(f"✓ 为用户 {user.username} 分配角色: 超级管理员")
    else:
        print(f"✓ 用户 {user.username} 已具有角色: 超级管理员")

    if created:
        print(f"默认管理员账号 -> 用户名: {DEFAULT_ADMIN['username']} 密码: {DEFAULT_ADMIN['password']}")


def sync_dispatch_permissions():
    """插入缺失的 dispatch 权限。"""
    defaults = {p['code']: p for p in Permission.get_default_permissions() if p['code'].startswith('dispatch:')}
    created = []
    for code in DISPATCH_CODES:
        if code not in defaults:
            print(f"! 警告: 默认权限清单中未找到 {code}，请检查 app.models.permission.Permission.get_default_permissions")
            continue
        existing = Permission.query.filter_by(code=code).first()
        if not existing:
            data = defaults[code]
            perm = Permission(
                name=data['name'],
                code=data['code'],
                description=data.get('description', ''),
                resource_type=data['resource_type'],
                resource_id=data.get('resource_id', ''),
                action=data['action']
            )
            db.session.add(perm)
            created.append(code)
    if created:
        db.session.commit()
        print('✓ 创建权限: ' + ', '.join(created))
    else:
        print('✓ 所有 dispatch 权限已存在')


def grant_permissions_to_roles():
    """为目标角色授予 dispatch 权限。"""
    # 获取所有目标权限
    perms = Permission.query.filter(Permission.code.in_(DISPATCH_CODES)).all()
    code_to_perm = {p.code: p for p in perms}
    missing = [c for c in DISPATCH_CODES if c not in code_to_perm]
    if missing:
        print('✗ 缺少权限，无法授予: ' + ', '.join(missing))
        return

    for role_def in TARGET_ROLES:
        role = Role.query.filter_by(name=role_def['name']).first()
        if not role:
            print(f"✗ 角色不存在，跳过: {role_def['name']}")
            continue
        granted_codes = []
        for code in DISPATCH_CODES:
            rp = RolePermission.grant_permission(role.id, code_to_perm[code].id)
            if rp:
                granted_codes.append(code)
        if granted_codes:
            db.session.commit()
        print(f"✓ 为角色 {role.name} 授予权限: {', '.join(DISPATCH_CODES)}")


def main():
    app = create_app()
    with app.app_context():
        print('=== 同步调度权限并授予角色 ===')
        ensure_roles()
        ensure_admin_user()
        sync_dispatch_permissions()
        grant_permissions_to_roles()
        print('=== 完成 ===')

if __name__ == '__main__':
    main()