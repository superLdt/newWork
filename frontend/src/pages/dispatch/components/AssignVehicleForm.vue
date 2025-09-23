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
      
      <el-form-item label="需求吨位">
        <el-input v-model="formattedRequiredWeight" disabled>
          <template #append>吨</template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="实际需求容积">
        <el-input v-model="task.required_volume" disabled>
          <template #append>m³</template>
        </el-input>
        <div v-if="tonnageVolumeRange" class="volume-range-info">
          容积区间: {{ tonnageVolumeRange }}
        </div>
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
          <el-table-column type="selection" width="55" :selectable="checkSelectable"></el-table-column>
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
      
      <!-- 显示已选车辆信息 -->
      <el-form-item label="已选车辆" v-if="selectedVehicleInfo">
        <el-card class="selected-vehicle-card">
          <div class="vehicle-info">
            <span class="license-plate">{{ selectedVehicleInfo.plate_number }}</span>
            <span class="vehicle-type">{{ selectedVehicleInfo.vehicle_type }}</span>
            <span class="volume-info">{{ selectedVehicleInfo.volume }}m³</span>
            <el-button type="danger" size="small" @click="clearSelection">移除</el-button>
          </div>
        </el-card>
      </el-form-item>
      
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { dispatchService } from '@/services/dispatchService'
import tonnageVolumeService from '@/services/tonnageVolumeService'

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
    const tonnageVolumeData = ref(null) // 吨位容积数据
    
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
    
    // 表单数据
    const formData = reactive({
      task_id: '',
      vehicles: [],
      notes: ''
    })
    
    // 表单验证规则
    const rules = {
      vehicles: [
        { 
          type: 'array', 
          required: true, 
          message: '请至少选择一辆车辆', 
          trigger: 'change',
          validator: (rule, value, callback) => {
            if (!value || value.length === 0) {
              callback(new Error('请至少选择一辆车辆'))
              return
            }
            
            // 唯一性验证：一个任务只能派遣一辆车
            if (value.length > 1) {
              callback(new Error('一个任务只能派遣一辆车，请重新选择'))
              return
            }
            
            callback()
          }
        }
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
    
    // 计算已选车辆信息
    const selectedVehicleInfo = computed(() => {
      if (!formData.vehicles.length || !vehicles.value.length) return null
      
      const selectedVehicleId = formData.vehicles[0]
      return vehicles.value.find(vehicle => vehicle.vehicle_id === selectedVehicleId) || null
    })
    
    // 清除选择
    const clearSelection = () => {
      formData.vehicles = []
    }
    
    // 检查车辆是否可选择（限制只能选择一辆车）
    const checkSelectable = (row, index) => {
      // 如果已经选择了一辆车，就不能再选择其他车辆
      return formData.vehicles.length === 0
    }
    
    // 初始化表单数据
    onMounted(async () => {
      formData.task_id = props.task.task_id
      await Promise.all([
        fetchAvailableVehicles(),
        loadTonnageVolumeData() // 加载吨位容积数据
      ])
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
      // 确保只选择一辆车
      if (selection.length > 0) {
        // 检查容积是否在范围内
        const selectedVehicle = selection[0]
        checkVolumeRange(selectedVehicle.volume)
        formData.vehicles = [selectedVehicle.vehicle_id]
      } else {
        formData.vehicles = []
      }
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
          // 用户取消，清空选择
          formData.vehicles = []
        })
      }
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
      cancel,
      checkSelectable,
      tonnageVolumeRange,
      formattedRequiredWeight,
      selectedVehicleInfo,
      clearSelection
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

.volume-range-info {
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
}

.selected-vehicle-card {
  width: 100%;
}

.vehicle-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.license-plate {
  font-weight: bold;
  font-size: 16px;
}

.vehicle-type {
  background-color: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.volume-info {
  color: #606266;
  font-size: 14px;
}
</style>