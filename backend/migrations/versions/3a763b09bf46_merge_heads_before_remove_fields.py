"""merge_heads_before_remove_fields

Revision ID: 3a763b09bf46
Revises: add_next_handler_role, e99179c55348
Create Date: 2025-09-23 16:42:34.413669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a763b09bf46'
down_revision = ('add_next_handler_role', 'e99179c55348')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
