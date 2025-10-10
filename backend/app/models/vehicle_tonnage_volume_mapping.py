from datetime import datetime
from app.extensions import db
from app.utils.tonnage_formatter import TonnageFormatter


class VehicleTonnageVolumeMapping(db.Model):
    """
    车辆吨位-容积对应表
    用于明确车辆档位，建立吨位与容积的标准映射关系
    """
    __tablename__ = 'vehicle_tonnage_volume_mapping'
    
    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tonnage = db.Column(db.String(20), unique=True, nullable=False, comment='标准吨位，如：5吨、8吨、12吨、20吨、30吨、40吨A、40吨B')
    min_volume = db.Column(db.Float, nullable=False, comment='最小容积要求(m³)')
    standard_volume = db.Column(db.Float, nullable=False, comment='标准容积(m³)')
    max_volume = db.Column(db.Float, comment='最大容积限制(m³)，可为空表示无上限')
    conversion_factor = db.Column(db.Float, nullable=False, comment='容积折算系数')
    vehicle_grade = db.Column(db.String(10), nullable=False, comment='车辆档位等级')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    
    def __init__(self, **kwargs):
        """
        初始化车辆吨位-容积映射对象
        自动格式化吨位字段
        """
        if 'tonnage' in kwargs:
            kwargs['tonnage'] = TonnageFormatter.format_tonnage(kwargs['tonnage'])
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f'<VehicleTonnageVolumeMapping {self.tonnage}: {self.min_volume}-{self.max_volume or "∞"}m³>'
    
    def to_dict(self):
        """
        将对象转换为字典格式
        Returns:
            dict: 包含映射信息的字典
        """
        return {
            'id': self.id,
            'tonnage': self.tonnage,
            'min_volume': self.min_volume,
            'standard_volume': self.standard_volume,
            'max_volume': self.max_volume,
            'conversion_factor': self.conversion_factor,
            'vehicle_grade': self.vehicle_grade,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def get_tonnage_volume_mapping(cls):
        """
        获取所有启用的吨位-容积映射关系
        Returns:
            dict: 吨位为键，容积信息为值的字典
        """
        mappings = cls.query.filter_by(is_active=True).all()
        return {mapping.tonnage: {
            'min_volume': mapping.min_volume,
            'standard_volume': mapping.standard_volume,
            'max_volume': mapping.max_volume,
            'conversion_factor': mapping.conversion_factor,
            'vehicle_grade': mapping.vehicle_grade
        } for mapping in mappings}
    
    @classmethod
    def get_volume_by_tonnage(cls, tonnage: str):
        """
        根据吨位获取对应的容积信息
        Args:
            tonnage: 标准吨位
        Returns:
            dict: 容积信息，如果未找到返回None
        """
        # 格式化输入的吨位
        formatted_tonnage = TonnageFormatter.format_tonnage(tonnage)
        mapping = cls.query.filter_by(tonnage=formatted_tonnage, is_active=True).first()
        if mapping:
            return {
                'min_volume': mapping.min_volume,
                'standard_volume': mapping.standard_volume,
                'max_volume': mapping.max_volume,
                'conversion_factor': mapping.conversion_factor,
                'vehicle_grade': mapping.vehicle_grade
            }
        return None
    
    @classmethod
    def get_tonnage_by_volume(cls, volume: float):
        """
        根据容积获取对应的吨位档位
        Args:
            volume: 容积值
        Returns:
            str: 对应的吨位，如果未找到返回None
        """
        mappings = cls.query.filter_by(is_active=True).order_by(cls.min_volume.desc()).all()
        for mapping in mappings:
            if volume >= mapping.min_volume:
                if mapping.max_volume is None or volume <= mapping.max_volume:
                    return mapping.tonnage
        return None
    
    @classmethod
    def initialize_default_data(cls):
        """
        初始化默认的吨位-容积映射数据
        """
        default_mappings = [
            {
                'tonnage': '5吨',
                'min_volume': 35.0,
                'standard_volume': 35.0,
                'max_volume': 44.0,
                'conversion_factor': 0.45,
                'vehicle_grade': 'A'
            },
            {
                'tonnage': '8吨',
                'min_volume': 45.0,
                'standard_volume': 45.0,
                'max_volume': 54.0,
                'conversion_factor': 0.51,
                'vehicle_grade': 'B'
            },
            {
                'tonnage': '12吨',
                'min_volume': 55.0,
                'standard_volume': 55.0,
                'max_volume': 99.0,
                'conversion_factor': 0.63,
                'vehicle_grade': 'C'
            },
            {
                'tonnage': '20吨',
                'min_volume': 100.0,
                'standard_volume': 100.0,
                'max_volume': 129.0,
                'conversion_factor': 0.83,
                'vehicle_grade': 'D'
            },
            {
                'tonnage': '30吨',
                'min_volume': 130.0,
                'standard_volume': 130.0,
                'max_volume': 149.0,
                'conversion_factor': 1.00,
                'vehicle_grade': 'E'
            },
            {
                'tonnage': '40吨A',
                'min_volume': 150.0,
                'standard_volume': 150.0,
                'max_volume': 179.0,
                'conversion_factor': 1.12,
                'vehicle_grade': 'F'
            },
            {
                'tonnage': '40吨B',
                'min_volume': 180.0,
                'standard_volume': 180.0,
                'max_volume': None,  # 无上限
                'conversion_factor': 1.23,
                'vehicle_grade': 'G'
            }
        ]
        
        for mapping_data in default_mappings:
            existing = cls.query.filter_by(tonnage=mapping_data['tonnage']).first()
            if not existing:
                mapping = cls(**mapping_data)
                db.session.add(mapping)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e