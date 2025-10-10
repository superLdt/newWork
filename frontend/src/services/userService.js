import { apiClient } from './apiClient'

/**
 * 用户管理服务
 */
export const userService = {
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  async getUserList(params = {}) {
    try {
      const response = await apiClient.get('/users/', { params })
      
      // 统一成功判定和返回格式
      if (response.code === 0 || response.code === 200 || response.code === 201 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取用户列表失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 获取用户详情
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  async getUserDetail(userId) {
    try {
      const response = await apiClient.get(`/users/${userId}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取用户详情失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取用户详情失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 创建用户
   * @param {Object} userData - 用户数据
   * @returns {Promise}
   */
  async createUser(userData) {
    try {
      const response = await apiClient.post('/users/', userData)
      
      if (response.code === 0 || response.code === 200 || response.code === 201 || response.success) {
        return {
          code: 0,
          message: response.message || '创建成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '创建用户失败',
          data: null
        }
      }
    } catch (error) {
      console.error('创建用户失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 更新用户
   * @param {number} userId - 用户ID
   * @param {Object} userData - 用户数据
   * @returns {Promise}
   */
  async updateUser(userId, userData) {
    try {
      const response = await apiClient.put(`/users/${userId}`, userData)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '更新成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '更新用户失败',
          data: null
        }
      }
    } catch (error) {
      console.error('更新用户失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 删除用户
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  async deleteUser(userId) {
    try {
      const response = await apiClient.delete(`/users/${userId}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '删除成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '删除用户失败',
          data: null
        }
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 绑定用户到派车单位
   * @param {number} userId - 用户ID
   * @param {number} dispatchUnitId - 派车单位ID
   * @returns {Promise}
   */
  async bindUserToDispatchUnit(userId, dispatchUnitId) {
    try {
      const response = await apiClient.post(`/users/${userId}/bind-dispatch-unit`, {
        dispatch_unit_id: dispatchUnitId
      })
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '绑定成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '绑定失败',
          data: null
        }
      }
    } catch (error) {
      console.error('绑定用户到派车单位失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 根据派车单位获取用户列表
   * @param {number} dispatchUnitId - 派车单位ID
   * @returns {Promise}
   */
  async getUsersByDispatchUnit(dispatchUnitId) {
    try {
      const response = await apiClient.get(`/users/by-dispatch-unit/${dispatchUnitId}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取用户列表失败',
          data: null
        }
      }
    } catch (error) {
      console.error('根据派车单位获取用户列表失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  }
}

export default userService