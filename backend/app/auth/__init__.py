#!/usr/bin/env python3
"""
认证模块包初始化文件

包含认证相关的API路由和业务逻辑
"""

from flask import Blueprint

# 创建认证蓝图
auth_bp = Blueprint('auth_bp', __name__)

# 导入路由模块
from . import routes