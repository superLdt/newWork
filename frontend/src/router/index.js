import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../pages/Dashboard.vue'
import UserManagement from '../pages/settings/UserManagement.vue'
import RoleManagement from '../pages/settings/RoleManagement.vue'
import PermissionManagement from '../pages/settings/PermissionManagement.vue'
import MenuManagement from '../pages/settings/MenuManagement.vue'
import SystemConfig from '../pages/settings/SystemConfig.vue'
import AuditLog from '../pages/settings/AuditLog.vue'
import ComingSoon from '../components/ComingSoon.vue'
import { authService } from '@/services/authService'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, requiresGuest: true }
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
        path: '/basic-data/vehicles',
        name: 'Vehicles',
        component: () => import('../pages/vehicle/VehicleManagement.vue'),
        meta: {
          title: '车辆管理',
          menuCode: 'vehicle_management',
          permissions: ['vehicle:read']
        }
      },
      {
        path: '/basic-data/drivers',
        name: 'Drivers',
        component: ComingSoon,
        meta: {
          title: '司机管理',
          menuCode: 'driver_management'
        }
      },
      {
        path: '/basic-data/dispatch-units',
        name: 'DispatchUnits',
        component: () => import('../pages/basic-data/DispatchUnitManagement.vue'),
        meta: {
          title: '派车单位管理',
          menuCode: 'dispatch_unit_management',
          permissions: ['dispatch_unit:read']
        }
      },
      {
        path: '/basic-data/tonnage-volume-mapping',
        name: 'TonnageVolumeMapping',
        component: () => import('../pages/basic-data/TonnageVolumeMapping.vue'),
        meta: {
          title: '吨位容积对应管理',
          menuCode: 'tonnage_volume_mapping',
          permissions: ['tonnage_volume:read']
        }
      },
      // 调度管理路由
      {
        path: '/dispatch/orders',
        name: 'TransportOrders',
        component: ComingSoon,
        meta: {
          title: '运输订单',
          menuCode: 'transport_orders'
        }
      },
      {
        path: '/dispatch/tasks',
        name: 'DispatchTasks',
        component: () => import('../pages/dispatch/DispatchTasks.vue'),
        meta: {
          title: '调度任务',
          menuCode: 'dispatch_tasks'
        }
      },
      {
        path: '/dispatch/dashboard',
        name: 'DispatchDashboard',
        component: () => import('../pages/dispatch/DispatchDashboard.vue'),
        meta: {
          title: '调度仪表盘',
          menuCode: 'dispatch_dashboard',
          permissions: ['dispatch:read']
        }
      },
      {
        path: '/dispatch/tracking',
        name: 'TransportTracking',
        component: ComingSoon,
        meta: {
          title: '运输跟踪',
          menuCode: 'transport_tracking'
        }
      },
      // 系统设置路由
      {
        path: '/settings/users',
        name: 'UserManagement',
        component: UserManagement,
        meta: {
          title: '用户管理',
          permission: 'user:read',
          menuCode: 'user_management'
        }
      },
      {
        path: '/settings/roles',
        name: 'RoleManagement',
        component: RoleManagement,
        meta: {
          title: '角色管理',
          permission: 'role:read',
          menuCode: 'role_management'
        }
      },
      {
        path: '/settings/permissions',
        name: 'PermissionManagement',
        component: PermissionManagement,
        meta: {
          title: '权限管理',
          permission: 'permission:read',
          menuCode: 'permission_management'
        }
      },
      {
        path: '/settings/menu',
        name: 'MenuManagement',
        component: MenuManagement,
        meta: {
          title: '菜单管理',
          permission: 'menu:read',
          menuCode: 'menu_management'
        }
      },
      {
        path: '/settings/config',
        name: 'SystemConfig',
        component: SystemConfig,
        meta: {
          title: '系统配置',
          requiresAdmin: true
        }
      },
      {
        path: '/settings/logs',
        name: 'AuditLog',
        component: AuditLog,
        meta: {
          title: '审计日志',
          requiresAdmin: true
        }
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

// 注意：路由守卫已移至 @/guards/permission.js 中统一处理
// 包括认证检查、权限验证、角色验证等功能

export default router