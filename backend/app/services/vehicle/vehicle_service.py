from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
from app.models.vehicle.vehicle_volume_history import VehicleVolumeHistory
from app.models.user import User
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class VehicleService:
    """
    车辆服务类，处理车辆相关的业务逻辑
    """
    
    @staticmethod
    def get_vehicle_list(page: int = 1, per_page: int = 10, query: str = None) -> Tuple[List[Dict], int]:
        """
        获取车辆列表
        
        Args:
            page: 页码
            per_page: 每页数量
            query: 搜索关键词
            
        Returns:
            Tuple[List[Dict], int]: 车辆列表和总数
        """
        try:
            query_obj = Vehicle.query
            
            # 如果有搜索关键词，添加过滤条件
            if query:
                query_obj = query_obj.filter(
                    db.or_(
                        Vehicle.license_plate.ilike(f'%{query}%'),
                        Vehicle.carriage_number.ilike(f'%{query}%')
                    )
                )
            
            # 分页
            pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
            vehicles = pagination.items
            total = pagination.total
            
            # 转换为字典列表
            vehicle_list = [vehicle.to_dict() for vehicle in vehicles]
            
            return vehicle_list, total
        except SQLAlchemyError as e:
            logger.error(f"获取车辆列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Dict]:
        """
        根据ID获取车辆信息
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            Optional[Dict]: 车辆信息字典，如果不存在则返回None
        """
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return None
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def create_vehicle(vehicle_data: Dict) -> Dict:
        """
        创建新车辆
        
        Args:
            vehicle_data: 车辆数据
            
        Returns:
            Dict: 创建的车辆信息
        """
        try:
            vehicle = Vehicle(
                task_id=vehicle_data.get('task_id'),
                manifest_number=vehicle_data.get('manifest_number'),
                dispatch_number=vehicle_data.get('dispatch_number'),
                license_plate=vehicle_data.get('license_plate'),
                carriage_number=vehicle_data.get('carriage_number'),
                created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                notes=vehicle_data.get('notes'),
                actual_volume=vehicle_data.get('actual_volume'),
                volume_photo_url=vehicle_data.get('volume_photo_url'),
                volume_modified_by=vehicle_data.get('volume_modified_by'),
                required_volume=vehicle_data.get('required_volume'),
                confirmed_volume=vehicle_data.get('confirmed_volume')
            )
            
            db.session.add(vehicle)
            db.session.commit()
            
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def update_vehicle(vehicle_id: int, vehicle_data: Dict) -> Optional[Dict]:
        """
        更新车辆信息
        
        Args:
            vehicle_id: 车辆ID
            vehicle_data: 车辆数据
            
        Returns:
            Optional[Dict]: 更新后的车辆信息，如果不存在则返回None
        """
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return None
            
            # 更新车辆信息
            for key, value in vehicle_data.items():
                if hasattr(vehicle, key) and key != 'id':
                    setattr(vehicle, key, value)
            
            db.session.commit()
            
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_vehicle(vehicle_id: int) -> bool:
        """
        删除车辆
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return False
            
            db.session.delete(vehicle)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def update_vehicle_volume(volume_data: Dict) -> Dict:
        """
        更新车辆容积
        
        Args:
            volume_data: 容积更新数据
                - vehicle_id: 车辆ID
                - original_volume: 原始容积
                - new_volume: 新容积
                - reason: 修改原因
                - modified_by: 修改人ID
                - volume_photo_url: 容积照片URL
                - approval_doc_url: 审批凭证URL
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 获取车辆信息
            vehicle = Vehicle.query.get(volume_data.get('vehicle_id'))
            if not vehicle:
                raise ValueError(f"车辆不存在: ID={volume_data.get('vehicle_id')}")
            
            # 验证容积范围
            original_volume = vehicle.actual_volume
            new_volume = volume_data.get('new_volume')
            
            # 容积范围验证：允许在原容积的80%~120%之间
            min_volume = original_volume * 0.8
            max_volume = original_volume * 1.2
            
            if new_volume < min_volume or new_volume > max_volume:
                raise ValueError(f"新容积超出允许范围: {min_volume:.2f} ~ {max_volume:.2f}")
            
            # 创建容积更新历史记录
            history = VehicleVolumeHistory(
                vehicle_id=vehicle.id,
                original_volume=original_volume,
                new_volume=new_volume,
                reason=volume_data.get('reason'),
                modified_by=volume_data.get('modified_by'),
                modified_at=datetime.now(),
                volume_photo_url=volume_data.get('volume_photo_url'),
                approval_doc_url=volume_data.get('approval_doc_url')
            )
            
            # 更新车辆容积
            vehicle.actual_volume = new_volume
            vehicle.volume_photo_url = volume_data.get('volume_photo_url')
            vehicle.volume_modified_by = volume_data.get('modified_by')
            
            db.session.add(history)
            db.session.commit()
            
            # 获取修改人信息
            user = User.query.get(volume_data.get('modified_by'))
            username = user.username if user else "未知用户"
            
            return {
                'success': True,
                'message': '车辆容积更新成功',
                'vehicle': vehicle.to_dict(),
                'history': history.to_dict(),
                'modifier': username
            }
        except ValueError as e:
            db.session.rollback()
            logger.error(f"更新车辆容积失败: {str(e)}")
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新车辆容积失败: {str(e)}")
            raise
    
    @staticmethod
    def get_volume_update_history(vehicle_id: int, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        获取车辆容积更新历史
        
        Args:
            vehicle_id: 车辆ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            Tuple[List[Dict], int]: 容积更新历史列表和总数
        """
        try:
            query_obj = VehicleVolumeHistory.query.filter_by(vehicle_id=vehicle_id)
            
            # 分页
            pagination = query_obj.order_by(VehicleVolumeHistory.modified_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            history_records = pagination.items
            total = pagination.total
            
            # 转换为字典列表
            history_list = [record.to_dict() for record in history_records]
            
            return history_list, total
        except SQLAlchemyError as e:
            logger.error(f"获取容积更新历史失败: {str(e)}")
            raise
    
    @staticmethod
    def get_vehicle_conversion_factors() -> List[Dict]:
        """
        获取车型折算系数表
        
        Returns:
            List[Dict]: 车型折算系数表
        """
        # 车型折算系数表
        conversion_factors = [
            {'type': '5吨', 'volume': 35, 'factor': 0.45},
            {'type': '8吨', 'volume': 45, 'factor': 0.51},
            {'type': '12吨', 'volume': 55, 'factor': 0.63},
            {'type': '20吨', 'volume': 100, 'factor': 0.83},
            {'type': '30吨', 'volume': 130, 'factor': 1.00},
            {'type': '40吨A', 'volume': 150, 'factor': 1.12},
            {'type': '40吨B', 'volume': 180, 'factor': 1.23}
        ]
        
        return conversion_factors