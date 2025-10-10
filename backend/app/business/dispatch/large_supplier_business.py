"""
大容积供应商相关业务逻辑模块

处理大容积供应商响应和确认相关业务逻辑
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

class LargeSupplierDispatchBusiness(BaseDispatchBusiness):
    """大容积供应商派车业务逻辑类"""
    
    @staticmethod
    def validate_large_capacity_supplier_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证大容积供应商响应数据
        
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
    def validate_outsourcing_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证外包管理公司响应数据（已废弃，请使用validate_large_capacity_supplier_response）
        
        Args:
            data: 响应数据
            
        Returns:
            Dict: 验证结果
        """
        # 为了向后兼容，保留此方法，但调用新方法
        return LargeSupplierDispatchBusiness.validate_large_capacity_supplier_response_data(data)
    
    @staticmethod
    def process_large_capacity_supplier_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理大容积供应商响应
        
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
            allowed_statuses = {'待响应'}
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
                    'supplier_type': '大容积供应商'
                }
                # 调用服务层创建车辆
                DispatchService.create_vehicle(vehicle_data_prepared)
            
            # 使用状态管理器计算下一个处理角色和状态
            timeline_status = '已响应'
            next_handler_role = DispatchStatusManager.get_next_handler_role(
                previous_status=task_dict['status'],
                new_status=timeline_status,
                operator_role='大容积供应商',
                business_type=task_dict.get('business_type', '') if task_dict.get('business_type') else None
            )
            
            # 使用状态管理器更新任务状态和处理角色（任务实际状态进入"待核查"）
            DispatchStatusManager.update_task_status(
                task_id=task_id,
                new_status='待核查',
                comment=f"大容积供应商提交响应，清单号:{data.get('manifest_number','')}, 派车单:{data.get('dispatch_number','')}"
            )
            
            return {
                 'valid': True,
                 'task_id': task_id,
                 'status': '待核查',
                 'current_handler_role': next_handler_role,
                 'message': '大容积供应商响应提交成功'
             }
        except Exception as e:
            return BaseDispatchBusiness._error(f'处理大容积供应商响应失败：{str(e)}')
    
    @staticmethod
    def confirm_large_capacity_supplier_task(task_id: str, confirm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        大容积供应商确认任务
        
        Args:
            task_id: 任务ID
            confirm_data: 确认数据
            
        Returns:
            Dict: 确认结果
        """
        try:
            # 获取当前用户
            current_user = get_current_user()
            if not current_user:
                raise ValueError('无法获取当前用户信息')

            # 使用服务层获取任务信息
            task_dict = DispatchService.get_dispatch_task_by_id(task_id)
            if not task_dict:
                raise ValueError(f'任务 {task_id} 不存在')
            
            # 检查任务状态（兼容中英文状态）
            allowed_statuses = {'待确认', 'awaiting_confirmation'}
            if task_dict['status'] not in allowed_statuses:
                raise ValueError(f'任务状态不允许确认，当前状态：{task_dict["status"]}')
            
            # 检查业务类型是否为大容积派车
            if task_dict.get('business_type') != '大容积派车':
                raise ValueError(f'只有大容积派车任务才能使用此确认接口，当前业务类型：{task_dict.get("business_type")}')
            
            # 检查用户是否为大容积供应商
            user_roles = [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
            if '大容积供应商' not in user_roles:
                raise ValueError('只有大容积供应商角色才能使用此确认接口')
            
            # 检查任务是否属于当前用户的派车单位
            unit_id = getattr(current_user, 'dispatch_unit_id', None)
            if not unit_id or task_dict.get('organizing_unit_id') != unit_id:
                raise ValueError('您只能确认属于您所在派车单位的任务')
            
            # 格式化actual_weight，确保带有"吨"字后缀
            current_actual_weight = task_dict.get('actual_weight')
            if current_actual_weight and not str(current_actual_weight).endswith('吨'):
                # 提取数字部分并添加"吨"字
                import re
                match = re.search(r'(\d+(?:\.\d+)?)', str(current_actual_weight))
                if match:
                    formatted_weight = f"{match.group(1)}吨"
                    # 更新actual_weight字段
                    DispatchService.update_task(task_id, {'actual_weight': formatted_weight})
            
            # 更新任务状态为已确认（与普通供应商确认保持一致）
            update_data = {
                'status': '已确认',
                'confirmed_by': current_user.id,
                'current_handler_user_id': current_user.id,  # 记录当前处理人用户ID
                'confirmed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'confirmation_notes': confirm_data.get('notes', '')
            }
            
            # 使用服务层更新任务
            DispatchService.update_task(task_id, update_data)
            
            # 记录状态历史
            status_history_data = {
                'previous_status': '待确认',
                'new_status': '已确认',
                'changed_by': current_user.id,
                'changed_at': datetime.now(),
                'comment': f'大容积供应商确认完成。{confirm_data.get("notes", "")}',
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
                'valid': True,
                'task_id': task_id,
                'status': '已完成',
                'message': '大容积供应商确认成功'
            }
        except Exception as e:
            return BaseDispatchBusiness._error(f'大容积供应商确认失败：{str(e)}')