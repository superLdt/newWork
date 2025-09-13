import { apiClient } from './apiClient'

/**
 * 派车单位服务
 */
export const dispatchUnitService = {
  /**
   * 获取派车单位列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  async getDispatchUnitList(params = {}) {
    try {
      const response = await apiClient.get('/dispatch-units/', { params })
      
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
          message: response.message || '获取派车单位列表失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取派车单位列表失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 获取派车单位详情
   * @param {number} unitId - 派车单位ID
   * @returns {Promise}
   */
  async getDispatchUnitDetail(unitId) {
    try {
      const response = await apiClient.get(`/dispatch-units/${unitId}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取派车单位详情失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取派车单位详情失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 创建派车单位
   * @param {Object} unitData - 派车单位数据
   * @returns {Promise}
   */
  async createDispatchUnit(unitData) {
    try {
      const response = await apiClient.post('/dispatch-units/', unitData)
      
      if (response.code === 0 || response.code === 200 || response.code === 201 || response.success) {
        return {
          code: 0,
          message: response.message || '创建成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '创建派车单位失败',
          data: null
        }
      }
    } catch (error) {
      console.error('创建派车单位失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 更新派车单位
   * @param {number} unitId - 派车单位ID
   * @param {Object} unitData - 派车单位数据
   * @returns {Promise}
   */
  async updateDispatchUnit(unitId, unitData) {
    try {
      const response = await apiClient.put(`/dispatch-units/${unitId}`, unitData)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '更新成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '更新派车单位失败',
          data: null
        }
      }
    } catch (error) {
      console.error('更新派车单位失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 删除派车单位
   * @param {number} unitId - 派车单位ID
   * @returns {Promise}
   */
  async deleteDispatchUnit(unitId) {
    try {
      const response = await apiClient.delete(`/dispatch-units/${unitId}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '删除成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '删除派车单位失败',
          data: null
        }
      }
    } catch (error) {
      console.error('删除派车单位失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 获取激活的派车单位列表
   * @returns {Promise}
   */
  async getActiveDispatchUnits() {
    try {
      const response = await apiClient.get('/dispatch-units/active')
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取激活派车单位列表失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取激活派车单位列表失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  }
}