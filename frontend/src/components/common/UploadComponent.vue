<template>
  <div class="upload-component">
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :data="uploadData"
      :on-change="handleChange"
      :before-upload="handleBeforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :on-remove="handleRemove"
      :on-exceed="handleExceed"
      :file-list="fileList"
      :accept="acceptTypes"
      :multiple="multiple"
      :limit="limit"
      :disabled="disabled"
      :drag="drag"
      :show-file-list="showFileList"
      :list-type="listType"
      :auto-upload="autoUpload"
      class="upload-wrapper"
    >
      <template v-if="drag">
        <div class="upload-drag-area">
          <el-icon class="upload-icon"><upload-filled /></el-icon>
          <div class="upload-text">
            <span>将文件拖到此处，或</span>
            <em>点击上传</em>
          </div>
          <div class="upload-tip" v-if="tip">{{ tip }}</div>
        </div>
      </template>
      
      <template v-else-if="listType === 'picture-card'">
        <el-icon><Plus /></el-icon>
      </template>
      
      <template v-else>
        <el-button type="primary" :disabled="disabled">
          <el-icon><upload-filled /></el-icon>
          {{ buttonText }}
        </el-button>
      </template>
      
      <template #tip v-if="tip && !drag">
        <div class="el-upload__tip">{{ tip }}</div>
      </template>
    </el-upload>

    <!-- 上传进度 -->
    <div v-if="showProgress && uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <el-progress :percentage="uploadProgress" :status="progressStatus" />
    </div>

    <!-- 文件预览 -->
    <div v-if="showPreview && previewFiles.length > 0" class="file-preview">
      <div class="preview-title">已上传文件</div>
      <div class="preview-list">
        <div
          v-for="(file, index) in previewFiles"
          :key="index"
          class="preview-item"
        >
          <div class="file-info">
            <el-icon class="file-icon">
              <Document v-if="!isImage(file.name)" />
              <Picture v-else />
            </el-icon>
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
          </div>
          <div class="file-actions">
            <el-button
              v-if="isImage(file.name)"
              type="text"
              size="small"
              @click="previewImage(file)"
            >
              预览
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="downloadFile(file)"
            >
              下载
            </el-button>
            <el-button
              type="text"
              size="small"
              class="delete-btn"
              @click="removeFile(index)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="imagePreviewVisible" title="图片预览" width="60%">
      <div class="image-preview-container">
        <img :src="previewImageUrl" alt="预览图片" class="preview-image" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Plus, Document, Picture } from '@element-plus/icons-vue'
import { UploadService, FILE_TYPES, UploadConfigGenerator } from '@/utils/upload'

// Props
const props = defineProps({
  // 文件类型：image, document, attachment, excel
  fileType: {
    type: String,
    default: 'attachment'
  },
  // 业务类型
  businessType: {
    type: String,
    default: ''
  },
  // 业务ID
  businessId: {
    type: String,
    default: ''
  },
  // 是否多选
  multiple: {
    type: Boolean,
    default: false
  },
  // 文件数量限制
  limit: {
    type: Number,
    default: 1
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否拖拽上传
  drag: {
    type: Boolean,
    default: false
  },
  // 是否显示文件列表
  showFileList: {
    type: Boolean,
    default: true
  },
  // 列表类型
  listType: {
    type: String,
    default: 'text' // text, picture, picture-card
  },
  // 是否自动上传
  autoUpload: {
    type: Boolean,
    default: true
  },
  // 按钮文字
  buttonText: {
    type: String,
    default: '选择文件'
  },
  // 提示文字
  tip: {
    type: String,
    default: ''
  },
  // 是否显示进度
  showProgress: {
    type: Boolean,
    default: true
  },
  // 是否显示预览
  showPreview: {
    type: Boolean,
    default: false
  },
  // 初始文件列表
  modelValue: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits([
  'update:modelValue',
  'success',
  'error',
  'progress',
  'remove',
  'exceed',
  'before-upload'
])

// Refs
const uploadRef = ref()
const fileList = ref([])
const uploadProgress = ref(0)
const progressStatus = ref('')
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const previewFiles = ref([])
const selectedCount = ref(0)

// Computed
const fileTypeConfig = computed(() => {
  return FILE_TYPES[props.fileType.toUpperCase()] || FILE_TYPES.ATTACHMENT
})

const uploadUrl = computed(() => {
  return `/api/v1/upload/${props.fileType}`
})

const uploadHeaders = computed(() => {
  const headers = {}
  // 添加认证头
  const token = localStorage.getItem('token')
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
})

const uploadData = computed(() => {
  const data = {}
  if (props.businessType) {
    data.business_type = props.businessType
  }
  if (props.businessId) {
    data.business_id = props.businessId
  }
  return data
})

const acceptTypes = computed(() => {
  return fileTypeConfig.value.extensions.join(',')
})

// Watch
watch(() => props.modelValue, (newVal) => {
  previewFiles.value = newVal || []
}, { immediate: true })

// Methods
const handleBeforeUpload = (file) => {
  const validation = UploadService.validateFile(file, fileTypeConfig.value)
  if (!validation.valid) {
    ElMessage.error(validation.message)
    return false
  }
  
  emit('before-upload', file)
  uploadProgress.value = 0
  progressStatus.value = ''
  return true
}

const handleSuccess = (response, file, fileList) => {
  uploadProgress.value = 100
  progressStatus.value = 'success'
  
  // 检查响应格式：后端返回code字段，200表示成功
  const isSuccess = response.code === 200 || response.success === true
  
  if (isSuccess) {
    ElMessage.success(response.message || '上传成功')
    
    // 更新预览文件列表
    const newFile = {
      ...response.data,
      name: file.name,
      size: file.size
    }
    
    if (props.multiple) {
      previewFiles.value.push(newFile)
    } else {
      previewFiles.value = [newFile]
    }
    
    emit('update:modelValue', previewFiles.value)
    emit('success', response.data, file, fileList)
  } else {
    ElMessage.error(response.message || '上传失败')
    emit('error', response, file, fileList)
  }
  
  // 清除进度
  setTimeout(() => {
    uploadProgress.value = 0
    progressStatus.value = ''
  }, 2000)
}

const handleChange = (file, fileList) => {
  selectedCount.value = fileList?.length || 0
}

const handleError = (error, file, fileList) => {
  uploadProgress.value = 0
  progressStatus.value = 'exception'
  
  console.error('上传失败:', error)
  ElMessage.error('上传失败，请重试')
  emit('error', error, file, fileList)
}

const handleProgress = (event, file, fileList) => {
  uploadProgress.value = Math.round(event.percent)
  emit('progress', event, file, fileList)
}

const handleRemove = (file, fileList) => {
  // 从预览列表中移除
  const index = previewFiles.value.findIndex(f => f.url === file.url || f.name === file.name)
  if (index > -1) {
    previewFiles.value.splice(index, 1)
    emit('update:modelValue', previewFiles.value)
  }
  
  emit('remove', file, fileList)
}

const handleExceed = (files, fileList) => {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
  emit('exceed', files, fileList)
}

const removeFile = (index) => {
  previewFiles.value.splice(index, 1)
  emit('update:modelValue', previewFiles.value)
}

const isImage = (fileName) => {
  return UploadService.isImage(fileName)
}

const formatFileSize = (bytes) => {
  return UploadService.formatFileSize(bytes)
}

const previewImage = (file) => {
  previewImageUrl.value = UploadService.getFileUrl(file.url || file.path)
  imagePreviewVisible.value = true
}

const downloadFile = (file) => {
  const url = UploadService.getFileUrl(file.url || file.path)
  const link = document.createElement('a')
  link.href = url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 暴露方法
const clearFiles = () => {
  uploadRef.value?.clearFiles()
  previewFiles.value = []
  emit('update:modelValue', [])
}

const submit = () => {
  uploadRef.value?.submit()
}

const abort = () => {
  uploadRef.value?.abort()
}

const getSelectedCount = () => {
  return (uploadRef.value?.uploadFiles?.length ?? selectedCount.value ?? 0)
}

const getSelectedFiles = () => {
  return uploadRef.value?.uploadFiles ?? []
}

defineExpose({
  clearFiles,
  submit,
  abort,
  getSelectedCount,
  getSelectedFiles
})
</script>

<style scoped>
.upload-component {
  width: 100%;
}

.upload-wrapper {
  width: 100%;
}

.upload-drag-area {
  padding: 40px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  background-color: #fafafa;
  transition: border-color 0.3s;
}

.upload-drag-area:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.upload-progress {
  margin-top: 16px;
}

.file-preview {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
}

.preview-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.file-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 8px;
}

.file-icon {
  font-size: 16px;
  color: #909399;
}

.file-name {
  font-size: 14px;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.delete-btn {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f56c6c;
}

.image-preview-container {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

:deep(.el-upload-dragger) {
  border: none;
  background: transparent;
}

:deep(.el-upload__tip) {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>