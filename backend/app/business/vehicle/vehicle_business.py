#!/usr/bin/env python3
"""
车辆业务逻辑模块

处理车辆相关的业务规则和验证逻辑，位于应用层
"""

from typing import Dict, Any, Tuple, List, Optional
from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
from app.models.vehicle.vehicle_volume_history import VehicleVolumeHistory
import logging

logger = logging.getLogger(__name__)

class VehicleBusiness:
    """
    车辆业务逻辑类，处理车辆相关的业务规则和验证逻辑
    """
    
    @staticmethod
    def validate_volume_update(vehicle: Vehicle, new_volume: float) -> Tuple[bool, str]:
        """
        验证车辆容积更新是否符合业务规则
        
        Args:
            vehicle: 车辆对象
            new_volume: 新容积值
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 获取车型折算系数表
        conversion_factors = VehicleBusiness.get_vehicle_conversion_factors()
        
        # 查找对应车型的容积范围
        vehicle_type = None
        min_volume = 0
        conversion_factor = 0
        
        # 根据当前容积确定车型
        for factor_info in conversion_factors:
            if vehicle.actual_volume >= factor_info['min_volume']:
                if min_volume <= factor_info['min_volume']:
                    min_volume = factor_info['min_volume']
                    vehicle_type = factor_info['vehicle_type']
                    conversion_factor = factor_info['conversion_factor']
        
        if not vehicle_type:
            return False, "无法确定车辆类型，请检查容积值"
        
        # 获取该车型的容积范围
        volume_range = None
        for factor_info in conversion_factors:
            if factor_info['vehicle_type'] == vehicle_type:
                volume_range = (factor_info['min_volume'], factor_info.get('max_volume'))
                break
        
        if not volume_range:
            return False, f"无法获取车型{vehicle_type}的容积范围"
        
        # 验证新容积是否在允许范围内
        min_allowed = volume_range[0] * 0.9  # 允许比最小值小10%
        max_allowed = volume_range[1] * 1.1 if volume_range[1] else float('inf')  # 允许比最大值大10%
        
        if new_volume < min_allowed:
            return False, f"新容积{new_volume}小于允许的最小值{min_allowed:.2f}"
        
        if volume_range[1] and new_volume > max_allowed:
            return False, f"新容积{new_volume}大于允许的最大值{max_allowed:.2f}"
        
        return True, ""
    
    @staticmethod
    def calculate_equivalent_volume(actual_volume: float) -> float:
        """
        根据实际容积和车型折算系数计算等效容积
        
        Args:
            actual_volume: 实际容积
            
        Returns:
            float: 等效容积
        """
        # 获取车型折算系数表
        conversion_factors = VehicleBusiness.get_vehicle_conversion_factors()
        
        # 查找对应车型的折算系数
        conversion_factor = 1.0  # 默认为1.0
        
        # 根据容积确定车型
        for factor_info in conversion_factors:
            if actual_volume >= factor_info['min_volume']:
                if factor_info.get('max_volume') is None or actual_volume <= factor_info['max_volume']:
                    conversion_factor = factor_info['conversion_factor']
                    break
        
        # 计算等效容积
        equivalent_volume = actual_volume * conversion_factor
        
        return equivalent_volume
    
    @staticmethod
    def get_vehicle_conversion_factors() -> List[Dict[str, Any]]:
        """
        获取车型折算系数表
        
        Returns:
            List[Dict[str, Any]]: 车型折算系数表
        """
        # 从数据库获取车型折算系数表
        references = VehicleCapacityReference.query.all()
        
        # 转换为字典列表
        factors = []
        for ref in references:
            factor_info = ref.to_dict()
            factor_info['min_volume'] = ref.min_capacity
            factor_info['max_volume'] = ref.max_capacity
            factor_info['vehicle_type'] = ref.vehicle_type
            factor_info['conversion_factor'] = ref.conversion_factor
            factors.append(factor_info)
        
        # 按最小容积排序
        factors.sort(key=lambda x: x['min_volume'])
        
        return factors
    
    @staticmethod
    def process_volume_update(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理车辆容积更新业务逻辑
        
        Args:
            data: 容积更新数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        from app.services.vehicle_service import VehicleService
        
        # 获取车辆信息
        vehicle_id = data.get('vehicle_id')
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        
        if not vehicle:
            raise ValueError(f"车辆ID {vehicle_id} 不存在")
        
        # 验证新容积是否符合业务规则
        new_volume = data.get('new_volume')
        is_valid, error_msg = VehicleBusiness.validate_volume_update(vehicle, new_volume)
        
        if not is_valid:
            raise ValueError(error_msg)
        
        # 调用服务层更新车辆容积
        result = VehicleService.update_vehicle_volume(data)
        
        # 计算等效容积
        result['equivalent_volume'] = VehicleBusiness.calculate_equivalent_volume(new_volume)
        
        return result