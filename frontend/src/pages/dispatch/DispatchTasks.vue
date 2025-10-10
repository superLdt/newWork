<template>
  <div class="dispatch-tasks-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>派车任务管理</h2>
          <el-button 
            type="primary" 
            @click="openCreateTaskDialog"
            v-if="hasPermission('dispatch:create') && canCreateTask"
          >新建派车任务</el-button>
        </div>
      </template>
      
      <!-- 搜索过滤区域 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="任务状态">
            <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
              <el-option label="待审核" value="待审核"></el-option>
              <el-option label="审核通过" value="审核通过"></el-option>
              <el-option label="待响应" value="待响应"></el-option>
              <el-option label="已响应" value="已响应"></el-option>
              <el-option label="任务完成" value="任务完成"></el-option>
              <el-option label="审核拒绝" value="审核拒绝"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="业务类型">
            <el-select v-model="filterForm.business_type" placeholder="选择业务类型" clearable>
              <el-option label="委办派车" value="委办派车"></el-option>
              <el-option label="自办派车" value="自办派车"></el-option>
              <el-option label="大容积派车" value="大容积派车"></el-option>
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
        <el-table-column type="index" label="序号" width="60"></el-table-column>
        <el-table-column prop="task_id" label="任务ID" width="160"></el-table-column>
        <el-table-column prop="business_type" label="业务类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.business_type === '自办派车' ? 'success' : (scope.row.business_type === '大容积派车' ? 'warning' : 'primary')">{{ scope.row.business_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="required_date" label="需求日期" width="120"></el-table-column>
        <el-table-column prop="origin_bureau" label="始发局" width="120"></el-table-column>
        <el-table-column prop="mail_route_name" label="邮路名称"></el-table-column>
        <el-table-column prop="transport_type" label="运输类型" width="100"></el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.required_date)">{{ getPriorityText(scope.row.required_date) }}</el-tag>
          </template>
        </el-table-column>
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
              v-if="scope.row.status === '待审核' && hasPermission('dispatch:approve')"
              @click="openApproveDialog(scope.row)"
            >审核</el-button>
            <el-button 
              size="small" 
              type="warning" 
              v-if="canSeeSupplierResponse(scope.row)"
              @click="openSupplierResponseDialog(scope.row)"
            >{{ getRoleBasedResponseText(scope.row) }}</el-button>
            <el-button 
              size="small" 
              type="success" 
              v-if="canShowSupplierConfirm(scope.row)"
              @click="openSupplierConfirmDialog(scope.row)"
            >确认</el-button>
            <el-button
              size="small"
              type="primary"
              v-if="canShowWorkshopVerify(scope.row)"
              @click="openWorkshopVerify(scope.row)"
            >核查</el-button>
            <el-button
              size="small"
              type="danger"
              v-if="canShowAppealReview(scope.row)"
              @click="openAppealReviewDialog(scope.row)"
            >申诉审核</el-button>
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
      :title="currentTask ? '派车任务详情' : ''"
      width="65%"
      top="5vh"
      :close-on-click-modal="false"
      @close="handleTaskDetailClose"
    >
      <TaskDetail 
        v-if="currentTask" 
        :task="currentTask" 
        :autoOpenWorkshopVerify="autoOpenWorkshopVerify"
        @task-updated="handleTaskUpdated"
      />
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
      :title="currentTask ? (currentTask.business_type === '自办派车' ? '内部响应' : '供应商响应') : '分配车辆'"
      width="60%"
    >
      <assign-vehicle-form 
        v-if="currentTask" 
        :task="currentTask" 
        @submit="handleAssignVehicleSubmit" 
        @cancel="assignVehicleDialogVisible = false"
      ></assign-vehicle-form>
    </el-dialog>
    
    <!-- 响应表单对话框（复用供应商响应表单） -->
    <el-dialog
      v-model="supplierResponseDialogVisible"
      :title="getResponseDialogTitle()"
      width="80%"
      top="5vh"
      :close-on-click-modal="false"
    >
      <supplier-response-form
        v-if="supplierResponseDialogVisible && currentTask"
        :task="currentTask"
        @response-success="handleResponseSuccessFromList"
        @cancel="supplierResponseDialogVisible = false"
      />
    </el-dialog>
    
    <!-- 供应商确认对话框 -->
    <SupplierConfirmDialog
      v-model:visible="supplierConfirmDialogVisible"
      :task="currentTask"
      @confirm-success="handleSupplierConfirmSuccess"
      @open-appeal-dialog="handleOpenAppealDialog"
    />

    <!-- 供应商申诉对话框 -->
    <SupplierAppealDialog
      v-model:visible="supplierAppealDialogVisible"
      :task="currentTask"
      @appeal-success="handleAppealSuccess"
    />

    <!-- 申诉审核对话框 -->
    <AppealReviewDialog
      v-model:visible="appealReviewDialogVisible"
      :task="currentTask"
      @review-success="handleAppealReviewSuccess"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import TaskDetail from './components/TaskDetail.vue'
import TaskForm from './components/TaskForm.vue'
import ApproveForm from './components/ApproveForm.vue'
import AssignVehicleForm from './components/AssignVehicleForm.vue'
import SupplierResponseForm from './components/SupplierResponseForm.vue'
import SupplierConfirmDialog from './components/SupplierConfirmDialog.vue'
import SupplierAppealDialog from './components/SupplierAppealDialog.vue'
import AppealReviewDialog from './components/AppealReviewDialog.vue'
import { usePermissionStore } from '@/stores/permission'
import { dispatchService } from '@/services/dispatchService'

export default {
  name: 'DispatchTasks',
  components: {
    TaskDetail,
    TaskForm,
    ApproveForm,
    AssignVehicleForm,
    SupplierResponseForm,
    SupplierConfirmDialog,
    SupplierAppealDialog,
    AppealReviewDialog
  },
  setup() {
    const permissionStore = usePermissionStore()
    const router = useRouter()
    
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
    const supplierResponseDialogVisible = ref(false)
    const supplierConfirmDialogVisible = ref(false)
    const supplierAppealDialogVisible = ref(false)
    const appealReviewDialogVisible = ref(false)
    
    // 新增：自动打开车间地调核查
    const autoOpenWorkshopVerify = ref(false)

    // 过滤表单
    const filterForm = reactive({
      status: '',
      business_type: '',
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
          business_type: filterForm.business_type,
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
      filterForm.business_type = ''
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
      // 使用dispatchService创建任务
      const result = await dispatchService.createTask(taskData)
      
      if (result && result.code === 0) {
        ElMessage.success(result.message || '创建任务成功')
        createTaskDialogVisible.value = false
        fetchTasks()
      } else {
        ElMessage.error(result?.message || '创建任务失败')
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

    // 检查是否可以创建任务（超级管理员、区域调度员和车间地调都可以）
    const canCreateTask = computed(() => {
      const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
      const hasRole = (names) => rolesArr.some(r => names.includes(r))
      return hasRole(['超级管理员', '区域调度员', '车间地调'])
    })

    // 基于当前用户角色返回响应按钮文本
    const getRoleBasedResponseText = (taskRow) => {
      try {
        const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
        const hasRole = (names) => rolesArr.some(r => names.includes(r))

        if (hasRole(['班组长', 'team_leader'])) return '自备派车'
        if (hasRole(['大容积供应商', 'large_capacity_supplier'])) return '大容积派车'
        if (hasRole(['供应商', 'supplier'])) return '供应商响应'

        // 兜底：按业务类型
        if (taskRow?.business_type === '自办派车') {
          return '内部响应'
        } else if (taskRow?.business_type === '大容积派车') {
          return '大容积派车'
        } else {
          return '供应商响应'
        }
      } catch(e) {
        // 异常时回退
        if (taskRow?.business_type === '自办派车') {
          return '内部响应'
        } else if (taskRow?.business_type === '大容积派车') {
          return '大容积派车'
        } else {
          return '供应商响应'
        }
      }
    }

    // 根据用户角色与当前任务，生成响应表单对话框标题
    const getResponseDialogTitle = () => {
      try {
        const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
        const hasRole = (names) => rolesArr.some(r => names.includes(r))

        if (hasRole(['班组长', 'team_leader'])) return '自备派车'
        if (hasRole(['大容积供应商', 'large_capacity_supplier'])) return '大容积派车'
        if (hasRole(['供应商', 'supplier'])) return '供应商响应'

        // 兜底：结合业务类型
        const bt = currentTask.value?.business_type
        if (bt === '自办派车') {
          return '内部响应'
        } else if (bt === '大容积派车') {
          return '大容积派车'
        } else {
          return '供应商响应'
        }
      } catch (e) {
        const bt = currentTask.value?.business_type
        if (bt === '自办派车') {
          return '内部响应'
        } else if (bt === '大容积派车') {
          return '大容积派车'
        } else {
          return '供应商响应'
        }
      }
    }

    // 按角色与任务状态决定是否显示响应按钮
    const canSeeSupplierResponse = (taskRow) => {
      try {
        const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
        const hasRole = (names) => rolesArr.some(r => names.includes(r))

        // 允许在待响应或审核通过阶段进行响应
        const allowedStatuses = ['待响应', '审核通过']
        if (!allowedStatuses.includes(taskRow?.status)) return false

        if (hasRole(['班组长', 'team_leader'])) return true
        if (hasRole(['大容积供应商', 'large_capacity_supplier'])) return true
        if (hasRole(['供应商', 'supplier'])) return true
        return false
      } catch (e) {
        return false
      }
    }

    // 打开响应表单对话框
    const openSupplierResponseDialog = (taskRow) => {
      currentTask.value = taskRow
      supplierResponseDialogVisible.value = true
    }

    // 从列表页响应成功后的处理
    const handleResponseSuccessFromList = async () => {
      try {
        ElMessage.success('响应提交成功')
        supplierResponseDialogVisible.value = false
        await fetchTasks()
        if (currentTask.value) {
          const updated = taskList.value.find(t => t.task_id === currentTask.value.task_id)
          if (updated) currentTask.value = { ...updated }
        }
      } catch (e) {
        ElMessage.error('刷新列表失败')
      }
    }

    // 计算优先级类型
    const getPriorityType = (requiredDate) => {
      const now = new Date()
      const reqDate = new Date(requiredDate)
      const diffHours = (reqDate.getTime() - now.getTime()) / (1000 * 60 * 60)

      if (diffHours < 0) {
        return 'danger' // 超时
      } else if (diffHours < 12) {
        return 'danger' // 特急
      } else if (diffHours < 24) {
        return 'warning' // 紧急
      } else {
        return 'success' // 正常
      }
    }

    // 计算优先级文本
    const getPriorityText = (requiredDate) => {
      const now = new Date()
      const reqDate = new Date(requiredDate)
      const diffHours = (reqDate.getTime() - now.getTime()) / (1000 * 60 * 60)

      if (diffHours < 0) {
        return '超时'
      } else if (diffHours < 12) {
        return '特急'
      } else if (diffHours < 24) {
        return '紧急'
      } else {
        return '正常'
      }
    }

    // 按角色与任务状态决定是否显示确认按钮
    const canShowSupplierConfirm = (taskRow) => {
      try {
        const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
        const hasRole = (names) => rolesArr.some(r => names.includes(r))

        // 只有待确认状态的任务才显示确认按钮
        if (taskRow?.status !== '待确认') return false

        // 班组长、供应商和大容积供应商都可以进行确认
        return hasRole(['班组长', 'team_leader', '供应商', 'supplier', '大容积供应商', 'large_capacity_supplier'])
      } catch (e) {
        return false
      }
    }

    // 打开供应商确认对话框
    const openSupplierConfirmDialog = (taskRow) => {
      currentTask.value = taskRow
      supplierConfirmDialogVisible.value = true
    }

    // 处理供应商确认成功
    const handleSupplierConfirmSuccess = async (result) => {
      try {
        ElMessage.success('供应商确认成功，任务已完成')
        supplierConfirmDialogVisible.value = false
        await fetchTasks()
        if (currentTask.value) {
          const updated = taskList.value.find(t => t.task_id === currentTask.value.task_id)
          if (updated) currentTask.value = { ...updated }
        }
      } catch (error) {
        ElMessage.error('刷新任务列表失败')
      }
    }

    // 处理打开申诉对话框
    const handleOpenAppealDialog = (task) => {
      currentTask.value = task
      supplierAppealDialogVisible.value = true
    }

    // 处理申诉成功
    const handleAppealSuccess = async (result) => {
      try {
        ElMessage.success('申诉提交成功，请等待审核')
        supplierAppealDialogVisible.value = false
        await fetchTasks()
        if (currentTask.value) {
          const updated = taskList.value.find(t => t.task_id === currentTask.value.task_id)
          if (updated) currentTask.value = { ...updated }
        }
      } catch (error) {
        ElMessage.error('刷新任务列表失败')
      }
    }

    // 新增：核查按钮相关
    const canShowWorkshopVerify = (taskRow) => {
      const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
      const hasRole = (names) => rolesArr.some(r => names.includes(r))
      return (
        (taskRow?.status === '待核查') &&
        hasRole(['车间地调', 'workshop_dispatcher'])
      )
    }

    // 判断是否显示申诉审核按钮
    const canShowAppealReview = (taskRow) => {
      const rolesArr = Array.isArray(permissionStore.roles) ? permissionStore.roles : []
      const hasRole = (names) => rolesArr.some(r => names.includes(r))
      return (
        (taskRow?.status === '申诉待审核') &&
        hasRole(['管理员', 'admin', '调度员', 'dispatcher', '超级管理员', '区域调度员'])
      )
    }

    // 打开申诉审核对话框
    const openAppealReviewDialog = (taskRow) => {
      currentTask.value = taskRow
      appealReviewDialogVisible.value = true
    }

    // 处理申诉审核成功
    const handleAppealReviewSuccess = async (result) => {
      try {
        ElMessage.success(`申诉${result.result === 'approved' ? '通过' : '驳回'}成功`)
        appealReviewDialogVisible.value = false
        await fetchTasks()
        if (currentTask.value) {
          const updated = taskList.value.find(t => t.task_id === currentTask.value.task_id)
          if (updated) currentTask.value = { ...updated }
        }
      } catch (error) {
        ElMessage.error('刷新任务列表失败')
      }
    }

    const openWorkshopVerify = (taskRow) => {
      // 跳转到独立的核查页面
      router.push({
        name: 'WorkshopVerification',
        params: { taskId: taskRow.task_id }
      })
    }

    // 处理任务详情更新（来自子组件）
    const handleTaskUpdated = async (updateData) => {
      try {
        ElMessage.success(`任务${updateData.action}操作成功`)
        // 刷新任务列表
        await fetchTasks()
        // 更新当前任务数据
        if (currentTask.value) {
          const updated = taskList.value.find(t => t.task_id === currentTask.value.task_id)
          if (updated) currentTask.value = { ...updated }
        }
      } catch (error) {
        ElMessage.error('刷新任务列表失败')
      }
    }

    // 处理任务详情对话框关闭
    const handleTaskDetailClose = () => {
      currentTask.value = null
      autoOpenWorkshopVerify.value = false
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
      hasPermission,
      canCreateTask,
      getPriorityType, // 暴露给模板
      getPriorityText,  // 暴露给模板
      handleTaskUpdated,
      handleTaskDetailClose,
      getRoleBasedResponseText,
      // 新增：响应表单相关
      supplierResponseDialogVisible,
      canSeeSupplierResponse,
      openSupplierResponseDialog,
      getResponseDialogTitle,
      handleResponseSuccessFromList,
      // 新增：供应商确认相关
      supplierConfirmDialogVisible,
      canShowSupplierConfirm,
      openSupplierConfirmDialog,
      handleSupplierConfirmSuccess,
      // 新增：申诉相关
      supplierAppealDialogVisible,
      handleOpenAppealDialog,
      handleAppealSuccess,
      // 新增：申诉审核相关
      appealReviewDialogVisible,
      canShowAppealReview,
      openAppealReviewDialog,
      handleAppealReviewSuccess,
      // 新增：核查按钮相关
      canShowWorkshopVerify,
      openWorkshopVerify,
      autoOpenWorkshopVerify
    }
  }
}
</script>

<style scoped>
/* 移除自定义的表头样式，让Element Plus使用默认样式 */
.dispatch-tasks-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.box-card {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: none;
  background: #ffffff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 2px solid #e4e7ed;
  margin-bottom: 24px;
}

.card-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.filter-container {
  margin-bottom: 24px;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #ebeef5;
}

.filter-container .el-form-item {
  margin-bottom: 0;
  margin-right: 16px;
}

.filter-container .el-form-item__label {
  font-weight: 500;
  color: #606266;
}

.filter-container .el-input__inner,
.filter-container .el-select .el-input__inner {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.filter-container .el-input__inner:focus,
.filter-container .el-select .el-input__inner:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.el-table {
  margin-top: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #ebeef5;
}

.el-table th.el-table__cell {
  /* 恢复Element Plus默认样式 */
  background-color: #f5f7fa;
  color: #606266;
  font-weight: bold;
  font-size: 14px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.el-table td.el-table__cell {
  padding: 12px 8px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background-color: #fafbfc;
}

.el-table--enable-row-hover .el-table__body tr:hover > td {
  background-color: #f0f7ff;
  transition: background-color 0.3s ease;
}

.el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.el-button--default:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.el-tag {
  border-radius: 6px;
  font-weight: 500;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #ebeef5;
}

.el-pagination .btn-prev,
.el-pagination .btn-next,
.el-pagination .el-pager li {
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.el-pagination .el-pager li.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: #ffffff;
}

.el-pagination .el-pager li:hover:not(.active) {
  color: #667eea;
  border-color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dispatch-tasks-container {
    padding: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .card-header h2 {
    font-size: 24px;
  }

  .filter-container {
    padding: 16px;
  }

  .filter-container .el-form-item {
    margin-right: 0;
    width: 100%;
    margin-bottom: 12px;
  }

  .filter-container .el-form-item:last-child {
    margin-bottom: 0;
  }

  .el-table {
    font-size: 14px;
  }

  .el-table th.el-table__cell,
  .el-table td.el-table__cell {
    padding: 12px 8px;
  }

  .pagination-container {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .card-header h2 {
    font-size: 20px;
  }

  .el-table th.el-table__cell,
  .el-table td.el-table__cell {
    padding: 8px 4px;
    font-size: 12px;
  }
}
</style>