# 智能运力系统 - 数据库设计文档

## 1. 数据库架构概览

智能运力系统采用关系型数据库设计，支持双轨派车流程和基于角色的访问控制。数据库包含派车任务管理、车辆信息、状态流转历史、用户权限和公司管理等核心功能模块。

## 2. 双轨派车流程概述

### 2.1 轨道A流程（需要审核）
1. **任务创建**：车间地调或区域调度员创建任务
2. **待调度员审核**：任务进入审核状态
3. **审核通过**：区域调度员审核通过后，任务进入待供应商响应状态
4. **供应商响应**：供应商确认并填写车辆信息
5. **任务完成**：任务执行完成

### 2.2 轨道B流程（直接派车）
1. **任务创建**：区域调度员或超级管理员创建任务
2. **待供应商响应**：任务直接进入待供应商响应状态
3. **供应商响应**：供应商确认并填写车辆信息
4. **任务完成**：任务执行完成

## 3. 主要表结构设计

### 3.1 派车任务表（manual_dispatch_tasks）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `task_id` | TEXT | PRIMARY KEY | 任务唯一ID |
| `required_date` | TEXT | NULL | 需求日期 |
| `start_bureau` | TEXT | NULL | 起始站段 |
| `route_direction` | TEXT | NULL | 路线方向 |
| `carrier_company` | TEXT | NULL | 运输公司 |
| `route_name` | TEXT | NULL | 路线名称 |
| `transport_type` | TEXT | NULL | 运输类型 |
| `requirement_type` | TEXT | NULL | 需求类型 |
| `volume` | INTEGER | NULL | 需求容积 |
| `weight` | REAL | NULL | 需求重量 |
| `special_requirements` | TEXT | NULL | 特殊要求 |
| `status` | TEXT | NULL | 任务状态 |
| `dispatch_track` | TEXT | NULL | 派车轨道 |
| `initiator_role` | TEXT | NULL | 发起人角色 |
| `initiator_user_id` | INTEGER | NULL | 发起人用户ID |
| `initiator_department` | TEXT | NULL | 发起人部门 |
| `audit_required` | BOOLEAN | NULL | 是否需要审核 |
| `auditor_role` | TEXT | NULL | 审核人角色 |
| `auditor_user_id` | INTEGER | NULL | 审核人用户ID |
| `audit_status` | TEXT | NULL | 审核状态 |
| `audit_time` | TEXT | NULL | 审核时间 |
| `audit_note` | TEXT | NULL | 审核备注 |
| `current_handler_role` | TEXT | NULL | 当前处理人角色 |
| `current_handler_user_id` | INTEGER | NULL | 当前处理人用户ID |
| `created_at` | TEXT | NULL | 创建时间 |
| `updated_at` | TEXT | NULL | 更新时间 |
| `assigned_supplier_id` | INTEGER | NULL | 分配供应商ID |

### 3.2 车辆信息表（vehicles）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 车辆唯一ID |
| `task_id` | TEXT | FOREIGN KEY | 关联任务ID |
| `manifest_number` | TEXT | NULL | 路单流水号 |
| `dispatch_number` | TEXT | NULL | 派车单号 |
| `license_plate` | TEXT | NULL | 车牌号 |
| `carriage_number` | TEXT | NULL | 车厢号 |
| `created_at` | TEXT | NULL | 创建时间 |
| `notes` | TEXT | NULL | 备注 |
| `actual_volume` | REAL | NULL | 实际容积 |
| `volume_photo_url` | TEXT | NULL | 容积照片URL |
| `volume_modified_by` | INTEGER | NULL | 容积修改人 |
| `required_volume` | REAL | NULL | 需求容积 |
| `confirmed_volume` | REAL | NULL | 确认容积 |
| `vehicle_type` | TEXT | NULL | 车辆类型 |
| `supplier_id` | INTEGER | NULL | 供应商ID |
| `supplier_type` | TEXT | NULL | 供应商类型 |
| `status` | TEXT | NULL | 车辆状态 |
| `confirmed_by` | INTEGER | NULL | 确认人ID |
| `confirmed_at` | TEXT | NULL | 确认时间 |
| `is_merged` | BOOLEAN | NULL | 是否已合并 |
| `is_downgraded` | BOOLEAN | NULL | 是否已降档 |
| `original_capacity` | REAL | NULL | 原始容积 |
| `updated_at` | TEXT | NULL | 更新时间 |

### 3.3 状态历史表（dispatch_status_history）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 历史记录ID |
| `task_id` | TEXT | FOREIGN KEY | 关联任务ID |
| `status_change` | TEXT | NULL | 状态变更 |
| `operator` | TEXT | NULL | 操作人 |
| `timestamp` | TEXT | NULL | 时间戳 |
| `note` | TEXT | NULL | 备注 |

### 3.4 用户表（User）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 用户唯一ID |
| `username` | TEXT | UNIQUE | 用户名 |
| `password` | TEXT | NOT NULL | 密码（加密存储） |
| `full_name` | TEXT | NULL | 姓名 |
| `email` | TEXT | NULL | 邮箱 |
| `phone` | TEXT | NULL | 手机号 |
| `company_id` | INTEGER | FOREIGN KEY | 所属公司ID |
| `is_active` | BOOLEAN | DEFAULT TRUE | 是否激活 |
| `created_at` | TIMESTAMP | NULL | 创建时间 |
| `updated_at` | TIMESTAMP | NULL | 更新时间 |

### 3.5 角色表（Role）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 角色唯一ID |
| `name` | TEXT | UNIQUE | 角色名称 |
| `description` | TEXT | NULL | 角色描述 |
| `created_at` | TIMESTAMP | NULL | 创建时间 |
| `updated_at` | TIMESTAMP | NULL | 更新时间 |

### 3.6 用户角色关联表（UserRole）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `user_id` | INTEGER | PRIMARY KEY, FOREIGN KEY | 用户ID |
| `role_id` | INTEGER | PRIMARY KEY, FOREIGN KEY | 角色ID |
| `created_at` | TIMESTAMP | NULL | 创建时间 |

### 3.7 公司表（Company）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 公司唯一ID |
| `name` | TEXT | UNIQUE | 公司名称 |
| `bank_name` | TEXT | NULL | 银行名称 |
| `account_number` | TEXT | NULL | 银行账号 |
| `address` | TEXT | NULL | 公司地址 |
| `contact_person` | TEXT | NULL | 联系人 |
| `contact_phone` | TEXT | NULL | 联系电话 |
| `created_at` | TIMESTAMP | NULL | 创建时间 |
| `updated_at` | TIMESTAMP | NULL | 更新时间 |

### 3.8 车辆容积参考表（vehicle_capacity_reference）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 主键ID |
| `vehicle_type` | TEXT | NULL | 车辆类型（支持5吨、8吨、12吨、20吨、30吨、40吨A、40吨B） |
| `standard_volume` | REAL | NULL | 标准容积 |
| `license_plate` | TEXT | NULL | 车牌号 |
| `suppliers` | TEXT | NULL | 供应商信息 |
| `created_at` | TEXT | NULL | 创建时间 |
| `updated_at` | TEXT | NULL | 更新时间 |

### 3.9 权限表（Permission）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 权限唯一ID |
| `name` | TEXT | NOT NULL | 权限名称 |
| `code` | TEXT | UNIQUE | 权限代码 |
| `description` | TEXT | NULL | 权限描述 |
| `resource_type` | TEXT | NOT NULL | 资源类型: menu, api, button |
| `resource_id` | TEXT | NULL | 资源标识 |
| `action` | TEXT | NOT NULL | 操作类型: read, write, delete, execute |
| `created_at` | TIMESTAMP | NULL | 创建时间 |
| `updated_at` | TIMESTAMP | NULL | 更新时间 |

### 3.10 菜单表（Menu）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 菜单唯一ID |
| `name` | TEXT | NOT NULL | 菜单名称 |
| `code` | TEXT | UNIQUE | 菜单代码 |
| `path` | TEXT | NULL | 路由路径 |
| `component` | TEXT | NULL | 组件路径 |
| `icon` | TEXT | NULL | 图标 |
| `parent_id` | INTEGER | FOREIGN KEY | 父菜单ID |
| `sort_order` | INTEGER | DEFAULT 0 | 排序 |
| `is_active` | BOOLEAN | DEFAULT TRUE | 是否启用 |
| `created_at` | TIMESTAMP | NULL | 创建时间 |
| `updated_at` | TIMESTAMP | NULL | 更新时间 |

### 3.11 角色权限关联表（RolePermission）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 关联记录唯一ID |
| `role_id` | INTEGER | FOREIGN KEY | 角色ID |
| `permission_id` | INTEGER | FOREIGN KEY | 权限ID |
| `granted_at` | TIMESTAMP | NULL | 授权时间 |
| `granted_by` | INTEGER | FOREIGN KEY | 授权人ID |

### 3.12 菜单权限关联表（MenuPermission）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 关联记录唯一ID |
| `menu_id` | INTEGER | FOREIGN KEY | 菜单ID |
| `permission_id` | INTEGER | FOREIGN KEY | 权限ID |

### 3.13 操作日志表（operation_logs）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 日志ID |
| `task_id` | TEXT | FOREIGN KEY | 关联任务ID |
| `user_id` | INTEGER | FOREIGN KEY | 操作用户ID |
| `user_role` | TEXT | NULL | 操作用户角色 |
| `operation_type` | TEXT | NULL | 操作类型 |
| `operation_content` | TEXT | NULL | 操作内容 |
| `ip_address` | TEXT | NULL | IP地址 |
| `operation_time` | TEXT | NULL | 操作时间 |

### 3.14 车辆容积更新历史表（vehicle_volume_history）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 记录ID |
| `vehicle_id` | INTEGER | FOREIGN KEY | 车辆ID |
| `original_volume` | REAL | NULL | 原始容积 |
| `new_volume` | REAL | NULL | 新容积 |
| `reason` | TEXT | NULL | 修改原因 |
| `modified_by` | INTEGER | FOREIGN KEY | 修改人ID |
| `modified_at` | TIMESTAMP | NULL | 修改时间 |
| `volume_photo_url` | TEXT | NULL | 容积照片URL |
| `approval_doc_url` | TEXT | NULL | 审批凭证URL |

### 3.15 车辆合并记录表（vehicle_merge_records）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 记录ID |
| `source_vehicle_id` | INTEGER | FOREIGN KEY | 源车辆ID |
| `target_vehicle_id` | INTEGER | FOREIGN KEY | 目标车辆ID |
| `merge_time` | TEXT | NULL | 合并时间 |
| `operator_id` | INTEGER | FOREIGN KEY | 操作人ID |
| `operator_role` | TEXT | NULL | 操作人角色 |
| `original_volume` | REAL | NULL | 原始容积 |
| `merged_volume` | REAL | NULL | 合并后容积 |
| `merge_reason` | TEXT | NULL | 合并原因 |

### 3.16 车辆降档记录表（vehicle_downgrade_records）

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| `id` | INTEGER | PRIMARY KEY | 记录ID |
| `vehicle_id` | INTEGER | FOREIGN KEY | 车辆ID |
| `downgrade_time` | TEXT | NULL | 降档时间 |
| `operator_id` | INTEGER | FOREIGN KEY | 操作人ID |
| `operator_role` | TEXT | NULL | 操作人角色 |
| `original_type` | TEXT | NULL | 原始车型 |
| `downgraded_type` | TEXT | NULL | 降档后车型 |
| `original_volume` | REAL | NULL | 原始容积 |
| `downgraded_volume` | REAL | NULL | 降档后容积 |
| `downgrade_reason` | TEXT | NULL | 降档原因 |

## 4. 状态流转规则

### 4.1 任务状态列表
- `待审核`: 任务创建后需要审核
- `审核通过`: 任务审核通过
- `待供应商响应`: 任务等待供应商确认
- `供应商已响应`: 供应商确认响应
- `任务完成`: 任务执行完成
- `审核拒绝`: 任务审核未通过

### 4.2 状态流转规则
- 车间地调创建的任务初始状态为`待审核`
- 区域调度员创建的任务可选择轨道A或轨道B：
  - 轨道A：初始状态为`待审核`
  - 轨道B：初始状态为`待供应商响应`
- 超级管理员创建的任务可选择轨道A或轨道B：
  - 轨道A：初始状态为`待审核`
  - 轨道B：初始状态为`待供应商响应`

## 5. 权限管理设计

### 5.1 角色定义
- **超级管理员**: 系统最高权限，可管理所有功能
- **区域调度员**: 负责任务审核、派车管理
- **车间地调**: 负责提交车辆需求、查看已分配的任务
- **供应商**: 负责响应任务、填写车辆信息
- **财务人员**: 负责财务对账，结算单生成等任务

### 5.2 角色权限矩阵

| 功能模块 | 权限操作 | 超级管理员 | 区域调度员 | 车间地调 | 供应商 | 财务人员 |
|----------|----------|------------|------------|----------|--------|----------|
| 任务管理 | 创建任务 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 任务管理 | 查看任务列表 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 任务管理 | 查看任务详情 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 任务管理 | 更新任务信息 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 审核流程 | 提交审核 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 审核流程 | 审核任务 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 状态管理 | 更新任务状态 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 状态管理 | 查看状态历史 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 供应商响应 | 确认响应 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 供应商响应 | 填写车辆信息 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 公司管理 | 查看公司列表 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 公司管理 | 添加公司 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 公司管理 | 更新公司信息 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 公司管理 | 删除公司 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 车辆管理 | 查看车辆容积参考 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 车辆管理 | 更新车辆容积参考 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 车辆管理 | 添加车辆容积参考 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 车辆管理 | 删除车辆容积参考 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 车辆管理 | 批量导入车辆容积参考 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 系统管理 | 用户管理 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 财务管理 | 查看结算单 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 财务管理 | 生成结算单 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 财务管理 | 导出财务数据 | ✅ | ✅ | ❌ | ❌ | ✅ |