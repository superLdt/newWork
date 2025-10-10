// 权限指令
import { usePermissionStore } from '@/stores/permission'

/**
 * 权限指令 v-permission
 * 用法：
 * v-permission="'user:create'" - 检查单个权限
 * v-permission="['user:create', 'user:update']" - 检查多个权限（任一）
 * v-permission.all="['user:create', 'user:update']" - 检查多个权限（全部）
 * v-permission.role="'admin'" - 检查角色
 */

const permission = {
  mounted(el, binding) {
    checkPermission(el, binding)
  },
  
  updated(el, binding) {
    checkPermission(el, binding)
  }
}

function checkPermission(el, binding) {
  const { value, modifiers } = binding
  const permissionStore = usePermissionStore()
  
  if (!value) {
    console.warn('v-permission directive requires a value')
    return
  }
  
  let hasPermission = false
  
  try {
    if (modifiers.role) {
      // 角色检查
      if (typeof value === 'string') {
        hasPermission = permissionStore.hasRole(value)
      } else if (Array.isArray(value)) {
        hasPermission = value.some(role => permissionStore.hasRole(role))
      }
    } else {
      // 权限检查
      if (typeof value === 'string') {
        hasPermission = permissionStore.hasPermission(value)
      } else if (Array.isArray(value)) {
        if (modifiers.all) {
          // 需要所有权限
          hasPermission = permissionStore.hasAllPermissions(value)
        } else {
          // 需要任一权限
          hasPermission = permissionStore.hasAnyPermission(value)
        }
      }
    }
  } catch (error) {
    console.error('Permission check failed:', error)
    hasPermission = false
  }
  
  // 控制元素显示/隐藏
  if (!hasPermission) {
    // 移除元素
    if (el.parentNode) {
      el.parentNode.removeChild(el)
    }
  } else {
    // 确保元素可见
    if (el.style.display === 'none') {
      el.style.display = ''
    }
  }
}

/**
 * 菜单访问权限指令 v-menu-access
 * 用法：
 * v-menu-access="'user_management'" - 检查菜单访问权限
 */
const menuAccess = {
  async mounted(el, binding) {
    await checkMenuAccess(el, binding)
  },
  
  async updated(el, binding) {
    await checkMenuAccess(el, binding)
  }
}

async function checkMenuAccess(el, binding) {
  const { value } = binding
  const permissionStore = usePermissionStore()
  
  if (!value) {
    console.warn('v-menu-access directive requires a menu code')
    return
  }
  
  let hasAccess = false
  
  try {
    if (typeof value === 'string') {
      // 使用支持服务端兜底的异步检查，避免菜单尚未加载导致的误判
      hasAccess = await permissionStore.checkMenuAccess(value)
    }
  } catch (error) {
    console.error('Menu access check failed:', error)
    hasAccess = false
  }
  
  // 控制元素显示/隐藏
  if (!hasAccess) {
    // 移除元素
    if (el.parentNode) {
      el.parentNode.removeChild(el)
    }
  } else {
    // 确保元素可见
    if (el.style.display === 'none') {
      el.style.display = ''
    }
  }
}

/**
 * 管理员权限指令 v-admin
 * 用法：
 * v-admin - 只有管理员可见
 */
const admin = {
  mounted(el, binding) {
    checkAdmin(el, binding)
  },
  
  updated(el, binding) {
    checkAdmin(el, binding)
  }
}

function checkAdmin(el, binding) {
  const permissionStore = usePermissionStore()
  
  const isAdmin = permissionStore.isAdmin
  
  // 控制元素显示/隐藏
  if (!isAdmin) {
    // 移除元素
    if (el.parentNode) {
      el.parentNode.removeChild(el)
    }
  } else {
    // 确保元素可见
    if (el.style.display === 'none') {
      el.style.display = ''
    }
  }
}

// 导出指令
export { permission, menuAccess, admin }

// 默认导出权限指令
export default permission