// 路由权限守卫
import { usePermissionStore } from '@/stores/permission'
import { ElMessage } from 'element-plus'

/**
 * 设置路由权限守卫
 * @param {Router} router - Vue Router 实例
 */
export function setupPermissionGuard(router) {
  // 全局前置守卫
  router.beforeEach(async (to, from, next) => {
    const permissionStore = usePermissionStore()
    
    try {
      // 检查是否需要认证
      if (to.meta.requiresAuth !== false) {
        const token = localStorage.getItem('token')
        
        if (!token) {
          // 没有token，跳转到登录页
          ElMessage.warning('请先登录')
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
        
        // 初始化权限信息（如果还没有初始化）
        if (!permissionStore.userInfo) {
          await permissionStore.initializeFromToken()
        }
      }
      
      // 检查路由权限
      if (to.meta.permission) {
        const hasPermission = await checkRoutePermission(to.meta.permission, permissionStore)
        
        if (!hasPermission) {
          ElMessage.error('您没有访问该页面的权限')
          // 跳转到403页面或返回上一页
          if (from.path !== '/') {
            next(false) // 阻止导航
          } else {
            next('/403') // 跳转到403页面
          }
          return
        }
      }
      
      // 检查角色权限
      if (to.meta.roles) {
        const hasRole = checkRouteRole(to.meta.roles, permissionStore)
        
        if (!hasRole) {
          ElMessage.error('您的角色无权访问该页面')
          if (from.path !== '/') {
            next(false)
          } else {
            next('/403')
          }
          return
        }
      }
      
      // 检查菜单访问权限
      if (to.meta.menuCode) {
        const hasMenuAccess = await checkMenuAccess(to.meta.menuCode, permissionStore)
        
        if (!hasMenuAccess) {
          ElMessage.error('您没有访问该菜单的权限')
          if (from.path !== '/') {
            next(false)
          } else {
            next('/403')
          }
          return
        }
      }
      
      // 检查管理员权限
      if (to.meta.requiresAdmin) {
        if (!permissionStore.isAdmin) {
          ElMessage.error('该页面仅限管理员访问')
          if (from.path !== '/') {
            next(false)
          } else {
            next('/403')
          }
          return
        }
      }
      
      // 所有检查通过，允许导航
      next()
      
    } catch (error) {
      console.error('Route permission check failed:', error)
      ElMessage.error('权限验证失败，请重新登录')
      
      // 清除无效的认证信息
      localStorage.removeItem('token')
      permissionStore.clearPermissions()
      
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  })
  
  // 全局后置钩子
  router.afterEach((to, from) => {
    // 可以在这里添加页面访问日志等功能
    console.log(`Navigation: ${from.path} -> ${to.path}`)
  })
}

/**
 * 检查路由权限
 * @param {string|Array|Object} permission - 权限配置
 * @param {Object} permissionStore - 权限store
 * @returns {Promise<boolean>}
 */
async function checkRoutePermission(permission, permissionStore) {
  if (!permission) return true
  
  // 管理员拥有所有权限
  if (permissionStore.isAdmin) return true
  
  if (typeof permission === 'string') {
    // 单个权限
    return await permissionStore.checkPermission(permission)
  } else if (Array.isArray(permission)) {
    // 权限数组，需要任一权限
    return permissionStore.hasAnyPermission(permission)
  } else if (typeof permission === 'object') {
    // 权限对象配置
    const { permissions, requireAll = false } = permission
    
    if (Array.isArray(permissions)) {
      if (requireAll) {
        return permissionStore.hasAllPermissions(permissions)
      } else {
        return permissionStore.hasAnyPermission(permissions)
      }
    }
  }
  
  return false
}

/**
 * 检查路由角色权限
 * @param {string|Array} roles - 角色配置
 * @param {Object} permissionStore - 权限store
 * @returns {boolean}
 */
function checkRouteRole(roles, permissionStore) {
  if (!roles) return true
  
  // 管理员拥有所有权限
  if (permissionStore.isAdmin) return true
  
  if (typeof roles === 'string') {
    // 单个角色
    return permissionStore.hasRole(roles)
  } else if (Array.isArray(roles)) {
    // 角色数组，需要任一角色
    return roles.some(role => permissionStore.hasRole(role))
  }
  
  return false
}

/**
 * 检查菜单访问权限
 * @param {string} menuCode - 菜单代码
 * @param {Object} permissionStore - 权限store
 * @returns {Promise<boolean>}
 */
async function checkMenuAccess(menuCode, permissionStore) {
  if (!menuCode) return true
  
  // 管理员拥有所有权限
  if (permissionStore.isAdmin) return true
  
  return await permissionStore.checkMenuAccess(menuCode)
}

/**
 * 路由元信息配置示例：
 * 
 * {
 *   path: '/users',
 *   component: UserManagement,
 *   meta: {
 *     requiresAuth: true,                    // 需要登录
 *     permission: 'user:read',               // 需要权限
 *     permissions: ['user:read', 'user:write'], // 需要任一权限
 *     permission: {                          // 权限对象配置
 *       permissions: ['user:read', 'user:write'],
 *       requireAll: true                     // 需要所有权限
 *     },
 *     roles: 'admin',                        // 需要角色
 *     roles: ['admin', 'manager'],           // 需要任一角色
 *     menuCode: 'user_management',           // 菜单代码
 *     requiresAdmin: true,                   // 仅管理员
 *     title: '用户管理'                      // 页面标题
 *   }
 * }
 */

/**
 * 动态添加路由权限
 * @param {Array} routes - 路由配置
 * @param {Object} permissionStore - 权限store
 * @returns {Array} 过滤后的路由
 */
export async function filterRoutesByPermission(routes, permissionStore) {
  const filtered = []
  
  for (const route of routes) {
    // 检查路由权限（支持异步）
    if (route.meta?.permission) {
      const ok = await checkRoutePermission(route.meta.permission, permissionStore)
      if (!ok) continue
    }
    
    // 检查角色权限
    if (route.meta?.roles) {
      if (!checkRouteRole(route.meta.roles, permissionStore)) continue
    }
    
    // 检查菜单权限（改为异步检查）
    if (route.meta?.menuCode) {
      const hasMenu = await permissionStore.checkMenuAccess(route.meta.menuCode)
      if (!hasMenu) continue
    }
    
    // 检查管理员权限
    if (route.meta?.requiresAdmin) {
      if (!permissionStore.isAdmin) continue
    }
    
    // 递归过滤子路由（异步）
    if (route.children && route.children.length > 0) {
      route.children = await filterRoutesByPermission(route.children, permissionStore)
    }
    
    filtered.push(route)
  }
  
  return filtered
}

/**
 * 生成动态路由
 * @param {Array} menus - 菜单数据
 * @param {Object} componentMap - 组件映射
 * @returns {Array} 动态路由配置
 */
export function generateRoutesFromMenus(menus, componentMap = {}) {
  const routes = []
  
  function processMenu(menu, parentPath = '') {
    const route = {
      path: menu.path || `${parentPath}/${menu.code}`,
      name: menu.code,
      component: componentMap[menu.component] || (() => import('@/components/ComingSoon.vue')),
      meta: {
        title: menu.name,
        icon: menu.icon,
        menuCode: menu.code,
        requiresAuth: true
      }
    }
    
    // 处理子菜单
    if (menu.children && menu.children.length > 0) {
      route.children = []
      menu.children.forEach(child => {
        const childRoute = processMenu(child, route.path)
        if (childRoute) {
          route.children.push(childRoute)
        }
      })
    }
    
    return route
  }
  
  menus.forEach(menu => {
    const route = processMenu(menu)
    if (route) {
      routes.push(route)
    }
  })
  
  return routes
}