import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue/global'
import App from './App.vue'
import router from './router'

// 权限相关导入
import { setupPermissionGuard } from '@/guards/permission'
import { permission, menuAccess, admin } from '@/directives/permission'

const app = createApp(App)
const pinia = createPinia()

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册权限指令
app.directive('permission', permission)
app.directive('menu-access', menuAccess)
app.directive('admin', admin)

// 使用插件
app.use(pinia)
app.use(ElementPlus)
app.use(router)

// 设置路由权限守卫
setupPermissionGuard(router)

app.mount('#app')