#!/usr/bin/env python3
"""
车辆降档业务逻辑模块

处理车辆降档相关的业务规则和验证逻辑，位于应用层
"""

from datetime import datetime
from app.services.vehicle.vehicle_service import VehicleService
from app.services.dispatch.dispatch_service import DispatchService
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class VehicleDowngradeBusiness:
    """
    车辆降档业务逻辑类
    负责处理车辆降档相关的业务规则和验证逻辑
    """
    
    @staticmethod
    def process_vehicle_downgrade(vehicle_id: int, downgrade_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理车辆降档
        
        参数:
            vehicle_id: 车辆ID
            downgrade_record: 降档记录数据
            
        返回:
            Dict[str, Any]: 降档结果
        """
        # 验证车辆是否存在
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"车辆不存在: ID {vehicle_id}")
        
        # 验证车辆当前状态是否允许降档
        if vehicle.get('status') not in ['available', 'maintenance']:
            raise ValueError(f"车辆当前状态为 {vehicle.get('status')}，不允许降档")
        
        # 验证车辆是否有进行中的任务
        active_tasks = DispatchService.get_vehicle_active_tasks(vehicle_id)
        if active_tasks and len(active_tasks) > 0:
            raise ValueError(f"车辆有{len(active_tasks)}个进行中的任务，无法降档")
        
        # 验证降档类型是否有效
        valid_types = VehicleService.get_valid_vehicle_types()
        if downgrade_record.get('new_type') not in valid_types:
            raise ValueError(f"无效的车辆类型: {downgrade_record.get('new_type')}")
        
        # 验证降档类型是否低于当前类型
        current_type_level = VehicleService.get_vehicle_type_level(vehicle.get('vehicle_type'))
        new_type_level = VehicleService.get_vehicle_type_level(downgrade_record.get('new_type'))
        
        if new_type_level >= current_type_level:
            raise ValueError(f"降档类型 {downgrade_record.get('new_type')} 不低于当前类型 {vehicle.get('vehicle_type')}")
        
        # 创建降档记录
        downgrade_result = VehicleService.create_vehicle_downgrade_record(downgrade_record)
        
        # 更新车辆类型
        VehicleService.update_vehicle(vehicle_id, {'vehicle_type': downgrade_record.get('new_type')})
        
        return {
            'success': True,
            'message': f"成功将车辆 {vehicle.get('plate_number')} 从 {downgrade_record.get('previous_type')} 降档为 {downgrade_record.get('new_type')}",
            'downgrade_record': downgrade_result
        }
    
    @staticmethod
    def get_vehicle_downgrade_history(vehicle_id: int) -> List[Dict[str, Any]]:
        """
        获取车辆降档历史
        
        参数:
            vehicle_id: 车辆ID
            
        返回:
            List[Dict[str, Any]]: 降档历史记录列表
        """
        # 验证车辆是否存在
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"车辆不存在: ID {vehicle_id}")
        
        # 获取降档历史记录
        downgrade_history = VehicleService.get_vehicle_downgrade_records(vehicle_id)
        
        return downgrade_history