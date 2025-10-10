# 人工派车流程系统 - 多角色权限管理方案

## 1. 角色定义

基于系统需求，人工派车流程系统涉及以下核心角色：

### 1.1 调度员
- **职责**：负责审批运输需求，提出运输需求，新增车辆信息
- **权限级别**：高级管理权限
- **系统角色代码**：`dispatch_manager`

### 1.2 车间地调
- **职责**：提出运输需求，确认车型信息，执行车辆合并操作，执行降档操作，确认运输任务完成情况，修改车辆容积信息
- **权限级别**：中级操作权限
- **系统角色代码**：`workshop_dispatcher`

### 1.3 供应商（委办公司）
- **职责**：派遣委办车辆执行运输任务，提供派车单号、车牌号、车厢号等信息，最终确认
- **权限级别**：有限操作权限
- **系统角色代码**：`supplier`

### 1.4 班组
- **职责**：派遣自办车辆执行运输任务，最终确认
- **权限级别**：有限操作权限
- **系统角色代码**：`team`

### 1.5 承运商
- **职责**：与供应商区分，使用自办车辆，最终确认，管理外包驾驶员，负责车辆派遣
- **权限级别**：有限操作权限
- **系统角色代码**：`carrier`

## 2. 权限设计

### 2.1 菜单权限

| 权限代码 | 权限名称 | 资源类型 | 资源路径 | 操作类型 | 适用角色 |
|---------|---------|---------|---------|---------|----------|
| `menu:dispatch_management` | 派车管理菜单 | menu | `/dispatch` | read | 所有角色 |
| `menu:dispatch_approval` | 派车审批菜单 | menu | `/dispatch/approval` | read | 调度员 |
| `menu:dispatch_request` | 派车申请菜单 | menu | `/dispatch/request` | read | 调度员, 车间地调 |
| `menu:vehicle_management` | 车辆管理菜单 | menu | `/dispatch/vehicles` | read | 调度员, 车间地调, 供应商, 班组, 承运商 |
| `menu:task_tracking` | 任务跟踪菜单 | menu | `/dispatch/tracking` | read | 所有角色 |
| `menu:supplier_response` | 供应商响应菜单 | menu | `/dispatch/supplier-response` | read | 供应商, 班组, 承运商 |
| `menu:workshop_confirmation` | 车间确认菜单 | menu | `/dispatch/workshop-confirmation` | read | 车间地调 |
| `menu:vehicle_create` | 新增车辆菜单 | menu | `/dispatch/vehicles/create` | read | 调度员 |

### 2.2 API权限

#### 2.2.0 车辆管理权限

| 权限代码 | 权限名称 | 资源类型 | 资源路径 | 操作类型 | 适用角色 |
|---------|---------|---------|---------|---------|----------|
| `vehicle:create` | 新增车辆 | api | `/api/dispatch/vehicles/create` | write | 调度员 |
| `vehicle:read` | 查看车辆 | api | `/api/dispatch/vehicles` | read | 所有角色 |
| `vehicle:update` | 更新车辆 | api | `/api/dispatch/vehicles` | write | 调度员, 车间地调, 供应商, 班组, 承运商 |

#### 2.2.1 任务管理权限

| 权限代码 | 权限名称 | 资源类型 | 资源路径 | 操作类型 | 适用角色 |
|---------|---------|---------|---------|---------|----------|
| `task:create` | 创建派车任务 | api | `/api/dispatch/tasks` | write | 调度员, 车间地调 |
| `task:read` | 查看派车任务 | api | `/api/dispatch/tasks` | read | 所有角色 |
| `task:update` | 更新派车任务 | api | `/api/dispatch/tasks` | write | 调度员, 车间地调 |
| `task:delete` | 删除派车任务 | api | `/api/dispatch/tasks` | delete | 调度员 |

#### 2.2.2 审核流程权限

| 权限代码 | 权限名称 | 资源类型 | 资源路径 | 操作类型 | 适用角色 |
|---------|---------|---------|---------|---------|----------|
| `audit:submit` | 提交审核 | api | `/api/dispatch/tasks/submit-audit` | write | 车间地调 |
| `audit:approve` | 审核通过 | api | `/api/dispatch/tasks/approve` | write | 调度员 |
| `audit:reject` | 审核拒绝 | api | `/api/dispatch/tasks/reject` | write | 调度员 |

#### 2.2.3 供应商响应权限

| 权限代码 | 权限名称 | 资源类型 | 资源路径 | 操作类型 | 适用角色 |
|---------|---------|---------|---------|---------|----------|
| `supplier:respond` | 供应商响应 | api | `/api/dispatch/tasks/respond` | write | 供应商, 班组, 承运商 |
| `supplier:update_vehicle` | 更新车辆信息 | api | `/api/dispatch/vehicles` | write | 供应商, 班组, 承运商 |

#### 2.2.4 车间确认权限

| 权限代码 | 权限名称 | 资源类型 | 资源路径 | 操作类型 | 适用角色 |
|---------|---------|---------|---------|---------|----------|
| `workshop:confirm` | 车间确认 | api | `/api/dispatch/tasks/confirm` | write | 车间地调 |
| `workshop:merge_vehicles` | 合并车辆 | api | `/api/dispatch/vehicles/merge` | write | 车间地调 |
| `workshop:downgrade` | 降档操作 | api | `/api/dispatch/vehicles/downgrade` | write | 车间地调 |
| `workshop:update_volume` | 更新车辆容积 | api | `/api/dispatch/vehicles/volume` | write | 车间地调 |

## 3. 角色权限映射

### 3.1 调度员 (dispatch_manager)

```
menu:dispatch_management
menu:dispatch_approval
menu:dispatch_request
menu:vehicle_management
menu:task_tracking
menu:vehicle_create
task:create
task:read
task:update
task:delete
audit:approve
audit:reject
vehicle:create
vehicle:read
vehicle:update
```

### 3.2 车间地调 (workshop_dispatcher)

```
menu:dispatch_management
menu:dispatch_request
menu:vehicle_management
menu:task_tracking
menu:workshop_confirmation
task:create
task:read
task:update
audit:submit
workshop:confirm
workshop:merge_vehicles
workshop:downgrade
workshop:update_volume
vehicle:read
vehicle:update
```

### 3.3 供应商 (supplier)

```
menu:dispatch_management
menu:vehicle_management
menu:task_tracking
menu:supplier_response
task:read
supplier:respond
supplier:update_vehicle
vehicle:read
vehicle:update
```

### 3.4 班组 (team)

```
menu:dispatch_management
menu:vehicle_management
menu:task_tracking
menu:supplier_response
task:read
supplier:respond
supplier:update_vehicle
```

### 3.5 承运商 (carrier)

```
menu:dispatch_management
menu:vehicle_management
menu:task_tracking
menu:supplier_response
task:read
supplier:respond
supplier:update_vehicle
```

## 4. 权限控制实现

### 4.1 后端权限控制

1. 使用现有的RBAC权限模型进行权限控制
2. 在API接口层面进行权限验证
3. 使用装饰器或中间件检查用户角色和权限

### 4.2 前端权限控制

1. 基于用户角色动态生成菜单
2. 使用路由守卫控制页面访问权限
3. 根据用户权限动态显示或隐藏操作按钮

## 5. 权限初始化

系统初始化时，需要创建上述角色和权限，并建立角色与权限的关联关系。可以通过数据库迁移脚本或初始化脚本实现。

```python
# 示例初始化代码
def init_dispatch_roles_and_permissions():
    # 创建角色
    roles = [
        {'name': '调度员', 'code': 'dispatch_manager', 'description': '负责审批运输需求，提出运输需求，新增车辆信息'},
        {'name': '车间地调', 'code': 'workshop_dispatcher', 'description': '提出运输需求，确认车型信息，执行车辆合并操作，执行降档操作，确认运输任务完成情况，修改车辆容积信息'},
        {'name': '供应商', 'code': 'supplier', 'description': '派遣委办车辆执行运输任务，提供派车单号、车牌号、车厢号等信息，最终确认'},
        {'name': '班组', 'code': 'team', 'description': '派遣自办车辆执行运输任务，最终确认'},
        {'name': '承运商', 'code': 'carrier', 'description': '与供应商区分，使用自办车辆，最终确认，管理外包驾驶员，负责车辆派遣'}
    ]
    
    # 创建权限
    permissions = [
        # 菜单权限
        {'name': '派车管理菜单', 'code': 'menu:dispatch_management', 'resource_type': 'menu', 'resource_id': '/dispatch', 'action': 'read'},
        {'name': '派车审批菜单', 'code': 'menu:dispatch_approval', 'resource_type': 'menu', 'resource_id': '/dispatch/approval', 'action': 'read'},
        # ... 其他权限
    ]
    
    # 角色权限映射
    role_permissions = {
        'dispatch_manager': ['menu:dispatch_management', 'menu:dispatch_approval', ...],
        'workshop_dispatcher': ['menu:dispatch_management', 'menu:dispatch_request', ...],
        # ... 其他角色权限
    }
    
    # 初始化数据库
    # ...
```

## 6. 权限验证流程

1. 用户登录系统，获取用户角色信息
2. 系统根据用户角色加载对应的权限列表
3. 前端根据权限列表动态生成菜单和操作按钮
4. 用户访问API接口时，后端验证用户是否具有相应权限
5. 如果用户没有权限，返回403错误

## 7. 特殊权限处理

### 7.1 数据权限

除了功能权限外，还需要考虑数据权限，确保用户只能访问和操作与自己相关的数据：

1. 调度员：可以查看和操作所有派车任务，是唯一可以新增车辆的角色
2. 车间地调：只能查看和操作自己创建的派车任务，以及需要自己确认的任务，可以修改车辆容积信息
3. 供应商/班组/承运商：只能查看和操作分配给自己的派车任务

### 7.2 状态转换权限

任务状态转换需要严格控制权限：

1. 只有调度员可以将任务从"待审核"转为"审核通过"或"审核拒绝"
2. 只有供应商/班组/承运商可以将任务从"待供应商响应"转为"供应商已响应"
3. 只有车间地调可以将任务从"供应商已响应"转为"任务完成"

### 7.3 车辆容积操作权限

车辆容积的操作需要特殊处理：

1. 车间地调可以在车辆到位后直接修改系统中该车辆的容积信息
2. 若车辆在系统中无容积记录（首次录入或未填写），车间地调必须补充填写容积，并强制上传车辆容积测量照片作为凭证
3. 当车间测量发现车辆实际容积小于系统中已记录的容积时，车间地调需修改系统容积至实际值，且必须上传本次测量照片用于追溯差异原因

## 8. 总结

本方案基于现有的RBAC权限模型，为人工派车流程系统设计了多角色权限管理方案，明确了各角色的权限范围和操作限制，确保系统安全可靠运行。方案特别强调了以下几点：

1. 角色职责明确划分：调度员、车间地调、供应商、班组、承运商各司其职
2. 权限精细化控制：菜单权限、API权限、数据权限、状态转换权限等多维度控制
3. 车辆容积操作特殊处理：明确车间地调对车辆容积的修改权限和操作规则
4. 车辆新增权限限制：仅调度员可以新增车辆，确保车辆信息的准确性和一致性

在实际实现过程中，需要根据具体业务需求进行调整和优化，确保系统既满足业务需求又保证数据安全。