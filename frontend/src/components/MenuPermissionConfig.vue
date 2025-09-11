<template>
  <div class="menu-permission-config">
    <el-card class="menu-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ role.name }} - 菜单权限配置</span>
          <div>
            <el-button @click="$emit('cancel')">返回</el-button>
            <el-button type="primary" @click="saveMenuPermissions">保存</el-button>
          </div>
        </div>
      </template>
      
      <div class="menu-tree-container">
        <el-input
          v-model="filterText"
          placeholder="搜索菜单"
          clearable
          prefix-icon="Search"
          class="filter-input"
        />
        
        <el-tree
          ref="menuTree"
          :data="menuTree"
          show-checkbox
          node-key="id"
          :props="defaultProps"
          :filter-node-method="filterNode"
          :default-checked-keys="selectedMenus"
          class="menu-tree"
        >
          <template #default="{ node, data }">
            <span class="custom-tree-node">
              <span>
                <el-icon v-if="data.icon" class="menu-icon">
                  <component :is="data.icon" />
                </el-icon>
                {{ data.name }}
              </span>
              <span v-if="data.path" class="menu-path">{{ data.path }}</span>
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
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

export default {
  name: 'MenuPermissionConfig',
  components: {
    Search,
    ...ElementPlusIconsVue
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
      menus: [],
      selectedMenus: [],
      filterText: '',
      defaultProps: {
        children: 'children',
        label: 'name'
      }
    }
  },
  computed: {
    menuTree() {
      // 构建菜单树
      const rootMenus = this.menus.filter(menu => !menu.parent_id)
      return this.buildMenuTree(rootMenus)
    }
  },
  watch: {
    filterText(val) {
      this.$refs.menuTree.filter(val)
    },
    role: {
      immediate: true,
      handler() {
        this.loadMenus()
      }
    }
  },
  methods: {
    async loadMenus() {
      this.loading = true
      try {
        // 获取所有菜单
        const allMenusResponse = await apiService.menus.getMenus()
        if (allMenusResponse.code === 200) {
          this.menus = allMenusResponse.data
        } else {
          ElMessage.error('获取菜单列表失败')
        }
        
        // 获取角色已有菜单权限
        const roleMenusResponse = await apiService.roles.getRoleMenus(this.role.id)
        if (roleMenusResponse.code === 200) {
          this.selectedMenus = roleMenusResponse.data.map(m => m.id)
        } else {
          ElMessage.error('获取角色菜单权限失败')
        }
      } catch (error) {
        ElMessage.error('加载菜单数据失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    buildMenuTree(menus) {
      return menus.map(menu => {
        const children = this.menus.filter(m => m.parent_id === menu.id)
        const node = {
          id: menu.id,
          name: menu.name,
          path: menu.path,
          icon: menu.icon
        }
        
        if (children.length > 0) {
          node.children = this.buildMenuTree(children)
        }
        
        return node
      })
    },
    async saveMenuPermissions() {
      this.loading = true
      try {
        const selectedMenuIds = this.$refs.menuTree.getCheckedKeys()
        
        const response = await apiService.roles.updateRoleMenus(
          this.role.id, 
          { menu_ids: selectedMenuIds }
        )
        
        if (response.code === 200) {
          ElMessage.success('菜单权限更新成功')
          this.$emit('saved')
        } else {
          ElMessage.error(response.message || '菜单权限更新失败')
        }
      } catch (error) {
        ElMessage.error('菜单权限更新失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    filterNode(value, data) {
      if (!value) return true
      return data.name.toLowerCase().includes(value.toLowerCase())
    }
  }
}
</script>

<style scoped>
.menu-permission-config {
  width: 100%;
}

.menu-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-tree-container {
  margin-top: 20px;
}

.filter-input {
  margin-bottom: 15px;
}

.menu-tree {
  max-height: 500px;
  overflow-y: auto;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.menu-icon {
  margin-right: 5px;
}

.menu-path {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}
</style>