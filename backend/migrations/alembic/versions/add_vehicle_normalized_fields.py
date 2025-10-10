"""
添加车辆标准化字段

Revision ID: 20240101_add_vehicle_normalized_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20240101_add_vehicle_normalized_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """添加车辆标准化字段"""
    # 添加标准化车牌号字段
    op.add_column('vehicles', sa.Column('normalized_license_plate', sa.String(20), nullable=True, comment='标准化车牌号'))
    
    # 添加运力评分字段
    op.add_column('vehicles', sa.Column('capacity_score', sa.Float(), nullable=True, comment='运力评分'))
    
    # 添加供应商分类字段
    op.add_column('vehicles', sa.Column('supplier_category', sa.String(50), nullable=True, comment='供应商分类'))
    
    # 添加创建时间字段
    op.add_column('vehicles', sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'))
    
    # 添加更新时间字段
    op.add_column('vehicles', sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'))
    
    # 创建索引提高查询性能
    op.create_index('ix_vehicles_normalized_license_plate', 'vehicles', ['normalized_license_plate'])
    op.create_index('ix_vehicles_capacity_score', 'vehicles', ['capacity_score'])
    op.create_index('ix_vehicles_supplier_category', 'vehicles', ['supplier_category'])


def downgrade():
    """回滚车辆标准化字段"""
    # 删除索引
    op.drop_index('ix_vehicles_normalized_license_plate', table_name='vehicles')
    op.drop_index('ix_vehicles_capacity_score', table_name='vehicles')
    op.drop_index('ix_vehicles_supplier_category', table_name='vehicles')
    
    # 删除字段
    op.drop_column('vehicles', 'normalized_license_plate')
    op.drop_column('vehicles', 'capacity_score')
    op.drop_column('vehicles', 'supplier_category')
    op.drop_column('vehicles', 'created_at')
    op.drop_column('vehicles', 'updated_at')