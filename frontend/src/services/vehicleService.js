import api from './api';

/**
 * 获取车辆列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @param {string} params.query - 搜索关键词
 * @returns {Promise} - 返回车辆列表数据
 */
export const getVehicleList = (params) => {
  return api.get('/vehicles', { params });
};

/**
 * 获取车辆详情
 * @param {string} id - 车辆ID
 * @returns {Promise} - 返回车辆详情数据
 */
export const getVehicleDetail = (id) => {
  return api.get(`/vehicles/${id}`);
};

/**
 * 添加车辆
 * @param {Object} vehicleData - 车辆数据
 * @returns {Promise} - 返回添加结果
 */
export const addVehicle = (vehicleData) => {
  return api.post('/vehicles', vehicleData);
};

/**
 * 更新车辆信息
 * @param {Object} vehicleData - 车辆数据
 * @returns {Promise} - 返回更新结果
 */
export const updateVehicle = (vehicleData) => {
  return api.put(`/vehicles/${vehicleData.id}`, vehicleData);
};

/**
 * 删除车辆
 * @param {string} id - 车辆ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteVehicle = (id) => {
  return api.delete(`/vehicles/${id}`);
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
  return api.post('/vehicles/update-volume', volumeData);
};

/**
 * 获取车辆容积更新历史
 * @param {string} vehicleId - 车辆ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @returns {Promise} - 返回容积更新历史数据
 */
export const getVolumeUpdateHistory = (vehicleId, params) => {
  return api.get(`/vehicles/${vehicleId}/volume-history`, { params });
};

/**
 * 获取车型折算系数表
 * @returns {Promise} - 返回车型折算系数表数据
 */
export const getVehicleConversionFactors = () => {
  return api.get('/vehicles/conversion-factors');
};