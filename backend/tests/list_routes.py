#!/usr/bin/env python3
"""
列出所有Flask路由
"""

import sys
import os

# 添加项目根路径（tests 的上一级目录）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app import create_app

def list_routes():
    """列出所有路由"""
    app = create_app()
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")

if __name__ == '__main__':
    list_routes()