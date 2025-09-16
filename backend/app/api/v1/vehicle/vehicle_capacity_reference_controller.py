from flask import request, jsonify
from app.services.vehicle.vehicle_capacity_reference_service import VehicleCapacityReferenceService
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class VehicleCapacityReferenceController:
    """
    车辆容积参考控制器类，处理车辆日常管理相关的API请求
    """
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_vehicle_list():
        """
        获取车辆容积参考列表
        ---
        tags:
          - 车辆容积参考管理
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
            description: 成功获取车辆列表
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
            
            # 调用服务层获取车辆列表
            vehicles, total = VehicleCapacityReferenceService.get_vehicle_list(page, per_page, query)
            
            # 返回成功响应
            return success_response({
                'items': vehicles,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        except Exception as e:
            logger.error(f"获取车辆列表失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_vehicle_detail(vehicle_id: int):
        """
        获取车辆详情
        ---
        tags:
          - 车辆容积参考管理
        parameters:
          - name: vehicle_id
            in: path
            type: integer
            required: true
            description: 车辆ID
        responses:
          200:
            description: 成功获取车辆详情
          404:
            description: 车辆不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取车辆详情
            vehicle = VehicleCapacityReferenceService.get_vehicle_by_id(vehicle_id)
            
            if not vehicle:
                return error_response("车辆不存在", 404)
            
            # 返回成功响应
            return success_response(vehicle)
        except Exception as e:
            logger.error(f"获取车辆详情失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:create')
    def create_vehicle():
        """
        创建车辆容积参考
        ---
        tags:
          - 车辆容积参考管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                vehicle_type:
                  type: string
                  description: 车辆类型
                standard_volume:
                  type: number
                  description: 标准容积
                license_plate:
                  type: string
                  description: 车牌号
                carriage_number:
                  type: string
                  description: 车厢号
                frequent_companies:
                  type: array
                  items:
                    type: string
                  description: 常用公司列表
                status:
                  type: string
                  description: 状态
                original_capacity:
                  type: number
                  description: 原始载重量
                suppliers:
                  type: string
                  description: 供应商信息
        responses:
          200:
            description: 成功创建车辆
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            if not data:
                return error_response("请求数据不能为空", 400)
            
            # 调用服务层创建车辆
            vehicle = VehicleCapacityReferenceService.create_vehicle(data)
            
            # 返回成功响应
            return success_response(vehicle, "车辆创建成功")
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"创建车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:update')
    def update_vehicle(vehicle_id: int):
        """
        更新车辆容积参考
        ---
        tags:
          - 车辆容积参考管理
        parameters:
          - name: vehicle_id
            in: path
            type: integer
            required: true
            description: 车辆ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                vehicle_type:
                  type: string
                  description: 车辆类型
                standard_volume:
                  type: number
                  description: 标准容积
                license_plate:
                  type: string
                  description: 车牌号
                carriage_number:
                  type: string
                  description: 车厢号
                frequent_companies:
                  type: array
                  items:
                    type: string
                  description: 常用公司列表
                status:
                  type: string
                  description: 状态
                original_capacity:
                  type: number
                  description: 原始载重量
                suppliers:
                  type: string
                  description: 供应商信息
        responses:
          200:
            description: 成功更新车辆
          400:
            description: 参数错误
          404:
            description: 车辆不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            if not data:
                return error_response("请求数据不能为空", 400)
            
            # 调用服务层更新车辆
            vehicle = VehicleCapacityReferenceService.update_vehicle(vehicle_id, data)
            
            if not vehicle:
                return error_response("车辆不存在", 404)
            
            # 返回成功响应
            return success_response(vehicle, "车辆更新成功")
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"更新车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:delete')
    def delete_vehicle(vehicle_id: int):
        """
        删除车辆容积参考
        ---
        tags:
          - 车辆容积参考管理
        parameters:
          - name: vehicle_id
            in: path
            type: integer
            required: true
            description: 车辆ID
        responses:
          200:
            description: 成功删除车辆
          404:
            description: 车辆不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层删除车辆
            success = VehicleCapacityReferenceService.delete_vehicle(vehicle_id)
            
            if not success:
                return error_response("车辆不存在", 404)
            
            # 返回成功响应
            return success_response(None, "车辆删除成功")
        except Exception as e:
            logger.error(f"删除车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_available_vehicles():
        """
        获取可用车辆列表
        ---
        tags:
          - 车辆容积参考管理
        responses:
          200:
            description: 成功获取可用车辆列表
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取可用车辆列表
            vehicles = VehicleCapacityReferenceService.get_available_vehicles()
            
            # 返回成功响应
            return success_response(vehicles)
        except Exception as e:
            logger.error(f"获取可用车辆列表失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def search_vehicles():
        """
        搜索车辆
        ---
        tags:
          - 车辆容积参考管理
        parameters:
          - name: license_plate
            in: query
            type: string
            description: 车牌号
          - name: carriage_number
            in: query
            type: string
            description: 车厢号
        responses:
          200:
            description: 成功搜索车辆
          500:
            description: 服务器错误
        """
        try:
            # 获取请求参数
            license_plate = request.args.get('license_plate')
            carriage_number = request.args.get('carriage_number')
            
            # 调用服务层搜索车辆
            vehicles = VehicleCapacityReferenceService.search_vehicles(
                license_plate=license_plate,
                carriage_number=carriage_number
            )
            
            # 返回成功响应
            return success_response(vehicles)
        except Exception as e:
            logger.error(f"搜索车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_vehicle_type_choices():
        """
        获取车辆类型选项
        ---
        tags:
          - 车辆容积参考管理
        responses:
          200:
            description: 成功获取车辆类型选项
          500:
            description: 服务器错误
        """
        try:
            from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
            
            # 获取车辆类型选项
            choices = VehicleCapacityReference.get_vehicle_type_choices()
            
            # 返回成功响应
            return success_response(choices)
        except Exception as e:
            logger.error(f"获取车辆类型选项失败: {str(e)}")
            return error_response(str(e), 500)