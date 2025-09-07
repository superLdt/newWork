<template>
  <div class="audit-log">
    <el-card class="log-card">
      <template #header>
        <div class="card-header">
          <span>审计日志</span>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="margin-right: 20px;"
        />
        <el-select v-model="userFilter" placeholder="用户" style="width: 150px; margin-right: 20px;">
          <el-option label="全部用户" value=""></el-option>
          <el-option label="管理员" value="admin"></el-option>
          <el-option label="经理" value="manager1"></el-option>
          <el-option label="用户1" value="user1"></el-option>
        </el-select>
        <el-select v-model="actionFilter" placeholder="操作类型" style="width: 150px; margin-right: 20px;">
          <el-option label="全部操作" value=""></el-option>
          <el-option label="登录" value="login"></el-option>
          <el-option label="登出" value="logout"></el-option>
          <el-option label="创建" value="create"></el-option>
          <el-option label="更新" value="update"></el-option>
          <el-option label="删除" value="delete"></el-option>
        </el-select>
        <el-button type="primary" @click="searchLogs">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      
      <el-table 
        :data="filteredLogs" 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
        <el-table-column prop="user" label="用户" width="120"></el-table-column>
        <el-table-column prop="action" label="操作" width="120">
          <template #default="scope">
            <el-tag :type="getActionType(scope.row.action)">
              {{ getActionName(scope.row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="资源" width="150"></el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column prop="ipAddress" label="IP地址" width="150"></el-table-column>
      </el-table>
      
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalLogs"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'AuditLog',
  components: {
    Search
  },
  data() {
    return {
      logs: [
        {
          id: 1,
          timestamp: '2023-05-15 14:30:25',
          user: 'admin',
          action: 'login',
          resource: '系统',
          description: '用户登录系统',
          ipAddress: '192.168.1.100'
        },
        {
          id: 2,
          timestamp: '2023-05-15 14:35:12',
          user: 'admin',
          action: 'create',
          resource: '用户管理',
          description: '创建新用户 user3',
          ipAddress: '192.168.1.100'
        },
        {
          id: 3,
          timestamp: '2023-05-15 15:20:45',
          user: 'manager1',
          action: 'update',
          resource: '车辆管理',
          description: '更新车辆信息 车牌号:京A12345',
          ipAddress: '192.168.1.105'
        },
        {
          id: 4,
          timestamp: '2023-05-15 16:10:30',
          user: 'user1',
          action: 'login',
          resource: '系统',
          description: '用户登录系统',
          ipAddress: '192.168.1.110'
        },
        {
          id: 5,
          timestamp: '2023-05-15 17:45:18',
          user: 'admin',
          action: 'delete',
          resource: '用户管理',
          description: '删除用户 user2',
          ipAddress: '192.168.1.100'
        }
      ],
      dateRange: '',
      userFilter: '',
      actionFilter: '',
      currentPage: 1,
      pageSize: 10,
      totalLogs: 5,
      loading: false
    }
  },
  computed: {
    filteredLogs() {
      // 在实际应用中，这里会根据过滤条件筛选数据
      // 目前只是演示分页功能
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.logs.slice(start, end)
    }
  },
  methods: {
    getActionType(action) {
      const typeMap = {
        login: 'success',
        logout: 'info',
        create: 'primary',
        update: 'warning',
        delete: 'danger'
      }
      return typeMap[action] || 'info'
    },
    getActionName(action) {
      const nameMap = {
        login: '登录',
        logout: '登出',
        create: '创建',
        update: '更新',
        delete: '删除'
      }
      return nameMap[action] || action
    },
    searchLogs() {
      ElMessage.info('正在搜索日志...')
      this.loading = true
      // 模拟搜索过程
      setTimeout(() => {
        this.loading = false
        ElMessage.success('搜索完成')
      }, 500)
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
    },
    handleCurrentChange(val) {
      this.currentPage = val
    }
  }
}
</script>

<style scoped>
.audit-log {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination-bar {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>