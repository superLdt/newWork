from datetime import datetime
from app.extensions import db


class ManualDispatchTask(db.Model):
    """
    手动派车任务模型类
    对应数据库设计文档中的manual_dispatch_tasks表
    """
    __tablename__ = 'manual_dispatch_tasks'
    
    task_id = db.Column(db.String(50), primary_key=True, comment='任务唯一ID')
    required_date = db.Column(db.String(20), comment='需求日期')
    origin_bureau = db.Column(db.String(100), comment='始发局')
    mail_route_name = db.Column(db.String(100), comment='邮路名称')
    organizing_unit = db.Column(db.String(100), comment='组开单位（承运商）')
    organizing_unit_id = db.Column(db.Integer, db.ForeignKey('dispatch_units.id'), comment='组开单位ID，关联派车单位表')
    transport_type = db.Column(db.String(50), comment='运输类型')
    requirement_type = db.Column(db.String(50), comment='需求类型')
    required_weight = db.Column(db.String(20), comment='需求吨位')
    required_volume = db.Column(db.Integer, comment='需求容积')
    actual_weight = db.Column(db.String(20), comment='实际吨位')
    actual_volume = db.Column(db.Integer, comment='实际容积')
    special_requirements = db.Column(db.Text, comment='特殊要求')
    status = db.Column(db.String(20), default='待审核', comment='任务状态')
    dispatch_track = db.Column(db.String(10), comment='派车轨道')
    initiator_role = db.Column(db.String(50), comment='发起人角色')
    initiator_user_id = db.Column(db.Integer, comment='发起人用户ID')
    initiator_department = db.Column(db.String(100), comment='发起人部门')
    audit_required = db.Column(db.Boolean, default=True, comment='是否需要审核')
    auditor_role = db.Column(db.String(50), comment='审核人角色')
    auditor_user_id = db.Column(db.Integer, comment='审核人用户ID')
    audit_status = db.Column(db.String(20), comment='审核状态')
    audit_time = db.Column(db.String(20), comment='审核时间')
    audit_note = db.Column(db.Text, comment='审核备注')
    current_handler_role = db.Column(db.String(50), comment='当前处理人角色')
    current_handler_user_id = db.Column(db.Integer, comment='当前处理人用户ID')
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    assigned_supplier_id = db.Column(db.Integer, comment='分配供应商ID')
    business_type = db.Column(db.String(20), default='委办派车', comment='业务类型：自办派车/委办派车')
    
    # 关系定义
    vehicles = db.relationship('Vehicle', backref='task', lazy=True, cascade='all, delete-orphan')
    status_history = db.relationship('DispatchStatusHistory', backref='task', lazy=True, cascade='all, delete-orphan')
    organizing_unit_obj = db.relationship('DispatchUnit', backref=db.backref('tasks', lazy=True))
    
    def __repr__(self):
        return f'<ManualDispatchTask {self.task_id}: {self.mail_route_name}>'
    
    def to_dict(self):
        """
        将任务对象转换为字典格式
        Returns:
            dict: 包含任务信息的字典
        """
        return {
            'task_id': self.task_id,
            'required_date': self.required_date,
            'origin_bureau': self.origin_bureau,
            'mail_route_name': self.mail_route_name,
            'organizing_unit': self.organizing_unit,
            'organizing_unit_id': self.organizing_unit_id,
            'organizing_unit_obj': self.organizing_unit_obj.to_dict() if self.organizing_unit_obj else None,
            'transport_type': self.transport_type,
            'requirement_type': self.requirement_type,
            'required_weight': self.required_weight,
            'required_volume': self.required_volume,
            'actual_weight': self.actual_weight,
            'actual_volume': self.actual_volume,
            'special_requirements': self.special_requirements,
            'status': self.status,
            'dispatch_track': self.dispatch_track,
            'initiator_role': self.initiator_role,
            'initiator_user_id': self.initiator_user_id,
            'initiator_department': self.initiator_department,
            'audit_required': self.audit_required,
            'auditor_role': self.auditor_role,
            'auditor_user_id': self.auditor_user_id,
            'audit_status': self.audit_status,
            'audit_time': self.audit_time,
            'audit_note': self.audit_note,
            'current_handler_role': self.current_handler_role,
            'current_handler_user_id': self.current_handler_user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'assigned_supplier_id': self.assigned_supplier_id,
            'business_type': self.business_type,
            'vehicles': [vehicle.to_dict() for vehicle in self.vehicles] if self.vehicles else [],
            'status_history': [history.to_dict() for history in self.status_history] if self.status_history else []
        }
    
    @classmethod
    def get_status_choices(cls):
        """
        获取任务状态选项列表
        Returns:
            list: 状态选项列表
        """
        return [
            '待审核', '审核通过', '待响应', 
            '已响应', '任务完成', '审核拒绝'
        ]
    
    @classmethod
    def get_dispatch_track_choices(cls):
        """
        获取派车轨道选项列表
        Returns:
            list: 轨道选项列表
        """
        return ['轨道A', '轨道B']
    
    @classmethod
    def get_weight_volume_mapping(cls):
        """
        获取吨位与标准容积的映射关系
        Returns:
            dict: 吨位-标准容积映射字典
        """
        return {
            '5吨': 35,
            '8吨': 45,
            '12吨': 55,
            '20吨': 100,
            '30吨': 130,
            '40吨A': 150,
            '40吨B': 180
        }
    
    @classmethod
    def get_standard_weight_options(cls):
        """
        获取标准吨位选项列表
        Returns:
            list: 标准吨位选项列表
        """
        return ['5吨', '8吨', '12吨', '20吨', '30吨', '40吨A', '40吨B']
    
    @classmethod
    def get_transport_type_options(cls):
        """
        获取运输类型选项列表
        Returns:
            list: 运输类型选项列表
        """
        return ['单程', '往返']
    
    @classmethod
    def get_requirement_type_options(cls):
        """
        获取需求类型选项列表
        Returns:
            list: 需求类型选项列表
        """
        return ['正班', '加班']
    
    @classmethod
    def get_business_type_options(cls):
        """
        获取业务类型选项列表
        Returns:
            list: 业务类型选项列表
        """
        return ['自办派车', '委办派车']