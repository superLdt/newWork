"""
班组相关业务逻辑模块

处理班组响应和相关业务逻辑
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

class TeamDispatchBusiness(BaseDispatchBusiness):
    """班组长派车业务逻辑类"""
    
    @staticmethod
    def validate_team_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证班组响应数据
        
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
    def process_team_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理班组响应
        
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
                raise ValueError(f'任务状态不允许提交班组响应，当前状态：{task_dict["status"]}')
            
            # 创建车辆记录
            for vehicle_data in data['vehicles']:
                vehicle_data_prepared = {
                    'task_id': task_id,
                    'manifest_number': data['manifest_number'],
                    'dispatch_number': data['dispatch_number'],
                    'license_plate': vehicle_data['license_plate'],
                    'carriage_number': vehicle_data.get('carriage_number', ''),
                    'vehicle_type': vehicle_data.get('vehicle_type', ''),
                    'vehicle_category': vehicle_data.get('vehicle_category', ''),
                    # 使用VehicleCapacityReference的字段
                    'actual_volume': vehicle_data.get('actual_volume', 0),  # 使用前端传入的实际容积
                    'required_volume': vehicle_data.get('required_volume', 0),
                    'original_capacity': vehicle_data.get('original_capacity', 0),
                    'supplier_id': current_user.dispatch_unit_id if hasattr(current_user, 'dispatch_unit_id') else None,
                    'notes': data.get('notes', ''),
                    'supplier_type': '班组'
                }
                
                # 调用服务层创建车辆
                DispatchService.create_vehicle(vehicle_data_prepared)
            
            # 计算下一处理角色并更新任务状态（先保存旧状态）
            old_status = task_dict['status']
            timeline_status = '已响应'
            next_role = DispatchStatusManager.get_next_handler_role(
                previous_status=old_status,
                new_status=timeline_status,
                operator_role='班组长',
                business_type=task_dict.get('business_type', '') if task_dict.get('business_type') else None
            )
            
            # 使用状态管理器更新任务状态和处理角色（任务实际状态进入"待车间核查"）
            DispatchStatusManager.update_task_status(
                task_id=task_id,
                new_status='待核查',
                comment=data.get('notes', '')
            )
            
            return {
                'valid': True,
                'task_id': task_id,
                'status': '待核查',
                'current_handler_role': next_role,
                'message': '班组派车响应提交成功'
            }
            
        except Exception as e:
            return BaseDispatchBusiness._error(f'处理班组响应失败：{str(e)}')