<template>
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
</template>

<script>
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'PermissionTree',
  components: {
    Search
  },
  props: {
    permissions: {
      type: Array,
      required: true
    },
    selectedPermissions: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
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
    }
  },
  methods: {
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
    },
    getCheckedPermissions() {
      // 获取选中的权限ID
      return this.$refs.permissionTree.getCheckedKeys()
        .filter(id => !id.toString().startsWith('group_')) // 过滤掉分组ID
    },
    setCheckedPermissions(permissionIds) {
      // 设置选中的权限
      this.$refs.permissionTree.setCheckedKeys(permissionIds)
    }
  }
}
</script>

<style scoped>
.permission-tree-container {
  width: 100%;
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