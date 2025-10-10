# -*- coding: utf-8 -*-
"""
通用上传服务

提供统一的文件上传、验证、保存功能
支持不同业务场景的文件上传需求
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app
from app.extensions import db
from app.models.common.file_record import FileRecord
import logging

logger = logging.getLogger(__name__)


class UploadConfig:
    """上传配置类"""
    
    # 文件类型配置
    FILE_TYPES = {
        'image': {
            'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'allowed_mimetypes': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'],
            'max_size': 5 * 1024 * 1024,  # 5MB
            'subfolder': 'images'
        },
        'document': {
            'allowed_extensions': ['.pdf', '.doc', '.docx', '.txt'],
            'allowed_mimetypes': [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ],
            'max_size': 10 * 1024 * 1024,  # 10MB
            'subfolder': 'documents'
        },
        'excel': {
            'allowed_extensions': ['.xls', '.xlsx'],
            'allowed_mimetypes': [
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ],
            'max_size': 10 * 1024 * 1024,  # 10MB
            'subfolder': 'excel'
        },
        'attachment': {
            'allowed_extensions': ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'],
            'allowed_mimetypes': [
                'image/jpeg', 'image/png',
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ],
            'max_size': 10 * 1024 * 1024,  # 10MB
            'subfolder': 'attachments'
        }
    }


class UploadService:
    """通用上传服务类"""
    
    @staticmethod
    def _ensure_dir(path: str) -> bool:
        """确保目录存在"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f'创建目录失败: {path}, 错误: {e}')
            return False
    
    @staticmethod
    def _get_upload_root() -> str:
        """获取上传根目录"""
        upload_root = current_app.config.get('UPLOAD_FOLDER')
        if not upload_root:
            upload_root = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'uploads')
        return os.path.abspath(upload_root)
    
    @staticmethod
    def validate_file(file: FileStorage, file_type: str) -> Tuple[bool, str]:
        """
        验证上传文件
        
        Args:
            file: 上传的文件对象
            file_type: 文件类型 (image/document/excel/attachment)
            
        Returns:
            Tuple[bool, str]: (是否通过验证, 错误信息)
        """
        if not file or not file.filename:
            return False, '缺少文件参数'
        
        if file_type not in UploadConfig.FILE_TYPES:
            return False, f'不支持的文件类型: {file_type}'
        
        config = UploadConfig.FILE_TYPES[file_type]
        
        # 验证文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in config['allowed_extensions']:
            return False, f'不支持的文件格式，仅支持: {", ".join(config["allowed_extensions"])}'
        
        # 验证MIME类型
        if file.mimetype and file.mimetype not in config['allowed_mimetypes']:
            return False, f'不支持的文件类型: {file.mimetype}'
        
        # 验证文件大小
        try:
            file.stream.seek(0, os.SEEK_END)
            size = file.stream.tell()
            file.stream.seek(0)
            if size > config['max_size']:
                max_size_mb = config['max_size'] / (1024 * 1024)
                return False, f'文件大小不能超过{max_size_mb}MB'
        except Exception as e:
            logger.warning(f'获取文件大小失败: {e}')
        
        return True, ''
    
    @staticmethod
    def save_file(file: FileStorage, file_type: str, business_type: str = None, 
                  business_id: str = None, user_id: int = None) -> Tuple[bool, Dict[str, Any]]:
        """
        保存上传文件
        
        Args:
            file: 上传的文件对象
            file_type: 文件类型 (image/document/excel/attachment)
            business_type: 业务类型 (可选)
            business_id: 业务ID (可选)
            user_id: 上传用户ID (可选)
            
        Returns:
            Tuple[bool, Dict]: (是否成功, 结果数据)
        """
        try:
            # 验证文件
            is_valid, error_msg = UploadService.validate_file(file, file_type)
            if not is_valid:
                return False, {'error': error_msg}
            
            config = UploadConfig.FILE_TYPES[file_type]
            
            # 获取上传目录
            upload_root = UploadService._get_upload_root()
            target_dir = os.path.join(upload_root, config['subfolder'])
            
            if not UploadService._ensure_dir(target_dir):
                return False, {'error': '创建上传目录失败'}
            
            # 生成唯一文件名
            original_filename = secure_filename(file.filename)
            name, ext = os.path.splitext(original_filename)
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{name}_{timestamp}_{unique_id[:8]}{ext}"
            
            # 保存文件
            file_path = os.path.join(target_dir, unique_filename)
            file.save(file_path)
            
            # 生成访问URL
            relative_path = f"{config['subfolder']}/{unique_filename}"
            file_url = f"/api/v1/upload/files/{relative_path}"
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            
            # 保存文件记录到数据库
            file_record = None
            if user_id:
                try:
                    file_record = FileRecord(
                        original_filename=original_filename,
                        stored_filename=unique_filename,
                        file_path=relative_path,
                        file_url=file_url,
                        file_type=file_type,
                        file_size=file_size,
                        mime_type=file.mimetype,
                        business_type=business_type,
                        business_id=business_id,
                        uploaded_by=user_id
                    )
                    db.session.add(file_record)
                    db.session.commit()
                except Exception as e:
                    logger.warning(f'保存文件记录失败: {e}')
                    # 不影响文件上传成功
            
            result = {
                'id': file_record.id if file_record else None,
                'url': file_url,
                'path': relative_path,
                'filename': original_filename,
                'size': file_size,
                'type': file.mimetype
            }
            
            return True, result
            
        except Exception as e:
            logger.error(f'保存文件失败: {e}')
            return False, {'error': f'保存文件失败: {str(e)}'}
    
    @staticmethod
    def delete_file(file_id: int = None, file_path: str = None) -> bool:
        """
        删除文件
        
        Args:
            file_id: 文件记录ID
            file_path: 文件路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            file_record = None
            
            # 通过ID查找文件记录
            if file_id:
                file_record = FileRecord.query.get(file_id)
                if not file_record:
                    logger.warning(f'文件记录不存在: {file_id}')
                    return False
                file_path = file_record.file_path
            
            if not file_path:
                logger.warning('缺少文件路径参数')
                return False
            
            # 删除物理文件
            upload_root = UploadService._get_upload_root()
            full_path = os.path.join(upload_root, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
            
            # 删除数据库记录
            if file_record:
                db.session.delete(file_record)
                db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f'删除文件失败: {e}')
            return False
    
    @staticmethod
    def get_file_info(file_id: int) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_id: 文件记录ID
            
        Returns:
            Optional[Dict]: 文件信息
        """
        try:
            file_record = FileRecord.query.get(file_id)
            if not file_record:
                return None
            
            return file_record.to_dict()
            
        except Exception as e:
            logger.error(f'获取文件信息失败: {e}')
            return None
    
    @staticmethod
    def get_business_files(business_type: str, business_id: str) -> List[Dict[str, Any]]:
        """
        获取业务相关的文件列表
        
        Args:
            business_type: 业务类型
            business_id: 业务ID
            
        Returns:
            List[Dict]: 文件列表
        """
        try:
            files = FileRecord.query.filter_by(
                business_type=business_type,
                business_id=business_id
            ).order_by(FileRecord.created_at.desc()).all()
            
            return [file.to_dict() for file in files]
            
        except Exception as e:
            logger.error(f'获取业务文件列表失败: {e}')
            return []