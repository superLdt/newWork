<template>
  <el-dialog 
    v-model="visible" 
    title="批量导入车辆" 
    width="80%" 
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-steps :active="currentStep" align-center class="import-steps">
      <el-step title="上传文件" />
      <el-step title="数据预览" />
      <el-step title="导入结果" />
    </el-steps>
    
    <!-- 步骤1：文件上传 -->
    <div v-if="currentStep === 0" class="upload-step">
      <div class="template-download">
        <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>1. 车牌号或车厢号至少填写一个</p>
            <p>2. 容积字段必填</p>
            <p>3. 车厢号格式如：皖A36T3挂</p>
            <p>4. 常用公司用逗号分隔</p>
          </template>
        </el-alert>
        
        <div class="template-actions">
          <el-button type="primary" @click="downloadTemplate" :loading="downloadLoading">
            <el-icon><Download /></el-icon>
            下载导入模板
          </el-button>
          <span class="tip">请先下载模板，按格式填写数据后上传</span>
        </div>
      </div>
      
      <el-upload
        ref="uploadRef"
        class="upload-area"
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        :show-file-list="false"
        accept=".xlsx,.xls"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将Excel文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持.xlsx、.xls格式，文件大小不超过10MB
          </div>
        </template>
      </el-upload>
      
      <div v-if="selectedFile" class="file-info">
        <el-tag type="success">
          <el-icon><Document /></el-icon>
          {{ selectedFile.name }}
        </el-tag>
        <el-button type="text" @click="removeFile">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 步骤2：数据预览 -->
    <div v-if="currentStep === 1" class="preview-step">
      <div class="preview-summary">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总记录数" :value="previewData.total_rows || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic 
              title="有效记录" 
              :value="previewData.summary?.valid_count || 0" 
              value-style="color: #67C23A"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic 
              title="错误记录" 
              :value="previewData.summary?.invalid_count || 0" 
              value-style="color: #F56C6C"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic 
              title="有效率" 
              :value="previewData.summary?.valid_rate || 0" 
              suffix="%"
            />
          </el-col>
        </el-row>
      </div>
      
      <div class="preview-actions">
        <el-button 
          v-if="previewData.summary?.invalid_count > 0" 
          type="warning" 
          @click="exportErrors"
          :loading="exportLoading"
        >
          <el-icon><Download /></el-icon>
          导出错误报告
        </el-button>
      </div>
      
      <el-table 
        :data="previewRows" 
        border 
        max-height="400"
        class="preview-table"
      >
        <el-table-column prop="row" label="行号" width="80" align="center" />
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="carriage_number" label="车厢号" width="120" />
        <el-table-column prop="actual_volume" label="容积" width="100" />
        <el-table-column prop="vehicle_type" label="车辆类型" width="100" />
        <el-table-column prop="vehicle_category" label="车辆分类" width="100" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.valid ? 'success' : 'danger'" size="small">
              {{ row.valid ? '有效' : '错误' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误信息" min-width="200">
          <template #default="{ row }">
            <div v-if="!row.valid" class="error-messages">
              <div v-for="error in row.errors" :key="error" class="error-item">
                <el-icon><WarningFilled /></el-icon>
                {{ error }}
              </div>
            </div>
            <span v-else class="success-text">
              <el-icon><CircleCheckFilled /></el-icon>
              验证通过
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 步骤3：导入结果 -->
    <div v-if="currentStep === 2" class="result-step">
      <el-result
        :icon="importResult.success ? 'success' : 'error'"
        :title="importResult.success ? '导入完成' : '导入失败'"
      >
        <template #sub-title>
          <div v-if="importResult.success" class="result-summary">
            <p class="success-count">✅ 成功导入 {{ importResult.success_count }} 条记录</p>
            <p v-if="importResult.error_count > 0" class="error-count">
              ❌ 失败 {{ importResult.error_count }} 条记录
            </p>
            <div v-if="importStatistics" class="statistics">
              <h4>导入统计</h4>
              <p>导入时间：{{ importStatistics.import_time }}</p>
              <div v-if="importStatistics.category_stats">
                <span>车辆分类：</span>
                <el-tag 
                  v-for="(count, category) in importStatistics.category_stats" 
                  :key="category" 
                  class="category-tag"
                >
                  {{ category }}：{{ count }}辆
                </el-tag>
              </div>
            </div>
          </div>
          <div v-else class="error-summary">
            {{ importResult.message }}
          </div>
        </template>
        
        <template #extra>
          <div v-if="importResult.errors && importResult.errors.length > 0" class="error-details">
            <el-collapse>
              <el-collapse-item title="查看错误详情">
                <div class="error-list">
                  <div v-for="(error, index) in importResult.errors" :key="index" class="error-item">
                    <el-icon><WarningFilled /></el-icon>
                    {{ error }}
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </template>
      </el-result>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ currentStep === 2 ? '关闭' : '取消' }}</el-button>
        <el-button v-if="currentStep > 0 && currentStep < 2" @click="prevStep">上一步</el-button>
        <el-button 
          v-if="currentStep < 2" 
          type="primary" 
          @click="nextStep"
          :disabled="!canProceed"
          :loading="processing"
        >
          {{ getNextButtonText() }}
        </el-button>
        <el-button v-if="currentStep === 2 && importResult.success" type="primary" @click="handleFinish">
          完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  UploadFilled,
  Document,
  Close,
  WarningFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import { vehicleService } from '@/services/vehicleService'

export default {
  name: 'VehicleImportDialog',
  components: {
    Download,
    UploadFilled,
    Document,
    Close,
    WarningFilled,
    CircleCheckFilled
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'import-success'],
  setup(props, { emit }) {
    const visible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })
    
    const currentStep = ref(0)
    const selectedFile = ref(null)
    const previewData = ref({})
    const importResult = ref({})
    const importStatistics = ref(null)
    
    const downloadLoading = ref(false)
    const processing = ref(false)
    const exportLoading = ref(false)
    
    // 扁平化预览数据，避免表格列 prop 使用点路径导致取值异常
    const previewRows = computed(() => {
      const list = previewData.value?.preview_data || []
      return list.map(item => ({
        row: item?.row ?? '',
        // 扁平化 processed_data 下的字段
        license_plate: item?.processed_data?.license_plate ?? '',
        carriage_number: item?.processed_data?.carriage_number ?? '',
        actual_volume: item?.processed_data?.actual_volume ?? '',
        vehicle_type: item?.processed_data?.vehicle_type ?? '',
        vehicle_category: item?.processed_data?.vehicle_category ?? '',
        // 保留用于显示状态和错误信息
        valid: item?.valid ?? false,
        errors: Array.isArray(item?.errors) ? item.errors : []
      }))
    })
    
    // 计算是否可以进行下一步
    const canProceed = computed(() => {
      if (currentStep.value === 0) {
        return selectedFile.value !== null
      }
      if (currentStep.value === 1) {
        return previewData.value.summary?.valid_count > 0
      }
      return false
    })
    
    // 获取下一步按钮文本
    const getNextButtonText = () => {
      if (currentStep.value === 0) return '解析数据'
      if (currentStep.value === 1) return '开始导入'
      return '下一步'
    }
    
    // 下载模板
    const downloadTemplate = async () => {
      try {
        downloadLoading.value = true
        const response = await vehicleService.downloadImportTemplate()

        // 兼容拦截器已返回 Blob 的情况（response 即为 Blob），
        // 以及未来可能返回 { data: Blob } 的情况
        let blob
        if (response instanceof Blob) {
          blob = response
        } else if (response && response.data instanceof Blob) {
          blob = response.data
        } else {
          // 不符合预期，避免把 undefined 或对象当作文件写入
          throw new Error('响应不是文件流，请检查登录状态或后端接口返回')
        }

        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'vehicle_import_template.xlsx'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('模板下载成功')
      } catch (error) {
        ElMessage.error('模板下载失败：' + error.message)
      } finally {
        downloadLoading.value = false
      }
    }
    
    // 文件选择处理
    const handleFileChange = (file) => {
      selectedFile.value = file
    }
    
    // 文件上传前验证
    const beforeUpload = (file) => {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                     file.type === 'application/vnd.ms-excel'
      const isLt10M = file.size / 1024 / 1024 < 10
      
      if (!isExcel) {
        ElMessage.error('只能上传Excel文件！')
        return false
      }
      if (!isLt10M) {
        ElMessage.error('文件大小不能超过10MB！')
        return false
      }
      return false // 阻止自动上传
    }
    
    // 移除文件
    const removeFile = () => {
      selectedFile.value = null
    }
    
    // 下一步
    const nextStep = async () => {
      if (currentStep.value === 0) {
        await parseFile()
      } else if (currentStep.value === 1) {
        await executeImport()
      }
    }
    
    // 上一步
    const prevStep = () => {
      if (currentStep.value > 0) {
        currentStep.value--
      }
    }
    
    // 解析文件
    const parseFile = async () => {
      if (!selectedFile.value) {
        ElMessage.error('请选择要上传的文件')
        return
      }
      
      try {
        processing.value = true
        
        const formData = new FormData()
        formData.append('file', selectedFile.value.raw)
        
        const response = await vehicleService.previewImportData(formData)
        
        if (response.code === 0) {
          previewData.value = response.data
          currentStep.value = 1
          
          if (response.data.summary?.invalid_count > 0) {
            ElMessage.warning(`发现 ${response.data.summary.invalid_count} 条错误记录，请检查后再导入`)
          }
        } else {
          ElMessage.error(response.message || '文件解析失败')
        }
      } catch (error) {
        ElMessage.error('文件解析失败：' + error.message)
      } finally {
        processing.value = false
      }
    }
    
    // 执行导入
    const executeImport = async () => {
      try {
        processing.value = true
        
        const response = await vehicleService.executeImport({
          validation_results: previewData.value.validation_results,
          filename: selectedFile.value?.name
        })
        
        if (response.code === 0) {
          importResult.value = response.data.import_result
          importStatistics.value = response.data.statistics
          currentStep.value = 2
          
          if (importResult.value.success) {
            ElMessage.success('导入完成！')
          } else {
            ElMessage.error('导入失败：' + importResult.value.message)
          }
        } else {
          ElMessage.error(response.message || '导入失败')
        }
      } catch (error) {
        ElMessage.error('导入失败：' + error.message)
      } finally {
        processing.value = false
      }
    }
    
    // 导出错误报告
    const exportErrors = async () => {
      try {
        exportLoading.value = true
        
        const response = await vehicleService.exportValidationErrors({
          validation_results: previewData.value.validation_results
        })
        
        // 兼容拦截器已返回 Blob 的情况
        let blob
        if (response instanceof Blob) {
          blob = response
        } else if (response && response.data instanceof Blob) {
          blob = response.data
        } else {
          throw new Error('响应不是文件流，请检查后端接口返回')
        }
        
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'validation_errors_report.xlsx'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('错误报告导出成功')
      } catch (error) {
        ElMessage.error('导出失败：' + error.message)
      } finally {
        exportLoading.value = false
      }
    }
    
    // 关闭对话框
    const handleClose = () => {
      visible.value = false
    }
    
    // 完成导入
    const handleFinish = () => {
      emit('import-success')
      handleClose()
    }
    
    // 重置状态
    const resetState = () => {
      currentStep.value = 0
      selectedFile.value = null
      previewData.value = {}
      importResult.value = {}
      importStatistics.value = null
      processing.value = false
    }
    
    // 监听对话框关闭
    watch(visible, (newVal) => {
      if (!newVal) {
        resetState()
      }
    })
    
    return {
      visible,
      currentStep,
      selectedFile,
      previewData,
      importResult,
      importStatistics,
      downloadLoading,
      processing,
      exportLoading,
      canProceed,
      getNextButtonText,
      downloadTemplate,
      handleFileChange,
      beforeUpload,
      removeFile,
      nextStep,
      prevStep,
      exportErrors,
      handleClose,
      handleFinish,
      previewRows
    }
  }
}
</script>

<style scoped>
.import-steps {
  margin-bottom: 30px;
}

.upload-step {
  padding: 20px 0;
}

.template-download {
  margin-bottom: 30px;
}

.template-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 15px;
}

.tip {
  color: #909399;
  font-size: 14px;
}

.upload-area {
  margin: 20px 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-step {
  padding: 20px 0;
}

.preview-summary {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.preview-actions {
  margin-bottom: 15px;
  text-align: right;
}

.preview-table {
  margin-top: 15px;
}

.error-messages {
  max-height: 100px;
  overflow-y: auto;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 5px;
  color: #f56c6c;
  font-size: 12px;
}

.success-text {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #67c23a;
  font-size: 12px;
}

.result-step {
  padding: 20px 0;
}

.result-summary {
  text-align: left;
}

.success-count {
  color: #67c23a;
  font-size: 16px;
  margin-bottom: 10px;
}

.error-count {
  color: #f56c6c;
  font-size: 16px;
  margin-bottom: 15px;
}

.statistics {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.statistics h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.category-tag {
  margin-right: 10px;
}

.error-summary {
  color: #f56c6c;
  font-size: 16px;
}

.error-details {
  margin-top: 20px;
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
}

.error-list .error-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.error-list .error-item:last-child {
  border-bottom: none;
}

.dialog-footer {
  text-align: right;
}
</style>