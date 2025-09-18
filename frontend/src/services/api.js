import { ElMessage } from 'element-plus'
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1', // 通过Vite代理避免CORS
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
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status
    const requestUrl = originalRequest?.url || ''
    const currentPath = window.location?.pathname || ''

    // 统一处理错误响应，确保错误信息结构一致
    const errorResponse = {
      code: status || 500,
      message: error.response?.data?.message || error.message || '请求失败',
      data: error.response?.data
    }

    // 401 未授权处理
    if (status === 401 && !originalRequest._retry) {
      // 对于登录接口或当前已在登录页，避免重定向，防止页面重载导致提示秒闪
      const isLoginRequest = requestUrl.includes('/auth/login')
      const alreadyOnLogin = currentPath === '/login'

      if (isLoginRequest || alreadyOnLogin) {
        return Promise.reject(errorResponse)
      }

      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // 尝试刷新token
        const refreshToken = localStorage.getItem('refreshToken') // 假设有refreshToken
        if (!refreshToken) {
          // 没有refreshToken，直接跳转登录
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return Promise.reject(errorResponse)
        }
        
        // 实际的刷新token请求，这里需要根据后端接口调整
        const refreshResponse = await axios.post('/api/v1/auth/refresh', { refreshToken })
        const newToken = refreshResponse.data.token
        localStorage.setItem('token', newToken)
        processQueue(null, newToken)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(errorResponse)
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(errorResponse)
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