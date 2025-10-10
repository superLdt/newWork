#!/usr/bin/env python3
"""
基础数据模块包初始化文件

包含基础数据管理的API路由和业务逻辑
"""

from flask import Blueprint

# 创建基础数据蓝图
basic_data_bp = Blueprint('basic_data_bp', __name__)

# 导入路由模块
from . import routes