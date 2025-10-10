from datetime import datetime
import json
from app.extensions import db


class VehicleCapacityReference(db.Model):
    """
    车辆容积参考模型类
    对应数据库设计文档中的vehicle_capacity_reference表
    用于车辆日常管理，不关联具体派车任务
    """
    __tablename__ = 'vehicle_capacity_reference'
    
    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    vehicle_type = db.Column(db.String(20), comment='车辆类型')
    standard_volume = db.Column(db.Float, comment='标准容积')
    license_plate = db.Column(db.String(20), comment='车牌号')
    carriage_number = db.Column(db.String(50), comment='车厢号')
    vehicle_category = db.Column(db.String(10), comment='车辆分类：单车/挂车')
    frequent_companies = db.Column(db.Text, default='[]', comment='常用公司列表，JSON格式')
    status = db.Column(db.String(20), default='active', comment='状态：active/inactive')
    original_capacity = db.Column(db.Float, comment='原始载重量(吨)')
    suppliers = db.Column(db.Text, comment='供应商信息')
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    
    def __repr__(self):
        return f'<VehicleCapacityReference {self.vehicle_type}: {self.standard_volume}>'
    
    def to_dict(self):
        """
        将车辆容积参考对象转换为字典格式
        Returns:
            dict: 包含车辆容积参考信息的字典
        """
        # 解析常用公司列表
        frequent_companies_list = []
        if self.frequent_companies:
            try:
                frequent_companies_list = json.loads(self.frequent_companies)
            except (json.JSONDecodeError, TypeError):
                frequent_companies_list = []
        
        return {
            'id': self.id,
            'vehicle_type': self.vehicle_type,
            'standard_volume': self.standard_volume,
            'license_plate': self.license_plate,
            'carriage_number': self.carriage_number,
            'vehicle_category': self.vehicle_category,
            'frequent_companies': frequent_companies_list,
            'status': self.status,
            'original_capacity': self.original_capacity,
            'suppliers': self.suppliers,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def get_vehicle_type_choices(cls):
        """
        获取车辆类型选项列表
        Returns:
            list: 车辆类型选项列表
        """
        return [
            '5吨', '8吨', '12吨', '20吨', 
            '30吨', '40吨A', '40吨B'
        ]