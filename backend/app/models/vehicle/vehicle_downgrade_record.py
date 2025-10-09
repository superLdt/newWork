# -*- coding: utf-8 -*-
from datetime import datetime
from app.extensions import db


class VehicleDowngradeRecord(db.Model):
    """
    车辆降档记录模型类
    记录车辆降档操作的历史记录
    """
    __tablename__ = 'vehicle_downgrade_records'
    
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    task_id = db.Column(db.String(50), comment='任务ID')
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), comment='车辆ID')
    dispatch_number = db.Column(db.String(100), comment='派车单号')
    operation_type = db.Column(db.String(20), comment='操作类型：downgrade/merge')
    operation_time = db.Column(db.DateTime, default=datetime.now, comment='操作时间')
    operator_id = db.Column(db.Integer, db.ForeignKey('User.id'), comment='操作人ID')
    operator_name = db.Column(db.String(100), comment='操作人姓名')
    operator_role = db.Column(db.String(50), comment='操作人角色')
    
    # 降档相关字段
    original_tonnage = db.Column(db.Float, comment='原始吨位')
    downgraded_tonnage = db.Column(db.Float, comment='降档后吨位')
    
    # 通用字段
    operation_reason = db.Column(db.Text, comment='操作原因/备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    vehicle = db.relationship('Vehicle', backref='downgrade_records', lazy=True)
    operator = db.relationship('User', foreign_keys=[operator_id], primaryjoin="VehicleDowngradeRecord.operator_id == User.id", backref='vehicle_downgrades', lazy=True)
    
    def __repr__(self):
        return f'<VehicleDowngradeRecord {self.id}: {self.operation_type}@{self.operation_time}>'
    
    def to_dict(self):
        """
        将车辆降档记录对象转换为字典格式
        Returns:
            dict: 包含车辆降档记录信息的字典
        """
        return {
            'id': self.id,
            'task_id': self.task_id,
            'vehicle_id': self.vehicle_id,
            'dispatch_number': self.dispatch_number,
            'operation_type': self.operation_type,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'operator_role': self.operator_role,
            'original_tonnage': self.original_tonnage,
            'downgraded_tonnage': self.downgraded_tonnage,
            'operation_reason': self.operation_reason,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }