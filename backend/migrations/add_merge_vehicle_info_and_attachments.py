#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：扩展合并记录表和创建操作附件表
1. 扩展vehicle_merge_records表，添加新增车辆信息字段
2. 创建operation_attachments表用于统一管理操作附件
"""

import sqlite3
import os
import time

def migrate_merge_and_attachments():
    """扩展合并记录表并创建操作附件表"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    # 设置较短的超时时间，避免长时间等待
    conn = sqlite3.connect(db_path, timeout=5.0)
    cursor = conn.cursor()
    
    # 设置WAL模式以减少锁冲突
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
    except Exception as e:
        print(f"设置数据库模式失败: {e}")
    
    try:
        print("开始数据库迁移...")
        
        # 1. 扩展vehicle_merge_records表
        print("1. 扩展vehicle_merge_records表...")
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicle_merge_records'")
        if cursor.fetchone():
            # 检查字段是否已存在
            cursor.execute("PRAGMA table_info(vehicle_merge_records)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # 添加新增车辆信息字段
            new_columns = [
                ('new_vehicle_license_plate', 'VARCHAR(20)', '新增车辆车牌号'),
                ('new_vehicle_tonnage', 'FLOAT', '新增车辆吨位'),
                ('new_vehicle_volume', 'FLOAT', '新增车辆容积'),
                ('new_vehicle_type', 'VARCHAR(20)', '新增车辆类型'),
                ('new_vehicle_carriage_number', 'VARCHAR(50)', '新增车辆车厢号')
            ]
            
            for col_name, col_type, comment in new_columns:
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE vehicle_merge_records ADD COLUMN {col_name} {col_type}")
                    print(f"  添加字段: {col_name} ({comment})")
                else:
                    print(f"  字段已存在: {col_name}")
        else:
            print("  vehicle_merge_records表不存在，跳过扩展")
        
        # 2. 创建operation_attachments表
        print("2. 创建operation_attachments表...")
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operation_attachments'")
        if not cursor.fetchone():
            create_attachments_table_sql = """
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
            cursor.execute(create_attachments_table_sql)
            print("  创建operation_attachments表成功")
            
            # 创建索引
            cursor.execute("CREATE INDEX idx_operation_attachments_operation ON operation_attachments(operation_type, operation_id)")
            cursor.execute("CREATE INDEX idx_operation_attachments_type ON operation_attachments(attachment_type)")
            print("  创建索引成功")
        else:
            print("  operation_attachments表已存在")
        
        # 3. 扩展vehicle_downgrade_records表（为降档操作也添加图片支持的准备）
        print("3. 检查vehicle_downgrade_records表...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicle_downgrade_records'")
        if cursor.fetchone():
            print("  vehicle_downgrade_records表存在，可以使用operation_attachments表管理其附件")
        else:
            print("  vehicle_downgrade_records表不存在")
        
        conn.commit()
        print("数据库迁移完成！")
        
        # 验证新表结构
        print("\n验证表结构:")
        
        # 验证vehicle_merge_records表结构
        cursor.execute("PRAGMA table_info(vehicle_merge_records)")
        merge_columns = cursor.fetchall()
        print("vehicle_merge_records表结构:")
        for col in merge_columns:
            print(f"  {col[1]} {col[2]}")
        
        # 验证operation_attachments表结构
        cursor.execute("PRAGMA table_info(operation_attachments)")
        attachment_columns = cursor.fetchall()
        print("\noperation_attachments表结构:")
        for col in attachment_columns:
            print(f"  {col[1]} {col[2]}")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_merge_and_attachments()