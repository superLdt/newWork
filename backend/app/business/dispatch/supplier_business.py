"""
供应商相关业务逻辑模块

处理供应商响应和相关业务逻辑
"""

from datetime import datetime
from typing import Dict, Any

from flask_jwt_extended import get_current_user

from app.extensions import db
from app.models.task import ManualDispatchTask
from app.models.vehicle.vehicle import Vehicle
from app.models.dispatch_status_history import DispatchStatusHistory
from app.business.dispatch.base_business import BaseDispatchBusiness
from app.business.dispatch.status_manager import DispatchStatusManager
from app.services.dispatch.dispatch_service import DispatchService


class SupplierDispatchBusiness(BaseDispatchBusiness):
    """供应商派车业务逻辑类"""
    

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
            return BaseDispatchBusiness._error('请求数据不能为空')
        
        # 验证必填字段
        required_fields = ['task_id', 'manifest_number', 'dispatch_number', 'vehicles']
        for field in required_fields:
            if not data.get(field):
                return BaseDispatchBusiness._error(f'{field} 不能为空')
        
        # 验证车辆和车厢数据
        vehicles = data.get('vehicles', [])
        carriages = data.get('carriages', [])
        
        return BaseDispatchBusiness.validate_vehicle_data(vehicles, carriages)
    
    @staticmethod
    def process_supplier_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理供应商响应
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 处理结果
        """
        try:
            task_id = data['task_id']
            
            # 获取当前用户
            current_user = get_current_user()
            if not current_user:
                raise ValueError('无法获取当前用户信息')

            # 使用服务层获取任务信息
            task_dict = DispatchService.get_dispatch_task_by_id(task_id)
            if not task_dict:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态（兼容中英文状态，统一业务层使用中文）
            allowed_statuses = {'待响应', '审核通过'}
            if task_dict['status'] not in allowed_statuses:
                raise ValueError(f'任务状态不允许提交供应商响应，当前状态：{task_dict["status"]}')
            
            # 创建车辆记录
            for vehicle_data in data['vehicles']:
                vehicle_data_prepared = {
                    'task_id': task_id,
                    'manifest_number': data['manifest_number'],
                    'dispatch_number': data['dispatch_number'],
                    'license_plate': vehicle_data['license_plate'],
                    'carriage_number': vehicle_data.get('carriage_number', ''),
                    'vehicle_type': vehicle_data['vehicle_type'],
                    'actual_volume': vehicle_data.get('actual_volume', 0),
                    'required_volume': vehicle_data.get('required_volume', 0),
                    'supplier_id': current_user.dispatch_unit_id if hasattr(current_user, 'dispatch_unit_id') else None,
                    'notes': data.get('notes', ''),
                    'supplier_type': '供应商'
                }
                # 调用服务层创建车辆
                DispatchService.create_vehicle(vehicle_data_prepared)
            
            # 使用状态管理器计算下一个处理角色和状态
            # 统一：时间线写入"已响应"，任务当前状态置为"待车间核查"
            timeline_status = '已响应'
            next_handler_role = DispatchStatusManager.get_next_handler_role(
                previous_status=task_dict['status'],
                new_status=timeline_status,
                operator_role='供应商',
                business_type=task_dict.get('business_type', '')
            )
            
            # 使用状态管理器更新任务状态和处理角色（任务实际状态进入"待车间核查"）
            DispatchStatusManager.update_task_status(
                task_id=task_id,
                new_status='待核查',
                comment=f"供应商提交响应，清单号:{data.get('manifest_number','')}, 派车单:{data.get('dispatch_number','')}"
            )
            
            # 记录状态历史 - 修复：使用模型字段 status_change/timestamp/note
            # 注意：状态历史记录已在DispatchStatusManager.update_task_status中处理
            # 这里不再重复记录
            
            return {
                'valid': True,
                'task_id': task_id,
                'status': '待核查',
                'current_handler_role': next_handler_role,
                'message': '供应商响应提交成功'
            }
            
        except Exception as e:
            return BaseDispatchBusiness._error(f'处理供应商响应失败：{str(e)}')
    
    @staticmethod
    def process_supplier_confirmation(task_id: str, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理供应商确认操作
        
        Args:
            task_id: 任务ID
            confirmation_data: 确认数据
            
        Returns:
            Dict: 处理结果
        """
        try:
            # 获取任务信息
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'success': False,
                    'message': '任务不存在'
                }
            
            # 检查任务状态是否允许确认
            if task['status'] != '待确认':
                return {
                    'success': False,
                    'message': f'任务状态不允许确认操作，当前状态：{task["status"]}'
                }
            
            # 获取当前用户信息
            current_user = get_current_user()
            if not current_user:
                return {
                    'success': False,
                    'message': '无法获取当前用户信息'
                }
            
            # 更新任务状态为已确认
            update_data = {
                'status': '已确认',
                'confirmed_by': current_user.id,
                'current_handler_user_id': current_user.id,  # 记录当前处理人用户ID
                'confirmed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'confirmed_volume': confirmation_data.get('confirmed_volume'),
                'confirmation_notes': confirmation_data.get('confirmation_notes', '')
            }
            
            # 如果是合并任务（status_type=2），保持原有的actual_weight（合并后的总重量）
            # 如果不是合并任务，则可以更新actual_weight
            if task.get('status_type') != 2:
                # 非合并任务，可以根据确认数据更新actual_weight
                if confirmation_data.get('actual_weight'):
                    actual_weight = confirmation_data.get('actual_weight')
                    # 格式化actual_weight，确保带有"吨"字后缀
                    if actual_weight and not str(actual_weight).endswith('吨'):
                        # 提取数字部分
                        import re
                        weight_match = re.search(r'(\d+(?:\.\d+)?)', str(actual_weight))
                        if weight_match:
                            weight_value = weight_match.group(1)
                            actual_weight = f"{weight_value}吨"
                    update_data['actual_weight'] = actual_weight
            # 合并任务不更新actual_weight，保持合并时计算的总重量
            
            # 使用服务层更新任务
            updated_task = DispatchService.update_task(task_id, update_data)
            
            # 记录状态历史
            status_history_data = {
                'previous_status': '待确认',
                'new_status': '已确认',
                'changed_by': current_user.id,
                'changed_at': datetime.now(),
                'comment': f'供应商确认完成。{confirmation_data.get("confirmation_notes", "")}',
                'next_handler_role': None  # 已完成，无下一处理人
            }
            
            DispatchService.update_task_status(task_id, '已确认', status_history_data)
            
            # 将任务标记为已完成
            final_update_data = {
                'status': '已完成',
                'current_handler_user_id': current_user.id,  # 记录当前处理人用户ID
                'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            DispatchService.update_task(task_id, final_update_data)
            
            # 记录完成状态历史
            completion_history_data = {
                'previous_status': '已确认',
                'new_status': '已完成',
                'changed_by': current_user.id,
                'changed_at': datetime.now(),
                'comment': '任务已完成',
                'next_handler_role': None
            }
            
            DispatchService.update_task_status(task_id, '已完成', completion_history_data)
            
            return {
                'success': True,
                'data': {
                    'task_id': task_id,
                    'status': '已完成',
                    'confirmed_by': current_user.id,
                    'confirmed_at': update_data['confirmed_at'],
                    'confirmed_volume': update_data['confirmed_volume'],
                    'confirmation_notes': update_data['confirmation_notes']
                },
                'message': '供应商确认成功，任务已完成'
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'处理供应商确认失败: {str(e)}')
            return {
                'success': False,
                'message': f'处理供应商确认失败: {str(e)}'
            }
    
    
    # 注意：申诉审核为管理员/调度员操作，已迁移至服务层 AppealService

    @staticmethod
    def get_task_operation_records(task_id: str) -> Dict[str, Any]:
        """
        获取任务操作记录
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 操作记录
        """
        try:
            from app.services.vehicle.vehicle_merge_service import VehicleMergeService
            
            # 获取任务信息
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'success': False,
                    'message': '任务不存在'
                }
            
            # 获取状态历史记录
            status_history = DispatchService.get_task_status_history(task_id)
            
            # 获取车辆合并记录
            merge_records = VehicleMergeService.get_merge_records_by_task(task_id)
            
            # 格式化操作记录
            operation_records = []
            for record in status_history:
                operation_records.append({
                    'id': record.get('id'),
                    'status_change': record.get('status_change'),
                    'operator': record.get('operator'),
                    'timestamp': record.get('timestamp'),
                    'note': record.get('note'),
                    'next_handler_role': record.get('next_handler_role'),
                    'next_handler_user_id': record.get('next_handler_user_id')
                })
            
            return {
                'success': True,
                'data': {
                    'task_id': task_id,
                    'task_info': task,
                    'operation_records': operation_records,
                    'vehicle_merge_records': merge_records.get('source_records', []),
                    'target_merge_records': merge_records.get('target_records', [])
                },
                'message': '获取操作记录成功'
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'获取任务操作记录失败: {str(e)}')
            return {
                'success': False,
                'message': f'获取任务操作记录失败: {str(e)}'
            }