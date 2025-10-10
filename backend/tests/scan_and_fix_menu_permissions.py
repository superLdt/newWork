#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用脚本：自动扫描并补齐菜单权限
目标：确保每个子菜单都至少绑定一个菜单类权限（menu:*），以便角色-菜单保存能够正确持久化到角色权限。

执行要点：
- 对于未绑定任何权限的菜单，自动创建权限：
  - code: menu:{menu.code}
  - name: {menu.name}菜单
  - description: 访问{menu.name}菜单
  - resource_type: menu
  - resource_id: menu.path（若无path，回退为 /{menu.code.replace('_','-')}）
  - action: read
- 将创建/找到的权限与该菜单通过 MenuPermission 进行绑定。

可选参数：
- --include-inactive: 是否包含未启用菜单（默认：否）
- --only-submenus: 仅处理子菜单（parent_id!=None）（默认：是）
- --dry-run: 仅查看将要进行的更改，不写入数据库（默认：否）

用法示例：
  python tests/scan_and_fix_menu_permissions.py
  python tests/scan_and_fix_menu_permissions.py --include-inactive
  python tests/scan_and_fix_menu_permissions.py --only-submenus=false
  python tests/scan_and_fix_menu_permissions.py --dry-run
"""
import os
import sys
import argparse

# 将项目根目录加入 Python 路径（以便 from app import create_app 等可用）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db
from app.models import Menu, Permission, MenuPermission


def ensure_menu_permission_for(menu, dry_run=False):
    """
    确保指定菜单拥有至少一个 menu:* 类型的权限，并完成 MenuPermission 绑定。

    Returns:
        dict: { 'menu_id': int, 'created_permission': bool, 'bound_permission': bool, 'permission_code': str }
    """
    # 1) 已有绑定？
    existing_bind_count = MenuPermission.query.filter_by(menu_id=menu.id).count()
    if existing_bind_count > 0:
        return {
            'menu_id': menu.id,
            'created_permission': False,
            'bound_permission': False,
            'permission_code': None
        }

    # 2) 生成目标权限代码
    perm_code = f"menu:{menu.code}"

    # 3) 查找或创建 Permission
    perm = Permission.query.filter_by(code=perm_code).first()
    created_permission = False
    if not perm:
        # 构造 resource_id：优先使用菜单 path；若无，回退到 /{code} （下划线转为连接符，便于URL风格）
        resource_id = menu.path or f"/{menu.code.replace('_', '-')}"
        perm = Permission(
            name=f"{menu.name}菜单",
            code=perm_code,
            description=f"访问{menu.name}菜单",
            resource_type='menu',
            resource_id=resource_id,
            action='read'
        )
        if not dry_run:
            db.session.add(perm)
            # 立刻flush以便获得自增ID，供后续MenuPermission绑定使用
            db.session.flush()
        created_permission = True

    # 4) 建立 MenuPermission 绑定
    bound_permission = False
    if not dry_run:
        mp = MenuPermission.bind_permission(menu.id, perm.id)
        bound_permission = True

    return {
        'menu_id': menu.id,
        'created_permission': created_permission,
        'bound_permission': bound_permission,
        'permission_code': perm_code
    }


def scan_and_fix(include_inactive=False, only_submenus=True, dry_run=False):
    app = create_app()
    with app.app_context():
        print("=== 自动扫描并补齐菜单权限（menu:*） ===")
        print(f"包含未启用菜单: {include_inactive}")
        print(f"仅处理子菜单: {only_submenus}")
        print(f"Dry-run: {dry_run}")

        # 选择待处理的菜单集合
        query = Menu.query
        if not include_inactive:
            query = query.filter(Menu.is_active == True)
        if only_submenus:
            query = query.filter(Menu.parent_id.isnot(None))
        menus = query.order_by(Menu.sort_order.asc()).all()

        total = len(menus)
        fixed = 0
        created_perm_count = 0
        bound_count = 0

        print(f"待检查菜单数量: {total}")
        for m in menus:
            result = ensure_menu_permission_for(m, dry_run=dry_run)
            if result['permission_code']:
                action_msgs = []
                if result['created_permission']:
                    created_perm_count += 1
                    action_msgs.append("创建Permission")
                if result['bound_permission']:
                    bound_count += 1
                    action_msgs.append("绑定MenuPermission")
                if action_msgs:
                    fixed += 1
                    print(f"✓ 修复菜单: {m.name} ({m.code}) -> {', '.join(action_msgs)} [{result['permission_code']}]")

        # 统一提交
        if not dry_run:
            db.session.commit()

        print("\n=== 扫描完成 ===")
        print(f"总计检查菜单: {total}")
        print(f"涉及修复菜单: {fixed}")
        print(f"新建权限数量: {created_perm_count}")
        print(f"建立/补齐绑定数量: {bound_count}")
        if dry_run:
            print("(dry-run 模式下未对数据库进行写入)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='自动扫描并补齐菜单权限（menu:*）')
    parser.add_argument('--include-inactive', action='store_true', help='包含未启用菜单')
    parser.add_argument('--only-submenus', dest='only_submenus', default=True, type=lambda v: str(v).lower() not in ('false', '0', 'no'), help='仅处理子菜单（默认：true）')
    parser.add_argument('--dry-run', action='store_true', help='仅查看将要进行的更改，不写入数据库')
    args = parser.parse_args()

    scan_and_fix(
        include_inactive=args.include_inactive,
        only_submenus=args.only_submenus,
        dry_run=args.dry_run
    )