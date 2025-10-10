#!/usr/bin/env python3
"""
查询用户角色关联信息
"""
import sqlite3

def check_user_roles():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 查询所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("所有表:")
    for table in tables:
        print(f"  {table[0]}")
    
    # 查询角色相关表
    role_tables = [t[0] for t in tables if 'role' in t[0].lower()]
    print(f"\n角色相关表: {role_tables}")
    
    # 查询Role表
    try:
        cursor.execute("SELECT * FROM Role LIMIT 5")
        roles = cursor.fetchall()
        print("\nRole表数据:")
        for role in roles:
            print(f"  {role}")
    except Exception as e:
        print(f"查询Role表失败: {e}")
    
    # 查询UserRole表
    try:
        cursor.execute("SELECT * FROM UserRole LIMIT 5")
        user_roles = cursor.fetchall()
        print("\nUserRole表数据:")
        for ur in user_roles:
            print(f"  {ur}")
    except Exception as e:
        print(f"查询UserRole表失败: {e}")
    
    # 查询用户及其角色
    try:
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, r.name as role_name
            FROM user u
            LEFT JOIN UserRole ur ON u.id = ur.user_id
            LEFT JOIN Role r ON ur.role_id = r.id
            LIMIT 10
        """)
        user_roles = cursor.fetchall()
        print("\n用户及其角色:")
        for ur in user_roles:
            print(f"  用户ID: {ur[0]}, 用户名: {ur[1]}, 姓名: {ur[2]}, 角色: {ur[3]}")
    except Exception as e:
        print(f"查询用户角色关联失败: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_user_roles()