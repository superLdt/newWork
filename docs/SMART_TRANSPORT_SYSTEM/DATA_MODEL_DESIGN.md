# 人工派车流程系统 - 数据模型设计

## 1. 数据模型概述

人工派车流程系统的数据模型设计基于现有的数据库结构，主要包括以下几个核心模型：

1. **派车任务模型**：记录派车任务的基本信息和状态
2. **车辆信息模型**：记录与派车任务关联的车辆信息
3. **状态历史模型**：记录派车任务状态变更的历史记录
4. **角色权限模型**：管理不同角色的权限
5. **操作记录模型**：记录用户的操作行为

## 2. 核心数据模型

### 2.1 派车任务模型（ManualDispatchTask）

在现有的 `ManualDispatchTask` 模型基础上，增加以下字段：

```python
class ManualDispatchTask(db.Model):
    __tablename__ = 'manual_dispatch_tasks'
    
    # 现有字段
    task_id = db.Column(db.String(50), primary_key=True, comment='任务唯一ID')
    required_date = db.Column(db.String(20), comment='需求日期')
    start_bureau = db.Column(db.String(100), comment='起始站段')
    route_direction = db.Column(db.String(50), comment='路线方向')
    carrier_company = db.Column(db.String(100), comment='运输公司')
    route_name = db.Column(db.String(100), comment='路线名称')
    transport_type = db.Column(db.String(50), comment='运输类型')
    requirement_type = db.Column(db.String(50), comment='需求类型')
    volume = db.Column(db.Integer, comment='需求容积')
    weight = db.Column(db.Float, comment='需求重量')
    special_requirements = db.Column(db.Text, comment='特殊要求')
    status = db.Column(db.String(20), default='待审核', comment='任务状态')
    dispatch_track = db.Column(db.String(10), comment='派车轨道')
    initiator_role = db.Column(db.String(50), comment='发起人角色')
    initiator_user_id = db.Column(db.Integer, comment='发起人用户ID')
    initiator_department = db.Column(db.String(100), comment='发起人部门')
    audit_required = db.Column(db.Boolean, default=True, comment='是否需要审核')
    auditor_role = db.Column(db.String(50), comment='审核人角色')
    auditor_user_id = db.Column(db.Integer, comment='审核人用户ID')
    audit_status = db.Column(db.String(20), comment='审核状态')
    audit_time = db.Column(db.String(20), comment='审核时间')
    audit_note = db.Column(db.Text, comment='审核备注')
    current_handler_role = db.Column(db.String(50), comment='当前处理人角色')
    current_handler_user_id = db.Column(db.Integer, comment='当前处理人用户ID')
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='更新时间')
    assigned_supplier_id = db.Column(db.Integer, comment='分配供应商ID')
    
    # 新增字段
    workshop_dispatcher_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='车间地调ID')
    workshop_dispatcher_note = db.Column(db.Text, comment='车间地调备注')
    workshop_confirmation_time = db.Column(db.String(20), comment='车间确认时间')
    supplier_response_time = db.Column(db.String(20), comment='供应商响应时间')
    supplier_note = db.Column(db.Text, comment='供应商备注')
    completion_time = db.Column(db.String(20), comment='完成时间')
    is_merged = db.Column(db.Boolean, default=False, comment='是否合并车辆')
    is_downgraded = db.Column(db.Boolean, default=False, comment='是否降档')
    downgrade_note = db.Column(db.Text, comment='降档说明')
    supplier_type = db.Column(db.String(20), comment='供应商类型：委办公司/班组/承运商')
    
    # 关系定义
    vehicles = db.relationship('Vehicle', backref='task', lazy=True, cascade='all, delete-orphan')
    status_history = db.relationship('DispatchStatusHistory', backref='task', lazy=True, cascade='all, delete-orphan')
    operation_logs = db.relationship('OperationLog', backref='task', lazy=True, cascade='all, delete-orphan')
    
    @classmethod
    def get_status_choices(cls):
        """获取任务状态选项列表"""
        return [
            '待审核', '审核通过', '待供应商响应', 
            '供应商已响应', '任务完成', '审核拒绝'
        ]
    
    @classmethod
    def get_dispatch_track_choices(cls):
        """获取派车轨道选项列表"""
        return ['轨道A', '轨道B']
    
    @classmethod
    def get_supplier_type_choices(cls):
        """获取供应商类型选项列表"""
        return ['委办公司', '班组', '承运商']
```

### 2.2 车辆信息模型（Vehicle）

在现有的 `Vehicle` 模型基础上，增加以下字段：

```python
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    # 现有字段
    id = db.Column(db.Integer, primary_key=True, comment='车辆唯一ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    manifest_number = db.Column(db.String(50), comment='货票号')
    dispatch_number = db.Column(db.String(50), comment='派车单号')
    license_plate = db.Column(db.String(20), comment='车牌号')
    carriage_number = db.Column(db.String(50), comment='车厢号')
    created_at = db.Column(db.String(20), comment='创建时间')
    notes = db.Column(db.Text, comment='备注')
    actual_volume = db.Column(db.Float, comment='实际容积')
    volume_photo_url = db.Column(db.String(200), comment='容积照片URL')
    volume_modified_by = db.Column(db.Integer, comment='容积修改人')
    required_volume = db.Column(db.Float, comment='需求容积')
    confirmed_volume = db.Column(db.Float, comment='确认容积')
    
    # 新增字段
    driver_name = db.Column(db.String(50), comment='司机姓名')
    driver_phone = db.Column(db.String(20), comment='司机电话')
    vehicle_type = db.Column(db.String(50), comment='车辆类型')
    load_capacity = db.Column(db.Float, comment='载重能力')
    supplier_id = db.Column(db.Integer, comment='供应商ID')
    supplier_type = db.Column(db.String(20), comment='供应商类型：委办公司/班组/承运商')
    is_merged = db.Column(db.Boolean, default=False, comment='是否被合并')
    merged_to_vehicle_id = db.Column(db.Integer, comment='合并到的车辆ID')
    is_downgraded = db.Column(db.Boolean, default=False, comment='是否降档')
    original_capacity = db.Column(db.Float, comment='原始容量')
    downgraded_capacity = db.Column(db.Float, comment='降档后容量')
    downgrade_reason = db.Column(db.Text, comment='降档原因')
    downgrade_time = db.Column(db.String(20), comment='降档时间')
    downgrade_by = db.Column(db.Integer, comment='降档操作人ID')
```

### 2.3 状态历史模型（DispatchStatusHistory）

保持现有的 `DispatchStatusHistory` 模型不变：

```python
class DispatchStatusHistory(db.Model):
    __tablename__ = 'dispatch_status_history'
    
    id = db.Column(db.Integer, primary_key=True, comment='历史记录ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    status_change = db.Column(db.String(50), comment='状态变更')
    operator = db.Column(db.String(100), comment='操作人')
    timestamp = db.Column(db.String(20), comment='时间戳')
    note = db.Column(db.Text, comment='备注')
```

### 2.4 操作记录模型（OperationLog）

新增 `OperationLog` 模型，用于记录用户的操作行为：

```python
class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True, comment='日志ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    user_id = db.Column(db.Integer, comment='操作用户ID')
    user_role = db.Column(db.String(50), comment='操作用户角色')
    operation_type = db.Column(db.String(50), comment='操作类型')
    operation_content = db.Column(db.Text, comment='操作内容')
    operation_time = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='操作时间')
    ip_address = db.Column(db.String(50), comment='IP地址')
    
    @classmethod
    def get_operation_type_choices(cls):
        """获取操作类型选项列表"""
        return [
            '创建任务', '更新任务', '删除任务', '提交审核',
            '审核通过', '审核拒绝', '供应商响应', '更新车辆信息',
            '车间确认', '合并车辆', '降档操作', '完成任务'
        ]
```

### 2.5 车辆合并记录模型（VehicleMergeRecord）

新增 `VehicleMergeRecord` 模型，用于记录车辆合并操作：

```python
class VehicleMergeRecord(db.Model):
    __tablename__ = 'vehicle_merge_records'
    
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    task_id = db.Column(db.String(50), db.ForeignKey('manual_dispatch_tasks.task_id'), comment='关联任务ID')
    source_vehicle_ids = db.Column(db.String(200), comment='源车辆ID列表，逗号分隔')
    target_vehicle_id = db.Column(db.Integer, comment='目标车辆ID')
    merge_time = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='合并时间')
    merge_by = db.Column(db.Integer, comment='合并操作人ID')
    merge_note = db.Column(db.Text, comment='合并说明')
```

## 3. 数据关系图

```
+---------------------+       +-------------------+
| ManualDispatchTask  |<----->| Vehicle          |
+---------------------+       +-------------------+
         |                            |
         |                            |
         v                            |
+---------------------+               |
| DispatchStatusHistory|              |
+---------------------+               |
         ^                            |
         |                            |
+---------------------+               |
| OperationLog        |               |
+---------------------+               |
         ^                            |
         |                            |
         |                            v
+---------------------+       +-------------------+
| User                |       | VehicleMergeRecord|
+---------------------+       +-------------------+
         |
         |
         v
+---------------------+
| Role                |
+---------------------+
         |
         |
         v
+---------------------+
| Permission          |
+---------------------+
```

## 4. 数据库迁移脚本

为了实现上述数据模型的变更，需要创建数据库迁移脚本：

```python
# 迁移脚本示例

def upgrade():
    # 为 manual_dispatch_tasks 表添加新字段
    op.add_column('manual_dispatch_tasks', sa.Column('workshop_dispatcher_id', sa.Integer(), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('workshop_dispatcher_note', sa.Text(), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('workshop_confirmation_time', sa.String(20), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('supplier_response_time', sa.String(20), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('supplier_note', sa.Text(), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('completion_time', sa.String(20), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('is_merged', sa.Boolean(), default=False))
    op.add_column('manual_dispatch_tasks', sa.Column('is_downgraded', sa.Boolean(), default=False))
    op.add_column('manual_dispatch_tasks', sa.Column('downgrade_note', sa.Text(), nullable=True))
    op.add_column('manual_dispatch_tasks', sa.Column('supplier_type', sa.String(20), nullable=True))
    op.create_foreign_key('fk_workshop_dispatcher_id', 'manual_dispatch_tasks', 'users', ['workshop_dispatcher_id'], ['id'])
    
    # 为 vehicles 表添加新字段
    op.add_column('vehicles', sa.Column('driver_name', sa.String(50), nullable=True))
    op.add_column('vehicles', sa.Column('driver_phone', sa.String(20), nullable=True))
    op.add_column('vehicles', sa.Column('vehicle_type', sa.String(50), nullable=True))
    op.add_column('vehicles', sa.Column('load_capacity', sa.Float(), nullable=True))
    op.add_column('vehicles', sa.Column('supplier_id', sa.Integer(), nullable=True))
    op.add_column('vehicles', sa.Column('supplier_type', sa.String(20), nullable=True))
    op.add_column('vehicles', sa.Column('is_merged', sa.Boolean(), default=False))
    op.add_column('vehicles', sa.Column('merged_to_vehicle_id', sa.Integer(), nullable=True))
    op.add_column('vehicles', sa.Column('is_downgraded', sa.Boolean(), default=False))
    op.add_column('vehicles', sa.Column('original_capacity', sa.Float(), nullable=True))
    op.add_column('vehicles', sa.Column('downgraded_capacity', sa.Float(), nullable=True))
    op.add_column('vehicles', sa.Column('downgrade_reason', sa.Text(), nullable=True))
    op.add_column('vehicles', sa.Column('downgrade_time', sa.String(20), nullable=True))
    op.add_column('vehicles', sa.Column('downgrade_by', sa.Integer(), nullable=True))
    
    # 创建 operation_logs 表
    op.create_table(
        'operation_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.String(50), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_role', sa.String(50), nullable=True),
        sa.Column('operation_type', sa.String(50), nullable=True),
        sa.Column('operation_content', sa.Text(), nullable=True),
        sa.Column('operation_time', sa.String(20), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['manual_dispatch_tasks.task_id'], name='fk_operation_logs_task_id')
    )
    
    # 创建 vehicle_merge_records 表
    op.create_table(
        'vehicle_merge_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.String(50), nullable=True),
        sa.Column('source_vehicle_ids', sa.String(200), nullable=True),
        sa.Column('target_vehicle_id', sa.Integer(), nullable=True),
        sa.Column('merge_time', sa.String(20), nullable=True),
        sa.Column('merge_by', sa.Integer(), nullable=True),
        sa.Column('merge_note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['manual_dispatch_tasks.task_id'], name='fk_vehicle_merge_records_task_id')
    )

def downgrade():
    # 删除外键约束
    op.drop_constraint('fk_workshop_dispatcher_id', 'manual_dispatch_tasks', type_='foreignkey')
    op.drop_constraint('fk_operation_logs_task_id', 'operation_logs', type_='foreignkey')
    op.drop_constraint('fk_vehicle_merge_records_task_id', 'vehicle_merge_records', type_='foreignkey')
    
    # 删除表
    op.drop_table('operation_logs')
    op.drop_table('vehicle_merge_records')
    
    # 删除 manual_dispatch_tasks 表的新字段
    op.drop_column('manual_dispatch_tasks', 'workshop_dispatcher_id')
    op.drop_column('manual_dispatch_tasks', 'workshop_dispatcher_note')
    op.drop_column('manual_dispatch_tasks', 'workshop_confirmation_time')
    op.drop_column('manual_dispatch_tasks', 'supplier_response_time')
    op.drop_column('manual_dispatch_tasks', 'supplier_note')
    op.drop_column('manual_dispatch_tasks', 'completion_time')
    op.drop_column('manual_dispatch_tasks', 'is_merged')
    op.drop_column('manual_dispatch_tasks', 'is_downgraded')
    op.drop_column('manual_dispatch_tasks', 'downgrade_note')
    op.drop_column('manual_dispatch_tasks', 'supplier_type')
    
    # 删除 vehicles 表的新字段
    op.drop_column('vehicles', 'driver_name')
    op.drop_column('vehicles', 'driver_phone')
    op.drop_column('vehicles', 'vehicle_type')
    op.drop_column('vehicles', 'load_capacity')
    op.drop_column('vehicles', 'supplier_id')
    op.drop_column('vehicles', 'supplier_type')
    op.drop_column('vehicles', 'is_merged')
    op.drop_column('vehicles', 'merged_to_vehicle_id')
    op.drop_column('vehicles', 'is_downgraded')
    op.drop_column('vehicles', 'original_capacity')
    op.drop_column('vehicles', 'downgraded_capacity')
    op.drop_column('vehicles', 'downgrade_reason')
    op.drop_column('vehicles', 'downgrade_time')
    op.drop_column('vehicles', 'downgrade_by')
```

## 5. 数据模型使用示例

### 5.1 创建派车任务

```python
def create_dispatch_task(data, user_id, user_role):
    # 生成任务ID
    task_id = generate_task_id()
    
    # 确定派车轨道和初始状态
    dispatch_track = data.get('dispatch_track')
    initial_status = '待审核' if dispatch_track == '轨道A' else '待供应商响应'
    
    # 创建任务
    task = ManualDispatchTask(
        task_id=task_id,
        required_date=data.get('required_date'),
        start_bureau=data.get('start_bureau'),
        route_direction=data.get('route_direction'),
        carrier_company=data.get('carrier_company'),
        route_name=data.get('route_name'),
        transport_type=data.get('transport_type'),
        requirement_type=data.get('requirement_type'),
        volume=data.get('volume'),
        weight=data.get('weight'),
        special_requirements=data.get('special_requirements'),
        status=initial_status,
        dispatch_track=dispatch_track,
        initiator_role=user_role,
        initiator_user_id=user_id,
        initiator_department=data.get('initiator_department'),
        audit_required=(dispatch_track == '轨道A'),
        assigned_supplier_id=data.get('assigned_supplier_id'),
        supplier_type=data.get('supplier_type')
    )
    
    db.session.add(task)
    
    # 记录状态历史
    status_history = DispatchStatusHistory(
        task_id=task_id,
        status_change=f'创建任务，初始状态：{initial_status}',
        operator=f'用户ID: {user_id}, 角色: {user_role}',
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        note='任务创建'
    )
    db.session.add(status_history)
    
    # 记录操作日志
    operation_log = OperationLog(
        task_id=task_id,
        user_id=user_id,
        user_role=user_role,
        operation_type='创建任务',
        operation_content=f'创建派车任务，任务ID：{task_id}',
        ip_address=get_client_ip()
    )
    db.session.add(operation_log)
    
    db.session.commit()
    return task
```

### 5.2 车辆合并操作

```python
def merge_vehicles(task_id, source_vehicle_ids, target_vehicle_id, user_id, user_role, merge_note):
    # 检查权限
    if user_role != 'workshop_dispatcher':
        return {'success': False, 'message': '只有车间地调可以执行车辆合并操作'}
    
    # 获取任务
    task = ManualDispatchTask.query.get(task_id)
    if not task:
        return {'success': False, 'message': '任务不存在'}
    
    # 检查任务状态
    if task.status != '供应商已响应':
        return {'success': False, 'message': '只有在供应商已响应状态下才能执行车辆合并操作'}
    
    # 获取源车辆
    source_vehicles = Vehicle.query.filter(Vehicle.id.in_(source_vehicle_ids)).all()
    if len(source_vehicles) != len(source_vehicle_ids):
        return {'success': False, 'message': '部分车辆不存在'}
    
    # 获取目标车辆
    target_vehicle = Vehicle.query.get(target_vehicle_id)
    if not target_vehicle:
        return {'success': False, 'message': '目标车辆不存在'}
    
    # 执行合并操作
    total_volume = target_vehicle.actual_volume
    for vehicle in source_vehicles:
        total_volume += vehicle.actual_volume
        vehicle.is_merged = True
        vehicle.merged_to_vehicle_id = target_vehicle_id
    
    # 更新目标车辆容积
    target_vehicle.actual_volume = total_volume
    
    # 更新任务状态
    task.is_merged = True
    
    # 记录合并操作
    merge_record = VehicleMergeRecord(
        task_id=task_id,
        source_vehicle_ids=','.join(map(str, source_vehicle_ids)),
        target_vehicle_id=target_vehicle_id,
        merge_by=user_id,
        merge_note=merge_note
    )
    db.session.add(merge_record)
    
    # 记录操作日志
    operation_log = OperationLog(
        task_id=task_id,
        user_id=user_id,
        user_role=user_role,
        operation_type='合并车辆',
        operation_content=f'合并车辆，源车辆ID：{source_vehicle_ids}，目标车辆ID：{target_vehicle_id}',
        ip_address=get_client_ip()
    )
    db.session.add(operation_log)
    
    db.session.commit()
    return {'success': True, 'message': '车辆合并成功'}
```

## 6. 总结

本文档设计了人工派车流程系统的数据模型，包括派车任务模型、车辆信息模型、状态历史模型、操作记录模型和车辆合并记录模型。这些模型共同构成了完整的派车流程数据体系，支持多角色协作完成派车任务。

在实际实现过程中，需要根据具体业务需求进行调整和优化，确保数据模型能够满足业务需求，并保持良好的性能和可维护性。