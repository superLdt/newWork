"""
车辆吨位-容积映射API控制器
提供吨位-容积映射关系的CRUD操作和查询接口
"""

from flask import request, jsonify
from app.services.tonnage_volume_mapping_service import TonnageVolumeMappingService
from app.common.response import success_response, error_response
from app.utils.exceptions import ValidationError, ResourceNotFoundError
from app.auth.decorators import permission_required
import logging

# Blueprint moved to routes file to keep controller slim
logger = logging.getLogger(__name__)


class TonnageVolumeMappingController:
    """车辆吨位-容积映射控制器"""
    
    def __init__(self):
        self.service = TonnageVolumeMappingService()
    
    @staticmethod
    @permission_required('tonnage_volume:read')
    # route moved to routes file: GET /mappings
    def get_all_mappings():
        """
        获取所有吨位-容积映射关系
        
        Returns:
            JSON: 包含所有映射关系的响应
        """
        try:
            controller = TonnageVolumeMappingController()
            mappings = controller.service.get_all_mappings()
            
            return success_response(
                data=mappings,
                message="获取吨位-容积映射关系成功"
            )
        except Exception as e:
             logger.error(f"获取吨位-容积映射关系时发生错误: {str(e)}")
             return error_response(
                 message="获取吨位-容积映射关系失败",
                 code=500
             )

    @staticmethod
    @permission_required('tonnage_volume:read')
    # route moved to routes file: GET /mappings/active
    def get_active_mappings():
        """
        获取所有启用的吨位-容积映射关系
        
        Returns:
            JSON: 包含启用映射关系的响应
        """
        try:
            controller = TonnageVolumeMappingController()
            mappings = controller.service.get_active_mappings()
            
            return success_response(
                data=mappings,
                message="获取启用映射关系成功"
            )
        except Exception as e:
             logger.error(f"获取启用映射关系时发生错误: {str(e)}")
             return error_response(
                 message="获取启用映射关系失败",
                 code=500
             )

    @staticmethod
    @permission_required('tonnage_volume:read')
    # route moved to routes file: GET /mappings/<int:mapping_id>
    def get_mapping_by_id(mapping_id):
        """
        根据ID获取单个吨位-容积映射关系
        
        Args:
            mapping_id: 映射关系ID
            
        Returns:
            JSON: 包含映射关系信息的响应
        """
        try:
            controller = TonnageVolumeMappingController()
            mapping = controller.service.get_mapping_by_id(mapping_id)
            
            return success_response(
                data=mapping,
                message="获取映射关系成功"
            )
        except ResourceNotFoundError as e:
             return error_response(
                 message=str(e),
                 code=404
             )
        except Exception as e:
            logger.error(f"获取映射关系时发生错误: {str(e)}")
            return error_response(
                message="获取映射关系失败",
                code=500
            )

    @staticmethod
    @permission_required('tonnage_volume:create')
    # route moved to routes file: POST /mappings
    def create_mapping():
        """
        创建新的吨位-容积映射关系
        Returns:
            JSON: 创建结果
        """
        try:
            data = request.get_json() or {}
            controller = TonnageVolumeMappingController()
            mapping = controller.service.create_mapping(data)
            return success_response(
                data=mapping,
                message="创建映射关系成功"
            )
        except ValidationError as e:
            return error_response(
                message=str(e),
                code=400
            )
        except Exception as e:
            logger.error(f"创建映射关系时发生错误: {str(e)}")
            return error_response(
                message="创建映射关系失败",
                code=500
            )

    @staticmethod
    @permission_required('tonnage_volume:update')
    # route moved to routes file: PUT /mappings/<int:mapping_id>
    def update_mapping(mapping_id):
        """
        更新吨位-容积映射关系
        Args:
            mapping_id: 映射关系ID
        Returns:
            JSON: 更新结果
        """
        try:
            data = request.get_json() or {}
            controller = TonnageVolumeMappingController()
            mapping = controller.service.update_mapping(mapping_id, data)
            return success_response(
                data=mapping,
                message="更新映射关系成功"
            )
        except ValidationError as e:
            return error_response(
                message=str(e),
                code=400
            )
        except ResourceNotFoundError as e:
            return error_response(
                message=str(e),
                code=404
            )
        except Exception as e:
            logger.error(f"更新映射关系时发生错误: {str(e)}")
            return error_response(
                message="更新映射关系失败",
                code=500
            )

    @staticmethod
    @permission_required('tonnage_volume:delete')
    # route moved to routes file: DELETE /mappings/<int:mapping_id>
    def delete_mapping(mapping_id):
        """
        删除吨位-容积映射关系
        Args:
            mapping_id: 映射关系ID
        Returns:
            JSON: 删除结果
        """
        try:
            controller = TonnageVolumeMappingController()
            controller.service.delete_mapping(mapping_id)
            return success_response(
                message="删除映射关系成功"
            )
        except ResourceNotFoundError as e:
            return error_response(
                message=str(e),
                code=404
            )
        except Exception as e:
            logger.error(f"删除映射关系时发生错误: {str(e)}")
            return error_response(
                message="删除映射关系失败",
                code=500
            )

    @staticmethod
    @permission_required('tonnage_volume:read')
    # route moved to routes file: GET /mappings/volume/<tonnage>
    def get_volume_by_tonnage(tonnage):
        """
        根据吨位获取对应的容积信息
        
        Args:
            tonnage: 标准吨位
            
        Returns:
            JSON: 包含容积信息的响应
        """
        try:
            controller = TonnageVolumeMappingController()
            volume_info = controller.service.get_volume_by_tonnage(tonnage)
            
            return success_response(
                data=volume_info,
                message="获取容积信息成功"
            )
        except ResourceNotFoundError as e:
            return error_response(
                message=str(e),
                code=404
            )
        except Exception as e:
            logger.error(f"获取容积信息时发生错误: {str(e)}")
            return error_response(
                message="获取容积信息失败",
                code=500
            )

    @staticmethod
    @permission_required('tonnage_volume:read')
    # route moved to routes file: GET /mappings/tonnage/<float:volume>
    def get_tonnage_by_volume(volume: float):
        """
        根据容积反查对应的吨位档位
        Args:
            volume: 容积值
        Returns:
            JSON: 包含吨位档位信息的响应
        """
        try:
            controller = TonnageVolumeMappingController()
            result = controller.service.get_tonnage_by_volume(volume)
            if not result:
                return error_response(
                    message="未找到匹配的吨位档位",
                    code=404
                )
            return success_response(
                data=result,
                message="获取吨位档位成功"
            )
        except Exception as e:
            logger.error(f"根据容积获取吨位档位时发生错误: {str(e)}")
            return error_response(
                message="获取吨位档位失败",
                code=500
            )