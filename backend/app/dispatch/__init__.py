#!/usr/bin/env python3
"""
调度管理模块包初始化文件

包含运输调度相关的API路由和业务逻辑
"""

from flask import Blueprint

# 创建调度管理蓝图
dispatch_bp = Blueprint('dispatch_bp', __name__)

# 导入路由模块
from . import routes