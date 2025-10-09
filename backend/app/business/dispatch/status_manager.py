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
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DispatchStatusManager:
    """
    派车流程状态管理类
    """
    
    # 状态转换映射，定义了状态之间的合法转换关系
    STATUS_TRANSITIONS = {
        'pending': ['approved', 'rejected'],           # 待审核 -> 审核通过/审核拒绝
        'approved': ['in_progress', 'pending_verification', 'cancelled'],      # 审核通过 -> 已响应/待核查/已取消
        'in_progress': ['pending_verification', 'cancelled'],  # 已响应 -> 待核查/已取消
        'pending_verification': ['verified', 'cancelled'],  # 待核查 -> 已核查/已取消
        'verified': ['pending_confirmation', 'cancelled'],  # 已核查 -> 待确认/已取消
        'pending_confirmation': ['confirmed', 'appeal_pending', 'cancelled'],    # 待确认 -> 已确认/申诉待审核/已取消
        'confirmed': ['completed', 'cancelled'],       # 已确认 -> 任务完成/已取消
        'appeal_pending': ['completed', 'cancelled'],  # 申诉待审核 -> 任务完成/已取消
        'rejected': ['pending', 'cancelled'],          # 审核拒绝 -> 待审核/已取消
        'completed': [],                               # 任务完成（终态）
        'cancelled': []                                # 已取消（终态）
    }
    
    # 新增：将中英文状态规范化到英文代码
    @staticmethod
    def _normalize_status(status: str) -> str:
        mapping = {
            '待审核': 'pending',
            '审核通过': 'approved',
            '审核拒绝': 'rejected',
            '待核查': 'pending_verification',
            '待车间核查': 'pending_verification',
            '已核查': 'verified',
            '待确认': 'pending_confirmation',
            '已确认': 'confirmed',
            '申诉待审核': 'appeal_pending',
            '任务完成': 'completed',
            '已取消': 'cancelled',
            # 修正：通用"待响应"应视为审核通过阶段
            '待响应': 'approved',
            # 统一：通用"已响应"视为进入进行中阶段
            '已响应': 'in_progress'
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
    def update_task_status(task_id: str, new_status: str, comment: Optional[str] = None) -> dict:
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
        current_status = task.get('status', '')
        if not DispatchStatusManager.validate_status_transition(current_status, new_status):
            raise ValueError(f"不允许从 {current_status} 转换到 {new_status}")
        
        # 识别操作者角色
        operator_role = None
        try:
            if hasattr(g, 'current_user') and g.current_user and g.current_user.roles:
                operator_role = g.current_user.roles[0].name
        except Exception:
            operator_role = None
        
        # 计算下一阶段处理人角色
        next_handler_role = DispatchStatusManager.get_next_handler_role(
            previous_status=current_status,
            new_status=new_status,
            operator_role=operator_role or '系统',
            business_type=task.get('business_type') or ''
        )
        
        # 准备状态历史数据
        status_history_data = {
            'task_id': task_id,
            'previous_status': current_status,
            'new_status': new_status,
            'changed_by': g.current_user.id if hasattr(g, 'current_user') else None,
            'changed_at': datetime.now(),
            'comment': comment,
            'next_handler_role': next_handler_role
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
            list: 状态流转记录列表（直接与 dispatch_status_history 表结构对齐）
        """
        # 获取任务状态历史（模型 to_dict 已包含 status_change/operator/timestamp/note/next_handler_role 等字段）
        status_history = DispatchService.get_task_status_history(task_id)
        
        # 直接返回，确保前端展示与数据库记录一致
        return status_history
    
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

    @staticmethod
    def get_next_handler_role(previous_status: str, new_status: str, operator_role: str, business_type: Optional[str] = None) -> str:
        """
        统一确定"状态 → 下一阶段操作人角色"的规则，避免业务层硬编码
        
        参数：
            previous_status: 变更前状态（可中文/英文）
            new_status: 变更新状态（可中文/英文）
            operator_role: 执行本次操作的角色（如：供应商/大容积供应商/班组长/区域调度员）
            business_type: 业务类型（自办派车/委办派车/大容积派车），可选
        返回：
            下一阶段操作人角色
        """
        # 规范化状态到英文代码
        norm_previous = DispatchStatusManager._normalize_status(previous_status)
        norm_new = DispatchStatusManager._normalize_status(new_status)

        # 根据新状态确定下一处理人角色
        # 审核阶段（待审核 -> 审核通过/审核拒绝）：由超级管理员/区域调度员完成
        if norm_new == 'pending':
            return '区域调度员'
            
        # 响应阶段（审核通过 -> 已响应）：由供应商/班组长/大容积供应商完成
        if norm_new == 'approved':
            # 使用基类方法根据业务类型确定下一处理人角色
            from app.business.dispatch.base_business import BaseDispatchBusiness
            return BaseDispatchBusiness._get_next_handler_role_by_business_type(business_type or '')
            
        # 核查阶段（已响应 -> 待核查）：由车间地调完成
        if norm_new == 'in_progress':
            return '车间地调'

        # 进入待核查/待车间核查阶段后，下一处理人仍为车间地调
        if norm_new == 'pending_verification':
            return '车间地调'
            
        # 确认阶段（已核查 -> 待确认）：由供应商/班组长/大容积供应商完成
        if norm_new == 'verified':
            # 使用基类方法根据业务类型确定下一处理人角色
            from app.business.dispatch.base_business import BaseDispatchBusiness
            return BaseDispatchBusiness._get_next_handler_role_by_business_type(business_type or '')
            
        # 确认阶段（待确认 -> 已确认）：由供应商/班组长/大容积供应商完成
        if norm_new == 'pending_confirmation':
            # 使用基类方法根据业务类型确定下一处理人角色
            from app.business.dispatch.base_business import BaseDispatchBusiness
            return BaseDispatchBusiness._get_next_handler_role_by_business_type(business_type or '')
            
        # 完成阶段（已确认 -> 任务完成）：由区域调度员完成
        if norm_new == 'confirmed':
            return '区域调度员'
            
        # 默认回退规则（非上述场景）
        return '区域调度员'
