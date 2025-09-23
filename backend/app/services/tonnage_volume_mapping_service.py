"""
车辆吨位-容积映射服务层
处理吨位-容积映射相关业务逻辑
"""

from typing import List, Dict, Any, Optional
from ..repositories.tonnage_volume_mapping_repository import TonnageVolumeMappingRepository
from ..utils.tonnage_formatter import TonnageFormatter
from ..utils.exceptions import ValidationError, ResourceNotFoundError


class TonnageVolumeMappingService:
    """车辆吨位-容积映射业务服务类"""
    
    def __init__(self):
        self.repository = TonnageVolumeMappingRepository()
    
    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """
        获取所有吨位-容积映射关系
        
        Returns:
            List[Dict[str, Any]]: 所有映射关系的字典列表
        """
        mappings = self.repository.find_all()
        return [mapping.to_dict() for mapping in mappings]
    
    def get_active_mappings(self) -> Dict[str, float]:
        """
        获取所有启用的吨位-容积映射关系
        
        Returns:
            Dict[str, float]: 吨位到标准容积的映射字典
        """
        return self.repository.get_tonnage_volume_dict()
    
    def get_mapping_by_id(self, mapping_id: int) -> Dict[str, Any]:
        """
        根据ID获取单个吨位-容积映射关系
        
        Args:
            mapping_id: 映射关系ID
            
        Returns:
            Dict[str, Any]: 映射关系信息
            
        Raises:
            ResourceNotFoundError: 映射关系不存在时抛出
        """
        mapping = self.repository.find_by_id(mapping_id)
        if not mapping:
            raise ResourceNotFoundError(f"映射关系ID {mapping_id} 不存在")
        return mapping.to_dict()
    
    def create_mapping(self, mapping_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新的吨位-容积映射关系
        
        Args:
            mapping_data: 映射数据
            
        Returns:
            Dict[str, Any]: 创建的映射关系信息
            
        Raises:
            ValidationError: 数据验证失败时抛出
        """
        # 验证必填字段
        self._validate_required_fields(mapping_data)
        
        # 格式化吨位字段
        if 'tonnage' in mapping_data:
            mapping_data['tonnage'] = TonnageFormatter.format_tonnage(mapping_data['tonnage'])
        
        # 验证业务规则
        self._validate_mapping_data(mapping_data)
        
        # 检查吨位是否已存在
        if self.repository.exists_by_tonnage(mapping_data['tonnage']):
            raise ValidationError(f"吨位 {mapping_data['tonnage']} 已存在")
        
        # 创建映射记录
        mapping = self.repository.create(mapping_data)
        return mapping.to_dict()
    
    def update_mapping(self, mapping_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新吨位-容积映射关系
        
        Args:
            mapping_id: 映射关系ID
            update_data: 更新数据
            
        Returns:
            Dict[str, Any]: 更新后的映射关系信息
            
        Raises:
            ResourceNotFoundError: 映射关系不存在时抛出
            ValidationError: 数据验证失败时抛出
        """
        # 查找映射记录
        mapping = self.repository.find_by_id(mapping_id)
        if not mapping:
            raise ResourceNotFoundError(f"映射关系ID {mapping_id} 不存在")
        
        # 格式化吨位字段
        if 'tonnage' in update_data:
            update_data['tonnage'] = TonnageFormatter.format_tonnage(update_data['tonnage'])
            
            # 检查新吨位是否与其他记录冲突
            if self.repository.exists_by_tonnage(update_data['tonnage'], exclude_id=mapping_id):
                raise ValidationError(f"吨位 {update_data['tonnage']} 已存在")
        
        # 验证更新数据
        self._validate_update_data(update_data)
        
        # 更新映射记录
        updated_mapping = self.repository.update(mapping, update_data)
        return updated_mapping.to_dict()
    
    def delete_mapping(self, mapping_id: int) -> bool:
        """
        删除吨位-容积映射关系
        
        Args:
            mapping_id: 映射关系ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            ResourceNotFoundError: 映射关系不存在时抛出
        """
        mapping = self.repository.find_by_id(mapping_id)
        if not mapping:
            raise ResourceNotFoundError(f"映射关系ID {mapping_id} 不存在")
        
        return self.repository.delete(mapping)
    
    def get_volume_by_tonnage(self, tonnage: str) -> Dict[str, Any]:
        """
        根据吨位获取对应的容积信息
        
        Args:
            tonnage: 标准吨位
            
        Returns:
            Dict[str, Any]: 容积信息
            
        Raises:
            ResourceNotFoundError: 未找到对应吨位时抛出
        """
        # 格式化吨位参数
        formatted_tonnage = TonnageFormatter.format_tonnage(tonnage)
        
        # 查找映射记录
        mapping = self.repository.find_by_tonnage(formatted_tonnage)
        if not mapping:
            raise ResourceNotFoundError(f"未找到吨位 {formatted_tonnage} 对应的容积信息")
        
        return {
            'tonnage': mapping.tonnage,
            'standard_volume': mapping.standard_volume,
            'min_volume': mapping.min_volume,
            'max_volume': mapping.max_volume,
            'vehicle_grade': mapping.vehicle_grade,
            'description': mapping.description if hasattr(mapping, 'description') else None
        }
    
    def get_tonnage_by_volume(self, volume: float) -> Dict[str, str]:
        """
        根据容积获取对应的吨位档位
        
        Args:
            volume: 容积值
            
        Returns:
            Dict[str, str]: 吨位档位信息
            
        Raises:
            ValidationError: 容积值无效时抛出
            ResourceNotFoundError: 未找到对应吨位档位时抛出
        """
        # 验证容积值
        if volume <= 0:
            raise ValidationError("容积值必须大于0")
        
        # 查找匹配的映射记录
        mapping = self.repository.find_by_volume_range(volume)
        if not mapping:
            raise ResourceNotFoundError(f"未找到容积 {volume}m³ 对应的吨位档位")
        
        return {'tonnage': mapping.tonnage}
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        验证必填字段
        
        Args:
            data: 数据字典
            
        Raises:
            ValidationError: 缺少必填字段时抛出
        """
        required_fields = ['tonnage', 'min_volume', 'standard_volume', 'conversion_factor', 'vehicle_grade']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"缺少必填字段: {field}")
    
    def _validate_mapping_data(self, data: Dict[str, Any]) -> None:
        """
        验证映射数据的业务规则
        
        Args:
            data: 映射数据
            
        Raises:
            ValidationError: 数据验证失败时抛出
        """
        # 验证吨位格式
        if not TonnageFormatter.validate_tonnage_format(data['tonnage']):
            raise ValidationError(f"无效的吨位格式: {data['tonnage']}")
        
        # 验证容积值
        if data['min_volume'] <= 0:
            raise ValidationError("最小容积必须大于0")
        
        if data['standard_volume'] <= 0:
            raise ValidationError("标准容积必须大于0")
        
        if data['min_volume'] > data['standard_volume']:
            raise ValidationError("最小容积不能大于标准容积")
        
        # 验证最大容积（如果提供）
        if 'max_volume' in data and data['max_volume'] is not None:
            if data['max_volume'] <= 0:
                raise ValidationError("最大容积必须大于0")
            if data['max_volume'] < data['standard_volume']:
                raise ValidationError("最大容积不能小于标准容积")
        
        # 验证转换系数
        if data['conversion_factor'] <= 0:
            raise ValidationError("容积折算系数必须大于0")
    
    def _validate_update_data(self, data: Dict[str, Any]) -> None:
        """
        验证更新数据
        
        Args:
            data: 更新数据
            
        Raises:
            ValidationError: 数据验证失败时抛出
        """
        # 验证吨位格式（如果提供）
        if 'tonnage' in data and not TonnageFormatter.validate_tonnage_format(data['tonnage']):
            raise ValidationError(f"无效的吨位格式: {data['tonnage']}")
        
        # 验证容积值（如果提供）
        if 'min_volume' in data and data['min_volume'] <= 0:
            raise ValidationError("最小容积必须大于0")
        
        if 'standard_volume' in data and data['standard_volume'] <= 0:
            raise ValidationError("标准容积必须大于0")
        
        if 'max_volume' in data and data['max_volume'] is not None and data['max_volume'] <= 0:
            raise ValidationError("最大容积必须大于0")
        
        # 验证转换系数（如果提供）
        if 'conversion_factor' in data and data['conversion_factor'] <= 0:
            raise ValidationError("容积折算系数必须大于0")