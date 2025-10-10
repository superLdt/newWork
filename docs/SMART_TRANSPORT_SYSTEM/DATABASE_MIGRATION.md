# 人工派车流程系统 - 数据库迁移设计

## 1. 数据库迁移概述

为了支持人工派车流程系统的多角色权限管理和流程控制，需要对现有数据库进行迁移，主要包括以下几个方面：

1. **权限表扩展**：添加新的权限项，支持多角色权限管理
2. **任务表扩展**：扩展派车任务表，增加流程控制相关字段
3. **车辆表扩展**：扩展车辆信息表，增加合并和降档相关字段
4. **新增表**：添加车辆合并记录表、降档记录表等新表

## 2. 数据库迁移脚本

### 2.1 权限表迁移

```sql
-- 添加新的权限项
INSERT INTO permissions (code, name, description, category) VALUES
('task:create', '创建派车任务', '允许创建新的派车任务', '任务管理'),
('task:read', '查看派车任务', '允许查看派车任务列表和详情', '任务管理'),
('task:update', '更新派车任务', '允许更新派车任务信息', '任务管理'),
('task:delete', '删除派车任务', '允许删除派车任务', '任务管理'),
('vehicle:create', '创建车辆', '允许创建新的车辆信息', '车辆管理'),
('vehicle:read', '查看车辆', '允许查看车辆信息', '车辆管理'),
('vehicle:update', '更新车辆', '允许更新车辆基本信息', '车辆管理'),
('audit:submit', '提交审核', '允许提交派车任务审核', '审核流程'),
('audit:approve', '审核通过', '允许审核通过派车任务', '审核流程'),
('audit:reject', '审核拒绝', '允许审核拒绝派车任务', '审核流程'),
('supplier:respond', '供应商响应', '允许供应商响应派车任务', '供应商管理'),
('supplier:update_vehicle', '更新车辆信息', '允许供应商更新车辆信息', '供应商管理'),
('workshop:confirm', '车间确认', '允许车间确认任务完成', '车间管理'),
('workshop:merge_vehicles', '合并车辆', '允许执行车辆合并操作', '车间管理'),
('workshop:downgrade', '降档操作', '允许执行降档操作', '车间管理'),
('workshop:update_volume', '更新车辆容积', '允许更新车辆实际容积信息', '车间管理'),
('menu:vehicle_create', '车辆创建菜单', '允许访问车辆创建菜单', '菜单权限');
```

### 2.2 角色权限关联

```sql
-- 调度员权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'dispatcher' AND p.code IN (
  'task:create', 'task:read', 'task:update', 'task:delete',
  'audit:approve', 'audit:reject',
  'vehicle:create', 'vehicle:read', 'vehicle:update',
  'menu:vehicle_create'
);

-- 车间地调权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'workshop_dispatcher' AND p.code IN (
  'task:create', 'task:read', 'task:update',
  'audit:submit',
  'workshop:confirm', 'workshop:merge_vehicles', 'workshop:downgrade', 'workshop:update_volume',
  'vehicle:read', 'vehicle:update'
);

-- 供应商权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'supplier' AND p.code IN (
  'task:read',
  'supplier:respond', 'supplier:update_vehicle',
  'vehicle:read', 'vehicle:update'
);

-- 班组权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'team' AND p.code IN (
  'task:read',
  'supplier:respond', 'supplier:update_vehicle'
);

-- 承运商权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'carrier' AND p.code IN (
  'task:read',
  'supplier:respond', 'supplier:update_vehicle'
);
```

### 2.3 任务表迁移

```sql
-- 扩展派车任务表
ALTER TABLE manual_dispatch_tasks
ADD COLUMN dispatch_track VARCHAR(50) NOT NULL DEFAULT '轨道A' COMMENT '派车轨道，轨道A需审核，轨道B直接派车',
ADD COLUMN initiator_role VARCHAR(50) COMMENT '发起人角色',
ADD COLUMN initiator_user_id INT COMMENT '发起人用户ID',
ADD COLUMN initiator_department VARCHAR(100) COMMENT '发起部门',
ADD COLUMN audit_required BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否需要审核',
ADD COLUMN assigned_supplier_id INT COMMENT '指定的供应商ID',
ADD COLUMN supplier_type VARCHAR(50) COMMENT '供应商类型，委办公司/班组/承运商',
ADD COLUMN current_handler_role VARCHAR(50) COMMENT '当前处理人角色',
ADD COLUMN is_merged BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否进行了车辆合并操作',
ADD COLUMN is_downgraded BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否进行了降档操作',
ADD COLUMN last_operation_time DATETIME COMMENT '最后操作时间',
ADD COLUMN last_operation_user_id INT COMMENT '最后操作用户ID';
```

### 2.4 车辆表迁移

```sql
-- 扩展车辆信息表
ALTER TABLE vehicles
ADD COLUMN is_merged BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已被合并',
ADD COLUMN merged_to_vehicle_id INT COMMENT '合并到的目标车辆ID',
ADD COLUMN original_capacity FLOAT COMMENT '原始载重量',
ADD COLUMN downgraded_capacity FLOAT COMMENT '降档后载重量',
ADD COLUMN is_downgraded BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已降档',
ADD COLUMN supplier_type VARCHAR(50) COMMENT '供应商类型，委办公司/班组/承运商',
ADD COLUMN supplier_id INT COMMENT '供应商ID',
ADD COLUMN response_time DATETIME COMMENT '响应时间',
ADD COLUMN response_note TEXT COMMENT '响应备注',
ADD COLUMN actual_volume FLOAT COMMENT '实际容积',
ADD COLUMN volume_photo_url VARCHAR(255) COMMENT '容积照片URL',
ADD COLUMN volume_modified_time DATETIME COMMENT '容积修改时间',
ADD COLUMN volume_modified_by INT COMMENT '容积修改人ID',
ADD COLUMN volume_modified_reason TEXT COMMENT '容积修改原因';
```

### 2.5 新增表

#### 2.5.1 车辆合并记录表

```sql
-- 创建车辆合并记录表
CREATE TABLE vehicle_merge_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task_id VARCHAR(50) NOT NULL COMMENT '关联的任务ID',
  source_vehicle_ids VARCHAR(255) NOT NULL COMMENT '源车辆ID列表，逗号分隔',
  target_vehicle_id INT NOT NULL COMMENT '目标车辆ID',
  merge_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '合并时间',
  merge_by INT NOT NULL COMMENT '执行合并的用户ID',
  merge_note TEXT COMMENT '合并备注'
) COMMENT '车辆合并记录表';
```

#### 2.5.2 降档记录表

```sql
-- 创建降档记录表
CREATE TABLE vehicle_downgrade_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL COMMENT '车辆ID',
  task_id VARCHAR(50) NOT NULL COMMENT '关联的任务ID',
  original_capacity FLOAT NOT NULL COMMENT '原始载重量',
  downgraded_capacity FLOAT NOT NULL COMMENT '降档后载重量',
  downgrade_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '降档时间',
  downgrade_by INT NOT NULL COMMENT '执行降档的用户ID',
  downgrade_reason TEXT COMMENT '降档原因'
) COMMENT '车辆降档记录表';
```

#### 2.5.3 车辆容积修改记录表

```sql
-- 创建车辆容积修改记录表
CREATE TABLE vehicle_volume_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL COMMENT '车辆ID',
  task_id VARCHAR(50) NOT NULL COMMENT '关联的任务ID',
  previous_volume FLOAT COMMENT '修改前容积',
  new_volume FLOAT NOT NULL COMMENT '修改后容积',
  photo_url VARCHAR(255) COMMENT '容积照片URL',
  modify_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  modify_by INT NOT NULL COMMENT '修改人ID',
  modify_reason TEXT NOT NULL COMMENT '修改原因',
  approval_document_url VARCHAR(255) COMMENT '审批凭证URL'
) COMMENT '车辆容积修改记录表';
```

#### 2.5.4 操作日志表

```sql
-- 创建操作日志表
CREATE TABLE operation_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task_id VARCHAR(50) NOT NULL COMMENT '关联的任务ID',
  user_id INT NOT NULL COMMENT '操作用户ID',
  user_role VARCHAR(50) NOT NULL COMMENT '操作用户角色',
  operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
  operation_content TEXT COMMENT '操作内容',
  operation_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  ip_address VARCHAR(50) COMMENT '操作IP地址'
) COMMENT '操作日志表';
```

## 3. 数据库迁移执行计划

### 3.1 迁移前准备

1. **备份数据库**：在执行迁移脚本前，对数据库进行完整备份
2. **测试环境验证**：在测试环境中执行迁移脚本，验证迁移结果
3. **制定回滚计划**：准备回滚脚本，以应对迁移失败的情况

### 3.2 迁移执行步骤

1. **停止相关服务**：暂停依赖数据库的服务
2. **执行备份**：执行数据库完整备份
3. **执行迁移脚本**：按顺序执行迁移脚本
   - 执行权限表迁移脚本
   - 执行任务表迁移脚本
   - 执行车辆表迁移脚本
   - 执行新增表脚本
4. **验证迁移结果**：检查数据库结构和数据是否正确
5. **启动服务**：重新启动依赖数据库的服务

### 3.3 回滚计划

如果迁移过程中出现问题，按照以下步骤进行回滚：

1. **停止相关服务**：暂停依赖数据库的服务
2. **执行回滚脚本**：执行预先准备的回滚脚本
3. **恢复备份**：如果回滚脚本执行失败，使用备份恢复数据库
4. **启动服务**：重新启动依赖数据库的服务

## 4. 数据迁移脚本

对于已有数据的迁移，需要执行以下脚本：

```sql
-- 更新现有派车任务的派车轨道和审核标志
UPDATE manual_dispatch_tasks
SET dispatch_track = '轨道A',
    audit_required = TRUE,
    current_handler_role = CASE
      WHEN status = '待审核' THEN '调度员'
      WHEN status = '待供应商响应' THEN '供应商'
      WHEN status = '供应商已响应' THEN '车间地调'
      ELSE NULL
    END;

-- 更新现有车辆信息的供应商类型
UPDATE vehicles v
JOIN manual_dispatch_tasks t ON v.task_id = t.task_id
SET v.supplier_type = t.supplier_type,
    v.supplier_id = t.assigned_supplier_id;

-- 初始化车辆容积信息
UPDATE vehicles
SET actual_volume = original_capacity * 0.95
WHERE actual_volume IS NULL AND original_capacity IS NOT NULL;

-- 创建车辆容积修改记录的初始数据
INSERT INTO vehicle_volume_records (vehicle_id, task_id, previous_volume, new_volume, modify_time, modify_by, modify_reason)
SELECT id, task_id, original_capacity, actual_volume, NOW(), 1, '系统初始化'
FROM vehicles
WHERE actual_volume IS NOT NULL;
```

## 5. 总结

本文档设计了人工派车流程系统的数据库迁移方案，包括权限表扩展、任务表扩展、车辆表扩展和新增表的创建。通过这些迁移，数据库结构将能够支持多角色权限管理和流程控制，为人工派车流程系统提供坚实的数据基础。

在实际执行迁移时，需要严格按照迁移执行计划进行，确保数据安全和系统稳定。同时，需要做好迁移前的准备工作和迁移后的验证工作，以应对可能出现的问题。