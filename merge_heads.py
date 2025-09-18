#!/usr/bin/env python3
"""
合并Alembic多头部修订
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from alembic import command
from alembic.config import Config

def merge_heads():
    """合并多个alembic头部"""
    app = create_app()
    
    with app.app_context():
        # 配置alembic
        config = Config('migrations/alembic.ini')
        config.set_main_option('script_location', 'migrations')
        
        try:
            # 合并头部
            command.merge(config, ['210d056425fb', 'add_vehicle_task_id_constraint'], 
                         message='merge multiple heads')
            print("Successfully merged multiple heads")
        except Exception as e:
            print(f"Error merging heads: {e}")
            return False
    
    return True

if __name__ == '__main__':
    success = merge_heads()
    sys.exit(0 if success else 1)