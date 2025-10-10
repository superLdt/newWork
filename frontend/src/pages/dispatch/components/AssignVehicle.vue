<template>
  <div class="assign-vehicle-container">
    <el-form :model="assignForm" label-width="120px" :rules="rules" ref="assignFormRef">
      <el-form-item label="任务ID" prop="task_id">
        <el-input v-model="assignForm.task_id" disabled></el-input>
      </el-form-item>
      
      <el-form-item label="需求吨位">
        <el-input v-model="formattedRequiredWeight" disabled>
          <template #append>吨</template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="实际需求容积">
        <el-input v-model="taskInfo.required_volume" disabled>
          <template #append>m³</template>
        </el-input>
        <div v-if="tonnageVolumeRange" class="volume-range-info">
          容积区间: {{ tonnageVolumeRange }}
        </div>
      </el-form-item>
      
      <el-divider content-position="left">选择车辆</el-divider>
      
      <el-form-item label="车辆筛选">
        <el-row :gutter="10">
          <el-col :span="8">
            <el-input v-model="vehicleFilter.plateNumber" placeholder="车牌号" clearable @input="filterVehicles"></el-input>
          </el-col>
          <el-col :span="8">
            <el-select v-model="vehicleFilter.type" placeholder="车型" clearable @change="filterVehicles" style="width: 100%">
              <el-option v-for="item in vehicleTypes" :key="item.value" :label="item.label" :value="item.value"></el-option>
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-select v-model="vehicleFilter.status" placeholder="状态" clearable @change="filterVehicles" style="width: 100%">
              <el-option v-for="item in vehicleStatuses" :key="item.value" :label="item.label" :value="item.value"></el-option>
            </el-select>
          </el-col>
        </el-row>
      </el-form-item>
      
      <el-form-item label="可用车辆" prop="selectedVehicles">
        <el-table
          :data="availableVehicles"
          style="width: 100%"
          @selection-change="handleSelectionChange"
          height="300px"
          border
        >
          <el-table-column type="selection" width="55" :selectable="checkSelectable"></el-table-column>
          <el-table-column prop="plate_number" label="车牌号" width="120"></el-table-column>
          <el-table-column prop="vehicle_type" label="车型" width="100"></el-table-column>
          <el-table-column prop="capacity" label="载重量" width="100">
            <template #default="scope">
              {{ scope.row.capacity }} 吨
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="容积" width="100">
            <template #default="scope">
              {{ scope.row.volume }} m³
            </template>
          </el-table-column>
          <el-table-column prop="driver_name" label="司机姓名" width="120"></el-table-column>
          <el-table-column prop="driver_phone" label="司机电话" width="150"></el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="当前位置"></el-table-column>
        </el-table>
      </el-form-item>
      
      <!-- 显示已选车辆信息 -->
      <el-form-item label="已选车辆" v-if="assignForm.selectedVehicles.length > 0">
        <el-card class="selected-vehicle-card">
          <div class="vehicle-info">
            <span class="license-plate">{{ assignForm.selectedVehicles[0].plate_number }}</span>
            <span class="vehicle-type">{{ assignForm.selectedVehicles[0].vehicle_type }}</span>
            <span class="volume-info">{{ assignForm.selectedVehicles[0].volume }}m³</span>
            <el-button type="danger" size="small" @click="removeVehicle(0)">移除</el-button>
          </div>
        </el-card>
      </el-form-item>
      
      <el-form-item label="分配说明" prop="notes">
        <el-input v-model="assignForm.notes" type="textarea" :rows="3" placeholder="请输入分配说明或特殊要求"></el-input>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">确认分配</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import tonnageVolumeService from '@/services/tonnageVolumeService'

export default {
  name: 'AssignVehicle',
  props: {
    taskId: {
      type: String,
      required: true
    },
    taskInfo: {
      type: Object,
      required: true
    }
  },
  emits: ['assign-success', 'cancel'],
  setup(props, { emit }) {
    const assignFormRef = ref(null)
    const tonnageVolumeData = ref(null) // 吨位容积数据
    
    // 格式化需求吨位显示
    const formattedRequiredWeight = computed(() => {
      if (!props.taskInfo.required_weight) return ''
      // 移除重复的"吨"字，如"40吨A吨"改为"40吨A"，"8吨吨"改为"8吨"
      return props.taskInfo.required_weight.replace(/吨.*吨$/, '吨')
    })
    
    // 获取吨位对应的容积区间
    const tonnageVolumeRange = computed(() => {
      if (!tonnageVolumeData.value || !props.taskInfo.required_weight) return ''
      
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
      if (!props.taskInfo.required_weight) return
      
      try {
        const response = await tonnageVolumeService.getVolumeByTonnage(props.taskInfo.required_weight)
        if (response && response.data) {
          tonnageVolumeData.value = response.data
        }
      } catch (error) {
        console.error('获取吨位容积数据失败:', error)
      }
    }
    
    // 表单数据
    const assignForm = reactive({
      task_id: props.taskId,
      selectedVehicles: [],
      notes: ''
    })
    
    // 表单验证规则
    const rules = {
      selectedVehicles: [
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
      ],
      notes: [
        { max: 200, message: '说明不能超过200个字符', trigger: 'blur' }
      ]
    }
    
    // 车辆筛选条件
    const vehicleFilter = reactive({
      plateNumber: '',
      type: '',
      status: '空闲'
    })
    
    // 车型选项
    const vehicleTypes = [
      { value: '厢式货车', label: '厢式货车' },
      { value: '平板车', label: '平板车' },
      { value: '冷藏车', label: '冷藏车' },
      { value: '集装箱车', label: '集装箱车' },
      { value: '罐式车', label: '罐式车' }
    ]
    
    // 车辆状态选项
    const vehicleStatuses = [
      { value: '空闲', label: '空闲' },
      { value: '在途', label: '在途' },
      { value: '维修', label: '维修' },
      { value: '休息', label: '休息' }
    ]
    
    // 所有车辆数据
    const allVehicles = ref([])
    
    // 过滤后的可用车辆
    const availableVehicles = computed(() => {
      return allVehicles.value.filter(vehicle => {
        const matchPlate = !vehicleFilter.plateNumber || 
          vehicle.plate_number.toLowerCase().includes(vehicleFilter.plateNumber.toLowerCase())
        const matchType = !vehicleFilter.type || vehicle.vehicle_type === vehicleFilter.type
        const matchStatus = !vehicleFilter.status || vehicle.status === vehicleFilter.status
        return matchPlate && matchType && matchStatus
      })
    })
    
    // 检查车辆是否可选择（限制只能选择一辆车）
    const checkSelectable = (row, index) => {
      // 如果已经选择了一辆车，就不能再选择其他车辆
      return assignForm.selectedVehicles.length === 0
    }
    
    // 获取车辆状态类型
    const getStatusType = (status) => {
      const statusMap = {
        '空闲': 'success',
        '在途': 'warning',
        '维修': 'danger',
        '休息': 'info'
      }
      return statusMap[status] || 'info'
    }
    
    // 加载车辆数据
    const loadVehicles = async () => {
      try {
        // 模拟API调用，实际项目中应替换为真实API
        // const response = await fetch('/api/vehicles/available')
        // const data = await response.json()
        // allVehicles.value = data
        
        // 模拟数据
        allVehicles.value = [
          { id: '1', plate_number: '京A12345', vehicle_type: '厢式货车', capacity: 10, volume: 30, driver_name: '张三', driver_phone: '13800138000', status: '空闲', location: '北京市海淀区' },
          { id: '2', plate_number: '京B67890', vehicle_type: '平板车', capacity: 15, volume: 40, driver_name: '李四', driver_phone: '13900139000', status: '空闲', location: '北京市朝阳区' },
          { id: '3', plate_number: '京C12345', vehicle_type: '冷藏车', capacity: 8, volume: 25, driver_name: '王五', driver_phone: '13700137000', status: '在途', location: '北京市丰台区' },
          { id: '4', plate_number: '京D67890', vehicle_type: '集装箱车', capacity: 20, volume: 50, driver_name: '赵六', driver_phone: '13600136000', status: '空闲', location: '北京市西城区' },
          { id: '5', plate_number: '京E12345', vehicle_type: '罐式车', capacity: 12, volume: 35, driver_name: '孙七', driver_phone: '13500135000', status: '维修', location: '北京市东城区' }
        ]
      } catch (error) {
        console.error('加载车辆数据失败:', error)
        ElMessage.error('加载车辆数据失败')
      }
    }
    
    // 表格选择变化
    const handleSelectionChange = (selection) => {
      // 确保只选择一辆车
      if (selection.length > 0) {
        // 检查容积是否在范围内
        const selectedVehicle = selection[0]
        checkVolumeRange(selectedVehicle.volume)
        assignForm.selectedVehicles = [selectedVehicle]
      } else {
        assignForm.selectedVehicles = []
      }
    }
    
    // 检查容积是否在需求范围内
    const checkVolumeRange = (volume) => {
      if (!volume || !props.taskInfo.required_volume || !tonnageVolumeData.value) return
      
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
          `该车容积(${selectedVolume}m³)不在吨位${props.taskInfo.required_weight}对应的容积区间${rangeDescription}内，是否派车？`,
          '容积范围提示',
          {
            confirmButtonText: '继续派车',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).catch(() => {
          // 用户取消，清空选择
          assignForm.selectedVehicles = []
        })
      }
    }
    
    // 移除已选车辆
    const removeVehicle = (index) => {
      assignForm.selectedVehicles.splice(index, 1)
    }
    
    // 过滤车辆
    const filterVehicles = () => {
      // 过滤逻辑已通过计算属性实现
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!assignFormRef.value) return
      
      await assignFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            // 检查选择的车辆是否满足任务需求
            const totalCapacity = assignForm.selectedVehicles.reduce((sum, vehicle) => sum + vehicle.capacity, 0)
            const totalVolume = assignForm.selectedVehicles.reduce((sum, vehicle) => sum + vehicle.volume, 0)
            
            if (totalCapacity < props.taskInfo.required_weight) {
              ElMessage.warning(`选择的车辆总载重量(${totalCapacity}吨)小于任务需求(${props.taskInfo.required_weight}吨)`)
              return
            }
            
            if (totalVolume < props.taskInfo.required_volume) {
              ElMessage.warning(`选择的车辆总容积(${totalVolume}m³)小于任务需求(${props.taskInfo.required_volume}m³)`)
              return
            }
            
            // 模拟API调用，实际项目中应替换为真实API
            // const response = await fetch(`/api/dispatch/tasks/${props.taskId}/assign`, {
            //   method: 'POST',
            //   headers: {
            //     'Content-Type': 'application/json'
            //   },
            //   body: JSON.stringify({
            //     vehicle_ids: assignForm.selectedVehicles.map(v => v.id),
            //     notes: assignForm.notes
            //   })
            // })
            // 
            // if (!response.ok) {
            //   throw new Error('分配车辆失败')
            // }
            
            ElMessage.success('车辆分配成功')
            emit('assign-success', {
              vehicles: assignForm.selectedVehicles,
              notes: assignForm.notes
            })
          } catch (error) {
            console.error('分配车辆失败:', error)
            ElMessage.error('分配车辆失败: ' + error.message)
          }
        } else {
          return false
        }
      })
    }
    
    // 取消
    const cancel = () => {
      emit('cancel')
    }
    
    onMounted(() => {
      loadVehicles()
      assignForm.task_id = props.taskId
      // 加载吨位容积数据
      loadTonnageVolumeData()
    })
    
    return {
      assignFormRef,
      assignForm,
      rules,
      vehicleFilter,
      vehicleTypes,
      vehicleStatuses,
      availableVehicles,
      getStatusType,
      handleSelectionChange,
      removeVehicle,
      filterVehicles,
      submitForm,
      cancel,
      taskInfo: props.taskInfo,
      checkSelectable,
      tonnageVolumeRange,
      formattedRequiredWeight
    }
  }
}
</script>

<style scoped>
.assign-vehicle-container {
  padding: 20px;
}

.el-divider {
  margin: 20px 0;
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