#!/usr/bin/env python3
"""
数据库初始化脚本
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.models.company import Company

def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        print("创建所有数据库表...")
        try:
            db.create_all()
            print("✅ 数据库表创建完成")
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            return
        
        print("开始创建种子数据...")
        
        # 创建默认公司
        if not Company.query.first():
            company = Company(
                name='智能运力公司',
                address='北京市朝阳区',
                contact_person='管理员',
                contact_phone='010-12345678'
            )
            db.session.add(company)
            print("✅ 创建默认公司")
        
        # 创建默认角色
        default_roles = [
            {'name': '超级管理员', 'description': '系统最高权限，可管理所有功能'},
            {'name': '区域调度员', 'description': '负责任务审核、派车管理'},
            {'name': '车间地调', 'description': '负责提交车辆需求、查看已分配的任务'},
            {'name': '供应商', 'description': '负责响应任务、填写车辆信息'},
            {'name': '财务人员', 'description': '负责财务对账，结算单生成等任务'}
        ]
        
        for role_data in default_roles:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(
                    name=role_data['name'],
                    description=role_data['description']
                )
                db.session.add(role)
                print(f"✅ 创建角色: {role_data['name']}")
        
        # 提交角色和公司数据
        db.session.commit()
        
        # 创建默认管理员用户
        if not User.query.filter_by(username='admin').first():
            company = Company.query.first()
            admin_role = Role.query.filter_by(name='超级管理员').first()
            
            admin_user = User(
                username='admin',
                full_name='系统管理员',
                email='admin@example.com',
                phone='13800138000',
                company_id=company.id if company else None
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.flush()  # 获取用户ID
            
            # 分配管理员角色
            if admin_role:
                admin_user.roles.append(admin_role)
            
            db.session.commit()
            print("✅ 创建管理员用户: admin/admin123")
        
        # 创建测试用户
        test_users = [
            {'username': 'dispatcher', 'full_name': '调度员', 'role': '区域调度员'},
            {'username': 'operator', 'full_name': '地调员', 'role': '车间地调'},
            {'username': 'supplier', 'full_name': '供应商', 'role': '供应商'}
        ]
        
        company = Company.query.first()
        
        for user_data in test_users:
            if not User.query.filter_by(username=user_data['username']).first():
                role = Role.query.filter_by(name=user_data['role']).first()
                
                user = User(
                    username=user_data['username'],
                    full_name=user_data['full_name'],
                    email=f"{user_data['username']}@example.com",
                    phone='13800138001',
                    company_id=company.id if company else None
                )
                user.set_password('123456')
                
                db.session.add(user)
                db.session.flush()
                
                if role:
                    user.roles.append(role)
                
                print(f"✅ 创建测试用户: {user_data['username']}/123456")
        
        db.session.commit()
        print("✅ 数据库初始化完成!")
        
        # 显示统计信息
        print(f"\n📊 数据统计:")
        print(f"公司数量: {Company.query.count()}")
        print(f"角色数量: {Role.query.count()}")
        print(f"用户数量: {User.query.count()}")

if __name__ == '__main__':
    init_database()