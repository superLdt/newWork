<template>
  <div class="role-management">
    <div v-if="currentView === 'list'">
      <el-card class="role-card">
        <template #header>
          <div class="card-header">
            <span>角色管理</span>
            <el-button type="primary" @click="showAddRoleDialog">
              <el-icon><Plus /></el-icon>
              添加角色
            </el-button>
          </div>
        </template>
        
        <el-table :data="roles" style="width: 100%" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="name" label="角色名称"></el-table-column>
          <el-table-column prop="description" label="描述"></el-table-column>
          <el-table-column prop="user_count" label="用户数" width="100"></el-table-column>
          <el-table-column label="操作" width="300">
            <template #default="scope">
              <el-button size="small" @click="editRole(scope.row)">编辑</el-button>
              <el-button size="small" type="primary" @click="configurePermissions(scope.row)">权限配置</el-button>
              <el-button size="small" type="success" @click="configureMenus(scope.row)">菜单配置</el-button>
              <el-button size="small" type="danger" @click="deleteRole(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <div v-else-if="currentView === 'permissions'">
      <role-permission-config 
        :role="selectedRole" 
        @cancel="currentView = 'list'" 
        @saved="handlePermissionsSaved"
      />
    </div>
    
    <div v-else-if="currentView === 'menus'">
      <menu-permission-config 
        :role="selectedRole" 
        @cancel="currentView = 'list'" 
        @saved="handleMenusSaved"
      />
    </div>
    
    <!-- 添加/编辑角色对话框 -->
    <el-dialog
      :title="editingRole.id ? '编辑角色' : '添加角色'"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form 
        :model="editingRole" 
        :rules="roleRules" 
        ref="roleForm"
        label-width="100px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="editingRole.name" :disabled="!!editingRole.id" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editingRole.description" type="textarea" />
        </el-form-item>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRole">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiService } from '@/services/api'
import RolePermissionConfig from '@/components/RolePermissionConfig.vue'
import MenuPermissionConfig from '@/components/MenuPermissionConfig.vue'

export default {
  name: 'RoleManagement',
  components: {
    Plus,
    RolePermissionConfig,
    MenuPermissionConfig
  },
  data() {
    return {
      roles: [],
      loading: false,
      dialogVisible: false,
      currentView: 'list', // 'list', 'permissions', 'menus'
      selectedRole: null,
      editingRole: {
        id: null,
        name: '',
        description: '',
        permissions: []
      },
      roleRules: {
        name: [
          { required: true, message: '请输入角色名称', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入描述', trigger: 'blur' }
        ]
      },

    }
  },
  mounted() {
    this.loadRoles()
  },
  methods: {
    async loadRoles() {
      this.loading = true
      try {
        const response = await apiService.roles.getRoles()
        
        if (response.code === 200) {
          // 使用后端返回的角色数据，后端已经包含user_count字段
          this.roles = response.data
        } else {
          ElMessage.error(response.message || '获取角色列表失败')
        }
      } catch (error) {
        ElMessage.error('获取角色列表失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    showAddRoleDialog() {
      this.dialogVisible = true
    },
    editRole(role) {
      this.editingRole = { ...role }
      this.dialogVisible = true
    },
    async saveRole() {
      this.$refs.roleForm.validate(async (valid) => {
        if (valid) {
          try {
            // 移除权限相关代码，因为后端API只支持更新描述
            let response
            if (this.editingRole.id) {
              // 编辑角色 - 只更新描述
              response = await apiService.roles.updateRole(this.editingRole.id, {
                description: this.editingRole.description
              })
            } else {
              // 添加角色
              response = await apiService.roles.createRole({
                name: this.editingRole.name,
                description: this.editingRole.description
              })
            }
            
            if (response.code === 200 || response.code === 201) {
              ElMessage.success(this.editingRole.id ? '角色更新成功' : '角色添加成功')
              this.dialogVisible = false
              this.resetForm()
              this.loadRoles() // 重新加载角色列表
            } else {
              ElMessage.error(response.message || (this.editingRole.id ? '角色更新失败' : '角色添加失败'))
            }
          } catch (error) {
            ElMessage.error((this.editingRole.id ? '角色更新失败' : '角色添加失败') + ': ' + error.message)
          }
        }
      })
    },
    async deleteRole(role) {
      // 检查角色是否有关联用户
      if (role.user_count > 0) {
        ElMessage.warning('该角色下有关联用户，无法删除')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          `确定要删除角色 "${role.name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await apiService.roles.deleteRole(role.id)
        
        if (response.code === 200) {
          ElMessage.success('删除成功')
          this.loadRoles() // 重新加载角色列表
        } else {
          ElMessage.error(response.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + error.message)
        }
      }
    },
    resetForm() {
      this.editingRole = {
        id: null,
        name: '',
        description: ''
      }
      this.$refs.roleForm?.resetFields()
    },
    configurePermissions(role) {
      this.selectedRole = { ...role }
      this.currentView = 'permissions'
    },
    configureMenus(role) {
      this.selectedRole = { ...role }
      this.currentView = 'menus'
    },
    handlePermissionsSaved() {
      ElMessage.success('权限配置已保存')
      this.currentView = 'list'
    },
    handleMenusSaved() {
      ElMessage.success('菜单权限配置已保存')
      this.currentView = 'list'
    }
  }
}
</script>

<style scoped>
.role-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>