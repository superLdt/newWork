<template>
  <!-- 有子菜单的情况 -->
  <el-sub-menu
    v-if="menu.children && menu.children.length > 0"
    :index="menu.path || menu.code"
    :key="menu.id"
  >
    <template #title>
      <el-icon v-if="menu.icon">
        <component :is="getIconComponent(menu.icon)" />
      </el-icon>
      <span>{{ menu.name }}</span>
    </template>
    
    <template v-for="child in menu.children" :key="child.id">
      <menu-item :menu="child" />
    </template>
  </el-sub-menu>
  
  <!-- 没有子菜单的情况 -->
  <el-menu-item
    v-else
    :index="menu.path || menu.code"
    :key="menu.id"
    @click="handleMenuClick(menu)"
  >
    <el-icon v-if="menu.icon">
      <component :is="getIconComponent(menu.icon)" />
    </el-icon>
    <template #title>
      <span>{{ menu.name }}</span>
    </template>
  </el-menu-item>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
  User,
  UserFilled,
  Key,
  DataBoard,
  Coordinate,
  OfficeBuilding
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  menu: {
    type: Object,
    required: true
  }
})

// 使用 router
const router = useRouter()

// 图标映射
const iconMap = {
  'el-icon-document': Document,
  'el-icon-menu': IconMenu,
  'el-icon-location': Location,
  'el-icon-setting': Setting,
  'el-icon-user': User,
  'el-icon-user-solid': UserFilled,
  'el-icon-key': Key,
  'el-icon-data-board': DataBoard,
  'el-icon-coordinate': Coordinate,
  'el-icon-office-building': OfficeBuilding
}

// 获取图标组件
function getIconComponent(iconName) {
  return iconMap[iconName] || Document
}

// 处理菜单点击
function handleMenuClick(menu) {
  if (menu.path) {
    try {
      router.push(menu.path)
    } catch (error) {
      console.error('Navigation failed:', error)
      ElMessage.error('页面跳转失败')
    }
  } else {
    console.warn('Menu path is not defined:', menu)
  }
}
</script>

<style scoped>
.el-menu-item,
.el-sub-menu {
  &.is-active {
    background-color: #409EFF !important;
  }
}

.el-menu-item:hover,
.el-sub-menu__title:hover {
  background-color: #263445 !important;
}

.el-icon {
  margin-right: 8px;
  width: 16px;
  height: 16px;
}
</style>