<template>
  <div class="task-detail-container">
    <!-- 当前操作状态提示栏 -->
    <div class="status-alert" :class="getStatusAlertClass(task.status)">
      <div class="alert-content">
        <el-icon class="alert-icon"><Warning /></el-icon>
        <div class="alert-text">
          <div class="current-status">当前状态：{{ getStatusText(task.status) }}</div>
          <div class="next-action">{{ getNextActionHint(task.status, currentUserRole) }}</div>
        </div>
      </div>
    </div>

    <!-- 任务概览卡片 -->
    <div class="overview-card">
      <div class="overview-header">
        <div class="task-title">
          <h2>{{ task.mail_route_name }}</h2>
          <el-tag :type="getStatusType(task.status)" size="large" class="status-tag">
            {{ getStatusText(task.status) }}
          </el-tag>
        </div>
        <div class="task-id">任务编号: {{ task.task_id }}</div>
      </div>
      
      <div class="overview-stats">
        <div class="stat-item">
          <div class="stat-label">需求日期</div>
          <div class="stat-value">{{ task.required_date }}</div>
          <div class="stat-time" v-if="task.required_time">{{ task.required_time }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">发起时间</div>
          <div class="stat-value">{{ formatDateTime(task.created_at || task.created_time) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">运输类型</div>
          <div class="stat-value">{{ task.transport_type }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">需求吨位</div>
          <div class="stat-value">{{ formattedRequiredWeight }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">需求容积</div>
          <div class="stat-value">{{ task.required_volume }} m³</div>
          <div class="stat-time" v-if="tonnageVolumeRange">容积区间: {{ tonnageVolumeRange }}</div>
        </div>
      </div>

      <!-- 角色差异化操作按钮 -->
      <div class="action-buttons" v-if="hasAvailableActions">
        <el-button 
          v-for="action in availableActions" 
          :key="action.key"
          :type="action.type" 
          :icon="action.icon"
          size="large"
          @click="handleAction(action.key)"
          :loading="loadingActions[action.key]"
        >
          {{ action.label }}
        </el-button>
      </div>

    <!-- 供应商响应表单对话框 -->
    <el-dialog
      v-model="supplierResponseDialogVisible"
      :title="getResponseDialogTitle()"
      width="80%"
      top="5vh"
      :close-on-click-modal="false"
      @close="handleSupplierResponseClose"
    >
      <supplier-response-form
        v-if="supplierResponseDialogVisible"
        :task="task"
        @response-success="handleResponseSuccess"
        @cancel="handleSupplierResponseClose"
      />
    </el-dialog>
    </div>

    <!-- 详细信息网格 -->
    <div class="detail-grid">
      <!-- 基本信息 -->
      <div class="detail-card">
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>基本信息</span>
        </div>
        <div class="card-content">
          <div class="info-row">
            <label>始发局:</label>
            <span>{{ task.origin_bureau }}</span>
          </div>
          <div class="info-row">
            <label>组织单位:</label>
            <span>{{ task.organizing_unit }}</span>
          </div>
          <div class="info-row">
            <label>需求类型:</label>
            <span>{{ task.requirement_type }}</span>
          </div>
          <div class="info-row">
            <label>派车轨道:</label>
            <span>{{ task.dispatch_track }}</span>
          </div>
          <div class="info-row">
            <label>实际容积:</label>
            <span>{{ task.required_volume }} m³</span>
            <span v-if="tonnageVolumeRange"> (容积区间: {{ tonnageVolumeRange }})</span>
          </div>
        </div>
      </div>

      <!-- 发起人信息 -->
      <div class="detail-card">
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>发起人信息</span>
        </div>
        <div class="card-content">
          <div class="info-row">
            <label>发起人角色:</label>
            <span>{{ task.initiator_role }}</span>
          </div>
          <div class="info-row">
            <label>发起人部门:</label>
            <span>{{ task.initiator_department }}</span>
          </div>
        </div>
      </div>

      <!-- 特殊要求 -->
      <div class="detail-card full-width" v-if="task.special_requirements">
        <div class="card-header">
          <el-icon><Warning /></el-icon>
          <span>特殊要求</span>
        </div>
        <div class="card-content">
          <div class="special-requirements">
            {{ task.special_requirements }}
          </div>
        </div>
      </div>
    </div>

    <!-- 分配车辆信息 -->
    <template v-if="task.vehicles && task.vehicles.length > 0">
      <div class="section-header">
        <el-icon><Van /></el-icon>
        <span>分配车辆信息</span>
        <div class="vehicle-count">共 {{ task.vehicles.length }} 辆</div>
      </div>
      
      <div class="vehicle-grid">
        <div class="vehicle-card" v-for="vehicle in task.vehicles" :key="vehicle.vehicle_id">
          <div class="vehicle-header">
            <div class="vehicle-plate">{{ vehicle.plate_number }}</div>
            <el-tag size="small" type="success">{{ vehicle.vehicle_type }}</el-tag>
          </div>
          <div class="vehicle-info">
            <div class="info-item">
              <el-icon><UserFilled /></el-icon>
              <span>{{ vehicle.driver_name }}</span>
            </div>
            <div class="info-item">
              <el-icon><Phone /></el-icon>
              <span>{{ vehicle.driver_phone }}</span>
            </div>
            <div class="info-item">
              <el-icon><Box /></el-icon>
              <span>载重: {{ vehicle.capacity }} 吨</span>
            </div>
            <div class="info-item">
              <el-icon><Box /></el-icon>
              <span>容积: {{ vehicle.volume }} m³</span>
            </div>
          </div>
          <div class="vehicle-notes" v-if="vehicle.notes">
            <el-icon><ChatDotRound /></el-icon>
            <span>{{ vehicle.notes }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 状态历史 -->
    <template v-if="task.status_history && task.status_history.length > 0">
      <div class="section-header">
        <el-icon><Clock /></el-icon>
        <span>状态历史</span>
      </div>
      
      <div class="timeline-container">
        <el-timeline>
          <el-timeline-item
            v-for="(history, index) in task.status_history"
            :key="index"
            :timestamp="formatDateTime(history.timestamp)"
            :type="getTimelineItemType(history.status)"
            :hollow="index !== 0"
            size="large"
          >
            <div class="timeline-content">
              <div class="timeline-title">{{ history.status }}</div>
              <div class="timeline-info">
                <div class="operator">操作人: {{ userFullNames[normalizeUserId(history.operator)] || normalizeUserId(history.operator) }}</div>
                <div class="comment" v-if="history.comment">{{ history.comment }}</div>
                <!-- 增强功能：显示下一阶段操作人信息 -->
                <div class="next-operator" v-if="history.next_handler_role">
                  下一阶段操作人角色: {{ history.next_handler_role }}
                </div>
                <div class="next-operator" v-else-if="getNextHandlerRole(history.status)">
                  下一阶段操作人角色: {{ getNextHandlerRole(history.status) }}
                </div>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </template>

    <!-- 操作确认对话框 -->
    <el-dialog
      v-model="actionDialogVisible"
      :title="currentAction?.label"
      width="500px"
    >
      <el-form :model="actionForm" label-width="80px">
        <el-form-item label="备注">
          <el-input
            v-model="actionForm.comment"
            type="textarea"
            :rows="3"
            placeholder="请输入操作备注..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAction" :loading="submitting">
          确认{{ currentAction?.label }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 车间地调核实核实操作对话框 -->
    <el-dialog
      v-model="workshopVerificationDialogVisible"
      title="车间地调核实操作"
      width="600px"
    >
      <el-form :model="workshopVerificationForm" label-width="100px">
        <el-form-item label="操作类型" required>
          <el-radio-group v-model="workshopVerificationForm.action">
            <el-radio label="verify_pass">核实通过</el-radio>
            <el-radio label="downgrade">降档处理</el-radio>
            <el-radio label="merge">合并任务</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 降档处理时显示 -->
        <el-form-item 
          v-if="workshopVerificationForm.action === 'downgrade'" 
          label="降档吨位" 
          required
        >
          <el-input
            v-model="workshopVerificationForm.downgradeTonnage"
            placeholder="请输入降档后的吨位，如：8吨"
          />
        </el-form-item>
        
        <!-- 合并任务时显示 -->
        <el-form-item 
          v-if="workshopVerificationForm.action === 'merge'" 
          label="合并到任务" 
          required
        >
          <el-input
            v-model="workshopVerificationForm.mergeTaskId"
            placeholder="请输入要合并到的任务ID"
          />
        </el-form-item>
        
        <el-form-item label="操作备注">
          <el-input
            v-model="workshopVerificationForm.comment"
            type="textarea"
            :rows="3"
            placeholder="请输入操作备注..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workshopVerificationDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmWorkshopVerification" 
          :loading="submitting"
          :disabled="!workshopVerificationForm.action"
        >
          确认操作
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, User, Warning, Van, UserFilled, Phone, Box, Clock, 
  ChatDotRound, Check, Close, Position, Select, CircleCheck, Promotion
} from '@element-plus/icons-vue'
import { usePermissionStore } from '@/stores/permission'
import { apiService } from '@/services/api'
import SupplierResponseForm from './SupplierResponseForm.vue'
import { useUserStore } from '@/stores/user'
import tonnageVolumeService from '@/services/tonnageVolumeService'

export default {
  name: 'TaskDetail',
  components: {
    Document,
    User,
    Warning,
    Van,
    UserFilled,
    Phone,
    Box,
    Clock,
    ChatDotRound,
    SupplierResponseForm
  },
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  setup(props, { emit }) {
    const permissionStore = usePermissionStore()
    const userStore = useUserStore()
    const actionDialogVisible = ref(false)
    const supplierResponseDialogVisible = ref(false)
    const workshopVerificationDialogVisible = ref(false) // 车间地调核实操作对话框
    const currentAction = ref(null)
    const submitting = ref(false)
    const loadingActions = reactive({})
    const userFullNames = reactive({}) // 用于存储用户ID到姓名的映射
    const tonnageVolumeData = ref(null) // 吨位容积数据

    // 车间地调核实操作表单
    const workshopVerificationForm = reactive({
      action: '', // 'verify_pass', 'downgrade', 'merge'
      comment: '',
      mergeTaskId: '', // 合并时的目标任务ID
      downgradeTonnage: '' // 降档时的新吨位
    })

    // 格式化需求吨位显示
    const formattedRequiredWeight = computed(() => {
      if (!props.task.required_weight) return ''
      // 移除重复的"吨"字，如"40吨A吨"改为"40吨A"，"8吨吨"改为"8吨"
      return props.task.required_weight.replace(/吨.*吨$/, '吨')
    })

    // 获取吨位对应的容积区间
    const tonnageVolumeRange = computed(() => {
      if (!tonnageVolumeData.value || !props.task.required_weight) return ''
      
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
      if (!props.task.required_weight) return
      
      try {
        const response = await tonnageVolumeService.getVolumeByTonnage(props.task.required_weight)
        if (response && response.data) {
          tonnageVolumeData.value = response.data
        }
      } catch (error) {
        console.error('获取吨位容积数据失败:', error)
      }
    }

    // 规范化提取用户ID：从任意字符串中提取第一个数字序列
    const normalizeUserId = (raw) => {
      if (raw === null || raw === undefined) return ''
      const s = String(raw)
      const m = s.match(/\d+/)
      // 如果找不到数字，返回原始字符串而不是空字符串
      return m ? m[0] : s
    }

    // 获取用户完整姓名（兼容写法）
    const fetchUserFullName = async (rawId) => {
      if (rawId === null || rawId === undefined) return ''
      const userId = normalizeUserId(rawId)
      const rawKey = String(rawId)
      // 如果没有提取到有效的用户ID（即返回的是原始字符串而不是数字），直接返回原始值
      if (userId === rawKey) return rawKey
      // 命中缓存（用规范化后的ID）
      if (userFullNames[userId] !== undefined) return userFullNames[userId]

      try {
        const resp = await apiService.users.getUser(userId)
        const data = resp.data
         const fullName = data?.full_name || data?.name || data?.username || userId
         // 双写缓存：既按标准ID存，也按原始字符串存，保证模板索引稳定
         userFullNames[userId] = fullName
         userFullNames[rawKey] = fullName
         return fullName
      } catch {
        // 兜底：至少把原始值写入原始键，避免多次请求
        userFullNames[rawKey] = rawKey
        return rawKey
      }
    }
  
    const actionForm = reactive({
      comment: ''
    })
  
    // 获取当前用户角色
    const currentUserRole = computed(() => {
      const userInfo = permissionStore.userInfo
      if (userInfo && userInfo.roles && userInfo.roles.length > 0) {
        const firstRole = userInfo.roles[0]
        if (typeof firstRole === 'string') {
          return firstRole
        } else if (firstRole && firstRole.name) {
          return firstRole.name
        }
      }
      if (permissionStore.roles && permissionStore.roles.length > 0) {
        return permissionStore.roles[0]
      }
      // 从userStore兜底读取角色（role_name）
      if (userStore?.currentUser?.role_name) {
        return userStore.currentUser.role_name
      }
      return 'regional_dispatcher'
    })

    // 状态标准化（兼容中文/英文状态）
    const normalizeStatus = (status) => {
      if (!status) return ''
      const map = {
        '待响应': 'awaiting_supplier_response',
        '待供应商响应': 'awaiting_supplier_response',
        '待班组派车': 'awaiting_team_assignment',
        '已审批': 'approved',
        '已拒绝': 'rejected',
        '已完成': 'completed',
        '进行中': 'in_progress',
        '已分配': 'assigned',
        '已确认': 'confirmed',
        '最终确认': 'final_confirmed',
        '已发车': 'departed'
      }
      return map[status] || status
    }

    // 角色-动作映射
    const roleActionMap = {
      '区域调度员': {
        '待审核': ['approve', 'reject'],
        '审核拒绝': ['approve', 'reject']
      },
      '超级管理员': {
        '待审核': ['approve', 'reject'],
        '审核拒绝': ['approve', 'reject']
      },
      '供应商': {
        '待响应': ['respond'],
        '已响应': ['confirm'],
        '核实通过': ['confirm'],
        '已降档': ['respond'],
        '已合并': ['respond']
      },
      '班组长': {
        '待响应': ['respond'],
        '已响应': ['confirm'],
        '核实通过': ['confirm'],
        '已降档': ['respond'],
        '已合并': ['respond']
      },
      '大容积供应商': {
        '待响应': ['respond'],
        '已响应': ['confirm'],
        '核实通过': ['confirm'],
        '已降档': ['respond'],
        '已合并': ['respond']
      },
      '车间地调': {
        '已响应': ['workshop_verify'],
        'supplier_responded': ['workshop_verify'],
        'team_assigned': ['workshop_verify']
      }
    }

    // 动作定义
    const actionDefinitions = {
      approve: { label: '审核通过', type: 'primary', icon: 'Check' },
      reject: { label: '审核拒绝', type: 'danger', icon: 'Close' },
      respond: { label: '响应任务', type: 'success', icon: 'Message' },
      confirm: { label: '确认发车', type: 'warning', icon: 'CircleCheck' },
      workshop_verify: { label: '核实操作', type: 'primary', icon: 'View' }
    }

    // 可用操作按钮
    const availableActions = computed(() => {
      if (!props.task || !currentUserRole.value) return []
      
      const userRole = currentUserRole.value
      const taskStatus = props.task.status
      
      // 获取当前角色在当前状态下可执行的动作
      const roleActions = roleActionMap[userRole]
      if (!roleActions) return []
      
      const availableActionKeys = roleActions[taskStatus] || []
      
      // 将动作键转换为完整的动作对象
      return availableActionKeys.map(actionKey => ({
        key: actionKey,
        ...actionDefinitions[actionKey]
      })).filter(action => action.label) // 过滤掉未定义的动作
    })

    const hasAvailableActions = computed(() => availableActions.value.length > 0)

    // 状态提示样式
    const getStatusAlertClass = (status) => {
      const s = normalizeStatus(status)
      const classMap = {
        pending: 'status-pending',
        approved: 'status-approved',
        rejected: 'status-rejected',
        awaiting_supplier_response: 'status-awaiting',
        awaiting_team_assignment: 'status-awaiting',
        supplier_responded: 'status-responded',
        team_assigned: 'status-assigned',
        assigned: 'status-assigned',
        confirmed: 'status-confirmed',
        final_confirmed: 'status-final-confirmed',
        departed: 'status-departed',
        completed: 'status-completed',
        cancelled: 'status-cancelled',
        in_progress: 'status-in-progress'
      }
      return classMap[s] || 'status-info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const s = normalizeStatus(status)
      const statusTextMap = {
        pending: '待审核',
        approved: '已审批',
        rejected: '已拒绝',
        awaiting_supplier_response: '待供应商响应',
        awaiting_team_assignment: '待班组派车',
        supplier_responded: '供应商已响应',
        team_assigned: '班组已派车',
        assigned: '已分配',
        confirmed: '已确认',
        final_confirmed: '最终确认',
        departed: '已发车',
        completed: '已完成',
        cancelled: '已取消',
        in_progress: '进行中'
      }
      return statusTextMap[s] || status
    }

    // 获取下一步操作提示
    const getNextActionHint = (status, role) => {
      const s = normalizeStatus(status)
      const hintMap = {
        pending: {
          '超级管理员': '请审核此任务',
          '区域调度员': '请审核此任务',
          '车间地调': '等待超级管理员或区域调度员审核',
          '供应商': '等待审核',
          '班组长': '等待审核',
          '大容积供应商': '等待审核',
          regional_dispatcher: '请审核此任务',
          supplier: '等待区域调度员审核',
          team_leader: '等待区域调度员审核',
          outsourcing_manager: '等待区域调度员审核',
          workshop_dispatcher: '等待区域调度员审核'
        },
        awaiting_supplier_response: {
          '超级管理员': '等待供应商响应',
          '区域调度员': '等待供应商响应',
          '车间地调': '等待供应商响应',
          '供应商': '请响应此委办任务',
          '班组长': '等待供应商响应',
          '大容积供应商': '等待供应商响应',
          regional_dispatcher: '等待供应商响应',
          supplier: '请响应此任务',
          team_leader: '等待供应商响应',
          outsourcing_manager: '等待供应商响应',
          workshop_dispatcher: '等待供应商响应'
        },
        awaiting_team_assignment: {
          '超级管理员': '等待班组或大容积供应商派车',
          '区域调度员': '等待班组或大容积供应商派车',
          '车间地调': '等待班组或大容积供应商派车',
          '供应商': '等待班组或大容积供应商派车',
          '班组长': '请派遣自办车辆',
          '大容积供应商': '请派遣大容积车辆',
          regional_dispatcher: '等待班组派车',
          supplier: '等待班组派车',
          team_leader: '请派遣车辆',
          outsourcing_manager: '请派遣车辆',
          workshop_dispatcher: '等待班组派车'
        },
        supplier_responded: {
          '超级管理员': '供应商已响应，等待进一步处理',
          '区域调度员': '供应商已响应，等待进一步处理',
          '车间地调': '供应商已响应，等待进一步处理',
          '供应商': '已响应任务',
          '班组长': '供应商已响应',
          '大容积供应商': '供应商已响应'
        },
        team_assigned: {
          '超级管理员': '班组已派车，等待进一步处理',
          '区域调度员': '班组已派车，等待进一步处理',
          '车间地调': '班组已派车，等待进一步处理',
          '供应商': '班组已派车',
          '班组长': '已派遣车辆',
          '大容积供应商': '班组已派车'
        },
        approved: {
          regional_dispatcher: '任务已审批，等待响应',
          supplier: '请响应此任务',
          team_leader: '等待响应',
          outsourcing_manager: '等待响应',
          workshop_dispatcher: '等待响应'
        },
        assigned: {
          regional_dispatcher: '任务已分配，等待确认',
          supplier: '任务已分配，等待确认',
          team_leader: '请确认此任务',
          outsourcing_manager: '等待确认',
          workshop_dispatcher: '等待确认'
        },
        confirmed: {
          regional_dispatcher: '任务已确认，等待最终确认',
          supplier: '任务已确认，等待最终确认',
          team_leader: '任务已确认，等待最终确认',
          outsourcing_manager: '请进行最终确认',
          workshop_dispatcher: '等待最终确认'
        },
        final_confirmed: {
          '超级管理员': '任务已最终确认，等待发车',
          '区域调度员': '任务已最终确认，等待发车',
          '车间地调': '请确认发车',
          '供应商': '任务已最终确认，等待发车',
          '班组长': '任务已最终确认，等待发车',
          '外包管理公司': '任务已最终确认，等待发车',
          regional_dispatcher: '任务已最终确认，等待发车',
          supplier: '任务已最终确认，等待发车',
          team_leader: '任务已最终确认，等待发车',
          outsourcing_manager: '任务已最终确认，等待发车',
          workshop_dispatcher: '请确认发车'
        },
        in_progress: '任务进行中',
        departed: '任务已发车',
        completed: '任务已完成',
        rejected: '任务已被拒绝',
        cancelled: '任务已取消'
      }
      
      if (status === 'departed' || status === 'completed' || status === 'rejected' || status === 'cancelled') {
        return hintMap[status]
      }
      
      return hintMap[status]?.[role] || '等待处理'
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const s = normalizeStatus(status)
      const statusMap = {
        pending: 'info',
        approved: 'success',
        rejected: 'danger',
        assigned: 'primary',
        confirmed: 'warning',
        final_confirmed: 'success',
        departed: 'primary',
        completed: 'success',
        cancelled: 'danger'
      }
      return statusMap[s] || 'info'
    }

    // 获取时间线项目类型
    const getTimelineItemType = (status) => {
      return getStatusType(status)
    }

    // 格式化日期时间
    const formatDateTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 处理操作
    const handleAction = (actionKey) => {
      const action = availableActions.value.find(a => a.key === actionKey)
      if (action) {
        currentAction.value = action
        
        if (actionKey === 'respond') {
          // 打开供应商响应表单
          supplierResponseDialogVisible.value = true
        } else if (actionKey === 'workshop_verify') {
          // 打开车间地调核实操作对话框
          workshopVerificationDialogVisible.value = true
        } else {
          actionForm.comment = ''
          actionDialogVisible.value = true
        }
      }
    }

    // 确认操作
    const confirmAction = async () => {
      if (!currentAction.value) return
      
      submitting.value = true
      loadingActions[currentAction.value.key] = true

      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success(`${currentAction.value.label}成功`)
        actionDialogVisible.value = false
        
        // 通知父组件刷新数据
        emit('task-updated', {
          action: currentAction.value.key,
          comment: actionForm.comment
        })
      } catch (error) {
        ElMessage.error(`${currentAction.value.label}失败`)
      } finally {
        submitting.value = false
        loadingActions[currentAction.value.key] = false
      }
    }

    // 获取响应对话框标题
    const getResponseDialogTitle = () => {
      const userRole = currentUserRole.value
      if (userRole === '供应商' || userRole === 'supplier') {
        return '供应商响应'
      } else if (userRole === '班组长' || userRole === 'team_leader') {
        return '自备派车'
      } else if (userRole === '大容积供应商' || userRole === 'large_capacity_supplier') {
        return '大容积派车'
      }
      return '响应任务'
    }

    // 处理供应商响应成功
    const handleResponseSuccess = (result) => {
      ElMessage.success('响应提交成功')
      supplierResponseDialogVisible.value = false
      emit('task-updated', result)
    }

    // 关闭供应商响应对话框
    const handleSupplierResponseClose = () => {
      supplierResponseDialogVisible.value = false
    }

    // 确认车间地调核实操作
    const confirmWorkshopVerification = async () => {
      if (!workshopVerificationForm.action) {
        ElMessage.warning('请选择操作类型')
        return
      }

      // 验证必填字段
      if (workshopVerificationForm.action === 'downgrade' && !workshopVerificationForm.downgradeTonnage) {
        ElMessage.warning('请输入降档吨位')
        return
      }

      if (workshopVerificationForm.action === 'merge' && !workshopVerificationForm.mergeTaskId) {
        ElMessage.warning('请输入要合并到的任务ID')
        return
      }

      submitting.value = true

      try {
        const requestData = {
          task_id: props.task.id,
          action: workshopVerificationForm.action,
          comment: workshopVerificationForm.comment
        }

        // 根据操作类型添加额外参数
        if (workshopVerificationForm.action === 'downgrade') {
          requestData.downgrade_tonnage = workshopVerificationForm.downgradeTonnage
        } else if (workshopVerificationForm.action === 'merge') {
          requestData.merge_task_id = workshopVerificationForm.mergeTaskId
        }

        const response = await apiService.post('/api/v1/dispatch/workshop-verification', requestData)
        
        if (response.success) {
          const actionLabels = {
            'verify_pass': '核实通过',
            'downgrade': '降档处理',
            'merge': '合并任务'
          }
          
          ElMessage.success(`${actionLabels[workshopVerificationForm.action]}成功`)
          workshopVerificationDialogVisible.value = false
          
          // 重置表单
          workshopVerificationForm.action = ''
          workshopVerificationForm.comment = ''
          workshopVerificationForm.mergeTaskId = ''
          workshopVerificationForm.downgradeTonnage = ''
          
          // 通知父组件刷新数据
          emit('task-updated', {
            action: 'workshop_verification',
            result: response.data
          })
        } else {
          ElMessage.error(response.message || '操作失败')
        }
      } catch (error) {
        console.error('车间地调核实操作失败:', error)
        ElMessage.error('操作失败，请稍后重试')
      } finally {
        submitting.value = false
      }
    }

    // 获取下一阶段操作人角色
    const getNextHandlerRole = (status) => {
      const statusMap = {
        '待审核': '区域调度员',
        '已审批': '供应商',
        '待供应商响应': '供应商',
        '待班组派车': '班组长',
        '供应商已响应': '区域调度员',
        '班组已派车': '区域调度员',
        '已分配': '车间地调',
        '已确认': '外包管理公司',
        '最终确认': '车间地调',
        '已发车': '已完成',
        '已完成': '',
        '已拒绝': '',
        '已取消': ''
      }
      return statusMap[status] || ''
    }

    onMounted(() => {
      if (props.task.status_history) {
        props.task.status_history.forEach(history => {
          fetchUserFullName(history.operator)
        })
      }
      // 加载吨位容积数据
      loadTonnageVolumeData()
    })

    return {
      currentUserRole,
      availableActions,
      hasAvailableActions,
      loadingActions,
      actionDialogVisible,
      supplierResponseDialogVisible,
      currentAction,
      actionForm,
      getStatusAlertClass,
      getStatusText,
      getNextActionHint,
      getStatusType,
      getTimelineItemType,
      formatDateTime,
      handleAction,
      confirmAction,
      getResponseDialogTitle,
      handleResponseSuccess,
      handleSupplierResponseClose,
      userFullNames,
      normalizeUserId,
      tonnageVolumeRange,
      formattedRequiredWeight,
      getNextHandlerRole,
    }
  }
}
</script>

<style scoped>
.task-detail-container {
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f0fe 100%);
  min-height: auto;
  max-height: 70vh;
  overflow-y: auto;
}

/* 状态提示栏样式 */
.status-alert {
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid;
}

/* 任务概览卡片 */
.overview-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(24, 144, 255, 0.1);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, #f8faff 0%, #e6f7ff 100%);
  border-radius: 12px;
  border: 1px solid rgba(24, 144, 255, 0.2);
}

/* 操作按钮区域 */
.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 12px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f7ff 100%);
  border-radius: 12px;
  margin-top: 12px;
}

.action-buttons .el-button {
  min-width: 100px;
  height: 40px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

/* 详情网格 */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.detail-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(24, 144, 255, 0.1);
  transition: all 0.3s ease;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.card-content {
  color: #666;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

/* 车辆信息样式 */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.vehicle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.vehicle-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(24, 144, 255, 0.1);
  transition: all 0.3s ease;
}

/* 时间线样式 */
.timeline-container {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(24, 144, 255, 0.1);
}

.timeline-content {
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.timeline-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.timeline-info {
  font-size: 14px;
  color: #666;
}

.timeline-info .operator {
  margin-bottom: 4px;
  font-weight: 500;
}

.timeline-info .comment {
  margin: 8px 0;
  padding: 8px 12px;
  background: #e9f5ff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.timeline-info .next-operator {
  margin-top: 8px;
  padding: 6px 12px;
  background: #fff7e6;
  border-radius: 4px;
  border-left: 3px solid #ffa000;
  font-weight: 500;
  color: #d2691e;
}
</style>
