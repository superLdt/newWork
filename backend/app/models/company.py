#!/usr/bin/env python3
"""
公司模型模块
定义Company数据模型及相关功能
"""

from datetime import datetime
from ..extensions import db


class Company(db.Model):
    """
    公司模型类
    对应数据库设计文档中的Company表
    """
    __tablename__ = 'Company'
    
    id = db.Column(db.Integer, primary_key=True, comment='公司唯一ID')
    name = db.Column(db.String(100), nullable=False, unique=True, comment='公司名称')
    bank_name = db.Column(db.String(100), comment='银行名称')
    account_number = db.Column(db.String(50), comment='银行账号')
    address = db.Column(db.String(200), comment='公司地址')
    contact_person = db.Column(db.String(50), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """
        将公司对象转换为字典格式
        
        Returns:
            dict: 公司信息字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'bank_name': self.bank_name,
            'account_number': self.account_number,
            'address': self.address,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        公司对象的字符串表示
        
        Returns:
            str: 公司信息字符串
        """
        return f'<Company {self.name}>'