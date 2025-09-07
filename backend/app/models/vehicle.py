from app.extensions import db


class Vehicle(db.Model):
    """
    车辆信息模型类
    对应数据库设计文档中的vehicles表
    """
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True, comment='车辆唯一ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    manifest_number = db.Column(db.String(50), comment='货票号')
    dispatch_number = db.Column(db.String(50), comment='派车单号')
    license_plate = db.Column(db.String(20), comment='车牌号')
    carriage_number = db.Column(db.String(50), comment='车厢号')
    created_at = db.Column(db.String(20), comment='创建时间')
    notes = db.Column(db.Text, comment='备注')
    actual_volume = db.Column(db.Float, comment='实际容积')
    volume_photo_url = db.Column(db.String(200), comment='容积照片URL')
    volume_modified_by = db.Column(db.Integer, comment='容积修改人')
    required_volume = db.Column(db.Float, comment='需求容积')
    confirmed_volume = db.Column(db.Float, comment='确认容积')
    
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
            'confirmed_volume': self.confirmed_volume
        }