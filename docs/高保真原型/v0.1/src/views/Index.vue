<template>
  <div class="index-container">
    <div class="index-header">
      <h2>索引管理</h2>
      <p>管理文件索引，监控索引任务状态</p>
      <a-button type="primary" @click="showAddFolderModal = true">
        <PlusOutlined />
        添加文件夹
      </a-button>
    </div>

    <!-- 统计信息 -->
    <div class="stats-cards">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stats-card">
            <a-statistic
              title="已索引文件"
              :value="stats.totalFiles"
              :precision="0"
              suffix="个"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stats-card">
            <a-statistic
              title="索引大小"
              :value="stats.indexSize"
              :precision="2"
              suffix="GB"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stats-card">
            <a-statistic
              title="活跃任务"
              :value="stats.activeTasks"
              :precision="0"
              suffix="个"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stats-card">
            <a-statistic
              title="成功率"
              :value="stats.successRate"
              :precision="1"
              suffix="%"
            />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 索引列表 -->
    <a-card class="index-list">
      <a-table
        :dataSource="indexList"
        :columns="indexColumns"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <!-- 状态列 -->
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            <SyncOutlined v-if="record.status === 'processing'" spin />
            {{ getStatusLabel(record.status) }}
          </a-tag>
        </template>

        <!-- 进度列 -->
        <template #progress="{ record }">
          <div v-if="record.status === 'processing'" class="progress-wrapper">
            <a-progress
              :percent="record.progress || 0"
              :show-info="true"
              size="small"
            />
            <div class="progress-info">
              {{ record.processedFiles }} / {{ record.totalFiles }}
            </div>
          </div>
          <span v-else>-</span>
        </template>

        <!-- 操作列 -->
        <template #action="{ record }">
          <a-dropdown :trigger="['click']" placement="bottomRight">
            <a-button type="link" size="small">
              操作 <DownOutlined />
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="viewIndexDetails(record)">
                  <EyeOutlined />
                  详情
                </a-menu-item>
                <a-menu-item
                  v-if="record.status === 'completed'"
                  @click="smartUpdate(record)"
                >
                  <SyncOutlined />
                  智能更新
                </a-menu-item>
                <a-menu-item
                  v-if="record.status === 'processing'"
                  @click="stopIndex(record)"
                  danger
                >
                  <StopOutlined />
                  停止
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item
                  @click="confirmDelete(record)"
                  danger
                >
                  <DeleteOutlined />
                  删除
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </template>
      </a-table>
    </a-card>

    <!-- 添加文件夹对话框 -->
    <a-modal
      v-model:open="showAddFolderModal"
      title="添加索引文件夹"
      width="600px"
      @ok="handleAddFolder"
    >
      <a-alert
        message="提示"
        description="当前仅支持一级目录索引，不会递归索引子文件夹"
        type="info"
        show-icon
        style="margin-bottom: 16px"
      />
      <a-form layout="vertical">
        <a-form-item label="选择文件夹">
          <a-input
            v-model:value="newFolder.path"
            placeholder="点击浏览选择文件夹"
            readonly
          >
            <template #suffix>
              <a-button type="link" @click="browseFolder">浏览</a-button>
            </template>
          </a-input>
        </a-form-item>

        <a-form-item label="文件类型">
          <a-checkbox-group v-model:value="newFolder.fileTypes">
            <a-checkbox value="document">文档 (txt, markdown, pdf, xls/xlsx, ppt/pptx, doc/docx)</a-checkbox>
            <a-checkbox value="audio">音频 (mp3, wav)</a-checkbox>
            <a-checkbox value="video">视频 (mp4, avi)</a-checkbox>
            <a-checkbox value="image">图片 (png, jpg)</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 索引详情对话框 -->
    <a-modal
      v-model:open="showDetailsModal"
      title="索引详情"
      width="800px"
      :footer="null"
    >
      <div v-if="selectedIndex" class="index-details">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="文件夹路径">
            {{ selectedIndex.folderPath }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(selectedIndex.status)">
              {{ getStatusLabel(selectedIndex.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="总文件数">
            {{ selectedIndex.totalFiles }}
          </a-descriptions-item>
          <a-descriptions-item label="已处理文件">
            {{ selectedIndex.processedFiles }}
          </a-descriptions-item>
          <a-descriptions-item label="错误数量">
            {{ selectedIndex.errorCount }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ formatDate(selectedIndex.createdAt) }}
          </a-descriptions-item>
          <a-descriptions-item label="完成时间">
            {{ selectedIndex.completedAt ? formatDate(selectedIndex.completedAt) : '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="处理时间">
            {{ selectedIndex.completedAt ? calculateDuration(selectedIndex.createdAt, selectedIndex.completedAt) : '-' }}
          </a-descriptions-item>
        </a-descriptions>

        <!-- 错误信息 -->
        <div v-if="selectedIndex.errorMessage" class="error-section">
          <h4>错误信息</h4>
          <a-alert
            :message="selectedIndex.errorMessage"
            type="error"
            show-icon
          />
        </div>

        <!-- 实时日志 -->
        <div v-if="selectedIndex.status === 'processing'" class="log-section">
          <h4>实时日志</h4>
          <div class="log-container">
            <div
              v-for="(log, index) in mockLogs"
              :key="index"
              class="log-entry"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-level" :class="log.level">{{ log.level }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  SyncOutlined,
  DownOutlined,
  EyeOutlined,
  StopOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'

// 响应式数据
const showAddFolderModal = ref(false)
const showDetailsModal = ref(false)
const selectedIndex = ref(null)

// 统计数据
const stats = reactive({
  totalFiles: 1234,
  indexSize: 2.3,
  activeTasks: 2,
  successRate: 98.5
})

// 新建文件夹配置
const newFolder = reactive({
  path: '',
  fileTypes: ['document', 'audio', 'video', 'image']
})

// 索引列表
const indexList = ref([
  {
    id: 1,
    folderPath: 'D:\\Work\\Documents',
    status: 'completed',
    progress: 100,
    totalFiles: 567,
    processedFiles: 567,
    errorCount: 2,
    createdAt: '2024-01-20T10:00:00Z',
    completedAt: '2024-01-20T10:15:00Z'
  },
  {
    id: 2,
    folderPath: 'D:\\Work\\Projects',
    status: 'processing',
    progress: 45,
    totalFiles: 234,
    processedFiles: 105,
    errorCount: 0,
    createdAt: '2024-01-20T14:00:00Z',
    completedAt: null
  },
  {
    id: 3,
    folderPath: 'D:\\Downloads',
    status: 'failed',
    progress: 23,
    totalFiles: 1234,
    processedFiles: 284,
    errorCount: 1,
    createdAt: '2024-01-19T16:00:00Z',
    completedAt: null,
    errorMessage: '文件访问权限不足: D:\\Downloads\\protected.zip'
  }
])

// Mock日志
const mockLogs = ref([
  { time: '14:30:15', level: 'info', message: '开始处理文件: project.pdf' },
  { time: '14:30:18', level: 'info', message: '文件处理完成: project.pdf (2.3MB)' },
  { time: '14:30:22', level: 'warn', message: '文件过大，跳过: large_video.mp4 (500MB)' },
  { time: '14:30:25', level: 'info', message: '开始处理文件: report.docx' }
])

// 表格配置
const indexColumns = [
  {
    title: '文件夹路径',
    dataIndex: 'folderPath',
    key: 'folderPath',
    ellipsis: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    slots: { customRender: 'status' }
  },
  {
    title: '进度',
    dataIndex: 'progress',
    key: 'progress',
    slots: { customRender: 'progress' }
  },
  {
    title: '文件数',
    dataIndex: 'totalFiles',
    key: 'totalFiles'
  },
  {
    title: '错误数',
    dataIndex: 'errorCount',
    key: 'errorCount'
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    customRender: ({ text }) => formatDate(text)
  },
  {
    title: '操作',
    key: 'action',
    slots: { customRender: 'action' }
  }
]

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: computed(() => indexList.value.length),
  showSizeChanger: true,
  showQuickJumper: true
})

// 方法
const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    pending: 'default',
    processing: 'processing',
    completed: 'success',
    failed: 'error'
  }
  return colorMap[status] || 'default'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return labelMap[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const calculateDuration = (start: string, end: string) => {
  const startTime = new Date(start).getTime()
  const endTime = new Date(end).getTime()
  const duration = Math.floor((endTime - startTime) / 1000)
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60
  return `${minutes}分${seconds}秒`
}

const browseFolder = () => {
  newFolder.path = 'D:\\Work\\Documents'
}

const handleAddFolder = () => {
  if (!newFolder.path) {
    message.error('请选择文件夹路径')
    return
  }

  // 添加新索引
  const newIndex = {
    id: Date.now(),
    folderPath: newFolder.path,
    status: 'pending',
    progress: 0,
    totalFiles: 0,
    processedFiles: 0,
    errorCount: 0,
    createdAt: new Date().toISOString(),
    completedAt: null
  }

  indexList.value.unshift(newIndex)
  showAddFolderModal.value = false
  message.success('索引任务已创建')

  // 重置表单
  newFolder.path = ''
  newFolder.fileTypes = ['document', 'audio', 'video', 'image']
}

const viewIndexDetails = (record: any) => {
  selectedIndex.value = record
  showDetailsModal.value = true
}

const smartUpdate = (record: any) => {
  // 模拟智能判断逻辑
  const needsFullRebuild = Math.random() > 0.7 // 30%概率需要重建

  if (needsFullRebuild) {
    // 显示重建确认对话框
    Modal.confirm({
      title: '索引需要重建',
      content: '检测到索引配置发生变化，需要重建索引。这可能需要较长时间，是否继续？',
      onOk() {
        performFullRebuild(record)
      },
      onCancel() {
        message.info('已取消更新操作')
      }
    })
  } else {
    // 直接执行增量更新
    performIncrementalUpdate(record)
  }
}

const performFullRebuild = (record: any) => {
  record.status = 'processing'
  record.progress = 0
  record.processedFiles = 0
  record.errorCount = 0
  record.createdAt = new Date().toISOString()
  record.completedAt = null
  message.success('索引重建已开始，正在重新处理所有文件')
}

const performIncrementalUpdate = (record: any) => {
  record.status = 'processing'
  record.progress = 0
  record.processedFiles = record.processedFiles // 保留已处理的文件数
  record.errorCount = 0
  record.createdAt = new Date().toISOString()
  record.completedAt = null
  message.success('智能更新已开始，将索引新增和修改的文件')
}

const stopIndex = (record: any) => {
  record.status = 'failed'
  record.errorMessage = '用户手动停止'
  message.info('索引任务已停止')
}

const confirmDelete = (record: any) => {
  Modal.confirm({
    title: '确定要删除这个索引吗？',
    content: `删除索引"${record.folderPath}"后，需要重新创建才能搜索该文件夹的内容。`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk() {
      deleteIndex(record)
    }
  })
}

const deleteIndex = (record: any) => {
  const index = indexList.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    indexList.value.splice(index, 1)
    message.success('索引已删除')
  }
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
}
</script>

<style scoped>
.index-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6);
}

.index-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
}

.index-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.index-header p {
  margin: var(--space-1) 0 0;
  color: var(--text-secondary);
}

.stats-cards {
  margin-bottom: var(--space-6);
}

.stats-card {
  text-align: center;
  border-radius: var(--radius-lg);
}

.index-list {
  border-radius: var(--radius-xl);
}

.progress-wrapper {
  width: 100%;
}

.progress-info {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-align: center;
  margin-top: var(--space-1);
}

.index-details {
  padding: var(--space-2) 0;
}

.error-section {
  margin-top: var(--space-6);
}

.error-section h4 {
  margin-bottom: var(--space-2);
  color: var(--error);
}

.log-section {
  margin-top: var(--space-6);
}

.log-section h4 {
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.log-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  height: 200px;
  overflow-y: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
}

.log-entry {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-1);
  align-items: flex-start;
}

.log-time {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.log-level {
  padding: 2px 6px;
  border-radius: var(--radius-base);
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.log-level.info {
  background: var(--primary-100);
  color: var(--primary-700);
}

.log-level.warn {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.log-message {
  color: var(--text-secondary);
  flex: 1;
  word-break: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .index-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .stats-cards .ant-col {
    margin-bottom: var(--space-3);
  }
}
</style>