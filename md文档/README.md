# 智能运力系统

## 版权信息

© 2025 安徽邮政运输管控中心. 智能运力系统 v1.0

版权所有 © 2025 安徽邮政运输管控中心

## 架构规范

系统严格遵循四层架构设计，确保代码的可维护性和可扩展性。详细架构规范请参考 [架构规则文档](../docs/architecture_rules.md) 和 [架构检查清单](../docs/architecture_checklist.md)。

### 架构分层

1. **表现层 (Presentation Layer)**: 处理HTTP请求和响应
2. **服务层 (Service Layer)**: 实现业务逻辑
3. **数据访问层 (Data Access Layer)**: 数据模型和持久化
4. **应用层 (Application Layer)**: 应用初始化和配置

详细信息请查看 [架构规则文档](../docs/architecture_rules.md)。

## 项目概述
本项目旨在开发一套集智能化、信息化、可视化于一体的智能运力系统，实现对运输资源的高效管理和优化调度。通过整合多源数据，运用先进的数据分析和算法技术，从而提高运输效率、降低运营成本、增强服务质量，实现运输过程的全数字化管理，为运输调度提供精准的数据支持和科学的决策依据。助力安徽邮政运输管控中心实现数字化转型和可持续发展。
### 项目背景
传统的运输管理方式存在效率低、成本高、服务质量差等问题。为了提升运输效率、降低运营成本、提高服务质量，本项目应运而生。
### 项目目标
- 实现对运输资源的智能化管理，包括车辆、司机、承运商等
- 提供完善的运输任务全生命周期管理功能，包括创建、审核、分配、执行、监控、完成等
- 整合多源数据，实现数据的实时采集、处理和分析
- 运用先进的数据分析和算法技术，提供精准的运输决策支持
基于Python/Flask构建后端RESTful API，前端使用Vue.js实现单页应用，并通过服务层设计模式和数据库适配器实现了灵活的架构。

### 主要功能
- **双轨派车流程**：支持轨道A（需要审核）和轨道B（直接派车）两种模式
- **任务全生命周期管理**：从创建到完成的完整任务管理
- **多角色权限控制**：支持超级管理员、区域调度员、车间地调、供应商等多角色协作
- **车辆信息管理**：车辆基本信息和容积数据管理
- **公司管理**：承运商公司信息管理
- **状态流转**：完整的任务状态流转和历史记录

## 技术栈

### 后端技术
- **框架**：Python/Flask
- **数据库**：SQLite（支持MySQL和PostgreSQL配置）
- **认证**：Flask-Login
- **架构模式**：服务层设计模式、适配器模式
- **API风格**：RESTful

### 前端技术
- **框架**：Vue.js
- **模块化**：ES6模块化架构
- **数据交互**：Fetch API（Promise/async-await）
- **样式**：自定义CSS

## 系统架构

### 整体架构
系统采用前后端分离的架构模式，后端提供RESTful API，前端通过AJAX调用API实现数据交互。系统核心采用服务层设计模式，通过数据库适配器支持多种数据库类型，并实现了完整的权限控制体系。

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   前端应用       │     │    Flask API    │     │    数据库层       │
│  (Vue.js + ES6) │◄───►│  (服务层架构)     │◄───►│ (SQLite/MySQL)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 核心模块

#### 后端模块
- **api/**: RESTful API接口集合
- **services/**: 服务层，包含数据库服务、错误处理等
- **modules/**: 业务功能模块
- **scripts/**: 脚本工具
- **tests/**: 测试代码

#### 前端模块
- **src/**: Vue应用源码
- **static/**: 静态资源，包含ES6模块和样式

### 服务层架构
服务层是系统的核心，提供了以下关键服务：
- **DatabaseService**: 数据库服务核心组件
- **DatabaseAdapter**: 数据库适配器，统一不同数据库的操作接口
- **ErrorHandler**: 统一错误处理机制

## 数据库架构

系统支持多种数据库类型，默认使用SQLite。数据库架构主要包括以下核心表：

### 主要数据表
1. **manual_dispatch_tasks**: 派车任务表
2. **vehicles**: 车辆信息表
3. **dispatch_status_history**: 任务状态历史表
4. **User**: 用户表
5. **Role**: 角色表
6. **UserRole**: 用户角色关联表
7. **Company**: 公司表
8. **vehicle_volume_reference**: 车辆容积参考表


## 双轨派车流程

系统实现了两种派车流程，适应不同的业务场景：

### 轨道A流程（需要审核）
1. **任务创建**：车间地调创建任务
2. **待调度员审核**：任务进入审核状态
3. **审核通过**：区域调度员/超级管理员审核通过后，判断委办/自办/大容积自办任务进入待供应商/班组长/大容积响应状态
4. **响应**：供应商/班组长/大容积确认并填写车辆信息
5. **车间核实**：车间地调核实派车与实际是否相符合，进行车型降档、车辆合并、车辆确认相关工作
6. **确认**：供应商/班组长/大容积确认派车任务
5. **任务完成**：任务执行完成

### 轨道B流程（直接派车）
1. **任务创建**：区域调度员或超级管理员创建任务
2. **响应**：供应商/班组长/大容积确认并填写车辆信息
3. **车间核实**：车间地调核实派车与实际是否相符合，进行车型降档、车辆合并、车辆确认相关工作
4. **确认**：供应商/班组长/大容积确认派车任务
5. **任务完成**：任务执行完成

## 角色权限

系统支持以下角色及其权限：

| 角色 | 权限说明 |
|------|----------|
| 超级管理员 | 系统所有功能的完全访问权限 |
| 区域调度员 | 创建和管理派车任务，审核任务，分派车辆 |
| 车间地调 | 创建派车任务，查看任务状态 |
| 供应商 | 查看分配给自己的任务，确认响应任务，填写车辆信息 |

## 前端ES6模块化架构

前端采用现代ES6模块化架构，主要模块包括：

### 核心模块
- **TaskManager**: 任务管理核心模块，提供任务数据的加载、搜索、分页等功能
- **TaskRenderer**: 任务渲染模块，负责任务数据的可视化展示
- **VehicleSearch**: 车辆搜索模块，提供车辆信息搜索功能
- **manualDispatch**: 手动派车模块，实现手动派车功能

### 初始化示例
```javascript
// TaskManager初始化示例
import { TaskManager } from './modules/TaskManager.js';

const taskManager = new TaskManager({
  apiEndpoint: '/api/dispatch/tasks',
  pageSize: 10
});

// 加载任务列表
taskManager.loadTasks().then(() => {
  console.log('Tasks loaded successfully');
});

// 事件监听
taskManager.on('data-loaded', (data) => {
  console.log('Received task data:', data.tasks);
});
```

## 原项目文件结构

```
├── .gitignore              # Git忽略文件配置
├── README.md               # 项目说明文档
├── app.py                  # Flask应用入口
├── config.py               # 项目配置文件
├── api/                    # API接口模块
│   ├── __init__.py         # API初始化
│   ├── audit.py            # 审核相关API
│   ├── company.py          # 公司管理API
│   ├── decorators.py       # 装饰器（权限控制等）
│   ├── dispatch.py         # 派车任务API
│   ├── utils.py            # API工具函数
│   └── validators.py       # 数据验证器
├── services/               # 服务层模块
│   ├── __init__.py         # 服务层初始化
│   ├── connection_pool.py  # 数据库连接池
│   ├── database_adapter.py # 数据库适配器
│   ├── database_interface.py # 数据库接口定义
│   ├── database_service.py # 数据库服务
│   ├── db_connection_manager.py # 数据库连接管理
│   ├── db_data_manager.py  # 数据库数据管理
│   ├── db_factory.py       # 数据库工厂
│   ├── db_manager_compat.py # 兼容旧数据库管理器
│   ├── db_table_manager.py # 数据库表管理
│   ├── error_handler.py    # 错误处理器
│   └── sqlite_database.py  # SQLite数据库实现
├── modules/                # 业务功能模块
│   ├── basic_data/         # 基础数据管理
│   ├── cost_analysis/      # 成本分析
│   ├── planning/           # 计划管理
│   ├── reconciliation/     # 对账管理
│   ├── scheduling/         # 调度管理
│   ├── system/             # 系统管理
│   └── user_management/    # 用户管理
├── static/                 # 静态资源
│   ├── css/                # 样式文件
│   ├── js/                 # JavaScript文件
│   └── modules/            # ES6模块
├── src/                    # Vue应用源码
│   ├── App.vue             # 主应用组件
│   ├── components/         # Vue组件
│   ├── main.js             # Vue应用入口
│   └── router.js           # 路由配置
├── templates/              # Flask模板
├── scripts/                # 脚本工具
└── tests/                  # 测试代码
```

## 运行说明

### 环境要求
- Python 3.8+ 
- SQLite（默认）或MySQL/PostgreSQL
- Node.js（前端开发）

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖（前端开发）
npm install
```

### 配置环境变量

```bash
# 设置环境变量（根据需要）
set FLASK_ENV=development
set SECRET_KEY=your-secret-key
set ENABLE_NEW_DATABASE=false
```

### 启动应用

```bash
# 启动Flask应用
flask run

# 或使用Python直接运行
python app.py
```

应用将在http://localhost:5000/启动。

## 开发指南

### 调试模式
在开发环境中，可以启用调试模式以便于开发：

```bash
set FLASK_ENV=development
set FLASK_DEBUG=1
```

### 前端开发
前端使用Vue.js开发，可以使用Vite进行构建：

```bash
# 开发模式启动
npm run dev

# 构建生产版本
npm run build
```

### 架构验证
为确保代码符合架构规范，提供了以下验证命令：

```bash
# 架构检查
make guard

# 架构验证
make validate

# 代码质量检查
make lint

# 代码格式化
make format
```

详细的任务执行规范请参考 [任务执行计划文档](../docs/task_execution_plan.md)。

### 数据库迁移
如需切换数据库或执行数据库迁移，请参考DATABASE_MIGRATION_GUIDE.md文件。

## 版本历史

### v1.01 (2025-08-10)
- 基础功能开发完成
- 实现TaskManagement核心模块

### v1.02 (2025-08-11)
- 实现时间优先级系统
- 更新TaskManager模块
- 添加TaskRenderer模块

### v1.03 (2025-08-12)
- 优化用户体验
- 修复已知问题

### v1.04 (2025-08-13)
- 文件变更：新增API_DESIGN.md和DATABASE_DESIGN.md
- 更新派车API：支持车辆容积信息的保存和查询

### v1.05 (2025-08-14)
- 新增功能特性：
  - 时间优先级计算：支持基于时间的任务优先级排序
  - 车辆容积数据：扩展车辆管理功能

### v1.06.0 (2025-08-15)
- ES6模块化完成：前端模块重构完成
- 服务层架构优化：数据库服务层重构
- 角色权限细化：完善多角色权限管理

### v2.0 (2025-08-15)
- 双轨派车功能：实现轨道A和轨道B的派车流程
- 系统集成：完成核心模块集成

### v2.1 (2025-08-16)
- 状态命名统一：统一任务状态命名规范
- 数据库迁移：开始从DatabaseManagerCompat迁移到SQLiteDatabase

## 文档目录

- **README.md**: 项目主文档
- **docs/SMART_TRANSPORT_SYSTEM/ALIGNMENT_SMART_TRANSPORT_SYSTEM.md**: 项目对齐文档
- **docs/SMART_TRANSPORT_SYSTEM/ARCHITECTURE_SMART_TRANSPORT_SYSTEM.md**: 项目架构文档
- **docs/SMART_TRANSPORT_SYSTEM/ATOM_TASKS_SMART_TRANSPORT_SYSTEM.md**: 原子任务文档
- **docs/SMART_TRANSPORT_SYSTEM/ASSESSMENT_SMART_TRANSPORT_SYSTEM.md**: 项目评估文档
- **md文档/API_DESIGN.md**: API设计文档
- **md文档/DATABASE_DESIGN.md**: 数据库设计文档
