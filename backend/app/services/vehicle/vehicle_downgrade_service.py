# -*- coding: utf-8 -*-
"""
车辆降档记录服务层
负责处理车辆降档记录的数据库操作
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.vehicle.vehicle_downgrade_record import VehicleDowngradeRecord
from app.models.vehicle.vehicle import Vehicle

logger = logging.getLogger(__name__)


class VehicleDowngradeService:
    """车辆降档记录服务类"""
    
    @staticmethod
    def create_downgrade_record(record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建降档记录
        
        Args:
            record_data: 降档记录数据
            
        Returns:
            Dict: 创建的记录信息，失败返回None
        """
        try:
            # 创建降档记录对象
            downgrade_record = VehicleDowngradeRecord(
                task_id=record_data.get('task_id'),
                vehicle_id=record_data.get('vehicle_id'),
                operation_type=record_data.get('operation_type', 'downgrade'),
                operation_time=record_data.get('operation_time', datetime.now()),
                operator_id=record_data.get('operator_id'),
                operator_name=record_data.get('operator_name'),
                operator_role=record_data.get('operator_role'),
                original_tonnage=record_data.get('original_tonnage'),
                downgraded_tonnage=record_data.get('downgraded_tonnage'),
                operation_reason=record_data.get('operation_reason'),
                dispatch_number=record_data.get('dispatch_number'),  # 添加派车单号字段
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            db.session.add(downgrade_record)
            db.session.flush()  # 立即刷新以检测约束错误
            # 立即提交，避免后续不同事务路径导致记录未写入
            db.session.commit()
            
            return downgrade_record.to_dict()
            
        except SQLAlchemyError as e:
            logger.error(f"创建降档记录失败: {str(e)}")
            db.session.rollback()
            return None
        except Exception as e:
            logger.error(f"创建降档记录异常: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_downgrade_records_by_task(task_id: str) -> List[Dict[str, Any]]:
        """
        根据任务ID获取降档记录
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[Dict]: 降档记录列表
        """
        try:
            records = VehicleDowngradeRecord.query.filter_by(
                task_id=task_id,
                operation_type='downgrade'
            ).order_by(VehicleDowngradeRecord.operation_time.desc()).all()
            
            return [record.to_dict() for record in records]
            
        except Exception as e:
            logger.error(f"获取降档记录失败: {str(e)}")
            return []
    
    @staticmethod
    def get_downgrade_records_by_vehicle(vehicle_id: int) -> List[Dict[str, Any]]:
        """
        根据车辆ID获取降档记录
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            List[Dict]: 降档记录列表
        """
        try:
            records = VehicleDowngradeRecord.query.filter_by(
                vehicle_id=vehicle_id,
                operation_type='downgrade'
            ).order_by(VehicleDowngradeRecord.operation_time.desc()).all()
            
            return [record.to_dict() for record in records]
            
        except Exception as e:
            logger.error(f"获取车辆降档记录失败: {str(e)}")
            return []
    
    @staticmethod
    def get_downgrade_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据记录ID获取降档记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Dict: 降档记录信息，不存在返回None
        """
        try:
            record = VehicleDowngradeRecord.query.get(record_id)
            return record.to_dict() if record else None
            
        except Exception as e:
            logger.error(f"获取降档记录失败: {str(e)}")
            return None
    
    @staticmethod
    def update_downgrade_record(record_id: int, update_data: Dict[str, Any]) -> bool:
        """
        更新降档记录
        
        Args:
            record_id: 记录ID
            update_data: 更新数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            record = VehicleDowngradeRecord.query.get(record_id)
            if not record:
                return False
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            record.updated_at = datetime.now()
            db.session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"更新降档记录失败: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"更新降档记录异常: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def delete_downgrade_record(record_id: int) -> bool:
        """
        删除降档记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            record = VehicleDowngradeRecord.query.get(record_id)
            if not record:
                return False
            
            db.session.delete(record)
            db.session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"删除降档记录失败: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"删除降档记录异常: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_vehicle_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
        """
        根据任务ID获取车辆信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 车辆信息，不存在返回None
        """
        try:
            vehicle = Vehicle.query.filter_by(task_id=task_id).order_by(Vehicle.created_at.desc()).first()
            return vehicle.to_dict() if vehicle else None
            
        except Exception as e:
            logger.error(f"获取车辆信息失败: {str(e)}")
            return None