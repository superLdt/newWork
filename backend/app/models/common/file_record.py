# -*- coding: utf-8 -*-
"""
文件记录模型

统一管理系统中所有上传的文件记录
"""

from datetime import datetime
from app.extensions import db


class FileRecord(db.Model):
    """
    文件记录模型类
    统一管理系统中所有上传的文件
    """
    __tablename__ = 'file_records'
    
    id = db.Column(db.Integer, primary_key=True, comment='文件记录ID')
    original_filename = db.Column(db.String(255), nullable=False, comment='原始文件名')
    stored_filename = db.Column(db.String(255), nullable=False, comment='存储文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='文件相对路径')
    file_url = db.Column(db.String(500), nullable=False, comment='文件访问URL')
    file_type = db.Column(db.String(50), nullable=False, comment='文件类型分类')
    file_size = db.Column(db.Integer, comment='文件大小（字节）')
    mime_type = db.Column(db.String(100), comment='MIME类型')
    
    # 业务关联字段
    business_type = db.Column(db.String(50), comment='业务类型')
    business_id = db.Column(db.String(100), comment='业务ID')
    
    # 上传信息
    uploaded_by = db.Column(db.Integer, db.ForeignKey('User.id'), comment='上传人ID')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')
    
    # 状态字段
    is_deleted = db.Column(db.Boolean, default=False, comment='是否已删除')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_files', lazy=True)
    
    # 索引
    __table_args__ = (
        db.Index('idx_file_records_business', 'business_type', 'business_id'),
        db.Index('idx_file_records_type', 'file_type'),
        db.Index('idx_file_records_uploader', 'uploaded_by'),
        db.Index('idx_file_records_upload_time', 'upload_time'),
    )
    
    def __repr__(self):
        return f'<FileRecord {self.id}: {self.original_filename}>'
    
    def to_dict(self):
        """
        将文件记录对象转换为字典格式
        Returns:
            dict: 包含文件记录信息的字典
        """
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'business_type': self.business_type,
            'business_id': self.business_id,
            'uploaded_by': self.uploaded_by,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S') if self.upload_time else None,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @classmethod
    def get_by_business(cls, business_type: str, business_id: str):
        """
        根据业务类型和ID获取文件列表
        
        Args:
            business_type: 业务类型
            business_id: 业务ID
            
        Returns:
            List[FileRecord]: 文件记录列表
        """
        return cls.query.filter_by(
            business_type=business_type,
            business_id=business_id,
            is_deleted=False
        ).order_by(cls.upload_time.desc()).all()
    
    @classmethod
    def get_by_type(cls, file_type: str):
        """
        根据文件类型获取文件列表
        
        Args:
            file_type: 文件类型
            
        Returns:
            List[FileRecord]: 文件记录列表
        """
        return cls.query.filter_by(
            file_type=file_type,
            is_deleted=False
        ).order_by(cls.upload_time.desc()).all()
    
    def soft_delete(self):
        """软删除文件记录"""
        self.is_deleted = True
        self.updated_at = datetime.now()
        db.session.commit()