from app.extensions import db
from datetime import datetime


class VehicleVolumeHistory(db.Model):
    """
    车辆容积更新历史记录模型类
    对应数据库设计文档中的vehicle_volume_history表
    """
    __tablename__ = 'vehicle_volume_history'
    
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), comment='车辆ID')
    original_volume = db.Column(db.Float, comment='原始容积')
    new_volume = db.Column(db.Float, comment='新容积')
    reason = db.Column(db.Text, comment='修改原因')
    modified_by = db.Column(db.Integer, db.ForeignKey('User.id'), comment='修改人ID')
    modified_at = db.Column(db.DateTime, default=datetime.now, comment='修改时间')
    volume_photo_url = db.Column(db.String(200), comment='容积照片URL')
    approval_doc_url = db.Column(db.String(200), comment='审批凭证URL')
    
    # 关联关系
    vehicle = db.relationship('Vehicle', backref=db.backref('volume_history', lazy='dynamic'))
    user = db.relationship('User', 
                          foreign_keys=[modified_by], 
                          primaryjoin="VehicleVolumeHistory.modified_by == User.id",
                          backref=db.backref('volume_modifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<VehicleVolumeHistory {self.id}: {self.vehicle_id} {self.original_volume}->{self.new_volume}'
    
    def to_dict(self):
        """
        将车辆容积更新历史记录对象转换为字典格式
        Returns:
            dict: 包含车辆容积更新历史记录信息的字典
        """
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'original_volume': self.original_volume,
            'new_volume': self.new_volume,
            'reason': self.reason,
            'modified_by': self.modified_by,
            'modified_at': self.modified_at.strftime('%Y-%m-%d %H:%M:%S') if self.modified_at else None,
            'volume_photo_url': self.volume_photo_url,
            'approval_doc_url': self.approval_doc_url,
            'modifier_name': self.user.username if self.user else None,
            'vehicle_license_plate': self.vehicle.license_plate if self.vehicle else None
        }