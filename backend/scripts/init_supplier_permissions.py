#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化供应商响应权限脚本
为供应商、班组长、外包管理公司角色分配响应权限
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

# 需要创建的权限
SUPPLIER_PERMISSIONS = [
    {
        'name': '供应商响应',
        'code': 'supplier:respond',
        'description': '供应商响应调度任务',
        'resource_type': 'api',
        'resource_id': '/dispatch/supplier-response',
        'action': 'write'
    },
    {
        'name': '班组派车',
        'code': 'team:assign',
        'description': '班组长派车响应',
        'resource_type': 'api',
        'resource_id': '/dispatch/team-response',
        'action': 'write'
    },
    {
        'name': '外包派车',
        'code': 'outsourcing:assign',
        'description': '外包管理公司派车响应',
        'resource_type': 'api',
        'resource_id': '/dispatch/outsourcing-response',
        'action': 'write'
    }
]

# 角色权限映射
ROLE_PERMISSION_MAPPING = {
    '供应商': ['supplier:respond'],
    '班组长': ['team:assign'],
    '外包管理公司': ['outsourcing:assign'],
    # 兼容英文角色名
    'supplier': ['supplier:respond'],
    'team_leader': ['team:assign'],
    'outsourcing_manager': ['outsourcing:assign']
}

def init_supplier_permissions():
    """初始化供应商响应权限并分配给相应角色"""
    app = create_app()
    
    with app.app_context():
        print("开始初始化供应商响应权限...")
        
        # 1. 创建权限
        created_permissions = {}
        for perm_data in SUPPLIER_PERMISSIONS:
            permission = Permission.query.filter_by(code=perm_data['code']).first()
            if not permission:
                permission = Permission(
                    name=perm_data['name'],
                    code=perm_data['code'],
                    description=perm_data['description'],
                    resource_type=perm_data['resource_type'],
                    resource_id=perm_data['resource_id'],
                    action=perm_data['action']
                )
                db.session.add(permission)
                db.session.commit()
                print(f"✓ 创建权限: {permission.name} ({permission.code})")
            else:
                print(f"✓ 权限已存在: {permission.name} ({permission.code})")
            
            created_permissions[permission.code] = permission
        
        # 2. 为角色分配权限
        for role_name, permission_codes in ROLE_PERMISSION_MAPPING.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                print(f"⚠ 未找到角色: {role_name}")
                continue
            
            print(f"\n为角色 '{role.name}' 分配权限:")
            
            for permission_code in permission_codes:
                permission = created_permissions.get(permission_code)
                if not permission:
                    print(f"  ⚠ 权限不存在: {permission_code}")
                    continue
                
                # 检查权限是否已分配
                existing = RolePermission.query.filter_by(
                    role_id=role.id,
                    permission_id=permission.id
                ).first()
                
                if not existing:
                    role_permission = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    db.session.add(role_permission)
                    db.session.commit()
                    print(f"  ✓ 分配权限: {permission.name}")
                else:
                    print(f"  ✓ 权限已存在: {permission.name}")
        
        print("\n供应商响应权限初始化完成！")
        
        # 3. 验证权限分配
        print("\n验证权限分配:")
        for role_name in ['供应商', '班组长', '外包管理公司', 'supplier', 'team_leader', 'outsourcing_manager']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                permissions = role.get_permission_codes()
                response_permissions = [p for p in permissions if 'respond' in p or 'assign' in p]
                if response_permissions:
                    print(f"  {role.name}: {', '.join(response_permissions)}")
                else:
                    print(f"  {role.name}: 无响应权限")

if __name__ == '__main__':
    init_supplier_permissions()