#!/usr/bin/env python3
"""
用户角色关联表模型
定义用户与角色的多对多关系
"""

from ..extensions import db

# 用户角色关联表
user_role = db.Table('UserRole',
    db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True, comment='用户ID'),
    db.Column('role_id', db.Integer, db.ForeignKey('Role.id'), primary_key=True, comment='角色ID'),
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp(), comment='创建时间')
)