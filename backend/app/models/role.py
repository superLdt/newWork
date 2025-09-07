from datetime import datetime
from app.extensions import db
from app.models.user_role import user_role


class Role(db.Model):
    """
    角色模型类
    对应数据库设计文档中的Role表
    """
    __tablename__ = 'Role'
    
    id = db.Column(db.Integer, primary_key=True, comment='角色唯一ID')
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    description = db.Column(db.Text, comment='角色描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        """
        将角色对象转换为字典格式
        Returns:
            dict: 包含角色信息的字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_default_roles(cls):
        """
        获取系统默认角色列表
        Returns:
            list: 默认角色列表
        """
        return [
            {'name': '超级管理员', 'description': '系统最高权限，可管理所有功能'},
            {'name': '区域调度员', 'description': '负责任务审核、派车管理'},
            {'name': '车间地调', 'description': '负责提交车辆需求、查看已分配的任务'},
            {'name': '供应商', 'description': '负责响应任务、填写车辆信息'},
            {'name': '财务人员', 'description': '负责财务对账，结算单生成等任务'}
        ]


# 关联表定义已移至 user_role.py