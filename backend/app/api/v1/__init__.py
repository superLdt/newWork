#!/usr/bin/env python3
"""
API v1模块包初始化文件

包含API v1版本的所有路由
"""

from flask import Blueprint

# 创建API v1蓝图
api_v1_bp = Blueprint('api_v1_bp', __name__, url_prefix='/api/v1')

# 导入路由模块
from . import user_management, role_management