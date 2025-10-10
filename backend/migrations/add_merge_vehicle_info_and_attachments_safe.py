#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全的数据库迁移脚本：扩展合并记录表和创建操作附件表
使用Flask-Migrate/Alembic风格的迁移
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate_database():
    """执行数据库迁移"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("开始数据库迁移...")
            
            # 1. 扩展vehicle_merge_records表
            print("1. 扩展vehicle_merge_records表...")
            
            # 检查表是否存在
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='vehicle_merge_records'"
            )).fetchone()
            
            if result:
                # 检查字段是否已存在
                columns_result = db.session.execute(text("PRAGMA table_info(vehicle_merge_records)")).fetchall()
                existing_columns = [col[1] for col in columns_result]
                
                # 添加新增车辆信息字段
                new_columns = [
                    ('new_vehicle_license_plate', 'VARCHAR(20)'),
                    ('new_vehicle_tonnage', 'FLOAT'),
                    ('new_vehicle_volume', 'FLOAT'),
                    ('new_vehicle_type', 'VARCHAR(20)'),
                    ('new_vehicle_carriage_number', 'VARCHAR(50)')
                ]
                
                for col_name, col_type in new_columns:
                    if col_name not in existing_columns:
                        try:
                            db.session.execute(text(f"ALTER TABLE vehicle_merge_records ADD COLUMN {col_name} {col_type}"))
                            print(f"  添加字段: {col_name}")
                        except Exception as e:
                            print(f"  添加字段 {col_name} 失败: {e}")
                    else:
                        print(f"  字段已存在: {col_name}")
            else:
                print("  vehicle_merge_records表不存在，跳过扩展")
            
            # 2. 创建operation_attachments表
            print("2. 创建operation_attachments表...")
            
            # 检查表是否已存在
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='operation_attachments'"
            )).fetchone()
            
            if not result:
                create_table_sql = """
                CREATE TABLE operation_attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type VARCHAR(20) NOT NULL,
                    operation_id INTEGER NOT NULL,
                    attachment_type VARCHAR(50) NOT NULL,
                    file_name VARCHAR(255),
                    file_path VARCHAR(500),
                    file_size INTEGER,
                    mime_type VARCHAR(100),
                    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by INTEGER,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (uploaded_by) REFERENCES User (id)
                )
                """
                db.session.execute(text(create_table_sql))
                print("  创建operation_attachments表成功")
                
                # 创建索引
                db.session.execute(text("CREATE INDEX idx_operation_attachments_operation ON operation_attachments(operation_type, operation_id)"))
                db.session.execute(text("CREATE INDEX idx_operation_attachments_type ON operation_attachments(attachment_type)"))
                print("  创建索引成功")
            else:
                print("  operation_attachments表已存在")
            
            # 提交事务
            db.session.commit()
            print("数据库迁移完成！")
            
            # 验证表结构
            print("\n验证表结构:")
            
            # 验证vehicle_merge_records表结构
            merge_columns = db.session.execute(text("PRAGMA table_info(vehicle_merge_records)")).fetchall()
            print("vehicle_merge_records表结构:")
            for col in merge_columns:
                print(f"  {col[1]} {col[2]}")
            
            # 验证operation_attachments表结构
            attachment_columns = db.session.execute(text("PRAGMA table_info(operation_attachments)")).fetchall()
            print("\noperation_attachments表结构:")
            for col in attachment_columns:
                print(f"  {col[1]} {col[2]}")
                
        except Exception as e:
            print(f"迁移失败: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_database()