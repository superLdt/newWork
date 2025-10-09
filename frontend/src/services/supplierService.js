import { apiClient } from './apiClient'

/**
 * 供应商服务类
 * 提供供应商相关的API接口
 */
class SupplierService {
  /**
   * 获取供应商申诉任务列表
   * @param {Object} params - 查询参数
   * @returns {Promise} API响应
   */
  async getSupplierAppealTasks(params = {}) {
    try {
      const response = await apiClient.get('/dispatch/supplier/appeal-tasks', { params })
      return {
        code: 200,
        data: response.data,
        message: '获取申诉任务列表成功'
      }
    } catch (error) {
      console.error('获取供应商申诉任务列表失败:', error)
      throw new Error(error.response?.data?.message || '获取申诉任务列表失败')
    }
  }

  /**
   * 获取申诉详情
   * @param {string|number} appealId - 申诉ID
   * @returns {Promise} API响应
   */
  async getAppealDetail(appealId) {
    try {
      // 后端申诉详情路由：/api/v1/dispatch/tasks/{task_id}/appeal
      const response = await apiClient.get(`/dispatch/tasks/${appealId}/appeal`)
      return {
        code: 200,
        data: response.data,
        message: '获取申诉详情成功'
      }
    } catch (error) {
      console.error('获取申诉详情失败:', error)
      throw new Error(error.response?.data?.message || '获取申诉详情失败')
    }
  }

  /**
   * 下载申诉附件
   * @param {string|number} attachmentId - 附件ID
   * @returns {Promise} 文件流
   */
  async downloadAppealAttachment(attachmentId) {
    try {
      // 后端目前返回证据文件直接包含URL，无专门下载路由
      const response = await apiClient.get(`/dispatch/appeals/attachments/${attachmentId}/download`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('下载申诉附件失败:', error)
      throw new Error(error.response?.data?.message || '下载申诉附件失败')
    }
  }

  /**
   * 提交申诉
   * @param {Object} appealData - 申诉数据
   * @returns {Promise} API响应
   */
  async submitAppeal(appealData) {
    try {
      // 提交申诉应走任务申诉提交路由，需要task_id
      const { task_id, ...payload } = appealData
      const response = await apiClient.post(`/dispatch/tasks/${task_id}/appeal`, payload)
      return {
        code: 200,
        data: response.data,
        message: '提交申诉成功'
      }
    } catch (error) {
      console.error('提交申诉失败:', error)
      throw new Error(error.response?.data?.message || '提交申诉失败')
    }
  }

  /**
   * 获取供应商统计信息
   * @returns {Promise} API响应
   */
  async getSupplierStats() {
    try {
      const response = await apiClient.get('/supplier/stats')
      return {
        code: 200,
        data: response.data,
        message: '获取统计信息成功'
      }
    } catch (error) {
      console.error('获取供应商统计信息失败:', error)
      throw new Error(error.response?.data?.message || '获取统计信息失败')
    }
  }

  /**
   * 获取供应商任务列表
   * @param {Object} params - 查询参数
   * @returns {Promise} API响应
   */
  async getSupplierTasks(params = {}) {
    try {
      const response = await apiClient.get('/supplier/tasks', { params })
      return {
        code: 200,
        data: response.data,
        message: '获取任务列表成功'
      }
    } catch (error) {
      console.error('获取供应商任务列表失败:', error)
      throw new Error(error.response?.data?.message || '获取任务列表失败')
    }
  }
}

// 创建服务实例
export const supplierService = new SupplierService()

// 默认导出
export default supplierService