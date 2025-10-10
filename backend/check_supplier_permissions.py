#!/usr/bin/env python3
"""
查询供应商角色的权限配置
"""
import sqlite3

def check_supplier_permissions():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 查询供应商角色的权限
    cursor.execute("""
        SELECT r.name, p.code, p.name, p.description
        FROM Role r 
        JOIN RolePermission rp ON r.id = rp.role_id 
        JOIN Permission p ON rp.permission_id = p.id 
        WHERE r.name = '供应商'
        ORDER BY p.code
    """)
    perms = cursor.fetchall()
    
    print('供应商角色权限:')
    if perms:
        for p in perms:
            print(f'  {p[1]} - {p[2]} ({p[3]})')
    else:
        print('  无权限配置')
    
    # 查询申诉相关权限
    print('\n申诉相关权限:')
    cursor.execute("""
        SELECT code, name, description
        FROM Permission 
        WHERE code LIKE '%appeal%' OR name LIKE '%申诉%'
        ORDER BY code
    """)
    appeal_perms = cursor.fetchall()
    
    if appeal_perms:
        for p in appeal_perms:
            print(f'  {p[0]} - {p[1]} ({p[2]})')
    else:
        print('  无申诉相关权限')
    
    # 检查供应商角色是否有申诉权限
    print('\n供应商角色申诉权限检查:')
    cursor.execute("""
        SELECT p.code, p.name
        FROM Role r 
        JOIN RolePermission rp ON r.id = rp.role_id 
        JOIN Permission p ON rp.permission_id = p.id 
        WHERE r.name = '供应商' AND (p.code LIKE '%appeal%' OR p.name LIKE '%申诉%')
    """)
    supplier_appeal_perms = cursor.fetchall()
    
    if supplier_appeal_perms:
        for p in supplier_appeal_perms:
            print(f'  ✓ {p[0]} - {p[1]}')
    else:
        print('  ✗ 供应商角色没有申诉相关权限')
    
    conn.close()

if __name__ == "__main__":
    check_supplier_permissions()