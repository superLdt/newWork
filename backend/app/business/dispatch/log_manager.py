# -*- coding: utf-8 -*-
"""
派车流程操作日志管理模块
"""

from flask import g
from datetime import datetime
from app.services.dispatch.dispatch_service import DispatchService
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DispatchLogManager:
    """
    派车流程操作日志管理类
    负责记录派车流程中的各种操作日志
    """
    
    # 操作类型定义
    ACTION_TYPES = {
        'create': '创建派车任务',
        'update': '更新派车任务',
        'approve': '审批派车任务',
        'reject': '拒绝派车任务',
        'assign': '分配车辆',
        'complete': '完成任务',
        'cancel': '取消任务',
        'merge': '合并车辆',
        'downgrade': '车辆降档'
    }
    
    @staticmethod
    def log_action(task_id: Optional[str], action_type: str, details: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        记录操作日志
        
        参数:
            task_id: 任务ID（字符串，可为None用于与任务无关的操作）
            action_type: 操作类型，必须是ACTION_TYPES中定义的类型
            details: 操作详情
            user_id: 操作用户ID，如果不提供则尝试从g.current_user获取
            
        返回:
            Optional[Dict[str, Any]]: 创建的日志记录，失败时返回None
        """
        # 验证操作类型
        if action_type not in DispatchLogManager.ACTION_TYPES:
            raise ValueError(f"不支持的操作类型: {action_type}")
        
        # 获取操作用户ID
        if user_id is None:
            user_id = g.current_user.id if hasattr(g, 'current_user') else None
        
        # 准备日志数据
        log_data = {
            'task_id': task_id,
            'action_type': action_type,
            'action_name': DispatchLogManager.ACTION_TYPES[action_type],
            'details': details,
            'user_id': user_id,
            'created_at': datetime.now()
        }
        
        try:
            # 调用服务层记录日志
            log_record = DispatchService.add_operation_log(log_data)
            logger.info(f"记录操作日志成功: {action_type}, 任务ID: {task_id}")
            return log_record
        except Exception as e:
            logger.error(f"记录操作日志失败: {str(e)}")
            # 操作日志记录失败不应影响主流程
            return None
    
    @staticmethod
    def get_task_logs(task_id: str) -> list:
        """
        获取任务的所有操作日志
        
        参数:
            task_id: 任务ID（字符串）
            
        返回:
            list: 操作日志列表
        """
        try:
            # 调用服务层获取任务日志
            logs = DispatchService.get_task_operation_logs(task_id)
            return logs
        except Exception as e:
            logger.error(f"获取任务操作日志失败: {str(e)}")
            return []