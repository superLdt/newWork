<template>
  <div class="permission-management">
    <el-card class="permission-card">
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button 
            type="primary" 
            @click="showAddPermissionDialog"
            v-permission="'permission:create'"
          >
            <el-icon><Plus /></el-icon>
            添加权限
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索权限名称或代码"
          style="width: 300px; margin-right: 20px;"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select 
          v-model="resourceTypeFilter" 
          placeholder="资源类型" 
          style="width: 120px; margin-right: 20px;"
          clearable
          @change="handleSearch"
        >
          <el-option label="全部" value=""></el-option>
          <el-option label="菜单" value="menu"></el-option>
          <el-option label="API" value="api"></el-option>
          <el-option label="按钮" value="button"></el-option>
        </el-select>
        
        <el-select 
          v-model="actionFilter" 
          placeholder="操作类型" 
          style="width: 120px; margin-right: 20px;"
          clearable
          @change="handleSearch"
        >
          <el-option label="全部" value=""></el-option>
          <el-option label="查看" value="read"></el-option>
          <el-option label="编辑" value="write"></el-option>
          <el-option label="删除" value="delete"></el-option>
          <el-option label="执行" value="execute"></el-option>
        </el-select>
        
        <el-button 
          type="info" 
          @click="getStatistics"
          v-permission="'permission:read'"
        >
          <el-icon><DataAnalysis /></el-icon>
          统计信息
        </el-button>
      </div>
      
      <el-table 
        :data="permissions" 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="权限名称" min-width="150"></el-table-column>
        <el-table-column prop="code" label="权限代码" min-width="150"></el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100">
          <template #default="scope">
            <el-tag :type="getResourceTypeTagType(scope.row.resource_type)">
              {{ getResourceTypeLabel(scope.row.resource_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="100">
          <template #default="scope">
            <el-tag :type="getActionTagType(scope.row.action)">
              {{ getActionLabel(scope.row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_id" label="资源标识" min-width="120"></el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              @click="editPermission(scope.row)"
              v-permission="'permission:update'"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deletePermission(scope.row)"
              v-permission="'permission:delete'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalPermissions"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑权限对话框 -->
    <el-dialog
      :title="editingPermission.id ? '编辑权限' : '添加权限'"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form 
        :model="editingPermission" 
        :rules="permissionRules" 
        ref="permissionForm"
        label-width="100px"
      >
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="editingPermission.name" placeholder="请输入权限名称" />
        </el-form-item>
        
        <el-form-item label="权限代码" prop="code">
          <el-input 
            v-model="editingPermission.code" 
            placeholder="请输入权限代码，如：user:create"
            :disabled="!!editingPermission.id"
          />
        </el-form-item>
        
        <el-form-item label="资源类型" prop="resource_type">
          <el-select v-model="editingPermission.resource_type" style="width: 100%;" placeholder="请选择资源类型">
            <el-option label="菜单" value="menu"></el-option>
            <el-option label="API接口" value="api"></el-option>
            <el-option label="按钮" value="button"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="操作类型" prop="action">
          <el-select v-model="editingPermission.action" style="width: 100%;" placeholder="请选择操作类型">
            <el-option label="查看" value="read"></el-option>
            <el-option label="编辑" value="write"></el-option>
            <el-option label="删除" value="delete"></el-option>
            <el-option label="执行" value="execute"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="资源标识" prop="resource_id">
          <el-input 
            v-model="editingPermission.resource_id" 
            placeholder="请输入资源标识，如：/users 或 user_management"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="editingPermission.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入权限描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="savePermission" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 统计信息对话框 -->
    <el-dialog
      title="权限统计信息"
      v-model="statisticsVisible"
      width="500px"
    >
      <div v-if="statistics">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总权限数">{{ statistics.total_permissions }}</el-descriptions-item>
          <el-descriptions-item label="使用中权限">{{ statistics.used_permissions }}</el-descriptions-item>
          <el-descriptions-item label="未使用权限">{{ statistics.unused_permissions }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 20px;">资源类型分布</h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item 
            v-for="(count, type) in statistics.resource_type_stats" 
            :key="type"
            :label="getResourceTypeLabel(type)"
          >
            {{ count }}
          </el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 20px;">操作类型分布</h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item 
            v-for="(count, action) in statistics.action_stats" 
            :key="action"
            :label="getActionLabel(action)"
          >
            {{ count }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, DataAnalysis } from '@element-plus/icons-vue'
import { usePermissionStore } from '@/stores/permission'

// 使用权限store
const permissionStore = usePermissionStore()

// 响应式数据
const permissions = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const statisticsVisible = ref(false)
const statistics = ref(null)

// 搜索和过滤
const searchKeyword = ref('')
const resourceTypeFilter = ref('')
const actionFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalPermissions = ref(0)

// 编辑表单
const permissionForm = ref()
const editingPermission = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  resource_type: '',
  resource_id: '',
  action: ''
})

// 表单验证规则
const permissionRules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_:]+$/, message: '权限代码只能包含字母、数字、下划线和冒号', trigger: 'blur' }
  ],
  resource_type: [
    { required: true, message: '请选择资源类型', trigger: 'change' }
  ],
  action: [
    { required: true, message: '请选择操作类型', trigger: 'change' }
  ]
}

// 生命周期
onMounted(() => {
  loadPermissions()
})

// 方法
async function loadPermissions() {
  try {
    loading.value = true
    
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (resourceTypeFilter.value) {
      params.resource_type = resourceTypeFilter.value
    }
    if (actionFilter.value) {
      params.action = actionFilter.value
    }
    
    const response = await permissionStore.getAllPermissions(params)
    
    if (response.code === 200) {
      permissions.value = response.data.items
      totalPermissions.value = response.data.total
    } else {
      ElMessage.error(response.message || '获取权限列表失败')
    }
  } catch (error) {
    ElMessage.error('获取权限列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadPermissions()
}

function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
  loadPermissions()
}

function handleCurrentChange(val) {
  currentPage.value = val
  loadPermissions()
}

function showAddPermissionDialog() {
  resetForm()
  dialogVisible.value = true
}

function editPermission(permission) {
  Object.assign(editingPermission, permission)
  dialogVisible.value = true
}

async function savePermission() {
  try {
    await permissionForm.value.validate()
    
    saving.value = true
    
    if (editingPermission.id) {
      // 编辑权限
      await permissionStore.updatePermission(editingPermission.id, editingPermission)
    } else {
      // 添加权限
      await permissionStore.createPermission(editingPermission)
    }
    
    dialogVisible.value = false
    await loadPermissions()
    
  } catch (error) {
    // 错误信息已在store中处理
  } finally {
    saving.value = false
  }
}

async function deletePermission(permission) {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限 "${permission.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await permissionStore.deletePermission(permission.id)
    await loadPermissions()
    
  } catch (error) {
    if (error !== 'cancel') {
      // 错误信息已在store中处理
    }
  }
}

async function getStatistics() {
  try {
    const response = await permissionStore.getAllPermissions({ statistics: true })
    if (response.code === 200) {
      statistics.value = response.data
      statisticsVisible.value = true
    }
  } catch (error) {
    ElMessage.error('获取统计信息失败: ' + error.message)
  }
}

function resetForm() {
  Object.assign(editingPermission, {
    id: null,
    name: '',
    code: '',
    description: '',
    resource_type: '',
    resource_id: '',
    action: ''
  })
  
  nextTick(() => {
    permissionForm.value?.resetFields()
  })
}

// 辅助方法
function getResourceTypeLabel(type) {
  const labels = {
    menu: '菜单',
    api: 'API',
    button: '按钮'
  }
  return labels[type] || type
}

function getResourceTypeTagType(type) {
  const types = {
    menu: 'primary',
    api: 'success',
    button: 'warning'
  }
  return types[type] || 'info'
}

function getActionLabel(action) {
  const labels = {
    read: '查看',
    write: '编辑',
    delete: '删除',
    execute: '执行'
  }
  return labels[action] || action
}

function getActionTagType(action) {
  const types = {
    read: 'info',
    write: 'primary',
    delete: 'danger',
    execute: 'warning'
  }
  return types[action] || 'info'
}
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination-bar {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>