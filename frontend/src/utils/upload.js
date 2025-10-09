/**
 * 通用上传工具类
 * 提供统一的文件上传、验证、处理功能
 */

import { ElMessage } from 'element-plus'
import axios from 'axios'

/**
 * 文件类型配置
 */
export const FILE_TYPES = {
  IMAGE: {
    name: 'image',
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    mimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    maxSize: 5 * 1024 * 1024, // 5MB
    description: '图片文件'
  },
  DOCUMENT: {
    name: 'document',
    extensions: ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    mimeTypes: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ],
    maxSize: 10 * 1024 * 1024, // 10MB
    description: '文档文件'
  },
  EXCEL: {
    name: 'excel',
    extensions: ['.xls', '.xlsx'],
    mimeTypes: [
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ],
    maxSize: 10 * 1024 * 1024, // 10MB
    description: 'Excel文件'
  },
  ATTACHMENT: {
    name: 'attachment',
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    mimeTypes: [
      'image/jpeg', 'image/png', 'image/gif',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ],
    maxSize: 10 * 1024 * 1024, // 10MB
    description: '附件文件'
  }
}

/**
 * 通用上传服务类
 */
export class UploadService {
  /**
   * 验证文件
   * @param {File} file - 要验证的文件
   * @param {Object} fileType - 文件类型配置
   * @returns {Object} 验证结果 {valid: boolean, message: string}
   */
  static validateFile(file, fileType) {
    if (!file) {
      return { valid: false, message: '请选择文件' }
    }

    // 检查文件扩展名
    const fileName = file.name.toLowerCase()
    const hasValidExtension = fileType.extensions.some(ext => fileName.endsWith(ext))
    
    if (!hasValidExtension) {
      return {
        valid: false,
        message: `仅支持 ${fileType.extensions.join(', ')} 格式的${fileType.description}`
      }
    }

    // 检查MIME类型
    if (fileType.mimeTypes && fileType.mimeTypes.length > 0) {
      if (!fileType.mimeTypes.includes(file.type)) {
        return {
          valid: false,
          message: `文件类型不正确，仅支持${fileType.description}`
        }
      }
    }

    // 检查文件大小
    if (file.size > fileType.maxSize) {
      const maxSizeMB = Math.round(fileType.maxSize / (1024 * 1024))
      return {
        valid: false,
        message: `文件大小不能超过 ${maxSizeMB}MB`
      }
    }

    return { valid: true, message: '验证通过' }
  }

  /**
   * 上传文件
   * @param {File} file - 要上传的文件
   * @param {Object} options - 上传选项
   * @param {string} options.type - 上传类型 (image/document/attachment)
   * @param {string} options.businessType - 业务类型
   * @param {string} options.businessId - 业务ID
   * @param {Function} options.onProgress - 进度回调
   * @returns {Promise} 上传结果
   */
  static async uploadFile(file, options = {}) {
    const {
      type = 'attachment',
      businessType,
      businessId,
      onProgress
    } = options

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      if (businessType) {
        formData.append('business_type', businessType)
      }
      if (businessId) {
        formData.append('business_id', businessId)
      }

      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }

      if (onProgress) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }

      const response = await axios.post(`/api/v1/upload/${type}`, formData, config)
      
      if (response.data.success) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message || '上传成功'
        }
      } else {
        return {
          success: false,
          message: response.data.message || '上传失败'
        }
      }
    } catch (error) {
      console.error('上传失败:', error)
      return {
        success: false,
        message: error.response?.data?.message || '上传失败，请重试'
      }
    }
  }

  /**
   * 上传图片
   * @param {File} file - 图片文件
   * @param {Object} options - 上传选项
   * @returns {Promise} 上传结果
   */
  static async uploadImage(file, options = {}) {
    const validation = this.validateFile(file, FILE_TYPES.IMAGE)
    if (!validation.valid) {
      ElMessage.error(validation.message)
      return { success: false, message: validation.message }
    }

    return this.uploadFile(file, { ...options, type: 'image' })
  }

  /**
   * 上传文档
   * @param {File} file - 文档文件
   * @param {Object} options - 上传选项
   * @returns {Promise} 上传结果
   */
  static async uploadDocument(file, options = {}) {
    const validation = this.validateFile(file, FILE_TYPES.DOCUMENT)
    if (!validation.valid) {
      ElMessage.error(validation.message)
      return { success: false, message: validation.message }
    }

    return this.uploadFile(file, { ...options, type: 'document' })
  }

  /**
   * 上传附件
   * @param {File} file - 附件文件
   * @param {Object} options - 上传选项
   * @returns {Promise} 上传结果
   */
  static async uploadAttachment(file, options = {}) {
    const validation = this.validateFile(file, FILE_TYPES.ATTACHMENT)
    if (!validation.valid) {
      ElMessage.error(validation.message)
      return { success: false, message: validation.message }
    }

    return this.uploadFile(file, { ...options, type: 'attachment' })
  }

  /**
   * 批量上传文件
   * @param {FileList|Array} files - 文件列表
   * @param {Object} options - 上传选项
   * @returns {Promise} 上传结果数组
   */
  static async uploadMultiple(files, options = {}) {
    const fileArray = Array.from(files)
    const uploadPromises = fileArray.map(file => this.uploadAttachment(file, options))
    
    try {
      const results = await Promise.allSettled(uploadPromises)
      return results.map((result, index) => ({
        file: fileArray[index],
        success: result.status === 'fulfilled' && result.value.success,
        data: result.status === 'fulfilled' ? result.value.data : null,
        message: result.status === 'fulfilled' ? result.value.message : result.reason?.message || '上传失败'
      }))
    } catch (error) {
      console.error('批量上传失败:', error)
      throw error
    }
  }

  /**
   * 获取文件预览URL
   * @param {string} filePath - 文件路径
   * @returns {string} 预览URL
   */
  static getFileUrl(filePath) {
    if (!filePath) return ''
    
    // 如果已经是完整URL，直接返回
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
      return filePath
    }
    
    // 构建完整的文件访问URL
    return `/api/v1/upload/files/${filePath}`
  }

  /**
   * 判断文件是否为图片
   * @param {string} fileName - 文件名
   * @returns {boolean} 是否为图片
   */
  static isImage(fileName) {
    if (!fileName) return false
    const ext = fileName.toLowerCase().split('.').pop()
    return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)
  }

  /**
   * 格式化文件大小
   * @param {number} bytes - 字节数
   * @returns {string} 格式化后的大小
   */
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
}

/**
 * Element Plus Upload 组件的通用配置生成器
 */
export class UploadConfigGenerator {
  /**
   * 生成 el-upload 的 before-upload 函数
   * @param {Object} fileType - 文件类型配置
   * @param {Object} options - 额外选项
   * @returns {Function} before-upload 函数
   */
  static createBeforeUpload(fileType, options = {}) {
    return (file) => {
      const validation = UploadService.validateFile(file, fileType)
      if (!validation.valid) {
        ElMessage.error(validation.message)
        return false
      }
      
      if (options.onValidationSuccess) {
        options.onValidationSuccess(file)
      }
      
      return true
    }
  }

  /**
   * 生成 el-upload 的 on-success 函数
   * @param {Function} callback - 成功回调
   * @returns {Function} on-success 函数
   */
  static createOnSuccess(callback) {
    return (response, file, fileList) => {
      if (response.success) {
        ElMessage.success(response.message || '上传成功')
        if (callback) {
          callback(response.data, file, fileList)
        }
      } else {
        ElMessage.error(response.message || '上传失败')
      }
    }
  }

  /**
   * 生成 el-upload 的 on-error 函数
   * @param {Function} callback - 错误回调
   * @returns {Function} on-error 函数
   */
  static createOnError(callback) {
    return (error, file, fileList) => {
      console.error('上传失败:', error)
      ElMessage.error('上传失败，请重试')
      if (callback) {
        callback(error, file, fileList)
      }
    }
  }

  /**
   * 生成完整的 el-upload 配置
   * @param {Object} fileType - 文件类型配置
   * @param {Object} callbacks - 回调函数
   * @returns {Object} el-upload 配置对象
   */
  static createUploadConfig(fileType, callbacks = {}) {
    return {
      beforeUpload: this.createBeforeUpload(fileType, callbacks),
      onSuccess: this.createOnSuccess(callbacks.onSuccess),
      onError: this.createOnError(callbacks.onError),
      onProgress: callbacks.onProgress,
      onRemove: callbacks.onRemove,
      accept: fileType.extensions.join(','),
      multiple: callbacks.multiple || false,
      limit: callbacks.limit,
      onExceed: callbacks.onExceed || (() => {
        ElMessage.warning(`最多只能上传 ${callbacks.limit} 个文件`)
      })
    }
  }
}

export default UploadService