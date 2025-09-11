from flask import request, jsonify
from app.services.vehicle.vehicle_service import VehicleService
from app.business.vehicle.vehicle_business import VehicleBusiness
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class VehicleController:
    """
    车辆控制器类，处理车辆相关的API请求
    """
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_vehicle_list():
        """
        获取车辆列表
        ---
        tags:
          - 车辆管理
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
            vehicles, total = VehicleService.get_vehicle_list(page, per_page, query)
            
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
          - 车辆管理
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
            vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
            
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
        创建车辆
        ---
        tags:
          - 车辆管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                task_id:
                  type: string
                  description: 关联任务ID
                manifest_number:
                  type: string
                  description: 货票号
                dispatch_number:
                  type: string
                  description: 派车单号
                license_plate:
                  type: string
                  description: 车牌号
                carriage_number:
                  type: string
                  description: 车厢号
                notes:
                  type: string
                  description: 备注
                actual_volume:
                  type: number
                  description: 实际容积
                required_volume:
                  type: number
                  description: 需求容积
                confirmed_volume:
                  type: number
                  description: 确认容积
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
            
            # 验证必填字段
            required_fields = ['license_plate', 'carriage_number']
            for field in required_fields:
                if field not in data or not data[field]:
                    return error_response(f"缺少必填字段: {field}", 400)
            
            # 调用服务层创建车辆
            vehicle = VehicleService.create_vehicle(data)
            
            # 返回成功响应
            return success_response(vehicle, "车辆创建成功")
        except Exception as e:
            logger.error(f"创建车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:update')
    def update_vehicle(vehicle_id: int):
        """
        更新车辆信息
        ---
        tags:
          - 车辆管理
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
                task_id:
                  type: string
                  description: 关联任务ID
                manifest_number:
                  type: string
                  description: 货票号
                dispatch_number:
                  type: string
                  description: 派车单号
                license_plate:
                  type: string
                  description: 车牌号
                carriage_number:
                  type: string
                  description: 车厢号
                notes:
                  type: string
                  description: 备注
                required_volume:
                  type: number
                  description: 需求容积
                confirmed_volume:
                  type: number
                  description: 确认容积
        responses:
          200:
            description: 成功更新车辆信息
          404:
            description: 车辆不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 调用服务层更新车辆信息
            vehicle = VehicleService.update_vehicle(vehicle_id, data)
            
            if not vehicle:
                return error_response("车辆不存在", 404)
            
            # 返回成功响应
            return success_response(vehicle, "车辆信息更新成功")
        except Exception as e:
            logger.error(f"更新车辆信息失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:delete')
    def delete_vehicle(vehicle_id: int):
        """
        删除车辆
        ---
        tags:
          - 车辆管理
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
            result = VehicleService.delete_vehicle(vehicle_id)
            
            if not result:
                return error_response("车辆不存在", 404)
            
            # 返回成功响应
            return success_response(None, "车辆删除成功")
        except Exception as e:
            logger.error(f"删除车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('workshop:update_volume')
    def update_vehicle_volume():
        """
        更新车辆容积
        ---
        tags:
          - 车辆管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                vehicle_id:
                  type: integer
                  description: 车辆ID
                new_volume:
                  type: number
                  description: 新容积
                reason:
                  type: string
                  description: 修改原因
                volume_photo_url:
                  type: string
                  description: 容积照片URL
                approval_doc_url:
                  type: string
                  description: 审批凭证URL
        responses:
          200:
            description: 成功更新车辆容积
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
            
            # 验证必填字段
            required_fields = ['vehicle_id', 'new_volume', 'reason', 'volume_photo_url', 'approval_doc_url']
            for field in required_fields:
                if field not in data or (field != 'reason' and not data[field]):
                    return error_response(f"缺少必填字段: {field}", 400)
            
            # 添加当前用户ID作为修改人
            from flask import g
            data['modified_by'] = g.current_user.id
            
            # 调用业务逻辑层处理容积更新
            result = VehicleBusiness.process_volume_update(data)
            
            # 返回成功响应
            return success_response(result, "车辆容积更新成功")
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"更新车辆容积失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_volume_update_history(vehicle_id: int):
        """
        获取车辆容积更新历史
        ---
        tags:
          - 车辆管理
        parameters:
          - name: vehicle_id
            in: path
            type: integer
            required: true
            description: 车辆ID
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
        responses:
          200:
            description: 成功获取容积更新历史
          500:
            description: 服务器错误
        """
        try:
            # 获取请求参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 调用服务层获取容积更新历史
            history, total = VehicleService.get_volume_update_history(vehicle_id, page, per_page)
            
            # 返回成功响应
            return success_response({
                'items': history,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        except Exception as e:
            logger.error(f"获取容积更新历史失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def get_vehicle_conversion_factors():
        """
        获取车型折算系数表
        ---
        tags:
          - 车辆管理
        responses:
          200:
            description: 成功获取车型折算系数表
          500:
            description: 服务器错误
        """
        try:
            # 调用业务逻辑层获取车型折算系数表
            factors = VehicleBusiness.get_vehicle_conversion_factors()
            
            # 返回成功响应
            return success_response(factors)
        except Exception as e:
            logger.error(f"获取车型折算系数表失败: {str(e)}")
            return error_response(str(e), 500)