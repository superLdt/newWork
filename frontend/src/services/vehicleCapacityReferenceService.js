import { apiClient } from './apiClient';

/**
 * 车辆容积参考服务
 * 用于车辆日常管理，不关联具体派车任务
 */
export const vehicleCapacityReferenceService = {
  /**
   * 获取车辆容积参考列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {string} params.query - 搜索关键词
   * @returns {Promise} - 返回车辆列表数据
   */
  async getVehicleList(params) {
    try {
      const response = await apiClient.get('/vehicle-capacity-reference', { params })
      
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
          message: response.message || '获取车辆列表失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取车辆列表失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  },

  /**
   * 获取车辆详情
   * @param {string} id - 车辆ID
   * @returns {Promise} - 返回车辆详情数据
   */
  async getVehicleDetail(id) {
    try {
      const response = await apiClient.get(`/vehicle-capacity-reference/${id}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取车辆详情失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取车辆详情失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 创建车辆容积参考
   * @param {Object} vehicleData - 车辆数据
   * @returns {Promise} - 返回创建结果
   */
  async createVehicle(vehicleData) {
    try {
      const response = await apiClient.post('/vehicle-capacity-reference', vehicleData)
      
      if (response.code === 0 || response.code === 200 || response.code === 201 || response.success) {
        return {
          code: 0,
          message: response.message || '创建成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '创建车辆失败',
          data: null
        }
      }
    } catch (error) {
      console.error('创建车辆失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 更新车辆容积参考
   * @param {Object} vehicleData - 车辆数据（包含id）
   * @returns {Promise} - 返回更新结果
   */
  async updateVehicle(vehicleData) {
    try {
      const { id, ...updateData } = vehicleData
      const response = await apiClient.put(`/vehicle-capacity-reference/${id}`, updateData)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '更新成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '更新车辆失败',
          data: null
        }
      }
    } catch (error) {
      console.error('更新车辆失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 删除车辆容积参考
   * @param {string} id - 车辆ID
   * @returns {Promise} - 返回删除结果
   */
  async deleteVehicle(id) {
    try {
      const response = await apiClient.delete(`/vehicle-capacity-reference/${id}`)
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '删除成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '删除车辆失败',
          data: null
        }
      }
    } catch (error) {
      console.error('删除车辆失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 获取可用车辆列表
   * @returns {Promise} - 返回可用车辆列表
   */
  async getAvailableVehicles() {
    try {
      const response = await apiClient.get('/vehicle-capacity-reference/available')
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取可用车辆失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取可用车辆失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 获取可用车厢列表
   * @returns {Promise} - 返回可用车厢列表
   */
  async getAvailableCarriages() {
    try {
      const response = await apiClient.get('/vehicle-capacity-reference/available-carriages')
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取可用车厢失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取可用车厢失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 搜索车辆
   * @param {Object} params - 搜索参数
   * @param {string} params.license_plate - 车牌号
   * @param {string} params.carriage_number - 车厢号
   * @returns {Promise} - 返回搜索结果
   */
  async searchVehicles(params) {
    try {
      const response = await apiClient.get('/vehicle-capacity-reference/search', { params })
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '搜索成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '搜索车辆失败',
          data: null
        }
      }
    } catch (error) {
      console.error('搜索车辆失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  },

  /**
   * 获取车辆类型选项
   * @returns {Promise} - 返回车辆类型选项
   */
  async getVehicleTypeChoices() {
    try {
      const response = await apiClient.get('/vehicle-capacity-reference/vehicle-types')
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取车辆类型失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取车辆类型失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: null
      }
    }
  }
};

// 导出便捷方法
export const {
  getVehicleList,
  getVehicleDetail,
  createVehicle,
  updateVehicle,
  deleteVehicle,
  getAvailableVehicles,
  searchVehicles,
  getVehicleTypeChoices
} = vehicleCapacityReferenceService;

export default vehicleCapacityReferenceService;