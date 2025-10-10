<template>
  <div class="menu-management">
    <el-card class="menu-card">
      <template #header>
        <div class="card-header">
          <span>菜单管理</span>
          <el-button 
            type="primary" 
            @click="showAddMenuDialog"
            v-permission="'menu:create'"
          >
            <el-icon><Plus /></el-icon>
            添加菜单
          </el-button>
        </div>
      </template>
      
      <div class="menu-container">
        <div class="menu-tree-container" v-loading="loading">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索菜单名称或代码"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-tree
            v-if="filteredMenus.length > 0"
            ref="menuTree"
            :data="filteredMenus"
            :props="defaultProps"
            node-key="id"
            highlight-current
            :expand-on-click-node="false"
            :default-expanded-keys="expandedKeys"
            @node-click="handleNodeClick"
            class="menu-tree"
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <div class="node-content">
                  <el-icon v-if="data.icon" class="menu-icon">
                    <component :is="getIconComponent(data.icon)" />
                  </el-icon>
                  <span class="menu-name">{{ data.name }}</span>
                  <el-tag size="small" effect="plain" class="menu-code">{{ data.code }}</el-tag>
                </div>
                <div class="node-actions" v-if="currentUser.is_admin || hasPermission('menu:update')">
                  <el-button 
                    type="primary" 
                    size="small" 
                    circle 
                    @click.stop="showEditMenuDialog(data)"
                    v-permission="'menu:update'"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    circle 
                    @click.stop="confirmDeleteMenu(data)"
                    v-permission="'menu:delete'"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
          <el-empty v-else description="暂无菜单数据" />
        </div>
        
        <div class="menu-detail" v-if="selectedMenu">
          <el-descriptions title="菜单详情" :column="1" border>
            <el-descriptions-item label="菜单名称">{{ selectedMenu.name }}</el-descriptions-item>
            <el-descriptions-item label="菜单代码">{{ selectedMenu.code }}</el-descriptions-item>
            <el-descriptions-item label="路由路径">{{ selectedMenu.path || '无' }}</el-descriptions-item>
            <el-descriptions-item label="组件路径">{{ selectedMenu.component || '无' }}</el-descriptions-item>
            <el-descriptions-item label="图标">
              <el-icon v-if="selectedMenu.icon">
                <component :is="getIconComponent(selectedMenu.icon)" />
              </el-icon>
              <span>{{ selectedMenu.icon || '无' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="排序">{{ selectedMenu.sort_order }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedMenu.is_active ? 'success' : 'danger'">
                {{ selectedMenu.is_active ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(selectedMenu.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDateTime(selectedMenu.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="menu-permissions" v-if="selectedMenu">
            <h3>菜单权限</h3>
            <el-button 
              type="primary" 
              size="small" 
              @click="showMenuPermissionDialog"
              v-permission="'menu:update'"
            >
              配置菜单权限
            </el-button>
            <el-table
              :data="menuPermissions"
              style="width: 100%; margin-top: 10px;"
              v-loading="permissionsLoading"
            >
              <el-table-column prop="name" label="权限名称" />
              <el-table-column prop="code" label="权限代码" />
              <el-table-column prop="resource_type" label="资源类型" />
              <el-table-column prop="action" label="操作类型" />
            </el-table>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 添加/编辑菜单对话框 -->
    <el-dialog
      v-model="menuDialogVisible"
      :title="isEdit ? '编辑菜单' : '添加菜单'"
      width="500px"
    >
      <el-form
        ref="menuFormRef"
        :model="menuForm"
        :rules="menuRules"
        label-width="100px"
      >
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" placeholder="请输入菜单名称" />
        </el-form-item>
        
        <el-form-item label="菜单代码" prop="code">
          <el-input v-model="menuForm.code" placeholder="请输入菜单代码" :disabled="isEdit" />
        </el-form-item>
        
        <el-form-item label="父级菜单" prop="parent_id">
          <el-tree-select
            v-model="menuForm.parent_id"
            :data="menuOptions"
            :props="{ label: 'name', children: 'children', value: 'id' }"
            placeholder="请选择父级菜单"
            clearable
            :render-after-expand="false"
          />
        </el-form-item>
        
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="menuForm.path" placeholder="请输入路由路径" />
        </el-form-item>
        
        <el-form-item label="组件路径" prop="component">
          <el-input v-model="menuForm.component" placeholder="请输入组件路径" />
        </el-form-item>
        
        <el-form-item label="图标" prop="icon">
          <el-select v-model="menuForm.icon" placeholder="请选择图标" clearable>
            <el-option
              v-for="(icon, name) in iconOptions"
              :key="name"
              :label="name"
              :value="name"
            >
              <div style="display: flex; align-items: center;">
                <el-icon>
                  <component :is="icon" />
                </el-icon>
                <span style="margin-left: 8px;">{{ name }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="menuForm.sort_order" :min="0" :max="999" />
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="menuForm.is_active"
            :active-value="true"
            :inactive-value="false"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMenuForm">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 菜单权限配置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="配置菜单权限"
      width="600px"
    >
      <div v-loading="allPermissionsLoading">
        <el-transfer
          v-model="selectedPermissionIds"
          :data="allPermissions"
          :props="{
            key: 'id',
            label: item => `${item.name} (${item.code})`
          }"
          :titles="['可选权限', '已选权限']"
          :button-texts="['移除', '添加']"
          :format="{ noChecked: '${total}', hasChecked: '${checked}/${total}' }"
        />
      </div>
      
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMenuPermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePermissionStore } from '@/stores/permission'
import { apiService } from '@/services/api'
import {
  Plus,
  Search,
  Edit,
  Delete,
  Document,
  Menu as IconMenu,
  Location,
  Setting,
  User,
  UserFilled,
  Key,
  DataBoard,
  Coordinate,
  OfficeBuilding,
  Calendar,
  Notebook,
  List
} from '@element-plus/icons-vue'

// 权限状态管理
const permissionStore = usePermissionStore()
const currentUser = computed(() => permissionStore.userInfo || {})
const hasPermission = (permission) => permissionStore.hasPermission(permission)

// 菜单树相关
const menuTree = ref(null)
const menus = ref([])
const filteredMenus = ref([])
const expandedKeys = ref([])
const searchKeyword = ref('')
const selectedMenu = ref(null)
const menuPermissions = ref([])
const permissionsLoading = ref(false)
const loading = ref(false)

// 菜单表单相关
const menuDialogVisible = ref(false)
const isEdit = ref(false)
const menuFormRef = ref(null)
const menuForm = ref({
  id: null,
  name: '',
  code: '',
  path: '',
  component: '',
  icon: '',
  parent_id: null,
  sort_order: 0,
  is_active: true
})

// 菜单权限相关
const permissionDialogVisible = ref(false)
const allPermissions = ref([])
const selectedPermissionIds = ref([])
const allPermissionsLoading = ref(false)

// 表单校验规则
const menuRules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入菜单代码', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '只能包含小写字母、数字和下划线，且必须以字母开头', trigger: 'blur' }
  ]
}

// 树形配置
const defaultProps = {
  children: 'children',
  label: 'name'
}

// 图标映射
const iconOptions = {
  'el-icon-document': Document,
  'el-icon-menu': IconMenu,
  'el-icon-location': Location,
  'el-icon-setting': Setting,
  'el-icon-user': User,
  'el-icon-user-solid': UserFilled,
  'el-icon-key': Key,
  'el-icon-data-board': DataBoard,
  'el-icon-coordinate': Coordinate,
  'el-icon-office-building': OfficeBuilding,
  'el-icon-calendar': Calendar,
  'el-icon-notebook': Notebook,
  'el-icon-list': List
}

// 获取图标组件
function getIconComponent(iconName) {
  return iconOptions[iconName] || Document
}

// 格式化日期时间
function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 加载菜单数据
async function loadMenus() {
  try {
    loading.value = true
    const response = await apiService.menus.getMenus()
    if (response.code === 200) {
      menus.value = response.data || []
      filteredMenus.value = menus.value
      
      // 展开所有节点
      expandedKeys.value = menus.value.map(menu => menu.id)
    } else {
      ElMessage.error(response.message || '获取菜单列表失败')
    }
  } catch (error) {
    console.error('Load menus failed:', error)
    ElMessage.error('获取菜单列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索菜单 - 使用防抖优化
let searchTimeout = null
function handleSearch() {
  // 清除之前的定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // 设置新的定时器，延迟执行搜索
  searchTimeout = setTimeout(() => {
    if (!searchKeyword.value) {
      filteredMenus.value = menus.value
      return
    }
    
    const keyword = searchKeyword.value.toLowerCase()
    
    // 递归搜索函数
    function searchInTree(nodes) {
      const result = []
      
      for (const node of nodes) {
        // 创建节点副本，避免修改原始数据
        const nodeCopy = { ...node }
        
        // 检查当前节点是否匹配
        const nameMatch = nodeCopy.name && nodeCopy.name.toLowerCase().includes(keyword)
        const codeMatch = nodeCopy.code && nodeCopy.code.toLowerCase().includes(keyword)
        
        // 递归搜索子节点
        if (nodeCopy.children && nodeCopy.children.length > 0) {
          nodeCopy.children = searchInTree(nodeCopy.children)
        }
        
        // 如果当前节点匹配或者子节点中有匹配项，则保留该节点
        if (nameMatch || codeMatch || (nodeCopy.children && nodeCopy.children.length > 0)) {
          result.push(nodeCopy)
        }
      }
      
      return result
    }
    
    filteredMenus.value = searchInTree(menus.value)
  }, 300) // 300ms 防抖延迟
}

// 处理节点点击
function handleNodeClick(data) {
  selectedMenu.value = data
  loadMenuPermissions(data.id)
}

// 加载菜单权限
async function loadMenuPermissions(menuId) {
  try {
    permissionsLoading.value = true
    const response = await apiService.menus.getMenu(menuId)
    if (response.code === 200) {
      // 如果API返回菜单权限信息，使用它；否则设为空数组
      menuPermissions.value = response.data.permissions || []
    } else {
      ElMessage.error(response.message || '获取菜单权限失败')
    }
  } catch (error) {
    console.error('Load menu permissions failed:', error)
    ElMessage.error('获取菜单权限失败: ' + error.message)
  } finally {
    permissionsLoading.value = false
  }
}

// 显示添加菜单对话框
function showAddMenuDialog() {
  isEdit.value = false
  menuForm.value = {
    id: null,
    name: '',
    code: '',
    path: '',
    component: '',
    icon: '',
    parent_id: null,
    sort_order: 0,
    is_active: true
  }
  menuDialogVisible.value = true
}

// 显示编辑菜单对话框
function showEditMenuDialog(menu) {
  isEdit.value = true
  menuForm.value = {
    id: menu.id,
    name: menu.name,
    code: menu.code,
    path: menu.path || '',
    component: menu.component || '',
    icon: menu.icon || '',
    parent_id: menu.parent_id,
    sort_order: menu.sort_order || 0,
    is_active: menu.is_active
  }
  menuDialogVisible.value = true
}

// 提交菜单表单
async function submitMenuForm() {
  // 先进行表单验证
  if (!menuFormRef.value) {
    ElMessage.error('表单引用不存在')
    return
  }
  
  try {
    // 验证表单
    await menuFormRef.value.validate()
  } catch (error) {
    ElMessage.error('请检查表单输入')
    return
  }
  
  try {
    const formData = { ...menuForm.value }
    
    // 检查是否选择了自己作为父菜单
    if (isEdit.value && formData.id === formData.parent_id) {
      ElMessage.error('不能选择自己作为父菜单')
      return
    }
    
    // 检查是否会形成循环引用
    if (isEdit.value && formData.parent_id) {
      const parentMenu = findMenuById(menus.value, formData.parent_id)
      if (isChildOf(parentMenu, formData.id)) {
        ElMessage.error('不能选择子菜单作为父菜单，这会导致循环引用')
        return
      }
    }
    
    let response
    if (isEdit.value) {
      // 更新菜单
      response = await apiService.menus.updateMenu(formData.id, formData)
    } else {
      // 创建菜单
      response = await apiService.menus.createMenu(formData)
    }
    
    if (response.code === 200 || response.code === 201) {
      ElMessage.success(isEdit.value ? '菜单更新成功' : '菜单创建成功')
      menuDialogVisible.value = false
      
      // 清除缓存
      cachedMenuOptions = null
      
      await loadMenus()
      
      // 如果是编辑模式，重新选中该菜单
      if (isEdit.value) {
        const updatedMenu = findMenuById(menus.value, formData.id)
        if (updatedMenu) {
          selectedMenu.value = updatedMenu
          await nextTick()
          if (menuTree.value) {
            menuTree.value.setCurrentKey(formData.id)
          }
        }
      }
      
      // 刷新权限状态
      if (permissionStore.refreshPermissions) {
        await permissionStore.refreshPermissions()
      }
    } else {
      ElMessage.error(response.message || (isEdit.value ? '菜单更新失败' : '菜单创建失败'))
    }
  } catch (error) {
    console.error(isEdit.value ? 'Update menu failed:' : 'Create menu failed:', error)
    ElMessage.error((isEdit.value ? '菜单更新失败: ' : '菜单创建失败: ') + error.message)
  }
}

// 确认删除菜单
function confirmDeleteMenu(menu) {
  ElMessageBox.confirm(
    `确定要删除菜单 "${menu.name}" 吗？${menu.children && menu.children.length > 0 ? '该操作将同时删除所有子菜单！' : ''}`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteMenu(menu.id)
  }).catch(() => {
    // 取消删除
  })
}

// 删除菜单
async function deleteMenu(menuId) {
  try {
    const response = await apiService.menus.deleteMenu(menuId)
    if (response.code === 200) {
      ElMessage.success('菜单删除成功')
      
      // 如果删除的是当前选中的菜单，清除选中状态
      if (selectedMenu.value && selectedMenu.value.id === menuId) {
        selectedMenu.value = null
        menuPermissions.value = []
      }
      
      // 清除缓存
      cachedMenuOptions = null
      
      await loadMenus()
      
      // 刷新权限状态
      if (permissionStore.refreshPermissions) {
        await permissionStore.refreshPermissions()
      }
    } else {
      ElMessage.error(response.message || '菜单删除失败')
    }
  } catch (error) {
    console.error('Delete menu failed:', error)
    ElMessage.error('菜单删除失败: ' + error.message)
  }
}

// 显示菜单权限配置对话框
async function showMenuPermissionDialog() {
  if (!selectedMenu.value) {
    ElMessage.warning('请先选择一个菜单')
    return
  }
  
  try {
    allPermissionsLoading.value = true
    permissionDialogVisible.value = true
    
    // 加载所有权限
    const response = await apiService.get('/permissions')
    if (response.code === 200) {
      allPermissions.value = response.data || []
      
      // 设置已选权限
      selectedPermissionIds.value = menuPermissions.value.map(p => p.id)
    } else {
      ElMessage.error(response.message || '获取权限列表失败')
    }
  } catch (error) {
    console.error('Load permissions failed:', error)
    ElMessage.error('获取权限列表失败: ' + error.message)
  } finally {
    allPermissionsLoading.value = false
  }
}

// 保存菜单权限
async function saveMenuPermissions() {
  if (!selectedMenu.value) return
  
  try {
    const response = await apiService.post(`/menus/${selectedMenu.value.id}/permissions`, {
      permission_ids: selectedPermissionIds.value
    })
    
    if (response.code === 200) {
      ElMessage.success('菜单权限配置成功')
      permissionDialogVisible.value = false
      
      // 重新加载菜单权限
      await loadMenuPermissions(selectedMenu.value.id)
      
      // 刷新权限状态
      await permissionStore.refreshPermissions()
    } else {
      ElMessage.error(response.message || '菜单权限配置失败')
    }
  } catch (error) {
    console.error('Save menu permissions failed:', error)
    ElMessage.error('菜单权限配置失败: ' + error.message)
  }
}

// 辅助函数：根据ID查找菜单
function findMenuById(menuList, id) {
  for (const menu of menuList) {
    if (menu.id === id) {
      return menu
    }
    if (menu.children && menu.children.length > 0) {
      const found = findMenuById(menu.children, id)
      if (found) return found
    }
  }
  return null
}

// 辅助函数：检查是否是子菜单
function isChildOf(menu, parentId) {
  if (!menu) return false
  if (menu.id === parentId) return true
  
  if (menu.children && menu.children.length > 0) {
    for (const child of menu.children) {
      if (isChildOf(child, parentId)) {
        return true
      }
    }
  }
  
  return false
}

// 计算菜单选项（用于父菜单选择）- 使用缓存优化
let cachedMenuOptions = null
let lastMenusLength = 0
let lastEditId = null

const menuOptions = computed(() => {
  const currentMenusLength = menus.value.length
  const currentEditId = isEdit.value ? menuForm.value.id : null
  
  // 如果数据没有变化，返回缓存的结果
  if (cachedMenuOptions && 
      lastMenusLength === currentMenusLength && 
      lastEditId === currentEditId) {
    return cachedMenuOptions
  }
  
  // 重新计算菜单选项
  let result
  if (isEdit.value && menuForm.value.id) {
    result = filterMenuOptions(menus.value, menuForm.value.id)
  } else {
    // 添加模式下，可以选择所有菜单作为父级菜单，包括父级菜单本身
    result = menus.value
  }
  
  // 更新缓存
  cachedMenuOptions = result
  lastMenusLength = currentMenusLength
  lastEditId = currentEditId
  
  return result
})

// 过滤菜单选项，排除自己及其子菜单（仅在编辑模式下）
function filterMenuOptions(menuList, excludeId) {
  return menuList
    .filter(menu => menu.id !== excludeId)
    .map(menu => {
      const newMenu = { ...menu }
      if (menu.children && menu.children.length > 0) {
        newMenu.children = filterMenuOptions(menu.children, excludeId)
      }
      return newMenu
    })
}

// 组件挂载时加载数据
onMounted(async () => {
  await loadMenus()
})
</script>

<style scoped>
.menu-management {
  padding: 20px;
}

.menu-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.menu-tree-container {
  width: 40%;
  border-right: 1px solid #ebeef5;
  padding-right: 20px;
}

.menu-tree {
  margin-top: 20px;
  height: 600px;
  overflow-y: auto;
}

.menu-detail {
  flex: 1;
  padding-left: 20px;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.node-content {
  display: flex;
  align-items: center;
}

.menu-icon {
  margin-right: 8px;
}

.menu-name {
  margin-right: 8px;
}

.menu-code {
  font-size: 12px;
}

.node-actions {
  display: flex;
  gap: 5px;
}

.menu-permissions {
  margin-top: 20px;
}
</style>