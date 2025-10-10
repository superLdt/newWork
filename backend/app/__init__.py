#!/usr/bin/env python3
"""
智能运力系统Flask应用初始化模块
"""

from flask import Flask
from flask_cors import CORS

# 从扩展模块导入扩展实例
from .extensions import db, jwt, migrate

def create_app(config_name='development'):
    """
    创建Flask应用工厂函数
    
    Args:
        config_name: 配置名称，可选 'development', 'testing', 'production'
    
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    from .config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    from .extensions import init_extensions
    init_extensions(app)
    
    # 启用CORS并应用配置（允许Authorization等预检头，支持凭证）
    CORS(
        app,
        origins=app.config.get('CORS_ORIGINS', '*'),
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Disposition']
    )
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    return app



def register_error_handlers(app):
    """注册错误处理器"""
    # 使用统一的错误处理中间件
    from .common.middleware.error_handler import register_error_handlers as register_app_error_handlers
    register_app_error_handlers(app)


def register_blueprints(app):
    """注册所有蓝图"""
    # 认证模块
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    # 基础数据模块
    from .basic_data import basic_data_bp
    app.register_blueprint(basic_data_bp, url_prefix='/api/v1/basic_data')
    
    # 调度管理模块
    from .dispatch import dispatch_bp
    app.register_blueprint(dispatch_bp, url_prefix='/api/v1/dispatch')
    
    # API v1模块（避免重复加前缀，这里不再额外指定url_prefix）
    from .api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp)