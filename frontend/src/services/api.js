import { ElMessage } from 'element-plus'
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}/api/v1` : '/api/v1', // 通过Vite代理避免CORS
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

let isRefreshing = false // 标记是否正在刷新token
let failedQueue = [] // 存储失败的请求

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    
    // 401 未授权错误处理
    if (error.response?.status === 401) {
      // 如果是登录请求失败，直接返回错误
      if (originalRequest.url?.includes('/auth/login')) {
        return Promise.reject(error.response?.data || error)
      }
      
      // 如果已经在登录页，不需要重定向
      if (window.location.pathname === '/login') {
        return Promise.reject(error.response?.data || error)
      }
      
      // 如果正在刷新token，将请求加入队列
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }
      
      // 尝试刷新token
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken && !originalRequest._retry) {
        originalRequest._retry = true
        isRefreshing = true
        
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
          })
          
          const { access_token } = response.data
          localStorage.setItem('token', access_token)
          
          // 处理队列中的请求
          processQueue(null, access_token)
          
          // 重试原请求
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // 刷新失败，清除认证信息并跳转登录
          processQueue(refreshError, null)
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          
          // 清除权限store
          const { usePermissionStore } = await import('@/stores/permission')
          const permissionStore = usePermissionStore()
          permissionStore.clearPermissions()
          
          // 跳转到登录页
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        // 没有refreshToken或已经重试过，清除认证信息并跳转登录
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        
        // 清除权限store
        const { usePermissionStore } = await import('@/stores/permission')
        const permissionStore = usePermissionStore()
        permissionStore.clearPermissions()
        
        window.location.href = '/login'
      }
    }
    
    // 403 权限不足错误处理
    if (error.response?.status === 403) {
      console.warn('权限不足:', error.response?.data?.message || '您没有权限执行此操作')
      // 不自动跳转，让组件自己处理权限错误
    }
    
    // 其他错误直接返回
    return Promise.reject(error.response?.data || error)
  }
)

// 导出API服务对象
export const apiService = {
  // 通用HTTP方法
  get: (url, config = {}) => api.get(url, config),
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),
  patch: (url, data = {}, config = {}) => api.patch(url, data, config),
  
  // 认证相关API
  auth: {
    // 用户登录
    login: (username, password) => {
      return api.post('/auth/login', { username, password })
    },
    
    // 用户登出
    logout: () => {
      return api.post('/auth/logout')
    },
    
    // 获取用户信息
    getUserInfo: () => {
      return api.get('/auth/userinfo')
    }
  },
  
  // 基础数据相关API
  basicData: {
    // 获取车辆列表
    getVehicles: () => {
      return api.get('/vehicles')
    },
    
    // 获取司机列表
    getDrivers: () => {
      return api.get('/basic_data/drivers')
    },
    
    // 获取派车单位列表
    getDispatchUnits: (params) => {
      return api.get('/dispatch-units', { params })
    }
  },
  
  // 调度相关API
  dispatch: {
    // 获取运输订单列表
    getOrders: () => {
      return api.get('/dispatch/orders')
    },
    
    // 创建调度任务
    createDispatch: (dispatchData) => {
      return api.post('/dispatch/dispatch', dispatchData)
    },
    
    // 获取运输跟踪信息
    getTrackingInfo: (dispatchId) => {
      return api.get(`/dispatch/tracking/${dispatchId}`)
    }
  },
  
  // 用户管理相关API
  users: {
    // 获取用户列表
    getUsers: (params) => {
      return api.get('/users', { params })
    },
    
    // 获取用户详情
    getUser: (userId) => {
      return api.get(`/users/${userId}`)
    },
    
    // 创建用户
    createUser: (userData) => {
      return api.post('/users', userData)
    },
    
    // 更新用户
    updateUser: (userId, userData) => {
      return api.put(`/users/${userId}`, userData)
    },
    
    // 删除用户
    deleteUser: (userId) => {
      return api.delete(`/users/${userId}`)
    }
  },
  
  // 角色管理相关API
  roles: {
    // 获取角色列表
    getRoles: () => {
      return api.get('/roles')
    },
    
    // 获取角色详情
    getRole: (roleId) => {
      return api.get(`/roles/${roleId}`)
    },
    
    // 创建角色
    createRole: (roleData) => {
      return api.post('/roles', roleData)
    },
    
    // 更新角色
    updateRole: (roleId, roleData) => {
      return api.put(`/roles/${roleId}`, roleData)
    },
    
    // 删除角色
    deleteRole: (roleId) => {
      return api.delete(`/roles/${roleId}`)
    },
    
    // 获取用户的角色
    getUserRolesApi: (userId) => {
      return api.get(`/roles/users/${userId}/roles`)
    },
    
    // 为用户分配角色
    assignRoleToUserApi: (userId, roleId) => {
      return api.post(`/roles/users/${userId}/roles`, { role_id: roleId })
    },
    
    // 移除用户的角色
    removeRoleFromUserApi: (userId, roleId) => {
      return api.delete(`/roles/users/${userId}/roles/${roleId}`)
    },
    
    // 获取角色权限
    getRolePermissions: (roleId) => {
      return api.get(`/role-permissions/roles/${roleId}/permissions`)
    },
    
    // 更新角色权限
    updateRolePermissions: (roleId, permissionData) => {
      return api.put(`/role-permissions/roles/${roleId}/permissions`, permissionData)
    },
    
    // 获取角色菜单权限
    getRoleMenus: (roleId) => {
      return api.get(`/roles/${roleId}/menus`)
    },
    
    // 更新角色菜单权限
    updateRoleMenus: (roleId, menuData) => {
      return api.put(`/roles/${roleId}/menus`, menuData)
    }
  },
  
  // 菜单管理相关API
  menus: {
    // 获取所有菜单
    getMenus: (params = {}) => {
      return api.get('/menus', { params })
    },
    
    // 获取菜单详情
    getMenu: (menuId) => {
      return api.get(`/menus/${menuId}`)
    },
    
    // 创建菜单
    createMenu: (menuData) => {
      return api.post('/menus', menuData)
    },
    
    // 更新菜单
    updateMenu: (menuId, menuData) => {
      return api.put(`/menus/${menuId}`, menuData)
    },
    
    // 删除菜单
    deleteMenu: (menuId) => {
      return api.delete(`/menus/${menuId}`)
    },
    
    // 获取当前用户菜单
    getCurrentUserMenus: () => {
      return api.get('/menus/current-user')
    }
  },
  
  // 权限管理相关API
  permissions: {
    // 获取权限列表
    getPermissions: (params) => {
      return api.get('/permissions', { params })
    },
    
    // 获取权限详情
    getPermission: (permissionId) => {
      return api.get(`/permissions/${permissionId}`)
    },
    
    // 创建权限
    createPermission: (permissionData) => {
      return api.post('/permissions', permissionData)
    },
    
    // 更新权限
    updatePermission: (permissionId, permissionData) => {
      return api.put(`/permissions/${permissionId}`, permissionData)
    },
    
    // 删除权限
    deletePermission: (permissionId) => {
      return api.delete(`/permissions/${permissionId}`)
    }
  }
}

export default api