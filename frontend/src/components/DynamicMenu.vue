<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="isCollapse"
    :unique-opened="false"
    class="dynamic-menu"
    router
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409EFF"
  >
    <template v-for="menu in menuTree" :key="menu.id">
      <menu-item :menu="menu" />
    </template>
  </el-menu>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePermissionStore } from '@/stores/permission'
import MenuItem from './MenuItem.vue'

// Props
const props = defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  }
})

// 使用 stores 和 router
const route = useRoute()
const permissionStore = usePermissionStore()

// 计算属性
const menuTree = computed(() => {
  return permissionStore.menuTree
})

const activeMenu = computed(() => {
  const { path } = route
  return path
})

// 监听路由变化
watch(
  () => route.path,
  () => {
    // 可以在这里添加菜单激活状态的处理逻辑
  }
)

// 组件挂载时加载菜单
onMounted(async () => {
  if (permissionStore.menus.length === 0) {
    await permissionStore.loadUserMenus()
  }
})
</script>

<style scoped>
.dynamic-menu {
  height: 100%;
  border-right: none;
}

.dynamic-menu:not(.el-menu--collapse) {
  width: 200px;
}
</style>