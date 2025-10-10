#!/usr/bin/env python3
"""
派车单位模型模块
定义DispatchUnit数据模型及相关功能
"""

from datetime import datetime
from ..extensions import db


class DispatchUnit(db.Model):
    """
    派车单位模型类
    对应数据库设计文档中的派车单位表
    """
    __tablename__ = 'dispatch_units'
    
    id = db.Column(db.Integer, primary_key=True, comment='派车单位唯一ID')
    name = db.Column(db.String(100), nullable=False, unique=True, comment='派车单位名称')
    unit_type = db.Column(db.String(50), comment='单位类型（供应商/内部单位）')
    bank_name = db.Column(db.String(100), comment='银行名称')
    account_number = db.Column(db.String(50), comment='银行账号')
    address = db.Column(db.String(200), comment='单位地址')
    contact_person = db.Column(db.String(50), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    email = db.Column(db.String(120), comment='邮箱')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """
        将派车单位对象转换为字典格式
        
        Returns:
            dict: 派车单位信息字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'unit_type': self.unit_type,
            'bank_name': self.bank_name,
            'account_number': self.account_number,
            'address': self.address,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        派车单位对象的字符串表示
        
        Returns:
            str: 派车单位信息字符串
        """
        return f'<DispatchUnit {self.name}>'