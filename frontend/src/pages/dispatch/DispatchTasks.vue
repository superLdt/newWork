<template>
  <div class="dispatch-tasks-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>派车任务管理</h2>
          <el-button type="primary" @click="openCreateTaskDialog">新建派车任务</el-button>
        </div>
      </template>
      
      <!-- 搜索过滤区域 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="任务状态">
            <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
              <el-option label="待审核" value="pending"></el-option>
              <el-option label="已审核" value="approved"></el-option>
              <el-option label="已分配" value="assigned"></el-option>
              <el-option label="进行中" value="in_progress"></el-option>
              <el-option label="已完成" value="completed"></el-option>
              <el-option label="已取消" value="cancelled"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="filterForm.query" placeholder="任务ID/路线名称"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchTasks">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 任务列表表格 -->
      <el-table
        v-loading="loading"
        :data="taskList"
        style="width: 100%"
        border
      >
        <el-table-column prop="task_id" label="任务ID" width="180"></el-table-column>
        <el-table-column prop="required_date" label="需求日期" width="120"></el-table-column>
        <el-table-column prop="start_bureau" label="起始站段" width="150"></el-table-column>
        <el-table-column prop="route_name" label="路线名称"></el-table-column>
        <el-table-column prop="transport_type" label="运输类型" width="120"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewTaskDetail(scope.row)">查看</el-button>
            <el-button 
              size="small" 
              type="primary" 
              v-if="scope.row.status === 'pending' && hasPermission('dispatch:approve')"
              @click="openApproveDialog(scope.row)"
            >审核</el-button>
            <el-button 
              size="small" 
              type="success" 
              v-if="scope.row.status === 'approved' && hasPermission('dispatch:assign')"
              @click="openAssignVehicleDialog(scope.row)"
            >分配车辆</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next, sizes, total"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>
    
    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="taskDetailDialogVisible"
      title="派车任务详情"
      width="70%"
    >
      <task-detail v-if="currentTask" :task="currentTask"></task-detail>
    </el-dialog>
    
    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="createTaskDialogVisible"
      title="创建派车任务"
      width="70%"
    >
      <task-form @submit="handleTaskSubmit" @cancel="createTaskDialogVisible = false"></task-form>
    </el-dialog>
    
    <!-- 审核任务对话框 -->
    <el-dialog
      v-model="approveDialogVisible"
      title="审核派车任务"
      width="50%"
    >
      <approve-form 
        v-if="currentTask" 
        :task="currentTask" 
        @submit="handleApproveSubmit" 
        @cancel="approveDialogVisible = false"
      ></approve-form>
    </el-dialog>
    
    <!-- 分配车辆对话框 -->
    <el-dialog
      v-model="assignVehicleDialogVisible"
      title="分配车辆"
      width="60%"
    >
      <assign-vehicle-form 
        v-if="currentTask" 
        :task="currentTask" 
        @submit="handleAssignVehicleSubmit" 
        @cancel="assignVehicleDialogVisible = false"
      ></assign-vehicle-form>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import TaskDetail from './components/TaskDetail.vue'
import TaskForm from './components/TaskForm.vue'
import ApproveForm from './components/ApproveForm.vue'
import AssignVehicleForm from './components/AssignVehicleForm.vue'
import { usePermissionStore } from '@/stores/permission'
import { dispatchService } from '@/services/dispatchService'

export default {
  name: 'DispatchTasks',
  components: {
    TaskDetail,
    TaskForm,
    ApproveForm,
    AssignVehicleForm
  },
  setup() {
    const permissionStore = usePermissionStore()
    
    // 数据状态
    const loading = ref(false)
    const taskList = ref([])
    const currentTask = ref(null)
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    
    // 对话框状态
    const taskDetailDialogVisible = ref(false)
    const createTaskDialogVisible = ref(false)
    const approveDialogVisible = ref(false)
    const assignVehicleDialogVisible = ref(false)
    
    // 过滤表单
    const filterForm = reactive({
      status: '',
      query: ''
    })
    
    // 获取任务列表
    const fetchTasks = async () => {
      loading.value = true
      try {
        // 使用dispatchService获取任务列表
        const params = {
          page: currentPage.value,
          per_page: pageSize.value,
          status: filterForm.status,
          query: filterForm.query
        }
        const result = await dispatchService.getTasks(params)
        
        if (result.code === 0) {
          taskList.value = result.data.items
          total.value = result.data.total
        } else {
          ElMessage.error(result.message || '获取任务列表失败')
        }
      } catch (error) {
        console.error('获取任务列表失败:', error)
        ElMessage.error('获取任务列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 搜索任务
    const searchTasks = () => {
      currentPage.value = 1
      fetchTasks()
    }
    
    // 重置过滤条件
    const resetFilter = () => {
      filterForm.status = ''
      filterForm.query = ''
      searchTasks()
    }
    
    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchTasks()
    }
    
    // 处理每页数量变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchTasks()
    }
    
    // 查看任务详情
    const viewTaskDetail = (task) => {
      currentTask.value = task
      taskDetailDialogVisible.value = true
    }
    
    // 打开创建任务对话框
    const openCreateTaskDialog = () => {
      createTaskDialogVisible.value = true
    }
    
    // 处理任务提交
    const handleTaskSubmit = async (taskData) => {
      try {
        // 使用dispatchService创建任务
        const result = await dispatchService.createTask(taskData)
        
        if (result.code === 0) {
          ElMessage.success('创建任务成功')
          createTaskDialogVisible.value = false
          fetchTasks()
        } else {
          ElMessage.error(result.message || '创建任务失败')
        }
      } catch (error) {
        console.error('创建任务失败:', error)
        ElMessage.error('创建任务失败')
      }
    }
    
    // 打开审核对话框
    const openApproveDialog = (task) => {
      currentTask.value = task
      approveDialogVisible.value = true
    }
    
    // 处理审核提交
    const handleApproveSubmit = async (approveData) => {
      try {
        // 使用dispatchService审核任务
        const result = await dispatchService.auditTask(currentTask.value.task_id, approveData)
        
        if (result.code === 0) {
          ElMessage.success('审核任务成功')
          approveDialogVisible.value = false
          fetchTasks()
        } else {
          ElMessage.error(result.message || '审核任务失败')
        }
      } catch (error) {
        console.error('审核任务失败:', error)
        ElMessage.error('审核任务失败')
      }
    }
    
    // 打开分配车辆对话框
    const openAssignVehicleDialog = (task) => {
      currentTask.value = task
      assignVehicleDialogVisible.value = true
    }
    
    // 处理分配车辆提交
    const handleAssignVehicleSubmit = async (vehicleData) => {
      try {
        // 使用dispatchService分配车辆
        const result = await dispatchService.assignVehicles(currentTask.value.task_id, vehicleData)
        
        if (result.code === 0) {
          ElMessage.success('分配车辆成功')
          assignVehicleDialogVisible.value = false
          fetchTasks()
        } else {
          ElMessage.error(result.message || '分配车辆失败')
        }
      } catch (error) {
        console.error('分配车辆失败:', error)
        ElMessage.error('分配车辆失败')
      }
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        'pending': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'assigned': 'primary',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger'
      }
      return statusMap[status] || 'info'
    }
    
    // 检查权限
    const hasPermission = (permission) => {
      return permissionStore.hasPermission(permission)
    }
    
    onMounted(() => {
      fetchTasks()
    })
    
    return {
      loading,
      taskList,
      currentTask,
      total,
      currentPage,
      pageSize,
      filterForm,
      taskDetailDialogVisible,
      createTaskDialogVisible,
      approveDialogVisible,
      assignVehicleDialogVisible,
      fetchTasks,
      searchTasks,
      resetFilter,
      handleCurrentChange,
      handleSizeChange,
      viewTaskDetail,
      openCreateTaskDialog,
      handleTaskSubmit,
      openApproveDialog,
      handleApproveSubmit,
      openAssignVehicleDialog,
      handleAssignVehicleSubmit,
      getStatusType,
      hasPermission
    }
  }
}
</script>

<style scoped>
.dispatch-tasks-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>