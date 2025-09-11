#!/usr/bin/env python3
"""
派车流程状态管理模块

负责管理派车任务的状态变更和状态历史记录
"""

from app.models.task import ManualDispatchTask
from app.models.dispatch_status_history import DispatchStatusHistory
from app.services.dispatch.dispatch_service import DispatchService
from flask import g
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DispatchStatusManager:
    """
    派车流程状态管理类
    """
    
    # 状态转换映射，定义了状态之间的合法转换关系
    STATUS_TRANSITIONS = {
        'pending': ['approved', 'rejected'],  # 待审核 -> 已审核/已拒绝
        'approved': ['assigned', 'cancelled'],  # 已审核 -> 已分配/已取消
        'rejected': ['pending', 'cancelled'],  # 已拒绝 -> 待审核/已取消
        'assigned': ['in_progress', 'cancelled'],  # 已分配 -> 进行中/已取消
        'in_progress': ['completed', 'cancelled'],  # 进行中 -> 已完成/已取消
        'completed': [],  # 已完成（终态）
        'cancelled': []  # 已取消（终态）
    }
    
    # 新增：将中英文状态规范化到英文代码
    @staticmethod
    def _normalize_status(status: str) -> str:
        mapping = {
            '待审核': 'pending',
            '审核通过': 'approved',
            '审核拒绝': 'rejected',
            '已分配': 'assigned',
            '进行中': 'in_progress',
            '任务完成': 'completed',
            '已取消': 'cancelled',
            # 业务中提到的供应商相关状态做合理映射
            '待供应商响应': 'assigned',
            '供应商已响应': 'in_progress'
        }
        # 已经是英文代码或未识别的状态原样返回
        return mapping.get(status, status)

    @staticmethod
    def validate_status_transition(current_status: str, new_status: str) -> bool:
        """
        验证状态转换是否合法
        
        参数:
            current_status: 当前状态（可为中文或英文）
            new_status: 新状态（可为中文或英文）
            
        返回:
            bool: 状态转换是否合法
        """
        # 规范化状态到英文代码
        norm_current = DispatchStatusManager._normalize_status(current_status)
        norm_new = DispatchStatusManager._normalize_status(new_status)

        if norm_current not in DispatchStatusManager.STATUS_TRANSITIONS:
            logger.error(f"无效的当前状态: {current_status}")
            return False
            
        # 检查是否是允许的状态转换（使用规范化后的英文代码）
        allowed_transitions = DispatchStatusManager.STATUS_TRANSITIONS.get(norm_current, [])
        if norm_new not in allowed_transitions:
            logger.error(f"不允许从 {current_status} 转换到 {new_status}")
            return False
            
        return True

    @staticmethod
    def update_task_status(task_id: str, new_status: str, comment: str = None) -> dict:
        """
        更新任务状态并记录状态历史
        
        参数:
            task_id: 任务ID（字符串）
            new_status: 新状态
            comment: 状态变更备注
            
        返回:
            dict: 更新结果
        """
        # 获取任务信息
        task = DispatchService.get_dispatch_task_by_id(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            raise ValueError(f"任务不存在: {task_id}")
        
        # 验证状态转换
        current_status = task.get('status')
        if not DispatchStatusManager.validate_status_transition(current_status, new_status):
            raise ValueError(f"不允许从 {current_status} 转换到 {new_status}")
        
        # 准备状态历史数据
        status_history_data = {
            'task_id': task_id,
            'previous_status': current_status,
            'new_status': new_status,
            'changed_by': g.current_user.id if hasattr(g, 'current_user') else None,
            'changed_at': datetime.now(),
            'comment': comment
        }
        
        # 更新任务状态并记录历史
        result = DispatchService.update_task_status(task_id, new_status, status_history_data)
        
        return result
    
    @staticmethod
    def get_status_flow(task_id: str) -> list:
        """
        获取任务状态流转记录
        
        参数:
            task_id: 任务ID（字符串）
            
        返回:
            list: 状态流转记录列表
        """
        # 获取任务状态历史
        status_history = DispatchService.get_task_status_history(task_id)
        
        # 格式化状态流转记录
        status_flow = []
        for history in status_history:
            status_flow.append({
                'id': history.get('id'),
                'previous_status': history.get('previous_status'),
                'new_status': history.get('new_status'),
                'changed_by': history.get('changed_by'),
                'changed_at': history.get('changed_at'),
                'comment': history.get('comment')
            })
        
        return status_flow
    
    @staticmethod
    def get_next_possible_statuses(current_status: str) -> list:
        """
        获取当前状态可转换的下一个状态列表
        
        参数:
            current_status: 当前状态
            
        返回:
            list: 可转换的下一个状态列表
        """
        if current_status not in DispatchStatusManager.STATUS_TRANSITIONS:
            logger.error(f"无效的当前状态: {current_status}")
            return []
            
        return DispatchStatusManager.STATUS_TRANSITIONS.get(current_status, [])
    
    @staticmethod
    def get_status_display_name(status: str) -> str:
        """
        获取状态的显示名称
        
        参数:
            status: 状态代码
            
        返回:
            str: 状态显示名称
        """
        status_choices = ManualDispatchTask.get_status_choices()
        for choice in status_choices:
            if choice[0] == status:
                return choice[1]
        return status