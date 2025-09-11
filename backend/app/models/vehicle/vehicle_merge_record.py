# -*- coding: utf-8 -*-
from datetime import datetime
from app.extensions import db


class VehicleMergeRecord(db.Model):
    """
    车辆合并记录模型类
    记录车辆合并操作的历史记录
    """
    __tablename__ = 'vehicle_merge_records'
    
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    source_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), comment='源车辆ID')
    target_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), comment='目标车辆ID')
    merge_time = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='合并时间')
    operator_id = db.Column(db.Integer, db.ForeignKey('User.id'), comment='操作人ID')
    operator_role = db.Column(db.String(50), comment='操作人角色')
    original_volume = db.Column(db.Float, comment='原始容积')
    merged_volume = db.Column(db.Float, comment='合并后容积')
    merge_reason = db.Column(db.Text, comment='合并原因')
    
    # 关系定义
    source_vehicle = db.relationship('Vehicle', foreign_keys=[source_vehicle_id], backref='as_source_merges', lazy=True)
    target_vehicle = db.relationship('Vehicle', foreign_keys=[target_vehicle_id], backref='as_target_merges', lazy=True)
    operator = db.relationship('User', foreign_keys=[operator_id], primaryjoin="VehicleMergeRecord.operator_id == User.id", backref='vehicle_merges', lazy=True)
    
    def __repr__(self):
        return f'<VehicleMergeRecord {self.id}: {self.source_vehicle_id}->{self.target_vehicle_id}@{self.merge_time}>'
    
    def to_dict(self):
        """
        将车辆合并记录对象转换为字典格式
        Returns:
            dict: 包含车辆合并记录信息的字典
        """
        return {
            'id': self.id,
            'source_vehicle_id': self.source_vehicle_id,
            'target_vehicle_id': self.target_vehicle_id,
            'merge_time': self.merge_time,
            'operator_id': self.operator_id,
            'operator_role': self.operator_role,
            'original_volume': self.original_volume,
            'merged_volume': self.merged_volume,
            'merge_reason': self.merge_reason
        }