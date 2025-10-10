# ARCHITECTURE_调度仪表盘

## 系统架构设计

### 1. 四层架构设计

#### 数据层（Data Layer）
- **实体模型**: ManualDispatchTask (已存在)
- **数据访问**: 通过SQLAlchemy ORM进行统计查询
- **查询优化**: 添加必要的数据库索引

#### 服务层（Service Layer）
- **DashboardService**: 仪表盘数据统计服务
  - get_task_statistics(): 获取任务统计概览
  - get_status_distribution(): 获取状态分布数据
  - get_track_distribution(): 获取轨道类型分布
  - get_urgent_tasks(): 获取紧急任务列表

#### 应用层（Application Layer）
- **DashboardAPI**: 提供RESTful API接口
  - GET /api/v1/dispatch/dashboard/statistics
  - GET /api/v1/dispatch/dashboard/distributions
  - GET /api/v1/dispatch/dashboard/urgent-tasks

#### 表现层（Presentation Layer）
- **Vue组件**: DispatchDashboard.vue
  - 统计卡片组件
  - 饼图/柱状图组件
  - 任务列表组件

### 2. 数据流设计
```
前端请求 → 路由分发 → API控制器 → 服务层 → 数据层 → 返回数据 → 前端渲染
```

### 3. 接口设计

#### 统计概览接口
```json
{
  "total_tasks": 150,
  "today_new_tasks": 5,
  "expiring_tasks": 3
}
```

#### 分布数据接口
```json
{
  "status_distribution": [
    {"status": "待审核", "count": 20},
    {"status": "审核通过", "count": 50}
  ],
  "track_distribution": [
    {"track": "轨道A", "count": 80},
    {"track": "轨道B", "count": 70}
  ]
}
```

#### 紧急任务接口
```json
[
  {
    "task_id": "TASK001",
    "route_name": "北京-上海",
    "status": "待审核",
    "created_at": "2024-01-01 10:00:00",
    "urgency_level": "high"
  }
]
```

### 4. 技术方案选择
- **图表库**: 使用ECharts或AntV G2
- **日期处理**: 使用day.js
- **状态管理**: Vuex存储仪表盘数据

### 5. 安全考虑
- 添加权限验证装饰器
- 数据访问权限控制
- API速率限制

### 6. 性能优化
- 数据库查询添加索引
- 使用缓存机制
- 分页加载大数据集