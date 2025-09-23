# 智能运力系统 - API设计文档

## 1. RESTful API接口体系概述

智能运力系统采用RESTful API设计风格，基于Flask框架实现，提供了完整的派车任务管理、审核流程、状态管理、派车单位管理和车辆管理等功能接口。系统支持双轨派车流程（轨道A和轨道B），并实现了基于角色的访问控制机制。

API接口采用统一的响应格式，支持分页查询、条件过滤和权限验证，确保系统安全性和可用性。

## 2. 双轨派车流程

### 2.1 轨道A流程（需要审核）
1. **任务创建**：车间地调或区域调度员创建任务
2. **待审核**：任务进入审核状态
3. **审核通过**：区域调度员审核通过后，任务进入待供应商响应状态
4. **供应商响应**：供应商确认并填写车辆信息
5. **任务完成**：任务执行完成

### 2.2 轨道B流程（直接派车）
1. **任务创建**：区域调度员或超级管理员创建任务
2. **待供应商响应**：任务直接进入待供应商响应状态
3. **供应商响应**：供应商确认并填写车辆信息
4. **任务完成**：任务执行完成

## 3. 状态流转

### 3.1 任务状态列表
- `待审核`: 任务创建后需要审核
- `审核通过`: 任务审核通过
- `待供应商响应`: 任务等待供应商确认
- `供应商已响应`: 供应商确认响应
- `任务完成`: 任务执行完成
- `审核拒绝`: 任务审核未通过

### 3.2 状态流转规则
- 车间地调创建的任务初始状态为`待审核`
- 区域调度员创建的任务可选择轨道A或轨道B：
  - 轨道A：初始状态为`待审核`
  - 轨道B：初始状态为`待供应商响应`
- 超级管理员创建的任务可选择轨道A或轨道B：
  - 轨道A：初始状态为`待审核`
  - 轨道B：初始状态为`待供应商响应`

## 4. API接口详细设计

### 4.1 任务管理接口

#### 创建派车任务
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch/tasks`
- **权限**: `dispatch:write`
- **请求参数**: JSON格式
  ```json
  {
    "required_date": "2023-08-20",
    "origin_bureau": "始发局A",
    "mail_route_name": "邮路名称",
    "organizing_unit": "组开单位",
    "organizing_unit_id": 1,
    "transport_type": "公路运输",
    "requirement_type": "普通货物",
    "required_volume": 100,
    "required_weight": "5.0",
    "special_requirements": "轻拿轻放",
    "assigned_supplier_id": 1,
    "dispatch_track": "A",
    "audit_required": true,
    "business_type": "委办派车"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "task_id": "T202308201000001",
      "status": "待审核",
      "dispatch_track": "A",
      "current_handler_role": "区域调度员"
    }
  }
  ```
- **业务逻辑**: 根据用户角色和选择的轨道确定任务初始状态和处理流程

#### 获取任务列表
- **HTTP方法**: GET
- **路径**: `/api/v1/dispatch/tasks`
- **权限**: `dispatch:read`
- **查询参数**: 
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `query`: 搜索关键词
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "items": [
        {
          "task_id": "T202308201000001",
          "required_date": "2023-08-20",
          "origin_bureau": "始发局A",
          "mail_route_name": "邮路名称",
          "organizing_unit": "组开单位",
          "transport_type": "公路运输",
          "requirement_type": "普通货物",
          "required_volume": 100,
          "required_weight": "5.0",
          "status": "待审核",
          "created_at": "2023-08-19 15:30:00",
          "updated_at": "2023-08-19 15:30:00",
          "special_requirements": "轻拿轻放",
          "business_type": "委办派车"
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 10
    }
  }
  ```

#### 获取任务详情
- **HTTP方法**: GET
- **路径**: `/api/v1/dispatch/tasks/{task_id}`
- **权限**: `dispatch:read`
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "task_id": "T202308201000001",
      "required_date": "2023-08-20",
      "origin_bureau": "始发局A",
      "mail_route_name": "邮路名称",
      "organizing_unit": "组开单位",
      "transport_type": "公路运输",
      "requirement_type": "普通货物",
      "required_volume": 100,
      "required_weight": "5.0",
      "status": "待审核",
      "created_at": "2023-08-19 15:30:00",
      "updated_at": "2023-08-19 15:30:00",
      "special_requirements": "轻拿轻放",
      "business_type": "委办派车",
      "vehicles": []
    }
  }
  ```

#### 更新任务信息
- **HTTP方法**: PUT
- **路径**: `/api/v1/dispatch/tasks/{task_id}`
- **权限**: `dispatch:write`
- **请求参数**: JSON格式
  ```json
  {
    "required_date": "2023-08-21",
    "origin_bureau": "始发局B",
    "mail_route_name": "邮路名称更新",
    "organizing_unit": "组开单位",
    "organizing_unit_id": 1,
    "transport_type": "公路运输",
    "requirement_type": "普通货物",
    "required_volume": 120,
    "required_weight": "6.0",
    "special_requirements": "轻拿轻放，小心易碎"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "task_id": "T202308201000001"
    }
  }
  ```

### 4.2 审核流程接口

#### 审核任务
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch/tasks/{task_id}/approve`
- **权限**: `dispatch:approve`
- **请求参数**: JSON格式
  ```json
  {
    "action": "approve",
    "note": "审核通过"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "审核成功",
    "data": {
      "task_id": "T202308201000001",
      "status": "审核通过"
    }
  }
  ```
- **业务逻辑**: 
  - `action`可选值: `approve`(通过), `reject`(拒绝)
  - 审核通过后，任务状态变为"审核通过"，然后自动进入"待供应商响应"状态
  - 审核拒绝后，任务状态变为"审核拒绝"

#### 获取任务状态历史
- **HTTP方法**: GET
- **路径**: `/api/v1/dispatch/tasks/{task_id}/status-history`
- **权限**: `dispatch:read`
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "task_id": "T202308201000001",
        "status_change": "待审核",
        "operator": "张三",
        "timestamp": "2023-08-19 15:30:00",
        "note": "任务创建"
      },
      {
        "id": 2,
        "task_id": "T202308201000001",
        "status_change": "审核通过",
        "operator": "李四",
        "timestamp": "2023-08-19 16:30:00",
        "note": "审核通过"
      }
    ]
  }
  ```

### 4.3 供应商响应接口

#### 分配车辆
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch/tasks/{task_id}/assign`
- **权限**: `dispatch:assign`
- **请求参数**: JSON格式
  ```json
  {
    "vehicles": [
      {
        "license_plate": "京A12345",
        "carriage_number": "C12345",
        "vehicle_type": "40吨A",
        "actual_volume": 100,
        "notes": "车辆备注"
      }
    ]
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "分配成功",
    "data": {
      "task_id": "T202308201000001",
      "status": "供应商已响应"
    }
  }
  ```
- **业务逻辑**: 供应商为任务分配车辆，任务状态变为"供应商已响应"

#### 完成任务
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch/tasks/{task_id}/complete`
- **权限**: `dispatch:complete`
- **请求参数**: JSON格式
  ```json
  {
    "note": "任务已完成"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "任务完成",
    "data": {
      "task_id": "T202308201000001",
      "status": "任务完成"
    }
  }
  ```
- **业务逻辑**: 将任务标记为完成状态

### 4.4 车辆管理接口

#### 获取车辆列表
- **HTTP方法**: GET
- **路径**: `/api/v1/vehicles`
- **权限**: `vehicle:read`
- **查询参数**: 
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `query`: 搜索关键词
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "items": [
        {
          "id": 1,
          "task_id": "T202308201000001",
          "license_plate": "京A12345",
          "carriage_number": "C12345",
          "vehicle_type": "40吨A",
          "actual_volume": 100,
          "status": "待确认",
          "created_at": "2023-08-19 17:30:00"
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 10
    }
  }
  ```

#### 更新车辆容积
- **HTTP方法**: POST
- **路径**: `/api/v1/vehicles/update-volume`
- **权限**: `vehicle:write`
- **请求参数**: JSON格式
  ```json
  {
    "vehicle_id": 1,
    "new_volume": 120,
    "reason": "容积调整",
    "volume_photo_url": "http://example.com/photo.jpg"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "vehicle_id": 1,
      "actual_volume": 120
    }
  }
  ```

#### 合并车辆
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch/vehicles/merge`
- **权限**: `vehicle:merge`
- **请求参数**: JSON格式
  ```json
  {
    "source_vehicle_id": 1,
    "target_vehicle_id": 2,
    "merge_reason": "优化装载"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "合并成功",
    "data": {
      "target_vehicle_id": 2,
      "merged_volume": 220
    }
  }
  ```
- **业务逻辑**: 将源车辆的容积合并到目标车辆，源车辆标记为已合并状态

#### 降档车辆
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch/vehicles/{vehicle_id}/downgrade`
- **权限**: `vehicle:downgrade`
- **请求参数**: JSON格式
  ```json
  {
    "downgraded_type": "30吨",
    "downgraded_volume": 80,
    "downgrade_reason": "车辆实际容量不足"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "降档成功",
    "data": {
      "vehicle_id": 1,
      "original_type": "40吨A",
      "downgraded_type": "30吨",
      "downgraded_volume": 80
    }
  }
  ```
- **业务逻辑**: 将车辆降级为较低容量的车型，记录降档历史

### 4.5 派车单位管理接口

#### 获取派车单位列表
- **HTTP方法**: GET
- **路径**: `/api/v1/dispatch-units`
- **权限**: `dispatch_unit:read`
- **查询参数**: 
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `query`: 搜索关键词
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "items": [
        {
          "id": 1,
          "name": "派车单位A",
          "unit_type": "供应商",
          "contact_person": "张三",
          "contact_phone": "13800138000",
          "is_active": true
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 10
    }
  }
  ```

#### 创建派车单位
- **HTTP方法**: POST
- **路径**: `/api/v1/dispatch-units`
- **权限**: `dispatch_unit:write`
- **请求参数**: JSON格式
  ```json
  {
    "name": "派车单位B",
    "unit_type": "供应商",
    "bank_name": "中国银行",
    "account_number": "6225123456789012",
    "address": "北京市海淀区",
    "contact_person": "李四",
    "contact_phone": "13900139000",
    "email": "lisi@example.com"
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "id": 2,
      "name": "派车单位B"
    }
  }
  ```

### 4.6 用户管理接口

#### 获取用户列表
- **HTTP方法**: GET
- **路径**: `/api/v1/users`
- **权限**: `user:read`
- **查询参数**: 
  - `page`: 页码，默认1
  - `per_page`: 每页数量，默认10
  - `query`: 搜索关键词
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "items": [
        {
          "id": 1,
          "username": "admin",
          "full_name": "系统管理员",
          "email": "admin@example.com",
          "phone": "13800138000",
          "dispatch_unit_id": null,
          "is_active": true,
          "roles": ["超级管理员"]
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 10
    }
  }
  ```

#### 创建用户
- **HTTP方法**: POST
- **路径**: `/api/v1/users`
- **权限**: `user:write`
- **请求参数**: JSON格式
  ```json
  {
    "username": "supplier1",
    "password": "password123",
    "full_name": "供应商用户",
    "email": "supplier@example.com",
    "phone": "13900139000",
    "dispatch_unit_id": 1
  }
  ```
- **响应示例**: 
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "id": 2,
      "username": "supplier1"
    }
  }
  ```

## 5. API实现状态

| 接口分类 | 接口名称 | 实现状态 | 备注 |
|---------|---------|---------|------|
| 任务管理 | 创建派车任务 | ✅ 已实现 | |
| 任务管理 | 获取任务列表 | ✅ 已实现 | |
| 任务管理 | 获取任务详情 | ✅ 已实现 | |
| 任务管理 | 更新任务信息 | ✅ 已实现 | |
| 审核流程 | 审核任务 | ✅ 已实现 | |
| 审核流程 | 获取任务状态历史 | ✅ 已实现 | |
| 供应商响应 | 分配车辆 | ✅ 已实现 | |
| 供应商响应 | 完成任务 | ✅ 已实现 | |
| 车辆管理 | 获取车辆列表 | ✅ 已实现 | |
| 车辆管理 | 更新车辆容积 | ✅ 已实现 | |
| 车辆管理 | 合并车辆 | ✅ 已实现 | |
| 车辆管理 | 降档车辆 | ✅ 已实现 | |
| 派车单位管理 | 获取派车单位列表 | ✅ 已实现 | |
| 派车单位管理 | 创建派车单位 | ✅ 已实现 | |
| 用户管理 | 获取用户列表 | ✅ 已实现 | |
| 用户管理 | 创建用户 | ✅ 已实现 | |

## 6. 错误处理

### 6.1 错误响应格式

```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

### 6.2 常见错误码

| 错误码 | 说明 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器内部错误 |
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "任务已提交审核",
      "new_status": "待调度员审核"
    }
  }
  ```
- **业务逻辑**: 将任务提交审核，更新任务状态

#### 审核通过
- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/approve`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "notes": "审核通过，同意派车",
    "assigned_supplier_id": "2"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "任务审核通过",
      "new_status": "待供应商响应"
    }
  }
  ```
- **业务逻辑**: 审核通过任务，更新任务状态为待供应商响应，可指定分配的供应商

#### 审核拒绝
- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/reject`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "notes": "任务信息不完整，需要补充"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "任务审核拒绝",
      "new_status": "审核拒绝"
    }
  }
  ```
- **业务逻辑**: 拒绝任务审核，更新任务状态为审核拒绝

### 4.3 状态管理接口

#### 更新任务状态
- **HTTP方法**: PUT
- **路径**: `/api/dispatch/tasks/{task_id}/status`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "new_status": "任务完成",
    "notes": "任务已成功完成"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "任务状态已更新",
      "new_status": "任务完成"
    }
  }
  ```
- **业务逻辑**: 更新任务状态，记录状态变更历史

#### 获取状态历史
- **HTTP方法**: GET
- **路径**: `/api/dispatch/tasks/{task_id}/history`
- **权限**: `车间地调`, `区域调度员`, `超级管理员`, `供应商`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": [
      {
        "status": "待调度员审核",
        "timestamp": "2025-08-19T15:30:00",
        "updated_by": "用户张三",
        "notes": "任务创建"
      },
      {
        "status": "待供应商响应",
        "timestamp": "2025-08-19T16:45:00",
        "updated_by": "用户李四",
        "notes": "审核通过"
      }
    ]
  }
  ```
- **业务逻辑**: 获取任务的完整状态变更历史

### 4.4 供应商响应接口

#### 供应商确认响应
- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/confirm`
- **权限**: `供应商`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "供应商响应成功",
      "task_id": "T202508201000001",
      "new_status": "供应商已响应"
    }
  }
  ```
- **业务逻辑**: 供应商确认响应任务，更新任务状态为供应商已响应
- **数据验证**: 
  - 任务必须存在
  - 任务状态必须为待供应商响应
  - 该任务不能已存在车辆信息

#### 供应商确认并填写车辆信息
- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/confirm-with-vehicle`
- **权限**: `供应商`
- **请求参数**: JSON格式
  ```json
  {
    "vehicle_number": "京A12345",
    "vehicle_type": "货车",
    "driver_name": "王五",
    "driver_phone": "13800138000",
    "capacity_volume": 15.0,
    "capacity_weight": 8.0
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "供应商响应并填写车辆信息成功",
      "task_id": "T202508201000001",
      "new_status": "供应商已响应",
      "vehicle_id": "1"
    }
  }
  ```
- **业务逻辑**: 供应商确认响应任务并填写车辆信息，更新任务状态为供应商已响应
- **数据验证**: 
  - 任务必须存在
  - 任务状态必须为待供应商响应
  - 车辆信息必须完整

### 4.5 公司管理接口

#### 获取公司列表
- **HTTP方法**: GET
- **路径**: `/api/company/list`
- **权限**: `车间地调`, `区域调度员`, `超级管理员`
- **查询参数**: 
  - `is_supplier`: 是否为供应商，可选
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认20
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "list": [
        {
          "id": "1",
          "name": "运输公司A",
          "contact_person": "张三",
          "contact_phone": "13800138000",
          "address": "北京市朝阳区",
          "is_supplier": true
        }
      ],
      "total": 1,
      "page": 1,
      "limit": 20
    }
  }
  ```
- **业务逻辑**: 获取公司列表，可筛选是否为供应商

#### 添加公司
- **HTTP方法**: POST
- **路径**: `/api/company`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "name": "运输公司B",
    "contact_person": "李四",
    "contact_phone": "13900139000",
    "address": "上海市浦东新区",
    "is_supplier": true
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "公司添加成功",
      "company_id": "2"
    }
  }
  ```
- **业务逻辑**: 添加新的公司信息
- **数据验证**: 
  - 公司名称不能为空
  - 联系电话格式必须正确

#### 获取公司ID
- **HTTP方法**: GET
- **路径**: `/api/company/id`
- **权限**: `车间地调`, `区域调度员`, `超级管理员`
- **查询参数**: 
  - `name`: 公司名称
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "company_id": "1"
    }
  }
  ```
- **业务逻辑**: 根据公司名称查询公司ID

### 4.6 车辆管理接口

#### 获取车辆容积参考数据
- **HTTP方法**: GET
- **路径**: `/api/vehicle/volume-reference`
- **权限**: `车间地调`, `区域调度员`, `超级管理员`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "1",
        "vehicle_type": "小型货车",
        "min_volume": 5.0,
        "max_volume": 10.0,
        "avg_volume": 7.5
      },
      {
        "id": "2",
        "vehicle_type": "中型货车",
        "min_volume": 10.0,
        "max_volume": 20.0,
        "avg_volume": 15.0
      }
    ]
  }
  ```
- **业务逻辑**: 获取车辆类型对应的容积参考数据

#### 更新车辆容积参考数据
- **HTTP方法**: PUT
- **路径**: `/api/vehicle/volume-reference/{id}`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "min_volume": 6.0,
    "max_volume": 12.0,
    "avg_volume": 9.0
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "车辆容积参考数据更新成功"
    }
  }
  ```
- **业务逻辑**: 更新特定车辆类型的容积参考数据
- **数据验证**: 
  - 容积数据必须为正数
  - min_volume <= avg_volume <= max_volume

#### 插入车辆容积参考数据
- **HTTP方法**: POST
- **路径**: `/api/vehicle/volume-reference`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "vehicle_type": "大型货车",
    "min_volume": 20.0,
    "max_volume": 35.0,
    "avg_volume": 27.5
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "车辆容积参考数据插入成功",
      "id": "3"
    }
  }
  ```
- **业务逻辑**: 插入新的车辆类型容积参考数据
- **数据验证**: 
  - 车辆类型不能为空
  - 容积数据必须为正数
  - min_volume <= avg_volume <= max_volume

#### 删除车辆容积参考数据
- **HTTP方法**: DELETE
- **路径**: `/api/vehicle/volume-reference/{id}`
- **权限**: `区域调度员`, `超级管理员`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "车辆容积参考数据删除成功"
    }
  }
  ```
- **业务逻辑**: 删除特定的车辆容积参考数据

#### 批量导入车辆容积参考数据
- **HTTP方法**: POST
- **路径**: `/api/vehicle/volume-reference/batch-import`
- **权限**: `区域调度员`, `超级管理员`
- **请求参数**: JSON格式
  ```json
  {
    "data": [
      {
        "vehicle_type": "小型货车",
        "min_volume": 5.0,
        "max_volume": 10.0,
        "avg_volume": 7.5
      },
      {
        "vehicle_type": "中型货车",
        "min_volume": 10.0,
        "max_volume": 20.0,
        "avg_volume": 15.0
      }
    ]
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "message": "车辆容积参考数据批量导入成功",
      "imported_count": 2,
      "failed_count": 0
    }
  }
  ```
- **业务逻辑**: 批量导入车辆容积参考数据
- **数据验证**: 
  - 每个数据项必须符合单个插入的验证规则

#### 车辆信息搜索
- **HTTP方法**: GET
- **路径**: `/api/vehicle/search`
- **权限**: `车间地调`, `区域调度员`, `超级管理员`
- **查询参数**: 
  - `vehicle_number`: 车牌号（模糊搜索）
  - `driver_name`: 司机姓名（模糊搜索）
  - `company_id`: 所属公司ID
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认20
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "list": [
        {
          "id": "1",
          "vehicle_number": "京A12345",
          "vehicle_type": "货车",
          "driver_name": "王五",
          "driver_phone": "13800138000",
          "capacity_volume": 15.0,
          "capacity_weight": 8.0,
          "company_id": "1",
          "company_name": "运输公司A"
        }
      ],
      "total": 1,
      "page": 1,
      "limit": 20
    }
  }
  ```
- **业务逻辑**: 根据条件搜索车辆信息

## 5. API实现状态

| 接口类别 | 接口名称 | 实现状态 | 备注 |
|----------|----------|----------|------|
| 任务管理 | 创建派车任务 | 已实现 | 支持双轨派车流程 |
| 任务管理 | 获取任务列表 | 已实现 | 支持分页和角色过滤 |
| 任务管理 | 获取任务详情 | 已实现 | 包含状态历史 |
| 任务管理 | 更新任务信息 | 已实现 | 支持更新任务基本信息 |
| 审核流程 | 提交审核 | 待实现 | |
| 审核流程 | 审核通过 | 待实现 | |
| 审核流程 | 审核拒绝 | 待实现 | |
| 状态管理 | 更新任务状态 | 待实现 | |
| 状态管理 | 获取状态历史 | 已实现 | 包含在任务详情接口中 |
| 供应商响应 | 供应商确认响应 | 已实现 | 支持基本确认 |
| 供应商响应 | 供应商确认并填写车辆信息 | 部分实现 | 支持填写车辆信息 |
| 公司管理 | 获取公司列表 | 待实现 | |
| 公司管理 | 添加公司 | 待实现 | |
| 公司管理 | 获取公司ID | 待实现 | |
| 车辆管理 | 获取车辆容积参考数据 | 待实现 | |
| 车辆管理 | 更新车辆容积参考数据 | 待实现 | |
| 车辆管理 | 插入车辆容积参考数据 | 待实现 | |
| 车辆管理 | 删除车辆容积参考数据 | 待实现 | |
| 车辆管理 | 批量导入车辆容积参考数据 | 待实现 | |
| 车辆管理 | 车辆信息搜索 | 待实现 | |

## 6. API错误处理

### 6.1 错误类型
- **APIError**: 通用API错误
- **ValidationError**: 数据验证错误
- **PermissionError**: 权限错误
- **NotFoundError**: 资源不存在错误

### 6.2 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": 4001,
    "message": "数据验证失败: 必填字段缺失"
  }
}
```

### 6.3 常见错误代码
| 错误代码 | 错误消息 | 说明 |
|----------|----------|------|
| 4001 | 数据验证失败 | 请求参数不符合要求 |
| 4002 | 无权限执行此操作 | 用户角色不满足权限要求 |
| 4041 | 任务不存在 | 找不到指定的任务 |
| 4042 | 任务状态不正确 | 当前任务状态不允许执行此操作 |
| 4043 | 该任务已存在车辆信息 | 任务已分配车辆，不能重复操作 |
| 5001 | 内部服务器错误 | 服务器处理请求时发生错误 |