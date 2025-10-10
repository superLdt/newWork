#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为Dashboard页面添加菜单项的脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from app.models import Menu
from app.extensions import db

def add_dashboard_menu():
    """添加Dashboard菜单项"""
    app = create_app()
    with app.app_context():
        # 检查是否已存在Dashboard菜单
        existing_menu = Menu.query.filter_by(code='dashboard').first()
        if existing_menu:
            print("Dashboard菜单项已存在:")
            print(f"ID: {existing_menu.id}")
            print(f"名称: {existing_menu.name}")
            print(f"代码: {existing_menu.code}")
            print(f"路径: {existing_menu.path}")
            return existing_menu
        
        # 创建Dashboard菜单项
        dashboard_menu = Menu(
            name='仪表盘',
            code='dashboard',
            path='/',
            component='pages/Dashboard',
            icon='el-icon-data-board',
            parent_id=None,
            sort_order=0,  # 作为首页，排序为0
            is_active=True
        )
        
        db.session.add(dashboard_menu)
        db.session.commit()
        
        print("成功创建Dashboard菜单项:")
        print(f"ID: {dashboard_menu.id}")
        print(f"名称: {dashboard_menu.name}")
        print(f"代码: {dashboard_menu.code}")
        print(f"路径: {dashboard_menu.path}")
        
        return dashboard_menu

if __name__ == '__main__':
    add_dashboard_menu()