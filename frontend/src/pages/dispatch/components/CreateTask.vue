<template>
  <div class="create-task-container">
    <el-form :model="taskForm" label-width="120px" :rules="rules" ref="taskFormRef">
      <el-form-item label="需求日期" prop="required_date">
        <el-date-picker
          v-model="taskForm.required_date"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        ></el-date-picker>
      </el-form-item>
      
      <el-form-item label="始发局" prop="origin_bureau">
        <el-select v-model="taskForm.origin_bureau" placeholder="请选择始发局" style="width: 100%">
          <el-option
            v-for="item in bureauOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="邮路名称" prop="mail_route_name">
        <el-input
          v-model="taskForm.mail_route_name"
          placeholder="请输入邮路名称"
          style="width: 100%"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="组开单位（承运商）" prop="organizing_unit">
        <el-select v-model="taskForm.organizing_unit" placeholder="请选择组开单位" style="width: 100%">
          <el-option
            v-for="item in companyOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="运输类型" prop="transport_type">
        <el-select v-model="taskForm.transport_type" placeholder="请选择运输类型" style="width: 100%">
          <el-option
            v-for="item in transportTypeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="需求类型" prop="requirement_type">
        <el-select v-model="taskForm.requirement_type" placeholder="请选择需求类型" style="width: 100%">
          <el-option
            v-for="item in requirementTypeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="标准吨位" prop="standard_weight">
        <el-select v-model="taskForm.standard_weight" placeholder="请选择标准吨位" style="width: 100%" @change="handleWeightChange">
          <el-option
            v-for="item in weightOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="标准容积" prop="standard_volume">
        <el-input v-model="taskForm.standard_volume" disabled placeholder="自动计算" style="width: 100%">
          <template #append>m³</template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="实际需求容积" prop="actual_volume">
        <el-input-number 
          v-model="taskForm.actual_volume" 
          :min="0" 
          :precision="0" 
          :step="1" 
          :disabled="actualVolumeDisabled"
          style="width: 100%"
        >
          <template #append>m³</template>
        </el-input-number>
        <div v-if="actualVolumeDisabled" style="font-size: 12px; color: #909399; margin-top: 5px;">
          实际容积由车间地调在发车环节确认时填写
        </div>
      </el-form-item>
      
      <el-form-item label="派车轨道" prop="dispatch_track">
        <el-select v-model="taskForm.dispatch_track" placeholder="请选择派车轨道" style="width: 100%">
          <el-option
            v-for="item in trackOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="特殊要求" prop="special_requirements">
        <el-input
          v-model="taskForm.special_requirements"
          type="textarea"
          :rows="3"
          placeholder="请输入特殊要求或备注信息"
        ></el-input>
      </el-form-item>

      <el-form-item v-if="showAuditField" label="是否需要审核" prop="audit_required">
        <el-switch
          v-model="taskForm.audit_required"
          :disabled="true"
          active-text="需要审核"
          inactive-text="无需审核"
        ></el-switch>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { usePermissionStore } from '@/stores/permission'

export default {
  name: 'CreateTask',
  emits: ['create-success', 'cancel'],
  setup(props, { emit }) {
    const taskFormRef = ref(null)
    const permissionStore = usePermissionStore()
    
    // 获取当前用户角色
    const currentUserRole = computed(() => {
      if (permissionStore.roles && permissionStore.roles.length > 0) {
        return permissionStore.roles[0] // 返回第一个角色
      }
      return '' // 默认无角色
    })
    
    // 是否显示审核字段（区域调度员、超级管理员、车间地调显示，其他角色隐藏）
    const showAuditField = computed(() => {
      const role = currentUserRole.value
      return role === '区域调度员' || role === '超级管理员' || role === '车间地调'
    })
    
    // 实际容积字段是否禁用（仅车间地调角色可编辑）
    const actualVolumeDisabled = computed(() => {
      const role = currentUserRole.value
      return role !== '车间地调'
    })
    
    // 表单数据
    const taskForm = reactive({
      required_date: null,
      origin_bureau: '',
      mail_route_name: '',
      organizing_unit: '',
      transport_type: '',
      requirement_type: '',
      standard_weight: '',
      standard_volume: 0,
      actual_volume: 0,
      dispatch_track: '',
      special_requirements: '',
      audit_required: false // 是否需要审核
    })
    
    // 表单验证规则
    const rules = {
      required_date: [
        { required: true, message: '请选择需求日期', trigger: 'change' }
      ],
      origin_bureau: [
        { required: true, message: '请选择始发局', trigger: 'change' }
      ],
      mail_route_name: [
        { required: true, message: '请输入邮路名称', trigger: 'blur' },
        { min: 1, max: 100, message: '邮路名称长度1-100字符', trigger: 'blur' }
      ],
      organizing_unit: [
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
        { 
          required: true, 
          message: '请输入实际需求容积', 
          trigger: 'blur',
          validator: (rule, value, callback) => {
            if (actualVolumeDisabled.value) {
              // 如果字段被禁用，跳过验证
              callback()
            } else if (value === null || value === undefined || value === '') {
              callback(new Error('请输入实际需求容积'))
            } else if (value < 0) {
              callback(new Error('容积不能为负数'))
            } else {
              callback()
            }
          }
        }
      ],
      dispatch_track: [
        { required: true, message: '请选择派车轨道', trigger: 'change' }
      ],
      special_requirements: [
        { max: 200, message: '特殊要求不能超过200个字符', trigger: 'blur' }
      ],
      audit_required: [
        { required: false, message: '审核需求自动设置', trigger: 'change' }
      ]
    }
    
    // 始发局选项
    const bureauOptions = [
      { value: '北京', label: '北京' },
      { value: '上海', label: '上海' },
      { value: '广州', label: '广州' },
      { value: '深圳', label: '深圳' },
      { value: '成都', label: '成都' }
    ]
    
    // 组开单位选项
    const companyOptions = [
      { value: '中国邮政', label: '中国邮政' },
      { value: '中铁快运', label: '中铁快运' },
      { value: '顺丰速运', label: '顺丰速运' },
      { value: '中通快递', label: '中通快递' },
      { value: '圆通速递', label: '圆通速递' },
      { value: '申通快递', label: '申通快递' },
      { value: '韵达快递', label: '韵达快递' },
      { value: '京东物流', label: '京东物流' },
      { value: '德邦快递', label: '德邦快递' }
    ]
    
    // 路线名称选项
    const routeOptions = [
      { value: '京沪线', label: '京沪线' },
      { value: '京广线', label: '京广线' },
      { value: '沪深线', label: '沪深线' },
      { value: '广深线', label: '广深线' },
      { value: '成渝线', label: '成渝线' }
    ]
    
    // 运输类型选项
    const transportTypeOptions = [
      { value: '单程', label: '单程' },
      { value: '往返', label: '往返' }
    ]
    
    // 需求类型选项
    const requirementTypeOptions = [
      { value: '正班', label: '正班' },
      { value: '加班', label: '加班' }
    ]
    
    // 标准吨位选项
    const weightOptions = [
      { value: '5吨', label: '5吨 (≥35m³)' },
      { value: '8吨', label: '8吨 (≥45m³)' },
      { value: '12吨', label: '12吨 (≥55m³)' },
      { value: '20吨', label: '20吨 (≥100m³)' },
      { value: '30吨', label: '30吨 (≥130m³)' },
      { value: '40吨A', label: '40吨A (≥150m³)' },
      { value: '40吨B', label: '40吨B (≥180m³)' }
    ]
    
    // 吨位-容积映射（标准吨位≥标准容积）
    const weightVolumeMapping = {
      '5吨': 35,    // 5吨 ≥ 35m³
      '8吨': 45,    // 8吨 ≥ 45m³
      '12吨': 55,   // 12吨 ≥ 55m³
      '20吨': 100,  // 20吨 ≥ 100m³
      '30吨': 130,  // 30吨 ≥ 130m³
      '40吨A': 150, // 40吨A ≥ 150m³
      '40吨B': 180  // 40吨B ≥ 180m³
    }
    
    // 派车轨道选项
    const trackOptions = [
      { value: '1号轨道', label: '1号轨道' },
      { value: '2号轨道', label: '2号轨道' },
      { value: '3号轨道', label: '3号轨道' },
      { value: '4号轨道', label: '4号轨道' },
      { value: '5号轨道', label: '5号轨道' }
    ]
    
    // 吨位选择变化处理
    const handleWeightChange = (value) => {
      if (value && weightVolumeMapping[value]) {
        taskForm.standard_volume = weightVolumeMapping[value]
        // 如果实际容积小于标准容积，自动更新实际容积
        if (taskForm.actual_volume < weightVolumeMapping[value]) {
          taskForm.actual_volume = weightVolumeMapping[value]
        }
      } else {
        taskForm.standard_volume = 0
      }
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!taskFormRef.value) return
      
      await taskFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            // 模拟API调用，实际项目中应替换为真实API
            // const response = await fetch('/api/dispatch/tasks', {
            //   method: 'POST',
            //   headers: {
            //     'Content-Type': 'application/json'
            //   },
            //   body: JSON.stringify(taskForm)
            // })
            // 
            // if (!response.ok) {
            //   throw new Error('创建派车任务失败')
            // }
            // 
            // const data = await response.json()
            
            ElMessage.success('派车任务创建成功')
            emit('create-success', {
              ...taskForm,
              task_id: 'TASK' + Date.now().toString().slice(-6) // 模拟生成任务ID
            })
          } catch (error) {
            console.error('创建派车任务失败:', error)
            ElMessage.error('创建派车任务失败: ' + error.message)
          }
        } else {
          return false
        }
      })
    }
    
    // 重置表单
    const resetForm = () => {
      if (taskFormRef.value) {
        taskFormRef.value.resetFields()
      }
    }
    
    // 取消
    const cancel = () => {
      emit('cancel')
    }
    
    // 根据用户角色自动设置审核需求
    const setAuditRequiredByRole = () => {
      const role = currentUserRole.value
      
      if (role === '区域调度员' || role === '超级管理员') {
        // 区域调度员和超级管理员不需要审核
        taskForm.audit_required = false
      } else if (role === '车间地调') {
        // 车间地调需要审核
        taskForm.audit_required = true
      } else {
        // 其他角色默认需要审核
        taskForm.audit_required = true
      }
    }
    
    onMounted(() => {
      // 根据角色设置审核需求
      setAuditRequiredByRole()
    })
    
    return {
      taskFormRef,
      taskForm,
      rules,
      bureauOptions,
      directionOptions,
      companyOptions,
      routeOptions,
      transportTypeOptions,
      requirementTypeOptions,
      weightOptions,
      trackOptions,
      handleWeightChange,
      currentUserRole,
      showAuditField,
      actualVolumeDisabled,
      submitForm,
      resetForm,
      cancel
    }
  }
}
</script>

<style scoped>
.create-task-container {
  padding: 20px;
}
</style>