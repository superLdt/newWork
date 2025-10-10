#!/usr/bin/env python3
"""
重置meimei用户密码为123456
"""
import sqlite3
from werkzeug.security import generate_password_hash

def reset_meimei_password():
    """重置meimei用户密码"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 生成新密码的哈希
    new_password_hash = generate_password_hash('admin123')
    
    # 更新meimei用户的密码
    cursor.execute("UPDATE user SET password = ? WHERE username = 'meimei'", (new_password_hash,))
    
    if cursor.rowcount > 0:
        print(f'✓ 成功重置用户meimei的密码为: admin123')
        conn.commit()
    else:
        print('✗ 用户meimei不存在')
    
    # 验证更新结果
    cursor.execute("SELECT username, password FROM user WHERE username = 'meimei'")
    user = cursor.fetchone()
    if user:
        print(f'用户: {user[0]}')
        print(f'新密码哈希: {user[1][:50]}...')
    
    conn.close()

if __name__ == '__main__':
    reset_meimei_password()