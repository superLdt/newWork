import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1', // 后端API基础URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

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
  (error) => {
    if (error.response && error.response.status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    
    // 统一处理错误响应，确保错误信息结构一致
    const errorResponse = {
      code: error.response?.status || 500,
      message: error.response?.data?.message || error.message || '请求失败',
      data: error.response?.data
    }
    
    return Promise.reject(errorResponse)
  }
)

// API服务对象
export const apiService = {
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
      return api.get('/basic_data/vehicles')
    },
    
    // 获取司机列表
    getDrivers: () => {
      return api.get('/basic_data/drivers')
    },
    
    // 获取客户列表
    getCustomers: () => {
      return api.get('/basic_data/customers')
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
    getUserRoles: (userId) => {
      return api.get(`/users/${userId}/roles`)
    },
    
    // 为用户分配角色
    assignRoleToUser: (userId, roleId) => {
      return api.post(`/users/${userId}/roles/${roleId}`)
    },
    
    // 移除用户的角色
    removeRoleFromUser: (userId, roleId) => {
      return api.delete(`/users/${userId}/roles/${roleId}`)
    }
  }
}

export default api