/**
 * 吨位-容积映射服务
 * 提供前端与后端吨位-容积映射API的交互功能
 */
import { apiClient } from './apiClient'

const API_BASE_URL = '/vehicle/tonnage-volume'

class TonnageVolumeService {
  /**
   * 获取所有吨位-容积映射关系
   * @param {Object} params - 查询参数
   * @returns {Promise} 兼容前端消费的响应结构 { data: { items, total }, code, message }
   */
  async getMappings(params = {}) {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/mappings`, { params })
      // 兼容后端目前返回 { code, message, data } 且 data 为数组（非分页对象）的情况
      const backendData = response?.data
      const items = Array.isArray(backendData)
        ? backendData
        : (backendData?.items || [])
      const total = Array.isArray(backendData)
        ? backendData.length
        : (typeof backendData?.total === 'number' ? backendData.total : items.length)

      // 返回页面期望的结构，避免修改页面代码
      return {
        code: response?.code,
        message: response?.message,
        data: {
          items,
          total
        }
      }
    } catch (error) {
      console.error('获取吨位-容积映射失败:', error)
      throw error
    }
  }

  /**
   * 获取活跃的吨位容积映射
   * @returns {Promise}
   */
  async getActiveMappings() {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/mappings/active`)
      return response
    } catch (error) {
      console.error('获取活跃映射失败:', error)
      throw error
    }
  }

  /**
   * 根据ID获取映射详情
   * @param {number} id - 映射ID
   * @returns {Promise}
   */
  async getMappingById(id) {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/mappings/${id}`)
      return response
    } catch (error) {
      console.error(`获取映射${id}详情失败:`, error)
      throw error
    }
  }

  /**
   * 根据吨位获取对应的容积信息
   * @param {string} tonnage - 标准吨位，如'5吨'、'40吨A'
   * @returns {Promise} 容积信息
   */
  async getVolumeByTonnage(tonnage) {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/mappings/volume/${encodeURIComponent(tonnage)}`)
      return response
    } catch (error) {
      console.error(`获取吨位${tonnage}对应容积失败:`, error)
      throw error
    }
  }

  /**
   * 根据容积获取对应的吨位档位
   * @param {number} volume - 容积值
   * @returns {Promise} 吨位档位信息
   */
  async getTonnageByVolume(volume) {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/mappings/tonnage/${volume}`)
      return response
    } catch (error) {
      console.error(`获取容积${volume}对应吨位失败:`, error)
      throw error
    }
  }

  /**
   * 创建新的吨位-容积映射关系
   * @param {Object} mappingData - 映射数据
   * @returns {Promise} API响应
   */
  async createMapping(mappingData) {
    try {
      const response = await apiClient.post(`${API_BASE_URL}/mappings`, mappingData)
      return response
    } catch (error) {
      console.error('创建吨位-容积映射失败:', error)
      throw error
    }
  }

  /**
   * 更新吨位-容积映射关系
   * @param {number} mappingId - 映射ID
   * @param {Object} mappingData - 更新数据
   * @returns {Promise} API响应
   */
  async updateMapping(mappingId, mappingData) {
    try {
      const response = await apiClient.put(`${API_BASE_URL}/mappings/${mappingId}`, mappingData)
      return response
    } catch (error) {
      console.error('更新吨位-容积映射失败:', error)
      throw error
    }
  }

  /**
   * 删除吨位-容积映射关系
   * @param {number} mappingId - 映射ID
   * @returns {Promise} API响应
   */
  async deleteMapping(mappingId) {
    try {
      const response = await apiClient.delete(`${API_BASE_URL}/mappings/${mappingId}`)
      return response
    } catch (error) {
      console.error('删除吨位-容积映射失败:', error)
      throw error
    }
  }

  /**
   * 获取标准吨位选项列表（用于前端下拉框）
   * @returns {Array} 标准吨位选项
   */
  getStandardTonnageOptions() {
    return [
      { value: '5吨', label: '5吨 (≥35m³)' },
      { value: '8吨', label: '8吨 (≥45m³)' },
      { value: '12吨', label: '12吨 (≥55m³)' },
      { value: '20吨', label: '20吨 (≥100m³)' },
      { value: '30吨', label: '30吨 (≥130m³)' },
      { value: '40吨A', label: '40吨A (≥150m³)' },
      { value: '40吨B', label: '40吨B (≥180m³)' }
    ]
  }

  /**
   * 格式化吨位字符串（去掉重复的'吨'字）
   * @param {string} tonnage - 原始吨位字符串
   * @returns {string} 格式化后的吨位字符串
   */
  formatTonnage(tonnage) {
    if (!tonnage || typeof tonnage !== 'string') {
      return tonnage
    }

    // 去除首尾空格
    tonnage = tonnage.trim()

    // 处理'数字吨字母吨'格式，如'40吨A吨' -> '40吨A'
    const pattern1 = /^(\d+吨[A-Z])吨$/
    const match1 = tonnage.match(pattern1)
    if (match1) {
      return match1[1]
    }

    // 处理'数字吨吨'格式，如'5吨吨' -> '5吨'
    const pattern2 = /^(\d+)吨吨$/
    const match2 = tonnage.match(pattern2)
    if (match2) {
      return `${match2[1]}吨`
    }

    // 处理多个连续'吨'字的情况
    tonnage = tonnage.replace(/吨+/g, '吨')

    return tonnage
  }

  /**
   * 验证吨位格式是否正确
   * @param {string} tonnage - 吨位字符串
   * @returns {boolean} 格式是否正确
   */
  validateTonnageFormat(tonnage) {
    if (!tonnage || typeof tonnage !== 'string') {
      return false
    }

    // 标准格式：数字+吨+可选字母
    const pattern = /^\d+吨[A-Z]?$/
    return pattern.test(tonnage.trim())
  }

  /**
   * 检查是否为有效的标准吨位
   * @param {string} tonnage - 吨位字符串
   * @returns {boolean} 是否为标准吨位
   */
  isValidStandardTonnage(tonnage) {
    const formattedTonnage = this.formatTonnage(tonnage)
    const standardOptions = this.getStandardTonnageOptions()
    return standardOptions.some(option => option.value === formattedTonnage)
  }
}

// 创建单例实例
const tonnageVolumeService = new TonnageVolumeService()

export default tonnageVolumeService