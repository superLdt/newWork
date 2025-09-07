<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

/* 全局样式 */
.el-header {
  padding: 0;
}

/* 移除了对el-aside和el-main的全局样式设置，避免影响折叠功能 */

/* 自定义样式 */
.main-layout {
  height: 100vh;
}

.header {
  background-color: #2c3e50;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.header-right {
  display: flex;
  align-items: center;
}

.username {
  margin: 0 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>