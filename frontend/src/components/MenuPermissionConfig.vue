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
        
        <!-- 批量操作按钮 -->
        <div class="batch-operations">
          <el-button size="small" @click="selectAll">全选</el-button>
          <el-button size="small" @click="unselectAll">全不选</el-button>
          <el-button size="small" @click="expandAll">展开全部</el-button>
          <el-button size="small" @click="collapseAll">收起全部</el-button>
        </div>
        
        <el-tree
          ref="menuTree"
          :data="menuTree"
          show-checkbox
          node-key="id"
          :props="defaultProps"
          :filter-node-method="filterNode"
          :default-checked-keys="selectedMenus"
          class="menu-tree"
          check-strictly="false"
          check-on-click-node
          :default-expand-all="true"
          empty-text="暂无菜单数据"
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
        const allMenusResponse = await apiService.menus.getMenus({ tree: false })
        if (allMenusResponse.code === 200) {
          this.menus = allMenusResponse.data
        } else {
          ElMessage.error('获取菜单列表失败')
        }
        
        // 获取角色已有菜单权限（现在返回完整菜单树，包含权限标记）
        const roleMenusResponse = await apiService.roles.getRoleMenus(this.role.id)
        if (roleMenusResponse.code === 200) {
          // 从返回的菜单树中提取有权限的菜单ID
          const extractPermissionIds = (nodes) => {
            if (!Array.isArray(nodes)) return []
            const ids = []
            const dfs = (arr) => {
              arr.forEach(n => {
                if (n.has_permission) {
                  ids.push(n.id)
                }
                if (n.children && n.children.length > 0) {
                  dfs(n.children)
                }
              })
            }
            dfs(nodes)
            return ids
          }
          
          this.selectedMenus = extractPermissionIds(roleMenusResponse.data)
          
          // 设置默认选中状态
          this.$nextTick(() => {
            if (this.$refs.menuTree) {
              this.$refs.menuTree.setCheckedKeys(this.selectedMenus)
            }
          })
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
    // 批量操作方法
    selectAll() {
      if (this.$refs.menuTree) {
        const allMenuIds = this.getAllMenuIds(this.menuTree)
        this.$refs.menuTree.setCheckedKeys(allMenuIds)
        ElMessage.success('已全选所有菜单')
      }
    },
    unselectAll() {
      if (this.$refs.menuTree) {
        this.$refs.menuTree.setCheckedKeys([])
        ElMessage.success('已取消选择所有菜单')
      }
    },
    expandAll() {
      if (this.$refs.menuTree) {
        const allMenuIds = this.getAllMenuIds(this.menuTree)
        allMenuIds.forEach(id => {
          this.$refs.menuTree.store.nodesMap[id].expanded = true
        })
        ElMessage.success('已展开所有菜单')
      }
    },
    collapseAll() {
      if (this.$refs.menuTree) {
        const allMenuIds = this.getAllMenuIds(this.menuTree)
        allMenuIds.forEach(id => {
          this.$refs.menuTree.store.nodesMap[id].expanded = false
        })
        ElMessage.success('已收起所有菜单')
      }
    },
    // 递归获取所有菜单ID
    getAllMenuIds(menus) {
      let ids = []
      menus.forEach(menu => {
        ids.push(menu.id)
        if (menu.children && menu.children.length > 0) {
          ids = ids.concat(this.getAllMenuIds(menu.children))
        }
      })
      return ids
    },
    async saveMenuPermissions() {
      this.loading = true
      try {
        // 获取所有选中的节点（包括父节点和子节点）
        const selectedMenuIds = this.$refs.menuTree.getCheckedKeys()
        // 获取半选中的节点（父节点下的子节点部分选中）
        const halfCheckedKeys = this.$refs.menuTree.getHalfCheckedKeys()
        
        // 合并所有需要保存的菜单ID
        const allSelectedIds = [...selectedMenuIds, ...halfCheckedKeys]
        
        const response = await apiService.roles.updateRoleMenus(
          this.role.id, 
          { menu_ids: allSelectedIds }
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

.batch-operations {
  margin-bottom: 15px;
  display: flex;
  gap: 8px;
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