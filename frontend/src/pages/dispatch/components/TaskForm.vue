<template>
  <div class="task-form-container">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      label-position="right"
    >
      <!-- 业务类型选择 -->
      <el-form-item label="业务类型" prop="business_type">
        <el-radio-group v-model="formData.business_type" @change="handleBusinessTypeChange">
          <el-radio-button label="委办派车">委办派车</el-radio-button>
          <el-radio-button label="自办派车">自办派车</el-radio-button>
          <el-radio-button label="大容积派车">大容积派车</el-radio-button>
        </el-radio-group>
        <div style="font-size: 12px; color: #909399; margin-top: 5px;">
          <span v-if="formData.business_type === '委办派车'">委托外部供应商提供车辆和司机服务</span>
          <span v-if="formData.business_type === '自办派车'">使用自有车辆和司机执行运输任务</span>
          <span v-if="formData.business_type === '大容积派车'">委托大容积供应商提供车辆和司机服务</span>
        </div>
      </el-form-item>
      
      <el-form-item label="需求日期" prop="required_date">
        <el-date-picker
          v-model="formData.required_date"
          type="date"
          placeholder="选择需求日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        ></el-date-picker>
      </el-form-item>
      
      <el-form-item label="始发局" prop="origin_bureau">
        <el-input v-model="formData.origin_bureau" placeholder="请输入始发局"></el-input>
      </el-form-item>
      
      <el-form-item label="邮路名称" prop="mail_route_name">
        <el-input v-model="formData.mail_route_name" placeholder="请输入邮路名称"></el-input>
      </el-form-item>
      
      <el-form-item label="组开单位" prop="organizing_unit_id">
        <el-select v-model="formData.organizing_unit_id" placeholder="请选择组开单位" @change="handleOrganizingUnitChange">
          <el-option
            v-for="unit in filteredDispatchUnits"
            :key="unit.id"
            :label="unit.name"
            :value="unit.id"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="运输类型" prop="transport_type">
        <el-select v-model="formData.transport_type" placeholder="请选择运输类型">
          <el-option label="单程" value="单程"></el-option>
          <el-option label="往返" value="往返"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="需求类型" prop="requirement_type">
        <el-select v-model="formData.requirement_type" placeholder="请选择需求类型">
          <el-option label="正班" value="正班"></el-option>
          <el-option label="加班" value="加班"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="需求吨位" prop="required_weight">
        <el-select v-model="formData.required_weight" placeholder="请选择需求吨位" @change="handleWeightChange">
          <el-option 
            v-for="option in tonnageOptions" 
            :key="option.value" 
            :label="option.label" 
            :value="option.value"
          ></el-option>
        </el-select>
        <div v-if="selectedTonnageVolumeRange" style="font-size: 12px; color: #909399; margin-top: 5px;">
          容积区间: {{ selectedTonnageVolumeRange }}
        </div>
      </el-form-item>
      
      <el-form-item label="需求容积(m³)" prop="required_volume">
        <el-input-number 
          v-model="formData.required_volume" 
          :min="0" 
          :precision="0"
          controls-position="right"
          :disabled="actualVolumeDisabled"
          style="width: 100%"
        ></el-input-number>
        <div v-if="actualVolumeDisabled" style="font-size: 12px; color: #909399; margin-top: 5px;">
          实际容积由车间地调在发车环节确认时填写
        </div>
      </el-form-item>
      
      <el-form-item label="特殊要求" prop="special_requirements">
        <el-input 
          v-model="formData.special_requirements" 
          type="textarea" 
          rows="3"
          placeholder="请输入特殊要求"
        ></el-input>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { usePermissionStore } from '@/stores/permission'
import { dispatchUnitService } from '@/services/dispatchUnitService'
import tonnageVolumeService from '@/services/tonnageVolumeService'
import dayjs from 'dayjs'

export default {
  name: 'TaskForm',
  props: {
    task: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const permissionStore = usePermissionStore()
    const dispatchUnits = ref([])
    const tonnageVolumeData = ref({}) // 存储吨位容积数据
    
    // 获取当前用户角色
    const currentUserRole = computed(() => {
      if (permissionStore.roles && permissionStore.roles.length > 0) {
        return permissionStore.roles[0] // 返回第一个角色
      }
      return '' // 默认无角色
    })
    
    // 实际容积字段是否禁用（仅车间地调角色可编辑）
    const actualVolumeDisabled = computed(() => {
      const role = currentUserRole.value
      return role !== '车间地调'
    })
    
    // 格式化需求吨位显示
    const formatRequiredWeight = (weight) => {
      if (!weight) return ''
      // 移除重复的"吨"字，如"40吨A吨"改为"40吨A"，"8吨吨"改为"8吨"
      return weight.replace(/吨.*吨$/, '吨')
    }
    
    // 吨位选项（包含容积区间信息）
    const tonnageOptions = computed(() => {
      const options = tonnageVolumeService.getStandardTonnageOptions()
      return options.map(option => {
        // 获取该吨位对应的容积数据
        const volumeData = tonnageVolumeData.value[option.value]
        if (volumeData) {
          const minVolume = volumeData.min_volume
          const maxVolume = volumeData.max_volume
          let volumeRange = ''
          if (maxVolume === null) {
            volumeRange = `${minVolume}m³以上`
          } else {
            volumeRange = `${minVolume}-${maxVolume}m³`
          }
          return {
            ...option,
            label: `${formatRequiredWeight(option.label)} (容积区间: ${volumeRange})`
          }
        }
        return {
          ...option,
          label: formatRequiredWeight(option.label)
        }
      })
    })
    
    // 选中吨位对应的容积区间
    const selectedTonnageVolumeRange = computed(() => {
      if (!formData.required_weight) return ''
      
      const volumeData = tonnageVolumeData.value[formData.required_weight]
      if (volumeData) {
        const minVolume = volumeData.min_volume
        const maxVolume = volumeData.max_volume
        if (maxVolume === null) {
          return `${minVolume}m³以上`
        }
        return `${minVolume}-${maxVolume}m³`
      }
      return ''
    })
    
    // 归一化需求日期到 Date 或 null
    const normalizeRequiredDate = (val) => {
      if (val === undefined || val === null) return null
      if (typeof val === 'string') {
        const v = val.trim()
        if (v === '' || v.toLowerCase() === 'invalid date' || v.toLowerCase() === 'nan') return null
        // YYYY-MM-DD
        if (/^\d{4}-\d{2}-\d{2}$/.test(v)) return new Date(v)
        const d = new Date(v)
        return isNaN(d.getTime()) ? null : d
      }
      if (val instanceof Date) {
        return isNaN(val.getTime()) ? null : val
      }
      return null
    }
    
    // 表单数据
    const formData = reactive({
      business_type: props.task?.business_type || '委办派车',
      required_date: normalizeRequiredDate(props.task?.required_date),
      origin_bureau: props.task?.origin_bureau || '',
      mail_route_name: props.task?.mail_route_name || '',
      organizing_unit: props.task?.organizing_unit || '',
      organizing_unit_id: props.task?.organizing_unit_id || null,
      transport_type: props.task?.transport_type || '',
      requirement_type: props.task?.requirement_type || '',
      required_weight: props.task?.required_weight || '',
      required_volume: props.task?.required_volume || 0,
      actual_weight: props.task?.actual_weight || '',
      actual_volume: props.task?.actual_volume || 0,
      special_requirements: props.task?.special_requirements || '',
      audit_required: props.task?.audit_required !== undefined ? props.task.audit_required : false
    })

    // 加载吨位容积数据
    const loadTonnageVolumeData = async () => {
      try {
        const response = await tonnageVolumeService.getActiveMappings()
        if (response && response.data) {
          // 确保response.data是数组格式
          let dataArray = []
          if (Array.isArray(response.data)) {
            dataArray = response.data
          } else if (response.data.items && Array.isArray(response.data.items)) {
            dataArray = response.data.items
          } else {
            console.warn('吨位容积数据格式不正确:', response.data)
            return
          }
          
          // 将数据转换为以吨位为键的对象
          const data = {}
          dataArray.forEach(item => {
            data[item.tonnage] = item
          })
          tonnageVolumeData.value = data
        }
      } catch (error) {
        console.error('获取吨位容积数据失败:', error)
        ElMessage.warning('获取吨位容积数据失败')
      }
    }

    // 吨位选择变化处理
    const handleWeightChange = async (value) => {
      if (value) {
        try {
          // 使用API获取吨位对应的容积信息
          const response = await tonnageVolumeService.getVolumeByTonnage(value)
          if (response.success && response.data) {
            // 直接更新需求容积为对应的标准容积
            formData.required_volume = response.data.standard_volume
          } else {
            // 如果API调用失败，使用本地映射作为备选
            const localMapping = getLocalWeightVolumeMapping()
            if (localMapping[value]) {
              formData.required_volume = localMapping[value]
            }
          }
        } catch (error) {
          console.error('获取吨位容积映射失败:', error)
          ElMessage.warning('获取吨位容积映射失败，使用默认值')
          // API调用失败时使用本地映射
          const localMapping = getLocalWeightVolumeMapping()
          if (localMapping[value]) {
            formData.required_volume = localMapping[value]
          }
        }
      }
    }

    // 获取本地吨位-容积映射（作为备选方案）
    const getLocalWeightVolumeMapping = () => {
      return {
        '5吨': 35,
        '8吨': 45,
        '12吨': 55,
        '20吨': 100,
        '30吨': 130,
        '40吨A': 150,
        '40吨B': 180
      }
    }
    
    // 监听需求吨位变化，自动设置需求容积
    watch(() => formData.required_weight, (newWeight) => {
      handleWeightChange(newWeight)
    })
    
    // 业务类型变化处理
    const handleBusinessTypeChange = (value) => {
      console.log('业务类型变更为:', value)
      
      // 切换业务类型时，检查当前选择的组开单位是否符合新的过滤条件
      if (formData.organizing_unit_id) {
        const currentUnit = dispatchUnits.value.find(unit => unit.id === formData.organizing_unit_id)
        if (currentUnit) {
          if (value === '自办派车') {
            // 自办派车只能选择内部单位或大容积供应商
            if (currentUnit.unit_type !== '内部单位' && currentUnit.unit_type !== '外包驾驶管理公司') {
              formData.organizing_unit_id = null
              formData.organizing_unit = ''
            }
          }
        }
      }
      
      // 根据业务类型调整其他字段的默认值或显示逻辑
      if (value === '自办派车') {
        // 自办派车的特殊处理逻辑
        if (!formData.organizing_unit) {
          formData.organizing_unit = '自办车队'
        }
      } else {
        // 委办派车的特殊处理逻辑
        if (!formData.organizing_unit) {
          formData.organizing_unit = ''
        }
      }
    }

    // 根据角色自动设置审核需求
    const setAuditRequiredByRole = () => {
      const role = currentUserRole.value
      if (role === '车间地调') {
        formData.audit_required = true // 车间地调需要审核
      } else if (role === '区域调度员') {
        formData.audit_required = false // 区域调度员不需要审核
      }
    }

    // 加载调度单位列表
    const loadDispatchUnits = async () => {
      try {
        const response = await dispatchUnitService.getActiveDispatchUnits()
        if (response.code === 0) {
          dispatchUnits.value = response.data || []
        } else {
          console.error('加载调度单位失败:', response.message)
        }
      } catch (error) {
        console.error('加载调度单位失败:', error)
      }
    }
    
    // 根据业务类型过滤组开单位
    const filteredDispatchUnits = computed(() => {
      if (formData.business_type === '自办派车') {
        // 自办派车只显示内部单位或大容积供应商
        return dispatchUnits.value.filter(unit => 
          unit.unit_type === '内部单位' || unit.unit_type === '外包驾驶管理公司'
        )
      } else {
        // 委办派车显示所有单位
        return dispatchUnits.value
      }
    })
    
    // 组开单位变化处理
    const handleOrganizingUnitChange = (unitId) => {
      const selectedUnit = dispatchUnits.value.find(unit => unit.id === unitId)
      if (selectedUnit) {
        formData.organizing_unit = selectedUnit.name
      }
    }

    // 组件挂载时设置审核需求和加载数据
    onMounted(() => {
      setAuditRequiredByRole()
      loadDispatchUnits()
      loadTonnageVolumeData()
    })
    
    // 表单验证规则
    const rules = {
      business_type: [
        { required: true, message: '请选择业务类型', trigger: 'change' }
      ],
      required_date: [
        { required: true, message: '请选择需求日期', trigger: 'change' }
      ],
      origin_bureau: [
        { required: true, message: '请输入始发局', trigger: 'blur' }
      ],
      mail_route_name: [
        { required: true, message: '请输入邮路名称', trigger: 'blur' }
      ],
      organizing_unit_id: [
        { required: true, message: '请选择组开单位', trigger: 'change' }
      ],
      transport_type: [
        { required: true, message: '请选择运输类型', trigger: 'change' }
      ],
      requirement_type: [
        { required: true, message: '请选择需求类型', trigger: 'change' }
      ],
      required_weight: [
        { required: true, message: '请选择需求吨位', trigger: 'change' }
      ],
      required_volume: [
        { required: true, message: '请输入实际需求容积', trigger: 'blur' }
      ]
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid, fields) => {
        if (valid) {
          // 整理表单数据，由父组件提交并处理消息
          const taskData = {
            ...formData,
            status: '待审核',
            dispatch_track: '轨道B',
            initiator_role: '车间地调',
            initiator_user_id: 1,
            current_handler_role: '审核员'
          }
          emit('submit', taskData)
        } else {
          console.log('表单验证失败', fields)
        }
      })
    }
    
    // 取消操作
    const cancel = () => {
      emit('cancel')
    }
    
    return {
      formRef,
      formData,
      rules,
      submitForm,
      cancel,
      actualVolumeDisabled,
      handleWeightChange,
      handleBusinessTypeChange,
      dispatchUnits,
      filteredDispatchUnits,
      handleOrganizingUnitChange,
      tonnageOptions,
      selectedTonnageVolumeRange
    }
  }
}
</script>

<style scoped>
.task-form-container {
  padding: 20px;
}
</style>