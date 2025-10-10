#!/usr/bin/env python3
"""
派车单位控制器模块
处理派车单位相关的API请求
"""

from flask import request, jsonify
from app.services.dispatch_unit_service import DispatchUnitService
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DispatchUnitController:
    """
    派车单位控制器类，处理派车单位相关的API请求
    """
    
    @staticmethod
    @permission_required('dispatch_unit:read')
    def get_dispatch_unit_list():
        """
        获取派车单位列表
        ---
        tags:
          - 派车单位管理
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
            description: 成功获取派车单位列表
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
            
            # 调用服务层获取派车单位列表
            units, total = DispatchUnitService.get_dispatch_unit_list(page, per_page, query)
            
            # 返回成功响应
            return success_response({
                'items': units,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        except Exception as e:
            logger.error(f"获取派车单位列表失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch_unit:read')
    def get_dispatch_unit_detail(unit_id: int):
        """
        获取派车单位详情
        ---
        tags:
          - 派车单位管理
        parameters:
          - name: unit_id
            in: path
            type: integer
            required: true
            description: 派车单位ID
        responses:
          200:
            description: 成功获取派车单位详情
          404:
            description: 派车单位不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取派车单位详情
            unit = DispatchUnitService.get_dispatch_unit_by_id(unit_id)
            
            if not unit:
                return error_response("派车单位不存在", 404)
            
            # 返回成功响应
            return success_response(unit)
        except Exception as e:
            logger.error(f"获取派车单位详情失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch_unit:create')
    def create_dispatch_unit():
        """
        创建派车单位
        ---
        tags:
          - 派车单位管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: 派车单位名称
                unit_type:
                  type: string
                  description: 单位类型
                bank_name:
                  type: string
                  description: 银行名称
                account_number:
                  type: string
                  description: 银行账号
                address:
                  type: string
                  description: 单位地址
                contact_person:
                  type: string
                  description: 联系人
                contact_phone:
                  type: string
                  description: 联系电话
                email:
                  type: string
                  description: 邮箱
        responses:
          200:
            description: 成功创建派车单位
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证必填字段
            required_fields = ['name']
            for field in required_fields:
                if field not in data or not data[field]:
                    return error_response(f"缺少必填字段: {field}", 400)
            
            # 调用服务层创建派车单位
            unit = DispatchUnitService.create_dispatch_unit(data)
            
            # 返回成功响应
            return success_response(unit, "派车单位创建成功")
        except Exception as e:
            logger.error(f"创建派车单位失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch_unit:update')
    def update_dispatch_unit(unit_id: int):
        """
        更新派车单位信息
        ---
        tags:
          - 派车单位管理
        parameters:
          - name: unit_id
            in: path
            type: integer
            required: true
            description: 派车单位ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: 派车单位名称
                unit_type:
                  type: string
                  description: 单位类型
                bank_name:
                  type: string
                  description: 银行名称
                account_number:
                  type: string
                  description: 银行账号
                address:
                  type: string
                  description: 单位地址
                contact_person:
                  type: string
                  description: 联系人
                contact_phone:
                  type: string
                  description: 联系电话
                email:
                  type: string
                  description: 邮箱
                is_active:
                  type: boolean
                  description: 是否激活
        responses:
          200:
            description: 成功更新派车单位信息
          404:
            description: 派车单位不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 调用服务层更新派车单位信息
            unit = DispatchUnitService.update_dispatch_unit(unit_id, data)
            
            if not unit:
                return error_response("派车单位不存在", 404)
            
            # 返回成功响应
            return success_response(unit, "派车单位信息更新成功")
        except Exception as e:
            logger.error(f"更新派车单位信息失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch_unit:delete')
    def delete_dispatch_unit(unit_id: int):
        """
        删除派车单位
        ---
        tags:
          - 派车单位管理
        parameters:
          - name: unit_id
            in: path
            type: integer
            required: true
            description: 派车单位ID
        responses:
          200:
            description: 成功删除派车单位
          404:
            description: 派车单位不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层删除派车单位
            result = DispatchUnitService.delete_dispatch_unit(unit_id)
            
            if not result:
                return error_response("派车单位不存在", 404)
            
            # 返回成功响应
            return success_response(None, "派车单位删除成功")
        except Exception as e:
            logger.error(f"删除派车单位失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch_unit:read')
    def get_active_dispatch_units():
        """
        获取所有激活的派车单位
        ---
        tags:
          - 派车单位管理
        responses:
          200:
            description: 成功获取激活的派车单位列表
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取激活的派车单位列表
            units = DispatchUnitService.get_active_dispatch_units()
            
            # 返回成功响应
            return success_response(units)
        except Exception as e:
            logger.error(f"获取激活派车单位列表失败: {str(e)}")
            return error_response(str(e), 500)