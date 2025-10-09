# -*- coding: utf-8 -*-
"""
车辆合并记录服务层
负责处理车辆合并记录的数据库操作
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.vehicle.vehicle_merge_record import VehicleMergeRecord
from app.models.vehicle.vehicle import Vehicle

logger = logging.getLogger(__name__)


class VehicleMergeService:
    """车辆合并记录服务类"""
    
    @staticmethod
    def create_merge_record(record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建合并记录
        
        Args:
            record_data: 合并记录数据
            
        Returns:
            Dict: 创建的记录信息，失败返回None
        """
        try:
            # 创建合并记录对象
            merge_record = VehicleMergeRecord(
                source_task_id=record_data.get('source_task_id'),
                source_dispatch_number=record_data.get('source_dispatch_number'),  # 添加源派车单号
                target_dispatch_number=record_data.get('target_dispatch_number'),  # 添加目标派车单号
                source_vehicle_id=record_data.get('source_vehicle_id'),
                operation_time=record_data.get('operation_time', datetime.now()),
                operator_id=record_data.get('operator_id'),
                operator_name=record_data.get('operator_name'),
                operator_role=record_data.get('operator_role'),
                original_volume=record_data.get('original_volume'),
                merged_volume=record_data.get('merged_volume'),
                merge_reason=record_data.get('merge_reason'),
                merge_status=record_data.get('merge_status', 'completed'),
                # 新增车辆信息字段映射
                new_vehicle_license_plate=record_data.get('new_vehicle_license_plate'),
                new_vehicle_tonnage=record_data.get('new_vehicle_tonnage'),
                new_vehicle_volume=record_data.get('new_vehicle_volume'),
                new_vehicle_type=record_data.get('new_vehicle_type'),
                new_vehicle_carriage_number=record_data.get('new_vehicle_carriage_number'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            db.session.add(merge_record)
            db.session.flush()  # 立即刷新以检测约束错误
            
            return merge_record.to_dict()
            
        except SQLAlchemyError as e:
            logger.error(f"创建合并记录失败: {str(e)}")
            db.session.rollback()
            return None
        except Exception as e:
            logger.error(f"创建合并记录异常: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_merge_records_by_source_task(task_id: str) -> List[Dict[str, Any]]:
        """
        根据源任务ID获取合并记录
        
        Args:
            task_id: 源任务ID
            
        Returns:
            List[Dict]: 合并记录列表
        """
        try:
            records = VehicleMergeRecord.query.filter_by(
                source_task_id=task_id
            ).order_by(VehicleMergeRecord.operation_time.desc()).all()
            
            return [record.to_dict() for record in records]
            
        except Exception as e:
            logger.error(f"获取源任务合并记录失败: {str(e)}")
            return []
    
    @staticmethod
    def get_merge_records_by_target_task(task_id: str) -> List[Dict[str, Any]]:
        """
        根据目标派车单号获取合并记录
        
        Args:
            task_id: 任务ID（已废弃，此方法现在返回空列表）
            
        Returns:
            List[Dict]: 合并记录列表（空列表）
        """
        try:
            # 由于已删除target_task_id字段，此方法现在返回空列表
            return []
            
        except Exception as e:
            logger.error(f"获取目标任务合并记录失败: {str(e)}")
            return []
    
    @staticmethod
    def get_merge_records_by_task(task_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        根据任务ID获取所有相关的合并记录（作为源任务和目标任务）
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 包含源任务和目标任务合并记录的字典
        """
        try:
            source_records = VehicleMergeService.get_merge_records_by_source_task(task_id)
            target_records = VehicleMergeService.get_merge_records_by_target_task(task_id)
            
            return {
                'source_records': source_records,
                'target_records': target_records,
                'has_records': len(source_records) > 0 or len(target_records) > 0
            }
            
        except Exception as e:
            logger.error(f"获取任务合并记录失败: {str(e)}")
            return {
                'source_records': [],
                'target_records': [],
                'has_records': False
            }
    
    @staticmethod
    def get_merge_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据记录ID获取合并记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Dict: 合并记录信息，不存在返回None
        """
        try:
            record = VehicleMergeRecord.query.get(record_id)
            return record.to_dict() if record else None
            
        except Exception as e:
            logger.error(f"获取合并记录失败: {str(e)}")
            return None
    
    @staticmethod
    def update_merge_record(record_id: int, update_data: Dict[str, Any]) -> bool:
        """
        更新合并记录
        
        Args:
            record_id: 记录ID
            update_data: 更新数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            record = VehicleMergeRecord.query.get(record_id)
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
            logger.error(f"更新合并记录失败: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"更新合并记录异常: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def delete_merge_record(record_id: int) -> bool:
        """
        删除合并记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            record = VehicleMergeRecord.query.get(record_id)
            if not record:
                return False
            
            db.session.delete(record)
            db.session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"删除合并记录失败: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"删除合并记录异常: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_vehicles_by_task_ids(task_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        根据任务ID列表获取车辆信息
        
        Args:
            task_ids: 任务ID列表
            
        Returns:
            Dict: 任务ID到车辆信息的映射
        """
        try:
            vehicles = Vehicle.query.filter(Vehicle.task_id.in_(task_ids)).all()
            result = {}
            
            for vehicle in vehicles:
                task_id = str(vehicle.task_id)
                if task_id not in result:
                    result[task_id] = []
                result[task_id].append(vehicle.to_dict())
            
            return result
            
        except Exception as e:
            logger.error(f"获取车辆信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_vehicle_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
        """
        根据任务ID获取最新的车辆信息
        
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