<template>
  <div class="task-form-container">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      label-position="right"
    >
      <el-form-item label="需求日期" prop="required_date">
        <el-date-picker
          v-model="formData.required_date"
          type="date"
          placeholder="选择需求日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        ></el-date-picker>
      </el-form-item>
      
      <el-form-item label="起始站段" prop="start_bureau">
        <el-input v-model="formData.start_bureau" placeholder="请输入起始站段"></el-input>
      </el-form-item>
      
      <el-form-item label="目的站段" prop="end_bureau">
        <el-input v-model="formData.end_bureau" placeholder="请输入目的站段"></el-input>
      </el-form-item>
      
      <el-form-item label="路线名称" prop="route_name">
        <el-input v-model="formData.route_name" placeholder="请输入路线名称"></el-input>
      </el-form-item>
      
      <el-form-item label="运输类型" prop="transport_type">
        <el-select v-model="formData.transport_type" placeholder="请选择运输类型">
          <el-option label="普通货物" value="regular"></el-option>
          <el-option label="危险品" value="dangerous"></el-option>
          <el-option label="特殊物资" value="special"></el-option>
          <el-option label="紧急物资" value="urgent"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="预计里程(km)" prop="estimated_distance">
        <el-input-number 
          v-model="formData.estimated_distance" 
          :min="0" 
          :precision="2"
          :step="10"
          controls-position="right"
        ></el-input-number>
      </el-form-item>
      
      <el-form-item label="预计时长(小时)" prop="estimated_duration">
        <el-input-number 
          v-model="formData.estimated_duration" 
          :min="0" 
          :precision="1"
          :step="0.5"
          controls-position="right"
        ></el-input-number>
      </el-form-item>
      
      <el-form-item label="联系人" prop="contact_person">
        <el-input v-model="formData.contact_person" placeholder="请输入联系人姓名"></el-input>
      </el-form-item>
      
      <el-form-item label="联系电话" prop="contact_phone">
        <el-input v-model="formData.contact_phone" placeholder="请输入联系电话"></el-input>
      </el-form-item>
      
      <el-form-item label="备注" prop="remarks">
        <el-input 
          v-model="formData.remarks" 
          type="textarea" 
          rows="3"
          placeholder="请输入备注信息"
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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { dispatchService } from '@/services/dispatchService'

export default {
  name: 'TaskForm',
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    
    // 表单数据
    const formData = reactive({
      required_date: '',
      start_bureau: '',
      end_bureau: '',
      route_name: '',
      transport_type: '',
      estimated_distance: 0,
      estimated_duration: 0,
      contact_person: '',
      contact_phone: '',
      remarks: ''
    })
    
    // 表单验证规则
    const rules = {
      required_date: [
        { required: true, message: '请选择需求日期', trigger: 'change' }
      ],
      start_bureau: [
        { required: true, message: '请输入起始站段', trigger: 'blur' }
      ],
      end_bureau: [
        { required: true, message: '请输入目的站段', trigger: 'blur' }
      ],
      route_name: [
        { required: true, message: '请输入路线名称', trigger: 'blur' }
      ],
      transport_type: [
        { required: true, message: '请选择运输类型', trigger: 'change' }
      ],
      contact_person: [
        { required: true, message: '请输入联系人姓名', trigger: 'blur' }
      ],
      contact_phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
      ]
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid, fields) => {
        if (valid) {
          try {
            // 使用dispatchService创建任务
            const result = await dispatchService.createTask(formData)
            ElMessage.success('创建任务成功')
            emit('submit', result)
          } catch (error) {
            console.error('创建任务失败:', error)
            ElMessage.error(error.message || '创建任务失败')
          }
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
      cancel
    }
  }
}
</script>

<style scoped>
.task-form-container {
  padding: 20px;
}
</style>