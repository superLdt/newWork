"""drop_operation_attachments_table

Revision ID: aae937d6b897
Revises: 553a2a22756a
Create Date: 2025-10-05 10:00:20.596061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aae937d6b897'
down_revision = '553a2a22756a'
branch_labels = None
depends_on = None


def upgrade():
    # 删除operation_attachments表
    op.drop_table('operation_attachments')


def downgrade():
    # 恢复operation_attachments表
    op.create_table('operation_attachments',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('operation_type', sa.VARCHAR(length=20), nullable=False),
        sa.Column('operation_id', sa.INTEGER(), nullable=False),
        sa.Column('attachment_type', sa.VARCHAR(length=50), nullable=True),
        sa.Column('file_name', sa.VARCHAR(length=255), nullable=False),
        sa.Column('file_path', sa.VARCHAR(length=500), nullable=False),
        sa.Column('file_size', sa.INTEGER(), nullable=True),
        sa.Column('mime_type', sa.VARCHAR(length=100), nullable=True),
        sa.Column('upload_time', sa.DATETIME(), nullable=True),
        sa.Column('uploaded_by', sa.INTEGER(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_operation_attachments_operation', 'operation_attachments', ['operation_type', 'operation_id'], unique=False)
    op.create_index('idx_operation_attachments_upload_time', 'operation_attachments', ['upload_time'], unique=False)
