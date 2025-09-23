#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
权限初始化脚本
用于初始化系统所有权限数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Permission
from app.extensions import db

def init_permissions():
    """初始化系统权限"""
    app = create_app()
    with app.app_context():
        print("开始初始化系统权限...")
        
        # 获取默认权限列表
        default_permissions = Permission.get_default_permissions()
        
        created_count = 0
        updated_count = 0
        
        for perm_data in default_permissions:
            # 检查权限是否已存在
            existing_perm = Permission.query.filter_by(code=perm_data['code']).first()
            
            if existing_perm:
                # 更新现有权限
                existing_perm.name = perm_data['name']
                existing_perm.description = perm_data['description']
                existing_perm.resource_type = perm_data['resource_type']
                existing_perm.resource_id = perm_data.get('resource_id', '')
                existing_perm.action = perm_data['action']
                updated_count += 1
                print(f"✓ 更新权限: {perm_data['name']} ({perm_data['code']})")
            else:
                # 创建新权限
                perm = Permission(
                    name=perm_data['name'],
                    code=perm_data['code'],
                    description=perm_data['description'],
                    resource_type=perm_data['resource_type'],
                    resource_id=perm_data.get('resource_id', ''),
                    action=perm_data['action']
                )
                db.session.add(perm)
                created_count += 1
                print(f"✓ 创建权限: {perm_data['name']} ({perm_data['code']})")
        
        # 提交所有更改
        db.session.commit()
        
        print(f"\n权限初始化完成！")
        print(f"创建权限: {created_count} 个")
        print(f"更新权限: {updated_count} 个")
        print(f"总权限数: {Permission.query.count()} 个")

if __name__ == '__main__':
    init_permissions()