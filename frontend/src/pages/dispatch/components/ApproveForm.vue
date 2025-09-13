<template>
  <div class="approve-form-container">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      label-position="right"
    >
      <el-form-item label="任务ID" prop="task_id">
        <el-input v-model="formData.task_id" disabled></el-input>
      </el-form-item>
      
      <el-form-item label="审核结果" prop="result">
        <el-radio-group v-model="formData.result">
          <el-radio label="approved">通过</el-radio>
          <el-radio label="rejected">拒绝</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="审核意见" prop="comment">
        <el-input 
          v-model="formData.comment" 
          type="textarea" 
          rows="4"
          placeholder="请输入审核意见"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'ApproveForm',
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    
    // 表单数据
    const formData = reactive({
      task_id: '',
      result: 'approved',
      comment: ''
    })
    
    // 表单验证规则
    const rules = {
      result: [
        { required: true, message: '请选择审核结果', trigger: 'change' }
      ],
      comment: [
        { required: true, message: '请输入审核意见', trigger: 'blur' }
      ]
    }
    
    // 初始化表单数据
    onMounted(() => {
      formData.task_id = props.task.task_id
    })
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid, fields) => {
        if (valid) {
          // 只进行表单验证，将数据传递给父组件处理
          const approveData = {
            approved: formData.result === 'approved',
            comment: formData.comment
          }
          emit('submit', approveData)
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
.approve-form-container {
  padding: 20px;
}
</style>