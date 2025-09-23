#!/usr/bin/env python3
"""
添加 dispatch_status_history 表的 next_handler_role 和 next_handler_user_id 字段
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def add_columns():
    """添加缺失的字段"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已经存在这些字段
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('dispatch_status_history')]
        
        if 'next_handler_role' not in columns:
            print("添加 next_handler_role 字段...")
            db.session.execute(text('ALTER TABLE dispatch_status_history ADD COLUMN next_handler_role VARCHAR(50)'))
        
        if 'next_handler_user_id' not in columns:
            print("添加 next_handler_user_id 字段...")
            db.session.execute(text('ALTER TABLE dispatch_status_history ADD COLUMN next_handler_user_id INTEGER'))
        
        db.session.commit()
        print("字段添加完成!")

if __name__ == '__main__':
    add_columns()