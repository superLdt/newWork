"""
车辆业务服务层

负责处理车辆相关的业务逻辑，包括：
- 业务规则验证
- 外部服务调用
- 复杂的业务逻辑处理
- 数据转换和标准化
"""

import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_repository import VehicleRepository
from app.external_services.supplier_api import SupplierAPIClient
from app.external_services.validation_service import ValidationService
from app.utils.validators import LicensePlateValidator
from app.exceptions.business_exceptions import (
    VehicleValidationError,
    ExternalServiceError,
    VehicleNotFoundError
)

logger = logging.getLogger(__name__)


class VehicleService:
    """车辆业务服务类"""
    
    def __init__(self):
        self.repository = VehicleRepository()
        self.supplier_client = SupplierAPIClient()
        self.validation_service = ValidationService()
        self.license_plate_validator = LicensePlateValidator()
    
    def create_vehicle(self, vehicle_data: Dict[str, Any]) -> Vehicle:
        """
        创建新车辆
        
        Args:
            vehicle_data: 车辆数据字典
            
        Returns:
            创建成功的车辆对象
            
        Raises:
            VehicleValidationError: 数据验证失败
            ExternalServiceError: 外部服务调用失败
        """
        try:
            # 1. 数据验证
            self._validate_vehicle_data(vehicle_data)
            
            # 2. 标准化车牌号
            normalized_plate = self._normalize_license_plate(
                vehicle_data.get('license_plate')
            )
            vehicle_data['normalized_license_plate'] = normalized_plate
            
            # 3. 验证车牌号唯一性
            if self.repository.exists_by_license_plate(normalized_plate):
                raise VehicleValidationError(
                    f"车牌号 '{vehicle_data.get('license_plate')}' 已存在"
                )
            
            # 4. 获取供应商信息
            supplier_info = self._get_supplier_info(vehicle_data.get('supplier_id'))
            vehicle_data['supplier_category'] = supplier_info.get('category')
            
            # 5. 计算运力评分
            capacity_score = self._calculate_capacity_score(vehicle_data)
            vehicle_data['capacity_score'] = capacity_score
            
            # 6. 设置时间戳
            vehicle_data['created_at'] = datetime.utcnow()
            vehicle_data['updated_at'] = datetime.utcnow()
            
            # 7. 保存到数据库
            vehicle = self.repository.create(vehicle_data)
            
            logger.info(f"成功创建车辆: {vehicle.id}")
            return vehicle
            
        except Exception as e:
            logger.error(f"创建车辆失败: {str(e)}")
            raise
    
    def update_vehicle(self, vehicle_id: int, update_data: Dict[str, Any]) -> Vehicle:
        """
        更新车辆信息
        
        Args:
            vehicle_id: 车辆ID
            update_data: 更新数据字典
            
        Returns:
            更新后的车辆对象
            
        Raises:
            VehicleNotFoundError: 车辆不存在
            VehicleValidationError: 数据验证失败
        """
        try:
            # 1. 检查车辆是否存在
            vehicle = self.repository.get_by_id(vehicle_id)
            if not vehicle:
                raise VehicleNotFoundError(f"车辆ID {vehicle_id} 不存在")
            
            # 2. 数据验证
            self._validate_vehicle_data(update_data, is_update=True)
            
            # 3. 如果更新车牌号，重新标准化
            if 'license_plate' in update_data:
                normalized_plate = self._normalize_license_plate(
                    update_data['license_plate']
                )
                update_data['normalized_license_plate'] = normalized_plate
                
                # 检查唯一性（排除当前车辆）
                if self.repository.exists_by_license_plate_excluding(
                    normalized_plate, vehicle_id
                ):
                    raise VehicleValidationError(
                        f"车牌号 '{update_data['license_plate']}' 已存在"
                    )
            
            # 4. 如果更新供应商，重新获取供应商信息
            if 'supplier_id' in update_data:
                supplier_info = self._get_supplier_info(update_data['supplier_id'])
                update_data['supplier_category'] = supplier_info.get('category')
            
            # 5. 重新计算运力评分
            if any(key in update_data for key in [
                'vehicle_type', 'load_capacity', 'vehicle_age', 'maintenance_status'
            ]):
                merged_data = {**vehicle.to_dict(), **update_data}
                update_data['capacity_score'] = self._calculate_capacity_score(merged_data)
            
            # 6. 更新时间戳
            update_data['updated_at'] = datetime.utcnow()
            
            # 7. 更新数据库
            updated_vehicle = self.repository.update(vehicle_id, update_data)
            
            logger.info(f"成功更新车辆: {vehicle_id}")
            return updated_vehicle
            
        except Exception as e:
            logger.error(f"更新车辆失败: {str(e)}")
            raise
    
    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        """
        根据ID获取车辆信息
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            车辆对象，如果不存在则返回None
        """
        return self.repository.get_by_id(vehicle_id)
    
    def search_vehicles(
        self,
        license_plate: Optional[str] = None,
        supplier_category: Optional[str] = None,
        min_capacity_score: Optional[float] = None,
        max_capacity_score: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Vehicle]:
        """
        搜索车辆
        
        Args:
            license_plate: 车牌号（模糊搜索）
            supplier_category: 供应商分类
            min_capacity_score: 最小运力评分
            max_capacity_score: 最大运力评分
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            车辆列表
        """
        # 标准化搜索条件
        search_params = {}
        
        if license_plate:
            search_params['normalized_license_plate'] = self._normalize_license_plate(
                license_plate
            )
        
        if supplier_category:
            search_params['supplier_category'] = supplier_category
        
        if min_capacity_score is not None:
            search_params['min_capacity_score'] = min_capacity_score
        
        if max_capacity_score is not None:
            search_params['max_capacity_score'] = max_capacity_score
        
        return self.repository.search(
            **search_params,
            limit=limit,
            offset=offset
        )
    
    def _validate_vehicle_data(self, data: Dict[str, Any], is_update: bool = False) -> None:
        """
        验证车辆数据
        
        Args:
            data: 车辆数据
            is_update: 是否为更新操作
            
        Raises:
            VehicleValidationError: 验证失败
        """
        required_fields = ['license_plate', 'vehicle_type', 'supplier_id']
        
        if not is_update:
            # 创建时必须包含所有必填字段
            for field in required_fields:
                if field not in data or not data[field]:
                    raise VehicleValidationError(f"缺少必填字段: {field}")
        
        # 验证车牌号格式
        if 'license_plate' in data and data['license_plate']:
            if not self.license_plate_validator.is_valid(data['license_plate']):
                raise VehicleValidationError("车牌号格式不正确")
        
        # 验证车辆类型
        if 'vehicle_type' in data and data['vehicle_type']:
            valid_types = ['truck', 'van', 'pickup', 'container']
            if data['vehicle_type'] not in valid_types:
                raise VehicleValidationError(f"无效的车辆类型: {data['vehicle_type']}")
        
        # 验证载重
        if 'load_capacity' in data and data['load_capacity'] is not None:
            if data['load_capacity'] <= 0:
                raise VehicleValidationError("载重必须大于0")
        
        # 验证车龄
        if 'vehicle_age' in data and data['vehicle_age'] is not None:
            if data['vehicle_age'] < 0:
                raise VehicleValidationError("车龄不能为负数")
    
    def _normalize_license_plate(self, license_plate: str) -> str:
        """
        标准化车牌号
        
        Args:
            license_plate: 原始车牌号
            
        Returns:
            标准化后的车牌号
        """
        if not license_plate:
            return ""
        
        # 去除空格和特殊字符，转为大写
        normalized = re.sub(r'[^\w]', '', str(license_plate)).upper()
        
        # 验证标准化后的格式
        if not self.license_plate_validator.is_valid(normalized):
            raise VehicleValidationError(f"无效的车牌号格式: {license_plate}")
        
        return normalized
    
    def _get_supplier_info(self, supplier_id: int) -> Dict[str, Any]:
        """
        获取供应商信息
        
        Args:
            supplier_id: 供应商ID
            
        Returns:
            供应商信息字典
            
        Raises:
            ExternalServiceError: 外部服务调用失败
        """
        try:
            return self.supplier_client.get_supplier_info(supplier_id)
        except Exception as e:
            logger.error(f"获取供应商信息失败: {str(e)}")
            # 返回默认值，避免外部服务故障影响主流程
            return {'category': 'unknown'}
    
    def _calculate_capacity_score(self, vehicle_data: Dict[str, Any]) -> float:
        """
        计算运力评分
        
        Args:
            vehicle_data: 车辆数据
            
        Returns:
            运力评分 (0-100)
        """
        score = 50.0  # 基础分
        
        # 根据车辆类型加分
        vehicle_type_scores = {
            'truck': 20,
            'van': 15,
            'pickup': 10,
            'container': 25
        }
        score += vehicle_type_scores.get(vehicle_data.get('vehicle_type'), 0)
        
        # 根据载重能力加分
        load_capacity = vehicle_data.get('load_capacity', 0)
        if load_capacity > 10000:
            score += 15
        elif load_capacity > 5000:
            score += 10
        elif load_capacity > 2000:
            score += 5
        
        # 根据车龄减分
        vehicle_age = vehicle_data.get('vehicle_age', 0)
        if vehicle_age > 10:
            score -= 20
        elif vehicle_age > 5:
            score -= 10
        elif vehicle_age > 3:
            score -= 5
        
        # 根据维护状态加分
        maintenance_status = vehicle_data.get('maintenance_status', 'unknown')
        maintenance_scores = {
            'excellent': 10,
            'good': 5,
            'fair': 0,
            'poor': -10
        }
        score += maintenance_scores.get(maintenance_status, 0)
        
        # 限制在0-100范围内
        return max(0, min(100, score))