#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性脚本：彻底移除“供应商管理”菜单（默认 id=18）及其所有子菜单，
同时删除对应的 MenuPermission 关联记录。

用法：
  python scripts/remove_supplier_management_menu.py --execute [--id 18]
  python scripts/remove_supplier_management_menu.py --dry-run [--id 18]
"""

import os
import sys
import argparse


def ensure_backend_on_path():
    """确保 backend 目录在 sys.path 中，以便导入 app 模块。"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)


def get_app_and_db():
    from app import create_app
    from app.extensions import db
    app = create_app()
    return app, db


def collect_descendant_menu_ids(db, Menu, root_id):
    """收集 root_id 及其所有子菜单的 id 列表（递归）。"""
    ids = []

    def dfs(mid):
        ids.append(mid)
        children = db.session.query(Menu.id).filter(Menu.parent_id == mid).all()
        for cid_tuple in children:
            cid = cid_tuple[0] if isinstance(cid_tuple, tuple) else cid_tuple
            dfs(cid)

    dfs(root_id)
    return ids


def remove_menu_and_permissions(root_id=18, dry_run=False):
    ensure_backend_on_path()
    from app.models.menu import Menu
    from app.models.menu_permission import MenuPermission

    app, db = get_app_and_db()
    with app.app_context():
        target = db.session.query(Menu).filter(Menu.id == root_id).first()
        if not target:
            print(f"未找到 id={root_id} 的菜单记录，可能已被删除。")
            return 0, 0, []

        all_ids = collect_descendant_menu_ids(db, Menu, root_id)
        print(f"将处理菜单ID列表：{all_ids}")

        # 统计待删除的关联与菜单数量
        perm_count = db.session.query(MenuPermission).filter(MenuPermission.menu_id.in_(all_ids)).count()
        menu_count = db.session.query(Menu).filter(Menu.id.in_(all_ids)).count()
        print(f"待删除 MenuPermission 记录数：{perm_count}")
        print(f"待删除 Menu 记录数：{menu_count}")

        if dry_run:
            print("干跑模式：不执行实际删除。")
            return perm_count, menu_count, all_ids

        # 先删除权限关联
        db.session.query(MenuPermission).filter(MenuPermission.menu_id.in_(all_ids)).delete(synchronize_session=False)
        # 再删除菜单
        db.session.query(Menu).filter(Menu.id.in_(all_ids)).delete(synchronize_session=False)
        db.session.commit()

        print("删除完成并已提交。")
        return perm_count, menu_count, all_ids


def main():
    parser = argparse.ArgumentParser(description='彻底移除供应商管理菜单及其子菜单和权限关联')
    parser.add_argument('--id', type=int, default=18, help='要删除的根菜单ID，默认18')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--execute', action='store_true', help='执行删除')
    group.add_argument('--dry-run', action='store_true', help='仅打印将要删除的记录，不执行')
    args = parser.parse_args()

    perm_count, menu_count, ids = remove_menu_and_permissions(root_id=args.id, dry_run=args.dry_run)
    print(f"结果：MenuPermission 删除数（或将删除）：{perm_count}，Menu 删除数（或将删除）：{menu_count}，涉及ID：{ids}")


if __name__ == '__main__':
    main()