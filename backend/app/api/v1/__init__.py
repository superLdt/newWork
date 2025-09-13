#!/usr/bin/env python3
"""
API v1模块包初始化文件

包含API v1版本的所有路由
"""

from flask import Blueprint

# 创建API v1蓝图
api_v1_bp = Blueprint('api_v1_bp', __name__, url_prefix='/api/v1')

# 导入路由模块
from . import user_management, permission_management, menu_management, role_permission_management
from .role_management import role_bp
from .vehicle import vehicle_bp
from .dispatch import dispatch_bp
from .dispatch_unit_routes import dispatch_unit_bp
from .user_management_routes import user_management_bp

# 注册所有API蓝图
api_v1_bp.register_blueprint(permission_management.bp)
api_v1_bp.register_blueprint(menu_management.bp)
api_v1_bp.register_blueprint(role_permission_management.bp)
api_v1_bp.register_blueprint(role_management.role_bp)
api_v1_bp.register_blueprint(vehicle_bp)
api_v1_bp.register_blueprint(dispatch_bp)
api_v1_bp.register_blueprint(dispatch_unit_bp)
api_v1_bp.register_blueprint(user_management_bp)