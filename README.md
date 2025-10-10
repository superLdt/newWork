# 智能运力系统

## 项目概述

智能运力系统是一个专注于车辆调度和运输管理的综合平台，旨在提高运输效率、优化资源配置，实现智能化的运输调度管理。系统采用前后端分离架构，提供了完整的用户权限管理、车辆管理、调度管理等功能模块。

## 技术栈

### 后端
- Flask 2.3.3
- SQLAlchemy
- JWT认证
- Celery异步任务

### 前端
- Vue 3
- Element Plus
- Pinia
- Vue Router
- ECharts

## 快速开始

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 初始化数据库
```bash
python -m flask db upgrade
```

4. 启动服务
```bash
python run.py
```

### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 开发模式启动
```bash
npm run dev
```

4. 构建生产版本
```bash
npm run build
```

## 系统功能

- **用户权限管理**：基于RBAC的权限控制
- **车辆管理**：车辆信息维护、容积/吨位管理
- **调度管理**：手动派车任务创建、调度状态流转
- **基础数据管理**：组织单位管理、吨位容积映射管理

## 项目结构

```
newCheguan/
├── backend/              # 后端代码
│   ├── app/              # 应用主目录
│   ├── migrations/       # 数据库迁移
│   ├── scripts/          # 脚本工具
│   └── tests/            # 测试用例
├── frontend/             # 前端代码
│   ├── src/              # 源代码
│   └── dist/             # 构建输出
├── docs/                 # 项目文档
└── md文档/               # 项目总结文档
```

## 文档资源

- [项目总结](md文档/PROJECT_SUMMARY.md)
- [API设计文档](md文档/API_DESIGN.md)
- [数据库设计文档](md文档/DATABASE_DESIGN.md)

## 开发团队

- 智能运力系统开发团队

## 许可证

MIT