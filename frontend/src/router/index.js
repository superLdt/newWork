import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../pages/Dashboard.vue'
import UserManagement from '../pages/settings/UserManagement.vue'
import RoleManagement from '../pages/settings/RoleManagement.vue'
import SystemConfig from '../pages/settings/SystemConfig.vue'
import AuditLog from '../pages/settings/AuditLog.vue'
import ComingSoon from '../components/ComingSoon.vue'
import { authService } from '@/services/authService'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      // 基础数据路由
      {
        path: '/data/vehicles',
        name: 'Vehicles',
        component: ComingSoon
      },
      {
        path: '/data/routes',
        name: 'Routes',
        component: ComingSoon
      },
      {
        path: '/data/companies',
        name: 'Companies',
        component: ComingSoon
      },
      // 调度管理路由
      {
        path: '/dispatch/manual',
        name: 'ManualDispatch',
        component: ComingSoon
      },
      {
        path: '/dispatch/tasks',
        name: 'TransportTasks',
        component: ComingSoon
      },
      // 系统管理路由
      {
        path: '/settings/user',
        name: 'UserManagement',
        component: UserManagement
      },
      {
        path: '/settings/role',
        name: 'RoleManagement',
        component: RoleManagement
      },
      {
        path: '/settings/config',
        name: 'SystemConfig',
        component: SystemConfig
      },
      {
        path: '/settings/logs',
        name: 'AuditLog',
        component: AuditLog
      },
      // 规划管理路由
      {
        path: '/planning/schedule',
        name: 'TransportSchedule',
        component: ComingSoon
      },
      {
        path: '/planning/optimization',
        name: 'RouteOptimization',
        component: ComingSoon
      },
      // 报表管理路由
      {
        path: '/reports/transport',
        name: 'TransportReports',
        component: ComingSoon
      },
      {
        path: '/reports/finance',
        name: 'FinanceReports',
        component: ComingSoon
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加导航守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    // 路由需要认证
    if (authService.isAuthenticated()) {
      // 用户已登录，允许访问
      next()
    } else {
      // 用户未登录，重定向到登录页面
      next('/login')
    }
  } else if (to.meta.requiresGuest) {
    // 路由只允许未登录用户访问
    if (authService.isAuthenticated()) {
      // 用户已登录，重定向到仪表盘
      next('/')
    } else {
      // 用户未登录，允许访问
      next()
    }
  } else {
    // 路由不需要特殊认证，直接访问
    next()
  }
})

export default router