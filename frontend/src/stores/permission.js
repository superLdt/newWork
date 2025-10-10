// 权限状态管理 Store
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import { ElMessage } from 'element-plus'

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const permissions = ref([])
  const roles = ref([])
  const menus = ref([])
  const userInfo = ref(null)
  const isAdmin = ref(false)
  const loading = ref(false)
  
  // 计算属性
  const hasPermission = computed(() => {
    return (permission) => {
      if (isAdmin.value) return true
      return permissions.value.includes(permission)
    }
  })
  
  const hasAnyPermission = computed(() => {
    return (permissionList) => {
      if (isAdmin.value) return true
      return permissionList.some(permission => permissions.value.includes(permission))
    }
  })
  
  const hasAllPermissions = computed(() => {
    return (permissionList) => {
      if (isAdmin.value) return true
      return permissionList.every(permission => permissions.value.includes(permission))
    }
  })
  
  const hasRole = computed(() => {
    return (role) => {
      return roles.value.includes(role)
    }
  })
  
  const canAccessMenu = computed(() => {
    return (menuCode) => {
      if (isAdmin.value) return true
      return findMenuInTree(menus.value, menuCode) !== null
    }
  })
  
  const menuTree = computed(() => {
    return buildMenuTree(menus.value)
  })
  
  // 辅助函数
  function findMenuInTree(menuList, targetCode) {
    for (const menu of menuList) {
      if (menu.code === targetCode) {
        return menu
      }
      if (menu.children && menu.children.length > 0) {
        const found = findMenuInTree(menu.children, targetCode)
        if (found) return found
      }
    }
    return null
  }
  
  function buildMenuTree(menuList) {
    if (!Array.isArray(menuList)) return []
    
    // 如果已经是树形结构，直接返回
    if (menuList.some(menu => menu.children)) {
      return menuList
    }
    
    // 构建树形结构
    const menuMap = new Map()
    const rootMenus = []
    
    // 创建菜单映射
    menuList.forEach(menu => {
      menuMap.set(menu.id, { ...menu, children: [] })
    })
    
    // 构建父子关系
    menuList.forEach(menu => {
      const menuItem = menuMap.get(menu.id)
      if (menu.parent_id && menuMap.has(menu.parent_id)) {
        const parent = menuMap.get(menu.parent_id)
        parent.children.push(menuItem)
      } else {
        rootMenus.push(menuItem)
      }
    })
    
    // 排序
    function sortMenus(menus) {
      menus.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      menus.forEach(menu => {
        if (menu.children && menu.children.length > 0) {
          sortMenus(menu.children)
        }
      })
    }
    
    sortMenus(rootMenus)
    return rootMenus
  }
  
  // Actions
  async function initializeFromToken() {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('No token found')
      }
      
      // 解析JWT Token获取权限信息
      const payload = parseJwtToken(token)
      if (payload) {
        permissions.value = payload.permissions || []
        roles.value = payload.roles || []
        isAdmin.value = payload.is_admin || false
        userInfo.value = {
          id: payload.sub,
          username: payload.username,
          full_name: payload.full_name,
          roles: payload.roles,
          is_admin: payload.is_admin
        }
        
        // 获取用户菜单
        await loadUserMenus()
      }
    } catch (error) {
      console.error('Initialize permission from token failed:', error)
      clearPermissions()
    }
  }
  
  async function loadUserMenus() {
    try {
      loading.value = true
      // 不使用缓存，确保获取最新菜单数据
      const response = await apiService.get('/menus/current-user?use_cache=false')
      
      if (response.code === 200) {
        menus.value = response.data || []
        console.log('Loaded menus:', menus.value.length, menus.value)
      } else {
        throw new Error(response.message || '获取用户菜单失败')
      }
    } catch (error) {
      console.error('Load user menus failed:', error)
      ElMessage.error('获取用户菜单失败: ' + error.message)
      menus.value = []
    } finally {
      loading.value = false
    }
  }
  
  async function refreshPermissions() {
    try {
      loading.value = true
      
      // 重新获取用户信息
      const userResponse = await apiService.get('/auth/userinfo')
      if (userResponse.code === 200) {
        const user = userResponse.data
        userInfo.value = user
        roles.value = user.roles?.map(role => role.name) || []
        isAdmin.value = user.roles?.some(role => role.name === '超级管理员') || false
      }
      
      // 获取用户权限
      if (userInfo.value?.id) {
        const permResponse = await apiService.get(`/permissions/user/${userInfo.value.id}`)
        if (permResponse.code === 200) {
          permissions.value = permResponse.data.permissions?.map(p => p.code) || []
        }
      }
      
      // 重新加载菜单
      await loadUserMenus()
      
    } catch (error) {
      console.error('Refresh permissions failed:', error)
      ElMessage.error('刷新权限信息失败: ' + error.message)
    } finally {
      loading.value = false
    }
  }
  
  function parseJwtToken(token) {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) {
        throw new Error('Invalid token format')
      }
      
      const payload = parts[1]
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
      return JSON.parse(decoded)
    } catch (error) {
      console.error('Parse JWT token failed:', error)
      return null
    }
  }
  
  function clearPermissions() {
    permissions.value = []
    roles.value = []
    menus.value = []
    userInfo.value = null
    isAdmin.value = false
  }
  
  async function checkPermission(permission) {
    if (isAdmin.value) return true
    
    // 如果本地没有权限信息，尝试从服务器获取
    if (permissions.value.length === 0 && userInfo.value?.id) {
      try {
        const response = await apiService.post('/permissions/check', {
          permission_code: permission
        })
        return response.data?.has_permission || false
      } catch (error) {
        console.error('Check permission failed:', error)
        return false
      }
    }
    
    return permissions.value.includes(permission)
  }
  
  async function checkMenuAccess(menuCode) {
    if (isAdmin.value) return true
    
    // 如果本地没有菜单信息，尝试从服务器获取
    if (menus.value.length === 0) {
      try {
        const response = await apiService.post('/menus/check-access', {
          menu_code: menuCode
        })
        return response.data?.has_access || false
      } catch (error) {
        console.error('Check menu access failed:', error)
        return false
      }
    }
    
    return findMenuInTree(menus.value, menuCode) !== null
  }
  
  // 权限管理相关方法
  async function getAllPermissions(params = {}) {
    try {
      const response = await apiService.get('/permissions', { params })
      return response
    } catch (error) {
      console.error('Get all permissions failed:', error)
      throw error
    }
  }
  
  async function createPermission(permissionData) {
    try {
      const response = await apiService.post('/permissions', permissionData)
      if (response.code === 201) {
        ElMessage.success('权限创建成功')
      }
      return response
    } catch (error) {
      console.error('Create permission failed:', error)
      ElMessage.error('权限创建失败: ' + error.message)
      throw error
    }
  }
  
  async function updatePermission(permissionId, permissionData) {
    try {
      const response = await apiService.put(`/permissions/${permissionId}`, permissionData)
      if (response.code === 200) {
        ElMessage.success('权限更新成功')
      }
      return response
    } catch (error) {
      console.error('Update permission failed:', error)
      ElMessage.error('权限更新失败: ' + error.message)
      throw error
    }
  }
  
  async function deletePermission(permissionId) {
    try {
      const response = await apiService.delete(`/permissions/${permissionId}`)
      if (response.code === 200) {
        ElMessage.success('权限删除成功')
      }
      return response
    } catch (error) {
      console.error('Delete permission failed:', error)
      ElMessage.error('权限删除失败: ' + error.message)
      throw error
    }
  }
  
  // 角色权限管理
  async function getRolePermissions(roleId) {
    try {
      const response = await apiService.get(`/role-permissions/roles/${roleId}/permissions`)
      return response
    } catch (error) {
      console.error('Get role permissions failed:', error)
      throw error
    }
  }
  
  async function assignPermissionsToRole(roleId, permissionIds) {
    try {
      const response = await apiService.post(`/role-permissions/roles/${roleId}/permissions`, {
        permission_ids: permissionIds
      })
      if (response.code === 201) {
        ElMessage.success('权限分配成功')
        // 如果是当前用户的角色，刷新权限
        if (roles.value.length > 0) {
          await refreshPermissions()
        }
      }
      return response
    } catch (error) {
      console.error('Assign permissions to role failed:', error)
      ElMessage.error('权限分配失败: ' + error.message)
      throw error
    }
  }
  
  async function syncRolePermissions(roleId, permissionIds) {
    try {
      const response = await apiService.post(`/role-permissions/roles/${roleId}/permissions/sync`, {
        permission_ids: permissionIds
      })
      if (response.code === 200) {
        ElMessage.success('权限同步成功')
        // 如果是当前用户的角色，刷新权限
        if (roles.value.length > 0) {
          await refreshPermissions()
        }
      }
      return response
    } catch (error) {
      console.error('Sync role permissions failed:', error)
      ElMessage.error('权限同步失败: ' + error.message)
      throw error
    }
  }
  
  // 菜单管理
  async function getAllMenus(params = {}) {
    try {
      const response = await apiService.get('/menus', { params })
      return response
    } catch (error) {
      console.error('Get all menus failed:', error)
      throw error
    }
  }
  
  async function createMenu(menuData) {
    try {
      const response = await apiService.post('/menus', menuData)
      if (response.code === 201) {
        ElMessage.success('菜单创建成功')
        // 刷新用户菜单
        await loadUserMenus()
      }
      return response
    } catch (error) {
      console.error('Create menu failed:', error)
      ElMessage.error('菜单创建失败: ' + error.message)
      throw error
    }
  }
  
  async function updateMenu(menuId, menuData) {
    try {
      const response = await apiService.put(`/menus/${menuId}`, menuData)
      if (response.code === 200) {
        ElMessage.success('菜单更新成功')
        // 刷新用户菜单
        await loadUserMenus()
      }
      return response
    } catch (error) {
      console.error('Update menu failed:', error)
      ElMessage.error('菜单更新失败: ' + error.message)
      throw error
    }
  }
  
  async function deleteMenu(menuId, force = false) {
    try {
      const response = await apiService.delete(`/menus/${menuId}`, {
        params: { force }
      })
      if (response.code === 200) {
        ElMessage.success('菜单删除成功')
        // 刷新用户菜单
        await loadUserMenus()
      }
      return response
    } catch (error) {
      console.error('Delete menu failed:', error)
      ElMessage.error('菜单删除失败: ' + error.message)
      throw error
    }
  }
  
  return {
    // 状态
    permissions,
    roles,
    menus,
    userInfo,
    isAdmin,
    loading,
    
    // 计算属性
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    canAccessMenu,
    menuTree,
    
    // 方法
    initializeFromToken,
    loadUserMenus,
    refreshPermissions,
    clearPermissions,
    checkPermission,
    checkMenuAccess,
    
    // 权限管理
    getAllPermissions,
    createPermission,
    updatePermission,
    deletePermission,
    
    // 角色权限管理
    getRolePermissions,
    assignPermissionsToRole,
    syncRolePermissions,
    
    // 菜单管理
    getAllMenus,
    createMenu,
    updateMenu,
    deleteMenu
  }
})