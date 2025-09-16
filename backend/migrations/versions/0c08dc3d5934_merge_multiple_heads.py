"""merge multiple heads

Revision ID: 0c08dc3d5934
Revises: 210d056425fb, add_vehicle_task_id_constraint
Create Date: 2025-09-14 17:40:47.388881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c08dc3d5934'
down_revision = ('210d056425fb', 'add_vehicle_task_id_constraint')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
