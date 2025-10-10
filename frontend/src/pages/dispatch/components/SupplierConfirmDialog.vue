<template>
  <el-dialog
    v-model="dialogVisible"
    :title="getDialogTitle"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 任务基本信息 -->
    <div class="task-info-section">
      <h4>任务信息</h4>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务ID">{{ task?.task_id }}</el-descriptions-item>
        <el-descriptions-item label="邮路名称">{{ task?.mail_route_name }}</el-descriptions-item>
        <el-descriptions-item label="需求容积">{{ task?.required_volume }}m³</el-descriptions-item>
        <el-descriptions-item label="需求日期">{{ task?.required_date }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 分配车辆信息 -->
    <div v-if="task?.vehicles && task.vehicles.length > 0" class="vehicle-info-section">
      <h4>分配车辆信息</h4>
      <div class="vehicle-grid">
        <div class="vehicle-card" v-for="vehicle in task.vehicles" :key="vehicle.vehicle_id">
          <div class="vehicle-header">
            <div class="vehicle-plate">{{ vehicle.plate_number }}</div>
            <div class="vehicle-tags">
              <el-tag size="small" type="success">{{ vehicle.vehicle_type }}</el-tag>
              <el-tag size="small" type="warning" v-if="vehicle.capacity || vehicle.original_capacity">
                {{ (vehicle.capacity || vehicle.original_capacity) + '吨' }}
              </el-tag>
            </div>
          </div>
          <div class="vehicle-info">
            <div class="info-item">
              <el-icon><Document /></el-icon>
    <span>路单流水号: {{ vehicle.manifest_number || '未提供' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Document /></el-icon>
              <span>派车单: {{ vehicle.dispatch_number || '未提供' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Box /></el-icon>
              <span>实际容积: {{ vehicle.actual_volume || vehicle.volume || '未提供' }} m³</span>
            </div>
            <div class="info-item">
              <el-icon><Box /></el-icon>
              <span>需求容积: {{ vehicle.required_volume || task.required_volume || '未提供' }} m³</span>
            </div>
          </div>
          <div class="vehicle-notes" v-if="vehicle.notes">
            <el-icon><ChatDotRound /></el-icon>
            <span>{{ vehicle.notes }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 合并车辆信息 -->
    <div v-if="mergedVehicles && mergedVehicles.length > 0" class="merged-vehicle-section">
      <h4>合并新增车辆信息</h4>
      <div class="vehicle-grid">
        <div class="vehicle-card merged-vehicle" v-for="mergedVehicle in mergedVehicles" :key="mergedVehicle.id">
          <div class="vehicle-header">
            <div class="vehicle-plate">{{ mergedVehicle.new_vehicle_license_plate }}</div>
            <div class="vehicle-tags">
              <el-tag size="small" type="info">{{ mergedVehicle.new_vehicle_type || '合并车辆' }}</el-tag>
              <el-tag size="small" type="warning" v-if="mergedVehicle.new_vehicle_tonnage">
                {{ mergedVehicle.new_vehicle_tonnage + '吨' }}
              </el-tag>
            </div>
          </div>
          <div class="vehicle-info">
            <div class="info-item">
              <el-icon><Document /></el-icon>
              <span>目标派车单: {{ mergedVehicle.target_dispatch_number || '未提供' }}</span>
            </div>
            <div class="info-item" v-if="mergedVehicle.new_vehicle_carriage_number">
              <el-icon><Document /></el-icon>
              <span>车厢号: {{ mergedVehicle.new_vehicle_carriage_number }}</span>
            </div>
            <div class="info-item">
              <el-icon><Box /></el-icon>
              <span>新增容积: {{ mergedVehicle.new_vehicle_volume || '未提供' }} m³</span>
            </div>
            <div class="info-item">
              <el-icon><Box /></el-icon>
              <span>合并后容积: {{ mergedVehicle.merged_volume || '未提供' }} m³</span>
            </div>
          </div>
          <div class="vehicle-notes" v-if="mergedVehicle.merge_reason">
            <el-icon><ChatDotRound /></el-icon>
            <span>合并原因: {{ mergedVehicle.merge_reason }}</span>
          </div>
          <div class="merge-info">
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>操作人: {{ mergedVehicle.operator_name }}</span>
            </div>
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span>操作时间: {{ formatDateTime(mergedVehicle.operation_time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作提示信息 -->
    <div v-if="operationRecords.has_operations" class="operation-alerts">
      <h4>操作记录</h4>
      <el-alert
        v-for="record in displayRecords"
        :key="record.id"
        :title="record.operation_type"
        :type="getOperationAlertType(record.operation_type)"
        :description="record.description"
        class="alert-item"
        show-icon
        :closable="false"
        :effect="isImportantOperation(record.operation_type) ? 'dark' : 'light'"
      />
    </div>

    <!-- 重要操作警告 -->
    <div v-if="hasImportantOperations" class="important-operation-warning">
      <el-alert
        title="重要操作提示"
        type="warning"
        description="当前任务存在降档或合并等重要操作，请仔细确认相关信息后再进行确认。"
        show-icon
        :closable="false"
        effect="dark"
      />
    </div>

    <!-- 确认表单 -->
    <div class="confirm-form-section">
      <h4>确认信息</h4>
      <el-form
        ref="confirmFormRef"
        :model="confirmForm"
        :rules="confirmRules"
        label-width="120px"
      >
        <el-form-item label="最终确认吨位">
          <div class="final-weight-display">
            <span class="weight-value">{{ task?.actual_weight || '未提供' }}</span>
          </div>
        </el-form-item>
        
        <el-form-item label="确认备注">
          <el-input
            v-model="confirmForm.confirmation_notes"
            type="textarea"
            :rows="3"
            placeholder="请输入确认备注（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <!-- 只有委办派车才显示申诉按钮，班组响应和大容积响应不显示 -->
        <el-button 
          v-if="shouldShowAppealButton"
          type="warning" 
          @click="handleAppeal" 
          :loading="submitting"
        >
          申诉
        </el-button>
        <el-button type="primary" @click="handleConfirm" :loading="submitting">
          确认完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dispatchService } from '@/services/dispatchService'
import { Document, Box, ChatDotRound, User, Clock } from '@element-plus/icons-vue'

export default {
  name: 'SupplierConfirmDialog',
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
  emits: ['update:visible', 'confirm-success', 'open-appeal-dialog'],
  setup(props, { emit }) {
    const confirmFormRef = ref(null)
    const submitting = ref(false)
    const operationRecords = ref({
      records: [],
      has_operations: false,
      downgrade_records: [],
      merge_records: [],
      target_merge_records: []
    })
    const mergedVehicles = ref([])
    const hasImportantOperations = ref(false)
    // 派生用于渲染的记录列表 - 只显示重要操作（降档和合并）
    const displayRecords = computed(() => {
      const baseRecords = operationRecords.value.operation_records || operationRecords.value.records || []
      return baseRecords
        .map(r => {
          const note = r?.note || ''
          const statusChange = r?.status_change || ''
          const isDowngrade = note.toLowerCase().includes('downgrade') || statusChange.includes('降档')
          const isMerge = note.toLowerCase().includes('merge') || statusChange.includes('合并')
          
          // 只返回重要操作
          if (!isDowngrade && !isMerge) return null
          
          const opType = isDowngrade ? '降档操作' : '合并操作'
          const desc = `${r?.operator || ''}：${note || statusChange}`.trim()
          return {
            id: r?.id,
            operation_type: opType,
            description: desc,
            original_record: r // 保留原始记录用于后续处理
          }
        })
        .filter(Boolean) // 过滤掉null值
    })

    // 对话框显示状态
    const dialogVisible = computed({
      get: () => props.visible,
      set: (value) => emit('update:visible', value)
    })

    // 动态对话框标题
    const getDialogTitle = computed(() => {
      const businessType = props.task?.business_type
      if (businessType === '大容积派车') {
        return '大容积派车确认'
      } else if (businessType === '自办派车') {
        return '班组确认'
      } else {
        return '供应商确认'
      }
    })

    // 是否显示申诉按钮 - 只有委办派车才显示申诉按钮
    const shouldShowAppealButton = computed(() => {
      const businessType = props.task?.business_type
      // 只有委办派车才显示申诉按钮，班组响应和大容积响应不显示
      return businessType === '委办派车'
    })

    // 确认表单（移除confirmed_volume字段，仅保留备注）
    const confirmForm = reactive({
      confirmation_notes: ''
    })

    // 表单验证规则（移除了confirmed_volume的验证）
    const confirmRules = {
      // 仅保留备注相关的验证规则（如需要）
    }

    // 格式化日期时间
    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      const date = new Date(dateTime)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 加载操作记录
    const getTaskId = () => {
      // 兜底：支持 props.task.task_id 或 props.task.id
      return props.task?.task_id || props.task?.id
    }

    const loadOperationRecords = async () => {
      const tid = getTaskId()
      if (!tid) return
      
      try {
        const result = await dispatchService.getTaskOperationRecords(tid)
        if (result && result.code === 0) {
          operationRecords.value = result.data || {
            downgrade_records: [],
            merge_records: [],
            target_merge_records: [],
            has_operations: false
          }
          
          // 设置合并车辆信息
          mergedVehicles.value = result.data?.vehicle_merge_records || []
          
          // 检查是否有重要操作（降档或合并）
          // 兼容 operation_records 与 records 两种字段名
          const baseRecords = operationRecords.value.operation_records || operationRecords.value.records || []
          // 检查 note/status_change 是否包含降档或合并关键字
          const hasDowngradeOrMerge = baseRecords.some(record => {
            const note = record?.note || ''
            const statusChange = record?.status_change || ''
            return note.includes('降档') || note.includes('合并') ||
                   statusChange.includes('降档') || statusChange.includes('合并') ||
                   note.toLowerCase().includes('downgrade') || note.toLowerCase().includes('merge')
          })

          // 同步标记重要操作
          hasImportantOperations.value = !!hasDowngradeOrMerge
          // 同步 has_operations 以驱动上方操作提示区块显示
          operationRecords.value.has_operations = !!hasDowngradeOrMerge
        }
      } catch (error) {
        console.error('加载操作记录失败:', error)
        operationRecords.value = {
          downgrade_records: [],
          merge_records: [],
          target_merge_records: [],
          has_operations: false
        }
        mergedVehicles.value = []
        hasImportantOperations.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      confirmForm.confirmation_notes = ''
      nextTick(() => {
        confirmFormRef.value?.clearValidate()
      })
    }

    // 处理确认操作
    const handleConfirm = async () => {
      if (!confirmFormRef.value) return

      // 移除了表单验证，因为实际吨位是只读字段
      try {

        // 二次确认
        await ElMessageBox.confirm(
          '确认提交供应商确认信息？提交后任务将标记为已完成。',
          '确认提交',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        submitting.value = true

        // 根据业务类型调用不同的API
        let result
        const businessType = props.task?.business_type
        
        if (businessType === '自办派车') {
          // 班组确认
          result = await dispatchService.confirmTeamTask(props.task.task_id, {
            confirmation_notes: confirmForm.confirmation_notes
          })
        } else if (businessType === '大容积派车') {
          // 大容积供应商确认
          result = await dispatchService.confirmLargeSupplierTask(props.task.task_id, {
            notes: confirmForm.confirmation_notes
          })
        } else {
          // 普通供应商确认（委办派车）
          result = await dispatchService.confirmSupplierTask(props.task.task_id, {
            confirmation_notes: confirmForm.confirmation_notes
          })
        }

        if (result && result.code === 0) {
          ElMessage.success('确认成功')
          emit('confirm-success', result.data)
          handleClose()
        } else {
          ElMessage.error(result?.message || '确认失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('确认操作失败')
        }
      } finally {
        submitting.value = false
      }
    }

    // 处理申诉操作
    const handleAppeal = async () => {
      try {
        // 二次确认
        await ElMessageBox.confirm(
          '确认提交申诉？申诉提交后将进入审核流程，请确保已准备好相关证明材料。',
          '确认申诉',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 打开申诉对话框
        emit('open-appeal-dialog', props.task)
        handleClose()
      } catch (error) {
        // 用户取消申诉
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
        loadOperationRecords()
      }
    })

    // 当任务ID变更或迟到时也触发加载，避免看不到提示
    watch(() => getTaskId(), (tid) => {
      if (dialogVisible.value && tid) {
        loadOperationRecords()
      }
    })

    // 获取操作类型对应的警告类型
    const getOperationAlertType = (operationType) => {
      if (operationType?.includes('降档')) return 'error'  // 使用红色表示降档操作
      if (operationType?.includes('合并')) return 'success'  // 使用绿色表示合并操作
      return 'info'
    }

    // 判断是否为重要操作
    const isImportantOperation = (operationType) => {
      return operationType?.includes('降档') || operationType?.includes('合并')
    }

     return {
       dialogVisible,
       getDialogTitle,
       shouldShowAppealButton,
       confirmFormRef,
       confirmForm,
       confirmRules,
       submitting,
       operationRecords,
       mergedVehicles,
       hasImportantOperations,
       displayRecords,
       formatDateTime,
       getOperationAlertType,
       isImportantOperation,
       handleConfirm,
       handleAppeal,
       handleClose
     }
  }
}
</script>

<style scoped>
.supplier-confirm-dialog {
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

.vehicle-info-section {
  margin-bottom: 20px;
}

.vehicle-info-section h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
}

.vehicle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.vehicle-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.vehicle-plate {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.vehicle-tags {
  display: flex;
  gap: 8px;
}

.vehicle-info {
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.info-item .el-icon {
  color: #909399;
}

.vehicle-notes {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f0f9ff;
  border-radius: 4px;
  color: #409eff;
  font-size: 13px;
}

.merged-vehicle-section {
  margin-bottom: 20px;
}

.merged-vehicle-section h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
}

.merged-vehicle {
  border-color: #67c23a;
  background: #f0f9ff;
}

.merge-info {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

.alert-item {
  margin-bottom: 8px;
}

.operation-alerts {
  margin-bottom: 20px;
}

.operation-alerts h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
}

.operation-alert {
  margin-bottom: 12px;
}

.operation-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.operation-list li {
  margin-bottom: 6px;
  line-height: 1.5;
}

.confirm-form-section {
  margin-bottom: 20px;
}

.confirm-form-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.unit-text {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-alert__content) {
  line-height: 1.6;
}

.important-operation-warning {
  margin-bottom: 20px;
}

.final-weight-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.weight-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.weight-unit {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
}
</style>