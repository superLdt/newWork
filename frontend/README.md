# 智能运力系统前端

## 项目概述

这是智能运力系统的前端部分，基于Vue 3 + JavaScript技术栈构建，使用Element Plus组件库实现现代化的用户界面。

## 技术栈

- Vue 3 (Composition API)
- JavaScript
- Element Plus UI 组件库
- Vue Router
- Vite 构建工具

## 项目结构

```
src/
├── components/          # 公共组件
├── layouts/             # 布局组件
├── pages/               # 页面组件
│   ├── settings/        # 系统设置相关页面
│   └── ...              # 其他业务页面
├── router/              # 路由配置
├── App.vue             # 根组件
└── main.js             # 入口文件
```

## 开发环境搭建

### 前置条件

- Node.js 16+ 版本
- npm 或 yarn 包管理器

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

默认访问地址: http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## Element Plus 图标使用

项目已全局注册所有 Element Plus 图标，可以直接在模板中使用：

```vue
<template>
  <el-icon><User /></el-icon>
  <el-icon><Setting /></el-icon>
</template>
```

## 路由结构

- `/login` - 登录页面
- `/` - 主界面布局
  - `/` - 仪表盘
  - `/settings/user` - 用户管理
  - `/settings/role` - 角色管理
  - `/settings/config` - 系统配置
  - `/settings/logs` - 审计日志
  - 其他功能页面使用 ComingSoon 组件占位

## 开发规范

1. 组件命名采用 PascalCase 格式
2. 使用 Element Plus 组件库构建界面
3. 遵循项目现有的样式和布局规范
4. 图标统一使用 Element Plus 图标组件

## 注意事项

1. 所有页面组件应放置在 `src/pages/` 目录下
2. 公共组件应放置在 `src/components/` 目录下
3. 路由配置在 `src/router/index.js` 文件中维护
4. 样式类名遵循 BEM 命名规范