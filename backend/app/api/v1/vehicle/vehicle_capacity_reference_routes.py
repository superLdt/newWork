from flask import Blueprint
from .vehicle_capacity_reference_controller import VehicleCapacityReferenceController

# 创建车辆容积参考管理蓝图
vehicle_capacity_reference_bp = Blueprint('vehicle_capacity_reference', __name__, url_prefix='/vehicle-capacity-reference')

# 车辆列表路由
vehicle_capacity_reference_bp.route('/', methods=['GET'], strict_slashes=False)(VehicleCapacityReferenceController.get_vehicle_list)
# 新增无尾斜杠路由，避免预检到/vehicle-capacity-reference发生重定向
vehicle_capacity_reference_bp.route('', methods=['GET'], strict_slashes=False)(VehicleCapacityReferenceController.get_vehicle_list)

# 车辆详情路由
vehicle_capacity_reference_bp.route('/<int:vehicle_id>', methods=['GET'])(VehicleCapacityReferenceController.get_vehicle_detail)

# 创建车辆路由
vehicle_capacity_reference_bp.route('/', methods=['POST'])(VehicleCapacityReferenceController.create_vehicle)

# 更新车辆路由
vehicle_capacity_reference_bp.route('/<int:vehicle_id>', methods=['PUT'])(VehicleCapacityReferenceController.update_vehicle)

# 删除车辆路由
vehicle_capacity_reference_bp.route('/<int:vehicle_id>', methods=['DELETE'])(VehicleCapacityReferenceController.delete_vehicle)

# 获取可用车辆列表路由
vehicle_capacity_reference_bp.route('/available', methods=['GET'])(VehicleCapacityReferenceController.get_available_vehicles)

# 搜索车辆路由
vehicle_capacity_reference_bp.route('/search', methods=['GET'])(VehicleCapacityReferenceController.search_vehicles)

# 获取车辆类型选项路由
vehicle_capacity_reference_bp.route('/vehicle-types', methods=['GET'])(VehicleCapacityReferenceController.get_vehicle_type_choices)