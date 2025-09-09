# 前端用户管理422错误解决方案

## 问题描述

前端访问用户管理页面时出现 "获取用户列表失败: Request failed with status code 422" 错误。

## 问题原因

用户管理和角色管理的API接口都需要JWT认证，但前端用户没有登录获取有效的token。

## 解决方案

### 方案1：使用登录功能（推荐）

1. **访问登录页面**
   - 打开浏览器访问：http://localhost:3000/login
   - 或者直接访问：http://localhost:3000/ （会自动重定向到登录页）

2. **使用测试账户登录**
   
   我们已经创建了以下测试账户：
   
   | 用户名 | 密码 | 角色 | 说明 |
   |--------|------|------|------|
   | admin | admin123 | 超级管理员 | 拥有所有权限 |
   | dispatcher | 123456 | 区域调度员 | 调度管理权限 |
   | operator | 123456 | 车间地调 | 基础操作权限 |
   | supplier | 123456 | 供应商 | 供应商权限 |

3. **登录后访问用户管理**
   - 登录成功后，点击左侧菜单的"系统管理" → "用户管理"
   - 或直接访问：http://localhost:3000/settings/user

### 方案2：API测试（开发调试用）

如果需要直接测试API接口，可以使用以下方法：

1. **获取JWT Token**
   ```bash
   cd backend
   python get_token.py
   ```

2. **使用Token测试API**
   ```bash
   # 获取用户列表
   curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:5000/api/v1/users
   
   # 获取角色列表
   curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:5000/api/v1/roles
   ```

### 方案3：临时移除认证（仅开发环境）

⚠️ **注意：此方案仅用于开发调试，生产环境不建议使用**

如果需要临时移除JWT认证要求，可以：

1. 编辑 `backend/app/api/v1/user_management.py`
2. 注释掉所有的 `@jwt_required()` 装饰器
3. 编辑 `backend/app/api/v1/role_management.py`
4. 注释掉所有的 `@jwt_required()` 装饰器
5. 重启后端服务

## 验证解决方案

### 1. 登录验证

1. 访问 http://localhost:3000/login
2. 使用 admin/admin123 登录
3. 登录成功后应该跳转到仪表盘页面
4. 检查浏览器开发者工具的 localStorage 中是否有 token

### 2. 用户管理功能验证

1. 点击左侧菜单"系统管理" → "用户管理"
2. 应该能看到用户列表，包含4个测试用户
3. 尝试添加、编辑、删除用户功能
4. 测试角色分配功能

### 3. 角色管理功能验证

1. 点击左侧菜单"系统管理" → "角色管理"
2. 应该能看到5个默认角色
3. 尝试添加、编辑角色功能
4. 检查用户数统计是否正确

## 技术说明

### JWT认证流程

1. **登录**：用户提交用户名和密码
2. **验证**：后端验证用户凭据
3. **生成Token**：验证成功后生成JWT token
4. **存储Token**：前端将token存储在localStorage中
5. **请求认证**：后续API请求在Header中携带token
6. **验证Token**：后端验证token有效性

### API认证Header格式

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token有效期

- 默认有效期：1小时（3600秒）
- Token过期后需要重新登录
- 前端会自动处理token过期情况

## 常见问题

### Q1: 登录后仍然提示422错误

**解决方法**：
1. 检查浏览器开发者工具的Network标签
2. 查看请求头是否包含Authorization字段
3. 清除浏览器缓存和localStorage
4. 重新登录

### Q2: Token过期怎么办

**解决方法**：
1. 重新登录获取新token
2. 或者实现token自动刷新机制（后续优化）

### Q3: 忘记测试账户密码

**解决方法**：
1. 查看本文档中的测试账户表格
2. 或者运行 `python init_db.py` 重新初始化数据库

## 后续优化建议

1. **Token自动刷新**：实现token即将过期时自动刷新
2. **记住登录状态**：实现"记住我"功能
3. **单点登录**：集成企业SSO系统
4. **权限细化**：基于角色的细粒度权限控制

## 总结

422错误是由于缺少JWT认证token导致的。通过登录获取有效token后，用户管理和角色管理功能都能正常使用。建议使用admin账户登录测试所有功能。