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
    status_type = db.Column(db.Integer, default=0, comment='任务状态类型：0正常/1降档/2合并')
    special_requirements = db.Column(db.Text, comment='特殊要求')
    status = db.Column(db.String(20), default='待审核', comment='任务状态')
    dispatch_track = db.Column(db.String(10), comment='派车轨道')
    initiator_role = db.Column(db.String(50), comment='发起人角色')
    initiator_user_id = db.Column(db.Integer, comment='发起人用户ID')
    initiator_department = db.Column(db.String(100), comment='发起人部门')
    audit_required = db.Column(db.Boolean, default=True, comment='是否需要审核')
    current_handler_role = db.Column(db.String(50), comment='当前处理人角色')
    current_handler_user_id = db.Column(db.Integer, comment='当前处理人用户ID')
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    business_type = db.Column(db.String(20), default='委办派车', comment='业务类型：自办派车/委办派车')
    
    # 申诉审核相关字段
    appeal_reviewed_by = db.Column(db.Integer, comment='申诉审核人用户ID')
    appeal_reviewed_at = db.Column(db.String(20), comment='申诉审核时间')
    appeal_review_result = db.Column(db.String(20), comment='申诉审核结果：approved/rejected')
    appeal_review_notes = db.Column(db.Text, comment='申诉审核备注')
    final_confirmed_tonnage = db.Column(db.String(20), comment='最终确认吨位')
    completed_at = db.Column(db.String(20), comment='任务完成时间')
    
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
        # 获取创建人姓名
        creator_name = None
        if self.initiator_user_id:
            try:
                from app.models.user import User
                user = User.query.get(self.initiator_user_id)
                if user:
                    creator_name = user.full_name or user.username or f"ID:{self.initiator_user_id}"
                else:
                    creator_name = f"ID:{self.initiator_user_id}"
            except Exception:
                creator_name = f"ID:{self.initiator_user_id}"
        
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
            'status_type': self.status_type,
            'special_requirements': self.special_requirements,
            'status': self.status,
            'dispatch_track': self.dispatch_track,
            'initiator_role': self.initiator_role,
            'initiator_user_id': self.initiator_user_id,
            'initiator_department': self.initiator_department,
            'creator_name': creator_name,  # 添加创建人姓名字段
            'audit_required': self.audit_required,
            'current_handler_role': self.current_handler_role,
            'current_handler_user_id': self.current_handler_user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'business_type': self.business_type,
            'appeal_reviewed_by': self.appeal_reviewed_by,
            'appeal_reviewed_at': self.appeal_reviewed_at,
            'appeal_review_result': self.appeal_review_result,
            'appeal_review_notes': self.appeal_review_notes,
            'final_confirmed_tonnage': self.final_confirmed_tonnage,
            'completed_at': self.completed_at,
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
            ('pending', '待审核'),
            ('approved', '审核通过'),
            ('in_progress', '已响应'),
            ('pending_verification', '待核查'),
            ('verified', '已核查'),
            ('pending_confirmation', '待确认'),
            ('confirmed', '已确认'),
            ('appeal_pending', '申诉待审核'),
            ('completed', '任务完成'),
            ('rejected', '审核拒绝'),
            ('cancelled', '已取消')
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
        return ['自办派车', '委办派车', '大容积派车']