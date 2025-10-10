#!/usr/bin/env python3
"""
派车单位路由模块
定义派车单位相关的API路由
"""

from flask import Blueprint
from .dispatch_unit_controller import DispatchUnitController

# 创建派车单位管理蓝图
dispatch_unit_bp = Blueprint('dispatch_unit', __name__, url_prefix='/dispatch-units')

# 派车单位列表路由
dispatch_unit_bp.route('/', methods=['GET'])(DispatchUnitController.get_dispatch_unit_list)

# 派车单位详情路由
dispatch_unit_bp.route('/<int:unit_id>', methods=['GET'])(DispatchUnitController.get_dispatch_unit_detail)

# 创建派车单位路由
dispatch_unit_bp.route('/', methods=['POST'])(DispatchUnitController.create_dispatch_unit)

# 更新派车单位路由
dispatch_unit_bp.route('/<int:unit_id>', methods=['PUT'])(DispatchUnitController.update_dispatch_unit)

# 删除派车单位路由
dispatch_unit_bp.route('/<int:unit_id>', methods=['DELETE'])(DispatchUnitController.delete_dispatch_unit)

# 获取激活的派车单位列表路由
dispatch_unit_bp.route('/active', methods=['GET'])(DispatchUnitController.get_active_dispatch_units)