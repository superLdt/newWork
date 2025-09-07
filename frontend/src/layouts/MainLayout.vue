<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="header-left">
        <div class="logo">
          <el-icon class="collapse-icon" @click="toggleSidebar">
            <component :is="isSidebarCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
          <span :class="{ 'collapsed-logo': isSidebarCollapsed }">智能运力系统</span>
        </div>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleUserCommand">
          <span class="el-dropdown-link">
            <el-avatar :size="30" icon="User" class="user-avatar" />
            <div class="user-info">
              <span class="username">{{ currentUser.full_name || currentUser.username || '管理员' }}</span>
              <span class="user-role">{{ currentUserRole || '系统管理员' }}</span>
            </div>
            <el-icon class="dropdown-icon">
              <arrow-down />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside :width="isSidebarCollapsed ? '64px' : '220px'" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          :collapse="isSidebarCollapsed"
          router
          @select="handleMenuSelect"
        >
          <el-tooltip 
            v-if="isSidebarCollapsed" 
            class="box-item" 
            effect="dark" 
            content="仪表盘" 
            placement="right"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
          </el-tooltip>
          <el-menu-item v-else index="/">
            <el-icon><House /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <el-sub-menu index="data">
            <template #title>
              <el-icon><Operation /></el-icon>
              <span>基础数据</span>
            </template>
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="车辆信息" 
              placement="right"
            >
              <el-menu-item index="/data/vehicles">车辆信息</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/data/vehicles">车辆信息</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="路线数据" 
              placement="right"
            >
              <el-menu-item index="/data/routes">路线数据</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/data/routes">路线数据</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="公司信息" 
              placement="right"
            >
              <el-menu-item index="/data/companies">公司信息</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/data/companies">公司信息</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="dispatch">
            <template #title>
              <el-icon><List /></el-icon>
              <span>调度管理</span>
            </template>
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="人工派车" 
              placement="right"
            >
              <el-menu-item index="/dispatch/manual">人工派车</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/dispatch/manual">人工派车</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="运输任务" 
              placement="right"
            >
              <el-menu-item index="/dispatch/tasks">运输任务</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/dispatch/tasks">运输任务</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="settings">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="用户管理" 
              placement="right"
            >
              <el-menu-item index="/settings/user">用户管理</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/settings/user">用户管理</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="角色管理" 
              placement="right"
            >
              <el-menu-item index="/settings/role">角色管理</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/settings/role">角色管理</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="系统设置" 
              placement="right"
            >
              <el-menu-item index="/settings/config">系统设置</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/settings/config">系统设置</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="审计日志" 
              placement="right"
            >
              <el-menu-item index="/settings/logs">审计日志</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/settings/logs">审计日志</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="planning">
            <template #title>
              <el-icon><Calendar /></el-icon>
              <span>规划管理</span>
            </template>
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="运输计划" 
              placement="right"
            >
              <el-menu-item index="/planning/schedule">运输计划</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/planning/schedule">运输计划</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="路线优化" 
              placement="right"
            >
              <el-menu-item index="/planning/optimization">路线优化</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/planning/optimization">路线优化</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="reports">
            <template #title>
              <el-icon><Notebook /></el-icon>
              <span>报表管理</span>
            </template>
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="运输报表" 
              placement="right"
            >
              <el-menu-item index="/reports/transport">运输报表</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/reports/transport">运输报表</el-menu-item>
            
            <el-tooltip 
              v-if="isSidebarCollapsed" 
              class="box-item" 
              effect="dark" 
              content="财务报表" 
              placement="right"
            >
              <el-menu-item index="/reports/finance">财务报表</el-menu-item>
            </el-tooltip>
            <el-menu-item v-else index="/reports/finance">财务报表</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
    
    <el-footer class="footer">
      <div class="copyright">
        安徽**运输中心@2025
      </div>
    </el-footer>
  </el-container>
</template>

<script>
import {
  House,
  Operation,
  List,
  Setting,
  User,
  SwitchButton,
  ArrowDown,
  Calendar,
  Notebook,
  Fold,
  Expand
} from '@element-plus/icons-vue'
import { authService } from '@/services/authService'

export default {
  name: 'MainLayout',
  components: {
    House,
    Operation,
    List,
    Setting,
    User,
    SwitchButton,
    ArrowDown,
    Calendar,
    Notebook,
    Fold,
    Expand
  },
  data() {
    return {
      activeMenu: '/',
      isSidebarCollapsed: false,
      currentUser: {},
      currentUserRole: ''
    }
  },
  watch: {
    '$route'(to) {
      this.activeMenu = to.path
    }
  },
  mounted() {
    // 检查用户是否已登录
    this.checkAuth()
    // 获取当前用户信息
    this.getCurrentUser()
  },
  methods: {
    checkAuth() {
      if (!authService.isAuthenticated()) {
        // 用户未登录，重定向到登录页面
        this.$router.push('/login')
      }
    },
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed
    },
    handleMenuSelect(index) {
      this.activeMenu = index
    },
    async getCurrentUser() {
      try {
        const user = JSON.parse(localStorage.getItem('user')) || {}
        this.currentUser = user
        
        // 获取用户角色，如果有多个角色，显示第一个
        if (user.roles && user.roles.length > 0) {
          this.currentUserRole = user.roles[0].name || '系统管理员'
        } else {
          this.currentUserRole = '系统管理员'
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.currentUser = {}
        this.currentUserRole = '系统管理员'
      }
    },
    async handleUserCommand(command) {
      switch (command) {
        case 'profile':
          // 跳转到个人资料页面
          break
        case 'settings':
          this.$router.push('/settings/config')
          break
        case 'logout':
          await authService.logout()
          this.$router.push('/login')
          break
      }
    }
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #2c3e50;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  transition: all 0.3s ease;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-icon {
  font-size: 24px;
  cursor: pointer;
  margin-right: 15px;
  transition: transform 0.3s ease;
}

.collapse-icon:hover {
  transform: scale(1.1);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  display: flex;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  transition: all 0.3s ease;
}

.collapsed-logo {
  font-size: 16px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  height: 100%;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  height: 100%;
  cursor: pointer;
}

.user-avatar {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  margin: 0 10px;
  align-items: flex-start;
  line-height: 1.1;
  min-width: 0; /* 允许子元素收缩 */
  justify-content: center; /* 垂直居中对齐 */
}

.username {
  font-size: 16px;
  font-weight: bold;
  color: #ffffff;
  line-height: 1.2;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  text-align: left; /* 左对齐 */
}

.user-role {
  font-size: 12px;
  color: #e8e8e8;
  opacity: 0.9;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  text-align: left; /* 左对齐 */
}

.dropdown-icon {
  font-size: 16px;
  color: #ffffff;
  transition: transform 0.3s ease;
}

.el-dropdown-link:hover .dropdown-icon {
  transform: rotate(180deg);
}

.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: calc(100vh - 60px - 50px); /* 减去头部和底部高度 */
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-menu {
  border-right: none;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  flex: 1;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  height: calc(100vh - 60px - 50px); /* 减去头部和底部高度 */
}

.footer {
  background-color: #ffffff;
  color: #909399;
  text-align: center;
  padding: 15px 0;
  border-top: 1px solid #e4e7ed;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0; /* 防止footer被压缩 */
}

.copyright {
  font-size: 14px;
}

/* Element Plus 菜单折叠样式 */
.el-menu--vertical.el-menu--collapse {
  width: 64px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.el-menu--vertical.el-menu--collapse .el-menu-item,
.el-menu--vertical.el-menu--collapse .el-sub-menu__title {
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Tooltip 动画 */
.el-tooltip__trigger {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .sidebar {
    transition: width 0.2s ease;
  }
  
  .main-content {
    padding: 15px;
    transition: padding 0.2s ease;
  }
}
</style>