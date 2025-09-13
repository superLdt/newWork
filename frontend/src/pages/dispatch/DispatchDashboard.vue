<template>
  <div class="dispatch-dashboard-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>调度仪表盘</h1>
      <el-button type="primary" @click="refreshDashboard">刷新数据</el-button>
    </div>

    <!-- 统计概览卡片 -->
    <div class="overview-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon total-tasks">
                <i class="el-icon-document"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardData.total_tasks || 0 }}</div>
                <div class="stat-label">总任务数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon today-tasks">
                <i class="el-icon-date"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardData.today_tasks || 0 }}</div>
                <div class="stat-label">今日新增</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon urgent-tasks">
                <i class="el-icon-warning"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardData.urgent_tasks || 0 }}</div>
                <div class="stat-label">紧急任务</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon timeout-tasks">
                <i class="el-icon-time"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardData.timeout_tasks || 0 }}</div>
                <div class="stat-label">即将超时</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分布图表区域 -->
    <div class="distribution-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <h3>任务状态分布</h3>
              </div>
            </template>
            <div class="chart-container">
              <div v-if="dashboardData.status_distribution && dashboardData.status_distribution.length > 0" 
                   class="pie-chart" 
                   ref="statusChart" 
                   style="height: 300px;"></div>
              <el-empty v-else description="暂无数据" :image-size="100"></el-empty>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <h3>轨道类型分布</h3>
              </div>
            </template>
            <div class="chart-container">
              <div v-if="dashboardData.track_distribution && dashboardData.track_distribution.length > 0" 
                   class="pie-chart" 
                   ref="trackChart" 
                   style="height: 300px;"></div>
              <el-empty v-else description="暂无数据" :image-size="100"></el-empty>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 紧急任务列表 -->
    <div class="urgent-tasks-section">
      <el-card class="urgent-card" shadow="hover">
        <template #header>
          <div class="urgent-header">
            <h3>紧急任务提醒</h3>
            <el-tag type="danger" v-if="dashboardData.urgent_task_list && dashboardData.urgent_task_list.length > 0">
              紧急任务: {{ dashboardData.urgent_task_list.length }} 个
            </el-tag>
          </div>
        </template>
        <div class="urgent-content">
          <el-table
            v-loading="loading"
            :data="dashboardData.urgent_task_list"
            style="width: 100%"
            empty-text="暂无紧急任务"
          >
            <el-table-column prop="task_id" label="任务ID" width="120"></el-table-column>
            <el-table-column prop="required_date" label="需求日期" width="120"></el-table-column>
            <el-table-column prop="origin_bureau" label="始发局" width="150"></el-table-column>
            <el-table-column prop="mail_route_name" label="邮路名称"></el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewTaskDetail(scope.row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { dispatchService } from '@/services/dispatchService'

/**
 * 调度仪表盘组件
 * 展示调度任务的统计概览、状态分布和紧急任务提醒
 */
export default {
  name: 'DispatchDashboard',
  
  setup() {
    const loading = ref(false)
    const dashboardData = reactive({})
    const statusChart = ref(null)
    const trackChart = ref(null)
    let statusChartInstance = null
    let trackChartInstance = null

    /**
     * 获取状态标签类型
     * @param {string} status - 任务状态
     * @returns {string} 标签类型
     */
    const getStatusType = (status) => {
      const statusMap = {
        'pending': 'warning',
        'approved': 'success', 
        'assigned': 'primary',
        'in_progress': 'info',
        'completed': 'success',
        'cancelled': 'danger'
      }
      return statusMap[status] || 'info'
    }

    /**
     * 获取仪表盘数据
     */
    const fetchDashboardData = async () => {
      loading.value = true
      try {
        const result = await dispatchService.getDashboardData()
        if (result.code === 0) {
          Object.assign(dashboardData, result.data)
          // 数据加载完成后渲染图表
          nextTick(() => {
            renderCharts()
          })
        } else {
          ElMessage.error(result.message || '获取仪表盘数据失败')
        }
      } catch (error) {
        console.error('获取仪表盘数据失败:', error)
        ElMessage.error('获取仪表盘数据失败')
      } finally {
        loading.value = false
      }
    }

    /**
     * 渲染状态分布饼图
     */
    const renderStatusChart = () => {
      if (!statusChart.value || !dashboardData.status_distribution) return
      
      if (statusChartInstance) {
        statusChartInstance.dispose()
      }
      
      statusChartInstance = echarts.init(statusChart.value)
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          data: dashboardData.status_distribution.map(item => item.status)
        },
        series: [{
          name: '任务状态',
          type: 'pie',
          radius: ['50%', '70%'],
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
          data: dashboardData.status_distribution.map(item => ({
            value: item.count,
            name: item.status
          }))
        }]
      }
      
      statusChartInstance.setOption(option)
    }

    /**
     * 渲染轨道类型分布饼图
     */
    const renderTrackChart = () => {
      if (!trackChart.value || !dashboardData.track_distribution) return
      
      if (trackChartInstance) {
        trackChartInstance.dispose()
      }
      
      trackChartInstance = echarts.init(trackChart.value)
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          data: dashboardData.track_distribution.map(item => item.dispatch_track)
        },
        series: [{
          name: '轨道类型',
          type: 'pie',
          radius: ['50%', '70%'],
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
          data: dashboardData.track_distribution.map(item => ({
            value: item.count,
            name: item.dispatch_track
          }))
        }]
      }
      
      trackChartInstance.setOption(option)
    }

    /**
     * 渲染所有图表
     */
    const renderCharts = () => {
      renderStatusChart()
      renderTrackChart()
    }

    /**
     * 刷新仪表盘数据
     */
    const refreshDashboard = () => {
      fetchDashboardData()
    }

    /**
     * 查看任务详情
     * @param {Object} task - 任务对象
     */
    const viewTaskDetail = (task) => {
      // 这里可以跳转到任务详情页面或打开详情对话框
      console.log('查看任务详情:', task)
      ElMessage.info(`查看任务 ${task.task_id} 的详情`)
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchDashboardData()
      // 监听窗口大小变化，重新渲染图表
      window.addEventListener('resize', renderCharts)
    })

    // 组件卸载前销毁图表实例
    onBeforeUnmount(() => {
      if (statusChartInstance) {
        statusChartInstance.dispose()
        statusChartInstance = null
      }
      if (trackChartInstance) {
        trackChartInstance.dispose()
        trackChartInstance = null
      }
      window.removeEventListener('resize', renderCharts)
    })

    return {
      loading,
      dashboardData,
      statusChart,
      trackChart,
      getStatusType,
      refreshDashboard,
      viewTaskDetail
    }
  }
}
</script>

<style scoped>
.dispatch-dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.overview-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  border: none;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.total-tasks {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.today-tasks {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.urgent-tasks {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.stat-icon.timeout-tasks {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.distribution-charts {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 8px;
  border: none;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.chart-container {
  position: relative;
}

.urgent-tasks-section {
  margin-bottom: 20px;
}

.urgent-card {
  border-radius: 8px;
  border: none;
}

.urgent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.urgent-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.urgent-content {
  padding: 10px 0;
}

.pie-chart {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .overview-cards .el-col {
    margin-bottom: 20px;
  }
  
  .distribution-charts .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>