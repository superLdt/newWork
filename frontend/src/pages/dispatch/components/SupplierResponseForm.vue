<template>
  <div class="supplier-response-container">
    <!-- 权限检查 -->
    <div v-if="!hasResponsePermission" class="no-permission">
      <el-alert
        title="权限不足"
        description="您没有权限响应此任务，请联系管理员"
        type="warning"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 供应商响应表单 -->
    <div v-else>
      <el-card class="task-info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <h3>任务信息</h3>
            <el-tag :type="getStatusType(task.status)">{{ getStatusText(task.status) }}</el-tag>
          </div>
        </template>
        
        <!-- 任务基本信息（只读） -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ task.task_id }}</el-descriptions-item>
          <el-descriptions-item label="需求日期">{{ task.required_date }}</el-descriptions-item>
          <el-descriptions-item label="始发局">{{ task.origin_bureau }}</el-descriptions-item>
          <el-descriptions-item label="邮路名称">{{ task.mail_route_name }}</el-descriptions-item>
          <el-descriptions-item label="运输类型">{{ task.transport_type }}</el-descriptions-item>
          <el-descriptions-item label="需求类型">{{ task.requirement_type }}</el-descriptions-item>
          <el-descriptions-item label="标准吨位">{{ task.standard_weight }}吨</el-descriptions-item>
          <el-descriptions-item label="实际需求容积">{{ task.actual_volume }}m³</el-descriptions-item>
          <el-descriptions-item label="特殊要求" :span="2">{{ task.special_requirements || '无' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="response-form-card" shadow="never">
        <template #header>
          <h3>车辆响应信息</h3>
        </template>

        <el-form
          ref="responseFormRef"
          :model="responseForm"
          :rules="responseRules"
          label-width="120px"
          label-position="right"
        >
          <!-- 必填字段：货票号和派车单号 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="货票号" prop="manifest_number">
                <el-input 
                  v-model="responseForm.manifest_number" 
                  placeholder="请输入货票号"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="派车单号" prop="dispatch_number">
                <el-input 
                  v-model="responseForm.dispatch_number" 
                  placeholder="请输入派车单号"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 车辆信息 -->
          <el-divider content-position="left">
            <el-icon><Van /></el-icon>
            车辆信息
          </el-divider>

          <!-- 车辆选择（表格多选 + 过滤） -->
          <div class="vehicle-select">
            <el-row :gutter="12" class="vehicle-filter">
              <el-col :span="18">
                <el-input v-model="vehicleFilter" placeholder="按车牌号/司机姓名搜索可用车辆" clearable />
              </el-col>
              <el-col :span="6" style="text-align:right;">
                <el-button :loading="loadingVehicles" @click="fetchAvailableVehicles">刷新列表</el-button>
              </el-col>
            </el-row>

            <el-table
              :data="filteredVehicles"
              v-loading="loadingVehicles"
              border
              height="360"
              @selection-change="rows => { selectedVehicles = rows; mapSelectedToPayload(); }"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="plate_number" label="车牌号" width="140" />
              <el-table-column prop="driver_name" label="司机" width="120" />
              <el-table-column prop="driver_phone" label="电话" width="140" />
              <el-table-column prop="vehicle_type" label="车型" width="120" />
              <el-table-column prop="capacity" label="载重(吨)" width="120">
                <template #default="scope">{{ scope.row.capacity ?? '-' }}</template>
              </el-table-column>
              <el-table-column prop="volume" label="容积(m³)" width="120">
                <template #default="scope">{{ scope.row.volume ?? '-' }}</template>
              </el-table-column>
            </el-table>

            <div style="margin-top:8px; text-align:right; color:#909399;">
              已选择 {{ selectedVehicles.length }} 辆车辆
            </div>
          </div>

          <!-- 响应备注 -->
          <el-form-item label="响应备注" prop="notes">
            <el-input 
              v-model="responseForm.notes" 
              type="textarea" 
              :rows="3"
              placeholder="请输入响应备注或特殊说明"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <!-- 操作按钮 -->
          <el-form-item>
            <div class="form-actions">
              <el-button 
                type="primary" 
                size="large"
                :loading="submitting"
                @click="submitResponse"
              >
                <el-icon><Check /></el-icon>
                提交响应
              </el-button>
              <el-button size="large" @click="cancel">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Van, 
  Plus, 
  Delete, 
  Check, 
  Close 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { dispatchService } from '@/services/dispatchService'

export default {
  name: 'SupplierResponseForm',
  components: {
    Van,
    Plus,
    Delete,
    Check,
    Close
  },
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  emits: ['response-success', 'cancel'],
  setup(props, { emit }) {
    const userStore = useUserStore()
    const permissionStore = usePermissionStore()
    const responseFormRef = ref(null)
    const submitting = ref(false)

    // 新增：可用车辆数据源
    const loadingVehicles = ref(false)
    const allVehicles = ref([])
    const vehicleFilter = ref('')
    const selectedVehicles = ref([])

    // 权限检查（允许在开发/未下发权限时按角色放行）
    const hasResponsePermission = computed(() => {
      // 1) 具备任一权限码，直接放行
      const checkPerm = permissionStore.hasPermission
      const hasPerm = (code) => (typeof checkPerm === 'function' ? checkPerm(code) : (checkPerm?.(code) || false))
      const neededPerms = ['supplier:respond', 'team:assign', 'outsourcing:assign']
      if (neededPerms.some(p => hasPerm(p))) return true

      // 2) 若权限列表未加载（为空），按角色兜底放行，避免联调受阻
      const perms = permissionStore.permissions || []
      const skipStrict = !Array.isArray(perms) || perms.length === 0
      if (!skipStrict) return false

      // 3) 角色兜底（从 permissionStore -> userStore 依次获取）
      let derivedRole = ''
      const info = permissionStore.userInfo
      if (info && Array.isArray(info.roles) && info.roles.length > 0) {
        // 后端返回的角色对象数组 [{ id, name }, ...]
        derivedRole = info.roles[0]?.name || ''
      } else if (Array.isArray(permissionStore.roles) && permissionStore.roles.length > 0) {
        // permissionStore 中已展开的角色名数组 ["供应商", ...]
        derivedRole = permissionStore.roles[0]
      } else if (userStore?.currentUser?.role_name) {
        // 兜底到 userStore（如存在）
        derivedRole = userStore.currentUser.role_name
      }

      const allowedRoles = ['供应商', '班组长', '外包管理公司', 'supplier', 'team_leader', 'outsourcing_manager']
      return allowedRoles.includes(derivedRole)
    })

    // 响应表单数据
    const responseForm = reactive({
      task_id: props.task.task_id,
      manifest_number: '',
      dispatch_number: '',
      vehicles: [], // 将由选择的车辆映射生成
      notes: ''
    })

    // 表单验证规则
    const responseRules = {
      manifest_number: [
        { required: true, message: '请输入货票号', trigger: 'blur' }
      ],
      dispatch_number: [
        { required: true, message: '请输入派车单号', trigger: 'blur' }
      ],
      vehicles: [
        { type: 'array', required: true, message: '请至少选择一辆车辆', trigger: 'change' }
      ],
      notes: [
        { max: 500, message: '备注不能超过500个字符', trigger: 'blur' }
      ]
    }

    // 新增：可用车辆过滤
    const filteredVehicles = computed(() => {
      if (!vehicleFilter.value) return allVehicles.value
      const keyword = vehicleFilter.value.toLowerCase()
      return allVehicles.value.filter(v => (
        (v.plate_number || '').toLowerCase().includes(keyword) ||
        (v.driver_name || '').toLowerCase().includes(keyword)
      ))
    })

    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        pending: 'warning',
        awaiting_supplier_response: 'info',
        awaiting_team_assignment: 'info',
        supplier_responded: 'success',
        team_assigned: 'success',
        approved: 'success',
        rejected: 'danger',
        completed: 'success'
      }
      return statusMap[status] || 'info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        pending: '待审核',
        awaiting_supplier_response: '待供应商响应',
        awaiting_team_assignment: '待班组派车',
        supplier_responded: '供应商已响应',
        team_assigned: '班组已派车',
        approved: '已审批',
        rejected: '已拒绝',
        completed: '已完成'
      }
      return statusMap[status] || status
    }

    // 提交响应（基于选择的车辆）
    const submitResponse = async () => {
      if (!responseFormRef.value) return
      await responseFormRef.value.validate(async (valid) => {
        if (!valid) return
        try {
          await ElMessageBox.confirm(
            '确认提交响应信息？提交后将无法修改。',
            '确认提交',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )

          submitting.value = true

          const totalVolume = (responseForm.vehicles || []).reduce((sum, v) => sum + (Number(v.actual_volume) || 0), 0)
          if (typeof props.task.actual_volume === 'number' && totalVolume < props.task.actual_volume) {
            ElMessage.warning(`车辆总容积(${totalVolume}m³)小于任务需求(${props.task.actual_volume}m³)，请确认是否继续提交`)
          }

          const userRole = userStore.currentUser?.role_name
          const requestData = {
            task_id: responseForm.task_id,
            manifest_number: responseForm.manifest_number,
            dispatch_number: responseForm.dispatch_number,
            vehicles: responseForm.vehicles,
            notes: responseForm.notes
          }

          let result
          if (userRole === '供应商' || userRole === 'supplier') {
            result = await dispatchService.submitSupplierResponse(requestData)
          } else if (userRole === '班组长' || userRole === 'team_leader') {
            result = await dispatchService.submitTeamResponse(requestData)
          } else if (userRole === '外包管理公司' || userRole === 'outsourcing_manager') {
            result = await dispatchService.submitOutsourcingResponse(requestData)
          } else {
            throw new Error('当前角色无权限进行此操作')
          }

          ElMessage.success('响应提交成功')
          emit('response-success', result)
        } catch (error) {
          if (error !== 'cancel') {
            console.error('提交响应失败:', error)
            ElMessage.error(error?.message || '提交响应失败')
          }
        } finally {
          submitting.value = false
        }
      })
    }

    // 取消
    const cancel = () => emit('cancel')

    // 将选择映射为提交 payload 所需字段
    const mapSelectedToPayload = () => {
      responseForm.vehicles = (selectedVehicles.value || []).map(v => ({
        license_plate: v.plate_number,
        carriage_number: v.carriage_number || '',
        driver_name: v.driver_name,
        driver_phone: v.driver_phone,
        vehicle_type: v.vehicle_type,
        load_capacity: v.capacity,
        actual_volume: v.volume
      }))
    }

    // 获取可用车辆
    const fetchAvailableVehicles = async () => {
      loadingVehicles.value = true
      try {
        if (!hasResponsePermission.value) {
          // 无权限时不发起请求，直接退出
          allVehicles.value = []
          return
        }
        const result = await dispatchService.getAvailableVehicles()
        allVehicles.value = result.data || []
      } catch (e) {
        console.error('获取可用车辆失败:', e)
        ElMessage.error('获取可用车辆失败')
      } finally {
        loadingVehicles.value = false
      }
    }

    onMounted(async () => {
      responseForm.task_id = props.task.task_id
      if (!hasResponsePermission.value) return
      await fetchAvailableVehicles()
    })

    return {
      responseFormRef,
      submitting,
      hasResponsePermission,
      responseForm,
      responseRules,
      // 移除旧的 vehicleRules & 手动添加删除逻辑，不再暴露
      getStatusType,
      getStatusText,
      // 新增：选择相关
      loadingVehicles,
      allVehicles,
      vehicleFilter,
      filteredVehicles,
      selectedVehicles,
      mapSelectedToPayload,
      fetchAvailableVehicles,
      // 提交/取消
      submitResponse,
      cancel
    }
  }
}
</script>

<style scoped>
.supplier-response-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.no-permission {
  text-align: center;
  padding: 40px;
}

.task-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.response-form-card {
  border-radius: 8px;
}

.vehicle-list {
  margin: 20px 0;
}

.vehicle-item {
  margin-bottom: 16px;
}

.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.add-vehicle-btn {
  text-align: center;
  margin: 20px 0;
}

.form-actions {
  text-align: center;
  padding-top: 20px;
}

.form-actions .el-button {
  margin: 0 10px;
  min-width: 120px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .supplier-response-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 10px;
  }
}

/* 美化样式 */
.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-divider {
  margin: 24px 0;
  font-weight: 600;
  color: #409eff;
}

.el-form-item {
  margin-bottom: 18px;
}

.el-input, .el-select {
  border-radius: 6px;
}

.el-button {
  border-radius: 6px;
  font-weight: 500;
}

.el-button--primary {
  background: linear-gradient(135deg, #409eff 0%, #1890ff 100%);
  border: none;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #40a9ff 100%);
}
</style>