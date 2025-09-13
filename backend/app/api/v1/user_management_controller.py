#!/usr/bin/env python3
"""
用户管理控制器模块
处理用户管理相关的API请求
"""

from flask import request, jsonify
from app.services.user_management_service import UserManagementService
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserManagementController:
    """
    用户管理控制器类，处理用户管理相关的API请求
    """
    
    @staticmethod
    @permission_required('user:read')
    def get_user_list():
        """
        获取用户列表
        ---
        tags:
          - 用户管理
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
            description: 页码
          - name: per_page
            in: query
            type: integer
            default: 10
            description: 每页数量
          - name: query
            in: query
            type: string
            description: 搜索关键词
        responses:
          200:
            description: 成功获取用户列表
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            query = request.args.get('query', '')
            
            # 调用服务层获取用户列表
            users, total = UserManagementService.get_user_list(page, per_page, query)
            
            # 返回成功响应
            return success_response({
                'items': users,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('user:read')
    def get_user_detail(user_id: int):
        """
        获取用户详情
        ---
        tags:
          - 用户管理
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: 用户ID
        responses:
          200:
            description: 成功获取用户详情
          404:
            description: 用户不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取用户详情
            user = UserManagementService.get_user_by_id(user_id)
            
            if not user:
                return error_response("用户不存在", 404)
            
            # 返回成功响应
            return success_response(user)
        except Exception as e:
            logger.error(f"获取用户详情失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('user:create')
    def create_user():
        """
        创建用户
        ---
        tags:
          - 用户管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: 用户名
                password:
                  type: string
                  description: 密码
                full_name:
                  type: string
                  description: 姓名
                email:
                  type: string
                  description: 邮箱
                phone:
                  type: string
                  description: 手机号
                dispatch_unit_id:
                  type: integer
                  description: 派车单位ID
                role_ids:
                  type: array
                  items:
                    type: integer
                  description: 角色ID列表
        responses:
          200:
            description: 成功创建用户
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证必填字段
            required_fields = ['username', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return error_response(f"缺少必填字段: {field}", 400)
            
            # 调用服务层创建用户
            user = UserManagementService.create_user(data)
            
            # 返回成功响应
            return success_response(user, "用户创建成功")
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('user:update')
    def update_user(user_id: int):
        """
        更新用户信息
        ---
        tags:
          - 用户管理
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: 用户ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: 用户名
                password:
                  type: string
                  description: 密码
                full_name:
                  type: string
                  description: 姓名
                email:
                  type: string
                  description: 邮箱
                phone:
                  type: string
                  description: 手机号
                dispatch_unit_id:
                  type: integer
                  description: 派车单位ID
                role_ids:
                  type: array
                  items:
                    type: integer
                  description: 角色ID列表
                is_active:
                  type: boolean
                  description: 是否激活
        responses:
          200:
            description: 成功更新用户信息
          404:
            description: 用户不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 调用服务层更新用户信息
            user = UserManagementService.update_user(user_id, data)
            
            if not user:
                return error_response("用户不存在", 404)
            
            # 返回成功响应
            return success_response(user, "用户信息更新成功")
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('user:delete')
    def delete_user(user_id: int):
        """
        删除用户
        ---
        tags:
          - 用户管理
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: 用户ID
        responses:
          200:
            description: 成功删除用户
          404:
            description: 用户不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层删除用户
            result = UserManagementService.delete_user(user_id)
            
            if not result:
                return error_response("用户不存在", 404)
            
            # 返回成功响应
            return success_response(None, "用户删除成功")
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('user:update')
    def bind_user_to_dispatch_unit(user_id: int):
        """
        绑定用户到派车单位
        ---
        tags:
          - 用户管理
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: 用户ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                dispatch_unit_id:
                  type: integer
                  description: 派车单位ID
        responses:
          200:
            description: 成功绑定用户到派车单位
          400:
            description: 参数错误
          404:
            description: 用户不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证必填字段
            if 'dispatch_unit_id' not in data:
                return error_response("缺少必填字段: dispatch_unit_id", 400)
            
            # 调用服务层绑定用户到派车单位
            user = UserManagementService.bind_user_to_dispatch_unit(user_id, data['dispatch_unit_id'])
            
            if not user:
                return error_response("用户不存在", 404)
            
            # 返回成功响应
            return success_response(user, "用户绑定派车单位成功")
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"绑定用户到派车单位失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('user:read')
    def get_users_by_dispatch_unit(dispatch_unit_id: int):
        """
        根据派车单位ID获取用户列表
        ---
        tags:
          - 用户管理
        parameters:
          - name: dispatch_unit_id
            in: path
            type: integer
            required: true
            description: 派车单位ID
        responses:
          200:
            description: 成功获取用户列表
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取用户列表
            users = UserManagementService.get_users_by_dispatch_unit(dispatch_unit_id)
            
            # 返回成功响应
            return success_response(users)
        except Exception as e:
            logger.error(f"根据派车单位获取用户列表失败: {str(e)}")
            return error_response(str(e), 500)