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
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), comment='车辆ID')
    downgrade_time = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='降档时间')
    operator_id = db.Column(db.Integer, db.ForeignKey('User.id'), comment='操作人ID')
    operator_role = db.Column(db.String(50), comment='操作人角色')
    original_type = db.Column(db.String(50), comment='原始车型')
    downgraded_type = db.Column(db.String(50), comment='降档后车型')
    original_volume = db.Column(db.Float, comment='原始容积')
    downgraded_volume = db.Column(db.Float, comment='降档后容积')
    downgrade_reason = db.Column(db.Text, comment='降档原因')
    
    # 关系定义
    vehicle = db.relationship('Vehicle', backref='downgrade_records', lazy=True)
    operator = db.relationship('User', foreign_keys=[operator_id], primaryjoin="VehicleDowngradeRecord.operator_id == User.id", backref='vehicle_downgrades', lazy=True)
    
    def __repr__(self):
        return f'<VehicleDowngradeRecord {self.id}: {self.vehicle_id}@{self.downgrade_time}>'
    
    def to_dict(self):
        """
        将车辆降档记录对象转换为字典格式
        Returns:
            dict: 包含车辆降档记录信息的字典
        """
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'downgrade_time': self.downgrade_time,
            'operator_id': self.operator_id,
            'operator_role': self.operator_role,
            'original_type': self.original_type,
            'downgraded_type': self.downgraded_type,
            'original_volume': self.original_volume,
            'downgraded_volume': self.downgraded_volume,
            'downgrade_reason': self.downgrade_reason
        }