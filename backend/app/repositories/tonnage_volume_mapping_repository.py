"""
车辆吨位-容积映射数据访问层
负责数据持久化和查询操作
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from ..models.vehicle_tonnage_volume_mapping import VehicleTonnageVolumeMapping
from ..extensions import db
from ..utils.exceptions import ValidationError, ResourceNotFoundError


class TonnageVolumeMappingRepository:
    """车辆吨位-容积映射数据访问层"""
    
    @staticmethod
    def find_all() -> List[VehicleTonnageVolumeMapping]:
        """
        获取所有吨位-容积映射记录
        
        Returns:
            List[VehicleTonnageVolumeMapping]: 所有映射记录
        """
        return VehicleTonnageVolumeMapping.query.all()
    
    @staticmethod
    def find_active_mappings() -> List[VehicleTonnageVolumeMapping]:
        """
        获取所有启用的吨位-容积映射记录
        
        Returns:
            List[VehicleTonnageVolumeMapping]: 启用的映射记录
        """
        return VehicleTonnageVolumeMapping.query.filter_by(is_active=True).all()
    
    @staticmethod
    def find_by_id(mapping_id: int) -> Optional[VehicleTonnageVolumeMapping]:
        """
        根据ID查找映射记录
        
        Args:
            mapping_id: 映射记录ID
            
        Returns:
            Optional[VehicleTonnageVolumeMapping]: 映射记录或None
        """
        return VehicleTonnageVolumeMapping.query.get(mapping_id)
    
    @staticmethod
    def find_by_tonnage(tonnage: str) -> Optional[VehicleTonnageVolumeMapping]:
        """
        根据吨位查找映射记录
        
        Args:
            tonnage: 标准吨位
            
        Returns:
            Optional[VehicleTonnageVolumeMapping]: 映射记录或None
        """
        return VehicleTonnageVolumeMapping.query.filter_by(tonnage=tonnage).first()
    
    @staticmethod
    def find_by_volume_range(volume: float) -> Optional[VehicleTonnageVolumeMapping]:
        """
        根据容积范围查找对应的吨位档位
        
        Args:
            volume: 容积值
            
        Returns:
            Optional[VehicleTonnageVolumeMapping]: 匹配的映射记录或None
        """
        return VehicleTonnageVolumeMapping.query.filter(
            VehicleTonnageVolumeMapping.min_volume <= volume,
            VehicleTonnageVolumeMapping.max_volume >= volume,
            VehicleTonnageVolumeMapping.is_active == True
        ).first()
    
    @staticmethod
    def create(mapping_data: Dict[str, Any]) -> VehicleTonnageVolumeMapping:
        """
        创建新的吨位-容积映射记录
        
        Args:
            mapping_data: 映射数据
            
        Returns:
            VehicleTonnageVolumeMapping: 创建的映射记录
            
        Raises:
            ValidationError: 数据验证失败或唯一约束冲突
        """
        try:
            mapping = VehicleTonnageVolumeMapping(**mapping_data)
            db.session.add(mapping)
            db.session.commit()
            return mapping
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e) or 'Duplicate entry' in str(e):
                raise ValidationError(f"吨位 {mapping_data.get('tonnage')} 已存在")
            raise ValidationError(f"数据完整性错误: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"创建映射记录失败: {str(e)}")
    
    @staticmethod
    def update(mapping: VehicleTonnageVolumeMapping, update_data: Dict[str, Any]) -> VehicleTonnageVolumeMapping:
        """
        更新吨位-容积映射记录
        
        Args:
            mapping: 要更新的映射记录
            update_data: 更新数据
            
        Returns:
            VehicleTonnageVolumeMapping: 更新后的映射记录
            
        Raises:
            ValidationError: 数据验证失败或唯一约束冲突
        """
        try:
            for key, value in update_data.items():
                if hasattr(mapping, key):
                    setattr(mapping, key, value)
            
            db.session.commit()
            return mapping
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e) or 'Duplicate entry' in str(e):
                raise ValidationError(f"吨位 {update_data.get('tonnage')} 已存在")
            raise ValidationError(f"数据完整性错误: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"更新映射记录失败: {str(e)}")
    
    @staticmethod
    def delete(mapping: VehicleTonnageVolumeMapping) -> bool:
        """
        删除吨位-容积映射记录
        
        Args:
            mapping: 要删除的映射记录
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            ValidationError: 删除失败
        """
        try:
            db.session.delete(mapping)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"删除映射记录失败: {str(e)}")
    
    @staticmethod
    def exists_by_tonnage(tonnage: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查指定吨位是否已存在
        
        Args:
            tonnage: 标准吨位
            exclude_id: 排除的记录ID（用于更新时检查）
            
        Returns:
            bool: 是否存在
        """
        query = VehicleTonnageVolumeMapping.query.filter_by(tonnage=tonnage)
        if exclude_id:
            query = query.filter(VehicleTonnageVolumeMapping.id != exclude_id)
        return query.first() is not None
    
    @staticmethod
    def get_tonnage_volume_dict() -> Dict[str, float]:
        """
        获取吨位-容积映射字典
        
        Returns:
            Dict[str, float]: 吨位到标准容积的映射字典
        """
        mappings = TonnageVolumeMappingRepository.find_active_mappings()
        return {mapping.tonnage: mapping.standard_volume for mapping in mappings}