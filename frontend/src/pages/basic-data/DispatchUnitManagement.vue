<template>
  <div class="dispatch-unit-management">
    <el-card class="unit-card">
      <template #header>
        <div class="card-header">
          <span>派车单位管理</span>
          <el-button type="primary" @click="showAddUnitDialog" v-if="hasPermission('dispatch_unit:create')">
            <el-icon><Plus /></el-icon>
            添加派车单位
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索单位名称或联系人"
          style="width: 300px; margin-right: 20px;"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态" style="width: 120px; margin-right: 20px;" @change="handleSearch">
          <el-option label="全部" value=""></el-option>
          <el-option label="启用" value="true"></el-option>
          <el-option label="禁用" value="false"></el-option>
        </el-select>
        <el-select v-model="typeFilter" placeholder="单位类型" style="width: 120px;" @change="handleSearch">
          <el-option label="全部" value=""></el-option>
          <el-option label="供应商" value="供应商"></el-option>
          <el-option label="内部单位" value="内部单位"></el-option>
          <el-option label="外包驾驶管理公司" value="外包驾驶管理公司"></el-option>
        </el-select>
      </div>
      
      <el-table 
        :data="unitList" 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="name" label="单位名称" width="200" />
        <el-table-column prop="unit_type" label="单位类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.unit_type === '供应商' ? 'success' : 'info'">
              {{ scope.row.unit_type || '未设置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="contact_person" label="联系人" width="120" />
        <el-table-column prop="contact_phone" label="联系电话" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewUnit(scope.row)" v-if="hasPermission('dispatch_unit:read')">查看</el-button>
            <el-button size="small" type="primary" @click="editUnit(scope.row)" v-if="hasPermission('dispatch_unit:update')">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteUnit(scope.row)" v-if="hasPermission('dispatch_unit:delete')">删除</el-button>
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
    
    <!-- 添加/编辑派车单位对话框 -->
    <el-dialog
      v-model="unitDialogVisible"
      :title="isEdit ? '编辑派车单位' : '添加派车单位'"
      width="60%"
    >
      <el-form
        ref="unitFormRef"
        :model="unitForm"
        :rules="unitFormRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位名称" prop="name">
              <el-input v-model="unitForm.name" placeholder="请输入单位名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位类型" prop="unit_type">
              <el-select v-model="unitForm.unit_type" placeholder="请选择单位类型" style="width: 100%">
                <el-option label="供应商" value="供应商"></el-option>
                <el-option label="内部单位" value="内部单位"></el-option>
                <el-option label="外包驾驶管理公司" value="外包驾驶管理公司"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="unitForm.contact_person" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="unitForm.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="unitForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="is_active">
              <el-switch
                v-model="unitForm.is_active"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="地址" prop="address">
              <el-input v-model="unitForm.address" placeholder="请输入地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="银行名称" prop="bank_name">
              <el-input v-model="unitForm.bank_name" placeholder="请输入银行名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号" prop="account_number">
              <el-input v-model="unitForm.account_number" placeholder="请输入银行账号" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="unitDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUnitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { usePermissionStore } from '@/stores/permission'
import { dispatchUnitService } from '@/services/dispatchUnitService'

export default {
  name: 'DispatchUnitManagement',
  components: {
    Plus,
    Search
  },
  setup() {
    const permissionStore = usePermissionStore()
    
    // 数据状态
    const loading = ref(false)
    const unitList = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    
    // 搜索过滤
    const searchKeyword = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    
    // 对话框状态
    const unitDialogVisible = ref(false)
    const isEdit = ref(false)
    const unitFormRef = ref(null)
    
    // 表单数据
    const unitForm = reactive({
      id: null,
      name: '',
      unit_type: '',
      contact_person: '',
      contact_phone: '',
      email: '',
      address: '',
      bank_name: '',
      account_number: '',
      is_active: true
    })
    
    // 表单验证规则
    const unitFormRules = {
      name: [
        { required: true, message: '请输入单位名称', trigger: 'blur' }
      ],
      unit_type: [
        { required: true, message: '请选择单位类型', trigger: 'change' }
      ],
      contact_person: [
        { required: true, message: '请输入联系人', trigger: 'blur' }
      ],
      contact_phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
      ],
      email: [
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ]
    }
    
    // 获取派车单位列表
    const fetchUnits = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          per_page: pageSize.value,
          query: searchKeyword.value
        }
        
        const response = await dispatchUnitService.getDispatchUnitList(params)
        if (response.code === 0) {
          unitList.value = response.data.items
          total.value = response.data.total
        } else {
          ElMessage.error(response.message || '获取派车单位列表失败')
        }
      } catch (error) {
        console.error('获取派车单位列表失败:', error)
        ElMessage.error('获取派车单位列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 搜索处理
    const handleSearch = () => {
      currentPage.value = 1
      fetchUnits()
    }
    
    // 分页处理
    const handleSizeChange = (size) => {
      pageSize.value = size
      fetchUnits()
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchUnits()
    }
    
    // 显示添加对话框
    const showAddUnitDialog = () => {
      isEdit.value = false
      resetUnitForm()
      unitDialogVisible.value = true
    }
    
    // 查看派车单位
    const viewUnit = (unit) => {
      ElMessage.info('查看功能开发中')
    }
    
    // 编辑派车单位
    const editUnit = (unit) => {
      isEdit.value = true
      Object.assign(unitForm, unit)
      unitDialogVisible.value = true
    }
    
    // 删除派车单位
    const deleteUnit = async (unit) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除派车单位 "${unit.name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await dispatchUnitService.deleteDispatchUnit(unit.id)
        if (response.code === 0) {
          ElMessage.success('删除成功')
          fetchUnits()
        } else {
          ElMessage.error(response.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除派车单位失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }
    
    // 提交表单
    const submitUnitForm = async () => {
      try {
        await unitFormRef.value.validate()
        
        const response = isEdit.value 
          ? await dispatchUnitService.updateDispatchUnit(unitForm.id, unitForm)
          : await dispatchUnitService.createDispatchUnit(unitForm)
        
        if (response.code === 0) {
          ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
          unitDialogVisible.value = false
          fetchUnits()
        } else {
          ElMessage.error(response.message || (isEdit.value ? '更新失败' : '创建失败'))
        }
      } catch (error) {
        console.error('提交表单失败:', error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
    
    // 重置表单
    const resetUnitForm = () => {
      Object.assign(unitForm, {
        id: null,
        name: '',
        unit_type: '',
        contact_person: '',
        contact_phone: '',
        email: '',
        address: '',
        bank_name: '',
        account_number: '',
        is_active: true
      })
      if (unitFormRef.value) {
        unitFormRef.value.clearValidate()
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 权限检查
    const hasPermission = (permission) => {
      return permissionStore.hasPermission(permission)
    }
    
    // 初始化
    onMounted(() => {
      fetchUnits()
    })
    
    return {
      loading,
      unitList,
      total,
      currentPage,
      pageSize,
      searchKeyword,
      statusFilter,
      typeFilter,
      unitDialogVisible,
      isEdit,
      unitFormRef,
      unitForm,
      unitFormRules,
      fetchUnits,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      showAddUnitDialog,
      viewUnit,
      editUnit,
      deleteUnit,
      submitUnitForm,
      resetUnitForm,
      formatDate,
      hasPermission
    }
  }
}
</script>

<style scoped>
.dispatch-unit-management {
  padding: 20px;
}

.unit-card {
  margin-bottom: 20px;
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  text-align: right;
}
</style>