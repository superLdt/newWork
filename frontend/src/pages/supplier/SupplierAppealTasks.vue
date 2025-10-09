<template>
  <div class="supplier-appeal-tasks">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span>我的申诉任务</span>
          <div class="header-actions">
            <el-button type="primary" @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :model="filterForm" inline>
          <el-form-item label="申诉状态">
            <el-select v-model="filterForm.appeal_status" placeholder="请选择申诉状态" clearable>
              <el-option label="申诉中" value="in_progress"></el-option>
              <el-option label="申诉通过" value="approved"></el-option>
              <el-option label="申诉驳回" value="rejected"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="申诉类型">
            <el-select v-model="filterForm.appeal_type" placeholder="请选择申诉类型" clearable>
              <el-option label="降档操作有误" value="downgrade_error"></el-option>
              <el-option label="合并吨位计算错误" value="merge_calculation_error"></el-option>
              <el-option label="实际容积与记录不符" value="volume_mismatch"></el-option>
              <el-option label="其他原因" value="other"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="申诉时间">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 申诉任务列表 -->
      <div class="table-section">
        <el-table
          :data="appealTasks"
          v-loading="loading"
          stripe
          border
          style="width: 100%"
          @row-click="handleRowClick"
        >
          <el-table-column prop="task_id" label="任务ID" width="120" />
          <el-table-column prop="dispatch_number" label="派车单号" width="150" />
          <el-table-column prop="appeal_type" label="申诉类型" width="120">
            <template #default="scope">
              <el-tag :type="getAppealTypeTagType(scope.row.appeal_type)">
                {{ getAppealTypeText(scope.row.appeal_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="appeal_reason" label="申诉原因" min-width="200" show-overflow-tooltip>
            <template #default="scope">
              {{ getAppealReasonText(scope.row.appeal_reason) }}
            </template>
          </el-table-column>
          <el-table-column prop="appeal_status" label="申诉状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.appeal_status)">
                {{ getStatusText(scope.row.appeal_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申诉时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="处理时间" width="180">
            <template #default="scope">
              {{ scope.row.updated_at ? formatDateTime(scope.row.updated_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click.stop="viewAppealDetail(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 申诉详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="申诉详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentAppeal" class="appeal-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentAppeal.task_id }}</el-descriptions-item>
          <el-descriptions-item label="派车单号">{{ currentAppeal.dispatch_number }}</el-descriptions-item>
          <el-descriptions-item label="申诉类型">
            <el-tag :type="getAppealTypeTagType(currentAppeal.appeal_type)">
              {{ getAppealTypeText(currentAppeal.appeal_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申诉状态">
            <el-tag :type="getStatusTagType(currentAppeal.appeal_status)">
              {{ getStatusText(currentAppeal.appeal_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申诉时间" :span="2">
            {{ formatDateTime(currentAppeal.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="申诉原因" :span="2">
            <div class="appeal-reason">{{ getAppealReasonText(currentAppeal.appeal_reason) }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="申诉描述" :span="2" v-if="currentAppeal.appeal_description">
            <div class="appeal-description">{{ currentAppeal.appeal_description }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="处理结果" :span="2" v-if="currentAppeal.review_result">
            <div class="review-result">{{ getReviewResultText(currentAppeal.review_result) }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="处理人" v-if="currentAppeal.reviewer_name">
            {{ currentAppeal.reviewer_name }}
          </el-descriptions-item>
          <el-descriptions-item label="处理时间" v-if="currentAppeal.updated_at">
            {{ formatDateTime(currentAppeal.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 申诉附件 -->
        <div v-if="currentAppeal.attachments && currentAppeal.attachments.length > 0" class="attachments-section">
          <h4>申诉附件</h4>
          <div class="attachment-list">
            <div
              v-for="attachment in currentAppeal.attachments"
              :key="attachment.id"
              class="attachment-item"
            >
              <el-icon><Document /></el-icon>
              <span class="attachment-name">{{ attachment.file_name }}</span>
              <el-button type="text" size="small" @click="downloadAttachment(attachment)">
                下载
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search, RefreshRight, Document } from '@element-plus/icons-vue'
import { supplierService } from '@/services/supplierService'
import { formatDateTime } from '@/utils/dateUtils'

// 响应式数据
const loading = ref(false)
const appealTasks = ref([])
const detailDialogVisible = ref(false)
const currentAppeal = ref(null)

// 筛选表单
const filterForm = reactive({
  appeal_status: '',
  appeal_type: '',
  dateRange: null
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 申诉类型映射（使用供应商前端枚举）
const appealTypeMap = {
  downgrade_error: '降档操作有误',
  merge_calculation_error: '合并吨位计算错误',
  volume_mismatch: '实际容积与记录不符',
  other: '其他原因'
}

// 申诉状态映射
const appealStatusMap = {
  in_progress: '申诉中',
  approved: '申诉通过',
  rejected: '申诉驳回'
}

// 获取申诉类型文本
const getAppealTypeText = (type) => {
  return appealTypeMap[type] || type
}

// 获取申诉类型标签类型
const getAppealTypeTagType = (type) => {
  const typeMap = {
    downgrade_error: 'danger',
    merge_calculation_error: 'warning',
    volume_mismatch: 'info',
    other: 'default'
  }
  return typeMap[type] || 'default'
}

// 获取状态文本
const getStatusText = (status) => {
  return appealStatusMap[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const statusMap = {
    in_progress: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[status] || 'default'
}

// 处理结果中文翻译
const getReviewResultText = (result) => {
  const val = (result || '').toLowerCase()
  const map = {
    approved: '通过',
    rejected: '驳回'
  }
  return map[val] || result || ''
}

// 翻译申诉原因代码为中文
const getAppealReasonText = (reason) => {
  const reasonMap = {
    downgrade_error: '降档操作有误',
    merge_calculation_error: '合并吨位计算错误',
    volume_mismatch: '实际容积与记录不符',
    other: '其他原因'
  }
  return reasonMap[reason] || reason || ''
}

// 基于申诉原因代码派生申诉类型（与原因保持一致）
const categorizeAppealType = (reason) => {
  const code = (reason || '').toLowerCase()
  if (['downgrade_error', 'merge_calculation_error', 'volume_mismatch', 'other'].includes(code)) {
    return code
  }
  // 兼容文本描述的回退逻辑（少量历史数据）
  if (/降档/.test(reason || '')) return 'downgrade_error'
  if (/合并|吨位|计算/.test(reason || '')) return 'merge_calculation_error'
  if (/容积|记录不符|不符/.test(reason || '')) return 'volume_mismatch'
  return 'other'
}

// 推断申诉状态：优先使用显式字段，其次使用审核结果
const deriveAppealStatus = (item) => {
  const direct = (item?.appeal_status || item?.status || '').toLowerCase()
  if (['approved', 'rejected', 'in_progress'].includes(direct)) return direct
  const res = (item?.appeal_review_result || item?.review_result || '').toLowerCase()
  if (res === 'approved') return 'approved'
  if (res === 'rejected') return 'rejected'
  return 'in_progress'
}

// 加载申诉任务列表
const loadAppealTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }

    // 处理日期范围
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0]
      params.end_date = filterForm.dateRange[1]
    }

    // 传递筛选参数到后端，确保服务端分页与筛选一致
    if (filterForm.appeal_status) {
      params.appeal_status = filterForm.appeal_status
      // 兼容后端可能使用的通用字段
      params.status = filterForm.appeal_status
    }
    if (filterForm.appeal_type) {
      params.appeal_type = filterForm.appeal_type
      // 兼容后端可能使用的通用字段
      params.type = filterForm.appeal_type
    }

    console.debug('[SupplierAppealTasks] 请求参数:', params)

    const response = await supplierService.getSupplierAppealTasks(params)
    
    if (response.code === 200) {
      const data = response.data || {}
      // 兼容后端返回结构：tasks 列表与 pagination.total
      let items = data.tasks || data.items || []

      // 为列表项派生申诉状态与类型（兼容不同后端字段）
      items = items.map(item => {
        const typeSource = item.appeal_type || item.appeal_reason || item.reason || ''
        return {
          ...item,
          appeal_status: deriveAppealStatus(item),
          appeal_type: categorizeAppealType(typeSource)
        }
      })

      // 本地筛选：申诉状态与类型
      if (filterForm.appeal_status) {
        items = items.filter(i => i.appeal_status === filterForm.appeal_status)
      }
      if (filterForm.appeal_type) {
        items = items.filter(i => i.appeal_type === filterForm.appeal_type)
      }

      appealTasks.value = items
      console.debug('[SupplierAppealTasks] 列表数量:', {
        total: items.length,
        filteredByStatus: filterForm.appeal_status || 'none',
        filteredByType: filterForm.appeal_type || 'none'
      })
      const pg = data.pagination || {}
      pagination.total = (pg.total ?? data.total ?? 0)
      // 同步后端分页信息（若提供）
      if (pg.per_page) {
        pagination.size = pg.per_page
      }
      if (pg.page) {
        pagination.page = pg.page
      }
    } else {
      ElMessage.error(response.message || '获取申诉任务列表失败')
    }
  } catch (error) {
    console.error('加载申诉任务失败:', error)
    ElMessage.error('获取申诉任务列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadAppealTasks()
}

// 重置筛选条件
const resetFilter = () => {
  Object.assign(filterForm, {
    appeal_status: '',
    appeal_type: '',
    dateRange: null
  })
  pagination.page = 1
  loadAppealTasks()
}

// 刷新数据
const refreshData = () => {
  loadAppealTasks()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadAppealTasks()
}

// 当前页改变
const handleCurrentChange = (page) => {
  pagination.page = page
  loadAppealTasks()
}

// 行点击事件
const handleRowClick = (row) => {
  viewAppealDetail(row)
}

// 查看申诉详情
const viewAppealDetail = async (appeal) => {
  try {
    const response = await supplierService.getAppealDetail(appeal.id)
    
    if (response.code === 200) {
      const detail = response.data || {}
      // 将后端返回的申诉详情字段映射到页面需要的结构
      currentAppeal.value = {
        task_id: detail.task_id || appeal.task_id || appeal.id,
        dispatch_number: appeal.dispatch_number || detail.task_id || '',
        appeal_type: categorizeAppealType(detail.appeal_reason),
        appeal_status: deriveAppealStatus(detail),
        created_at: detail.appeal_submitted_at || appeal.created_at || '',
        updated_at: appeal.appeal_reviewed_at || '',
        review_result: appeal.appeal_review_result || '',
        reviewer_name: appeal.appeal_reviewer_name || '',
        appeal_reason: detail.appeal_reason || '',
        appeal_description: detail.appeal_description || '',
        attachments: (detail.evidence_files || []).map(f => ({
          id: f.id,
          file_name: f.filename,
          url: f.url,
          file_size: f.file_size,
          upload_time: f.upload_time
        }))
      }
      detailDialogVisible.value = true
    } else {
      ElMessage.error(response.message || '获取申诉详情失败')
    }
  } catch (error) {
    console.error('获取申诉详情失败:', error)
    ElMessage.error('获取申诉详情失败: ' + error.message)
  }
}

// 下载附件
const downloadAttachment = async (attachment) => {
  try {
    // 优先使用后端返回的文件URL直接下载
    if (attachment.url) {
      const link = document.createElement('a')
      link.href = attachment.url
      link.setAttribute('download', attachment.file_name || '')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else {
      // 兼容旧逻辑：通过服务端下载接口（如果存在）
      const response = await supplierService.downloadAppealAttachment(attachment.id)
      const url = window.URL.createObjectURL(new Blob([response]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', attachment.file_name || '')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('下载附件失败:', error)
    ElMessage.error('下载附件失败: ' + error.message)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadAppealTasks()
})

// 当选择筛选条件变化时自动刷新列表
watch(() => filterForm.appeal_status, () => {
  pagination.page = 1
  loadAppealTasks()
})
watch(() => filterForm.appeal_type, () => {
  pagination.page = 1
  loadAppealTasks()
})
</script>

<style scoped>
.supplier-appeal-tasks {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.table-section {
  margin-bottom: 20px;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.appeal-detail {
  max-height: 600px;
  overflow-y: auto;
}

.appeal-reason,
.appeal-description,
.review-result {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.attachments-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.attachments-section h4 {
  margin-bottom: 12px;
  color: #303133;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.attachment-name {
  flex: 1;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .supplier-appeal-tasks {
    padding: 10px;
  }
  
  .filter-section {
    padding: 12px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>