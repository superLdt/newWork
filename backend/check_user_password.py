#!/usr/bin/env python3
"""
查询用户密码信息
"""
import sqlite3

def check_user_password():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 查询meimei用户信息
    cursor.execute("SELECT username, password FROM user WHERE username = 'meimei'")
    user = cursor.fetchone()
    
    if user:
        print(f'用户: {user[0]}')
        print(f'密码哈希: {user[1][:50]}...')
    else:
        print('用户meimei不存在')
    
    # 查询所有用户的用户名
    cursor.execute("SELECT username FROM user")
    users = cursor.fetchall()
    print('\n所有用户:')
    for u in users:
        print(f'  {u[0]}')
    
    conn.close()

if __name__ == "__main__":
    check_user_password()