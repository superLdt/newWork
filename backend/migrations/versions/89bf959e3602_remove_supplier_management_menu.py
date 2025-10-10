"""remove_supplier_management_menu

Revision ID: 89bf959e3602
Revises: 70e1f79df5cf
Create Date: 2025-10-07 14:08:05.259425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89bf959e3602'
down_revision = '70e1f79df5cf'
branch_labels = None
depends_on = None


def upgrade():
    # 删除供应商管理菜单 (id=16)
    op.execute("DELETE FROM menu WHERE id = 16")


def downgrade():
    # 恢复供应商管理菜单
    op.execute("""
        INSERT INTO menu (id, name, path, parent_id, icon, sort_order, is_active, created_at, updated_at)
        VALUES (16, '供应商管理', 'supplier_management', '/supplier', 'supplier', 100, 1, datetime('now'), datetime('now'))
    """)
