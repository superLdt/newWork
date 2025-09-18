"""merge heads

Revision ID: ce46259aac3c
Revises: 0c08dc3d5934, add_organizing_unit_id
Create Date: 2025-09-17 18:18:51.136847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce46259aac3c'
down_revision = ('0c08dc3d5934', 'add_organizing_unit_id')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
