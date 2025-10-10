"""empty message

Revision ID: 76a79e85fe75
Revises: add_task_vehicle_unique_constraint, ce46259aac3c
Create Date: 2025-09-20 18:08:14.489528

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76a79e85fe75'
down_revision = ('add_task_vehicle_unique_constraint', 'ce46259aac3c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
