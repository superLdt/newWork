#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的菜单项
"""

from app import create_app
from app.models import Menu

def check_menus():
    """检查菜单"""
    app = create_app()
    with app.app_context():
        print("=== 当前数据库中的菜单项 ===")
        menus = Menu.query.all()
        for menu in menus:
            print(f"{menu.id}: {menu.name} ({menu.code}) - {menu.path}")
        print("========================")

if __name__ == '__main__':
    check_menus()