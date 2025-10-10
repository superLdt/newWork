from flask import Blueprint
from .vehicle_controller import VehicleController

# 创建车辆管理蓝图
vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/vehicles')

# 车辆列表路由
vehicle_bp.route('/', methods=['GET'], strict_slashes=False)(VehicleController.get_vehicle_list)
# 新增无尾斜杠路由，避免预检到/vehicles发生重定向
vehicle_bp.route('', methods=['GET'], strict_slashes=False)(VehicleController.get_vehicle_list)

# 车辆详情路由
vehicle_bp.route('/<int:vehicle_id>', methods=['GET'])(VehicleController.get_vehicle_detail)

# 创建车辆路由
vehicle_bp.route('/', methods=['POST'])(VehicleController.create_vehicle)

# 更新车辆路由
vehicle_bp.route('/<int:vehicle_id>', methods=['PUT'])(VehicleController.update_vehicle)

# 删除车辆路由
vehicle_bp.route('/<int:vehicle_id>', methods=['DELETE'])(VehicleController.delete_vehicle)

# 获取可用车辆列表路由
vehicle_bp.route('/available', methods=['GET'])(VehicleController.get_available_vehicles)

# 更新车辆容积路由
vehicle_bp.route('/update-volume', methods=['POST'])(VehicleController.update_vehicle_volume)

# 获取车辆容积更新历史路由
vehicle_bp.route('/<int:vehicle_id>/volume-history', methods=['GET'])(VehicleController.get_volume_update_history)

# 获取车型折算系数表路由
vehicle_bp.route('/conversion-factors', methods=['GET'])(VehicleController.get_vehicle_conversion_factors)

# 车辆导入相关路由
# 下载导入模板路由
vehicle_bp.route('/import/template', methods=['GET'])(VehicleController.download_import_template)

# 预览导入数据路由
vehicle_bp.route('/import/preview', methods=['POST'])(VehicleController.preview_import_data)

# 执行批量导入路由
vehicle_bp.route('/import/execute', methods=['POST'])(VehicleController.execute_import)

# 导出验证错误报告路由
vehicle_bp.route('/import/export-errors', methods=['POST'])(VehicleController.export_validation_errors)