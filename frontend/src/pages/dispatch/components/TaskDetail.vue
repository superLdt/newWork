<template>
  <div class="task-detail-container">
    <el-descriptions title="基本信息" :column="2" border>
      <el-descriptions-item label="任务ID">{{ task.task_id }}</el-descriptions-item>
      <el-descriptions-item label="需求日期">{{ task.required_date }}</el-descriptions-item>
      <el-descriptions-item label="起始站段">{{ task.start_bureau }}</el-descriptions-item>
      <el-descriptions-item label="路线方向">{{ task.route_direction }}</el-descriptions-item>
      <el-descriptions-item label="运输公司">{{ task.carrier_company }}</el-descriptions-item>
      <el-descriptions-item label="路线名称">{{ task.route_name }}</el-descriptions-item>
      <el-descriptions-item label="运输类型">{{ task.transport_type }}</el-descriptions-item>
      <el-descriptions-item label="需求类型">{{ task.requirement_type }}</el-descriptions-item>
      <el-descriptions-item label="需求容积">{{ task.volume }}</el-descriptions-item>
      <el-descriptions-item label="需求重量">{{ task.weight }}</el-descriptions-item>
      <el-descriptions-item label="派车轨道">{{ task.dispatch_track }}</el-descriptions-item>
      <el-descriptions-item label="任务状态">
        <el-tag :type="getStatusType(task.status)">{{ task.status }}</el-tag>
      </el-descriptions-item>
    </el-descriptions>
    
    <el-divider content-position="left">特殊要求</el-divider>
    <div class="special-requirements">
      {{ task.special_requirements || '无' }}
    </div>
    
    <el-divider content-position="left">发起人信息</el-divider>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="发起人角色">{{ task.initiator_role }}</el-descriptions-item>
      <el-descriptions-item label="发起人部门">{{ task.initiator_department }}</el-descriptions-item>
    </el-descriptions>
    
    <template v-if="task.vehicles && task.vehicles.length > 0">
      <el-divider content-position="left">分配车辆信息</el-divider>
      <el-table :data="task.vehicles" style="width: 100%" border>
        <el-table-column prop="vehicle_id" label="车辆ID" width="120"></el-table-column>
        <el-table-column prop="plate_number" label="车牌号" width="120"></el-table-column>
        <el-table-column prop="driver_name" label="司机姓名" width="120"></el-table-column>
        <el-table-column prop="driver_phone" label="司机电话" width="150"></el-table-column>
        <el-table-column prop="vehicle_type" label="车型" width="100"></el-table-column>
        <el-table-column prop="capacity" label="载重量" width="100"></el-table-column>
        <el-table-column prop="volume" label="容积" width="100"></el-table-column>
        <el-table-column prop="notes" label="备注"></el-table-column>
      </el-table>
    </template>
    
    <template v-if="task.status_history && task.status_history.length > 0">
      <el-divider content-position="left">状态历史</el-divider>
      <el-timeline>
        <el-timeline-item
          v-for="(history, index) in task.status_history"
          :key="index"
          :timestamp="history.timestamp"
          :type="getTimelineItemType(history.status)"
        >
          <h4>{{ history.status }}</h4>
          <p>操作人: {{ history.operator }}</p>
          <p>备注: {{ history.comment || '无' }}</p>
        </el-timeline-item>
      </el-timeline>
    </template>
  </div>
</template>

<script>
export default {
  name: 'TaskDetail',
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  setup() {
    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        'pending': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'assigned': 'primary',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
        '待审核': 'info',
        '已审核': 'success',
        '已拒绝': 'danger',
        '已分配': 'primary',
        '进行中': 'warning',
        '已完成': 'success',
        '已取消': 'danger'
      }
      return statusMap[status] || 'info'
    }
    
    // 获取时间线项目类型
    const getTimelineItemType = (status) => {
      const typeMap = {
        'pending': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'assigned': 'primary',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
        '待审核': 'info',
        '已审核': 'success',
        '已拒绝': 'danger',
        '已分配': 'primary',
        '进行中': 'warning',
        '已完成': 'success',
        '已取消': 'danger'
      }
      return typeMap[status] || 'info'
    }
    
    return {
      getStatusType,
      getTimelineItemType
    }
  }
}
</script>

<style scoped>
.task-detail-container {
  padding: 20px;
}

.special-requirements {
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
  min-height: 60px;
}

.el-divider {
  margin: 24px 0;
}
</style>