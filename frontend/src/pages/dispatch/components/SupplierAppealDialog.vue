<template>
  <el-dialog
    v-model="dialogVisible"
    title="供应商申诉"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <div class="appeal-dialog">
      <!-- 任务基本信息 -->
      <div class="task-info-section">
        <h4>任务信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ task.task_id }}</el-descriptions-item>
          <el-descriptions-item label="邮路名称">{{ task.mail_route_name }}</el-descriptions-item>
          <el-descriptions-item label="需求吨位">{{ task.required_weight }}</el-descriptions-item>
          <el-descriptions-item label="实际吨位">{{ task.actual_weight }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 申诉表单 -->
      <div class="appeal-form-section">
        <h4>申诉信息</h4>
        <el-form
          ref="appealFormRef"
          :model="appealForm"
          :rules="appealRules"
          label-width="120px"
        >
          <el-form-item label="申诉原因" prop="appeal_reason">
            <el-select
              v-model="appealForm.appeal_reason"
              placeholder="请选择申诉原因"
              style="width: 100%"
            >
              <el-option label="降档操作有误" value="downgrade_error" />
              <el-option label="合并吨位计算错误" value="merge_calculation_error" />
              <el-option label="实际容积与记录不符" value="volume_mismatch" />
              <el-option label="其他原因" value="other" />
            </el-select>
          </el-form-item>

          <el-form-item label="申诉说明" prop="appeal_description">
            <el-input
              v-model="appealForm.appeal_description"
              type="textarea"
              :rows="4"
              placeholder="请详细说明申诉原因和具体情况"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="证明材料" prop="appeal_photos">
            <UploadComponent
            ref="uploadComponentRef"
            v-model="appealForm.appeal_photos"
            file-type="image"
            business-type="supplier_appeal"
            :business-id="task.task_id"
            :multiple="true"
            :limit="5"
            list-type="picture-card"
            :auto-upload="false"
            tip="支持jpg/png格式，单个文件不超过5MB，最多上传5张"
            @success="handleUploadSuccess"
            @error="handleUploadError"
          />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          提交申诉
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dispatchService } from '@/services/dispatchService'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import UploadComponent from '@/components/common/UploadComponent.vue'

export default {
  name: 'SupplierAppealDialog',
  components: {
    Plus,
    UploadComponent
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    task: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:visible', 'appeal-success'],
  setup(props, { emit }) {
    const userStore = useUserStore()
    const appealFormRef = ref(null)
    const uploadComponentRef = ref(null)
    const submitting = ref(false)

    // 对话框显示状态
    const dialogVisible = computed({
      get: () => props.visible,
      set: (value) => emit('update:visible', value)
    })

    // 申诉表单数据
    const appealForm = reactive({
      appeal_reason: '',
      appeal_description: '',
      appeal_photos: []
    })

    // 表单验证规则
    const appealRules = {
      appeal_reason: [
        { required: true, message: '请选择申诉原因', trigger: 'change' }
      ],
      appeal_description: [
        { required: true, message: '请填写申诉说明', trigger: 'blur' },
        { min: 10, message: '申诉说明至少10个字符', trigger: 'blur' }
      ]
    }

    // 上传成功处理
    const handleUploadSuccess = (data, file, fileList) => {
      ElMessage.success('图片上传成功')
      
      // 使用组件暴露的方法获取已选文件数量，避免直接访问内部$refs
      const uploadComponent = uploadComponentRef.value
      const totalFiles = uploadComponent?.getSelectedCount?.() ?? (Array.isArray(fileList) ? fileList.length : 0)
      const uploadedFiles = Array.isArray(appealForm.appeal_photos) ? appealForm.appeal_photos.length : 0
      
      // 当所有文件上传完成且处于提交中状态时，提交申诉数据
      if (submitting.value && totalFiles > 0 && uploadedFiles >= totalFiles) {
        submitAppealData()
      }
    }

    // 提交申诉数据
    const submitAppealData = async () => {
      try {
        const submitData = {
          appeal_reason: appealForm.appeal_reason,
          appeal_description: appealForm.appeal_description,
          appeal_photos: appealForm.appeal_photos.map(file => file.url || file.path)
        }

        const result = await dispatchService.submitSupplierAppeal(props.task.task_id, submitData)

        if (result && result.code === 0) {
          ElMessage.success('申诉提交成功，请等待审核')
          emit('appeal-success', result.data)
          handleClose()
        } else {
          ElMessage.error(result?.message || '申诉提交失败')
        }
      } catch (error) {
        console.error('申诉数据提交失败:', error)
        ElMessage.error('申诉提交失败')
      } finally {
        submitting.value = false
      }
    }

    // 上传失败处理
    const handleUploadError = (error, file, fileList) => {
      ElMessage.error('图片上传失败')
      submitting.value = false
    }

    // 提交申诉
    const handleSubmit = async () => {
      if (!appealFormRef.value) return

      try {
        // 表单验证
        await appealFormRef.value.validate()

        // 检查是否选择了证明材料文件（兼容手动上传未提交场景）
        const uploadComponent = uploadComponentRef.value
        const selectedCount = uploadComponent?.getSelectedCount?.() ?? 0
        const hasModelFiles = Array.isArray(appealForm.appeal_photos) && appealForm.appeal_photos.length > 0
        if (selectedCount === 0 && !hasModelFiles) {
          ElMessage.warning('请上传至少一张证明材料')
          return
        }

        // 二次确认
        await ElMessageBox.confirm(
          '确认提交申诉？申诉提交后将进入审核流程。',
          '确认提交',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        submitting.value = true

        // 如果是手动上传模式，优先提交未上传的选中文件
        if (uploadComponent && uploadComponent.submit && selectedCount > appealForm.appeal_photos.length) {
          uploadComponent.submit()
          // 后续由 handleUploadSuccess 在全部上传完成后触发 submitAppealData
        } else {
          // v-model 已包含文件或没有待上传文件，直接提交
          await submitAppealData()
        }
        
      } catch (error) {
        if (error !== 'cancel') {
          console.error('申诉提交失败:', error)
          ElMessage.error('申诉提交失败')
        }
        submitting.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      if (appealFormRef.value) {
        appealFormRef.value.resetFields()
      }
      appealForm.appeal_reason = ''
      appealForm.appeal_description = ''
      appealForm.appeal_photos = []
      // 清空上传组件内部文件列表与预览，避免再次打开残留
      const comp = uploadComponentRef.value
      if (comp && typeof comp.clearFiles === 'function') {
        try { comp.clearFiles() } catch (e) {}
      }
    }

    // 处理对话框关闭
    const handleClose = () => {
      dialogVisible.value = false
      resetForm()
    }

    // 监听对话框显示状态
    watch(() => props.visible, (visible) => {
      if (visible) {
        resetForm()
      }
    })

    return {
      dialogVisible,
      appealFormRef,
      uploadComponentRef,
      appealForm,
      appealRules,
      submitting,
      handleUploadSuccess,
      handleUploadError,
      handleSubmit,
      handleClose,
      submitAppealData
    }
  }
}
</script>

<style scoped>
.appeal-dialog {
  padding: 20px;
}

.task-info-section {
  margin-bottom: 20px;
}

.task-info-section h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
}

.appeal-form-section {
  margin-bottom: 20px;
}

.appeal-form-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style>