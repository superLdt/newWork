"""remove_supplier_management_menu_id18

Revision ID: 9f12ab34cdef
Revises: 89bf959e3602
Create Date: 2025-10-07 16:35:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f12ab34cdef'
down_revision = '89bf959e3602'
branch_labels = None
depends_on = None


def upgrade():
    # 递归查找 id=18 的所有子菜单，并删除其权限关联与菜单记录
    op.execute(
        """
        WITH RECURSIVE menu_tree AS (
            SELECT id FROM Menu WHERE id = 18
            UNION ALL
            SELECT m.id FROM Menu m JOIN menu_tree mt ON m.parent_id = mt.id
        )
        DELETE FROM MenuPermission WHERE menu_id IN (SELECT id FROM menu_tree);
        """
    )
    op.execute(
        """
        WITH RECURSIVE menu_tree AS (
            SELECT id FROM Menu WHERE id = 18
            UNION ALL
            SELECT m.id FROM Menu m JOIN menu_tree mt ON m.parent_id = mt.id
        )
        DELETE FROM Menu WHERE id IN (SELECT id FROM menu_tree);
        """
    )


def downgrade():
    # 恢复供应商管理菜单的基础记录（不恢复关联权限）
    op.execute(
        """
        INSERT INTO Menu (id, name, code, path, component, icon, parent_id, sort_order, is_active, created_at, updated_at)
        VALUES (18, '供应商管理', 'supplier_management', '/supplier', NULL, 'supplier', NULL, 50, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
    )