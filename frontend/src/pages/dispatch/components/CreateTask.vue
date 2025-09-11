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
      
      <el-form-item label="起始站段" prop="start_bureau">
        <el-select v-model="taskForm.start_bureau" placeholder="请选择起始站段" style="width: 100%">
          <el-option
            v-for="item in bureauOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="路线方向" prop="route_direction">
        <el-select v-model="taskForm.route_direction" placeholder="请选择路线方向" style="width: 100%">
          <el-option
            v-for="item in directionOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="运输公司" prop="carrier_company">
        <el-select v-model="taskForm.carrier_company" placeholder="请选择运输公司" style="width: 100%">
          <el-option
            v-for="item in companyOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="路线名称" prop="route_name">
        <el-select v-model="taskForm.route_name" placeholder="请选择路线名称" style="width: 100%">
          <el-option
            v-for="item in routeOptions"
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
      
      <el-form-item label="需求容积" prop="volume">
        <el-input-number v-model="taskForm.volume" :min="0" :precision="2" :step="1" style="width: 100%">
          <template #append>m³</template>
        </el-input-number>
      </el-form-item>
      
      <el-form-item label="需求重量" prop="weight">
        <el-input-number v-model="taskForm.weight" :min="0" :precision="2" :step="1" style="width: 100%">
          <template #append>吨</template>
        </el-input-number>
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
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'CreateTask',
  emits: ['create-success', 'cancel'],
  setup(props, { emit }) {
    const taskFormRef = ref(null)
    
    // 表单数据
    const taskForm = reactive({
      required_date: '',
      start_bureau: '',
      route_direction: '',
      carrier_company: '',
      route_name: '',
      transport_type: '',
      requirement_type: '',
      volume: 0,
      weight: 0,
      dispatch_track: '',
      special_requirements: ''
    })
    
    // 表单验证规则
    const rules = {
      required_date: [
        { required: true, message: '请选择需求日期', trigger: 'change' }
      ],
      start_bureau: [
        { required: true, message: '请选择起始站段', trigger: 'change' }
      ],
      route_direction: [
        { required: true, message: '请选择路线方向', trigger: 'change' }
      ],
      carrier_company: [
        { required: true, message: '请选择运输公司', trigger: 'change' }
      ],
      route_name: [
        { required: true, message: '请选择路线名称', trigger: 'change' }
      ],
      transport_type: [
        { required: true, message: '请选择运输类型', trigger: 'change' }
      ],
      requirement_type: [
        { required: true, message: '请选择需求类型', trigger: 'change' }
      ],
      volume: [
        { required: true, message: '请输入需求容积', trigger: 'blur' },
        { type: 'number', min: 0.01, message: '容积必须大于0', trigger: 'blur' }
      ],
      weight: [
        { required: true, message: '请输入需求重量', trigger: 'blur' },
        { type: 'number', min: 0.01, message: '重量必须大于0', trigger: 'blur' }
      ],
      dispatch_track: [
        { required: true, message: '请选择派车轨道', trigger: 'change' }
      ],
      special_requirements: [
        { max: 200, message: '特殊要求不能超过200个字符', trigger: 'blur' }
      ]
    }
    
    // 站段选项
    const bureauOptions = [
      { value: '北京', label: '北京' },
      { value: '上海', label: '上海' },
      { value: '广州', label: '广州' },
      { value: '深圳', label: '深圳' },
      { value: '成都', label: '成都' }
    ]
    
    // 路线方向选项
    const directionOptions = [
      { value: '南向北', label: '南向北' },
      { value: '北向南', label: '北向南' },
      { value: '东向西', label: '东向西' },
      { value: '西向东', label: '西向东' }
    ]
    
    // 运输公司选项
    const companyOptions = [
      { value: '中铁物流', label: '中铁物流' },
      { value: '中远海运', label: '中远海运' },
      { value: '顺丰物流', label: '顺丰物流' },
      { value: '京东物流', label: '京东物流' },
      { value: '德邦物流', label: '德邦物流' }
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
      { value: '普通货运', label: '普通货运' },
      { value: '快速货运', label: '快速货运' },
      { value: '冷链运输', label: '冷链运输' },
      { value: '危险品运输', label: '危险品运输' },
      { value: '大件运输', label: '大件运输' }
    ]
    
    // 需求类型选项
    const requirementTypeOptions = [
      { value: '常规', label: '常规' },
      { value: '紧急', label: '紧急' },
      { value: '特殊', label: '特殊' },
      { value: '临时', label: '临时' }
    ]
    
    // 派车轨道选项
    const trackOptions = [
      { value: '1号轨道', label: '1号轨道' },
      { value: '2号轨道', label: '2号轨道' },
      { value: '3号轨道', label: '3号轨道' },
      { value: '4号轨道', label: '4号轨道' },
      { value: '5号轨道', label: '5号轨道' }
    ]
    
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
    
    onMounted(() => {
      // 可以在这里加载初始数据
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
      trackOptions,
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