#!/usr/bin/env python3
"""
智能运力系统扩展初始化模块
集中管理所有Flask扩展的初始化
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# 数据库ORM
db = SQLAlchemy()

# JWT认证管理
jwt = JWTManager()

# 数据库迁移管理
migrate = Migrate()

# 可以在这里添加其他扩展的初始化
# 例如：缓存、邮件、任务队列等

def init_extensions(app):
    """
    初始化所有Flask扩展
    
    Args:
        app: Flask应用实例
    """
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # 可以在这里初始化其他扩展
    # cache.init_app(app)
    # mail.init_app(app)
    
    return app