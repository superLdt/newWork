from datetime import datetime
from app.extensions import db


class Vehicle(db.Model):
    """
    车辆信息模型类
    对应数据库设计文档中的vehicles表
    """
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True, comment='车辆唯一ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
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
    supplier_id = db.Column(db.Integer, db.ForeignKey('Company.id'), comment='供应商ID')
    supplier_type = db.Column(db.String(50), comment='供应商类型')
    driver_name = db.Column(db.String(50), comment='司机姓名')
    driver_phone = db.Column(db.String(20), comment='司机电话')
    driver_id_card = db.Column(db.String(20), comment='司机身份证号')
    status = db.Column(db.String(20), default='待确认', comment='车辆状态')
    confirmed_by = db.Column(db.Integer, comment='确认人ID')
    confirmed_at = db.Column(db.String(20), comment='确认时间')
    is_merged = db.Column(db.Boolean, default=False, comment='是否已合并')
    is_downgraded = db.Column(db.Boolean, default=False, comment='是否已降档')
    original_capacity = db.Column(db.Float, comment='原始容积')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    
    def __repr__(self):
        return f'<Vehicle {self.license_plate}: {self.manifest_number}>'
    
    def to_dict(self):
        """
        将车辆对象转换为字典格式
        Returns:
            dict: 包含车辆信息的字典
        """
        return {
            'id': self.id,
            'task_id': self.task_id,
            'manifest_number': self.manifest_number,
            'dispatch_number': self.dispatch_number,
            'license_plate': self.license_plate,
            'carriage_number': self.carriage_number,
            'created_at': self.created_at,
            'notes': self.notes,
            'actual_volume': self.actual_volume,
            'volume_photo_url': self.volume_photo_url,
            'volume_modified_by': self.volume_modified_by,
            'required_volume': self.required_volume,
            'confirmed_volume': self.confirmed_volume,
            'vehicle_type': self.vehicle_type,
            'supplier_id': self.supplier_id,
            'supplier_type': self.supplier_type,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'driver_id_card': getattr(self, 'driver_id_card', None),
            'status': self.status,
            'confirmed_by': self.confirmed_by,
            'confirmed_at': self.confirmed_at,
            'is_merged': self.is_merged,
            'is_downgraded': self.is_downgraded,
            'original_capacity': self.original_capacity,
            'updated_at': self.updated_at
        }