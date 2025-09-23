from flask import Blueprint
from .tonnage_volume_mapping_controller import TonnageVolumeMappingController

# 与 vehicle_capacity_reference_routes.py 保持一致的蓝图与路由定义方式
# 该蓝图会在 app/api/v1/__init__.py 中以 url_prefix '/vehicle/tonnage-volume' 注册

tonnage_volume_mapping_bp = Blueprint('tonnage_volume_mapping', __name__)

# 列表与查询
tonnage_volume_mapping_bp.route('/mappings', methods=['GET'])(TonnageVolumeMappingController.get_all_mappings)
tonnage_volume_mapping_bp.route('/mappings/active', methods=['GET'])(TonnageVolumeMappingController.get_active_mappings)
tonnage_volume_mapping_bp.route('/mappings/<int:mapping_id>', methods=['GET'])(TonnageVolumeMappingController.get_mapping_by_id)

# 创建、更新、删除
tonnage_volume_mapping_bp.route('/mappings', methods=['POST'])(TonnageVolumeMappingController.create_mapping)
tonnage_volume_mapping_bp.route('/mappings/<int:mapping_id>', methods=['PUT'])(TonnageVolumeMappingController.update_mapping)
tonnage_volume_mapping_bp.route('/mappings/<int:mapping_id>', methods=['DELETE'])(TonnageVolumeMappingController.delete_mapping)

# 其它查询
tonnage_volume_mapping_bp.route('/mappings/volume/<tonnage>', methods=['GET'])(TonnageVolumeMappingController.get_volume_by_tonnage)
tonnage_volume_mapping_bp.route('/mappings/tonnage/<float:volume>', methods=['GET'])(TonnageVolumeMappingController.get_tonnage_by_volume)