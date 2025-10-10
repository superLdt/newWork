"""merge heads

Revision ID: 210d056425fb
Revises: ca6e10835313, update_company_to_dispatch_unit
Create Date: 2025-09-13 19:10:07.779513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '210d056425fb'
down_revision = ('ca6e10835313', 'update_company_to_dispatch_unit')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
