#!/usr/bin/env python3
"""
智能运输系统后端启动脚本
"""

import os
from app import create_app

# 创建Flask应用实例
app = create_app()

if __name__ == '__main__':
    # 获取端口配置，默认为5000
    port = int(os.environ.get('PORT', 5000))
    
    # 启动开发服务器
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', True)
    )