# 角色菜单权限系统架构设计

## 系统架构概览

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation Layer)                │
├─────────────────────────────────────────────────────────────┤
│  Vue组件  │  权限指令  │  路由守卫  │  权限配置界面  │  动态菜单  │
├─────────────────────────────────────────────────────────────┤
│                     应用层 (Application Layer)               │
├─────────────────────────────────────────────────────────────┤
│  权限API  │  菜单API  │  角色API  │  权限中间件  │  JWT验证   │
├─────────────────────────────────────────────────────────────┤
│                     服务层 (Service Layer)                   │
├─────────────────────────────────────────────────────────────┤
│ 权限服务  │ 菜单服务  │ 角色服务  │ 缓存服务  │ 权限验证服务 │
├─────────────────────────────────────────────────────────────┤
│                     数据层 (Data Layer)                      │
├─────────────────────────────────────────────────────────────┤
│   User   │   Role   │ Permission │   Menu   │ RolePermission │
└─────────────────────────────────────────────────────────────┘
```

## 数据模型设计

### 核心实体关系图
```
User ──────┐
           │ M:N
           ▼
        UserRole ────── Role ──────┐
                                   │ M:N  
                                   ▼
                            RolePermission ────── Permission
                                                      │
                                                      │ 1:N
                                                      ▼
                                                    Menu
```

### 数据表结构

#### 1. permissions 表（权限表）
```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,           -- 权限名称
    code VARCHAR(50) NOT NULL UNIQUE,            -- 权限代码
    description TEXT,                            -- 权限描述
    resource_type VARCHAR(20) NOT NULL,          -- 资源类型: menu, api, button
    resource_id VARCHAR(100),                    -- 资源标识
    action VARCHAR(20) NOT NULL,                 -- 操作类型: read, write, delete, execute
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. menus 表（菜单表）
```sql
CREATE TABLE menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,                  -- 菜单名称
    code VARCHAR(50) NOT NULL UNIQUE,            -- 菜单代码
    path VARCHAR(200),                           -- 路由路径
    component VARCHAR(200),                      -- 组件路径
    icon VARCHAR(50),                            -- 图标
    parent_id INTEGER,                           -- 父菜单ID
    sort_order INTEGER DEFAULT 0,               -- 排序
    is_active BOOLEAN DEFAULT TRUE,              -- 是否启用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES menus(id)
);
```

#### 3. role_permissions 表（角色权限关联表）
```sql
CREATE TABLE role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,                          -- 授权人ID
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(role_id, permission_id)
);
```

#### 4. menu_permissions 表（菜单权限关联表）
```sql
CREATE TABLE menu_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(menu_id, permission_id)
);
```

## 后端API设计

### 权限管理API

#### 1. 权限CRUD接口
```python
# GET /api/v1/permissions - 获取权限列表
# POST /api/v1/permissions - 创建权限
# PUT /api/v1/permissions/{id} - 更新权限
# DELETE /api/v1/permissions/{id} - 删除权限
# GET /api/v1/permissions/{id} - 获取权限详情
```

#### 2. 菜单管理接口
```python
# GET /api/v1/menus - 获取菜单树
# POST /api/v1/menus - 创建菜单
# PUT /api/v1/menus/{id} - 更新菜单
# DELETE /api/v1/menus/{id} - 删除菜单
# GET /api/v1/menus/user/{user_id} - 获取用户权限菜单
```

#### 3. 角色权限接口
```python
# GET /api/v1/roles/{role_id}/permissions - 获取角色权限
# POST /api/v1/roles/{role_id}/permissions - 批量分配权限
# DELETE /api/v1/roles/{role_id}/permissions/{permission_id} - 移除权限
# GET /api/v1/users/{user_id}/permissions - 获取用户所有权限
```

### 权限验证中间件设计

```python
from functools import wraps
from flask import request, jsonify, g
from app.services.permission_service import PermissionService

def require_permission(permission_code):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 从JWT token获取用户信息
            user_id = g.current_user.id
            
            # 验证用户是否具有指定权限
            if not PermissionService.check_user_permission(user_id, permission_code):
                return jsonify({
                    'code': 403,
                    'message': '权限不足',
                    'data': None
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 使用示例
@bp.route('/users', methods=['POST'])
@require_permission('user:create')
def create_user():
    pass
```

## 前端架构设计

### 权限管理组件结构

```
src/
├── components/
│   ├── Permission/
│   │   ├── PermissionTree.vue          # 权限树组件
│   │   ├── RolePermissionConfig.vue    # 角色权限配置
│   │   └── MenuPermissionConfig.vue    # 菜单权限配置
│   └── Layout/
│       ├── DynamicMenu.vue             # 动态菜单组件
│       └── PermissionButton.vue        # 权限按钮组件
├── directives/
│   └── permission.js                   # 权限指令
├── guards/
│   └── permission.js                   # 路由权限守卫
├── services/
│   └── permission.js                   # 权限服务
└── stores/
    └── permission.js                   # 权限状态管理
```

### 动态菜单组件设计

```vue
<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="isCollapse"
    :unique-opened="false"
    class="el-menu-vertical"
    router
  >
    <menu-item
      v-for="menu in userMenus"
      :key="menu.id"
      :menu="menu"
    />
  </el-menu>
</template>

<script>
import { computed } from 'vue'
import { usePermissionStore } from '@/stores/permission'
import MenuItem from './MenuItem.vue'

export default {
  name: 'DynamicMenu',
  components: { MenuItem },
  setup() {
    const permissionStore = usePermissionStore()
    
    const userMenus = computed(() => {
      return permissionStore.getUserMenus()
    })
    
    return {
      userMenus
    }
  }
}
</script>
```

### 权限指令设计

```javascript
// src/directives/permission.js
import { usePermissionStore } from '@/stores/permission'

export default {
  mounted(el, binding) {
    const { value } = binding
    const permissionStore = usePermissionStore()
    
    if (value) {
      const hasPermission = permissionStore.checkPermission(value)
      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  },
  updated(el, binding) {
    const { value, oldValue } = binding
    if (value !== oldValue) {
      // 权限变更时重新检查
      this.mounted(el, binding)
    }
  }
}

// 使用示例
// <el-button v-permission="'user:create'">添加用户</el-button>
```

### 路由权限守卫

```javascript
// src/guards/permission.js
import { usePermissionStore } from '@/stores/permission'
import { ElMessage } from 'element-plus'

export function setupPermissionGuard(router) {
  router.beforeEach(async (to, from, next) => {
    const permissionStore = usePermissionStore()
    
    // 检查路由是否需要权限验证
    if (to.meta.requiresAuth) {
      const requiredPermission = to.meta.permission
      
      if (requiredPermission) {
        const hasPermission = await permissionStore.checkPermission(requiredPermission)
        
        if (!hasPermission) {
          ElMessage.error('您没有访问该页面的权限')
          next('/403')
          return
        }
      }
    }
    
    next()
  })
}
```

## 权限缓存策略

### 后端缓存设计

```python
from flask_caching import Cache
from app.extensions import cache

class PermissionService:
    @staticmethod
    @cache.memoize(timeout=300)  # 缓存5分钟
    def get_user_permissions(user_id):
        """获取用户权限列表（带缓存）"""
        # 查询用户所有角色的权限
        permissions = db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            UserRole, RolePermission.role_id == UserRole.role_id
        ).filter(
            UserRole.user_id == user_id
        ).all()
        
        return [p.code for p in permissions]
    
    @staticmethod
    def clear_user_permission_cache(user_id):
        """清除用户权限缓存"""
        cache_key = f'get_user_permissions_{user_id}'
        cache.delete(cache_key)
```

### 前端缓存设计

```javascript
// src/stores/permission.js
import { defineStore } from 'pinia'
import { permissionApi } from '@/services/api'

export const usePermissionStore = defineStore('permission', {
  state: () => ({
    permissions: [],
    menus: [],
    roles: [],
    lastUpdateTime: null
  }),
  
  getters: {
    hasPermission: (state) => (permission) => {
      return state.permissions.includes(permission)
    },
    
    getUserMenus: (state) => () => {
      return buildMenuTree(state.menus)
    }
  },
  
  actions: {
    async loadUserPermissions() {
      try {
        const response = await permissionApi.getUserPermissions()
        this.permissions = response.data.permissions
        this.menus = response.data.menus
        this.roles = response.data.roles
        this.lastUpdateTime = Date.now()
      } catch (error) {
        console.error('加载用户权限失败:', error)
      }
    },
    
    checkPermission(permission) {
      return this.permissions.includes(permission)
    },
    
    clearPermissions() {
      this.permissions = []
      this.menus = []
      this.roles = []
      this.lastUpdateTime = null
    }
  }
})
```

## 安全机制设计

### 1. JWT Token权限信息

```python
# 在JWT payload中包含权限信息
def generate_token(user):
    permissions = PermissionService.get_user_permissions(user.id)
    payload = {
        'user_id': user.id,
        'username': user.username,
        'permissions': permissions,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
```

### 2. 权限验证层级

```
第一层：路由守卫（前端）
    ↓
第二层：组件权限指令（前端）
    ↓
第三层：API权限中间件（后端）
    ↓
第四层：数据库权限验证（后端）
```

### 3. 权限日志审计

```python
class PermissionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50))  # 操作类型
    resource = db.Column(db.String(100))  # 资源
    permission = db.Column(db.String(50))  # 权限代码
    result = db.Column(db.String(20))  # 结果: success, denied
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 性能优化策略

### 1. 数据库优化
- 为权限查询添加复合索引
- 使用数据库视图简化复杂权限查询
- 权限数据预加载和批量查询

### 2. 缓存优化
- Redis缓存用户权限信息
- 菜单结构缓存
- 权限验证结果缓存

### 3. 前端优化
- 权限数据懒加载
- 菜单组件虚拟滚动
- 权限状态本地存储

## 扩展性设计

### 1. 权限模板
- 预定义角色权限模板
- 支持权限模板的导入导出
- 批量权限配置功能

### 2. 多租户支持
- 租户级权限隔离
- 跨租户权限共享机制
- 租户权限继承策略

### 3. 动态权限
- 运行时权限注册
- 插件化权限扩展
- 权限规则引擎

## 总结

本架构设计基于RBAC模型，采用四层架构模式，确保了权限系统的安全性、性能和扩展性。通过完善的缓存机制、多层权限验证和审计日志，为系统提供了可靠的权限管控能力。