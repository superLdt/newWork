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
          <el-descriptions-item label="需求吨位">{{ formattedRequiredWeight }}</el-descriptions-item>
          <el-descriptions-item label="需求容积">{{ task.required_volume }}m³</el-descriptions-item>
          <el-descriptions-item label="容积区间" v-if="tonnageVolumeRange">{{ tonnageVolumeRange }}</el-descriptions-item>
          <el-descriptions-item label="容积区间(调试)" v-else>未获取到容积区间数据</el-descriptions-item>
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
          <!-- 必填字段：路单流水号和派车单号 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="路单流水号" prop="manifest_number">
                <el-input 
                  v-model="responseForm.manifest_number" 
                  placeholder="请输入路单流水号"
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

          <!-- 车辆选择（左右分栏布局） -->
          <div class="vehicle-selection-container">
            <!-- 车辆选择区域 -->
            <el-row :gutter="20">
              <!-- 左侧：车辆信息表格 -->
              <el-col :span="14">
                <el-card class="vehicle-table-card" shadow="never">
                  <template #header>
                    <div class="card-header">
                      <h4>可用车辆列表</h4>
                      <div class="header-actions">
                        <el-input
                          v-model="vehicleFilter"
                          placeholder="搜索车牌号/车型"
                          clearable
                          style="width: 200px; margin-right: 10px;"
                        >
                          <template #prefix>
                            <el-icon><Search /></el-icon>
                          </template>
                        </el-input>
                        <el-button :loading="loadingVehicles" @click="fetchAvailableVehicles">
                          <el-icon><Refresh /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </template>

                  <el-table
                    :data="filteredVehicles"
                    v-loading="loadingVehicles"
                    border
                    height="400"
                    @row-click="handleVehicleRowClick"
                    row-class-name="clickable-row"
                  >
                    <el-table-column prop="license_plate" label="车牌号" width="140" />
                    <el-table-column prop="vehicle_type" label="车型" width="120" />
                    <el-table-column prop="vehicle_category" label="分类" width="100" />
                    <el-table-column prop="standard_volume" label="容积(m³)" width="120">
                      <template #default="scope">{{ scope.row.standard_volume ?? '-' }}</template>
                    </el-table-column>
                    <el-table-column prop="original_capacity" label="载重(吨)" width="120">
                      <template #default="scope">{{ scope.row.original_capacity ?? '-' }}</template>
                    </el-table-column>
                    <el-table-column label="操作" width="80" fixed="right">
                      <template #default="scope">
                        <el-button
                          type="primary"
                          size="small"
                          @click.stop="addVehicle(scope.row)"
                          :disabled="isVehicleSelected(scope.row.id)"
                        >
                          <el-icon><Plus /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>

                  <div class="table-footer">
                    <span>共 {{ filteredVehicles.length }} 辆可用车辆</span>
                  </div>
                </el-card>
              </el-col>

              <!-- 右侧：选中车辆容器 -->
              <el-col :span="10">
                <el-card class="selected-vehicles-card" shadow="never">
                  <template #header>
                    <div class="card-header">
                      <h4>已选车辆</h4>
                      <el-tag type="primary">{{ selectedVehicles.length }} 辆</el-tag>
                    </div>
                  </template>

                  <div class="selected-vehicles-container">
                    <div v-if="selectedVehicles.length === 0" class="empty-state">
                      <el-empty description="暂未选择车辆" :image-size="80">
                        <template #image>
                          <el-icon size="60" color="#c0c4cc"><Van /></el-icon>
                        </template>
                      </el-empty>
                    </div>

                    <div v-else class="selected-vehicles-list">
                      <div
                        v-for="vehicle in selectedVehicles"
                        :key="vehicle.id"
                        class="selected-vehicle-item"
                      >
                        <div class="vehicle-info">
                          <div class="vehicle-main">
                            <span class="license-plate">{{ vehicle.license_plate }}</span>
                            <span class="vehicle-type">{{ vehicle.vehicle_type }}</span>
                          </div>
                          <div class="vehicle-details">
                            <span class="detail-item">
                              <el-icon><ScaleToOriginal /></el-icon>
                              {{ vehicle.standard_volume ?? '-' }}m³
                            </span>
                            <span class="detail-item">
                              <el-icon><Van /></el-icon>
                              {{ vehicle.original_capacity ?? '-' }}吨
                            </span>
                          </div>
                        </div>
                        <div class="vehicle-actions">
                          <el-button
                            type="danger"
                            size="small"
                            @click="removeVehicle(vehicle.id)"
                            circle
                          >
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="selection-actions" v-if="selectedVehicles.length > 0">
                    <el-button
                      size="small"
                      @click="clearVehicleSelection"
                    >
                      <el-icon><Close /></el-icon>
                      清空选择
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 车厢选择区域 -->
            <el-row :gutter="20" style="margin-top: 20px;">
              <!-- 左侧：车厢信息表格 -->
              <el-col :span="14">
                <el-card class="carriage-table-card" shadow="never">
                  <template #header>
                    <div class="card-header">
                      <h4>可用车厢列表</h4>
                      <div class="header-actions">
                        <el-input
                          v-model="carriageFilter"
                          placeholder="搜索车厢号/车型"
                          clearable
                          style="width: 200px; margin-right: 10px;"
                        >
                          <template #prefix>
                            <el-icon><Search /></el-icon>
                          </template>
                        </el-input>
                        <el-button :loading="loadingCarriages" @click="fetchAvailableCarriages">
                          <el-icon><Refresh /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </template>

                  <el-table
                    :data="filteredCarriages"
                    v-loading="loadingCarriages"
                    border
                    height="400"
                    @row-click="handleCarriageRowClick"
                    row-class-name="clickable-row"
                  >
                    <el-table-column prop="carriage_number" label="车厢号" width="140" />
                    <el-table-column prop="vehicle_type" label="车型" width="120" />
                    <el-table-column prop="vehicle_category" label="分类" width="100" />
                    <el-table-column prop="standard_volume" label="容积(m³)" width="120">
                      <template #default="scope">{{ scope.row.standard_volume ?? '-' }}</template>
                    </el-table-column>
                    <el-table-column prop="original_capacity" label="载重(吨)" width="120">
                      <template #default="scope">{{ scope.row.original_capacity ?? '-' }}</template>
                    </el-table-column>
                    <el-table-column label="操作" width="80" fixed="right">
                      <template #default="scope">
                        <el-button
                          type="primary"
                          size="small"
                          @click.stop="addCarriage(scope.row)"
                          :disabled="isCarriageSelected(scope.row.id)"
                        >
                          <el-icon><Plus /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>

                  <div class="table-footer">
                    <span>共 {{ filteredCarriages.length }} 个可用车厢</span>
                  </div>
                </el-card>
              </el-col>

              <!-- 右侧：选中车厢容器 -->
              <el-col :span="10">
                <el-card class="selected-carriages-card" shadow="never">
                  <template #header>
                    <div class="card-header">
                      <h4>已选车厢</h4>
                      <el-tag type="success">{{ selectedCarriages.length }} 个</el-tag>
                    </div>
                  </template>

                  <div class="selected-carriages-container">
                    <div v-if="selectedCarriages.length === 0" class="empty-state">
                      <el-empty description="暂未选择车厢" :image-size="80">
                        <template #image>
                          <el-icon size="60" color="#c0c4cc"><Box /></el-icon>
                        </template>
                      </el-empty>
                    </div>

                    <div v-else class="selected-carriages-list">
                      <div
                        v-for="carriage in selectedCarriages"
                        :key="carriage.id"
                        class="selected-carriage-item"
                      >
                        <div class="carriage-info">
                          <div class="carriage-main">
                            <span class="carriage-number">{{ carriage.carriage_number }}</span>
                            <span class="carriage-type">{{ carriage.vehicle_type }}</span>
                          </div>
                          <div class="carriage-details">
                            <span class="detail-item">
                              <el-icon><ScaleToOriginal /></el-icon>
                              {{ carriage.standard_volume ?? '-' }}m³
                            </span>
                            <span class="detail-item">
                              <el-icon><Box /></el-icon>
                              {{ carriage.original_capacity ?? '-' }}吨
                            </span>
                          </div>
                        </div>
                        <div class="carriage-actions">
                          <el-button
                            type="danger"
                            size="small"
                            @click="removeCarriage(carriage.id)"
                            circle
                          >
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="selection-actions" v-if="selectedCarriages.length > 0">
                    <el-button
                      size="small"
                      @click="clearCarriageSelection"
                    >
                      <el-icon><Close /></el-icon>
                      清空选择
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
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
  Close,
  Search,
  Refresh,
  Box,
  ScaleToOriginal
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { dispatchService } from '@/services/dispatchService'
import { vehicleCapacityReferenceService } from '@/services/vehicleCapacityReferenceService'
import tonnageVolumeService from '@/services/tonnageVolumeService'

export default {
  name: 'SupplierResponseForm',
  components: {
    Van,
    Plus,
    Delete,
    Check,
    Close,
    Search,
    Refresh,
    Box,
    ScaleToOriginal,
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
    const tonnageVolumeData = ref(null) // 吨位容积数据

    // 格式化需求吨位显示
    const formattedRequiredWeight = computed(() => {
      if (!props.task.required_weight) return ''
      // 移除重复的"吨"字，如"40吨A吨"改为"40吨A"，"8吨吨"改为"8吨"
      return props.task.required_weight.replace(/吨.*吨$/, '吨')
    })

    // 获取吨位对应的容积区间
    const tonnageVolumeRange = computed(() => {
      console.log('计算吨位容积区间，数据:', tonnageVolumeData.value, '需求吨位:', props.task.required_weight)
      if (!tonnageVolumeData.value || !props.task.required_weight) {
        console.log('数据不足，返回空字符串')
        return ''
      }
      
      const data = tonnageVolumeData.value
      if (data.min_volume !== undefined && data.max_volume !== undefined) {
        if (data.max_volume === null) {
          return `${data.min_volume}m³以上`
        }
        return `${data.min_volume}-${data.max_volume}m³`
      }
      return ''
    })

    // 加载吨位容积数据
    const loadTonnageVolumeData = async () => {
      console.log('开始加载吨位容积数据，需求吨位:', props.task.required_weight)
      if (!props.task.required_weight) {
        console.log('需求吨位为空，跳过加载')
        return
      }
      
      try {
        const response = await tonnageVolumeService.getVolumeByTonnage(props.task.required_weight)
        console.log('获取吨位容积数据响应:', response)
        if (response && response.data) {
          tonnageVolumeData.value = response.data
          console.log('吨位容积数据已设置:', tonnageVolumeData.value)
        } else {
          console.log('响应中没有数据')
        }
      } catch (error) {
        console.error('获取吨位容积数据失败:', error)
      }
    }

     // 新增：可用车辆数据源
     const loadingVehicles = ref(false)
     const allVehicles = ref([])
     const vehicleFilter = ref('')
     const selectedVehicles = ref([])

     // 新增：可用车厢数据源
     const loadingCarriages = ref(false)
     const allCarriages = ref([])
     const carriageFilter = ref('')
     const selectedCarriages = ref([])

    // 权限检查（允许在开发/未下发权限时按角色放行）
    const hasResponsePermission = computed(() => {
      // 1) 具备任一权限码，直接放行
      const checkPerm = permissionStore.hasPermission
      const hasPerm = (code) => (typeof checkPerm === 'function' ? checkPerm(code) : (checkPerm?.(code) || false))
      const neededPerms = ['supplier:respond', 'team:assign', 'outsourcing:assign']
      if (neededPerms.some(p => hasPerm(p))) return true

      // 2) 角色兜底（从 permissionStore -> userStore 依次获取），不再因“已加载但缺少权限码”而直接拦截
      let derivedRole = ''
      const info = permissionStore.userInfo
      if (info && Array.isArray(info.roles) && info.roles.length > 0) {
        const first = info.roles[0]
        derivedRole = typeof first === 'string' ? first : (first?.name || '')
      } else if (Array.isArray(permissionStore.roles) && permissionStore.roles.length > 0) {
        // permissionStore 中已展开的角色名数组 ["供应商", ...]
        derivedRole = permissionStore.roles[0]
      } else if (userStore?.currentUser?.role_name) {
        // 兜底到 userStore（如存在）
        derivedRole = userStore.currentUser.role_name
      }

      const allowedRoles = ['供应商', '班组长', '大容积供应商', 'supplier', 'team_leader', 'large_capacity_supplier']
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
        { required: true, message: '请输入路单流水号', trigger: 'blur' }
      ],
      dispatch_number: [
        { required: true, message: '请输入派车单号', trigger: 'blur' }
      ],
      vehicles: [
        { 
          type: 'array', 
          required: true, 
          message: '请至少选择一辆车辆', 
          trigger: 'change',
          validator: (rule, value, callback) => {
            if (!value || value.length === 0) {
              callback(new Error('已选车辆不能为空'))
              return
            }
            
            // 唯一性验证：一个任务只能派遣一辆车或一个车厢
            const totalVehicles = selectedVehicles.value.length
            const totalCarriages = selectedCarriages.value.length
            
            if (totalVehicles + totalCarriages > 1) {
              callback(new Error('一个任务只能派遣一辆车或一个车厢，请重新选择'))
              return
            }
            
            if (totalVehicles === 0 && totalCarriages === 0) {
              callback(new Error('请至少选择一辆车辆或一个车厢'))
              return
            }
            
            // 如果选择了车厢，必须有车辆
            if (selectedCarriages.value.length > 0 && value.length === 0) {
              callback(new Error('选择车厢后，已选车辆不能为空'))
              return
            }
            
            callback()
          }
        }
      ],
      notes: [
        { max: 500, message: '备注不能超过500个字符', trigger: 'blur' }
      ]
    }

    // 新增：可用车辆过滤（只显示车牌号不为空的）
    const filteredVehicles = computed(() => {
      let vehicles = allVehicles.value.filter(v => v.license_plate && v.license_plate.trim() !== '')
      
      if (!vehicleFilter.value) return vehicles
      const keyword = vehicleFilter.value.toLowerCase()
      return vehicles.filter(v => (
        (v.license_plate || '').toLowerCase().includes(keyword) ||
        (v.vehicle_type || '').toLowerCase().includes(keyword)
      ))
    })

    // 新增：可用车厢过滤（只显示车厢号不为空的）
    const filteredCarriages = computed(() => {
      let carriages = allCarriages.value.filter(c => c.carriage_number && c.carriage_number.trim() !== '')
      
      if (!carriageFilter.value) return carriages
      const keyword = carriageFilter.value.toLowerCase()
      return carriages.filter(c => (
        (c.carriage_number || '').toLowerCase().includes(keyword) ||
        (c.vehicle_type || '').toLowerCase().includes(keyword)
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

          const totalVolume = (responseForm.vehicles || []).reduce((sum, v) => sum + (Number(v.standard_volume) || 0), 0)
          if (typeof props.task.required_volume === 'number' && totalVolume < props.task.required_volume) {
        ElMessage.warning(`车辆总容积(${totalVolume}m³)小于任务需求(${props.task.required_volume}m³)，请确认是否继续提交`)
          }

          // 优先根据权限码确定提交通道；若权限未初始化则根据角色名称兜底
          const checkPerm = permissionStore.hasPermission
          const hasPerm = (code) => (typeof checkPerm === 'function' ? checkPerm(code) : (checkPerm?.(code) || false))

          // 从权限或角色推导提交类型：supplier/team/outsourcing
          const resolveSubmitType = () => {
            // 1) 权限优先
            if (hasPerm('supplier:respond')) return 'supplier'
            if (hasPerm('team:assign')) return 'team'
            if (hasPerm('outsourcing:assign')) return 'outsourcing'

            // 2) 若权限不足，则基于角色兜底（兼容字符串或对象 roles）
            let roleName = ''
            const info = permissionStore.userInfo
            if (info && Array.isArray(info.roles) && info.roles.length > 0) {
              const first = info.roles[0]
              roleName = typeof first === 'string' ? first : (first?.name || '')
            } else if (Array.isArray(permissionStore.roles) && permissionStore.roles.length > 0) {
              roleName = permissionStore.roles[0]
            } else if (userStore?.currentUser?.role_name) {
              roleName = userStore.currentUser.role_name
            }

            // 兼容英文 key 与中文名称，以及"大容积供应商/外包驾驶管理公司"展示名
            if (['供应商', 'supplier'].includes(roleName)) return 'supplier'
            if (['班组长', 'team_leader'].includes(roleName)) return 'team'
            if (['大容积供应商', 'large_capacity_supplier'].includes(roleName)) return 'outsourcing'

            // 3) 再次兜底：根据任务状态推断（防止因角色字符串差异而阻塞）
            const status = props.task?.status
            if (status === 'awaiting_supplier_response' || status === 'approved') return 'supplier'
            if (status === 'awaiting_team_assignment') {
              // 若角色疑似大容积/外包，则走 outsourcing，否则默认走 team
              if (['大容积供应商', 'large_capacity_supplier'].includes(roleName)) return 'outsourcing'
              return 'team'
            }

            return ''
          }

          const submitType = resolveSubmitType()

          const requestData = {
            task_id: responseForm.task_id,
            manifest_number: responseForm.manifest_number,
            dispatch_number: responseForm.dispatch_number,
            vehicles: responseForm.vehicles,
            notes: responseForm.notes
          }

          let result
          if (submitType === 'supplier') {
            result = await dispatchService.submitSupplierResponse(requestData)
          } else if (submitType === 'team') {
            result = await dispatchService.submitTeamResponse(requestData)
          } else if (submitType === 'outsourcing') {
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

    // 处理车辆表格行点击
    const handleVehicleRowClick = (row) => {
      if (!isVehicleSelected(row.id)) {
        addVehicle(row)
      }
    }

    // 处理车厢表格行点击
    const handleCarriageRowClick = (row) => {
      if (!isCarriageSelected(row.id)) {
        addCarriage(row)
      }
    }

    // 添加车辆到选中列表
    const addVehicle = (vehicle) => {
      // 检查是否已选择车辆或车厢
      if (selectedVehicles.value.length > 0) {
        ElMessage.warning('一个任务只能派遣一辆车或一个车厢，请先移除已选车辆')
        return
      }
      
      if (selectedCarriages.value.length > 0) {
        ElMessage.warning('一个任务只能派遣一辆车或一个车厢，请先移除已选车厢')
        return
      }
      
      selectedVehicles.value.push({ ...vehicle })
      mapSelectedToPayload()
      
      // 检查容积是否在范围内
      checkVolumeRange(vehicle.standard_volume)
      
      ElMessage.success(`已添加车辆：${vehicle.license_plate}`)
    }

    // 从选中列表移除车辆
    const removeVehicle = (vehicleId) => {
      const index = selectedVehicles.value.findIndex(v => v.id === vehicleId)
      if (index > -1) {
        const vehicle = selectedVehicles.value[index]
        selectedVehicles.value.splice(index, 1)
        mapSelectedToPayload()
        ElMessage.success(`已移除车辆：${vehicle.license_plate}`)
      }
    }

    // 检查车辆是否已被选择
    const isVehicleSelected = (vehicleId) => {
      return selectedVehicles.value.some(v => v.id === vehicleId)
    }

    // 添加车厢到选中列表
    const addCarriage = (carriage) => {
      // 检查是否已选择车辆或车厢
      if (selectedCarriages.value.length > 0) {
        ElMessage.warning('一个任务只能派遣一个车厢，请先移除已选车厢')
        return
      }
      
      if (selectedVehicles.value.length > 0) {
        ElMessage.warning('一个任务只能派遣一辆车或一个车厢，请先移除已选车辆')
        return
      }
      
      selectedCarriages.value.push({ ...carriage })
      mapSelectedToPayload()
      
      // 检查容积是否在范围内
      checkVolumeRange(carriage.standard_volume)
      
      ElMessage.success(`已添加车厢：${carriage.carriage_number}`)
    }

    // 从选中列表移除车厢
    const removeCarriage = (carriageId) => {
      const index = selectedCarriages.value.findIndex(c => c.id === carriageId)
      if (index > -1) {
        const carriage = selectedCarriages.value[index]
        selectedCarriages.value.splice(index, 1)
        mapSelectedToPayload()
        ElMessage.success(`已移除车厢：${carriage.carriage_number}`)
      }
    }

    // 检查车厢是否已被选择
    const isCarriageSelected = (carriageId) => {
      return selectedCarriages.value.some(c => c.id === carriageId)
    }

    // 清空车辆选择
    const clearVehicleSelection = async () => {
      if (selectedVehicles.value.length === 0) return
      
      try {
        await ElMessageBox.confirm(
          '确认清空所有已选择的车辆吗？',
          '确认清空',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        selectedVehicles.value = []
        mapSelectedToPayload()
        ElMessage.success('已清空车辆选择')
      } catch {
        // 用户取消操作
      }
    }

    // 清空车厢选择
    const clearCarriageSelection = async () => {
      if (selectedCarriages.value.length === 0) return
      
      try {
        await ElMessageBox.confirm(
          '确认清空所有已选择的车厢吗？',
          '确认清空',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        selectedCarriages.value = []
        mapSelectedToPayload()
        ElMessage.success('已清空车厢选择')
      } catch {
        // 用户取消操作
      }
    }

    // 将选择映射为提交 payload 所需字段（更新以包含车厢）
    const mapSelectedToPayload = () => {
      responseForm.vehicles = (selectedVehicles.value || []).map(v => ({
        license_plate: v.license_plate,
        carriage_number: v.carriage_number || '',
        vehicle_type: v.vehicle_type,
        vehicle_category: v.vehicle_category,
        standard_volume: v.standard_volume,
        original_capacity: v.original_capacity,
        suppliers: v.suppliers
      }))

      // 如果有选择车厢，也添加到vehicles数组中（或者根据API需求调整）
      responseForm.carriages = (selectedCarriages.value || []).map(c => ({
        carriage_number: c.carriage_number,
        vehicle_type: c.vehicle_type,
        vehicle_category: c.vehicle_category,
        standard_volume: c.standard_volume,
        original_capacity: c.original_capacity,
        suppliers: c.suppliers
      }))
    }

    // 检查容积是否在需求范围内
    const checkVolumeRange = (volume) => {
      if (!volume || !props.task.required_volume || !tonnageVolumeData.value) return
      
      const selectedVolume = parseFloat(volume)
      
      // 获取吨位对应的容积区间
      const data = tonnageVolumeData.value
      const minVolume = data.min_volume !== undefined ? parseFloat(data.min_volume) : null
      const maxVolume = data.max_volume !== undefined ? parseFloat(data.max_volume) : null
      
      console.log('容积检查:', { selectedVolume, minVolume, maxVolume })
      
      // 检查是否在吨位对应的容积区间内
      let inRange = true
      let rangeDescription = ''
      
      if (minVolume !== null && maxVolume !== null) {
        // 区间范围检查（有最小值和最大值）
        inRange = selectedVolume >= minVolume && selectedVolume <= maxVolume
        rangeDescription = `${minVolume}-${maxVolume}m³`
      } else if (minVolume !== null && maxVolume === null) {
        // 最小值以上范围检查（只有最小值，无最大值）
        inRange = selectedVolume >= minVolume
        rangeDescription = `${minVolume}m³以上`
      } else if (minVolume === null && maxVolume !== null) {
        // 最大值以下范围检查（只有最大值，无最小值）
        inRange = selectedVolume <= maxVolume
        rangeDescription = `≤${maxVolume}m³`
      } else {
        // 无区间限制
        inRange = true
        rangeDescription = '无限制'
      }
      
      // 只有当容积超出吨位区间时才提示
      if (!inRange) {
        ElMessageBox.confirm(
          `该车容积(${selectedVolume}m³)不在吨位${props.task.required_weight}对应的容积区间${rangeDescription}内，是否派车？`,
          '容积范围提示',
          {
            confirmButtonText: '继续派车',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).catch(() => {
          // 用户取消，移除选择
          if (selectedVehicles.value.length > 0) {
            selectedVehicles.value = []
          }
          if (selectedCarriages.value.length > 0) {
            selectedCarriages.value = []
          }
          mapSelectedToPayload()
        })
      }
    }

    // 获取可用车辆（使用VehicleCapacityReference接口）
    const fetchAvailableVehicles = async () => {
      loadingVehicles.value = true
      try {
        if (!hasResponsePermission.value) {
          // 无权限时不发起请求，直接退出
          allVehicles.value = []
          return
        }
        const result = await vehicleCapacityReferenceService.getAvailableVehicles()
        allVehicles.value = result.data || []
      } catch (e) {
        console.error('获取可用车辆失败:', e)
        ElMessage.error('获取可用车辆失败')
      } finally {
        loadingVehicles.value = false
      }
    }

    // 获取可用车厢（使用VehicleCapacityReference接口）
    const fetchAvailableCarriages = async () => {
      loadingCarriages.value = true
      try {
        if (!hasResponsePermission.value) {
          // 无权限时不发起请求，直接退出
          allCarriages.value = []
          return
        }
        const result = await vehicleCapacityReferenceService.getAvailableCarriages()
        allCarriages.value = result.data || []
      } catch (e) {
        console.error('获取可用车厢失败:', e)
        ElMessage.error('获取可用车厢失败')
      } finally {
        loadingCarriages.value = false
      }
    }

    onMounted(async () => {
      console.log('SupplierResponseForm组件挂载，任务数据:', props.task)
      responseForm.task_id = props.task.task_id
      if (!hasResponsePermission.value) {
        console.log('没有响应权限，跳过数据加载')
        return
      }
      console.log('开始加载数据...')
      await Promise.all([
        fetchAvailableVehicles(),
        fetchAvailableCarriages(),
        loadTonnageVolumeData() // 加载吨位容积数据
      ])
      console.log('数据加载完成')
    })

    return {
      responseFormRef,
      submitting,
      hasResponsePermission,
      responseForm,
      responseRules,
      getStatusType,
      getStatusText,
      // 车辆相关
      loadingVehicles,
      allVehicles,
      vehicleFilter,
      filteredVehicles,
      selectedVehicles,
      handleVehicleRowClick,
      addVehicle,
      removeVehicle,
      isVehicleSelected,
      clearVehicleSelection,
      fetchAvailableVehicles,
      // 车厢相关
      loadingCarriages,
      allCarriages,
      carriageFilter,
      filteredCarriages,
      selectedCarriages,
      handleCarriageRowClick,
      addCarriage,
      removeCarriage,
      isCarriageSelected,
      clearCarriageSelection,
      fetchAvailableCarriages,
      // 通用方法
      mapSelectedToPayload,
      // 提交/取消
      submitResponse,
      cancel,
      // 吨位容积相关
      tonnageVolumeRange,
      formattedRequiredWeight
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

/* 车辆选择容器样式 */
.vehicle-selection-container {
  margin: 20px 0;
}

.vehicle-table-card,
.selected-vehicles-card {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.vehicle-table-card :deep(.el-card__body),
.selected-vehicles-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
}

.table-footer {
  margin-top: 12px;
  text-align: right;
  color: #909399;
  font-size: 14px;
}

/* 选中车辆容器样式 */
.selected-vehicles-container,
.selected-carriages-container {
  flex: 1;
  min-height: 0;
  margin-bottom: 16px;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selected-vehicles-list,
.selected-carriages-list {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.selected-vehicle-item,
.selected-carriage-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
  transition: all 0.3s;
}

.selected-vehicle-item:hover,
.selected-carriage-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.vehicle-info,
.carriage-info {
  flex: 1;
}

.vehicle-main,
.carriage-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.license-plate,
.carriage-number {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.vehicle-type,
.carriage-type {
  background: #e1f3d8;
  color: #67c23a;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.vehicle-details,
.carriage-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #606266;
  font-size: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.vehicle-actions,
.carriage-actions {
  margin-left: 12px;
}

.selection-actions {
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
  text-align: center;
}

/* 表格行点击样式 */
:deep(.clickable-row) {
  cursor: pointer;
}

:deep(.clickable-row:hover) {
  background-color: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .vehicle-selection-container :deep(.el-row) {
    flex-direction: column;
  }
  
  .vehicle-selection-container :deep(.el-col) {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .vehicle-table-card,
  .selected-vehicles-card {
    height: auto;
    min-height: 300px;
  }
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .header-actions .el-input {
    width: 100% !important;
    margin-right: 0 !important;
  }
  
  .vehicle-details {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>