import { apiClient } from './apiClient';

/**
 * 车辆服务
 */
export const vehicleService = {
  /**
   * 获取车辆列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.pageSize - 每页数量
   * @param {string} params.query - 搜索关键词
   * @returns {Promise} - 返回车辆列表数据
   */
  async getVehicleList(params) {
    try {
      const response = await apiClient.get('/vehicles', { params })
      
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
   * 获取可用车辆列表
   * @returns {Promise} - 返回可用车辆列表
   */
  async getAvailableVehicles() {
    try {
      const response = await apiClient.get('/vehicles/available')
      
      if (response.code === 0 || response.code === 200 || response.success) {
        return {
          code: 0,
          message: response.message || '获取成功',
          data: response.data || response
        }
      } else {
        return {
          code: response.code || 1,
          message: response.message || '获取可用车辆列表失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取可用车辆列表失败:', error)
      return {
        code: error.code || 500,
        message: error.message || 'Network Error',
        data: undefined
      }
    }
  }
};

// 保持向后兼容
export const getVehicleList = vehicleService.getVehicleList;

/**
 * 获取车辆详情
 * @param {string} id - 车辆ID
 * @returns {Promise} - 返回车辆详情数据
 */
export const getVehicleDetail = (id) => {
  return apiClient.get(`/vehicles/${id}`);
};

/**
 * 添加车辆
 * @param {Object} vehicleData - 车辆数据
 * @returns {Promise} - 返回添加结果
 */
export const addVehicle = (vehicleData) => {
  // 确保必填字段存在
  if (!vehicleData.license_plate || !vehicleData.carriage_number) {
    return Promise.reject(new Error('缺少必填字段: license_plate 或 carriage_number'));
  }
  
  return apiClient.post('/vehicles', vehicleData);
};

/**
 * 更新车辆信息
 * @param {Object} vehicleData - 车辆数据
 * @returns {Promise} - 返回更新结果
 */
export const updateVehicle = (vehicleData) => {
  if (!vehicleData.id) {
    return Promise.reject(new Error('缺少车辆ID'));
  }
  
  return apiClient.put(`/vehicles/${vehicleData.id}`, vehicleData);
};

/**
 * 删除车辆
 * @param {string} id - 车辆ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteVehicle = (id) => {
  return apiClient.delete(`/vehicles/${id}`);
};

/**
 * 更新车辆容积
 * @param {Object} volumeData - 容积更新数据
 * @param {string} volumeData.vehicleId - 车辆ID
 * @param {number} volumeData.originalVolume - 原始容积
 * @param {number} volumeData.newVolume - 新容积
 * @param {string} volumeData.reason - 修改原因
 * @param {string} volumeData.volumePhotoUrl - 容积照片URL
 * @param {string} volumeData.approvalDocUrl - 审批凭证URL
 * @returns {Promise} - 返回更新结果
 */
export const updateVehicleVolume = (volumeData) => {
  return apiClient.post('/vehicles/update-volume', volumeData);
};

/**
 * 下载车辆导入模板
 * @returns {Promise} - 返回模板文件
 */
export const downloadImportTemplate = () => {
  return apiClient.get('/vehicles/import/template', {
    responseType: 'blob'
  });
};

/**
 * 预览导入数据
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise} - 返回预览结果
 */
export const previewImportData = (formData) => {
  return apiClient.post('/vehicles/import/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 执行批量导入
 * @param {Object} importData - 导入数据
 * @param {Array} importData.validation_results - 验证结果列表
 * @param {string} importData.filename - 文件名
 * @returns {Promise} - 返回导入结果
 */
export const executeImport = (importData) => {
  return apiClient.post('/vehicles/import/execute', importData);
};

/**
 * 导出验证错误报告
 * @param {Object} errorData - 错误数据
 * @param {Array} errorData.validation_results - 验证结果列表
 * @returns {Promise} - 返回错误报告文件
 */
export const exportValidationErrors = (errorData) => {
  return apiClient.post('/vehicles/import/export-errors', errorData, {
    responseType: 'blob'
  });
};

// 扩展vehicleService对象
vehicleService.downloadImportTemplate = downloadImportTemplate;
vehicleService.previewImportData = previewImportData;
vehicleService.executeImport = executeImport;
vehicleService.exportValidationErrors = exportValidationErrors;

/**
 * 获取车辆容积更新历史
 * @param {string} vehicleId - 车辆ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @returns {Promise} - 返回容积更新历史数据
 */
export const getVolumeUpdateHistory = (vehicleId, params) => {
  return apiClient.get(`/vehicles/${vehicleId}/volume-history`, { params });
};

/**
 * 获取车型折算系数表
 * @returns {Promise} - 返回车型折算系数表数据
 */
export const getVehicleConversionFactors = () => {
  return apiClient.get('/vehicles/conversion-factors');
};