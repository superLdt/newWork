<template>
  <div class="workshop-verification-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-button 
        type="text" 
        @click="goBack" 
        class="back-button"
      >
        <el-icon><ArrowLeft /></el-icon>
        返回任务列表
      </el-button>
      <h1>车间地调核查</h1>
    </div>

    <!-- 任务信息卡片 -->
    <el-card class="task-info-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>任务信息</span>
          <el-tag 
            :type="getStatusType(task.status)" 
            size="large"
          >
            {{ task.status }}
          </el-tag>
        </div>
      </template>

      <div class="task-info-grid" v-if="task.task_id">
        <div class="info-item">
          <label>任务ID：</label>
          <span>{{ task.task_id }}</span>
        </div>
        <div class="info-item">
          <label>邮路名称：</label>
          <span>{{ task.mail_route_name }}</span>
        </div>
        <div class="info-item">
          <label>业务类型：</label>
          <span>{{ task.business_type }}</span>
        </div>
        <div class="info-item">
          <label>需求吨位：</label>
          <span>{{ formattedRequiredWeight }}</span>
        </div>
        <div class="info-item">
          <label>要求时间：</label>
          <span>{{ formatDateTime(task.required_date) }}</span>
        </div>
        <div class="info-item">
          <label>创建时间：</label>
          <span>{{ formatDateTime(task.created_at) }}</span>
        </div>
        <div class="info-item">
          <label>创建人：</label>
          <span>{{ task.creator_name }}</span>
        </div>
        <div class="info-item">
          <label>组开单位：</label>
          <span>{{ task.organizing_unit }}</span>
        </div>
        <div class="info-item full-width" v-if="task.remarks">
          <label>任务备注：</label>
          <span>{{ task.remarks }}</span>
        </div>
      </div>
    </el-card>

    <!-- 响应车辆信息卡片 -->
    <el-card class="vehicle-info-card" v-if="task.vehicles && task.vehicles.length > 0">
      <template #header>
        <span>响应车辆信息</span>
      </template>
      
      <el-table 
        :data="task.vehicles" 
        border 
        stripe
        class="vehicle-table"
      >
    <el-table-column prop="manifest_number" label="路单流水号" width="120" />
        <el-table-column prop="dispatch_number" label="派车单号" width="120" />
        <el-table-column prop="license_plate" label="车牌" width="100" />
        <el-table-column prop="carriage_number" label="车厢号" width="100" />
        <el-table-column prop="actual_volume" label="实际容积" width="120">
          <template #default="scope">
            <span :class="{ 'tonnage-mismatch': isTonnageMismatch(scope.row) }">
              {{ formatVolume(scope.row.actual_volume) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="vehicle_type" label="实际吨位" width="120">
          <template #default="scope">
            <span :class="{ 'tonnage-mismatch': isTonnageMismatch(scope.row) }">
              {{ formatTonnage(scope.row.vehicle_type) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="required_volume" label="需求容积" width="100">
          <template #default="scope">
            {{ scope.row.required_volume }} m³
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag 
              v-if="isTonnageMismatch(scope.row)" 
              type="warning" 
              size="small"
            >
              吨位不一致
            </el-tag>
            <el-tag 
              v-else 
              type="success" 
              size="small"
            >
              正常
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 吨位不一致提示 -->
      <div v-if="hasTonnageMismatch" class="tonnage-warning">
        <el-alert
          title="注意：存在车辆实际吨位与需求吨位不一致"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            该车实际吨位与需求吨位不一致，需要降档或合并操作。
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 核查操作卡片 -->
    <el-card class="verification-card">
      <template #header>
        <span>核查操作</span>
      </template>

      <el-form 
        :model="verificationForm" 
        :rules="verificationRules"
        ref="verificationFormRef"
        label-width="120px"
        class="verification-form"
      >
        <el-form-item label="操作类型" prop="action" required>
          <el-radio-group v-model="verificationForm.action" size="large" @change="handleActionChange">
            <el-radio-button 
              label="verify_pass" 
              :disabled="!canVerifyPass && !isBusinessTypeRestricted"
            >
              核实通过
              <span v-if="!canVerifyPass && !isBusinessTypeRestricted" class="disabled-tip">（吨位不一致）</span>
            </el-radio-button>
            <el-radio-button 
              label="downgrade" 
              :disabled="isBusinessTypeRestricted"
            >
              降档处理
              <span v-if="isBusinessTypeRestricted" class="disabled-tip">（业务类型限制）</span>
            </el-radio-button>
            <el-radio-button 
              label="merge" 
              :disabled="isBusinessTypeRestricted"
            >
              合并派车单
              <span v-if="isBusinessTypeRestricted" class="disabled-tip">（业务类型限制）</span>
            </el-radio-button>
          </el-radio-group>
          <div v-if="!canVerifyPass && !isBusinessTypeRestricted" class="form-tip warning-tip">
            检测到车辆实际吨位与需求吨位不一致，只能进行降档处理或合并派车单操作
          </div>
          <div v-if="isBusinessTypeRestricted" class="form-tip info-tip">
            当前业务类型（{{ task.business_type }}）仅支持核实通过操作
          </div>
        </el-form-item>

        <!-- 合并派车单时的车厢容积照片上传 -->
        <el-form-item label="车厢容积照片" v-if="verificationForm.action === 'merge'">
          <div class="attachment-upload">
            <div class="upload-group">
              <label style="display:block; margin-bottom:6px;">合并前派车车辆车厢容积照片</label>
              <UploadComponent
                v-model="mergeBeforeImages"
                file-type="image"
                business-type="merge_before"
                :business-id="task?.task_id"
                :multiple="true"
                :limit="10"
                list-type="picture-card"
                tip="支持jpg/png格式，单个文件不超过5MB"
                @success="handleMergeBeforeUploadSuccess"
                @remove="handleMergeBeforeUploadRemove"
              />
            </div>
            <div class="upload-group" style="margin-top:12px;">
              <label style="display:block; margin-bottom:6px;">新增派车车辆车厢容积照片</label>
              <UploadComponent
                v-model="mergeNewImages"
                file-type="image"
                business-type="merge_new"
                :business-id="task?.task_id"
                :multiple="true"
                :limit="10"
                list-type="picture-card"
                tip="支持jpg/png格式，单个文件不超过5MB"
                @success="handleMergeNewUploadSuccess"
                @remove="handleMergeNewUploadRemove"
              />
            </div>
            <div class="form-tip">请分别上传合并前和新增车辆的车厢容积照片，用于记录合并操作。</div>
          </div>
        </el-form-item>
        
        <!-- 降档处理时显示 -->
        <el-form-item 
          v-if="verificationForm.action === 'downgrade'" 
          label="降档吨位" 
          prop="downgradeTonnage"
          required
        >
          <el-select
            v-model="verificationForm.downgradeTonnage"
            placeholder="请选择降档后的吨位"
            style="width: 300px;"
            clearable
          >
            <el-option
              v-for="tonnage in allowedTonnageOptions"
              :key="tonnage"
              :label="`${tonnage}吨`"
              :value="tonnage"
            />
          </el-select>
          <div class="form-tip">
            当前需求吨位：{{ formattedRequiredWeight }}
          </div>
        </el-form-item>

        <!-- 降档处理时的车厢容积照片上传 -->
        <el-form-item 
          v-if="verificationForm.action === 'downgrade'" 
          label="车厢容积照片"
        >
          <div class="upload-section">
            <UploadComponent
              v-model="downgradeImages"
              file-type="image"
              business-type="downgrade"
              :business-id="task?.task_id"
              :multiple="true"
              :limit="10"
              list-type="picture-card"
              tip="请上传派车车辆车厢容积照片，支持jpg/png格式，单个文件不超过5MB"
              @success="handleDowngradeUploadSuccess"
              @remove="handleDowngradeUploadRemove"
            />
          </div>
        </el-form-item>
        
        <!-- 合并派车单时显示 -->
        <el-form-item 
          v-if="verificationForm.action === 'merge'" 
          label="合并车辆派车单号" 
          prop="mergeDispatchNumber"
          required
        >
          <el-input
            v-model="verificationForm.mergeDispatchNumber"
            placeholder="请输入要合并到的派车单号"
            style="width: 300px;"
          />
          <div class="form-tip">
            请确保目标派车单存在且状态允许合并
          </div>
        </el-form-item>
        
        <!-- 选择合并车辆 -->
        <el-form-item 
          v-if="verificationForm.action === 'merge'" 
          label="选择合并车辆"
        >
          <div class="merge-vehicles-section">
            <div class="current-vehicles">
              <h4>当前任务车辆：</h4>
              <el-table 
                :data="task.vehicles" 
                border 
                size="small"
                class="merge-vehicle-table"
              >
                <el-table-column prop="license_plate" label="车牌" width="100" />
                <el-table-column prop="carriage_number" label="车厢号" width="100" />
                <el-table-column prop="actual_volume" label="实际容积" width="120">
                  <template #default="scope">
                    {{ formatVolume(scope.row.actual_volume || scope.row.standard_volume) }}
                  </template>
                </el-table-column>
                <el-table-column prop="vehicle_type" label="实际吨位" width="120">
                  <template #default="scope">
                    {{ formatTonnage(scope.row.vehicle_type || scope.row.original_capacity) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div class="additional-vehicles">
              <h4>新增合并车辆：</h4>
              <el-button 
                type="primary" 
                size="small" 
                @click="showAddVehicleDialog = true"
                style="margin-bottom: 10px;"
              >
                添加车辆
              </el-button>
              
              <el-table 
                :data="verificationForm.mergeVehicles" 
                border 
                size="small"
                class="merge-vehicle-table"
                v-show="verificationForm.mergeVehicles.length > 0"
              >
                <el-table-column prop="license_plate" label="车牌" width="100" />
                <el-table-column prop="carriage_number" label="车厢号" width="100" />
                <el-table-column prop="actual_volume" label="实际容积" width="120">
                  <template #default="scope">
                    {{ formatVolume(scope.row.actual_volume) }}
                  </template>
                </el-table-column>
                <el-table-column prop="vehicle_type" label="实际吨位" width="120">
                  <template #default="scope">
                    {{ formatTonnage(scope.row.vehicle_type) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="scope">
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="removeMergeVehicle(scope.$index)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <div v-show="verificationForm.mergeVehicles.length === 0" class="empty-vehicles">
                暂无新增车辆
              </div>
            </div>
            
            <!-- 合并后容积和吨位预览 -->
            <div class="merge-summary" v-show="verificationForm.mergeVehicles.length > 0">
              <h4>合并后预览：</h4>
              <div class="summary-info">
                <span>总容积：{{ totalMergedVolume }} m³</span>
                <span style="margin-left: 20px;">合并吨位：{{ mergedTonnage }}</span>
                <span 
                  v-if="isOverRequiredWeight" 
                  style="margin-left: 20px; color: #e6a23c;"
                >
                  ⚠️ 超出需求吨位，该车合并最大计算吨位为{{ getRequiredWeightValue() }}吨
                </span>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="操作备注" prop="comment">
          <el-input
            v-model="verificationForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请输入操作备注..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            @click="submitVerification" 
            :loading="submitting"
            :disabled="!verificationForm.action"
          >
            确认{{ getActionLabel(verificationForm.action) }}
          </el-button>
          <el-button 
            size="large"
            @click="resetForm"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作历史 -->
    <el-card class="history-card" v-if="task.status_history && task.status_history.length > 0">
      <template #header>
        <span>操作历史</span>
      </template>
      
      <el-timeline>
        <el-timeline-item
          v-for="(history, index) in task.status_history"
          :key="index"
          :timestamp="formatDateTime(history.timestamp)"
          placement="top"
        >
          <div class="history-item">
            <div class="history-status">{{ history.status_change }}</div>
            <div class="history-operator">操作人：{{ history.operator }}</div>
            <div class="history-note" v-if="history.note">{{ history.note }}</div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
    <!-- 添加车辆对话框 -->
    <el-dialog
      v-model="showAddVehicleDialog"
      title="添加合并车辆"
      width="900px"
      :before-close="handleCloseAddVehicleDialog"
    >
      <div class="vehicle-selection-section">
        <!-- 顶部搜索与分页设置 -->
        <div style="display:flex; gap:12px; align-items:center; margin-bottom:10px;">
          <el-input
            v-model="searchQuery"
            placeholder="输入车牌号进行模糊筛选"
            clearable
            style="width:260px;"
          />
          <el-select v-model="pageSize" style="width:120px;" placeholder="每页数量">
            <el-option :label="'每页 10'" :value="10" />
            <el-option :label="'每页 20'" :value="20" />
            <el-option :label="'每页 50'" :value="50" />
          </el-select>
          <el-button type="primary" size="small" @click="loadAvailableVehicles" :loading="vehicleListLoading">刷新列表</el-button>
        </div>

        <el-table
          :data="paginatedVehicles"
          border
          size="small"
          max-height="300px"
          v-loading="vehicleListLoading"
          @row-click="handleVehicleSelect"
          highlight-current-row
          :row-key="row => row.license_plate + (row.carriage_number || '')"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="license_plate" label="车牌号" width="120" />
          <el-table-column prop="carriage_number" label="车厢号" width="120" />
          <el-table-column prop="actual_volume" label="实际容积" width="120">
            <template #default="scope">
              {{ formatVolume(scope.row.actual_volume || scope.row.standard_volume) }}
            </template>
          </el-table-column>
          <el-table-column prop="vehicle_type" label="实际吨位" width="120">
            <template #default="scope">
              {{ formatTonnage(scope.row.vehicle_type || scope.row.original_capacity) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click.stop="handleVehicleSelect(scope.row)"
                :disabled="selectedVehicleFromList && selectedVehicleFromList.license_plate === scope.row.license_plate"
              >
                {{ selectedVehicleFromList && selectedVehicleFromList.license_plate === scope.row.license_plate ? '已选择' : '选择' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!vehicleListLoading && filteredVehicles.length === 0" class="empty-data" style="text-align: center; padding: 20px; color: #999;">
          暂无可用车辆
        </div>

        <div style="display:flex; justify-content:flex-end; margin-top:8px;">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="filteredVehicles.length"
            :page-size="pageSize"
            :current-page="currentPage"
            @current-change="(p)=> currentPage = p"
          />
        </div>

        <!-- 显示选中的车辆信息 -->
        <div v-if="selectedVehicleFromList" class="selected-vehicle-info" style="margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 4px;">
          <h4 style="margin: 0 0 10px 0; color: #409eff;">已选择车辆：</h4>
          <p style="margin: 5px 0;"><strong>车牌号：</strong>{{ selectedVehicleFromList.license_plate }}</p>
          <p style="margin: 5px 0;"><strong>车厢号：</strong>{{ selectedVehicleFromList.carriage_number }}</p>
          <p style="margin: 5px 0;"><strong>实际容积：</strong>{{ formatVolume(selectedVehicleFromList.actual_volume || selectedVehicleFromList.standard_volume) }}</p>
          <p style="margin: 5px 0;"><strong>实际吨位：</strong>{{ formatTonnage(selectedVehicleFromList.vehicle_type || selectedVehicleFromList.original_capacity) }}</p>
        </div>

        <!-- 合并的手动表单（与列表同一界面） -->
        <div style="margin-top:16px;">
          <el-form
            ref="addVehicleFormRef"
            :model="addVehicleForm"
            :rules="addVehicleRules"
            label-width="100px"
          >
            <div style="display:flex; gap:16px; flex-wrap:wrap;">
              <el-form-item label="车牌号" prop="license_plate">
                <el-input
                  v-model="addVehicleForm.license_plate"
                  placeholder="输入车牌号可同步筛选上方列表"
                  style="width: 220px;"
                  clearable
                />
              </el-form-item>
            </div>
          </el-form>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCloseAddVehicleDialog">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleAddVehicle"
            :disabled="!selectedVehicleFromList && !addVehicleForm.license_plate"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { dispatchService } from '@/services/dispatchService'
import { apiService } from '@/services/api'
import { authService } from '@/services/authService'
import tonnageVolumeService from '@/services/tonnageVolumeService'
import { vehicleCapacityReferenceService } from '@/services/vehicleCapacityReferenceService'
import { usePermissionStore } from '@/stores/permission'
import UploadComponent from '@/components/common/UploadComponent.vue'

export default {
  name: 'WorkshopVerification',
  components: {
    ArrowLeft,
    UploadComponent
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const permissionStore = usePermissionStore()
    
    // 数据状态
    const loading = ref(false)
    const submitting = ref(false)
    const task = ref({})
    const verificationFormRef = ref(null)
    const showAddVehicleDialog = ref(false)
    const addVehicleFormRef = ref(null)
    const tonnageOptions = ref([])
    const tonnageVolumeMapping = ref([])
    
    // 附件相关状态
    const attachments = ref([])
    const imageFileList = ref([])
    const docFileList = ref([])
    
    // 新的上传组件数据
    const mergeBeforeImages = ref([])
    const mergeNewImages = ref([])
    const downgradeImages = ref([])
    
    // 保留旧的文件列表状态以兼容现有逻辑
    const mergeBeforeImageFileList = ref([])
    const mergeNewImageFileList = ref([])
    const downgradeImageFileList = ref([])
    
    // 车辆选择相关数据
    const addVehicleTabActive = ref('select') // 'select' 或 'manual'
    const availableVehicles = ref([])
    const selectedVehicleFromList = ref(null)
    const vehicleListLoading = ref(false)
    const searchQuery = ref('')
    const pageSize = ref(20)
    const currentPage = ref(1)
    
    // 核查表单
    const verificationForm = reactive({
      action: 'verify_pass', // 默认选择核实通过
      comment: '',
      mergeDispatchNumber: '', // 合并时的目标派车单号
      downgradeTonnage: '', // 降档时的新吨位
      mergeVehicles: [] // 选择的合并车辆
    })
    
    // 添加车辆表单
    const addVehicleForm = reactive({
      license_plate: '',
      carriage_number: '',
      actual_volume: null,
      vehicle_type: ''
    })

    // 表单验证规则
    const verificationRules = {
      action: [
        { required: true, message: '请选择操作类型', trigger: 'change' }
      ],
      downgradeTonnage: [
        { 
          required: true, 
          message: '请选择降档吨位', 
          trigger: 'change',
          validator: (rule, value, callback) => {
            if (verificationForm.action === 'downgrade') {
              if (!value) {
                callback(new Error('请选择降档吨位'))
              } else if (!allowedTonnageOptions.includes(Number(value))) {
                callback(new Error('请选择有效的吨位选项'))
              } else {
                callback()
              }
            } else {
              callback()
            }
          }
        }
      ],
      mergeDispatchNumber: [
        { 
          required: true, 
          message: '请输入要合并到的派车单号', 
          trigger: 'blur',
          validator: (rule, value, callback) => {
            if (verificationForm.action === 'merge') {
              if (!value) {
                callback(new Error('请输入要合并到的派车单号'))
              } else if (!/^[A-Za-z0-9\-_]+$/.test(value)) {
                callback(new Error('派车单号格式不正确'))
              } else {
                callback()
              }
            } else {
              callback()
            }
          }
        }
      ]
    }
    
    // 添加车辆表单验证规则
    const addVehicleRules = {
      license_plate: [
        { required: true, message: '请输入车牌号', trigger: 'blur' },
        { pattern: /^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$/, message: '请输入正确的车牌号格式', trigger: 'blur' }
      ],
      carriage_number: [],
      actual_volume: [
        { required: true, message: '请输入实际容积', trigger: 'blur' },
        { type: 'number', min: 0, message: '实际容积必须大于0', trigger: 'blur' }
      ],
      vehicle_type: [
        { required: true, message: '请选择实际吨位', trigger: 'change' }
      ]
    }

    // 格式化需求吨位显示
    const formattedRequiredWeight = computed(() => {
      if (!task.value.required_weight) return ''
      return task.value.required_weight.replace(/吨.*吨$/, '吨')
    })

    // 本地模糊筛选、分页
    const normalize = (s) => (s || '').toString().toUpperCase().replace(/\s+/g, '')
    const filteredVehicles = computed(() => {
      const q = normalize(searchQuery.value)
      const list = Array.isArray(availableVehicles.value) ? availableVehicles.value : []
      if (!q) return list
      return list.filter(v => normalize(v.license_plate).includes(q))
    })
    const paginatedVehicles = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredVehicles.value.slice(start, end)
    })

    // 显示格式化
    const formatVolume = (val) => {
      const num = parseFloat(val)
      if (Number.isNaN(num)) return '—'
      return `${num.toFixed(2)} m³`
    }
    const formatTonnage = (val) => {
      if (val === null || val === undefined || val === '') return '—'
      const text = val.toString().replace(/吨/g, '')
      return `${text}吨`
    }

    // 检查车辆吨位是否不一致
    const isTonnageMismatch = (vehicle) => {
      if (!vehicle || !task.value.required_weight) return false
      
      // 从需求吨位中提取数字
      const requiredWeightMatch = task.value.required_weight.match(/(\d+(?:\.\d+)?)/);
      if (!requiredWeightMatch) return false
      
      const requiredWeight = parseFloat(requiredWeightMatch[1]);
      
      // 从车辆类型中提取数字（实际吨位）
      const actualWeightMatch = vehicle.vehicle_type?.toString().match(/(\d+(?:\.\d+)?)/);
      if (!actualWeightMatch) return false
      
      const actualWeight = parseFloat(actualWeightMatch[1]);
      
      // 比较实际吨位和需求吨位
      return actualWeight !== requiredWeight;
    }

    // 计算是否存在吨位不一致的车辆
    const hasTonnageMismatch = computed(() => {
      if (!task.value.vehicles || !Array.isArray(task.value.vehicles)) return false
      return task.value.vehicles.some(vehicle => isTonnageMismatch(vehicle))
    })

    // 检查是否可以核实通过（只有吨位一致时才能核实通过）
    const canVerifyPass = computed(() => {
      if (!task.value.vehicles || !Array.isArray(task.value.vehicles)) return true
      // 如果没有车辆信息，允许核实通过
      if (task.value.vehicles.length === 0) return true
      
      // 大容积派车和班组派车不需要验证吨位一致性，直接允许核实通过
      const businessType = task.value?.business_type
      if (businessType === '大容积派车' || businessType === '班组派车') {
        return true
      }
      
      // 其他业务类型只有所有车辆吨位都一致时才能核实通过
      return !task.value.vehicles.some(vehicle => isTonnageMismatch(vehicle))
    })

    // 检查业务类型是否限制降档和合并操作
    const isBusinessTypeRestricted = computed(() => {
      const businessType = task.value?.business_type
      return businessType === '自办派车' || businessType === '大容积派车'
    })

    // 获取实际吨位（用于降档处理的默认值）
    const getActualTonnage = () => {
      if (!task.value.vehicles || !Array.isArray(task.value.vehicles) || task.value.vehicles.length === 0) {
        return ''
      }
      
      // 取第一个车辆的实际吨位作为默认值
      const firstVehicle = task.value.vehicles[0]
      const actualWeightMatch = firstVehicle.vehicle_type?.toString().match(/(\d+(?:\.\d+)?)/);
      return actualWeightMatch ? actualWeightMatch[1] : ''
    }

    // 允许的吨位选项（仅限5、8、12、20、30吨）
    const allowedTonnageOptions = [5, 8, 12, 20, 30]
    
    // 计算合并后的总容积
    const totalMergedVolume = computed(() => {
      let currentVolume = 0
      console.log('totalMergedVolume计算 - task.value.vehicles:', task.value.vehicles)
      if (task.value.vehicles && Array.isArray(task.value.vehicles)) {
        currentVolume = task.value.vehicles.reduce((sum, vehicle) => {
          // 去除单位后缀（如 "m³"）并解析数值
          const volumeStr = String(vehicle.actual_volume || '0').replace(/[^\d.]/g, '')
          const volume = parseFloat(volumeStr) || 0
          console.log('totalMergedVolume计算 - 当前车辆容积:', vehicle.actual_volume, '清理后:', volumeStr, '解析后:', volume)
          return sum + volume
        }, 0)
      }
      console.log('totalMergedVolume计算 - 当前任务车辆总容积:', currentVolume)
      
      console.log('totalMergedVolume计算 - verificationForm.mergeVehicles:', verificationForm.mergeVehicles)
      const additionalVolume = verificationForm.mergeVehicles.reduce((sum, vehicle) => {
        // 去除单位后缀（如 "m³"）并解析数值
        const volumeStr = String(vehicle.actual_volume || '0').replace(/[^\d.]/g, '')
        const volume = parseFloat(volumeStr) || 0
        console.log('totalMergedVolume计算 - 合并车辆容积:', vehicle.actual_volume, '清理后:', volumeStr, '解析后:', volume)
        return sum + volume
      }, 0)
      console.log('totalMergedVolume计算 - 合并车辆总容积:', additionalVolume)
      
      const total = (currentVolume + additionalVolume).toFixed(2)
      console.log('totalMergedVolume计算 - 最终总容积:', total)
      return total
    })
    
    // 根据总容积计算合并吨位
    const mergedTonnage = computed(() => {
      // 去除单位后缀（如 "m³"）并解析数值
      const volumeStr = String(totalMergedVolume.value || '0').replace(/[^\d.]/g, '')
      const volume = parseFloat(volumeStr)
      console.log('mergedTonnage计算 - 总容积字符串:', totalMergedVolume.value, '清理后:', volumeStr, '解析后:', volume)
      console.log('mergedTonnage计算 - tonnageVolumeMapping长度:', tonnageVolumeMapping.value.length)
      console.log('mergedTonnage计算 - tonnageVolumeMapping数据:', tonnageVolumeMapping.value)
      
      if (!volume || tonnageVolumeMapping.value.length === 0) {
        console.log('mergedTonnage计算 - 返回空值，原因:', !volume ? '容积为空' : '映射数据为空')
        return ''
      }
      
      // 获取需求吨位
      let requiredWeight = null
      if (task.value && task.value.required_weight) {
        const requiredWeightMatch = task.value.required_weight.match(/(\d+(?:\.\d+)?)/);
        if (requiredWeightMatch) {
          requiredWeight = parseFloat(requiredWeightMatch[1]);
          console.log('mergedTonnage计算 - 需求吨位:', requiredWeight)
        }
      }
      
      // 按吨位从小到大排序
      const sortedMappings = [...tonnageVolumeMapping.value].sort((a, b) => a.tonnage - b.tonnage)
      console.log('mergedTonnage计算 - 排序后的映射:', sortedMappings)
      
      // 找到最合适的吨位：根据容积范围匹配
      let bestMatch = null
      
      // 查找容积在范围内的吨位
      for (const mapping of sortedMappings) {
        const minVolume = mapping.min_volume || 0
        const maxVolume = mapping.max_volume || Infinity
        console.log(`mergedTonnage计算 - 检查${mapping.tonnage}吨: ${minVolume} <= ${volume} <= ${maxVolume}`)
        
        if (volume >= minVolume && volume <= maxVolume) {
          bestMatch = mapping
          console.log(`mergedTonnage计算 - 找到匹配的吨位: ${mapping.tonnage}吨`)
          break
        }
      }
      
      // 如果没找到精确匹配，选择最接近的吨位（容积刚好超出范围的情况）
      if (!bestMatch) {
        console.log('mergedTonnage计算 - 未找到精确匹配，寻找最接近的吨位')
        // 找到第一个最小容积小于等于实际容积的吨位
        for (const mapping of sortedMappings.reverse()) {
          if (volume >= (mapping.min_volume || 0)) {
            bestMatch = mapping
            console.log(`mergedTonnage计算 - 选择最接近的吨位: ${mapping.tonnage}吨`)
            break
          }
        }
        // 如果还是没找到，选择最小的吨位
        if (!bestMatch) {
          bestMatch = sortedMappings[0]
          console.log(`mergedTonnage计算 - 选择最小吨位: ${bestMatch?.tonnage}吨`)
        }
      }
      
      console.log('mergedTonnage计算 - 最佳匹配:', bestMatch)
      
      // 记录原始计算的吨位（用于超出检查）
      const originalTonnage = bestMatch ? bestMatch.tonnage : 0
      
      // 应用需求吨位上限限制
      let finalTonnage = originalTonnage
      if (requiredWeight && finalTonnage > requiredWeight) {
        console.log(`mergedTonnage计算 - 应用上限限制: ${finalTonnage}吨 -> ${requiredWeight}吨`)
        finalTonnage = requiredWeight
      }
      
      const result = finalTonnage ? `${finalTonnage}吨` : ''
      console.log('mergedTonnage计算 - 最终结果:', result)
      
      return result
    })

    // 获取原始计算的合并吨位（未应用上限限制）
    const getOriginalMergedTonnage = () => {
      const volumeStr = String(totalMergedVolume.value || '0').replace(/[^\d.]/g, '')
      const volume = parseFloat(volumeStr)
      if (!volume || tonnageVolumeMapping.value.length === 0) return null
      
      const sortedMappings = [...tonnageVolumeMapping.value].sort((a, b) => a.tonnage - b.tonnage)
      let bestMatch = null
      
      for (const mapping of sortedMappings) {
        const minVolume = mapping.min_volume || 0
        const maxVolume = mapping.max_volume || Infinity
        if (volume >= minVolume && volume <= maxVolume) {
          bestMatch = mapping
          break
        }
      }
      
      if (!bestMatch) {
        for (const mapping of sortedMappings.reverse()) {
          if (volume >= (mapping.min_volume || 0)) {
            bestMatch = mapping
            break
          }
        }
        if (!bestMatch) {
          bestMatch = sortedMappings[0]
        }
      }
      
      return bestMatch ? bestMatch.tonnage : null
    }

    // 获取合并吨位的数值（用于写入数据库的actual_weight）
    const getMergedTonnageValue = () => {
      // 去除单位后缀（如 "m³"）并解析数值
      const volumeStr = String(totalMergedVolume.value || '0').replace(/[^\d.]/g, '')
      const volume = parseFloat(volumeStr)
      if (!volume || tonnageVolumeMapping.value.length === 0) return null
      
      // 获取需求吨位
      let requiredWeight = null
      if (task.value && task.value.required_weight) {
        const requiredWeightMatch = task.value.required_weight.match(/(\d+(?:\.\d+)?)/);
        if (requiredWeightMatch) {
          requiredWeight = parseFloat(requiredWeightMatch[1]);
        }
      }
      
      // 按吨位从小到大排序
      const sortedMappings = [...tonnageVolumeMapping.value].sort((a, b) => a.tonnage - b.tonnage)
      
      // 找到最合适的吨位：根据容积范围匹配
      let bestMatch = null
      
      // 查找容积在范围内的吨位
      for (const mapping of sortedMappings) {
        const minVolume = mapping.min_volume || 0
        const maxVolume = mapping.max_volume || Infinity
        
        if (volume >= minVolume && volume <= maxVolume) {
          bestMatch = mapping
          break
        }
      }
      
      // 如果没找到精确匹配，选择最接近的吨位
      if (!bestMatch) {
        for (const mapping of sortedMappings.reverse()) {
          if (volume >= (mapping.min_volume || 0)) {
            bestMatch = mapping
            break
          }
        }
        if (!bestMatch) {
          bestMatch = sortedMappings[0]
        }
      }
      
      // 应用需求吨位上限限制
      let finalTonnage = bestMatch ? bestMatch.tonnage : null
      if (requiredWeight && finalTonnage && finalTonnage > requiredWeight) {
        finalTonnage = requiredWeight
      }
      
      return finalTonnage
    }

    // 检查是否超出需求吨位
    // 获取需求吨位数值
    const getRequiredWeightValue = () => {
      if (!task.value || !task.value.required_weight) return null
      const requiredWeightMatch = task.value.required_weight.match(/(\d+(?:\.\d+)?)/);
      return requiredWeightMatch ? parseFloat(requiredWeightMatch[1]) : null
    }

    // 基于映射：从吨位找标准容积，从容积找推荐吨位
    const findMappingByTonnage = (t) => {
      const tn = Number(t)
      return tonnageVolumeMapping.value.find(m => Number(m.tonnage) === tn)
    }
    const bestTonnageByVolume = (vol) => {
      const volume = Number(vol)
      if (!volume || tonnageVolumeMapping.value.length === 0) return null
      const sorted = [...tonnageVolumeMapping.value].sort((a, b) => a.tonnage - b.tonnage)
      let match = null
      for (const m of sorted) {
        if (Number(m.standard_volume) >= volume) { match = m; break }
      }
      if (!match) match = sorted[sorted.length - 1]
      return match ? Number(match.tonnage) : null
    }
    
    // 检查合并后吨位是否超过需求吨位
    const isOverRequiredWeight = computed(() => {
      if (!task.value.required_weight || !totalMergedVolume.value) return false
      
      const requiredWeightMatch = task.value.required_weight.match(/(\d+(?:\.\d+)?)/);
      if (!requiredWeightMatch) return false
      
      const requiredWeight = parseFloat(requiredWeightMatch[1]);
      const originalTonnage = getOriginalMergedTonnage()
      
      if (!originalTonnage) return false
      
      return originalTonnage > requiredWeight
    })

    // 获取需求吨位（用于默认选择）
    const getRequiredTonnage = () => {
      if (!task.value || !task.value.required_weight) return null
      const requiredWeight = parseFloat(task.value.required_weight)
      // 如果需求吨位在允许的选项中，返回该值；否则返回null
      return allowedTonnageOptions.includes(requiredWeight) ? requiredWeight : null
    }

    // 监听操作类型变化，自动设置降档吨位默认值
    const handleActionChange = () => {
      // 如果业务类型限制了降档和合并操作，强制选择核实通过
      if (isBusinessTypeRestricted.value && (verificationForm.action === 'downgrade' || verificationForm.action === 'merge')) {
        verificationForm.action = 'verify_pass'
        ElMessage.warning('当前业务类型仅支持核实通过操作')
        return
      }
      
      if (verificationForm.action === 'downgrade') {
        // 使用供应商响应车辆的实际吨位作为默认值
        const actualTonnage = getActualTonnage()
        if (actualTonnage && allowedTonnageOptions.includes(Number(actualTonnage))) {
          verificationForm.downgradeTonnage = actualTonnage
        } else {
          // 如果实际吨位不在允许范围内，清空选择
          verificationForm.downgradeTonnage = ''
        }
      }
    }

    // 上传前校验：图片
    const beforeUploadImage = (file) => {
      const isValidType = ['image/jpeg', 'image/png'].includes(file.type)
      const isLt5M = file.size / 1024 / 1024 <= 5
      if (!isValidType) {
        ElMessage.warning('仅支持jpg/png图片')
        return false
      }
      if (!isLt5M) {
        ElMessage.warning('图片大小不能超过5MB')
        return false
      }
      return true
    }

    // 上传成功：图片
    const handleImageSuccess = (response, file, fileList) => {
      if (response && (response.code === 0 || response.success === true)) {
        const url = response?.data?.url || response?.url || file?.url || ''
        const item = {
          attachment_type: 'image',
          file_name: file.name,
          file_path: url,
          file_size: file.size,
          mime_type: file.type,
          description: '现场照片'
        }
        attachments.value.push(item)
        imageFileList.value = fileList || []
        ElMessage.success('图片上传成功')
      } else {
        ElMessage.error(response?.message || '图片上传失败')
      }
    }

    // 移除图片
    const handleImageRemove = (file, fileList) => {
      imageFileList.value = fileList || []
      const url = (file?.response && (file.response?.data?.url || file.response?.url)) || file?.url || ''
      attachments.value = attachments.value.filter(a => !(a.attachment_type === 'image' && a.file_name === file.name && (url ? a.file_path === url : true)))
    }

    // 上传前校验：文档
    const beforeUploadDoc = (file) => {
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      const isValidType = allowedTypes.includes(file.type) || /\.(pdf|doc|docx)$/i.test(file.name)
      const isLt10M = file.size / 1024 / 1024 <= 10
      if (!isValidType) {
        ElMessage.warning('仅支持pdf/doc/docx文档')
        return false
      }
      if (!isLt10M) {
        ElMessage.warning('文件大小不能超过10MB')
        return false
      }
      return true
    }

    // 上传成功：文档
    const handleDocSuccess = (response, file, fileList) => {
      if (response && (response.code === 0 || response.success === true)) {
        const url = response?.data?.url || response?.url || file?.url || ''
        const item = {
          attachment_type: 'document',
          file_name: file.name,
          file_path: url,
          file_size: file.size,
          mime_type: file.type,
          description: '审批凭证'
        }
        attachments.value.push(item)
        docFileList.value = fileList || []
        ElMessage.success('文件上传成功')
      } else {
        ElMessage.error(response?.message || '文件上传失败')
      }
    }

    // 移除文档
    const handleDocRemove = (file, fileList) => {
      docFileList.value = fileList || []
      const url = (file?.response && (file.response?.data?.url || file.response?.url)) || file?.url || ''
      attachments.value = attachments.value.filter(a => !(a.attachment_type === 'document' && a.file_name === file.name && (url ? a.file_path === url : true)))
    }

    // 合并前车辆照片上传处理
    const beforeUploadMergeBeforeImage = (file) => {
      const isValidType = ['image/jpeg', 'image/png'].includes(file.type)
      const isLt5M = file.size / 1024 / 1024 <= 5
      if (!isValidType) {
        ElMessage.warning('仅支持jpg/png图片')
        return false
      }
      if (!isLt5M) {
        ElMessage.warning('图片大小不能超过5MB')
        return false
      }
      return true
    }

    const handleMergeBeforeImageSuccess = (response, file, fileList) => {
      if (response && (response.code === 0 || response.success === true)) {
        const url = response?.data?.url || response?.url || file?.url || ''
        const item = {
          attachment_type: 'merge_before_image',
          file_name: file.name,
          file_path: url,
          file_size: file.size,
          mime_type: file.type,
          description: '合并前派车车辆车厢容积照片'
        }
        attachments.value.push(item)
        mergeBeforeImageFileList.value = fileList || []
        ElMessage.success('合并前车辆照片上传成功')
      } else {
        ElMessage.error(response?.message || '合并前车辆照片上传失败')
      }
    }

    const handleMergeBeforeImageRemove = (file, fileList) => {
      mergeBeforeImageFileList.value = fileList || []
      const url = (file?.response && (file.response?.data?.url || file.response?.url)) || file?.url || ''
      attachments.value = attachments.value.filter(a => !(a.attachment_type === 'merge_before_image' && a.file_name === file.name && (url ? a.file_path === url : true)))
    }

    // 新增车辆照片上传处理
    const beforeUploadMergeNewImage = (file) => {
      const isValidType = ['image/jpeg', 'image/png'].includes(file.type)
      const isLt5M = file.size / 1024 / 1024 <= 5
      if (!isValidType) {
        ElMessage.warning('仅支持jpg/png图片')
        return false
      }
      if (!isLt5M) {
        ElMessage.warning('图片大小不能超过5MB')
        return false
      }
      return true
    }

    const handleMergeNewImageSuccess = (response, file, fileList) => {
      if (response && (response.code === 0 || response.success === true)) {
        const url = response?.data?.url || response?.url || file?.url || ''
        const item = {
          attachment_type: 'merge_new_image',
          file_name: file.name,
          file_path: url,
          file_size: file.size,
          mime_type: file.type,
          description: '新增派车车辆车厢容积照片'
        }
        attachments.value.push(item)
        mergeNewImageFileList.value = fileList || []
        ElMessage.success('新增车辆照片上传成功')
      } else {
        ElMessage.error(response?.message || '新增车辆照片上传失败')
      }
    }

    const handleMergeNewImageRemove = (file, fileList) => {
      mergeNewImageFileList.value = fileList || []
      const url = (file?.response && (file.response?.data?.url || file.response?.url)) || file?.url || ''
      attachments.value = attachments.value.filter(a => !(a.attachment_type === 'merge_new_image' && a.file_name === file.name && (url ? a.file_path === url : true)))
    }

    // 降档处理照片上传处理
    const beforeUploadDowngradeImage = (file) => {
      const isValidType = ['image/jpeg', 'image/png'].includes(file.type)
      const isLt5M = file.size / 1024 / 1024 <= 5
      if (!isValidType) {
        ElMessage.warning('仅支持jpg/png图片')
        return false
      }
      if (!isLt5M) {
        ElMessage.warning('图片大小不能超过5MB')
        return false
      }
      return true
    }

    const handleDowngradeImageSuccess = (response, file, fileList) => {
      if (response && (response.code === 0 || response.success === true)) {
        const url = response?.data?.url || response?.url || file?.url || ''
        const item = {
          attachment_type: 'downgrade_image',
          file_name: file.name,
          file_path: url,
          file_size: file.size,
          mime_type: file.type,
          description: '降档处理车厢容积照片'
        }
        attachments.value.push(item)
        downgradeImageFileList.value = fileList || []
        ElMessage.success('降档处理照片上传成功')
      } else {
        ElMessage.error(response?.message || '降档处理照片上传失败')
      }
    }

    const handleDowngradeImageRemove = (file, fileList) => {
      downgradeImageFileList.value = fileList || []
      const url = (file?.response && (file.response?.data?.url || file.response?.url)) || file?.url || ''
      attachments.value = attachments.value.filter(a => !(a.attachment_type === 'downgrade_image' && a.file_name === file.name && (url ? a.file_path === url : true)))
    }

    // 新的上传组件事件处理方法
    const handleMergeBeforeUploadSuccess = (files) => {
      files.forEach(file => {
        const item = {
          attachment_type: 'merge_before_image',
          file_name: file.name,
          file_path: file.url,
          file_size: file.size,
          mime_type: file.type,
          description: '合并前派车车辆车厢容积照片'
        }
        attachments.value.push(item)
      })
      // 同步到旧的文件列表以保持兼容性
      mergeBeforeImageFileList.value = mergeBeforeImages.value.map(file => ({
        name: file.name,
        url: file.url,
        response: { data: { url: file.url } }
      }))
    }

    const handleMergeBeforeUploadRemove = (files) => {
      // 从附件列表中移除
      const fileUrls = files.map(f => f.url)
      attachments.value = attachments.value.filter(a => 
        !(a.attachment_type === 'merge_before_image' && fileUrls.includes(a.file_path))
      )
      // 同步到旧的文件列表
      mergeBeforeImageFileList.value = mergeBeforeImages.value.map(file => ({
        name: file.name,
        url: file.url,
        response: { data: { url: file.url } }
      }))
    }

    const handleMergeNewUploadSuccess = (files) => {
      files.forEach(file => {
        const item = {
          attachment_type: 'merge_new_image',
          file_name: file.name,
          file_path: file.url,
          file_size: file.size,
          mime_type: file.type,
          description: '新增派车车辆车厢容积照片'
        }
        attachments.value.push(item)
      })
      // 同步到旧的文件列表以保持兼容性
      mergeNewImageFileList.value = mergeNewImages.value.map(file => ({
        name: file.name,
        url: file.url,
        response: { data: { url: file.url } }
      }))
    }

    const handleMergeNewUploadRemove = (files) => {
      // 从附件列表中移除
      const fileUrls = files.map(f => f.url)
      attachments.value = attachments.value.filter(a => 
        !(a.attachment_type === 'merge_new_image' && fileUrls.includes(a.file_path))
      )
      // 同步到旧的文件列表
      mergeNewImageFileList.value = mergeNewImages.value.map(file => ({
        name: file.name,
        url: file.url,
        response: { data: { url: file.url } }
      }))
    }

    const handleDowngradeUploadSuccess = (files) => {
      files.forEach(file => {
        const item = {
          attachment_type: 'downgrade_image',
          file_name: file.name,
          file_path: file.url,
          file_size: file.size,
          mime_type: file.type,
          description: '降档处理车厢容积照片'
        }
        attachments.value.push(item)
      })
      // 同步到旧的文件列表以保持兼容性
      downgradeImageFileList.value = downgradeImages.value.map(file => ({
        name: file.name,
        url: file.url,
        response: { data: { url: file.url } }
      }))
    }

    const handleDowngradeUploadRemove = (files) => {
      // 从附件列表中移除
      const fileUrls = files.map(f => f.url)
      attachments.value = attachments.value.filter(a => 
        !(a.attachment_type === 'downgrade_image' && fileUrls.includes(a.file_path))
      )
      // 同步到旧的文件列表
      downgradeImageFileList.value = downgradeImages.value.map(file => ({
        name: file.name,
        url: file.url,
        response: { data: { url: file.url } }
      }))
    }

    // 输入联动：车牌模糊筛选、容积/吨位自动匹配
    let isAutoUpdating = false
    watch(() => addVehicleForm.license_plate, (val) => {
      searchQuery.value = val || ''
      currentPage.value = 1
    })
    watch(() => searchQuery.value, () => {
      currentPage.value = 1
    })
    watch(() => addVehicleForm.vehicle_type, (val) => {
      if (isAutoUpdating) return
      const m = findMappingByTonnage(val)
      if (m) {
        isAutoUpdating = true
        addVehicleForm.actual_volume = m.standard_volume
        isAutoUpdating = false
      }
    })
    watch(() => addVehicleForm.actual_volume, (val) => {
      if (isAutoUpdating) return
      const t = bestTonnageByVolume(val)
      if (t !== null) {
        isAutoUpdating = true
        addVehicleForm.vehicle_type = t
        isAutoUpdating = false
      }
    })

    // 获取任务详情
    const fetchTaskDetail = async () => {
      const taskId = route.params.taskId
      if (!taskId) {
        ElMessage.error('缺少任务ID参数')
        setTimeout(() => {
          goBack()
        }, 2000)
        return
      }

      loading.value = true
      try {
        const result = await dispatchService.getTaskDetail(taskId)
        if (result.code === 0) {
          task.value = result.data
          
          // 验证任务状态是否允许核查
          if (task.value.status !== '待核查' && task.value.status !== '待车间核查') {
            ElMessage.warning(`当前任务状态为"${task.value.status}"，不允许进行核查操作`)
            // 延迟返回任务列表
            setTimeout(() => {
              goBack()
            }, 3000) // 增加延迟时间到3秒，让用户有足够时间看到提示
          }
        } else {
          ElMessage.error(result.message || '获取任务详情失败')
          setTimeout(() => {
            goBack()
          }, 3000) // 增加延迟时间到3秒
        }
      } catch (error) {
        console.error('获取任务详情失败:', error)
        ElMessage.error('获取任务详情失败')
        setTimeout(() => {
          goBack()
        }, 3000) // 增加延迟时间到3秒
      } finally {
        loading.value = false
      }
    }

    // 提交核查操作
    const submitVerification = async () => {
      if (!verificationFormRef.value) return
      
      // 验证吨位一致性（大容积派车和班组派车跳过验证）
      const businessType = task.value?.business_type
      const skipTonnageCheck = businessType === '大容积派车' || businessType === '班组派车'
      
      if (verificationForm.action === 'verify_pass' && !skipTonnageCheck && !canVerifyPass.value) {
        ElMessage.warning('存在吨位不一致的车辆，无法执行核实通过操作')
        return
      }
      
      try {
        const valid = await verificationFormRef.value.validate()
        if (!valid) return
      } catch (error) {
        return
      }

      // 检查吨位一致时的降档处理和合并任务确认
      const isWeightConsistent = task.value.vehicles && !task.value.vehicles.some(vehicle => 
        isTonnageMismatch(vehicle)
      )
      
      if (isWeightConsistent && (verificationForm.action === 'downgrade' || verificationForm.action === 'merge')) {
        const actionText = verificationForm.action === 'downgrade' ? '降档处理' : '合并派车单'
        const confirmResult = await ElMessageBox.confirm(
          `当前实际吨位与需求吨位一致，是否强制执行"${actionText}"操作？`,
          '吨位一致确认',
          {
            confirmButtonText: '强制执行',
            cancelButtonText: '取消',
            type: 'warning',
            dangerouslyUseHTMLString: true,
            message: `<div style="color: #e6a23c;">
              <i class="el-icon-warning" style="margin-right: 8px;"></i>
              当前实际吨位与需求吨位一致，通常不需要执行${actionText}操作。
              <br/>确认要强制执行吗？
            </div>`
          }
        ).catch(() => false)

        if (!confirmResult) return
      }

      // 二次确认
      const actionLabels = {
        'verify_pass': '核实通过',
        'downgrade': '降档处理',
        'merge': '合并派车单'
      }
      
      const confirmResult = await ElMessageBox.confirm(
        `确认要执行"${actionLabels[verificationForm.action]}"操作吗？`,
        '确认操作',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).catch(() => false)

      if (!confirmResult) return

      submitting.value = true

      try {
        const requestData = {
          // 后端要求字段：operation_type，而非 action
          operation_type: (verificationForm.action === 'verify_pass') ? 'confirm' : verificationForm.action,
          comment: verificationForm.comment
        }

        // 根据操作类型添加额外参数（字段名与后端保持一致）
        if (verificationForm.action === 'downgrade') {
          const tonnageValue = Number(verificationForm.downgradeTonnage)
          if (Number.isNaN(tonnageValue) || tonnageValue <= 0) {
            ElMessage.warning('降档吨位必须为大于0的数字')
            submitting.value = false
            return
          }
          requestData.tonnage = tonnageValue
        } else if (verificationForm.action === 'merge') {
          const dispatchNumber = verificationForm.mergeDispatchNumber.trim()
          if (!dispatchNumber) {
            ElMessage.warning('合并目标派车单号不能为空')
            submitting.value = false
            return
          }
          
          // 验证合并后吨位不超过需求吨位
          if (isOverRequiredWeight.value) {
            const requiredWeight = getRequiredWeightValue()
            ElMessage.warning(`合并后的吨位超过需求吨位，该车合并最大计算吨位为${requiredWeight}吨`)
            // 仅提示，不拦截。实际写入的吨位会在 getMergedTonnageValue 中被按上限处理。
          }
          
          // 验证必须添加至少一个合并车辆
          if (!verificationForm.mergeVehicles || verificationForm.mergeVehicles.length === 0) {
            ElMessage.warning('请至少添加一个合并车辆')
            submitting.value = false
            return
          }
          
          requestData.merge_dispatch_number = dispatchNumber
          requestData.merge_vehicles = verificationForm.mergeVehicles || []
          
          // 设置合并后的实际吨位 - 使用前端提示的合并吨位
          const displayedTonnage = mergedTonnage.value
          if (displayedTonnage) {
            // 提取数字部分，去掉"吨"字
            const tonnageMatch = displayedTonnage.match(/(\d+(?:\.\d+)?)/)
            if (tonnageMatch) {
              requestData.actual_weight = `${tonnageMatch[1]}吨`
            }
          }

          // 新增车辆信息（用于后端合并记录）
          if (verificationForm.mergeVehicles && verificationForm.mergeVehicles.length > 0) {
            const v = verificationForm.mergeVehicles[0]
            // 解析吨位数字
            const parseNumber = (val) => {
              if (typeof val === 'number') return val
              const m = String(val || '').match(/(\d+(?:\.\d+)?)/)
              return m ? parseFloat(m[1]) : null
            }
            requestData.new_vehicle_info = {
              license_plate: v.license_plate,
              carriage_number: v.carriage_number || '',
              tonnage: parseNumber(v.vehicle_type),
              volume: parseNumber(v.actual_volume),
              vehicle_type: v.vehicle_type
            }
          }
        }

        // 并入附件
        if (attachments.value && attachments.value.length > 0) {
          requestData.attachments = attachments.value
        }

        // 使用 apiService 的基准前缀 /api/v1，这里不要再手动加 /api/v1
        const response = await apiService.post(`/dispatch/tasks/${task.value.task_id}/workshop-verification`, requestData)
        const success = response?.success === true
        
        if (success) {
          ElMessage.success(`${actionLabels[verificationForm.action]}成功`)
          
          // 操作成功后返回任务列表
          setTimeout(() => {
            goBack()
          }, 1500)
        } else {
          // 显示具体的错误信息
          ElMessage.error(response?.message || '操作失败')
          // 添加延迟，确保用户能看到错误信息
          setTimeout(() => {
            // 不自动返回，让用户看到错误信息
          }, 3000)
        }
      } catch (error) {
        console.error('核查操作失败:', error)
        // 显示具体的错误信息
        if (error.response && error.response.data && error.response.data.message) {
          ElMessage.error(`操作失败: ${error.response.data.message}`)
        } else {
          ElMessage.error('操作失败，请重试')
        }
        // 添加延迟，确保用户能看到错误信息
        setTimeout(() => {
          // 不自动返回，让用户看到错误信息
        }, 3000)
      } finally {
        submitting.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      if (verificationFormRef.value) {
        verificationFormRef.value.resetFields()
      }
      verificationForm.action = ''
      verificationForm.comment = ''
      verificationForm.mergeDispatchNumber = ''
      verificationForm.downgradeTonnage = ''
      verificationForm.mergeVehicles = []
      // 清空附件与文件列表
      attachments.value = []
      imageFileList.value = []
      docFileList.value = []
    }

    // 返回任务列表
    const goBack = () => {
      router.push('/dispatch/tasks')
    }

    // 获取操作标签
    const getActionLabel = (action) => {
      const labels = {
        'verify_pass': '核实通过',
        'downgrade': '降档处理',
        'merge': '合并派车单'
      }
      return labels[action] || '操作'
    }
    
    // 加载吨位选项和映射关系
    const loadTonnageData = async () => {
      try {
        console.log('loadTonnageData - 开始加载吨位数据')
        // 获取标准吨位选项
        tonnageOptions.value = tonnageVolumeService.getStandardTonnageOptions()
        console.log('loadTonnageData - 标准吨位选项:', tonnageOptions.value)
        
        // 获取吨位容积映射关系
        const mappingResult = await tonnageVolumeService.getActiveMappings()
        console.log('loadTonnageData - API响应:', mappingResult)
        
        if (mappingResult.code === 200 && mappingResult.data) {
          // 直接使用API返回的数组数据，包含完整的映射信息
          tonnageVolumeMapping.value = mappingResult.data.map(mapping => ({
            tonnage: parseInt(mapping.tonnage),
            min_volume: parseFloat(mapping.min_volume),
            standard_volume: parseFloat(mapping.standard_volume),
            max_volume: parseFloat(mapping.max_volume)
          }))
          console.log('loadTonnageData - 映射关系加载成功:', tonnageVolumeMapping.value)
        } else {
          console.error('loadTonnageData - API返回错误:', mappingResult)
        }
      } catch (error) {
        console.error('加载吨位数据失败:', error)
      }
    }
    
    // 添加车辆
    const handleAddVehicle = async () => {
      console.log('handleAddVehicle - 开始执行，当前mergeVehicles长度:', verificationForm.mergeVehicles.length)
      
      const existingVehicles = [
        ...(task.value.vehicles || []),
        ...verificationForm.mergeVehicles
      ]

      // 检查合并车辆数量限制（最多1辆）
      if (verificationForm.mergeVehicles.length >= 1) {
        console.log('handleAddVehicle - 车辆数量已达上限')
        ElMessage.warning('合并车辆最多只能添加1辆')
        return
      }

      // 优先使用选中的列表车辆
      if (selectedVehicleFromList.value) {
        console.log('handleAddVehicle - 使用选中的列表车辆:', selectedVehicleFromList.value)
        const v = selectedVehicleFromList.value
        const isDuplicate = existingVehicles.some(vehicle => 
          vehicle.license_plate === v.license_plate
        )
        if (isDuplicate) {
          ElMessage.warning('该车牌号已存在，请勿重复添加')
          return
        }
        
        const newVehicle = {
          license_plate: v.license_plate,
          carriage_number: v.carriage_number || '',
          actual_volume: v.actual_volume || v.standard_volume,
          vehicle_type: (() => {
            // 处理吨位数据，确保格式一致
            let tonnageValue = v.vehicle_type || v.original_capacity
            if (tonnageValue) {
              // 如果是字符串，提取数字部分
              if (typeof tonnageValue === 'string') {
                const match = tonnageValue.match(/(\d+(?:\.\d+)?)/);
                return match ? `${match[1]}吨` : tonnageValue;
              } else if (typeof tonnageValue === 'number') {
                return `${tonnageValue}吨`;
              }
            }
            return tonnageValue
          })()
        }
        
        console.log('handleAddVehicle - 准备添加车辆:', newVehicle)
        verificationForm.mergeVehicles.push(newVehicle)
        console.log('handleAddVehicle - 添加后mergeVehicles长度:', verificationForm.mergeVehicles.length)
        console.log('handleAddVehicle - 添加后mergeVehicles内容:', verificationForm.mergeVehicles)
        
        resetAddVehicleForm()
        selectedVehicleFromList.value = null
        showAddVehicleDialog.value = false
        ElMessage.success('车辆添加成功')
        return
      }

      // 无选择时校验手动输入
      if (!addVehicleFormRef.value) return
      try {
        await addVehicleFormRef.value.validate()
      } catch (e) {
        return
      }
      const isDuplicate = existingVehicles.some(vehicle => 
        vehicle.license_plate === addVehicleForm.license_plate
      )
      if (isDuplicate) {
        ElMessage.warning('该车牌号已存在，请勿重复添加')
        return
      }
      
      const newVehicle = {
        license_plate: addVehicleForm.license_plate,
        carriage_number: addVehicleForm.carriage_number || '',
        actual_volume: addVehicleForm.actual_volume,
        vehicle_type: addVehicleForm.vehicle_type
      }
      
      console.log('handleAddVehicle - 准备添加手动输入车辆:', newVehicle)
      verificationForm.mergeVehicles.push(newVehicle)
      console.log('handleAddVehicle - 添加后mergeVehicles长度:', verificationForm.mergeVehicles.length)
      console.log('handleAddVehicle - 添加后mergeVehicles内容:', verificationForm.mergeVehicles)
      
      resetAddVehicleForm()
      showAddVehicleDialog.value = false
      ElMessage.success('车辆添加成功')
    }
    
    // 删除合并车辆
    const removeMergeVehicle = (index) => {
      console.log('removeMergeVehicle - 删除前mergeVehicles长度:', verificationForm.mergeVehicles.length)
      console.log('removeMergeVehicle - 删除前mergeVehicles内容:', verificationForm.mergeVehicles)
      console.log('removeMergeVehicle - 删除索引:', index)
      
      verificationForm.mergeVehicles.splice(index, 1)
      
      console.log('removeMergeVehicle - 删除后mergeVehicles长度:', verificationForm.mergeVehicles.length)
      console.log('removeMergeVehicle - 删除后mergeVehicles内容:', verificationForm.mergeVehicles)
      
      ElMessage.success('车辆删除成功')
    }
    
    // 加载可用车辆列表
    const loadAvailableVehicles = async (retryCount = 0) => {
      vehicleListLoading.value = true
      
      try {
        // 如果权限未初始化，尝试重新初始化
        if (!permissionStore.userInfo && retryCount < 2) {
          console.log('权限信息未初始化，尝试重新加载...')
          await permissionStore.initializeFromToken()
        }
        
        // 检查权限
        if (!permissionStore.hasPermission('vehicle:read')) {
          // 如果是管理员或权限检查失败但重试次数未达上限，允许一次重试
          if (permissionStore.isAdmin || (retryCount < 1 && permissionStore.userInfo)) {
            console.log('权限检查失败，尝试重试...')
            vehicleListLoading.value = false
            return await loadAvailableVehicles(retryCount + 1)
          }
          
          ElMessage.error('没有权限查看车辆列表')
          return
        }
        
        const res = await vehicleCapacityReferenceService.getAvailableVehicles()
        if (res && res.code === 0) {
          const list = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.items) ? res.data.items : [])
          availableVehicles.value = list.map(vehicle => ({
            ...vehicle,
            displayText: `${vehicle.license_plate} - ${vehicle.carriage_number} (${vehicle.vehicle_type}吨)`
          }))
        } else {
          ElMessage.warning(res?.message || '获取车辆列表失败')
          availableVehicles.value = []
        }
      } catch (error) {
        console.error('加载车辆列表失败:', error)
        
        // 如果是权限错误且还有重试机会，尝试重新初始化权限
        if ((error.code === 401 || error.code === 403) && retryCount < 1) {
          console.log('权限错误，尝试重新初始化权限...')
          try {
            await permissionStore.refreshPermissions()
            vehicleListLoading.value = false
            return await loadAvailableVehicles(retryCount + 1)
          } catch (refreshError) {
            console.error('权限刷新失败:', refreshError)
          }
        }
        
        ElMessage.error(error?.message || '加载车辆列表失败')
        availableVehicles.value = []
      } finally {
        vehicleListLoading.value = false
      }
    }
    
    // 处理车辆选择
    const handleVehicleSelect = (vehicle) => {
      selectedVehicleFromList.value = vehicle
      if (vehicle) {
        console.log('handleVehicleSelect - 选择的车辆数据:', vehicle)
        
        // 自动填充表单数据，优先使用actual_volume，如果没有则使用standard_volume
        addVehicleForm.license_plate = vehicle.license_plate
        addVehicleForm.carriage_number = vehicle.carriage_number
        
        // 处理容积：优先使用actual_volume，如果没有则使用standard_volume
        const volumeValue = vehicle.actual_volume || vehicle.standard_volume
        addVehicleForm.actual_volume = typeof volumeValue === 'number' ? volumeValue : parseFloat(volumeValue) || null
        
        // 处理吨位：优先使用vehicle_type，如果没有则使用original_capacity
        let tonnageValue = vehicle.vehicle_type || vehicle.original_capacity
        if (tonnageValue) {
          // 如果是字符串，提取数字部分
          if (typeof tonnageValue === 'string') {
            const match = tonnageValue.match(/(\d+(?:\.\d+)?)/);
            tonnageValue = match ? `${match[1]}吨` : tonnageValue;
          } else if (typeof tonnageValue === 'number') {
            tonnageValue = `${tonnageValue}吨`;
          }
        }
        addVehicleForm.vehicle_type = tonnageValue
        
        console.log('handleVehicleSelect - 填充后的表单数据:', {
          license_plate: addVehicleForm.license_plate,
          carriage_number: addVehicleForm.carriage_number,
          actual_volume: addVehicleForm.actual_volume,
          vehicle_type: addVehicleForm.vehicle_type
        })
      }
    }
    
    // 处理选项卡切换
    const handleTabChange = (tabName) => {
      addVehicleTabActive.value = tabName
      selectedVehicleFromList.value = null
      resetAddVehicleForm()
      
      // 如果切换到选择车辆选项卡，加载车辆列表
      if (tabName === 'select' && availableVehicles.value.length === 0) {
        loadAvailableVehicles()
      }
    }
    
    // 重置添加车辆表单
    const resetAddVehicleForm = () => {
      if (addVehicleFormRef.value) {
        addVehicleFormRef.value.resetFields()
      }
      addVehicleForm.license_plate = ''
      addVehicleForm.carriage_number = ''
      addVehicleForm.actual_volume = null
      addVehicleForm.vehicle_type = ''
    }
    
    // 关闭添加车辆对话框
    const handleCloseAddVehicleDialog = () => {
      resetAddVehicleForm()
      selectedVehicleFromList.value = null
      addVehicleTabActive.value = 'select'
      showAddVehicleDialog.value = false
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        '待核查': 'warning',
        '待审核': 'info',
        '待响应': 'primary',
        '审核通过': 'success',
        '已完成': 'success',
        '已取消': 'danger'
      }
      return statusMap[status] || 'info'
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

    // 组件挂载时获取任务详情
    onMounted(() => {
      // 添加一个短暂的延迟，确保页面完全加载后再获取任务详情
      setTimeout(() => {
        fetchTaskDetail()
        loadTonnageData()
      }, 100)
    })

    // 监听添加车辆对话框的打开，自动加载可用车辆
    watch(showAddVehicleDialog, (visible) => {
      if (visible && addVehicleTabActive.value === 'select' && availableVehicles.value.length === 0) {
        loadAvailableVehicles()
      }
    })

    return {
      loading,
      submitting,
      task,
      verificationForm,
      // 附件相关状态
      attachments,
      imageFileList,
      docFileList,
      mergeBeforeImageFileList,
      mergeNewImageFileList,
      downgradeImageFileList,
      // 上传处理方法
      beforeUploadImage,
      handleImageSuccess,
      handleImageRemove,
      beforeUploadDoc,
      handleDocSuccess,
      handleDocRemove,
      beforeUploadMergeBeforeImage,
      handleMergeBeforeImageSuccess,
      handleMergeBeforeImageRemove,
      beforeUploadMergeNewImage,
      handleMergeNewImageSuccess,
      handleMergeNewImageRemove,
      beforeUploadDowngradeImage,
      handleDowngradeImageSuccess,
      handleDowngradeImageRemove,
      authService,
      verificationFormRef,
      verificationRules,
      allowedTonnageOptions,
      formattedRequiredWeight,
      isTonnageMismatch,
      hasTonnageMismatch,
      canVerifyPass,
      isBusinessTypeRestricted,
      showAddVehicleDialog,
      addVehicleForm,
      addVehicleFormRef,
      addVehicleRules,
      tonnageOptions,
      totalMergedVolume,
      mergedTonnage,
      getMergedTonnageValue,
      isOverRequiredWeight,
      getRequiredWeightValue,
      // 车辆选择相关
      addVehicleTabActive,
      availableVehicles,
      selectedVehicleFromList,
      vehicleListLoading,
      // 列表搜索与分页
      searchQuery,
      pageSize,
      currentPage,
      filteredVehicles,
      paginatedVehicles,
      handleActionChange,
      fetchTaskDetail,
      submitVerification,
      resetForm,
      goBack,
      getActionLabel,
      getStatusType,
      // 显示格式化方法
      formatVolume,
      formatTonnage,
      formatDateTime,
      loadTonnageData,
      handleAddVehicle,
      removeMergeVehicle,
      resetAddVehicleForm,
      handleCloseAddVehicleDialog,
      // 车辆选择相关方法
      loadAvailableVehicles,
      handleVehicleSelect,
      handleTabChange
    }
  }
}
</script>

<style scoped>
.workshop-verification-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #409eff;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  background: #ecf5ff;
}

.back-button:hover {
  color: #337ecc;
  background: #d9ecff;
  transform: translateY(-1px);
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.task-info-card,
.verification-card,
.history-card,
.vehicle-info-card {
  margin-bottom: 24px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  overflow: hidden;
  transition: all 0.3s ease;
}

.task-info-card:hover,
.verification-card:hover,
.history-card:hover,
.vehicle-info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.task-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  padding: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.info-item:hover {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  padding-left: 8px;
  padding-right: 8px;
}

.info-item.full-width {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  padding: 16px;
  border: none;
}

.info-item label {
  font-weight: 600;
  color: #409eff;
  min-width: 100px;
  margin-right: 12px;
  font-size: 14px;
}

.info-item span {
  color: #303133;
  word-break: break-all;
  font-weight: 500;
}

.verification-form {
  max-width: 700px;
  padding: 24px;
}

.merge-vehicles-section {
  border: 2px solid rgba(64, 158, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  background: rgba(64, 158, 255, 0.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.merge-vehicles-section h4 {
  margin: 0 0 16px 0;
  color: #409eff;
  font-size: 16px;
  font-weight: 700;
}

.current-vehicles,
.additional-vehicles {
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 10px;
  border: 1px solid rgba(64, 158, 255, 0.15);
}

.additional-vehicles:last-child {
  margin-bottom: 0;
}

.merge-vehicle-table {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-vehicles {
  text-align: center;
  color: #409eff;
  padding: 32px;
  font-size: 16px;
  font-weight: 500;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 8px;
  border: 2px dashed rgba(64, 158, 255, 0.3);
}

.merge-summary {
  border-top: 2px solid rgba(64, 158, 255, 0.2);
  padding-top: 20px;
  margin-top: 20px;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.merge-summary h4 {
  margin: 0 0 16px 0;
  color: #409eff;
  font-size: 16px;
  font-weight: 700;
}

.summary-info {
  display: flex;
  align-items: center;
  font-size: 15px;
  color: #303133;
  font-weight: 500;
}

.summary-info span {
  font-weight: 600;
  color: #409eff;
}

.form-tip {
  font-size: 13px;
  color: #409eff;
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.form-tip.warning-tip {
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.1);
  border-left-color: #e53e3e;
}

.history-item {
  padding: 16px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.15);
  transition: all 0.3s ease;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(31, 38, 135, 0.2);
}

.history-status {
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
  font-size: 15px;
}

.history-operator {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
  font-weight: 500;
}

.history-note {
  font-size: 14px;
  color: #606266;
  background: rgba(64, 158, 255, 0.05);
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

/* 车辆信息表格样式 */
.vehicle-table {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(31, 38, 135, 0.15);
}

/* 吨位不一致高亮样式 */
.tonnage-mismatch {
  color: #e53e3e;
  font-weight: 700;
  background: linear-gradient(135deg, rgba(229, 62, 62, 0.1) 0%, rgba(229, 62, 62, 0.05) 100%);
  padding: 4px 12px;
  border-radius: 8px;
  border: 2px solid rgba(229, 62, 62, 0.3);
  box-shadow: 0 2px 8px rgba(229, 62, 62, 0.2);
}

/* 吨位不一致警告样式 */
.tonnage-warning {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(229, 62, 62, 0.1) 0%, rgba(229, 62, 62, 0.05) 100%);
  border-radius: 12px;
  border: 2px solid rgba(229, 62, 62, 0.2);
}

/* 上传区域样式优化 */
.upload-section {
  padding: 20px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 2px dashed rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.upload-section:hover {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.08);
}

.attachment-upload {
  padding: 20px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 2px solid rgba(102, 126, 234, 0.2);
}

.upload-group {
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.upload-group label {
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .workshop-verification-container {
    padding: 12px;
  }
  
  .page-header {
    padding: 16px;
    margin-bottom: 16px;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .task-info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .verification-form {
    max-width: 100%;
    padding: 16px;
  }
  
  .merge-vehicles-section {
    padding: 16px;
  }
  
  .upload-section,
  .attachment-upload {
    padding: 16px;
  }
}

/* 按钮样式优化 */
.el-button--primary {
  background: #409eff;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
}

.el-button--primary:hover {
  background: #337ecc;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.el-button--success {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(72, 187, 120, 0.3);
}

.el-button--success:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.4);
}

.el-button--danger {
  background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(229, 62, 62, 0.3);
}

.el-button--danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(229, 62, 62, 0.4);
}

/* 表单控件样式优化 */
.el-input__wrapper {
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
}

.el-input__wrapper:hover {
  border-color: rgba(64, 158, 255, 0.4);
}

.el-input__wrapper.is-focus {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.el-select .el-input__wrapper {
  border-radius: 8px;
}

.el-card {
  border-radius: 12px;
  border: 2px solid rgba(64, 158, 255, 0.15);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
</style>