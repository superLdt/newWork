<template>
  <div class="user-management">
    <el-card class="user-card">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddUserDialog">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名或邮箱"
          style="width: 300px; margin-right: 20px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态" style="width: 120px; margin-right: 20px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="启用" value="active"></el-option>
          <el-option label="禁用" value="inactive"></el-option>
        </el-select>
        <el-select v-model="roleFilter" placeholder="角色" style="width: 120px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="管理员" value="admin"></el-option>
          <el-option label="经理" value="manager"></el-option>
          <el-option label="用户" value="user"></el-option>
        </el-select>
      </div>
      
      <el-table 
        :data="filteredUsers" 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="username" label="用户名"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag 
              :type="getRoleTagType(scope.row.role_id)"
            >
              {{ getRoleName(scope.row.role_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              active-value="active"
              inactive-value="inactive"
              @change="toggleUserStatus(scope.row)"
            />
            <span :class="scope.row.status === 'active' ? 'status-active' : 'status-inactive'">
              {{ scope.row.status === 'active' ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="assignRoles(scope.row)">分配角色</el-button>
            <el-button size="small" type="danger" @click="deleteUser(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalUsers"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      :title="editingUser.id ? '编辑用户' : '添加用户'"
      v-model="dialogVisible"
      width="500px"
      @close="resetForm"
    >
      <el-form 
        :model="editingUser" 
        :rules="userRules" 
        ref="userForm"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editingUser.username" :disabled="!!editingUser.id" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="editingUser.full_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editingUser.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="editingUser.phone" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser.id">
          <el-input v-model="editingUser.password" type="password" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword" v-if="!editingUser.id">
          <el-input v-model="editingUser.confirmPassword" type="password" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="editingUser.role_id" style="width: 100%;" placeholder="请选择角色">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 角色分配对话框 -->
    <UserRoleAssignment
      v-model="roleAssignmentVisible"
      :user="selectedUser"
      v-if="selectedUser"
    />
  </div>
</template>

<script>
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiService } from '@/services/api'
import UserRoleAssignment from '@/components/UserRoleAssignment.vue'

export default {
  name: 'UserManagement',
  components: {
    Plus,
    Search,
    UserRoleAssignment
  },
  data() {
    return {
      users: [],
      roles: [], // 添加角色列表数据
      searchKeyword: '',
      statusFilter: '',
      roleFilter: '',
      currentPage: 1,
      pageSize: 10,
      totalUsers: 0,
      loading: false,
      dialogVisible: false,
      roleAssignmentVisible: false,
      selectedUser: null,
      editingUser: {
        id: null,
        username: '',
        full_name: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',
        role_id: null // 改为 role_id 以匹配后端API
      },
      userRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        full_name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { 
            validator: (rule, value, callback) => {
              if (value !== this.editingUser.password) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ],
        role_id: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    filteredUsers() {
      // 由于我们已经从API获取数据，这里不再需要客户端过滤
      return this.users
    }
  },
  mounted() {
    this.loadUsers()
    this.loadRoles() // 加载角色列表
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const response = await apiService.users.getUsers({
          page: this.currentPage,
          per_page: this.pageSize
        })
        
        if (response.code === 200) {
          this.users = response.data.items.map(user => ({
            ...user,
            status: user.is_active ? 'active' : 'inactive',
            is_active: user.is_active,
            created_at: user.created_at ? new Date(user.created_at).toLocaleString() : '',
            // 从用户的角色列表中获取第一个角色ID
            role_id: user.roles && user.roles.length > 0 ? user.roles[0].id : null
          }))
          this.totalUsers = response.data.total
        } else {
          ElMessage.error(response.message || '获取用户列表失败')
        }
      } catch (error) {
        ElMessage.error('获取用户列表失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    async loadRoles() {
      try {
        const response = await apiService.roles.getRoles()
        if (response.code === 200) {
          this.roles = response.data
        }
      } catch (error) {
        ElMessage.error('获取角色列表失败: ' + error.message)
      }
    },
    getRoleName(roleId) {
      const role = this.roles.find(r => r.id === roleId)
      return role ? role.name : '未分配角色'
    },
    getRoleTagType(roleId) {
      const role = this.roles.find(r => r.id === roleId)
      if (!role) return 'info'
      return role.name.includes('管理员') ? 'danger' : 
             role.name.includes('经理') ? 'warning' : 'info'
    },
    showAddUserDialog() {
      this.dialogVisible = true
    },
    editUser(user) {
      this.editingUser = { 
        ...user, 
        password: '', 
        confirmPassword: '',
        full_name: user.full_name || user.fullname || '',
        role_id: user.role_id || (user.roles && user.roles.length > 0 ? user.roles[0].id : null)
      }
      this.dialogVisible = true
    },
    async saveUser() {
      this.$refs.userForm.validate(async (valid) => {
        if (valid) {
          try {
            let response
            if (this.editingUser.id) {
              // 编辑用户
              const userData = {
                full_name: this.editingUser.full_name,
                email: this.editingUser.email,
                phone: this.editingUser.phone,
                role_id: this.editingUser.role_id
              }
              
              // 如果密码不为空，则更新密码
              if (this.editingUser.password) {
                userData.password = this.editingUser.password
              }
              
              response = await apiService.users.updateUser(this.editingUser.id, userData)
            } else {
              // 添加用户
              const userData = {
                username: this.editingUser.username,
                full_name: this.editingUser.full_name,
                email: this.editingUser.email,
                phone: this.editingUser.phone,
                password: this.editingUser.password,
                role_id: this.editingUser.role_id
              }
              
              response = await apiService.users.createUser(userData)
            }
            
            if (response.code === 200) {
              ElMessage.success(this.editingUser.id ? '用户更新成功' : '用户添加成功')
              this.dialogVisible = false
              this.resetForm()
              this.loadUsers() // 重新加载用户列表
            } else {
              ElMessage.error(response.message || (this.editingUser.id ? '用户更新失败' : '用户添加失败'))
            }
          } catch (error) {
            ElMessage.error((this.editingUser.id ? '用户更新失败' : '用户添加失败') + ': ' + error.message)
          }
        }
      })
    },
    async deleteUser(user) {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${user.username}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await apiService.users.deleteUser(user.id)
        
        if (response.code === 200) {
          ElMessage.success('删除成功')
          this.loadUsers() // 重新加载用户列表
        } else {
          ElMessage.error(response.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + error.message)
        }
      }
    },
    async toggleUserStatus(user) {
      try {
        const response = await apiService.users.updateUser(user.id, { 
          is_active: user.status === 'active' 
        })
        
        if (response.code === 200) {
          ElMessage.success(`用户${user.status === 'active' ? '启用' : '禁用'}成功`)
          user.is_active = user.status === 'active'
        } else {
          ElMessage.error(response.message || '状态更新失败')
          // 恢复状态
          user.status = user.status === 'active' ? 'inactive' : 'active'
        }
      } catch (error) {
        ElMessage.error('状态更新失败: ' + error.message)
        // 恢复状态
        user.status = user.status === 'active' ? 'inactive' : 'active'
      }
    },
    resetForm() {
      this.editingUser = {
        id: null,
        username: '',
        full_name: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',
        role_id: null
      }
      this.$refs.userForm?.resetFields()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.loadUsers()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadUsers()
    },
    assignRoles(user) {
      this.selectedUser = user
      this.roleAssignmentVisible = true
    }
  }
}
</script>

<style scoped>
.user-management {
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

.status-active {
  color: #67c23a;
  margin-left: 5px;
}

.status-inactive {
  color: #909399;
  margin-left: 5px;
}
</style>