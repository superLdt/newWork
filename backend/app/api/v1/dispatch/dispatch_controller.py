from flask import request, jsonify
from app.services.dispatch.dispatch_service import DispatchService
from app.business.dispatch.dispatch_business import DispatchBusiness
from app.business.dispatch.status_manager import DispatchStatusManager
from app.business.vehicle.vehicle_downgrade_business import VehicleDowngradeBusiness
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DispatchController:
    """
    派车流程控制器类，处理派车相关的API请求
    """
    
    @staticmethod
    @permission_required('dispatch:read')
    def get_dispatch_task_list():
        """
        获取派车任务列表
        ---
        tags:
          - 派车管理
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
          - name: status
            in: query
            type: string
            description: 任务状态
        responses:
          200:
            description: 成功获取派车任务列表
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
            status = request.args.get('status', '')
            
            # 调用服务层获取派车任务列表（修复命名不一致）
            filters = {}
            if status:
                filters['status'] = status
            if query:
                # 将通用查询映射为按邮路名称模糊查询
                filters['mail_route_name'] = query
            tasks, total = DispatchService.get_task_list(page, per_page, filters)
            
            # 返回成功响应
            return success_response({
                'items': tasks,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        except Exception as e:
            logger.error(f"获取派车任务列表失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:read')
    def get_dispatch_task_detail(task_id: str):
        """
        获取派车任务详情
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
        responses:
          200:
            description: 成功获取派车任务详情
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取派车任务详情（修复命名不一致）
            task = DispatchService.get_task_by_id(task_id)
            
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 返回成功响应
            return success_response(task)
        except Exception as e:
            logger.error(f"获取派车任务详情失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:create')
    def create_dispatch_task():
        """
        创建派车任务
        ---
        tags:
          - 派车管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                required_date:
                  type: string
                  format: date
                  description: 需求日期
                origin_bureau:
                  type: string
                  description: 始发局
                mail_route_name:
                  type: string
                  description: 邮路名称
                organizing_unit:
                  type: string
                  description: 组开单位（承运商）
                transport_type:
                  type: string
                  description: 运输类型
                requirement_type:
                  type: string
                  description: 需求类型
                standard_weight:
                  type: string
                  description: 标准吨位
                standard_volume:
                  type: integer
                  description: 标准容积
                actual_volume:
                  type: integer
                  description: 实际需求容积
                special_requirements:
                  type: string
                  description: 特殊要求
                initiator_department:
                  type: string
                  description: 发起人部门
                audit_required:
                  type: boolean
                  description: 是否需要审核
        responses:
          201:
            description: 成功创建派车任务
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            # 调用业务层验证任务创建
            validation_result = DispatchBusiness.validate_task_creation(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层创建派车任务（包含角色判断逻辑）
            task = DispatchBusiness.create_dispatch_task(data)
            
            # 返回成功响应
            return success_response(task, code=201)
        except Exception as e:
            logger.error(f"创建派车任务失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:update')
    def update_dispatch_task(task_id: str):
        """
        更新派车任务
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: string
            required: true
            description: 任务ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                required_date:
                  type: string
                  format: date
                  description: 需求日期
                origin_bureau:
                  type: string
                  description: 始发局
                mail_route_name:
                  type: string
                  description: 邮路名称
                organizing_unit:
                  type: string
                  description: 组开单位（承运商）
                transport_type:
                  type: string
                  description: 运输类型
                requirement_type:
                  type: string
                  description: 需求类型
                standard_weight:
                  type: string
                  description: 标准吨位
                standard_volume:
                  type: integer
                  description: 标准容积
                actual_volume:
                  type: integer
                  description: 实际需求容积
                special_requirements:
                  type: string
                  description: 特殊要求
                initiator_department:
                  type: string
                  description: 发起人部门
                audit_required:
                  type: boolean
                  description: 是否需要审核
        responses:
          200:
            description: 成功更新派车任务
          400:
            description: 参数错误
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 调用业务层验证任务更新
            validation_result = DispatchBusiness.validate_task_update(task_id, data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用服务层更新派车任务
            updated_task = DispatchService.update_dispatch_task(task_id, data)
            
            # 返回成功响应
            return success_response(updated_task)
        except Exception as e:
            logger.error(f"更新派车任务失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:approve')
    def approve_dispatch_task(task_id: str):
        """
        审核派车任务
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                approved:
                  type: boolean
                  description: 是否通过审核
                comment:
                  type: string
                  description: 审核意见
        responses:
          200:
            description: 成功审核派车任务
          400:
            description: 参数错误
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验�证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            if 'approved' not in data:
                return error_response("缺少审核结果参数", 400)
            
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 调用业务层验证任务审核
            validation_result = DispatchBusiness.validate_task_approval(task_id, data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层处理任务审核
            result = DispatchBusiness.process_task_approval(task_id, data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"审核派车任务失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:assign')
    def assign_vehicle(task_id: str):
        """
        分配车辆
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                vehicle_id:
                  type: integer
                  description: 车辆ID
                driver_name:
                  type: string
                  description: 司机姓名
                driver_phone:
                  type: string
                  description: 司机电话
                notes:
                  type: string
                  description: 备注
        responses:
          200:
            description: 成功分配车辆
          400:
            description: 参数错误
          404:
            description: 任务或车辆不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            if 'vehicle_id' not in data:
                return error_response("缺少车辆ID参数", 400)
            
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 调用业务层验证车辆分配
            validation_result = DispatchBusiness.validate_vehicle_assignment(task_id, data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层处理车辆分配
            result = DispatchBusiness.process_vehicle_assignment(task_id, data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"分配车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:complete')
    def complete_task(task_id: str):
        """
        完成派车任务
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                completion_notes:
                  type: string
                  description: 完成备注
        responses:
          200:
            description: 成功完成派车任务
          400:
            description: 参数错误
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 调用业务层验证任务完成
            validation_result = DispatchBusiness.validate_task_completion(task_id, data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层处理任务完成
            result = DispatchBusiness.process_task_completion(task_id, data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"完成派车任务失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('supplier:respond')
    def submit_supplier_response():
        """
        提交供应商响应
        ---
        tags:
          - 派车管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                task_id:
                  type: string
                  description: 任务ID
                manifest_number:
                  type: string
                  description: 货票号
                dispatch_number:
                  type: string
                  description: 派车单号
                vehicles:
                  type: array
                  description: 车辆信息列表
                  items:
                    type: object
                    properties:
                      license_plate:
                        type: string
                        description: 车牌号
                      carriage_number:
                        type: string
                        description: 车厢号
                      driver_name:
                        type: string
                        description: 司机姓名
                      driver_phone:
                        type: string
                        description: 司机电话
                      vehicle_type:
                        type: string
                        description: 车辆类型
                      load_capacity:
                        type: number
                        description: 载重量
                      actual_volume:
                        type: number
                        description: 实际容积
                notes:
                  type: string
                  description: 响应备注
        responses:
          200:
            description: 响应提交成功
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 数据验证
            validation_result = DispatchBusiness.validate_supplier_response_data(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层处理供应商响应
            result = DispatchBusiness.process_supplier_response(data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"提交供应商响应失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('team:assign')
    def submit_team_response():
        """
        提交班组派车响应
        ---
        tags:
          - 派车管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                task_id:
                  type: string
                  description: 任务ID
                manifest_number:
                  type: string
                  description: 货票号
                dispatch_number:
                  type: string
                  description: 派车单号
                vehicles:
                  type: array
                  description: 车辆信息列表
                notes:
                  type: string
                  description: 响应备注
        responses:
          200:
            description: 班组响应提交成功
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 数据验证
            validation_result = DispatchBusiness.validate_team_response_data(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层处理班组响应
            result = DispatchBusiness.process_team_response(data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"提交班组响应失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('outsourcing:assign')
    def submit_outsourcing_response():
        """
        提交外包管理公司响应
        ---
        tags:
          - 派车管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                task_id:
                  type: string
                  description: 任务ID
                manifest_number:
                  type: string
                  description: 货票号
                dispatch_number:
                  type: string
                  description: 派车单号
                vehicles:
                  type: array
                  description: 车辆信息列表
                notes:
                  type: string
                  description: 响应备注
        responses:
          200:
            description: 外包响应提交成功
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 数据验证
            validation_result = DispatchBusiness.validate_outsourcing_response_data(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'], 400)
            
            # 调用业务层处理外包响应
            result = DispatchBusiness.process_outsourcing_response(data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"提交外包响应失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('dispatch:read')
    def get_task_status_history(task_id: str):
        """
        获取派车任务状态历史
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
        responses:
          200:
            description: 成功获取派车任务状态历史
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 调用状态管理器获取任务状态流转记录
            status_flow = DispatchStatusManager.get_status_flow(task_id)
            
            # 返回成功响应
            return success_response(status_flow)
        except Exception as e:
            logger.error(f"获取派车任务状态历史失败: {str(e)}")
            return error_response(str(e), 500)
            
    @staticmethod
    @permission_required('dispatch:read')
    def get_next_possible_statuses(task_id: str):
        """
        获取任务可能的下一个状态
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
        responses:
          200:
            description: 成功获取任务可能的下一个状态
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 获取当前状态
            current_status = task.get('status')
            
            # 调用状态管理器获取可能的下一个状态
            next_statuses = DispatchStatusManager.get_next_possible_statuses(current_status)
            
            # 格式化状态信息
            formatted_statuses = []
            for status in next_statuses:
                formatted_statuses.append({
                    'code': status,
                    'name': DispatchStatusManager.get_status_display_name(status)
                })
            
            # 返回成功响应
            return success_response(formatted_statuses)
        except Exception as e:
            logger.error(f"获取任务可能的下一个状态失败: {str(e)}")
            return error_response(str(e), 500)
            
    @staticmethod
    @permission_required('dispatch:read')
    def get_task_operation_logs(task_id: str):
        """
        获取派车任务操作日志
        ---
        tags:
          - 派车管理
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: 任务ID
        responses:
          200:
            description: 成功获取派车任务操作日志
          404:
            description: 任务不存在
          500:
            description: 服务器错误
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return error_response("派车任务不存在", 404)
            
            # 调用日志管理器获取任务操作日志
            logs = DispatchLogManager.get_task_logs(task_id)
            
            # 返回成功响应
            return success_response(logs)
        except Exception as e:
            logger.error(f"获取派车任务操作日志失败: {str(e)}")
            return error_response(str(e), 500)
            
    @staticmethod
    @permission_required('vehicle:read')
    def get_vehicle_downgrade_history(vehicle_id: int):
        """
        获取车辆降档历史
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
            description: 成功获取车辆降档历史
          404:
            description: 车辆不存在
          500:
            description: 服务器错误
        """
        try:
            # 调用业务层获取车辆降档历史
            history = VehicleDowngradeBusiness.get_vehicle_downgrade_history(vehicle_id)
            
            # 返回成功响应
            return success_response(history)
        except ValueError as e:
            logger.error(f"获取车辆降档历史失败: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            logger.error(f"获取车辆降档历史失败: {str(e)}")
            return error_response(str(e), 500)
            
    @staticmethod
    @permission_required('vehicle:merge')
    def merge_vehicles():
        """
        合并车辆
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
                source_vehicle_id:
                  type: integer
                  description: 源车辆ID
                target_vehicle_id:
                  type: integer
                  description: 目标车辆ID
                reason:
                  type: string
                  description: 合并原因
        responses:
          200:
            description: 成功合并车辆
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
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            if 'source_vehicle_id' not in data or 'target_vehicle_id' not in data:
                return error_response("缺少源车辆ID或目标车辆ID参数", 400)
            
            # 调用业务层处理车辆合并
            result = DispatchBusiness.merge_vehicles(
                source_vehicle_id=data['source_vehicle_id'],
                target_vehicle_id=data['target_vehicle_id']
            )
            
            # 返回成功响应
            return success_response(result)
        except ValueError as e:
            logger.error(f"合并车辆失败: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"合并车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:downgrade')
    def downgrade_vehicle(vehicle_id: int):
        """
        降档车辆
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
                reason:
                  type: string
                  description: 降档原因
                downgrade_type:
                  type: string
                  description: 降档后的车辆类型
        responses:
          200:
            description: 成功降档车辆
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
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            if 'downgrade_type' not in data:
                return error_response("缺少降档类型参数", 400)
                
            if 'reason' not in data:
                return error_response("缺少降档原因参数", 400)
            
            # 调用业务层处理车辆降档
            result = DispatchBusiness.downgrade_vehicle(
                vehicle_id=vehicle_id,
                downgrade_data={
                    'downgrade_type': data['downgrade_type'],
                    'reason': data['reason']
                }
            )
            
            # 返回成功响应
            return success_response(result)
        except ValueError as e:
            logger.error(f"降档车辆失败: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"降档车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:merge')
    def merge_vehicles():
        """
        合并车辆
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
                source_vehicle_id:
                  type: integer
                  description: 源车辆ID
                target_vehicle_id:
                  type: integer
                  description: 目标车辆ID
                reason:
                  type: string
                  description: 合并原因
        responses:
          200:
            description: 成功合并车辆
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
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            if 'source_vehicle_id' not in data or 'target_vehicle_id' not in data:
                return error_response("缺少源车辆ID或目标车辆ID参数", 400)
            
            # 调用业务层处理车辆合并
            result = DispatchBusiness.process_vehicle_merge(data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"合并车辆失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:downgrade')
    def downgrade_vehicle(vehicle_id: int):
        """
        降档车辆
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
                reason:
                  type: string
                  description: 降档原因
                new_vehicle_type:
                  type: string
                  description: 新车辆类型
        responses:
          200:
            description: 成功降档车辆
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
            
            # 验证请求数据
            if not data:
                return error_response("请求数据不能为空", 400)
            
            if 'new_vehicle_type' not in data:
                return error_response("缺少新车辆类型参数", 400)
            
            # 调用业务层处理车辆降档
            result = DispatchBusiness.process_vehicle_downgrade(vehicle_id, data)
            
            # 返回成功响应
            return success_response(result)
        except Exception as e:
            logger.error(f"降档车辆失败: {str(e)}")
            return error_response(str(e), 500)