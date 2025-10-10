<template>
  <div class="role-permission-config">
    <el-card class="permission-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ role.name }} - 权限配置</span>
          <div>
            <el-button @click="$emit('cancel')">返回</el-button>
            <el-button type="primary" @click="savePermissions">保存</el-button>
          </div>
        </div>
      </template>
      
      <div class="permission-tree-container">
        <el-input
          v-model="filterText"
          placeholder="搜索权限"
          clearable
          prefix-icon="Search"
          class="filter-input"
        />
        
        <el-tree
          ref="permissionTree"
          :data="permissionGroups"
          show-checkbox
          node-key="id"
          :props="defaultProps"
          :filter-node-method="filterNode"
          :default-checked-keys="selectedPermissions"
          class="permission-tree"
          :empty-text="'暂无权限数据'"
        >
          <template #default="{ node, data }">
            <span class="custom-tree-node">
              <span>{{ node.label }}</span>
              <span v-if="data.description" class="permission-description">{{ data.description }}</span>
            </span>
          </template>
        </el-tree>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { apiService } from '@/services/api'

export default {
  name: 'RolePermissionConfig',
  components: {
    Search
  },
  props: {
    role: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      permissions: [], // 确保初始化为空数组
      selectedPermissions: [],
      filterText: '',
      defaultProps: {
        children: 'children',
        label: 'name'
      }
    }
  },
  computed: {
    permissionGroups() {
      // 将权限按模块分组
      const groups = {}
      
      // 确保 permissions 是数组
      if (!Array.isArray(this.permissions)) {
        console.error('permissions 不是数组:', this.permissions)
        return []
      }
      
      this.permissions.forEach(permission => {
        // 确保 permission 对象有效
        if (!permission || !permission.code) {
          console.warn('无效的权限对象:', permission)
          return
        }
        
        const [module] = permission.code.split(':')
        if (!groups[module]) {
          groups[module] = {
            id: `group_${module}`,
            name: this.formatModuleName(module),
            children: []
          }
        }
        
        groups[module].children.push({
          id: permission.id,
          name: this.formatPermissionName(permission.code),
          code: permission.code,
          description: permission.description
        })
      })
      
      return Object.values(groups)
    }
  },
  watch: {
    filterText(val) {
      this.$refs.permissionTree.filter(val)
    },
    role: {
      immediate: true,
      handler() {
        this.loadPermissions()
      }
    }
  },
  methods: {
    async loadPermissions() {
      this.loading = true
      // 确保初始化为空数组
      this.permissions = []
      this.selectedPermissions = []
      
      try {
        // 获取所有权限（显式请求大页尺寸，避免分页导致空数据）
        const allPermissionsResponse = await apiService.permissions.getPermissions({ page: 1, per_page: 1000 })
        console.log('所有权限响应:', allPermissionsResponse)
        if (allPermissionsResponse.code === 200) {
          // 确保数据是数组
          if (allPermissionsResponse.data && Array.isArray(allPermissionsResponse.data)) {
            this.permissions = allPermissionsResponse.data
          } else if (allPermissionsResponse.data && Array.isArray(allPermissionsResponse.data.items)) {
            // 处理分页结构 { items: [], total: n }
            this.permissions = allPermissionsResponse.data.items
          } else if (allPermissionsResponse.data && Array.isArray(allPermissionsResponse.data.permissions)) {
            // 处理嵌套结构 { permissions: [] }
            this.permissions = allPermissionsResponse.data.permissions
          } else {
            this.permissions = []
          }
          console.log('处理后的所有权限:', this.permissions, '数量:', this.permissions.length)
        } else {
          ElMessage.error('获取权限列表失败')
        }
        
        // 获取角色已有权限
        const rolePermissionsResponse = await apiService.roles.getRolePermissions(this.role.id)
        if (rolePermissionsResponse.code === 200 && rolePermissionsResponse.data) {
          // 处理嵌套数据结构
          console.log('角色权限响应数据:', rolePermissionsResponse.data)
          
          // 检查数据结构中是否包含permissions字段
          let permissionsData = []
          if (Array.isArray(rolePermissionsResponse.data.permissions)) {
            permissionsData = rolePermissionsResponse.data.permissions
          } else if (Array.isArray(rolePermissionsResponse.data)) {
            // 尝试直接使用data，如果它是数组
            permissionsData = rolePermissionsResponse.data
          }
          console.log('角色已有权限数据:', permissionsData)
          this.selectedPermissions = permissionsData.map(p => p.id)

          // 如果所有权限为空，但角色权限不为空，则回退使用角色权限以避免树显示“暂无数据”
          if (this.permissions.length === 0 && permissionsData.length > 0) {
            console.warn('所有权限列表为空，使用角色已有权限作为显示数据（临时回退）')
            this.permissions = permissionsData
          }
        } else {
          ElMessage.error('获取角色权限失败')
        }

        // 等下一个tick，确保树节点已渲染后再设置勾选状态
        this.$nextTick(() => {
          try {
            this.$refs.permissionTree && this.$refs.permissionTree.setCheckedKeys(this.selectedPermissions)
          } catch (e) {
            console.warn('设置树勾选状态失败:', e)
          }
        })
      } catch (error) {
        console.error('加载权限数据失败:', error)
        ElMessage.error('加载权限数据失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading = false
      }
    },
    async savePermissions() {
      this.loading = true
      try {
        const selectedPermissionIds = this.$refs.permissionTree.getCheckedKeys()
          .filter(id => !id.toString().startsWith('group_')) // 过滤掉分组ID
        
        // 使用已存在的 API 方法以匹配后端路由 (PUT /role-permissions/roles/:id/permissions)
        const response = await apiService.roles.updateRolePermissions(
          this.role.id,
          { permission_ids: selectedPermissionIds }
        )
        
        if (response.code === 200) {
          // 由父组件统一展示成功提示，子组件不再弹出成功消息
          this.$emit('saved')
        } else {
          ElMessage.error(response.message || '权限更新失败')
        }
      } catch (error) {
        ElMessage.error('权限更新失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    filterNode(value, data) {
      if (!value) return true
      return data.name.toLowerCase().includes(value.toLowerCase())
    },
    formatModuleName(module) {
      // 将模块名称格式化为更友好的显示
      const moduleMap = {
        'user': '用户管理',
        'role': '角色管理',
        'permission': '权限管理',
        'menu': '菜单管理',
        'system': '系统管理',
        'audit': '审计日志'
      }
      
      return moduleMap[module] || module.charAt(0).toUpperCase() + module.slice(1)
    },
    formatPermissionName(code) {
      // 将权限代码格式化为更友好的显示
      const [, action] = code.split(':')
      
      const actionMap = {
        'create': '创建',
        'read': '查看',
        'update': '更新',
        'delete': '删除',
        'manage': '管理',
        'assign': '分配',
        'export': '导出',
        'import': '导入'
      }
      
      return actionMap[action] || action
    }
  }
}
</script>

<style scoped>
.role-permission-config {
  width: 100%;
}

.permission-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.permission-tree-container {
  margin-top: 20px;
}

.filter-input {
  margin-bottom: 15px;
}

.permission-tree {
  max-height: 500px;
  overflow-y: auto;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.permission-description {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}
</style>