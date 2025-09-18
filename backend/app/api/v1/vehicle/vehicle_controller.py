from flask import request, jsonify, make_response
from app.services.vehicle.vehicle_service import VehicleService
from app.business.vehicle.vehicle_business import VehicleBusiness
from app.services.vehicle_validation_service import VehicleValidationService
from app.services.excel_processing_service import ExcelProcessingService
from app.services.batch_import_service import BatchImportService
from app.auth.decorators import permission_required, permission_required_any
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
    @permission_required('vehicle:create')
    def download_import_template():
        """
        下载车辆导入模板
        ---
        tags:
          - 车辆管理
        responses:
          200:
            description: 成功下载模板文件
          500:
            description: 服务器错误
        """
        try:
            # 生成模板文件
            template_content = ExcelProcessingService.create_import_template()
            
            # 创建响应
            response = make_response(template_content)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = 'attachment; filename=vehicle_import_template.xlsx'
            
            return response
            
        except Exception as e:
            logger.error(f"下载导入模板失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:create')
    def preview_import_data():
        """
        预览导入数据
        ---
        tags:
          - 车辆管理
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: Excel文件
        responses:
          200:
            description: 成功预览导入数据
          400:
            description: 文件格式错误或数据验证失败
          500:
            description: 服务器错误
        """
        try:
            # 检查文件是否存在
            if 'file' not in request.files:
                return error_response('未找到上传文件', 400)
            
            file = request.files['file']
            if file.filename == '':
                return error_response('未选择文件', 400)
            
            # 验证文件格式和大小
            file_validation = ExcelProcessingService.validate_file_format(
                file.filename, 
                len(file.read())
            )
            file.seek(0)  # 重置文件指针
            
            if not file_validation['valid']:
                return error_response({
                    'message': '文件验证失败',
                    'errors': file_validation['errors']
                }, 400)
            
            # 解析Excel文件
            parse_result = ExcelProcessingService.parse_excel_file(
                file.read(), 
                file.filename
            )
            
            if not parse_result['success']:
                return error_response(parse_result['error'], 400)
            
            # 验证和处理数据
            validation_result = ExcelProcessingService.validate_and_process_data(
                parse_result['data']
            )
            
            return success_response({
                'total_rows': parse_result['total_rows'],
                'summary': validation_result['summary'],
                'preview_data': validation_result['preview_data'],
                'validation_results': validation_result['validation_results']
            })
            
        except Exception as e:
            logger.error(f"预览导入数据失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:create')
    def execute_import():
        """
        执行批量导入
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
                validation_results:
                  type: array
                  description: 验证结果列表
        responses:
          200:
            description: 导入完成
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            data = request.get_json()
            validation_results = data.get('validation_results', [])
            
            if not validation_results:
                return error_response('没有可导入的数据', 400)
            
            # 获取当前用户ID
            from flask import g
            user_id = g.current_user.id if hasattr(g, 'current_user') and getattr(g, 'current_user') is not None else None
            
            # 验证导入权限
            permission_check = BatchImportService.validate_import_permission(user_id)
            if not permission_check['valid']:
                return error_response(permission_check['message'], 403)
            
            # 执行批量导入
            import_result = BatchImportService.import_vehicles(
                validation_results, 
                user_id
            )
            
            # 创建导入日志
            log_data = BatchImportService.create_import_log(
                import_result, 
                user_id, 
                data.get('filename', '')
            )
            
            # 获取导入统计
            statistics = BatchImportService.get_import_statistics(
                import_result.get('created_vehicles', [])
            )
            
            return success_response({
                'import_result': import_result,
                'statistics': statistics,
                'log_id': log_data.get('id')
            })
            
        except Exception as e:
            logger.error(f"执行批量导入失败: {str(e)}")
            return error_response(str(e), 500)
    
    @staticmethod
    @permission_required('vehicle:read')
    def export_validation_errors():
        """
        导出验证错误报告
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
                validation_results:
                  type: array
                  description: 验证结果列表
        responses:
          200:
            description: 成功导出错误报告
          400:
            description: 参数错误
          500:
            description: 服务器错误
        """
        try:
            data = request.get_json()
            validation_results = data.get('validation_results', [])
            
            # 生成错误报告
            error_report = ExcelProcessingService.export_validation_errors(validation_results)
            
            # 创建响应
            response = make_response(error_report)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = 'attachment; filename=validation_errors_report.xlsx'
            
            return response
            
        except Exception as e:
            logger.error(f"导出验证错误报告失败: {str(e)}")
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
            
            # 使用验证服务验证数据
            validation_errors = VehicleValidationService.validate_vehicle_data(data)
            if validation_errors:
                return error_response({
                    'message': '数据验证失败',
                    'errors': validation_errors
                }, 400)
            
            # 自动设置车辆分类
            data = VehicleValidationService.auto_set_category(data)
            
            # 标准化常用公司数据
            if 'frequent_companies' in data:
                data['frequent_companies'] = VehicleValidationService.normalize_frequent_companies(
                    data['frequent_companies']
                )
            
            # 调用服务层创建车辆
            vehicle = VehicleService.create_vehicle(data)
            
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
            
            # 使用验证服务验证数据（更新时可能不需要所有必填字段）
            validation_errors = VehicleValidationService.validate_vehicle_data(data)
            if validation_errors:
                return error_response({
                    'message': '数据验证失败',
                    'errors': validation_errors
                }, 400)
            
            # 自动设置车辆分类
            data = VehicleValidationService.auto_set_category(data)
            
            # 标准化常用公司数据
            if 'frequent_companies' in data:
                data['frequent_companies'] = VehicleValidationService.normalize_frequent_companies(
                    data['frequent_companies']
                )
            
            # 调用服务层更新车辆信息
            vehicle = VehicleService.update_vehicle(vehicle_id, data)
            
            if not vehicle:
                return error_response("车辆不存在", 404)
            
            # 返回成功响应
            return success_response(vehicle, "车辆信息更新成功")
        except ValueError as e:
            return error_response(str(e), 400)
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
    @permission_required_any(['supplier:respond', 'team:assign', 'outsourcing:assign'])
    def get_available_vehicles():
        """
        获取可用车辆列表
        ---
        tags:
          - 车辆管理
        responses:
          200:
            description: 成功获取可用车辆列表
          500:
            description: 服务器错误
        """
        try:
            # 调用服务层获取可用车辆列表
            vehicles = VehicleService.get_available_vehicles()
            
            # 返回成功响应
            return success_response(vehicles)
        except Exception as e:
            logger.error(f"获取可用车辆列表失败: {str(e)}")
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