#!/usr/bin/env python3
"""
用户管理路由模块
定义用户管理相关的API路由
"""

from flask import Blueprint
from .user_management_controller import UserManagementController

# 创建用户管理蓝图
user_management_bp = Blueprint('user_management', __name__, url_prefix='/users')

# 用户列表路由
user_management_bp.route('/', methods=['GET'])(UserManagementController.get_user_list)

# 用户详情路由
user_management_bp.route('/<int:user_id>', methods=['GET'])(UserManagementController.get_user_detail)

# 创建用户路由
user_management_bp.route('/', methods=['POST'])(UserManagementController.create_user)

# 更新用户路由
user_management_bp.route('/<int:user_id>', methods=['PUT'])(UserManagementController.update_user)

# 删除用户路由
user_management_bp.route('/<int:user_id>', methods=['DELETE'])(UserManagementController.delete_user)

# 绑定用户到派车单位路由
user_management_bp.route('/<int:user_id>/bind-dispatch-unit', methods=['POST'])(UserManagementController.bind_user_to_dispatch_unit)

# 根据派车单位获取用户列表路由
user_management_bp.route('/by-dispatch-unit/<int:dispatch_unit_id>', methods=['GET'])(UserManagementController.get_users_by_dispatch_unit)