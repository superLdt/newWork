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
    def _error(msg: str) -> Dict[str, Any]:
        return {'valid': False, 'message': msg}
    
    # == 供应商响应相关验证和处理 ==
    @staticmethod
    def validate_supplier_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证供应商响应数据
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 验证结果
        """
        if not data:
            return DispatchBusiness._error('请求数据不能为空')
        
        # 验证必填字段
        required_fields = ['task_id', 'manifest_number', 'dispatch_number', 'vehicles']
        for field in required_fields:
            if not data.get(field):
                return DispatchBusiness._error(f'{field} 不能为空')
        
        # 验证车辆信息
        vehicles = data.get('vehicles', [])
        carriages = data.get('carriages', [])
        
        # 计算总的车辆和车厢数量
        total_vehicles = len(vehicles) if vehicles else 0
        total_carriages = len(carriages) if carriages else 0
        total_count = total_vehicles + total_carriages
        
        # 唯一性验证：一个任务只能派遣一辆车或一个车厢
        if total_count == 0:
            return DispatchBusiness._error('至少需要提供一辆车辆或一个车厢信息')
        elif total_count > 1:
            return DispatchBusiness._error('一个任务只能派遣一辆车或一个车厢，不能同时派遣多个')
        
        # 验证车辆信息
        if vehicles:
            for i, vehicle in enumerate(vehicles):
                # 车牌号必填
                if not vehicle.get('license_plate'):
                    return DispatchBusiness._error(f'第{i+1}辆车的车牌号不能为空')
                
                # 车辆类型必填
                if not vehicle.get('vehicle_type'):
                    return DispatchBusiness._error(f'第{i+1}辆车的车辆类型不能为空')
        
        # 验证车厢信息
        if carriages:
            for i, carriage in enumerate(carriages):
                # 车厢号必填
                if not carriage.get('carriage_number'):
                    return DispatchBusiness._error(f'第{i+1}个车厢的车厢号不能为空')
                
                # 车辆类型必填
                if not carriage.get('vehicle_type'):
                    return DispatchBusiness._error(f'第{i+1}个车厢的车辆类型不能为空')
        
        return {'valid': True, 'message': '数据验证通过'}
    
    @staticmethod
    def validate_team_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证班组响应数据
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 验证结果
        """
        # 班组响应与供应商响应验证规则相同
        return DispatchBusiness.validate_supplier_response_data(data)
    
    @staticmethod
    def validate_large_capacity_supplier_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证大容积供应商响应数据
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 验证结果
        """
        # 大容积供应商响应与供应商响应验证规则相同
        return DispatchBusiness.validate_supplier_response_data(data)
    
    @staticmethod
    def validate_outsourcing_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证外包管理公司响应数据（已废弃，请使用validate_large_capacity_supplier_response）
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 验证结果
        """
        # 为了向后兼容，保留此方法，但调用新方法
        return DispatchBusiness.validate_large_capacity_supplier_response_data(data)
    
    @staticmethod
    def process_supplier_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理供应商响应
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 处理结果
        """
        from app.models.task import ManualDispatchTask
        from app.models.vehicle.vehicle import Vehicle
        from app.models.dispatch_status_history import DispatchStatusHistory
        from app.extensions import db
        from datetime import datetime
        from flask_jwt_extended import get_current_user
        
        try:
            task_id = data['task_id']
            
            # 获取当前用户
            current_user = get_current_user()
            if not current_user:
                raise ValueError('无法获取当前用户信息')
            
            # 查找任务
            task = ManualDispatchTask.query.filter_by(task_id=task_id).first()
            if not task:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态（兼容中英文状态，统一业务层使用中文）
            allowed_statuses = {'待响应', '待供应商响应', '审核通过', 'awaiting_supplier_response', 'approved', 'awaiting_response'}
            if task.status not in allowed_statuses:
                raise ValueError(f'任务状态不允许提交供应商响应，当前状态：{task.status}')
            
            # 创建车辆记录
            for vehicle_data in data['vehicles']:
                vehicle = Vehicle(
                    task_id=task_id,
                    manifest_number=data['manifest_number'],
                    dispatch_number=data['dispatch_number'],
                    license_plate=vehicle_data['license_plate'],
                    carriage_number=vehicle_data.get('carriage_number', ''),
                    driver_name=vehicle_data['driver_name'],
                    driver_phone=vehicle_data['driver_phone'],
                    vehicle_type=vehicle_data['vehicle_type'],
                    load_capacity=vehicle_data['load_capacity'],
                    volume_capacity=vehicle_data.get('volume_capacity', 0),
                    actual_weight=vehicle_data.get('actual_weight', 0),
                    actual_volume=vehicle_data.get('actual_volume', 0),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(vehicle)
            
            # 使用状态管理器计算下一个处理角色和状态
            new_status = '已响应'  # 供应商响应后的状态
            next_handler_role = DispatchStatusManager.get_next_handler_role(
                previous_status=task.status,
                new_status=new_status,
                operator_role='供应商',
                business_type=task.business_type if hasattr(task, 'business_type') else None
            )
            
            # 更新任务状态和处理角色
            task.status = new_status
            task.current_handler_role = next_handler_role
            task.updated_at = datetime.now()
            
            # 记录状态历史 - 修复：使用模型字段 status_change/timestamp/note
            status_history = DispatchStatusHistory(
                task_id=task_id,
                status_change=new_status,
                operator=str(current_user.id),  # 记录用户ID
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                note=f"供应商提交响应，清单号:{data.get('manifest_number','')}, 派车单:{data.get('dispatch_number','')}",
                next_handler_role=next_handler_role
            )
            db.session.add(status_history)
            
            # 提交事务
            db.session.commit()
            
            return {
                'task_id': task_id,
                'status': new_status,
                'current_handler_role': next_handler_role,
                'message': '供应商响应提交成功'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def process_team_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理班组响应
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 处理结果
        """
        from app.models.task import ManualDispatchTask
        from app.models.vehicle.vehicle import Vehicle
        from app.models.dispatch_status_history import DispatchStatusHistory
        from app.extensions import db
        from datetime import datetime
        
        try:
            task_id = data['task_id']
            
            # 查找任务
            task = ManualDispatchTask.query.filter_by(task_id=task_id).first()
            if not task:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态（兼容中英文状态，统一业务层使用中文）
            allowed_statuses = {'待响应', '待班组派车', '审核通过', 'awaiting_team_assignment', 'approved', 'awaiting_response'}
            if task.status not in allowed_statuses:
                raise ValueError(f'任务状态不允许提交班组响应，当前状态：{task.status}')
            
            # 创建车辆记录
            for vehicle_data in data['vehicles']:
                vehicle = Vehicle(
                    task_id=task_id,
                    manifest_number=data['manifest_number'],
                    dispatch_number=data['dispatch_number'],
                    license_plate=vehicle_data['license_plate'],
                    carriage_number=vehicle_data.get('carriage_number', ''),
                    vehicle_type=vehicle_data.get('vehicle_type', ''),
                    vehicle_category=vehicle_data.get('vehicle_category', ''),
                    # 使用VehicleCapacityReference的字段
                    actual_volume=vehicle_data.get('standard_volume', 0),  # 使用标准容积作为实际容积
                    original_capacity=vehicle_data.get('original_capacity', 0),
                    notes=data.get('notes', ''),
                    supplier_type='班组'
                )
                
                db.session.add(vehicle)
            
            # 计算下一处理角色并更新任务状态（先保存旧状态）
            old_status = task.status
            new_status = '已响应'
            next_role = DispatchStatusManager.get_next_handler_role(
                previous_status=old_status,
                new_status=new_status,
                operator_role='班组长',
                business_type=task.business_type if hasattr(task, 'business_type') else None
            )
            task.status = new_status
            
            # 记录状态历史
            status_history = DispatchStatusHistory(
                task_id=task_id,
                status_change=new_status,
                operator='班组长',
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                note=data.get('notes', ''),
                next_handler_role=next_role
            )
            db.session.add(status_history)
            
            # 提交事务
            db.session.commit()
            
            return {
                'task_id': task_id,
                'status': '已响应',
                'message': '班组派车响应提交成功'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def process_large_capacity_supplier_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理大容积供应商响应
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 处理结果
        """
        from app.models.task import ManualDispatchTask
        from app.models.vehicle.vehicle import Vehicle
        from app.models.dispatch_status_history import DispatchStatusHistory
        from app.extensions import db
        from datetime import datetime
        
        try:
            task_id = data['task_id']
            
            # 查找任务
            task = ManualDispatchTask.query.filter_by(task_id=task_id).first()
            if not task:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态（兼容中英文状态，统一业务层使用中文）
            allowed_statuses = {'待响应', '待班组派车', '审核通过', 'awaiting_team_assignment', 'approved', 'awaiting_response'}
            if task.status not in allowed_statuses:
                raise ValueError(f'任务状态不允许提交大容积供应商响应，当前状态：{task.status}')
            
            # 创建车辆记录
            for vehicle_data in data['vehicles']:
                vehicle = Vehicle(
                    task_id=task_id,
                    manifest_number=data['manifest_number'],
                    dispatch_number=data['dispatch_number'],
                    license_plate=vehicle_data['license_plate'],
                    carriage_number=vehicle_data.get('carriage_number', ''),
                    vehicle_type=vehicle_data.get('vehicle_type', ''),
                    vehicle_category=vehicle_data.get('vehicle_category', ''),
                    # 使用VehicleCapacityReference的字段
                    actual_volume=vehicle_data.get('standard_volume', 0),  # 使用标准容积作为实际容积
                    original_capacity=vehicle_data.get('original_capacity', 0),
                    notes=data.get('notes', ''),
                    supplier_type='大容积供应商'
                )
                
                db.session.add(vehicle)
            
            # 计算下一处理角色并更新任务状态（先保存旧状态）
            old_status = task.status
            new_status = '已响应'
            next_role = DispatchStatusManager.get_next_handler_role(
                previous_status=old_status,
                new_status=new_status,
                operator_role='大容积供应商',
                business_type=task.business_type if hasattr(task, 'business_type') else None
            )
            task.status = new_status
            
            # 记录状态历史
            status_history = DispatchStatusHistory(
                task_id=task_id,
                status_change=new_status,
                operator='大容积供应商',
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                note=data.get('notes', ''),
                next_handler_role=next_role
            )
            db.session.add(status_history)
            
            # 提交事务
            db.session.commit()
            
            return {
                'task_id': task_id,
                'status': '已响应',
                'message': '大容积供应商响应提交成功'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def process_outsourcing_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理外包管理公司响应（已废弃，请使用process_large_capacity_supplier_response）
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 处理结果
        """
        # 为了向后兼容，保留此方法，但调用新方法
        return DispatchBusiness.process_large_capacity_supplier_response(data)

    @staticmethod
    def _bad(msg: str) -> Dict[str, Any]:
        return {'valid': False, 'message': msg}

    # == 新增：创建/更新/审核/分配/完成 校验方法 ==
    @staticmethod
    def validate_task_creation(data: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['required_date', 'origin_bureau', 'mail_route_name', 'transport_type', 'requirement_type', 'required_weight', 'required_volume']
        for f in required_fields:
            if f not in data or data.get(f) in (None, ''):
                return DispatchBusiness._bad(f"缺少必填字段: {f}")
        return DispatchBusiness._ok()

    @staticmethod
    def validate_task_update(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        allowed_fields = {'required_date', 'origin_bureau', 'mail_route_name', 'organizing_unit', 'transport_type', 'requirement_type', 'required_weight', 'required_volume', 'actual_weight', 'actual_volume', 'special_requirements', 'initiator_department', 'audit_required'}
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
        
        # 唯一性验证：检查任务是否已经分配了车辆
        existing_vehicles = DispatchService.get_vehicles_by_task_id(task_id)
        if existing_vehicles and len(existing_vehicles) > 0:
            return DispatchBusiness._bad("该任务已经分配了车辆，一个任务只能派遣一辆车或一个车厢")
        
        return DispatchBusiness._ok()

    @staticmethod
    def validate_task_completion(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # 备注可选，但若提供需为字符串（兼容 completion_note 与 completion_notes）
        note = data.get('completion_note', data.get('completion_notes', None))
        if note is not None and not isinstance(note, str):
            return DispatchBusiness._bad("completion_note 必须为字符串")
        return DispatchBusiness._ok()

    # == 新增：根据角色决定初始状态的辅助方法 ==
    @staticmethod
    def _get_initial_status_by_role_and_business_type(business_type: str) -> str:
        """
        根据用户角色和业务类型获取初始状态
        
        参数:
            business_type: 业务类型（自办派车/委办派车）
        
        返回:
            str: 初始状态
        """
        # 获取当前用户角色
        current_user = getattr(g, 'current_user', None)
        if not current_user:
            return '待审核'  # 默认待审核状态
        
        # 获取用户的第一个角色作为主要角色
        user_roles = [role.name for role in current_user.roles] if current_user.roles else []
        if not user_roles:
            return '待审核'  # 默认待审核状态
        
        primary_role = user_roles[0]
        
        # 根据角色和业务类型确定初始状态
        if primary_role in ['超级管理员', '区域调度员']:
            return '审核通过'  # 管理员和区域调度员创建的任务直接审核通过
        elif primary_role == '车间地调':
            return '待审核'   # 车间地调创建的任务需要审核
        else:
            return '待审核'   # 其他角色默认需要审核
    
    @staticmethod
    def _determine_next_status_after_approval(data: Dict[str, Any], business_type: str) -> str:
        """
        根据业务规则决定审核通过后的下一个状态
        
        参数:
            data: 派车任务数据
            business_type: 业务类型
            
        返回:
            str: 下一个状态
        """
        # 根据业务类型决定下一个状态
        if business_type == '委办派车':
            return '待响应'  # 委办派车等待供应商响应
        else:
            return '待响应'  # 自办派车等待内部车队响应

    # == 既有方法 ==
    @staticmethod
    def create_dispatch_task(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建派车任务
        
        参数:
            data: 派车任务数据
            
        返回:
            Dict[str, Any]: 创建的派车任务
        """
        # 验证必填字段 - 与服务层create_task方法保持一致
        required_fields = ['required_date', 'origin_bureau', 'mail_route_name', 'transport_type', 'requirement_type', 'required_weight', 'required_volume']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 获取当前用户
        current_user = getattr(g, 'current_user', None)
        if not current_user:
            raise ValueError("无法获取当前用户信息")
        
        # 根据业务类型和用户角色设置初始状态
        business_type = data.get('business_type', '委办派车')
        initial_status = DispatchBusiness._get_initial_status_by_role_and_business_type(business_type)
        data['status'] = initial_status
        data['created_by'] = current_user.id
        data['created_at'] = datetime.now()
        
        # 如果是超级管理员或区域调度员发起，直接设置为审核通过后的状态
        if initial_status == '审核通过':
            next_status = DispatchBusiness._determine_next_status_after_approval(data, business_type)
            data['status'] = next_status
        
        # 调用服务层创建任务，传递current_user参数
        task = DispatchService.create_dispatch_task(data, current_user)
        
        # 记录操作日志
        log_details = {
            'task_data': {
                'required_date': str(data.get('required_date')),
                'origin_bureau': data.get('origin_bureau'),
                'mail_route_name': data.get('mail_route_name'),
                'transport_type': data.get('transport_type'),
                'requirement_type': data.get('requirement_type'),
                'required_weight': data.get('required_weight'),
                'required_volume': data.get('required_volume')
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
        
        # 验证任务状态，只有待审核状态的任务可以更新
        if task['status'] != '待审核':
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
        
        Args:
            task_id: 任务ID
            approval_data: 审批数据
            
        Returns:
            Dict: 处理结果
        """
        from app.models.task import ManualDispatchTask
        from app.models.dispatch_status_history import DispatchStatusHistory
        from app.extensions import db
        from datetime import datetime
        from flask_jwt_extended import get_current_user
        
        try:
            # 获取当前用户
            current_user = get_current_user()
            if not current_user:
                raise ValueError('无法获取当前用户信息')
            
            # 查找任务
            task = ManualDispatchTask.query.filter_by(task_id=task_id).first()
            if not task:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态
            if task.status != '待审核':
                raise ValueError(f'任务状态不允许审批，当前状态：{task.status}')
            
            # 获取审批结果
            approved = approval_data.get('approved', False)
            remarks = approval_data.get('remarks', '')
            
            # 根据审批结果设置新状态
            if approved:
                new_status = '待响应'  # 审核通过后等待响应
            else:
                new_status = '审核拒绝'
            
            # 识别操作者角色（用于状态管理器）
            operator_role = None
            try:
                operator_role = current_user.roles[0].name if getattr(current_user, 'roles', None) else None
            except Exception:
                operator_role = None
            operator_role = operator_role or '系统'
            
            # 计算下一处理角色：自办派车时根据“派车单位(organizing_unit_id)”自动判定 班组长/大容积供应商；其他情况走统一规则
            auto_pick_note = ''
            if approved and getattr(task, 'business_type', None) == '自办派车':
                try:
                    from app.models.company import DispatchUnit
                    unit = None
                    if getattr(task, 'organizing_unit_id', None):
                        unit = DispatchUnit.query.get(task.organizing_unit_id)
                    if not unit and getattr(task, 'organizing_unit_obj', None):
                        unit = task.organizing_unit_obj
                    if unit and getattr(unit, 'unit_type', None) == '内部单位':
                        next_handler_role = '班组长'
                        auto_pick_note = f"（自动选择：派车单位类型=内部单位 → 下一处理人=班组长）"
                    elif unit and getattr(unit, 'unit_type', None) == '供应商':
                        next_handler_role = '大容积供应商'
                        auto_pick_note = f"（自动选择：派车单位类型=供应商 → 下一处理人=大容积供应商）"
                    else:
                        # 回退到统一规则
                        next_handler_role = DispatchStatusManager.get_next_handler_role(
                            previous_status=task.status,
                            new_status=new_status,
                            operator_role=operator_role,
                            business_type=getattr(task, 'business_type', None)
                        )
                        if unit:
                            auto_pick_note = f"（自动选择回退：未知单位类型={getattr(unit, 'unit_type', None)} → 统一规则={next_handler_role}）"
                        else:
                            auto_pick_note = f"（自动选择回退：未找到派车单位 → 统一规则={next_handler_role}）"
                except Exception:
                    # 任何异常也回退到统一规则
                    next_handler_role = DispatchStatusManager.get_next_handler_role(
                        previous_status=task.status,
                        new_status=new_status,
                        operator_role=operator_role,
                        business_type=getattr(task, 'business_type', None)
                    )
                    auto_pick_note = f"（自动选择异常回退 → 统一规则={next_handler_role}）"
            else:
                # 非自办或未通过审批，走统一规则
                next_handler_role = DispatchStatusManager.get_next_handler_role(
                    previous_status=task.status,
                    new_status=new_status,
                    operator_role=operator_role,
                    business_type=getattr(task, 'business_type', None)
                )
            
            # 更新任务状态
            task.status = new_status
            task.current_handler_role = next_handler_role
            task.updated_at = datetime.now()
            
            # 记录状态历史 - 使用模型字段 status_change/timestamp/note/next_handler_role
            status_history = DispatchStatusHistory(
                task_id=task_id,
                status_change=new_status,
                operator=str(current_user.id),  # 记录用户ID
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                note=f"审批{'通过' if approved else '拒绝'}：{remarks}" + (auto_pick_note or ''),
                next_handler_role=next_handler_role
            )
            db.session.add(status_history)
            
            # 提交事务
            db.session.commit()
            
            return {
                'task_id': task_id,
                'status': new_status,
                'current_handler_role': next_handler_role,
                'message': f"任务审批{'通过' if approved else '拒绝'}成功"
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
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
        
        # 验证任务状态：允许在“审核通过/待响应”阶段分配车辆
        from app.business.dispatch.status_manager import DispatchStatusManager as _DSM
        norm_status = _DSM._normalize_status(task['status'])
        if norm_status != 'approved':
            raise ValueError(f"当前任务状态为 {task['status']}，不能进行车辆分配操作")
        
        # 验证车辆数据（允许缺少 vehicle_id 时按车牌新建）
        if not vehicle_data.get('vehicle_id') and not vehicle_data.get('license_plate'):
            raise ValueError("缺少必填字段: vehicle_id 或 license_plate 至少提供一个")
        for field in ['driver_name', 'driver_phone']:
            if field not in vehicle_data or not vehicle_data.get(field):
                raise ValueError(f"缺少必填字段: {field}")
        
        # 调用服务层分配车辆
        vehicle_assignment = DispatchService.assign_vehicle_to_task(task_id, vehicle_data)
        
        # 使用状态管理器更新任务状态 -> 进入“已分配”
        comment = f"分配车辆: {vehicle_data.get('vehicle_id') or vehicle_data.get('license_plate')}"
        result = DispatchStatusManager.update_task_status(task_id, '已分配', comment)
        
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
        
        # 验证任务状态，已响应的任务可以完成
        if task['status'] != '已响应':
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

    @staticmethod
    def process_workshop_verification(task_id: str, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理车间地调核实操作
        
        Args:
            task_id: 任务ID
            verification_data: 核实数据
            
        Returns:
            Dict: 处理结果
        """
        from app.models.task import ManualDispatchTask
        from app.models.dispatch_status_history import DispatchStatusHistory
        from app.extensions import db
        from datetime import datetime
        from flask_jwt_extended import get_current_user
        
        try:
            # 获取当前用户
            current_user = get_current_user()
            if not current_user:
                raise ValueError('无法获取当前用户信息')
            
            # 查找任务
            task = ManualDispatchTask.query.filter_by(task_id=task_id).first()
            if not task:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态 - 只有"已响应"状态的任务可以进行核实
            if task.status not in ['已响应', 'supplier_responded', 'team_assigned']:
                raise ValueError(f'任务状态不允许核实操作，当前状态：{task.status}')
            
            # 获取核实操作类型
            verification_type = verification_data.get('verification_type')  # 'approve', 'downgrade', 'merge'
            remarks = verification_data.get('remarks', '')
            
            if verification_type == 'approve':
                # 核实通过，进入下一状态
                new_status = '核实通过'
                next_handler_role = '供应商'  # 返回给供应商确认
                
            elif verification_type == 'downgrade':
                # 降档操作
                downgrade_reason = verification_data.get('downgrade_reason', '')
                new_status = '已降档'
                next_handler_role = '供应商'  # 返回给供应商重新响应
                
                # 调用车辆降档业务逻辑
                from app.business.vehicle.vehicle_downgrade_business import VehicleDowngradeBusiness
                vehicle_ids = verification_data.get('vehicle_ids', [])
                for vehicle_id in vehicle_ids:
                    VehicleDowngradeBusiness.downgrade_vehicle(
                        vehicle_id=vehicle_id,
                        downgrade_reason=downgrade_reason,
                        operator_id=current_user.id
                    )
                
            elif verification_type == 'merge':
                # 合并操作
                merge_data = verification_data.get('merge_data', {})
                source_vehicle_id = merge_data.get('source_vehicle_id')
                target_vehicle_id = merge_data.get('target_vehicle_id')
                
                if not source_vehicle_id or not target_vehicle_id:
                    raise ValueError('合并操作需要提供源车辆ID和目标车辆ID')
                
                # 调用车辆合并业务逻辑
                DispatchBusiness.merge_vehicles(
                    source_vehicle_id=source_vehicle_id,
                    target_vehicle_id=target_vehicle_id
                )
                
                new_status = '已合并'
                next_handler_role = '供应商'  # 返回给供应商确认
                
            else:
                raise ValueError(f'不支持的核实操作类型：{verification_type}')
            
            # 更新任务状态
            task.status = new_status
            task.current_handler_role = next_handler_role
            task.updated_at = datetime.now()
            
            # 记录状态历史
            status_history = DispatchStatusHistory(
                task_id=task_id,
                status_change=new_status,
                operator=str(current_user.id),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                note=f'车间地调核实操作（{verification_type}）：{remarks}',
                next_handler_role=next_handler_role
            )
            db.session.add(status_history)
            
            # 提交事务
            db.session.commit()
            
            return {
                'task_id': task_id,
                'status': new_status,
                'current_handler_role': next_handler_role,
                'verification_type': verification_type,
                'message': f'车间地调核实操作（{verification_type}）成功'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e