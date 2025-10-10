"""Update company table to dispatch_unit and modify vehicle table

Revision ID: update_company_to_dispatch_unit
Revises: 
Create Date: 2025-01-13 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'update_company_to_dispatch_unit'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### 创建新的派车单位表 ###
    op.create_table('dispatch_units',
        sa.Column('id', sa.Integer(), nullable=False, comment='派车单位唯一ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='派车单位名称'),
        sa.Column('unit_type', sa.String(length=50), nullable=True, comment='单位类型（供应商/内部单位）'),
        sa.Column('bank_name', sa.String(length=100), nullable=True, comment='银行名称'),
        sa.Column('account_number', sa.String(length=50), nullable=True, comment='银行账号'),
        sa.Column('address', sa.String(length=200), nullable=True, comment='单位地址'),
        sa.Column('contact_person', sa.String(length=50), nullable=True, comment='联系人'),
        sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='联系电话'),
        sa.Column('email', sa.String(length=120), nullable=True, comment='邮箱'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # ### 迁移Company表数据到dispatch_units表 ###
    # 首先检查Company表是否存在
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'Company' in inspector.get_table_names():
        # 迁移数据
        op.execute("""
            INSERT INTO dispatch_units (id, name, unit_type, bank_name, account_number, address, contact_person, contact_phone, is_active, created_at, updated_at)
            SELECT id, name, '供应商' as unit_type, bank_name, account_number, address, contact_person, contact_phone, 1 as is_active, created_at, updated_at
            FROM Company
        """)
    
    # ### 更新User表的外键引用 ###
    # 创建临时表
    op.create_table('User_temp',
        sa.Column('id', sa.Integer(), nullable=False, comment='用户唯一ID'),
        sa.Column('username', sa.String(length=80), nullable=False, comment='用户名'),
        sa.Column('password', sa.String(length=128), nullable=False, comment='密码（加密存储）'),
        sa.Column('full_name', sa.String(length=100), nullable=True, comment='姓名'),
        sa.Column('email', sa.String(length=120), nullable=True, comment='邮箱'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='手机号'),
        sa.Column('dispatch_unit_id', sa.Integer(), nullable=True, comment='所属派车单位ID'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.ForeignKeyConstraint(['dispatch_unit_id'], ['dispatch_units.id'], )
    )
    
    # 迁移User表数据
    if 'User' in inspector.get_table_names():
        op.execute("""
            INSERT INTO User_temp (id, username, password, full_name, email, phone, dispatch_unit_id, is_active, created_at, updated_at)
            SELECT id, username, password, full_name, email, phone, company_id as dispatch_unit_id, is_active, created_at, updated_at
            FROM User
        """)
    
    # 删除旧的User表
    op.drop_table('User')
    
    # 重命名临时表
    op.rename_table('User_temp', 'User')
    
    # ### 更新vehicles表结构 ###
    # 创建临时表
    op.create_table('vehicles_temp',
        sa.Column('id', sa.Integer(), nullable=False, comment='车辆唯一ID'),
        sa.Column('task_id', sa.String(length=50), nullable=True, comment='关联任务ID'),
        sa.Column('manifest_number', sa.String(length=50), nullable=True, comment='路单流水号'),
        sa.Column('dispatch_number', sa.String(length=50), nullable=True, comment='派车单号'),
        sa.Column('license_plate', sa.String(length=20), nullable=True, comment='车牌号'),
        sa.Column('carriage_number', sa.String(length=50), nullable=True, comment='车厢号'),
        sa.Column('created_at', sa.String(length=20), nullable=True, comment='创建时间'),
        sa.Column('notes', sa.Text(), nullable=True, comment='备注'),
        sa.Column('actual_volume', sa.Float(), nullable=True, comment='实际容积'),
        sa.Column('volume_photo_url', sa.String(length=200), nullable=True, comment='容积照片URL'),
        sa.Column('volume_modified_by', sa.Integer(), nullable=True, comment='容积修改人'),
        sa.Column('required_volume', sa.Float(), nullable=True, comment='需求容积'),
        sa.Column('confirmed_volume', sa.Float(), nullable=True, comment='确认容积'),
        sa.Column('vehicle_type', sa.String(length=20), nullable=True, comment='车辆类型'),
        sa.Column('supplier_id', sa.Integer(), nullable=True, comment='供应商ID'),
        sa.Column('supplier_type', sa.String(length=50), nullable=True, comment='供应商类型'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='车辆状态'),
        sa.Column('confirmed_by', sa.Integer(), nullable=True, comment='确认人ID'),
        sa.Column('confirmed_at', sa.String(length=20), nullable=True, comment='确认时间'),
        sa.Column('is_merged', sa.Boolean(), nullable=True, comment='是否已合并'),
        sa.Column('is_downgraded', sa.Boolean(), nullable=True, comment='是否已降档'),
        sa.Column('original_capacity', sa.Float(), nullable=True, comment='原始容积'),
        sa.Column('updated_at', sa.String(length=20), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['manual_dispatch_tasks.task_id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['dispatch_units.id'], )
    )
    
    # 迁移vehicles表数据（移除司机相关字段）
    if 'vehicles' in inspector.get_table_names():
        op.execute("""
            INSERT INTO vehicles_temp (id, task_id, manifest_number, dispatch_number, license_plate, carriage_number, created_at, notes, actual_volume, volume_photo_url, volume_modified_by, required_volume, confirmed_volume, vehicle_type, supplier_id, supplier_type, status, confirmed_by, confirmed_at, is_merged, is_downgraded, original_capacity, updated_at)
            SELECT id, task_id, manifest_number, dispatch_number, license_plate, carriage_number, created_at, notes, actual_volume, volume_photo_url, volume_modified_by, required_volume, confirmed_volume, vehicle_type, supplier_id, supplier_type, status, confirmed_by, confirmed_at, is_merged, is_downgraded, original_capacity, updated_at
            FROM vehicles
        """)
    
    # 删除旧的vehicles表
    op.drop_table('vehicles')
    
    # 重命名临时表
    op.rename_table('vehicles_temp', 'vehicles')
    
    # ### 删除旧的Company表 ###
    if 'Company' in inspector.get_table_names():
        op.drop_table('Company')


def downgrade():
    # ### 回滚操作 ###
    # 重新创建Company表
    op.create_table('Company',
        sa.Column('id', sa.Integer(), nullable=False, comment='公司唯一ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='公司名称'),
        sa.Column('bank_name', sa.String(length=100), nullable=True, comment='银行名称'),
        sa.Column('account_number', sa.String(length=50), nullable=True, comment='银行账号'),
        sa.Column('address', sa.String(length=200), nullable=True, comment='公司地址'),
        sa.Column('contact_person', sa.String(length=50), nullable=True, comment='联系人'),
        sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='联系电话'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # 迁移数据回Company表
    op.execute("""
        INSERT INTO Company (id, name, bank_name, account_number, address, contact_person, contact_phone, created_at, updated_at)
        SELECT id, name, bank_name, account_number, address, contact_person, contact_phone, created_at, updated_at
        FROM dispatch_units
    """)
    
    # 回滚User表
    op.create_table('User_old',
        sa.Column('id', sa.Integer(), nullable=False, comment='用户唯一ID'),
        sa.Column('username', sa.String(length=80), nullable=False, comment='用户名'),
        sa.Column('password', sa.String(length=128), nullable=False, comment='密码（加密存储）'),
        sa.Column('full_name', sa.String(length=100), nullable=True, comment='姓名'),
        sa.Column('email', sa.String(length=120), nullable=True, comment='邮箱'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='手机号'),
        sa.Column('company_id', sa.Integer(), nullable=True, comment='所属公司ID'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.ForeignKeyConstraint(['company_id'], ['Company.id'], )
    )
    
    op.execute("""
        INSERT INTO User_old (id, username, password, full_name, email, phone, company_id, is_active, created_at, updated_at)
        SELECT id, username, password, full_name, email, phone, dispatch_unit_id as company_id, is_active, created_at, updated_at
        FROM User
    """)
    
    op.drop_table('User')
    op.rename_table('User_old', 'User')
    
    # 回滚vehicles表（添加司机字段）
    op.create_table('vehicles_old',
        sa.Column('id', sa.Integer(), nullable=False, comment='车辆唯一ID'),
        sa.Column('task_id', sa.String(length=50), nullable=True, comment='关联任务ID'),
        sa.Column('manifest_number', sa.String(length=50), nullable=True, comment='路单流水号'),
        sa.Column('dispatch_number', sa.String(length=50), nullable=True, comment='派车单号'),
        sa.Column('license_plate', sa.String(length=20), nullable=True, comment='车牌号'),
        sa.Column('carriage_number', sa.String(length=50), nullable=True, comment='车厢号'),
        sa.Column('created_at', sa.String(length=20), nullable=True, comment='创建时间'),
        sa.Column('notes', sa.Text(), nullable=True, comment='备注'),
        sa.Column('actual_volume', sa.Float(), nullable=True, comment='实际容积'),
        sa.Column('volume_photo_url', sa.String(length=200), nullable=True, comment='容积照片URL'),
        sa.Column('volume_modified_by', sa.Integer(), nullable=True, comment='容积修改人'),
        sa.Column('required_volume', sa.Float(), nullable=True, comment='需求容积'),
        sa.Column('confirmed_volume', sa.Float(), nullable=True, comment='确认容积'),
        sa.Column('vehicle_type', sa.String(length=20), nullable=True, comment='车辆类型'),
        sa.Column('supplier_id', sa.Integer(), nullable=True, comment='供应商ID'),
        sa.Column('supplier_type', sa.String(length=50), nullable=True, comment='供应商类型'),
        sa.Column('driver_name', sa.String(length=50), nullable=True, comment='司机姓名'),
        sa.Column('driver_phone', sa.String(length=20), nullable=True, comment='司机电话'),
        sa.Column('driver_id_card', sa.String(length=20), nullable=True, comment='司机身份证号'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='车辆状态'),
        sa.Column('confirmed_by', sa.Integer(), nullable=True, comment='确认人ID'),
        sa.Column('confirmed_at', sa.String(length=20), nullable=True, comment='确认时间'),
        sa.Column('is_merged', sa.Boolean(), nullable=True, comment='是否已合并'),
        sa.Column('is_downgraded', sa.Boolean(), nullable=True, comment='是否已降档'),
        sa.Column('original_capacity', sa.Float(), nullable=True, comment='原始容积'),
        sa.Column('updated_at', sa.String(length=20), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['manual_dispatch_tasks.task_id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['Company.id'], )
    )
    
    op.execute("""
        INSERT INTO vehicles_old (id, task_id, manifest_number, dispatch_number, license_plate, carriage_number, created_at, notes, actual_volume, volume_photo_url, volume_modified_by, required_volume, confirmed_volume, vehicle_type, supplier_id, supplier_type, status, confirmed_by, confirmed_at, is_merged, is_downgraded, original_capacity, updated_at)
        SELECT id, task_id, manifest_number, dispatch_number, license_plate, carriage_number, created_at, notes, actual_volume, volume_photo_url, volume_modified_by, required_volume, confirmed_volume, vehicle_type, supplier_id, supplier_type, status, confirmed_by, confirmed_at, is_merged, is_downgraded, original_capacity, updated_at
        FROM vehicles
    """)
    
    op.drop_table('vehicles')
    op.rename_table('vehicles_old', 'vehicles')
    
    # 删除dispatch_units表
    op.drop_table('dispatch_units')