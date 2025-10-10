#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查并修复“供应商管理”菜单脚本

用法：
  python scripts/check_supplier_management_menu.py --print   # 仅打印状态
  python scripts/check_supplier_management_menu.py --disable # 禁用菜单（is_active=False）
"""

import sys
import os
from typing import List

# 将后端目录加入模块搜索路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from app import create_app
from app.extensions import db
from app.models import Menu


def find_supplier_management_menus() -> List[Menu]:
    """查找与供应商管理相关的菜单记录"""
    q = Menu.query.filter(
        (Menu.name == '供应商管理') |
        (Menu.code == 'supplier_management') |
        (Menu.path == 'supplier_management') |
        (Menu.path.like('%supplier%'))
    ).order_by(Menu.sort_order.asc())
    return q.all()


def main():
    # 解析参数
    disable = '--disable' in sys.argv
    # 创建应用并推入上下文
    app = create_app('development')
    with app.app_context():
        menus = find_supplier_management_menus()
        if not menus:
            print('[INFO] 未找到与“供应商管理”相关的菜单记录。')
            return

        print('[INFO] 找到如下菜单记录:')
        for m in menus:
            print(f"  id={m.id}, name={m.name}, code={m.code}, path={m.path}, "
                  f"parent_id={m.parent_id}, is_active={m.is_active}, sort_order={m.sort_order}")

        if disable:
            changed = 0
            for m in menus:
                if m.is_active:
                    m.is_active = False
                    changed += 1
            if changed:
                db.session.commit()
                print(f'[OK] 已禁用 {changed} 条菜单记录（is_active=False）。')
            else:
                print('[INFO] 所有相关菜单已是禁用状态，无需变更。')


if __name__ == '__main__':
    main()