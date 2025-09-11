from flask import Blueprint
from .vehicle_controller import VehicleController

# 创建车辆管理蓝图
vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/api/v1/vehicles')

# 车辆列表路由
vehicle_bp.route('/', methods=['GET'])(VehicleController.get_vehicle_list)

# 车辆详情路由
vehicle_bp.route('/<int:vehicle_id>', methods=['GET'])(VehicleController.get_vehicle_detail)

# 创建车辆路由
vehicle_bp.route('/', methods=['POST'])(VehicleController.create_vehicle)

# 更新车辆路由
vehicle_bp.route('/<int:vehicle_id>', methods=['PUT'])(VehicleController.update_vehicle)

# 删除车辆路由
vehicle_bp.route('/<int:vehicle_id>', methods=['DELETE'])(VehicleController.delete_vehicle)

# 更新车辆容积路由
vehicle_bp.route('/update-volume', methods=['POST'])(VehicleController.update_vehicle_volume)

# 获取车辆容积更新历史路由
vehicle_bp.route('/<int:vehicle_id>/volume-history', methods=['GET'])(VehicleController.get_volume_update_history)

# 获取车型折算系数表路由
vehicle_bp.route('/conversion-factors', methods=['GET'])(VehicleController.get_vehicle_conversion_factors)