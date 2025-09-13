#!/usr/bin/env python3
"""
派车单位服务模块
处理派车单位相关的业务逻辑
"""

from app.models.company import DispatchUnit
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class DispatchUnitService:
    """
    派车单位服务类，处理派车单位相关的业务逻辑
    """
    
    @staticmethod
    def get_dispatch_unit_list(page: int = 1, per_page: int = 10, query: str = None) -> Tuple[List[Dict], int]:
        """
        获取派车单位列表
        
        Args:
            page: 页码
            per_page: 每页数量
            query: 搜索关键词
            
        Returns:
            Tuple[List[Dict], int]: 派车单位列表和总数
        """
        try:
            query_obj = DispatchUnit.query
            
            # 如果有搜索关键词，添加过滤条件
            if query:
                query_obj = query_obj.filter(
                    db.or_(
                        DispatchUnit.name.ilike(f'%{query}%'),
                        DispatchUnit.contact_person.ilike(f'%{query}%')
                    )
                )
            
            # 分页
            pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
            units = pagination.items
            total = pagination.total
            
            # 转换为字典列表
            unit_list = [unit.to_dict() for unit in units]
            
            return unit_list, total
        except SQLAlchemyError as e:
            logger.error(f"获取派车单位列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_dispatch_unit_by_id(unit_id: int) -> Optional[Dict]:
        """
        根据ID获取派车单位信息
        
        Args:
            unit_id: 派车单位ID
            
        Returns:
            Optional[Dict]: 派车单位信息字典，如果不存在则返回None
        """
        try:
            unit = DispatchUnit.query.get(unit_id)
            if not unit:
                return None
            return unit.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取派车单位信息失败: {str(e)}")
            raise
    
    @staticmethod
    def create_dispatch_unit(unit_data: Dict) -> Dict:
        """
        创建新派车单位
        
        Args:
            unit_data: 派车单位数据
            
        Returns:
            Dict: 创建的派车单位信息
        """
        try:
            unit = DispatchUnit(
                name=unit_data.get('name'),
                unit_type=unit_data.get('unit_type'),
                bank_name=unit_data.get('bank_name'),
                account_number=unit_data.get('account_number'),
                address=unit_data.get('address'),
                contact_person=unit_data.get('contact_person'),
                contact_phone=unit_data.get('contact_phone'),
                email=unit_data.get('email'),
                is_active=unit_data.get('is_active', True)
            )
            
            db.session.add(unit)
            db.session.commit()
            
            return unit.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建派车单位失败: {str(e)}")
            raise
    
    @staticmethod
    def update_dispatch_unit(unit_id: int, unit_data: Dict) -> Optional[Dict]:
        """
        更新派车单位信息
        
        Args:
            unit_id: 派车单位ID
            unit_data: 派车单位数据
            
        Returns:
            Optional[Dict]: 更新后的派车单位信息，如果不存在则返回None
        """
        try:
            unit = DispatchUnit.query.get(unit_id)
            if not unit:
                return None
            
            # 更新派车单位信息
            for key, value in unit_data.items():
                # 避免直接更新created_at和updated_at，它们由数据库自动管理
                if hasattr(unit, key) and key != 'id' and key not in ['created_at', 'updated_at']:
                    setattr(unit, key, value)
            
            db.session.commit()
            
            return unit.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新派车单位信息失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_dispatch_unit(unit_id: int) -> bool:
        """
        删除派车单位
        
        Args:
            unit_id: 派车单位ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            unit = DispatchUnit.query.get(unit_id)
            if not unit:
                return False
            
            db.session.delete(unit)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除派车单位失败: {str(e)}")
            raise
    
    @staticmethod
    def get_active_dispatch_units() -> List[Dict]:
        """
        获取所有激活的派车单位
        
        Returns:
            List[Dict]: 激活的派车单位列表
        """
        try:
            units = DispatchUnit.query.filter_by(is_active=True).all()
            return [unit.to_dict() for unit in units]
        except SQLAlchemyError as e:
            logger.error(f"获取激活派车单位列表失败: {str(e)}")
            raise