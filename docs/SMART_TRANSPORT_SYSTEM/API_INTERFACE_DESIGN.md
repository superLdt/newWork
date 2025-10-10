# 人工派车流程系统 - API接口设计

## 1. API接口概述

人工派车流程系统的API接口设计基于RESTful风格，主要包括以下几个模块：

1. **任务管理接口**：创建、查询、更新和删除派车任务
2. **审核流程接口**：提交审核、审核通过、审核拒绝
3. **供应商响应接口**：供应商响应任务、更新车辆信息
4. **车间确认接口**：车间确认任务完成、车辆合并、降档操作
5. **状态查询接口**：查询任务状态、状态历史
6. **操作日志接口**：记录和查询操作日志

## 2. API接口详细设计

### 2.1 任务管理接口

#### 2.1.1 创建派车任务

- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks`
- **权限**: `task:create`
- **请求参数**: JSON格式
  ```json
  {
    "required_date": "2023-08-20",
    "start_bureau": "站点A",
    "route_direction": "南向北",
    "carrier_company": "运输公司A",
    "route_name": "A-B线路",
    "transport_type": "公路运输",
    "requirement_type": "普通货物",
    "volume": 30,
    "weight": 15.5,
    "special_requirements": "轻拿轻放",
    "dispatch_track": "轨道A",
    "initiator_department": "物流部",
    "assigned_supplier_id": 1,
    "supplier_type": "委办公司"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "task_id": "T20230820001",
      "status": "待审核",
      "dispatch_track": "轨道A",
      "current_handler_role": "调度负责人"
    },
    "message": "派车任务创建成功"
  }
  ```
- **业务逻辑**: 
  - 根据用户角色和选择的轨道确定任务初始状态
  - 调度负责人/车间地调创建的任务可以选择轨道A或轨道B
  - 轨道A的初始状态为"待审核"，轨道B的初始状态为"待供应商响应"
  - 记录任务创建的操作日志和状态历史

#### 2.1.2 获取任务列表

- **HTTP方法**: GET
- **路径**: `/api/dispatch/tasks`
- **权限**: `task:read`
- **查询参数**: 
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认20
  - `status`: 任务状态，可选
  - `dispatch_track`: 派车轨道，可选
  - `start_date`: 开始日期，可选
  - `end_date`: 结束日期，可选
  - `keyword`: 关键词搜索，可选
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "list": [
        {
          "task_id": "T20230820001",
          "required_date": "2023-08-20",
          "start_bureau": "站点A",
          "route_name": "A-B线路",
          "carrier_company": "运输公司A",
          "transport_type": "公路运输",
          "requirement_type": "普通货物",
          "volume": 30,
          "weight": 15.5,
          "status": "待审核",
          "dispatch_track": "轨道A",
          "created_at": "2023-08-19 15:30:00",
          "updated_at": "2023-08-19 15:30:00"
        }
      ],
      "total": 1,
      "page": 1,
      "limit": 20
    },
    "message": "获取任务列表成功"
  }
  ```
- **业务逻辑**: 
  - 根据用户角色返回不同范围的任务列表
  - 调度负责人可以看到所有任务
  - 车间地调可以看到自己创建的任务和需要自己确认的任务
  - 供应商/班组/承运商只能看到分配给自己的任务

#### 2.1.3 获取任务详情

- **HTTP方法**: GET
- **路径**: `/api/dispatch/tasks/{task_id}`
- **权限**: `task:read`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "task_id": "T20230820001",
      "required_date": "2023-08-20",
      "start_bureau": "站点A",
      "route_direction": "南向北",
      "carrier_company": "运输公司A",
      "route_name": "A-B线路",
      "transport_type": "公路运输",
      "requirement_type": "普通货物",
      "volume": 30,
      "weight": 15.5,
      "special_requirements": "轻拿轻放",
      "status": "待审核",
      "dispatch_track": "轨道A",
      "initiator_role": "车间地调",
      "initiator_user_id": 1,
      "initiator_department": "物流部",
      "audit_required": true,
      "created_at": "2023-08-19 15:30:00",
      "updated_at": "2023-08-19 15:30:00",
      "vehicles": [],
      "status_history": [
        {
          "status_change": "创建任务，初始状态：待审核",
          "operator": "用户ID: 1, 角色: 车间地调",
          "timestamp": "2023-08-19 15:30:00",
          "note": "任务创建"
        }
      ]
    },
    "message": "获取任务详情成功"
  }
  ```
- **业务逻辑**: 
  - 获取任务的详细信息，包括状态历史记录和关联的车辆信息
  - 根据用户角色控制可见的信息范围

#### 2.1.4 更新任务信息

- **HTTP方法**: PUT
- **路径**: `/api/dispatch/tasks/{task_id}`
- **权限**: `task:update`
- **请求参数**: JSON格式
  ```json
  {
    "required_date": "2023-08-21",
    "start_bureau": "站点A",
    "route_direction": "南向北",
    "carrier_company": "运输公司B",
    "route_name": "A-C线路",
    "transport_type": "公路运输",
    "requirement_type": "普通货物",
    "volume": 35,
    "weight": 17.5,
    "special_requirements": "轻拿轻放，防潮"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "task_id": "T20230820001"
    },
    "message": "任务更新成功"
  }
  ```
- **业务逻辑**: 
  - 更新任务的基本信息，不包括状态变更
  - 只有在特定状态下才能更新任务信息
  - 记录任务更新的操作日志

#### 2.1.5 删除任务

- **HTTP方法**: DELETE
- **路径**: `/api/dispatch/tasks/{task_id}`
- **权限**: `task:delete`
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "任务删除成功"
  }
  ```
- **业务逻辑**: 
  - 只有调度负责人可以删除任务
  - 只能删除"待审核"或"审核拒绝"状态的任务
  - 记录任务删除的操作日志

### 2.2 审核流程接口

#### 2.2.1 提交审核

- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/submit-audit`
- **权限**: `audit:submit`
- **请求参数**: JSON格式
  ```json
  {
    "note": "请尽快审核此任务"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "提交审核成功"
  }
  ```
- **业务逻辑**: 
  - 只有车间地调可以提交审核
  - 只能提交"待审核"状态的任务
  - 记录提交审核的操作日志和状态历史

#### 2.2.2 审核通过

- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/approve`
- **权限**: `audit:approve`
- **请求参数**: JSON格式
  ```json
  {
    "note": "审核通过，请尽快安排车辆"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "审核通过成功"
  }
  ```
- **业务逻辑**: 
  - 只有调度负责人可以审核通过
  - 只能审核"待审核"状态的任务
  - 审核通过后，任务状态变更为"待供应商响应"
  - 记录审核通过的操作日志和状态历史

#### 2.2.3 审核拒绝

- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/reject`
- **权限**: `audit:reject`
- **请求参数**: JSON格式
  ```json
  {
    "note": "信息不完整，请补充详细的运输需求"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "审核拒绝成功"
  }
  ```
- **业务逻辑**: 
  - 只有调度负责人可以审核拒绝
  - 只能审核"待审核"状态的任务
  - 审核拒绝后，任务状态变更为"审核拒绝"
  - 记录审核拒绝的操作日志和状态历史

### 2.3 供应商响应接口

#### 2.3.1 供应商响应任务

- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/respond`
- **权限**: `supplier:respond`
- **请求参数**: JSON格式
  ```json
  {
    "note": "已安排车辆，预计明天到达",
    "vehicles": [
      {
        "license_plate": "京A12345",
        "driver_name": "张三",
        "driver_phone": "13800138000",
        "vehicle_type": "货车",
        "load_capacity": 15.0,
        "actual_volume": 15.0,
        "carriage_number": "C001"
      },
      {
        "license_plate": "京B67890",
        "driver_name": "李四",
        "driver_phone": "13900139000",
        "vehicle_type": "货车",
        "load_capacity": 15.0,
        "actual_volume": 15.0,
        "carriage_number": "C002"
      }
    ]
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "响应任务成功"
  }
  ```
- **业务逻辑**: 
  - 只有供应商/班组/承运商可以响应任务
  - 只能响应"待供应商响应"状态的任务
  - 响应后，任务状态变更为"供应商已响应"
  - 创建车辆信息记录
  - 记录供应商响应的操作日志和状态历史

#### 2.3.2 更新车辆信息

- **HTTP方法**: PUT
- **路径**: `/api/dispatch/vehicles/{vehicle_id}`
- **权限**: `supplier:update_vehicle`
- **请求参数**: JSON格式
  ```json
  {
    "license_plate": "京A12345",
    "driver_name": "张三",
    "driver_phone": "13800138000",
    "vehicle_type": "货车",
    "load_capacity": 15.0,
    "actual_volume": 15.0,
    "carriage_number": "C001",
    "notes": "车辆已准备就绪"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "车辆信息更新成功"
  }
  ```
- **业务逻辑**: 
  - 只有供应商/班组/承运商可以更新车辆信息
  - 只能更新自己创建的车辆信息
  - 记录车辆信息更新的操作日志

### 2.4 车间确认接口

#### 2.4.1 车间确认任务完成

- **HTTP方法**: POST
- **路径**: `/api/dispatch/tasks/{task_id}/confirm`
- **权限**: `workshop:confirm`
- **请求参数**: JSON格式
  ```json
  {
    "note": "任务已完成，车辆已离开"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "确认任务完成成功"
  }
  ```
- **业务逻辑**: 
  - 只有车间地调可以确认任务完成
  - 只能确认"供应商已响应"状态的任务
  - 确认后，任务状态变更为"任务完成"
  - 记录任务完成的操作日志和状态历史

#### 2.4.2 车辆合并操作

- **HTTP方法**: POST
- **路径**: `/api/dispatch/vehicles/merge`
- **权限**: `workshop:merge_vehicles`
- **请求参数**: JSON格式
  ```json
  {
    "task_id": "T20230820001",
    "source_vehicle_ids": [1, 2],
    "target_vehicle_id": 1,
    "merge_note": "合并两辆车的容积"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "车辆合并成功"
  }
  ```
- **业务逻辑**: 
  - 只有车间地调可以执行车辆合并操作
  - 只能合并"供应商已响应"状态任务的车辆
  - 合并后，源车辆标记为已合并，目标车辆容积增加
  - 记录车辆合并的操作日志和合并记录

#### 2.4.3 降档操作

- **HTTP方法**: POST
- **路径**: `/api/dispatch/vehicles/downgrade`
- **权限**: `workshop:downgrade`
- **请求参数**: JSON格式
  ```json
  {
    "vehicle_id": 1,
    "downgraded_capacity": 10.0,
    "downgrade_reason": "实际装载量减半"
  }
  ```
- **响应示例**: 
  ```json
  {
    "success": true,
    "message": "降档操作成功"
  }
  ```
- **业务逻辑**: 
  - 只有车间地调可以执行降档操作
  - 只能对"供应商已响应"状态任务的车辆执行降档操作
  - 降档后，记录原始容量和降档后容量
  - 记录降档操作的操作日志

### 2.5 状态查询接口

#### 2.5.1 查询任务状态

- **HTTP方法**: GET
- **路径**: `/api/dispatch/tasks/{task_id}/status`
- **权限**: `task:read`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "task_id": "T20230820001",
      "status": "待审核",
      "dispatch_track": "轨道A",
      "current_handler_role": "调度负责人",
      "updated_at": "2023-08-19 15:30:00"
    },
    "message": "获取任务状态成功"
  }
  ```
- **业务逻辑**: 
  - 获取任务的当前状态信息
  - 所有角色都可以查询任务状态，但需要有权限访问该任务

#### 2.5.2 查询状态历史

- **HTTP方法**: GET
- **路径**: `/api/dispatch/tasks/{task_id}/history`
- **权限**: `task:read`
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "list": [
        {
          "status_change": "创建任务，初始状态：待审核",
          "operator": "用户ID: 1, 角色: 车间地调",
          "timestamp": "2023-08-19 15:30:00",
          "note": "任务创建"
        }
      ]
    },
    "message": "获取状态历史成功"
  }
  ```
- **业务逻辑**: 
  - 获取任务的状态变更历史记录
  - 所有角色都可以查询状态历史，但需要有权限访问该任务

### 2.6 操作日志接口

#### 2.6.1 查询操作日志

- **HTTP方法**: GET
- **路径**: `/api/dispatch/tasks/{task_id}/logs`
- **权限**: `task:read`
- **查询参数**: 
  - `page`: 页码，默认1
  - `limit`: 每页数量，默认20
  - `operation_type`: 操作类型，可选
- **响应示例**: 
  ```json
  {
    "success": true,
    "data": {
      "list": [
        {
          "id": 1,
          "task_id": "T20230820001",
          "user_id": 1,
          "user_role": "车间地调",
          "operation_type": "创建任务",
          "operation_content": "创建派车任务，任务ID：T20230820001",
          "operation_time": "2023-08-19 15:30:00",
          "ip_address": "192.168.1.1"
        }
      ],
      "total": 1,
      "page": 1,
      "limit": 20
    },
    "message": "获取操作日志成功"
  }
  ```
- **业务逻辑**: 
  - 获取任务的操作日志记录
  - 调度负责人可以查看所有操作日志
  - 其他角色只能查看与自己相关的操作日志

## 3. API接口实现示例

### 3.1 创建派车任务接口实现

```python
from flask import request, jsonify
from app.models.task import ManualDispatchTask
from app.models.dispatch_status_history import DispatchStatusHistory
from app.models.operation_log import OperationLog
from app.extensions import db
from app.utils.auth import login_required, permission_required
from app.utils.common import generate_task_id, get_client_ip
from datetime import datetime

@app.route('/api/dispatch/tasks', methods=['POST'])
@login_required
@permission_required('task:create')
def create_dispatch_task():
    data = request.json
    user_id = request.user.id
    user_role = request.user.role.code
    
    # 生成任务ID
    task_id = generate_task_id()
    
    # 确定派车轨道和初始状态
    dispatch_track = data.get('dispatch_track')
    
    # 根据用户角色和派车轨道确定初始状态
    if user_role == 'workshop_dispatcher':
        # 车间地调只能使用轨道A
        dispatch_track = '轨道A'
        initial_status = '待审核'
        audit_required = True
    else:
        # 调度负责人可以选择轨道
        if dispatch_track == '轨道A':
            initial_status = '待审核'
            audit_required = True
        else:
            initial_status = '待供应商响应'
            audit_required = False
    
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
        audit_required=audit_required,
        assigned_supplier_id=data.get('assigned_supplier_id'),
        supplier_type=data.get('supplier_type'),
        current_handler_role='调度负责人' if initial_status == '待审核' else '供应商'
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
    
    return jsonify({
        'success': True,
        'data': {
            'task_id': task_id,
            'status': initial_status,
            'dispatch_track': dispatch_track,
            'current_handler_role': '调度负责人' if initial_status == '待审核' else '供应商'
        },
        'message': '派车任务创建成功'
    })
```

### 3.2 车辆合并接口实现

```python
from flask import request, jsonify
from app.models.task import ManualDispatchTask
from app.models.vehicle import Vehicle
from app.models.vehicle_merge_record import VehicleMergeRecord
from app.models.operation_log import OperationLog
from app.extensions import db
from app.utils.auth import login_required, permission_required
from app.utils.common import get_client_ip
from datetime import datetime

@app.route('/api/dispatch/vehicles/merge', methods=['POST'])
@login_required
@permission_required('workshop:merge_vehicles')
def merge_vehicles():
    data = request.json
    user_id = request.user.id
    user_role = request.user.role.code
    
    # 检查权限
    if user_role != 'workshop_dispatcher':
        return jsonify({
            'success': False,
            'message': '只有车间地调可以执行车辆合并操作'
        }), 403
    
    task_id = data.get('task_id')
    source_vehicle_ids = data.get('source_vehicle_ids')
    target_vehicle_id = data.get('target_vehicle_id')
    merge_note = data.get('merge_note')
    
    # 获取任务
    task = ManualDispatchTask.query.get(task_id)
    if not task:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    
    # 检查任务状态
    if task.status != '供应商已响应':
        return jsonify({
            'success': False,
            'message': '只有在供应商已响应状态下才能执行车辆合并操作'
        }), 400
    
    # 获取源车辆
    source_vehicles = Vehicle.query.filter(Vehicle.id.in_(source_vehicle_ids)).all()
    if len(source_vehicles) != len(source_vehicle_ids):
        return jsonify({
            'success': False,
            'message': '部分车辆不存在'
        }), 404
    
    # 获取目标车辆
    target_vehicle = Vehicle.query.get(target_vehicle_id)
    if not target_vehicle:
        return jsonify({
            'success': False,
            'message': '目标车辆不存在'
        }), 404
    
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
    
    return jsonify({
        'success': True,
        'message': '车辆合并成功'
    })
```

## 4. 总结

本文档设计了人工派车流程系统的API接口，包括任务管理接口、审核流程接口、供应商响应接口、车间确认接口、状态查询接口和操作日志接口。这些接口共同构成了完整的派车流程API体系，支持多角色协作完成派车任务。

在实际实现过程中，需要根据具体业务需求进行调整和优化，确保API接口能够满足业务需求，并保持良好的性能和可维护性。同时，需要注意接口的安全性，确保只有授权用户才能访问和操作相应的接口。