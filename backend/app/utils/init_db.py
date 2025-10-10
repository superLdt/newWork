#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建所有表并确保与模型一致
"""

import os
import sys

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import *

def init_database():
    """初始化数据库"""
    # 创建Flask应用
    app = create_app('development')
    
    with app.app_context():
        # 删除所有现有表
        print("Dropping all tables...")
        db.drop_all()
        
        # 创建所有表
        print("Creating all tables...")
        db.create_all()
        
        print("Database initialized successfully!")
        print("Tables created:")
        for table in db.metadata.tables:
            print(f"  - {table}")

if __name__ == "__main__":
    init_database()