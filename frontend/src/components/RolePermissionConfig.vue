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
      permissions: [],
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
      
      this.permissions.forEach(permission => {
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
      try {
        // 获取所有权限
        const allPermissionsResponse = await apiService.permissions.getPermissions()
        if (allPermissionsResponse.code === 200) {
          this.permissions = allPermissionsResponse.data
        } else {
          ElMessage.error('获取权限列表失败')
        }
        
        // 获取角色已有权限
        const rolePermissionsResponse = await apiService.roles.getRolePermissions(this.role.id)
        if (rolePermissionsResponse.code === 200) {
          this.selectedPermissions = rolePermissionsResponse.data.map(p => p.id)
        } else {
          ElMessage.error('获取角色权限失败')
        }
      } catch (error) {
        ElMessage.error('加载权限数据失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    async savePermissions() {
      this.loading = true
      try {
        const selectedPermissionIds = this.$refs.permissionTree.getCheckedKeys()
          .filter(id => !id.toString().startsWith('group_')) // 过滤掉分组ID
        
        const response = await apiService.roles.updateRolePermissions(
          this.role.id, 
          { permission_ids: selectedPermissionIds }
        )
        
        if (response.code === 200) {
          ElMessage.success('权限更新成功')
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