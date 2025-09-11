#!/usr/bin/env python3
"""
派车流程业务逻辑模块

处理派车流程相关的业务规则和验证逻辑，位于应用层
"""

from flask import g
from datetime import datetime
from app.services.dispatch.dispatch_service import DispatchService
from app.business.dispatch.status_manager import DispatchStatusManager
from app.business.dispatch.log_manager import DispatchLogManager
from app.business.vehicle.vehicle_downgrade_business import VehicleDowngradeBusiness
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DispatchBusiness:
    """
    派车流程业务逻辑类
    负责处理派车流程相关的业务规则和验证逻辑
    """

    # == 新增：统一的校验结果包装 ==
    @staticmethod
    def _ok(msg: str = 'OK') -> Dict[str, Any]:
        return {'valid': True, 'message': msg}

    @staticmethod
    def _bad(msg: str) -> Dict[str, Any]:
        return {'valid': False, 'message': msg}

    # == 新增：创建/更新/审核/分配/完成 校验方法 ==
    @staticmethod
    def validate_task_creation(data: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['title', 'description', 'start_time', 'end_time', 'vehicle_type', 'passenger_count']
        for f in required_fields:
            if f not in data or data.get(f) in (None, ''):
                return DispatchBusiness._bad(f"缺少必填字段: {f}")
        return DispatchBusiness._ok()

    @staticmethod
    def validate_task_update(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        allowed_fields = {'title','description','start_time','end_time','vehicle_type','passenger_count','location','contact_person','contact_phone'}
        if not any(k in data for k in allowed_fields):
            return DispatchBusiness._bad("未提供可更新的字段")
        return DispatchBusiness._ok()

    @staticmethod
    def validate_task_approval(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'is_approved' not in data and 'approved' not in data:
            return DispatchBusiness._bad("缺少审核结果参数")
        return DispatchBusiness._ok()

    @staticmethod
    def validate_vehicle_assignment(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # 允许二选一：vehicle_id 或 license_plate
        if not data.get('vehicle_id') and not data.get('license_plate'):
            return DispatchBusiness._bad("缺少必填字段: vehicle_id 或 license_plate 至少提供一个")
        for f in ['driver_name','driver_phone']:
            if f not in data or not data.get(f):
                return DispatchBusiness._bad(f"缺少必填字段: {f}")
        return DispatchBusiness._ok()

    @staticmethod
    def validate_task_completion(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # 备注可选，但若提供需为字符串（兼容 completion_note 与 completion_notes）
        note = data.get('completion_note', data.get('completion_notes', None))
        if note is not None and not isinstance(note, str):
            return DispatchBusiness._bad("completion_note 必须为字符串")
        return DispatchBusiness._ok()

    # == 既有方法 ==
    def create_dispatch_task(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建派车任务
        
        参数:
            data: 派车任务数据
            
        返回:
            Dict[str, Any]: 创建的派车任务
        """
        # 验证必填字段
        required_fields = ['title', 'description', 'start_time', 'end_time', 'vehicle_type', 'passenger_count']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 设置初始状态为待审核
        data['status'] = 'pending'
        data['created_by'] = g.current_user.id if hasattr(g, 'current_user') else None
        data['created_at'] = datetime.now()
        
        # 调用服务层创建任务
        task = DispatchService.create_dispatch_task(data)
        
        # 记录操作日志
        log_details = {
            'task_data': {
                'title': data.get('title'),
                'description': data.get('description'),
                'start_time': str(data.get('start_time')),
                'end_time': str(data.get('end_time')),
                'vehicle_type': data.get('vehicle_type'),
                'passenger_count': data.get('passenger_count')
            }
        }
        # 修复错误的键名，使用 task_id
        DispatchLogManager.log_action(task['task_id'], 'create', log_details)
        
        return task

    @staticmethod
    def update_dispatch_task(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新派车任务
        
        参数:
            task_id: 任务ID
            data: 更新数据
            
        返回:
            Dict[str, Any]: 更新后的派车任务
        """
        # 获取当前任务
        task = DispatchService.get_dispatch_task_by_id(task_id)
        if not task:
            raise ValueError("派车任务不存在")
        
        # 验证任务状态，只有待审核状态的任务可以更新（兼容英文代码和中文状态）
        if task['status'] not in ['pending', '待审核']:
            raise ValueError(f"当前任务状态为 {task['status']}，不能更新")
        
        # 调用服务层更新任务
        updated_task = DispatchService.update_dispatch_task(task_id, data)
        
        # 记录操作日志
        log_details = {
            'updated_fields': data,
            'previous_data': {
                'title': task.get('title'),
                'description': task.get('description'),
                'start_time': str(task.get('start_time')),
                'end_time': str(task.get('end_time')),
                'vehicle_type': task.get('vehicle_type'),
                'passenger_count': task.get('passenger_count')
            }
        }
        DispatchLogManager.log_action(task_id, 'update', log_details)
        
        return updated_task

    @staticmethod
    def process_task_approval(task_id: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务审批
        
        参数:
            task_id: 任务ID
            approval_data: 审批数据
            
        返回:
            Dict[str, Any]: 处理结果
        """
        # 获取当前任务
        task = DispatchService.get_dispatch_task_by_id(task_id)
        if not task:
            raise ValueError("派车任务不存在")
        
        # 验证任务状态，只有待审核状态的任务可以审批（兼容英文代码和中文状态）
        if task['status'] not in ['pending', '待审核']:
            raise ValueError(f"当前任务状态为 {task['status']}，不能进行审批操作")
        
        # 获取审批结果和备注（兼容 is_approved / approved）
        is_approved = approval_data.get('is_approved', approval_data.get('approved', False))
        comment = approval_data.get('comment', '')
        
        # 确定新状态
        new_status = 'approved' if is_approved else 'rejected'
        
        # 使用状态管理器更新任务状态
        result = DispatchStatusManager.update_task_status(task_id, new_status, comment)
        
        # 记录操作日志
        log_details = {
            'approval_result': 'approved' if is_approved else 'rejected',
            'comment': comment
        }
        DispatchLogManager.log_action(task_id, 'approve' if is_approved else 'reject', log_details)
        
        return result

    @staticmethod
    def process_vehicle_assignment(task_id: str, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理车辆分配
        
        参数:
            task_id: 任务ID
            vehicle_data: 车辆数据
            
        返回:
            Dict[str, Any]: 处理结果
        """
        # 获取当前任务
        task = DispatchService.get_dispatch_task_by_id(task_id)
        if not task:
            raise ValueError("派车任务不存在")
        
        # 验证任务状态，只有已审批状态的任务可以分配车辆（兼容英文代码和中文状态）
        if task['status'] not in ['approved', '审核通过']:
            raise ValueError(f"当前任务状态为 {task['status']}，不能进行车辆分配操作")
        
        # 验证车辆数据（允许缺少 vehicle_id 时按车牌新建）
        if not vehicle_data.get('vehicle_id') and not vehicle_data.get('license_plate'):
            raise ValueError("缺少必填字段: vehicle_id 或 license_plate 至少提供一个")
        for field in ['driver_name', 'driver_phone']:
            if field not in vehicle_data or not vehicle_data.get(field):
                raise ValueError(f"缺少必填字段: {field}")
        
        # 调用服务层分配车辆
        vehicle_assignment = DispatchService.assign_vehicle_to_task(task_id, vehicle_data)
        
        # 使用状态管理器更新任务状态
        comment = f"分配车辆: {vehicle_data.get('vehicle_id') or vehicle_data.get('license_plate')}"
        result = DispatchStatusManager.update_task_status(task_id, 'assigned', comment)
        
        # 记录操作日志
        log_details = {
            'vehicle_id': vehicle_data.get('vehicle_id'),
            'driver_name': vehicle_data.get('driver_name'),
            'driver_phone': vehicle_data.get('driver_phone')
        }
        DispatchLogManager.log_action(task_id, 'assign', log_details)
        
        return result

    @staticmethod
    def process_task_completion(task_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务完成
        
        参数:
            task_id: 任务ID
            completion_data: 完成数据
            
        返回:
            Dict[str, Any]: 处理结果
        """
        # 获取当前任务
        task = DispatchService.get_dispatch_task_by_id(task_id)
        if not task:
            raise ValueError("派车任务不存在")
        
        # 验证任务状态，已分配或进行中的任务可以完成（兼容英文代码和中文状态）
        if task['status'] not in ['assigned', 'in_progress', '供应商已响应', '进行中']:
            raise ValueError(f"当前任务状态为 {task['status']}，不能进行任务完成操作")
        
        # 兼容 completion_note 与 completion_notes
        note = completion_data.get('completion_note', completion_data.get('completion_notes', '任务已完成'))
        
        # 更新任务信息
        update_data = {
            'completion_notes': note,
            'completion_time': datetime.now()
        }
        
        # 更新任务基本信息
        DispatchService.update_dispatch_task(task_id, update_data)
        
        # 使用状态管理器更新任务状态
        comment = note
        # 若当前状态为已分配（含别名），先自动流转到进行中，再标记完成
        current_status = task.get('status')
        norm_status = DispatchStatusManager._normalize_status(current_status)
        if norm_status == 'assigned':
            DispatchStatusManager.update_task_status(task_id, 'in_progress', '自动流转到进行中以完成任务')
        result = DispatchStatusManager.update_task_status(task_id, 'completed', comment)
        
        # 记录操作日志
        log_details = {
            'completion_note': note,
            'completion_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        DispatchLogManager.log_action(task_id, 'complete', log_details)
        
        return result

    @staticmethod
    def merge_vehicles(source_vehicle_id: int, target_vehicle_id: int) -> Dict[str, Any]:
        """
        合并车辆
        
        参数:
            source_vehicle_id: 源车辆ID（将被合并的车辆）
            target_vehicle_id: 目标车辆ID（合并后保留的车辆）
            
        返回:
            Dict[str, Any]: 合并结果
        """
        # 验证源车辆和目标车辆是否存在
        source_vehicle = DispatchService.get_vehicle_by_id(source_vehicle_id)
        if not source_vehicle:
            raise ValueError(f"源车辆不存在: ID {source_vehicle_id}")
            
        target_vehicle = DispatchService.get_vehicle_by_id(target_vehicle_id)
        if not target_vehicle:
            raise ValueError(f"目标车辆不存在: ID {target_vehicle_id}")
            
        # 验证源车辆和目标车辆不是同一辆车
        if source_vehicle_id == target_vehicle_id:
            raise ValueError("源车辆和目标车辆不能是同一辆车")
            
        # 验证源车辆和目标车辆类型是否兼容
        if source_vehicle['vehicle_type'] != target_vehicle['vehicle_type']:
            raise ValueError(f"车辆类型不兼容: 源车辆类型 {source_vehicle['vehicle_type']}, 目标车辆类型 {target_vehicle['vehicle_type']}")
            
        # 验证源车辆没有进行中的任务
        active_tasks = DispatchService.get_vehicle_active_tasks(source_vehicle_id)
        if active_tasks and len(active_tasks) > 0:
            raise ValueError(f"源车辆有{len(active_tasks)}个进行中的任务，无法合并")
            
        # 获取源车辆的历史任务
        source_tasks = DispatchService.get_vehicle_completed_tasks(source_vehicle_id)
        
        # 将源车辆的历史任务转移到目标车辆
        for task in source_tasks:
            DispatchService.update_task_vehicle(task['id'], target_vehicle_id)
            
        # 记录合并操作
        merge_record = {
            'source_vehicle_id': source_vehicle_id,
            'target_vehicle_id': target_vehicle_id,
            'source_vehicle_info': source_vehicle,
            'merged_at': datetime.now(),
            'merged_by': g.current_user.id if hasattr(g, 'current_user') else None,
            'tasks_transferred': len(source_tasks)
        }
        
        # 保存合并记录
        merge_result = DispatchService.create_vehicle_merge_record(merge_record)
        
        # 标记源车辆为已合并状态
        DispatchService.update_vehicle(source_vehicle_id, {'status': 'merged', 'merged_to': target_vehicle_id})
        
        # 记录操作日志
        log_details = {
            'source_vehicle_id': source_vehicle_id,
            'source_vehicle_info': {
                'plate_number': source_vehicle.get('plate_number'),
                'vehicle_type': source_vehicle.get('vehicle_type')
            },
            'target_vehicle_id': target_vehicle_id,
            'target_vehicle_info': {
                'plate_number': target_vehicle.get('plate_number'),
                'vehicle_type': target_vehicle.get('vehicle_type')
            },
            'tasks_transferred': len(source_tasks)
        }
        DispatchLogManager.log_action(None, 'merge', log_details)
        
        return {
            'success': True,
            'message': f"成功将车辆 {source_vehicle.get('plate_number')} 合并到 {target_vehicle.get('plate_number')}",
            'merge_record': merge_result,
            'tasks_transferred': len(source_tasks)
        }
    
    @staticmethod
    def downgrade_vehicle(vehicle_id: int, downgrade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        车辆降档
        
        参数:
            vehicle_id: 车辆ID
            downgrade_data: 降档数据
            
        返回:
            Dict[str, Any]: 降档结果
        """
        # 验证车辆是否存在
        vehicle = DispatchService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"车辆不存在: ID {vehicle_id}")
        
        # 验证降档原因
        if 'reason' not in downgrade_data or not downgrade_data['reason']:
            raise ValueError("降档原因为必填项")
        
        # 验证降档类型
        if 'downgrade_type' not in downgrade_data or not downgrade_data['downgrade_type']:
            raise ValueError("降档类型为必填项")
        
        # 准备降档记录数据
        downgrade_record = {
            'vehicle_id': vehicle_id,
            'previous_type': vehicle.get('vehicle_type'),
            'new_type': downgrade_data.get('downgrade_type'),
            'reason': downgrade_data.get('reason'),
            'downgraded_at': datetime.now(),
            'downgraded_by': g.current_user.id if hasattr(g, 'current_user') else None
        }
        
        # 调用车辆降档业务逻辑
        result = VehicleDowngradeBusiness.process_vehicle_downgrade(vehicle_id, downgrade_record)
        
        # 记录操作日志
        log_details = {
            'vehicle_id': vehicle_id,
            'vehicle_info': {
                'plate_number': vehicle.get('plate_number'),
                'previous_type': vehicle.get('vehicle_type'),
                'new_type': downgrade_data.get('downgrade_type')
            },
            'reason': downgrade_data.get('reason')
        }
        DispatchLogManager.log_action(None, 'downgrade', log_details)
        
        return result