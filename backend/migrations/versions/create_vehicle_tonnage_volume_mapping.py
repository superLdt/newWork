"""创建车辆吨位-容积对应表

Revision ID: create_vehicle_tonnage_volume_mapping
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_vehicle_tonnage_volume_mapping'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """创建车辆吨位-容积对应表"""
    op.create_table('vehicle_tonnage_volume_mapping',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('tonnage', sa.String(20), nullable=False, comment='标准吨位，如：5吨、8吨、12吨、20吨、30吨、40吨A、40吨B'),
        sa.Column('min_volume', sa.Float(), nullable=False, comment='最小容积要求(m³)'),
        sa.Column('standard_volume', sa.Float(), nullable=False, comment='标准容积(m³)'),
        sa.Column('max_volume', sa.Float(), nullable=True, comment='最大容积限制(m³)，可为空表示无上限'),
        sa.Column('conversion_factor', sa.Float(), nullable=False, comment='容积折算系数'),
        sa.Column('vehicle_grade', sa.String(10), nullable=False, comment='车辆档位等级'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否启用'),
        sa.Column('created_at', sa.String(20), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.String(20), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tonnage')
    )
    
    # 插入默认数据
    op.execute("""
        INSERT INTO vehicle_tonnage_volume_mapping 
        (tonnage, min_volume, standard_volume, max_volume, conversion_factor, vehicle_grade, is_active, created_at, updated_at)
        VALUES 
        ('5吨', 35.0, 35.0, 44.0, 0.45, 'A', 1, datetime('now'), datetime('now')),
        ('8吨', 45.0, 45.0, 54.0, 0.51, 'B', 1, datetime('now'), datetime('now')),
        ('12吨', 55.0, 55.0, 99.0, 0.63, 'C', 1, datetime('now'), datetime('now')),
        ('20吨', 100.0, 100.0, 129.0, 0.83, 'D', 1, datetime('now'), datetime('now')),
        ('30吨', 130.0, 130.0, 149.0, 1.00, 'E', 1, datetime('now'), datetime('now')),
        ('40吨A', 150.0, 150.0, 179.0, 1.12, 'F', 1, datetime('now'), datetime('now')),
        ('40吨B', 180.0, 180.0, NULL, 1.23, 'G', 1, datetime('now'), datetime('now'))
    """)


def downgrade():
    """删除车辆吨位-容积对应表"""
    op.drop_table('vehicle_tonnage_volume_mapping')