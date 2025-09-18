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
      const data = await apiClient.get('/dispatch/tasks', { params })
      // 统一成功判定：后端 code 200/201/0 或 success=true 均视为成功
      if (
        data && (data.code === 0 || data.code === 200 || data.code === 201 || data.success === true)
      ) {
        const payload = data.data !== undefined ? data.data : data
        const items = Array.isArray(payload) ? payload : (payload.items || [])
        const total = Array.isArray(payload) ? payload.length : (payload.total || 0)
        return {
          code: 0,
          message: data.message || '获取派车任务成功',
          data: {
            items,
            total,
            page: params.page,
            per_page: params.per_page
          }
        }
      }
      // 未识别为成功，抛出错误让调用方进入 catch 分支
      throw new Error(data?.message || '获取派车任务失败')
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
      return response
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
      const data = await apiClient.post('/dispatch/tasks', taskData)
      // 统一响应格式：
      // - 后端 body.code = 200/201 视为成功
      // - 或 body.code = 0（已是规范化）视为成功
      // - 或 body.success === true 视为成功（另一类返回规范）
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '创建任务成功',
          // 若后端直接返回实体对象，则回传 data 本体；若包装在 data 字段则优先返回内部 data
          data: data.data !== undefined ? data.data : data
        }
      }
      // 其他情况原样返回，交由调用方处理
      return data
    } catch (error) {
      console.error('创建派车任务失败:', error)
      // api 拦截器已将错误标准化为 { code, message, data }
      return error
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
      return response
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
      const data = await apiClient.post(`/dispatch/tasks/${taskId}/audit`, auditData)
      // 统一成功判定与规范化
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '审核任务成功',
          data: data.data !== undefined ? data.data : data
        }
      }
      return data
    } catch (error) {
      console.error('审核派车任务失败:', error)
      // 保持与其他方法一致的错误返回
      return error
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
      const data = await apiClient.post(`/dispatch/tasks/${taskId}/assign`, assignData)
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '分配车辆成功',
          data: data.data !== undefined ? data.data : data
        }
      }
      return data
    } catch (error) {
      console.error('分配车辆失败:', error)
      return error
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
      const data = await apiClient.post(`/dispatch/tasks/${taskId}/complete`, completeData)
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '完成任务成功',
          data: data.data !== undefined ? data.data : data
        }
      }
      return data
    } catch (error) {
      console.error('完成派车任务失败:', error)
      return error
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
      return response
    } catch (error) {
      console.error('获取可用车辆列表失败:', error)
      throw error
    }
  },

  /**
   * 获取仪表盘统计数据
   * @returns {Promise} - 返回仪表盘数据
   */
  async getDashboardData() {
    try {
      const data = await apiClient.get('/dispatch/dashboard/complete')
      // 统一成功判定：后端 code 200/201/0 或 success=true 均视为成功
      if (
        data && (data.code === 0 || data.code === 200 || data.code === 201 || data.success === true)
      ) {
        const payload = data.data !== undefined ? data.data : data
        const statistics = payload.statistics || {}
        const status_distribution = payload.status_distribution || []
        const track_distribution = payload.track_distribution || []
        const urgent_task_list = payload.urgent_tasks || payload.urgent_task_list || []

        // 扁平化并对齐前端组件期望字段
        const normalized = {
          total_tasks: statistics.total_tasks || 0,
          today_tasks: statistics.today_new_tasks || statistics.today_tasks || 0,
          timeout_tasks: statistics.expiring_tasks || statistics.timeout_tasks || 0,
          status_distribution,
          track_distribution,
          urgent_task_list,
          // 提供紧急任务数量给顶部卡片使用
          urgent_tasks: Array.isArray(urgent_task_list)
            ? urgent_task_list.length
            : (typeof urgent_task_list === 'number' ? urgent_task_list : 0)
        }

        return {
          code: 0,
          message: data.message || '获取仪表盘数据成功',
          data: normalized
        }
      }
      // 未识别为成功，抛出错误让调用方进入 catch 分支
      throw new Error(data?.message || '获取仪表盘数据失败')
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
      throw error
    }
  },

  /**
   * 获取统计概览数据
   * @returns {Promise} - 返回统计概览数据
   */
  async getDashboardStatistics() {
    try {
      const response = await apiClient.get('/dispatch/dashboard/statistics')
      return response
    } catch (error) {
      console.error('获取统计概览数据失败:', error)
      throw error
    }
  },

  /**
   * 获取分布数据
   * @returns {Promise} - 返回分布数据
   */
  async getDashboardDistributions() {
    try {
      const response = await apiClient.get('/dispatch/dashboard/distributions')
      return response
    } catch (error) {
      console.error('获取分布数据失败:', error)
      throw error
    }
  },

  /**
   * 获取紧急任务
   * @returns {Promise} - 返回紧急任务数据
   */
  async getUrgentTasks() {
    try {
      const response = await apiClient.get('/dispatch/urgent-tasks')
      return response
    } catch (error) {
      console.error('获取紧急任务失败:', error)
      throw error
    }
  },

  /**
   * 提交供应商响应
   * @param {Object} responseData - 响应数据
   * @returns {Promise} - 返回响应结果
   */
  async submitSupplierResponse(responseData) {
    try {
      const data = await apiClient.post('/dispatch/tasks/supplier-response', responseData)
      
      // 统一成功判定
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '响应提交成功',
          data: data.data !== undefined ? data.data : data
        }
      }
      
      // 未识别为成功，抛出错误
      throw new Error(data?.message || '响应提交失败')
    } catch (error) {
      console.error('提交供应商响应失败:', error)
      throw error
    }
  },

  /**
   * 提交班组派车响应
   * @param {Object} responseData - 响应数据
   * @returns {Promise} - 返回响应结果
   */
  async submitTeamResponse(responseData) {
    try {
      const data = await apiClient.post('/dispatch/tasks/team-response', responseData)
      
      // 统一成功判定
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '派车响应提交成功',
          data: data.data !== undefined ? data.data : data
        }
      }
      
      // 未识别为成功，抛出错误
      throw new Error(data?.message || '派车响应提交失败')
    } catch (error) {
      console.error('提交班组派车响应失败:', error)
      throw error
    }
  },

  /**
   * 提交大容积供应商响应
   * @param {Object} responseData - 响应数据
   * @returns {Promise} - 返回响应结果
   */
  async submitOutsourcingResponse(responseData) {
    try {
      const data = await apiClient.post('/dispatch/tasks/outsourcing-response', responseData)
      
      // 统一成功判定
      if (
        data && (
          data.code === 0 ||
          data.code === 200 ||
          data.code === 201 ||
          data.success === true
        )
      ) {
        return {
          code: 0,
          message: data.message || '大容积响应提交成功',
          data: data.data !== undefined ? data.data : data
        }
      }
      
      // 未识别为成功，抛出错误
      throw new Error(data?.message || '大容积响应提交失败')
    } catch (error) {
      console.error('提交大容积供应商响应失败:', error)
      throw error
    }
  }
}