#!/usr/bin/env python3
"""
用户管理服务模块
处理用户管理相关的业务逻辑
"""

from app.models.user import User
from app.models.role import Role
from app.models.company import DispatchUnit
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class UserManagementService:
    """
    用户管理服务类，处理用户管理相关的业务逻辑
    """
    
    @staticmethod
    def get_user_list(page: int = 1, per_page: int = 10, query: str = None) -> Tuple[List[Dict], int]:
        """
        获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
            query: 搜索关键词
            
        Returns:
            Tuple[List[Dict], int]: 用户列表和总数
        """
        try:
            query_obj = User.query
            
            # 如果有搜索关键词，添加过滤条件
            if query:
                query_obj = query_obj.filter(
                    db.or_(
                        User.username.ilike(f'%{query}%'),
                        User.full_name.ilike(f'%{query}%'),
                        User.email.ilike(f'%{query}%')
                    )
                )
            
            # 分页
            pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
            users = pagination.items
            total = pagination.total
            
            # 转换为字典列表
            user_list = [user.to_dict() for user in users]
            
            return user_list, total
        except SQLAlchemyError as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 用户信息字典，如果不存在则返回None
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            return user.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            raise
    
    @staticmethod
    def create_user(user_data: Dict) -> Dict:
        """
        创建新用户
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict: 创建的用户信息
        """
        try:
            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=user_data.get('username')).first()
            if existing_user:
                raise ValueError(f"用户名 '{user_data.get('username')}' 已存在")
            
            user = User(
                username=user_data.get('username'),
                full_name=user_data.get('full_name'),
                email=user_data.get('email'),
                phone=user_data.get('phone'),
                dispatch_unit_id=user_data.get('dispatch_unit_id'),
                is_active=user_data.get('is_active', True)
            )
            
            # 设置密码
            if 'password' in user_data:
                user.set_password(user_data['password'])
            
            db.session.add(user)
            db.session.flush()  # 获取用户ID
            
            # 分配角色
            if 'role_ids' in user_data and user_data['role_ids']:
                roles = Role.query.filter(Role.id.in_(user_data['role_ids'])).all()
                user.roles = roles
            
            db.session.commit()
            
            return user.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建用户失败: {str(e)}")
            raise
    
    @staticmethod
    def update_user(user_id: int, user_data: Dict) -> Optional[Dict]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            
        Returns:
            Optional[Dict]: 更新后的用户信息，如果不存在则返回None
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # 检查用户名是否已被其他用户使用
            if 'username' in user_data and user_data['username'] != user.username:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user:
                    raise ValueError(f"用户名 '{user_data['username']}' 已存在")
            
            # 更新用户信息
            for key, value in user_data.items():
                if key == 'password' and value:
                    user.set_password(value)
                elif key == 'role_ids':
                    # 更新角色
                    if value:
                        roles = Role.query.filter(Role.id.in_(value)).all()
                        user.roles = roles
                    else:
                        user.roles = []
                elif hasattr(user, key) and key not in ['id', 'created_at']:
                    setattr(user, key, value)
            
            db.session.commit()
            
            return user.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新用户信息失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            db.session.delete(user)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除用户失败: {str(e)}")
            raise
    
    @staticmethod
    def bind_user_to_dispatch_unit(user_id: int, dispatch_unit_id: int) -> Optional[Dict]:
        """
        绑定用户到派车单位
        
        Args:
            user_id: 用户ID
            dispatch_unit_id: 派车单位ID
            
        Returns:
            Optional[Dict]: 更新后的用户信息，如果不存在则返回None
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # 验证派车单位是否存在
            dispatch_unit = DispatchUnit.query.get(dispatch_unit_id)
            if not dispatch_unit:
                raise ValueError(f"派车单位不存在: ID={dispatch_unit_id}")
            
            user.dispatch_unit_id = dispatch_unit_id
            db.session.commit()
            
            return user.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"绑定用户到派车单位失败: {str(e)}")
            raise
    
    @staticmethod
    def get_users_by_dispatch_unit(dispatch_unit_id: int) -> List[Dict]:
        """
        根据派车单位ID获取用户列表
        
        Args:
            dispatch_unit_id: 派车单位ID
            
        Returns:
            List[Dict]: 用户列表
        """
        try:
            users = User.query.filter_by(dispatch_unit_id=dispatch_unit_id).all()
            return [user.to_dict() for user in users]
        except SQLAlchemyError as e:
            logger.error(f"根据派车单位获取用户列表失败: {str(e)}")
            raise