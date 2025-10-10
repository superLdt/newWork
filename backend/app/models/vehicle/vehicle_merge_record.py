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
    source_task_id = db.Column(db.String(50), comment='源任务ID')
    source_dispatch_number = db.Column(db.String(100), comment='源派车单号')
    target_dispatch_number = db.Column(db.String(100), comment='目标派车单号')
    source_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), comment='源车辆ID')
    operation_time = db.Column(db.DateTime, default=datetime.now, comment='操作时间')
    operator_id = db.Column(db.Integer, db.ForeignKey('User.id'), comment='操作人ID')
    operator_name = db.Column(db.String(100), comment='操作人姓名')
    operator_role = db.Column(db.String(50), comment='操作人角色')
    original_volume = db.Column(db.Float, comment='原始容积')
    merged_volume = db.Column(db.Float, comment='合并后容积')
    merge_reason = db.Column(db.Text, comment='合并原因')
    merge_status = db.Column(db.String(20), default='completed', comment='合并状态：completed/cancelled')
    
    # 新增车辆信息字段
    new_vehicle_license_plate = db.Column(db.String(20), comment='新增车辆车牌号')
    new_vehicle_tonnage = db.Column(db.Float, comment='新增车辆吨位')
    new_vehicle_volume = db.Column(db.Float, comment='新增车辆容积')
    new_vehicle_type = db.Column(db.String(20), comment='新增车辆类型')
    new_vehicle_carriage_number = db.Column(db.String(50), comment='新增车辆车厢号')
    
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    source_vehicle = db.relationship('Vehicle', foreign_keys=[source_vehicle_id], backref='as_source_merges', lazy=True)
    operator = db.relationship('User', foreign_keys=[operator_id], primaryjoin="VehicleMergeRecord.operator_id == User.id", backref='vehicle_merges', lazy=True)
    
    def __repr__(self):
        return f'<VehicleMergeRecord {self.id}: {self.source_task_id}->{self.target_dispatch_number}@{self.operation_time}>'
    
    def to_dict(self):
        """
        将车辆合并记录对象转换为字典格式
        Returns:
            dict: 包含车辆合并记录信息的字典
        """
        return {
            'id': self.id,
            'source_task_id': self.source_task_id,
            'source_dispatch_number': self.source_dispatch_number,
            'target_dispatch_number': self.target_dispatch_number,
            'source_vehicle_id': self.source_vehicle_id,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'operator_role': self.operator_role,
            'original_volume': self.original_volume,
            'merged_volume': self.merged_volume,
            'merge_reason': self.merge_reason,
            'merge_status': self.merge_status,
            # 新增车辆信息
            'new_vehicle_license_plate': self.new_vehicle_license_plate,
            'new_vehicle_tonnage': self.new_vehicle_tonnage,
            'new_vehicle_volume': self.new_vehicle_volume,
            'new_vehicle_type': self.new_vehicle_type,
            'new_vehicle_carriage_number': self.new_vehicle_carriage_number,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }