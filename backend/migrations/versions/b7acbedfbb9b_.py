"""empty message

Revision ID: b7acbedfbb9b
Revises: 76a79e85fe75, create_vehicle_tonnage_volume_mapping
Create Date: 2025-09-20 18:38:53.737553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7acbedfbb9b'
down_revision = ('76a79e85fe75', 'create_vehicle_tonnage_volume_mapping')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
