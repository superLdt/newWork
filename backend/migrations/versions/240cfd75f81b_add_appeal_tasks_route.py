"""add_appeal_tasks_route

Revision ID: 240cfd75f81b
Revises: 89bf959e3602
Create Date: 2025-10-07 14:11:29.065710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '240cfd75f81b'
down_revision = '89bf959e3602'
branch_labels = None
depends_on = None


def upgrade():
    # 更新申诉任务管理菜单路径，将其移动到调度管理下
    op.execute("""
        UPDATE menu 
        SET path = '/dispatch/appeal-tasks', parent_id = 2 
        WHERE id = 17
    """)


def downgrade():
    # 恢复申诉任务管理菜单到原来的路径
    op.execute("""
        UPDATE menu 
        SET path = '/supplier/appeal-tasks', parent_id = 16 
        WHERE id = 17
    """)
