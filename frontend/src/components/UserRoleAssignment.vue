<template>
  <div class="user-role-assignment">
    <el-dialog
      :title="`为用户 ${user.username} 分配角色`"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <div class="current-roles" v-if="userRoles.length > 0">
        <h4>当前角色</h4>
        <div class="role-tags">
          <el-tag
            v-for="role in userRoles"
            :key="role.id"
            type="info"
            closable
            @close="removeRole(role.id)"
          >
            {{ role.name }}
          </el-tag>
        </div>
      </div>
      
      <div class="assign-role">
        <h4>分配新角色</h4>
        <el-select
          v-model="selectedRoleId"
          placeholder="选择角色"
          style="width: 100%; margin-bottom: 10px;"
        >
          <el-option
            v-for="role in availableRoles"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
        <el-button
          type="primary"
          :disabled="!selectedRoleId"
          @click="assignRole"
        >
          分配角色
        </el-button>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { apiService } from '@/services/api'

export default {
  name: 'UserRoleAssignment',
  props: {
    user: {
      type: Object,
      required: true
    },
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      dialogVisible: this.modelValue,
      userRoles: [],
      allRoles: [],
      selectedRoleId: null,
      loading: false
    }
  },
  computed: {
    availableRoles() {
      const assignedRoleIds = this.userRoles.map(role => role.id)
      return this.allRoles.filter(role => !assignedRoleIds.includes(role.id))
    }
  },
  watch: {
    modelValue(val) {
      this.dialogVisible = val
      if (val) {
        this.loadUserRoles()
        this.loadAllRoles()
      }
    },
    dialogVisible(val) {
      this.$emit('update:modelValue', val)
    }
  },
  methods: {
    /**
     * 加载用户的角色列表
     */
    async loadUserRoles() {
      try {
        const response = await apiService.roles.getUserRoles(this.user.id)
        if (response.code === 200) {
          this.userRoles = response.data
        } else {
          ElMessage.error(response.message || '获取用户角色失败')
        }
      } catch (error) {
        ElMessage.error('获取用户角色失败: ' + error.message)
      }
    },
    
    /**
     * 加载所有角色列表
     */
    async loadAllRoles() {
      try {
        const response = await apiService.roles.getRoles()
        if (response.code === 200) {
          this.allRoles = response.data
        } else {
          ElMessage.error(response.message || '获取角色列表失败')
        }
      } catch (error) {
        ElMessage.error('获取角色列表失败: ' + error.message)
      }
    },
    
    /**
     * 为用户分配角色
     */
    async assignRole() {
      if (!this.selectedRoleId) return
      
      try {
        const response = await apiService.roles.assignRoleToUser(this.user.id, this.selectedRoleId)
        if (response.code === 200) {
          ElMessage.success('角色分配成功')
          this.selectedRoleId = null
          await this.loadUserRoles() // 重新加载用户角色
        } else {
          ElMessage.error(response.message || '角色分配失败')
        }
      } catch (error) {
        ElMessage.error('角色分配失败: ' + error.message)
      }
    },
    
    /**
     * 移除用户的角色
     */
    async removeRole(roleId) {
      try {
        const response = await apiService.roles.removeRoleFromUser(this.user.id, roleId)
        if (response.code === 200) {
          ElMessage.success('角色移除成功')
          await this.loadUserRoles() // 重新加载用户角色
        } else {
          ElMessage.error(response.message || '角色移除失败')
        }
      } catch (error) {
        ElMessage.error('角色移除失败: ' + error.message)
      }
    },
    
    /**
     * 重置表单
     */
    resetForm() {
      this.userRoles = []
      this.allRoles = []
      this.selectedRoleId = null
    }
  }
}
</script>

<style scoped>
.user-role-assignment {
  .current-roles {
    margin-bottom: 20px;
    
    h4 {
      margin-bottom: 10px;
      color: #606266;
    }
    
    .role-tags {
      .el-tag {
        margin-right: 8px;
        margin-bottom: 8px;
      }
    }
  }
  
  .assign-role {
    h4 {
      margin-bottom: 10px;
      color: #606266;
    }
  }
}
</style>