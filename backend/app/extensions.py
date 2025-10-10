#!/usr/bin/env python3
"""
智能运力系统扩展初始化模块
集中管理所有Flask扩展的初始化
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

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
    migrate.init_app(app, db, render_as_batch=True)
    
    # 可以在这里初始化其他扩展
    # cache.init_app(app)
    # mail.init_app(app)
    
    return app

# 新增：为 get_current_user 提供用户查找回调
@jwt.user_lookup_loader
def load_user_from_jwt(_jwt_header, jwt_data):
    """根据 JWT 中的身份标识加载用户，用于 flask_jwt_extended.get_current_user()。"""
    try:
        identity = jwt_data.get("sub")
        if identity is None:
            return None
        # 延迟导入以避免循环依赖
        from app.models.user import User
        # 身份在登录时以 str(user.id) 存储，这里兼容转换
        try:
            identity = int(identity)
        except Exception:
            pass
        return User.query.get(identity)
    except Exception:
        return None