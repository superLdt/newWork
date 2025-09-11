<template>
  <div class="assign-vehicle-form-container">
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
      
      <el-divider content-position="left">选择车辆</el-divider>
      
      <div class="vehicle-filter">
        <el-input
          v-model="vehicleFilter"
          placeholder="搜索车牌号/司机姓名"
          clearable
          @input="filterVehicles"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="vehicle-list" v-loading="loading">
        <el-table
          ref="vehicleTable"
          :data="filteredVehicles"
          style="width: 100%"
          border
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="vehicle_id" label="车辆ID" width="100"></el-table-column>
          <el-table-column prop="plate_number" label="车牌号" width="120"></el-table-column>
          <el-table-column prop="vehicle_type" label="车型" width="100"></el-table-column>
          <el-table-column prop="driver_name" label="司机姓名" width="100"></el-table-column>
          <el-table-column prop="driver_phone" label="司机电话" width="150"></el-table-column>
          <el-table-column prop="capacity" label="载重量" width="100"></el-table-column>
          <el-table-column prop="volume" label="容积" width="100"></el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'available' ? 'success' : 'info'">
                {{ scope.row.status === 'available' ? '可用' : '忙碌' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <el-form-item label="分配备注" prop="notes">
        <el-input 
          v-model="formData.notes" 
          type="textarea" 
          rows="3"
          placeholder="请输入分配备注"
        ></el-input>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm" :disabled="!formData.vehicles.length">提交</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { dispatchService } from '@/services/dispatchService'

export default {
  name: 'AssignVehicleForm',
  components: {
    Search
  },
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const vehicleTable = ref(null)
    const loading = ref(false)
    const vehicles = ref([])
    const vehicleFilter = ref('')
    
    // 表单数据
    const formData = reactive({
      task_id: '',
      vehicles: [],
      notes: ''
    })
    
    // 表单验证规则
    const rules = {
      vehicles: [
        { type: 'array', required: true, message: '请至少选择一辆车辆', trigger: 'change' }
      ]
    }
    
    // 过滤后的车辆列表
    const filteredVehicles = computed(() => {
      if (!vehicleFilter.value) return vehicles.value
      
      const keyword = vehicleFilter.value.toLowerCase()
      return vehicles.value.filter(vehicle => {
        return vehicle.plate_number.toLowerCase().includes(keyword) ||
               vehicle.driver_name.toLowerCase().includes(keyword)
      })
    })
    
    // 初始化表单数据
    onMounted(async () => {
      formData.task_id = props.task.task_id
      await fetchAvailableVehicles()
    })
    
    // 获取可用车辆
    const fetchAvailableVehicles = async () => {
      loading.value = true
      try {
        const result = await dispatchService.getAvailableVehicles()
        vehicles.value = result.data || []
      } catch (error) {
        console.error('获取可用车辆失败:', error)
        ElMessage.error('获取可用车辆失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理车辆选择变化
    const handleSelectionChange = (selection) => {
      formData.vehicles = selection.map(item => item.vehicle_id)
    }
    
    // 过滤车辆
    const filterVehicles = () => {
      // 过滤逻辑由计算属性处理
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid, fields) => {
        if (valid) {
          if (formData.vehicles.length === 0) {
            ElMessage.warning('请至少选择一辆车辆')
            return
          }
          
          try {
            // 使用dispatchService分配车辆
            const result = await dispatchService.assignVehicles(formData.task_id, {
              vehicle_ids: formData.vehicles,
              notes: formData.notes
            })
            ElMessage.success('分配车辆成功')
            emit('submit', result)
          } catch (error) {
            console.error('分配车辆失败:', error)
            ElMessage.error(error.message || '分配车辆失败')
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
      vehicleTable,
      loading,
      vehicles,
      filteredVehicles,
      vehicleFilter,
      formData,
      rules,
      handleSelectionChange,
      filterVehicles,
      submitForm,
      cancel
    }
  }
}
</script>

<style scoped>
.assign-vehicle-form-container {
  padding: 20px;
}

.vehicle-filter {
  margin-bottom: 15px;
}

.vehicle-list {
  margin-bottom: 20px;
  max-height: 400px;
  overflow-y: auto;
}
</style>