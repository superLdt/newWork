<template>
  <div class="tonnage-volume-mapping">
    <div class="page-header">
      <h2>吨位容积对应管理</h2>
      <el-button type="primary" @click="showCreateDialog" v-if="hasPermission('tonnage_volume:create')">
        <el-icon><Plus /></el-icon>
        新增映射
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form :model="searchForm" inline>
        <el-form-item label="吨位">
          <el-input v-model="searchForm.tonnage" placeholder="请输入吨位" clearable />
        </el-form-item>
        <el-form-item label="车辆等级">
          <el-select v-model="searchForm.vehicle_grade" placeholder="请选择车辆等级" clearable>
            <el-option label="A级" value="A" />
            <el-option label="B级" value="B" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchMappings">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="table-section">
      <el-table :data="mappings" v-loading="loading" stripe>
        <el-table-column prop="tonnage" label="吨位" width="100" />
        <el-table-column prop="min_volume" label="最小容积(m³)" width="120" />
        <el-table-column prop="standard_volume" label="标准容积(m³)" width="120" />
        <el-table-column prop="max_volume" label="最大容积(m³)" width="120" />
        <el-table-column prop="conversion_factor" label="转换系数" width="100" />
        <el-table-column prop="vehicle_grade" label="车辆等级" width="100">
          <template #default="{ row }">
            <el-tag :type="row.vehicle_grade === 'A' ? 'success' : 'warning'">
              {{ row.vehicle_grade }}级
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="showEditDialog(row)"
              v-if="hasPermission('tonnage_volume:update')"
            >
              编辑
            </el-button>
            <el-button 
              :type="row.is_active ? 'warning' : 'success'" 
              size="small" 
              @click="toggleStatus(row)"
              v-if="hasPermission('tonnage_volume:update')"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteMapping(row)"
              v-if="hasPermission('tonnage_volume:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchMappings"
          @current-change="fetchMappings"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      v-model="dialogVisible" 
      width="600px"
      @close="resetForm"
    >
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        label-width="120px"
      >
        <el-form-item label="吨位" prop="tonnage">
          <el-input v-model="form.tonnage" placeholder="请输入吨位，如：20" />
        </el-form-item>
        <el-form-item label="最小容积" prop="min_volume">
          <el-input-number 
            v-model="form.min_volume" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            placeholder="请输入最小容积"
          />
          <span class="unit">m³</span>
        </el-form-item>
        <el-form-item label="标准容积" prop="standard_volume">
          <el-input-number 
            v-model="form.standard_volume" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            placeholder="请输入标准容积"
          />
          <span class="unit">m³</span>
        </el-form-item>
        <el-form-item label="最大容积" prop="max_volume">
          <el-input-number 
            v-model="form.max_volume" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            placeholder="请输入最大容积"
          />
          <span class="unit">m³</span>
        </el-form-item>
        <el-form-item label="转换系数" prop="conversion_factor">
          <el-input-number 
            v-model="form.conversion_factor" 
            :precision="2" 
            :step="0.01" 
            :min="0"
            placeholder="请输入转换系数"
          />
        </el-form-item>
        <el-form-item label="车辆等级" prop="vehicle_grade">
          <el-select v-model="form.vehicle_grade" placeholder="请选择车辆等级">
            <el-option label="A级" value="A" />
            <el-option label="B级" value="B" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch 
            v-model="form.is_active" 
            active-text="启用" 
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { usePermissionStore } from '@/stores/permission'
const permissionStore = usePermissionStore()
const hasPermission = (code) => permissionStore.hasPermission?.value
  ? permissionStore.hasPermission.value(code)
  : false
import { formatDateTime } from '@/utils/dateUtils'
import tonnageVolumeService from '@/services/tonnageVolumeService'

// 响应式数据
const loading = ref(false)
const mappings = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)

// 搜索表单
const searchForm = reactive({
  tonnage: '',
  vehicle_grade: '',
  is_active: null
})

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 表单数据
const form = reactive({
  tonnage: '',
  min_volume: null,
  standard_volume: null,
  max_volume: null,
  conversion_factor: null,
  vehicle_grade: '',
  is_active: true
})

// 表单引用
const formRef = ref()

// 表单验证规则
const rules = {
  tonnage: [
    { required: true, message: '请输入吨位', trigger: 'blur' }
  ],
  min_volume: [
    { required: true, message: '请输入最小容积', trigger: 'blur' },
    { type: 'number', min: 0, message: '最小容积必须大于等于0', trigger: 'blur' }
  ],
  standard_volume: [
    { required: true, message: '请输入标准容积', trigger: 'blur' },
    { type: 'number', min: 0, message: '标准容积必须大于等于0', trigger: 'blur' }
  ],
  max_volume: [
    { required: true, message: '请输入最大容积', trigger: 'blur' },
    { type: 'number', min: 0, message: '最大容积必须大于等于0', trigger: 'blur' }
  ],
  conversion_factor: [
    { required: true, message: '请输入转换系数', trigger: 'blur' },
    { type: 'number', min: 0, message: '转换系数必须大于等于0', trigger: 'blur' }
  ],
  vehicle_grade: [
    { required: true, message: '请选择车辆等级', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  return isEdit.value ? '编辑吨位容积映射' : '新增吨位容积映射'
})

// 方法
const fetchMappings = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    
    const response = await tonnageVolumeService.getMappings(params)
    mappings.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  Object.assign(searchForm, {
    tonnage: '',
    vehicle_grade: '',
    is_active: null
  })
  pagination.page = 1
  fetchMappings()
}

const showCreateDialog = () => {
  isEdit.value = false
  currentId.value = null
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    tonnage: '',
    min_volume: null,
    standard_volume: null,
    max_volume: null,
    conversion_factor: null,
    vehicle_grade: '',
    is_active: true
  })
  formRef.value?.resetFields()
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 验证容积逻辑
    if (form.min_volume > form.standard_volume) {
      ElMessage.error('最小容积不能大于标准容积')
      return
    }
    if (form.standard_volume > form.max_volume) {
      ElMessage.error('标准容积不能大于最大容积')
      return
    }
    
    loading.value = true
    
    if (isEdit.value) {
      await tonnageVolumeService.updateMapping(currentId.value, form)
      ElMessage.success('更新成功')
    } else {
      await tonnageVolumeService.createMapping(form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchMappings()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (row) => {
  try {
    const action = row.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(`确定要${action}该映射吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tonnageVolumeService.updateMapping(row.id, {
      ...row,
      is_active: !row.is_active
    })
    
    ElMessage.success(`${action}成功`)
    fetchMappings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

const deleteMapping = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该映射吗？删除后不可恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tonnageVolumeService.deleteMapping(row.id)
    ElMessage.success('删除成功')
    fetchMappings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 生命周期
onMounted(() => {
  fetchMappings()
})
</script>

<style scoped>
.tonnage-volume-mapping {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.search-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.table-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.unit {
  margin-left: 8px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>