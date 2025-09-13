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
        <el-select v-model="roleFilter" placeholder="角色" style="width: 120px; margin-right: 20px;" @change="handleSearch">
          <el-option label="全部" value=""></el-option>
          <el-option label="管理员" value="admin"></el-option>
          <el-option label="经理" value="manager"></el-option>
          <el-option label="用户" value="user"></el-option>
        </el-select>
        <el-select v-model="dispatchUnitFilter" placeholder="派车单位" style="width: 150px;" @change="handleSearch">
          <el-option label="全部" value=""></el-option>
          <el-option label="未绑定" value="unbound"></el-option>
          <el-option
            v-for="unit in dispatchUnits"
            :key="unit.id"
            :label="unit.name"
            :value="unit.id"
          ></el-option>
        </el-select>
      </div>
      
      <el-table 
        :data="filteredUsers" 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="id" label="ID" width="70" align="center"></el-table-column>
        <el-table-column prop="username" label="用户名" width="120" show-overflow-tooltip></el-table-column>
        <el-table-column prop="full_name" label="姓名" width="100" show-overflow-tooltip></el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip></el-table-column>
        <el-table-column prop="phone" label="手机号" width="120" show-overflow-tooltip></el-table-column>
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="scope">
            <el-tag 
              :type="getRoleTagType(scope.row.role_id)"
              size="small"
            >
              {{ getRoleName(scope.row.role_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dispatch_unit" label="派车单位" width="120" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.dispatch_unit" type="info" size="small">
              {{ scope.row.dispatch_unit.name }}
            </el-tag>
            <span v-else class="text-gray-400">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <div class="status-cell">
              <el-switch
                v-model="scope.row.status"
                active-value="active"
                inactive-value="inactive"
                @change="toggleUserStatus(scope.row)"
                size="small"
              />
              <span :class="scope.row.status === 'active' ? 'status-active' : 'status-inactive'" class="status-text">
                {{ scope.row.status === 'active' ? '启用' : '禁用' }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <div class="action-group">
              <el-dropdown trigger="click" @command="handleCommand">
                <el-button size="small" type="primary">
                  操作 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{action: 'edit', user: scope.row}">
                      <el-icon><Edit /></el-icon> 编辑
                    </el-dropdown-item>
                    <el-dropdown-item :command="{action: 'roles', user: scope.row}">
                      <el-icon><User /></el-icon> 分配角色
                    </el-dropdown-item>
                    <el-dropdown-item :command="{action: 'bind', user: scope.row}">
                      <el-icon><Connection /></el-icon> 绑定单位
                    </el-dropdown-item>
                    <el-dropdown-item divided :command="{action: 'delete', user: scope.row}">
                      <el-icon><Delete /></el-icon> 删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
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
      @success="loadUsers"
      v-if="selectedUser"
    />
    
    <!-- 派车单位绑定对话框 -->
    <el-dialog
      title="绑定派车单位"
      v-model="dispatchUnitBindVisible"
      width="500px"
      @close="resetDispatchUnitForm"
    >
      <el-form 
        :model="dispatchUnitForm" 
        :rules="dispatchUnitRules" 
        ref="dispatchUnitFormRef"
        label-width="100px"
      >
        <el-form-item label="用户" prop="username">
          <el-input v-model="dispatchUnitForm.username" disabled />
        </el-form-item>
        <el-form-item label="当前单位" prop="current_unit">
          <el-input v-model="dispatchUnitForm.current_unit" disabled />
        </el-form-item>
        <el-form-item label="派车单位" prop="dispatch_unit_id">
          <el-select 
            v-model="dispatchUnitForm.dispatch_unit_id" 
            placeholder="请选择派车单位"
            style="width: 100%"
            clearable
            filterable
          >
            <el-option
              v-for="unit in dispatchUnits"
              :key="unit.id"
              :label="unit.name"
              :value="unit.id"
            >
              <span>{{ unit.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ unit.unit_type }}</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dispatchUnitBindVisible = false">取消</el-button>
          <el-button type="primary" @click="submitDispatchUnitBind" :loading="bindLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Plus, Search, Edit, User, Connection, Delete, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiService } from '@/services/api'
import { userService } from '@/services/userService'
import { dispatchUnitService } from '@/services/dispatchUnitService'
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
      dispatchUnits: [], // 派车单位列表
      searchKeyword: '',
      statusFilter: '',
      roleFilter: '',
      dispatchUnitFilter: '', // 派车单位筛选
      currentPage: 1,
      pageSize: 10,
      totalUsers: 0,
      loading: false,
      bindLoading: false,
      dialogVisible: false,
      roleAssignmentVisible: false,
      dispatchUnitBindVisible: false,
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
      dispatchUnitForm: {
        user_id: null,
        username: '',
        current_unit: '',
        dispatch_unit_id: null
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
      },
      dispatchUnitRules: {
        dispatch_unit_id: [
          { required: true, message: '请选择派车单位', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => {
        const matchesSearch = !this.searchKeyword || 
          user.username.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          user.email.toLowerCase().includes(this.searchKeyword.toLowerCase())
        
        const matchesStatus = !this.statusFilter || user.status === this.statusFilter
        const matchesRole = !this.roleFilter || user.role === this.roleFilter
        
        const matchesDispatchUnit = !this.dispatchUnitFilter || 
          (this.dispatchUnitFilter === 'unbound' && !user.dispatch_unit) ||
          (user.dispatch_unit && user.dispatch_unit.id == this.dispatchUnitFilter)
        
        return matchesSearch && matchesStatus && matchesRole && matchesDispatchUnit
      })
    }
  },
  mounted() {
    this.loadUsers()
    this.loadRoles() // 加载角色列表
    this.loadDispatchUnits() // 加载派车单位列表
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          per_page: this.pageSize,
          query: this.searchKeyword
        }
        
        const response = await userService.getUserList(params)
        
        if (response.code === 0) {
          this.users = response.data.items.map(user => ({
            ...user,
            status: user.is_active ? 'active' : 'inactive',
            is_active: user.is_active,
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
              
              response = await userService.updateUser(this.editingUser.id, userData)
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
              
              response = await userService.createUser(userData)
            }
            
            if (response.code === 0) {
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
        
        const response = await userService.deleteUser(user.id)
        
        if (response.code === 0) {
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
        const response = await userService.updateUser(user.id, { 
          is_active: user.status === 'active' 
        })
        
        if (response.code === 0) {
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
    // 搜索处理
    handleSearch() {
      this.currentPage = 1
      // 由于使用了计算属性filteredUsers，这里不需要重新加载数据
    },
    assignRoles(user) {
      this.selectedUser = user
      this.roleAssignmentVisible = true
    },
    // 绑定派车单位
    bindDispatchUnit(user) {
      this.dispatchUnitForm = {
        user_id: user.id,
        username: user.username,
        current_unit: user.dispatch_unit ? user.dispatch_unit.name : '未绑定',
        dispatch_unit_id: user.dispatch_unit ? user.dispatch_unit.id : null
      }
      this.dispatchUnitBindVisible = true
    },
    // 加载派车单位列表
    async loadDispatchUnits() {
      try {
        const response = await dispatchUnitService.getDispatchUnitList({ per_page: 1000 })
        if (response.code === 0) {
          this.dispatchUnits = response.data.items || []
        } else {
          ElMessage.error(response.message || '获取派车单位列表失败')
        }
      } catch (error) {
        console.error('获取派车单位列表失败:', error)
        ElMessage.error('获取派车单位列表失败')
      }
    },
    // 提交派车单位绑定
    async submitDispatchUnitBind() {
      try {
        await this.$refs.dispatchUnitFormRef.validate()
        
        this.bindLoading = true
        const response = await userService.bindUserToDispatchUnit(
          this.dispatchUnitForm.user_id,
          this.dispatchUnitForm.dispatch_unit_id
        )
        
        if (response.code === 0) {
          ElMessage.success('绑定成功')
          this.dispatchUnitBindVisible = false
          this.loadUsers() // 重新加载用户列表
        } else {
          ElMessage.error(response.message || '绑定失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('绑定失败: ' + error.message)
        }
      } finally {
        this.bindLoading = false
      }
    },
    // 重置派车单位表单
    resetDispatchUnitForm() {
      this.dispatchUnitForm = {
        user_id: null,
        username: '',
        current_unit: '',
        dispatch_unit_id: null
      }
      this.$refs.dispatchUnitFormRef?.resetFields()
    },
    handleCommand(command) {
      const { action, user } = command;
      switch (action) {
        case 'edit':
          this.editUser(user);
          break;
        case 'roles':
          this.assignRoles(user);
          break;
        case 'bind':
          this.bindDispatchUnit(user);
          break;
        case 'delete':
          this.deleteUser(user);
          break;
      }
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

.action-group {
  display: flex;
  justify-content: center;
}

.action-group .el-button--primary {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.action-group .el-button--primary:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #409eff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 14px;
}

@media screen and (max-width: 768px) {
  .action-group {
    justify-content: flex-start;
  }
  
  .action-group .el-button {
    padding: 4px 8px;
    font-size: 12px;
  }
}

.status-active {
  color: #67c23a;
  margin-left: 5px;
}

.status-inactive {
  color: #f56c6c;
  margin-left: 5px;
}

.status-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header-wrapper) {
  background-color: #f8f9fa;
}

:deep(.el-table__body-wrapper) {
  background-color: #ffffff;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
  transition: background-color 0.3s ease;
}

:deep(.el-table__cell) {
  padding: 12px 8px;
}

:deep(.el-table th) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
  font-size: 13px;
}

:deep(.el-table td) {
  font-size: 13px;
  color: #606266;
}

.text-gray-400 {
  color: #9ca3af;
  font-style: italic;
}

.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.el-table .el-table__cell {
  padding: 12px 0;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}
</style>