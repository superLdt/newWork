<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="header-left">
        <div class="logo">
          <el-icon class="collapse-icon" @click="toggleSidebar">
            <component :is="isSidebarCollapsed ? Expand : Fold" />
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
              <ArrowDown />
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
        <!-- 使用动态菜单组件 -->
         <dynamic-menu :is-collapse="isSidebarCollapsed" />
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

<script setup>
import { ref, computed } from 'vue';
import { usePermissionStore } from '@/stores/permission';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { authService } from '@/services/authService';
import { Expand, Fold, User, ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue';
import DynamicMenu from '@/components/DynamicMenu.vue';

const permissionStore = usePermissionStore();
const router = useRouter();

const isSidebarCollapsed = ref(false);

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const currentUser = computed(() => permissionStore.userInfo || {});
const currentUserRole = computed(() => {
  if (permissionStore.isAdmin) return '超级管理员';
  return permissionStore.roles && permissionStore.roles.length > 0 ? permissionStore.roles[0] : '系统管理员';
});

const handleUserCommand = (command) => {
  if (command === 'logout') {
    authService.logout();
    router.push('/login');
    ElMessage.success('您已成功退出登录');
  } else {
    ElMessage.info(`点击了 ${command}`);
  }
};
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