<template>
  <div class="coming-soon">
    <el-card class="soon-card">
      <div class="card-content">
        <el-icon :size="80" color="#409eff"><Timer /></el-icon>
        <h2>功能即将上线</h2>
        <p>我们正在努力开发此功能，敬请期待！</p>
        <el-button type="primary" @click="$router.back()">返回上一页</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Timer } from '@element-plus/icons-vue'

export default {
  name: 'ComingSoon',
  components: {
    Timer
  }
}
</script>

<style scoped>
.coming-soon {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 400px;
}

.soon-card {
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.card-content {
  padding: 40px 20px;
}

.card-content h2 {
  margin: 20px 0 10px;
  color: #303133;
}

.card-content p {
  color: #606266;
  margin-bottom: 30px;
}
</style>