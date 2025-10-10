"""合并多个头部版本

Revision ID: 8cc0ef138595
Revises: 32e365216ced, updated_business_type_field
Create Date: 2025-10-03 10:43:47.918607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cc0ef138595'
down_revision = ('32e365216ced', 'updated_business_type_field')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
