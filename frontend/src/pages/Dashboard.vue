<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-summary">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-blue">
              <el-icon color="#409eff"><Van /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">24</div>
              <div class="stat-label">车辆总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-green">
              <el-icon color="#67c23a"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">18</div>
              <div class="stat-label">今日任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-orange">
              <el-icon color="#e6a23c"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">126</div>
              <div class="stat-label">注册用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-gray">
              <el-icon color="#909399"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">98%</div>
              <div class="stat-label">任务完成率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="chart-section">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>任务统计</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="taskChart" class="chart-wrapper"></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>派车统计</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="dispatchChart" class="chart-wrapper"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="recent-section">
      <el-col :span="24">
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <span>最新任务</span>
            </div>
          </template>
          <el-table :data="recentTasks" style="width: 100%">
            <el-table-column prop="id" label="任务ID" width="100"></el-table-column>
            <el-table-column prop="vehicle" label="车辆" width="120"></el-table-column>
            <el-table-column prop="driver" label="司机" width="120"></el-table-column>
            <el-table-column prop="route" label="路线"></el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getTagType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="180"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { Van, List, User, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  components: {
    Van,
    List,
    User,
    TrendCharts
  },
  data() {
    return {
      recentTasks: [
        {
          id: 'T2023001',
          vehicle: '京A12345',
          driver: '张三',
          route: '北京 → 上海',
          status: '进行中',
          time: '2023-05-15 08:30'
        },
        {
          id: 'T2023002',
          vehicle: '沪B67890',
          driver: '李四',
          route: '上海 → 广州',
          status: '已完成',
          time: '2023-05-15 09:15'
        },
        {
          id: 'T2023003',
          vehicle: '粤C11111',
          driver: '王五',
          route: '广州 → 深圳',
          status: '待发车',
          time: '2023-05-15 10:00'
        },
        {
          id: 'T2023004',
          vehicle: '苏D22222',
          driver: '赵六',
          route: '南京 → 杭州',
          status: '已取消',
          time: '2023-05-15 11:30'
        },
        {
          id: 'T2023005',
          vehicle: '浙E33333',
          driver: '孙七',
          route: '杭州 → 宁波',
          status: '进行中',
          time: '2023-05-15 13:45'
        }
      ]
    }
  },
  mounted() {
    this.initCharts()
  },
  beforeUnmount() {
    if (this.taskChart) {
      this.taskChart.dispose()
    }
    if (this.dispatchChart) {
      this.dispatchChart.dispose()
    }
  },
  methods: {
    initCharts() {
      // 任务统计图表
      this.taskChart = echarts.init(this.$refs.taskChart)
      const taskOption = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: [12, 18, 15, 22, 19, 25, 20],
            type: 'line',
            smooth: true,
            areaStyle: {
              color: '#409eff'
            },
            lineStyle: {
              color: '#409eff'
            }
          }
        ]
      }
      this.taskChart.setOption(taskOption)
      
      // 派车统计图表
      this.dispatchChart = echarts.init(this.$refs.dispatchChart)
      const dispatchOption = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          bottom: '0%',
          left: 'center'
        },
        series: [
          {
            name: '派车统计',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 12, name: '已完成', itemStyle: { color: '#67c23a' } },
              { value: 5, name: '进行中', itemStyle: { color: '#409eff' } },
              { value: 3, name: '待发车', itemStyle: { color: '#e6a23c' } },
              { value: 2, name: '已取消', itemStyle: { color: '#909399' } }
            ]
          }
        ]
      }
      this.dispatchChart.setOption(dispatchOption)
      
      // 监听窗口大小变化，自适应图表
      window.addEventListener('resize', this.resizeCharts)
    },
    
    resizeCharts() {
      if (this.taskChart) {
        this.taskChart.resize()
      }
      if (this.dispatchChart) {
        this.dispatchChart.resize()
      }
    },
    
    getTagType(status) {
      const statusMap = {
        '已完成': 'success',
        '进行中': 'primary',
        '待发车': 'warning',
        '已取消': 'info'
      }
      return statusMap[status] || 'info'
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background-color: #f5f7fa;
}

.stats-summary {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.bg-blue {
  background-color: #ecf5ff;
}

.bg-green {
  background-color: #f0f9eb;
}

.bg-orange {
  background-color: #fdf6ec;
}

.bg-gray {
  background-color: #f4f4f5;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.chart-container {
  height: 300px;
}

.chart-wrapper {
  width: 100%;
  height: 100%;
}

.recent-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 4px;
}
</style>