from app.extensions import db


class DispatchStatusHistory(db.Model):
    """
    派车状态历史模型类
    对应数据库设计文档中的dispatch_status_history表
    """
    __tablename__ = 'dispatch_status_history'
    
    id = db.Column(db.Integer, primary_key=True, comment='历史记录ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    status_change = db.Column(db.String(50), comment='状态变更')
    operator = db.Column(db.String(100), comment='操作人')
    timestamp = db.Column(db.String(20), comment='时间戳')
    note = db.Column(db.Text, comment='备注')
    
    def __repr__(self):
        return f'<DispatchStatusHistory {self.task_id}: {self.status_change}>'
    
    def to_dict(self):
        """
        将状态历史对象转换为字典格式
        Returns:
            dict: 包含状态历史信息的字典
        """
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status_change': self.status_change,
            'operator': self.operator,
            'timestamp': self.timestamp,
            'note': self.note
        }