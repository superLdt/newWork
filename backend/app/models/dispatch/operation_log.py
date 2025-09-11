# -*- coding: utf-8 -*-
from datetime import datetime
from app.extensions import db


class OperationLog(db.Model):
    """
    操作日志模型类
    记录用户对派车任务的操作行为
    """
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True, comment='日志ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), comment='操作用户ID')
    user_role = db.Column(db.String(50), comment='操作用户角色')
    operation_type = db.Column(db.String(50), comment='操作类型')
    operation_content = db.Column(db.Text, comment='操作内容')
    ip_address = db.Column(db.String(50), comment='IP地址')
    operation_time = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='操作时间')
    
    # 关系定义
    task = db.relationship('ManualDispatchTask', backref='operation_logs', lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], primaryjoin="OperationLog.user_id == User.id", backref='operation_logs', lazy=True)
    
    def __repr__(self):
        return f'<OperationLog {self.id}: {self.operation_type}@{self.operation_time}'
    
    def to_dict(self):
        """
        将操作日志对象转换为字典格式
        Returns:
            dict: 包含操作日志信息的字典
        """
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_role': self.user_role,
            'operation_type': self.operation_type,
            'operation_content': self.operation_content,
            'ip_address': self.ip_address,
            'operation_time': self.operation_time
        }
    
    @classmethod
    def get_operation_type_choices(cls):
        """
        获取操作类型选项列表
        Returns:
            list: 操作类型选项列表
        """
        return [
            '创建任务', '编辑任务', '删除任务', '审核任务', 
            '派车', '确认车辆', '修改车辆信息', '合并车辆',
            '降档操作', '确认完成', '查看详情'
        ]