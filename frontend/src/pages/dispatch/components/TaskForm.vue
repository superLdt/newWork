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
        </el-radio-group>
        <div style="font-size: 12px; color: #909399; margin-top: 5px;">
          <span v-if="formData.business_type === '委办派车'">委托外部供应商提供车辆和司机服务</span>
          <span v-if="formData.business_type === '自办派车'">使用自有车辆和司机执行运输任务</span>
        </div>
      </el-form-item>
      
      <el-form-item label="需求日期" prop="required_date">
        <el-date-picker
          v-model="formData.required_date"
          type="datetime"
          placeholder="选择需求日期和时间"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
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
      
      <el-form-item label="标准吨位" prop="standard_weight">
        <el-select v-model="formData.standard_weight" placeholder="请选择标准吨位" @change="handleWeightChange">
          <el-option label="5吨 (≥35m³)" value="5吨"></el-option>
          <el-option label="8吨 (≥45m³)" value="8吨"></el-option>
          <el-option label="12吨 (≥55m³)" value="12吨"></el-option>
          <el-option label="20吨 (≥100m³)" value="20吨"></el-option>
          <el-option label="30吨 (≥130m³)" value="30吨"></el-option>
          <el-option label="40吨A (≥150m³)" value="40吨A"></el-option>
          <el-option label="40吨B (≥180m³)" value="40吨B"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="标准容积(m³)" prop="standard_volume">
        <el-input-number 
          v-model="formData.standard_volume" 
          :min="0" 
          :precision="0"
          controls-position="right"
        ></el-input-number>
      </el-form-item>
      
      <el-form-item label="实际需求容积(m³)" prop="actual_volume">
        <el-input-number 
          v-model="formData.actual_volume" 
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
      
      <el-form-item label="发起人部门" prop="initiator_department">
        <el-input v-model="formData.initiator_department" placeholder="请输入发起人部门"></el-input>
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
import { usePermissionStore } from '@/stores/permission'
import { dispatchUnitService } from '@/services/dispatchUnitService'
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
    
    // 吨位-容积映射表（标准吨位≥标准容积）
     const weightVolumeMap = {
       '5吨': 35,    // 5吨 ≥ 35m³
       '8吨': 45,    // 8吨 ≥ 45m³
       '12吨': 55,   // 12吨 ≥ 55m³
       '20吨': 100,  // 20吨 ≥ 100m³
       '30吨': 130,  // 30吨 ≥ 130m³
       '40吨A': 150, // 40吨A ≥ 150m³
       '40吨B': 180  // 40吨B ≥ 180m³
     }

    // 归一化需求日期到 Date 或 null
    const normalizeRequiredDate = (val) => {
      if (val === undefined || val === null) return null
      if (typeof val === 'string') {
        const v = val.trim()
        if (v === '' || v.toLowerCase() === 'invalid date' || v.toLowerCase() === 'nan') return null
        // YYYY-MM-DD HH:mm:ss
        if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(v)) return new Date(v.replace(' ', 'T'))
        // YYYY-MM-DD HH:mm
        if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(v)) return new Date(v.replace(' ', 'T') + ':00')
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
      standard_weight: props.task?.standard_weight || '',
      standard_volume: props.task?.standard_volume || 0,
      actual_volume: props.task?.actual_volume || 0,
      special_requirements: props.task?.special_requirements || '',
      initiator_department: props.task?.initiator_department || '',
      audit_required: props.task?.audit_required !== undefined ? props.task.audit_required : false
    })

    // 吨位选择变化处理
     const handleWeightChange = (value) => {
       if (value && weightVolumeMap[value]) {
         formData.standard_volume = weightVolumeMap[value]
         // 如果实际容积小于标准容积，自动更新实际容积
         if (formData.actual_volume < weightVolumeMap[value]) {
           formData.actual_volume = weightVolumeMap[value]
         }
       } else {
         formData.standard_volume = 0
       }
     }
     
     // 监听标准吨位变化，自动设置标准容积
     watch(() => formData.standard_weight, (newWeight) => {
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
             // 自办派车只能选择内部单位或外包驾驶管理公司
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
         // 自办派车只显示内部单位或外包驾驶管理公司
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
      standard_weight: [
        { required: true, message: '请选择标准吨位', trigger: 'change' }
      ],
      standard_volume: [
        { required: true, message: '标准容积自动计算', trigger: 'change' }
      ],
      actual_volume: [
        { required: true, message: '请输入实际需求容积', trigger: 'blur' }
      ]
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid, fields) => {
        if (valid) {
          // 格式化日期时间为 'YYYY-MM-DD HH:mm:ss'
          const formatDateTime = (val) => {
            if (!val) return ''
            if (typeof val === 'string') {
              return val
            }
            const d = new Date(val)
            const pad = (n) => String(n).padStart(2, '0')
            const y = d.getFullYear()
            const m = pad(d.getMonth() + 1)
            const day = pad(d.getDate())
            const h = pad(d.getHours())
            const mi = pad(d.getMinutes())
            const s = pad(d.getSeconds())
            return `${y}-${m}-${day} ${h}:${mi}:${s}`
          }

          // 整理表单数据，由父组件提交并处理消息
          const taskData = {
            ...formData,
            required_date: formatDateTime(formData.required_date),
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
        handleOrganizingUnitChange
     }
  }
}
</script>

<style scoped>
.task-form-container {
  padding: 20px;
}
</style>