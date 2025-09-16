from datetime import datetime
import json
import re
from app.extensions import db
from sqlalchemy.orm import validates


class Vehicle(db.Model):
    """
    车辆信息模型类
    对应数据库设计文档中的vehicles表
    用于派车响应，必须关联具体的派车任务
    """
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True, comment='车辆唯一ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), nullable=False, comment='关联任务ID')
    manifest_number = db.Column(db.String(50), comment='路单流水号')
    dispatch_number = db.Column(db.String(50), comment='派车单号')
    license_plate = db.Column(db.String(20), comment='车牌号')
    carriage_number = db.Column(db.String(50), comment='车厢号')
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    notes = db.Column(db.Text, comment='备注')
    actual_volume = db.Column(db.Float, comment='实际容积')
    volume_photo_url = db.Column(db.String(200), comment='容积照片URL')
    volume_modified_by = db.Column(db.Integer, comment='容积修改人')
    required_volume = db.Column(db.Float, comment='需求容积')
    confirmed_volume = db.Column(db.Float, comment='确认容积')
    vehicle_type = db.Column(db.String(20), comment='车辆类型')
    supplier_id = db.Column(db.Integer, db.ForeignKey('dispatch_units.id'), comment='供应商ID')
    supplier_type = db.Column(db.String(50), comment='供应商类型')
    status = db.Column(db.String(20), default='待确认', comment='车辆状态')
    confirmed_by = db.Column(db.Integer, comment='确认人ID')
    confirmed_at = db.Column(db.String(20), comment='确认时间')
    is_merged = db.Column(db.Boolean, default=False, comment='是否已合并')
    is_downgraded = db.Column(db.Boolean, default=False, comment='是否已降档')
    original_capacity = db.Column(db.Float, comment='原始容积')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    
    # 新增字段
    vehicle_category = db.Column(db.String(10), comment='车辆分类：单车/挂车')
    frequent_companies = db.Column(db.Text, default='[]', comment='常用公司列表，JSON格式')
    
    def __repr__(self):
        return f'<Vehicle {self.license_plate}: {self.manifest_number}>'