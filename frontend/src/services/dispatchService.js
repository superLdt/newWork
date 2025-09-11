// 派车任务服务模块
import { apiClient } from './apiClient'

/**
 * 派车任务服务
 * 提供派车任务相关的API接口封装
 */
export const dispatchService = {
  /**
   * 获取派车任务列表
   * @param {Object} params - 查询参数
   * @returns {Promise} - 返回任务列表数据
   */
  async getTasks(params = {}) {
    try {
      const response = await apiClient.get('/dispatch/tasks', { params })
      return response.data
    } catch (error) {
      console.error('获取派车任务列表失败:', error)
      throw error
    }
  },

  /**
   * 获取派车任务详情
   * @param {string|number} taskId - 任务ID
   * @returns {Promise} - 返回任务详情数据
   */
  async getTaskDetail(taskId) {
    try {
      const response = await apiClient.get(`/dispatch/tasks/${taskId}`)
      return response.data
    } catch (error) {
      console.error('获取派车任务详情失败:', error)
      throw error
    }
  },

  /**
   * 创建派车任务
   * @param {Object} taskData - 任务数据
   * @returns {Promise} - 返回创建结果
   */
  async createTask(taskData) {
    try {
      const response = await apiClient.post('/dispatch/tasks', taskData)
      return response.data
    } catch (error) {
      console.error('创建派车任务失败:', error)
      throw error
    }
  },

  /**
   * 更新派车任务
   * @param {string|number} taskId - 任务ID
   * @param {Object} taskData - 任务数据
   * @returns {Promise} - 返回更新结果
   */
  async updateTask(taskId, taskData) {
    try {
      const response = await apiClient.put(`/dispatch/tasks/${taskId}`, taskData)
      return response.data
    } catch (error) {
      console.error('更新派车任务失败:', error)
      throw error
    }
  },

  /**
   * 审核派车任务
   * @param {string|number} taskId - 任务ID
   * @param {Object} auditData - 审核数据
   * @returns {Promise} - 返回审核结果
   */
  async auditTask(taskId, auditData) {
    try {
      const response = await apiClient.post(`/dispatch/tasks/${taskId}/audit`, auditData)
      return response.data
    } catch (error) {
      console.error('审核派车任务失败:', error)
      throw error
    }
  },

  /**
   * 分配车辆到任务
   * @param {string|number} taskId - 任务ID
   * @param {Object} assignData - 分配数据
   * @returns {Promise} - 返回分配结果
   */
  async assignVehicles(taskId, assignData) {
    try {
      const response = await apiClient.post(`/dispatch/tasks/${taskId}/assign`, assignData)
      return response.data
    } catch (error) {
      console.error('分配车辆失败:', error)
      throw error
    }
  },

  /**
   * 完成派车任务
   * @param {string|number} taskId - 任务ID
   * @param {Object} completeData - 完成数据
   * @returns {Promise} - 返回操作结果
   */
  async completeTask(taskId, completeData) {
    try {
      const response = await apiClient.post(`/dispatch/tasks/${taskId}/complete`, completeData)
      return response.data
    } catch (error) {
      console.error('完成派车任务失败:', error)
      throw error
    }
  },

  /**
   * 获取可用车辆列表
   * @param {Object} params - 查询参数
   * @returns {Promise} - 返回可用车辆列表
   */
  async getAvailableVehicles(params = {}) {
    try {
      const response = await apiClient.get('/vehicles/available', { params })
      return response.data
    } catch (error) {
      console.error('获取可用车辆列表失败:', error)
      throw error
    }
  }
}