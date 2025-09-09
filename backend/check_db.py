#!/usr/bin/env python3
"""
检查数据库表结构
"""

from app import create_app
from app.extensions import db
from sqlalchemy import inspect

def check_database():
    """检查数据库表"""
    app = create_app('development')
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"数据库中的表: {tables}")
        
        # 检查必要的表是否存在
        required_tables = ['User', 'Role', 'user_role', 'Company']
        missing_tables = []
        
        for table in required_tables:
            if table not in tables:
                missing_tables.append(table)
            else:
                print(f"✅ 表 {table} 存在")
        
        if missing_tables:
            print(f"❌ 缺少表: {missing_tables}")
            print("尝试创建所有表...")
            try:
                db.create_all()
                print("✅ 所有表创建完成")
            except Exception as e:
                print(f"❌ 创建表失败: {e}")
        else:
            print("✅ 所有必要的表都存在")
        
        # 再次检查
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"最终数据库表: {tables}")

if __name__ == '__main__':
    check_database()