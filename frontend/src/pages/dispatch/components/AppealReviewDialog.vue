<template>
  <el-dialog
    v-model="dialogVisible"
    title="申诉审核"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="appeal-review-container" v-if="task">
      <!-- 任务基本信息 -->
      <el-card class="task-info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>任务信息</span>
          </div>
        </template>
        <!-- 任务编号单独一行 -->
        <el-row :gutter="16">
          <el-col :span="24">
            <div class="info-item task-number-item">
              <span class="label">任务编号：</span>
              <span class="value task-number">{{ task.task_id }}</span>
            </div>
          </el-col>
        </el-row>
        <!-- 业务类型和状态 -->
        <el-row :gutter="16" style="margin-top: 12px;">
          <el-col :span="12">
            <div class="info-item">
              <span class="label">业务类型：</span>
              <span class="value">{{ task.business_type }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">当前状态：</span>
              <el-tag :type="getStatusType(task.status)">{{ task.status }}</el-tag>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="16" style="margin-top: 12px;">
          <el-col :span="12">
            <div class="info-item">
              <span class="label">起始地：</span>
              <span class="value">{{ task.origin_bureau }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">邮路名称：</span>
              <span class="value">{{ task.mail_route_name }}</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 申诉详情 -->
      <el-card class="appeal-info-card" shadow="never" style="margin-top: 16px;">
        <template #header>
          <div class="card-header">
            <el-icon><Warning /></el-icon>
            <span>申诉详情</span>
          </div>
        </template>
        <div v-if="appealInfo">
          <el-row :gutter="16">
            <el-col :span="12">
              <div class="info-item">
                <span class="label">申诉时间：</span>
                <span class="value">{{ formatDateTime(appealInfo.created_at) }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="label">申诉人：</span>
                <span class="value">{{ appealInfo.supplier_name || '供应商' }}</span>
              </div>
            </el-col>
          </el-row>
          <div class="info-item" style="margin-top: 12px;">
            <span class="label">申诉原因：</span>
            <el-tag type="warning" style="margin-left: 8px;">{{ translateAppealReason(appealInfo.reason) }}</el-tag>
          </div>
          <div class="info-item" style="margin-top: 12px;">
            <span class="label">申诉说明：</span>
            <div class="description-content">{{ appealInfo.description || '无' }}</div>
          </div>
          
          <!-- 证明材料（无数据也显示空态） -->
          <div class="info-item" style="margin-top: 16px;">
            <span class="label">证明材料：</span>
            <div 
              v-if="appealInfo?.evidence_files && appealInfo.evidence_files.length > 0"
              class="evidence-files"
            >
              <div 
                v-for="(file, index) in appealInfo.evidence_files" 
                :key="index"
                class="evidence-item"
              >
                <div v-if="isImageFile(file.filename)" class="image-item">
                  <div class="file-title">{{ file.filename }}</div>
                  <el-image
                    :src="resolveFileUrl(file.url)"
                    :preview-src-list="getImageUrls()"
                    fit="cover"
                    class="evidence-image"
                    :alt="file.filename"
                    @load="(e) => handleImageLoad(e, file)"
                    @error="(e) => handleImageError(e, file)"
                  />
                  <!-- 移除调试URL显示 -->
                </div>
                <div v-else class="file-item">
                  <el-icon><Document /></el-icon>
                  <span>{{ file.filename }}</span>
                  <el-button 
                    type="primary" 
                    size="small" 
                    text
                    @click="downloadFile(file)"
                  >
                    下载
                  </el-button>
                </div>
              </div>
            </div>
            <div v-else class="no-evidence">
              <el-empty description="暂无证明材料" :image-size="60" />
            </div>
          </div>
        </div>
        <div v-else class="no-appeal-info">
          <el-empty description="暂无申诉信息" />
        </div>
      </el-card>

      <!-- 审核操作 -->
      <el-card class="review-action-card" shadow="never" style="margin-top: 16px;">
        <template #header>
          <div class="card-header">
            <el-icon><Select /></el-icon>
            <span>审核操作</span>
          </div>
        </template>
        <el-form :model="reviewForm" :rules="reviewRules" ref="reviewFormRef" label-width="100px">
          <el-form-item label="审核结果" prop="result">
            <el-radio-group v-model="reviewForm.result">
              <el-radio value="approved">
                <el-icon><CircleCheck /></el-icon>
                申诉通过
              </el-radio>
              <el-radio value="rejected">
                <el-icon><Close /></el-icon>
                申诉驳回
              </el-radio>
            </el-radio-group>
          </el-form-item>
          
          <!-- 申诉通过时显示最终确认吨位选择 -->
          <el-form-item 
            v-if="reviewForm.result === 'approved'" 
            label="最终确认吨位" 
            prop="finalTonnage"
          >
            <el-select 
              v-model="reviewForm.finalTonnage" 
              placeholder="请选择最终确认吨位"
              style="width: 200px;"
            >
              <el-option
                v-for="tonnage in tonnageOptions"
                :key="tonnage"
                :label="tonnage"
                :value="tonnage"
              />
            </el-select>
            <span class="form-tip">申诉通过时需要确认最终吨位数</span>
          </el-form-item>
          
          <el-form-item label="审核意见" prop="comment">
            <el-input
              v-model="reviewForm.comment"
              type="textarea"
              :rows="4"
              placeholder="请输入审核意见..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSubmitReview"
          :loading="submitting"
        >
          提交审核
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, Warning, Select, CircleCheck, Close
} from '@element-plus/icons-vue'
import { dispatchService } from '@/services/dispatchService'

export default {
  name: 'AppealReviewDialog',
  components: {
    Document,
    Warning,
    Select,
    CircleCheck,
    Close
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    task: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible', 'review-success'],
  setup(props, { emit }) {
    const reviewFormRef = ref(null)
    const submitting = ref(false)
    const appealInfo = ref(null)

    const dialogVisible = computed({
      get: () => props.visible,
      set: (value) => emit('update:visible', value)
    })

    const reviewForm = reactive({
      result: '',
      comment: '',
      finalTonnage: ''
    })

    const reviewRules = {
      result: [
        { required: true, message: '请选择审核结果', trigger: 'change' }
      ],
      finalTonnage: [
        { 
          validator: (rule, value, callback) => {
            if (reviewForm.result === 'approved' && !value) {
              callback(new Error('申诉通过时必须选择最终确认吨位'))
            } else {
              callback()
            }
          }, 
          trigger: 'change' 
        }
      ],
      comment: [
        { required: true, message: '请输入审核意见', trigger: 'blur' },
        { min: 5, message: '审核意见至少5个字符', trigger: 'blur' }
      ]
    }

    // 吨位选项
    const tonnageOptions = ref([
      '5吨', '8吨', '12吨', '20吨', '30吨', '40吨A', '40吨B'
    ])

    // 监听对话框打开，获取申诉信息
    watch(() => props.visible, async (newVal) => {
      if (newVal && props.task) {
        await fetchAppealInfo()
      }
    })

    // 获取申诉信息
    const fetchAppealInfo = async () => {
      try {
        // 调用获取申诉详情的API
        const response = await fetch(`/api/v1/dispatch/tasks/${props.task.task_id}/appeal`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const result = await response.json()
        
        // 兼容后端返回结构：有的接口返回 { code: 200, message, data }，
        // 也可能由服务封装成 { code: 0, ... }，因此统一以 code 判断成功
        const isSuccess = (
          (typeof result.code !== 'undefined' && (result.code === 200 || result.code === 0)) ||
          result.success === true
        )
        
        if (isSuccess) {
          console.log('Appeal info received:', result.data)
          appealInfo.value = {
            created_at: result.data.appeal_submitted_at,
            supplier_name: result.data.appeal_user_name,
            reason: result.data.appeal_reason,
            description: result.data.appeal_description,
            evidence_files: (result.data.evidence_files || []).map(f => {
              console.log('Processing file:', f)
              return {
                ...f,
                url: f.url // 保持原始URL，让resolveFileUrl函数处理
              }
            })
          }
          console.log('Final appeal info:', appealInfo.value)
        } else {
          throw new Error(result.message || '获取申诉信息失败')
        }
      } catch (error) {
        console.error('获取申诉信息失败:', error)
        ElMessage.error('获取申诉信息失败')
        // 使用默认数据作为后备
        appealInfo.value = {
          created_at: new Date().toISOString(),
          supplier_name: '未知供应商',
          reason: '申诉信息获取失败',
          description: '无法获取申诉详情，请联系管理员。',
          evidence_files: []
        }
      }
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        '待审核': 'warning',
        '审核通过': 'success',
        '待响应': 'info',
        '已响应': 'primary',
        '任务完成': 'success',
        '审核拒绝': 'danger',
        '申诉待审核': 'warning'
      }
      return statusMap[status] || 'info'
    }

    // 格式化日期时间
    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString('zh-CN')
    }

    // 判断是否为图片文件
    const isImageFile = (filename) => {
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
      const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'))
      return imageExtensions.includes(ext)
    }

    // 获取所有图片URL用于预览
    const getImageUrls = () => {
      if (!appealInfo.value?.evidence_files) return []
      const urls = appealInfo.value.evidence_files
        .filter(file => isImageFile(file.filename))
        .map(file => resolveFileUrl(file.url))
      console.log('Preview image URLs:', urls)
      return urls
    }

    // 下载文件
    const downloadFile = (file) => {
      const link = document.createElement('a')
      link.href = resolveFileUrl(file.url)
      link.download = file.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // 规范化后端返回的文件URL为可访问的绝对地址
    const resolveFileUrl = (url) => {
      if (!url) return ''
      const raw = String(url)
      const trimmed = raw.trim()
      
      // 如果已经是绝对URL，直接返回
      const isAbsolute = /^https?:\/\//i.test(trimmed)
      if (isAbsolute) return trimmed
      
      // 获取基础URL（优先使用环境变量）
      const baseUrl = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.host}`
      
      // 如果已经是完整的API路径，添加基础URL
      if (trimmed.startsWith('/api/v1/upload/files/')) {
        const fullUrl = `${baseUrl}${trimmed}`
        return fullUrl
      }
      
      // 若是不带开头斜杠但已包含api/v1前缀，补齐开头斜杠并添加基础URL
      if (trimmed.startsWith('api/v1/upload/files/')) {
        const fullUrl = `${baseUrl}/${trimmed}`
        return fullUrl
      }
      
      // 处理相对路径，统一转换为后端文件访问路径
      let cleanUrl = trimmed
      if (cleanUrl.startsWith('/')) {
        cleanUrl = cleanUrl.substring(1) // 移除开头的斜杠
      }
      
      // 构建完整的文件访问URL
      const fullUrl = `${baseUrl}/api/v1/upload/files/${cleanUrl}`
      return fullUrl
    }

    // 图片加载与错误日志
    const handleImageLoad = (event, file) => {
      const src = resolveFileUrl(file.url)
      console.log('Image loaded successfully:', { filename: file.filename, src })
    }
    const handleImageError = (event, file) => {
      const src = resolveFileUrl(file.url)
      console.error('Image failed to load:', { 
        filename: file.filename, 
        originalUrl: file.url,
        resolvedSrc: src, 
        event,
        errorType: event.type,
        target: event.target
      })
      ElMessage.warning(`图片加载失败：${file.filename}`)
    }

    // 提交审核
    const handleSubmitReview = async () => {
      try {
        const valid = await reviewFormRef.value.validate()
        if (!valid) return

        await ElMessageBox.confirm(
          `确定要${reviewForm.result === 'approved' ? '通过' : '驳回'}此申诉吗？`,
          '确认审核',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        submitting.value = true

        const reviewData = {
          review_result: reviewForm.result,
          review_notes: reviewForm.comment,
          final_tonnage: reviewForm.finalTonnage
        }

        await dispatchService.processAppealReview(props.task.task_id, reviewData)

        ElMessage.success(`申诉${reviewForm.result === 'approved' ? '通过' : '驳回'}成功`)
        emit('review-success', {
          task_id: props.task.task_id,
          result: reviewForm.result
        })
        handleClose()

      } catch (error) {
        console.error('提交审核失败:', error)
        ElMessage.error('提交审核失败')
      } finally {
        submitting.value = false
      }
    }

    // 翻译申诉原因
    const translateAppealReason = (reason) => {
      const reasonMap = {
        'downgrade_error': '降档错误',
        'tonnage_error': '吨位错误',
        'route_error': '路线错误',
        'time_error': '时间错误',
        'vehicle_error': '车辆错误',
        'other': '其他原因'
      }
      return reasonMap[reason] || reason || '未知原因'
    }

    // 关闭对话框
    const handleClose = () => {
      dialogVisible.value = false
      // 重置表单
      reviewForm.result = ''
      reviewForm.comment = ''
      reviewForm.finalTonnage = ''
      appealInfo.value = null
      if (reviewFormRef.value) {
        reviewFormRef.value.resetFields()
      }
    }

    return {
      dialogVisible,
      reviewFormRef,
      submitting,
      appealInfo,
      reviewForm,
      reviewRules,
      tonnageOptions,
      getStatusType,
      formatDateTime,
      isImageFile,
      getImageUrls,
      downloadFile,
      resolveFileUrl,
      translateAppealReason,
      handleImageLoad,
      handleImageError,
      handleSubmitReview,
      handleClose
    }
  }
}
</script>

<style scoped>
.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

.appeal-review-container {
  max-height: 600px;
  overflow-y: auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.task-number-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.task-number {
  font-weight: 600;
  font-size: 16px;
  color: #409eff;
}

.info-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.info-item .label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
  flex-shrink: 0;
}

.info-item .value {
  color: #303133;
  flex: 1;
}

.description-content {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-top: 8px;
  line-height: 1.6;
  color: #303133;
}

.evidence-files {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.evidence-item {
  flex-shrink: 0;
}

.image-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.file-title {
  font-size: 12px;
  color: #606266;
  text-align: center;
  max-width: 120px;
  word-break: break-all;
  line-height: 1.4;
}

.evidence-image {
  width: 120px;
  height: 120px;
  border-radius: 4px;
  cursor: pointer;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.no-appeal-info {
  text-align: center;
  padding: 40px 0;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-radio) {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

:deep(.el-radio__label) {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>