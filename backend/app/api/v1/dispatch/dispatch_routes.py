from flask import Blueprint
from .dispatch_controller import DispatchController
from .dashboard_controller import DashboardController

# 创建派车管理蓝图（挂载到/api/v1/dispatch）
dispatch_bp = Blueprint('dispatch', __name__, url_prefix='/dispatch')

# 派车任务列表路由
dispatch_bp.route('/tasks', methods=['GET'])(DispatchController.get_dispatch_task_list)

# 派车任务详情路由
dispatch_bp.route('/tasks/<string:task_id>', methods=['GET'])(DispatchController.get_dispatch_task_detail)

# 创建派车任务路由
dispatch_bp.route('/tasks', methods=['POST'])(DispatchController.create_dispatch_task)

# 更新派车任务路由
dispatch_bp.route('/tasks/<string:task_id>', methods=['PUT'])(DispatchController.update_dispatch_task)

# 审核派车任务路由
dispatch_bp.route('/tasks/<string:task_id>/approve', methods=['POST'])(DispatchController.approve_dispatch_task)

# 审核派车任务路由（兼容audit接口）
dispatch_bp.route('/tasks/<string:task_id>/audit', methods=['POST'])(DispatchController.approve_dispatch_task)

# 分配车辆路由
dispatch_bp.route('/tasks/<string:task_id>/assign', methods=['POST'])(DispatchController.assign_vehicle)

# 完成派车任务路由
dispatch_bp.route('/tasks/<string:task_id>/complete', methods=['POST'])(DispatchController.complete_task)

# 获取派车任务状态历史路由
dispatch_bp.route('/tasks/<string:task_id>/status-history', methods=['GET'])(DispatchController.get_task_status_history)

# 获取任务可能的下一个状态
dispatch_bp.route('/tasks/<string:task_id>/next-statuses', methods=['GET'])(DispatchController.get_next_possible_statuses)

# 获取任务操作日志
dispatch_bp.route('/tasks/<string:task_id>/operation-logs', methods=['GET'])(DispatchController.get_task_operation_logs)

# 合并车辆路由
dispatch_bp.route('/vehicles/merge', methods=['POST'])(DispatchController.merge_vehicles)

# 降档车辆路由
dispatch_bp.route('/vehicles/<int:vehicle_id>/downgrade', methods=['POST'])(DispatchController.downgrade_vehicle)

# 获取车辆降档历史路由
dispatch_bp.route('/vehicles/<int:vehicle_id>/downgrade-history', methods=['GET'])(DispatchController.get_vehicle_downgrade_history)

# 仪表盘统计概览路由
dispatch_bp.route('/dashboard/statistics', methods=['GET'])(DashboardController.get_dashboard_statistics)

# 仪表盘分布数据路由
dispatch_bp.route('/dashboard/distributions', methods=['GET'])(DashboardController.get_dashboard_distributions)

# 紧急任务列表路由
dispatch_bp.route('/dashboard/urgent-tasks', methods=['GET'])(DashboardController.get_urgent_tasks)

# 完整仪表盘数据路由
dispatch_bp.route('/dashboard/complete', methods=['GET'])(DashboardController.get_complete_dashboard)

# 供应商响应路由
dispatch_bp.route('/tasks/supplier-response', methods=['POST'])(DispatchController.submit_supplier_response)

# 班组派车响应路由
dispatch_bp.route('/tasks/team-response', methods=['POST'])(DispatchController.submit_team_response)

# 外包管理公司响应路由
dispatch_bp.route('/tasks/outsourcing-response', methods=['POST'])(DispatchController.submit_outsourcing_response)