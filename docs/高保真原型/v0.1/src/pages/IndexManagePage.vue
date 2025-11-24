<template>
  <div class="index-manage-page">
    <div class="index-container">
      <div class="index-header">
        <h1 class="index-title">索引管理</h1>
        <p class="index-description">管理和监控文件索引任务</p>
      </div>

      <div class="index-content">
        <div class="index-actions">
          <a-button type="primary" size="large" @click="showCreateModal = true">
            <SimpleIcon type="plus" />
            添加索引文件夹
          </a-button>
          <a-button size="large" @click="handleBatchOperation">
            <SimpleIcon type="menu" />
            批量操作
          </a-button>
          <a-button size="large" @click="handleExportConfig">
            <SimpleIcon type="download" />
            导出配置
          </a-button>
        </div>

        <div class="index-list">
          <a-card
            v-for="index in mockIndexes"
            :key="index.id"
            class="index-card"
            :loading="index.status === 'processing'"
          >
            <template #title>
              <div class="card-title">
                <SimpleIcon type="database" class="title-icon" />
                <span class="title-text">{{ index.folderPath }}</span>
                <a-tag :color="getStatusColor(index.status)" size="small">
                  {{ getStatusLabel(index.status) }}
                </a-tag>
              </div>
            </template>

            <div class="card-content">
              <div class="index-stats">
                <div class="stat-item">
                  <span class="stat-label">文件数量:</span>
                  <span class="stat-value">{{ index.totalFiles.toLocaleString() }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">文件大小:</span>
                  <span class="stat-value">{{ formatFileSize(index.totalSize) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">更新时间:</span>
                  <span class="stat-value">{{ formatTime(index.updatedAt) }}</span>
                </div>
              </div>

              <div v-if="index.status === 'processing'" class="progress-section">
                <div class="progress-info">
                  <span>处理进度: {{ index.processedFiles }} / {{ index.totalFiles }}</span>
                  <span>{{ Math.round((index.processedFiles / index.totalFiles) * 100) }}%</span>
                </div>
                <a-progress
                  :percent="Math.round((index.processedFiles / index.totalFiles) * 100)"
                  :stroke-color="getProgressColor()"
                />
                <div class="current-file" v-if="index.currentFile">
                  当前: {{ index.currentFile }}
                </div>
              </div>

              <div class="card-actions">
                <a-button
                  v-if="index.status === 'completed'"
                  type="primary"
                  ghost
                  size="small"
                  @click="handleReindex(index)"
                >
                  <SimpleIcon type="refresh" />
                  重新索引
                </a-button>
                <a-button
                  v-if="index.status === 'processing'"
                  type="default"
                  size="small"
                  @click="handlePause(index)"
                >
                  <SimpleIcon type="pause" />
                  暂停
                </a-button>
                <a-button
                  type="default"
                  size="small"
                  @click="handleViewDetails(index)"
                >
                  <SimpleIcon type="preview" />
                  查看详情
                </a-button>
                <a-button
                  type="default"
                  size="small"
                  @click="handleDelete(index)"
                  danger
                >
                  <SimpleIcon type="delete" />
                  删除
                </a-button>
              </div>
            </div>
          </a-card>
        </div>
      </div>
    </div>

    <!-- 创建索引模态框 -->
    <a-modal
      v-model:open="showCreateModal"
      title="添加索引文件夹"
      width="600px"
      @ok="handleCreateIndex"
    >
      <a-form layout="vertical">
        <a-form-item label="文件夹路径" required>
          <a-input v-model:value="newIndex.folderPath" placeholder="选择或输入文件夹路径" />
          <a-button type="link" @click="handleSelectFolder">
            <SimpleIcon type="open" />
            浏览文件夹
          </a-button>
        </a-form-item>
        <a-form-item label="文件类型">
          <a-checkbox-group v-model:value="newIndex.fileTypes">
            <a-checkbox value="pdf">PDF文档</a-checkbox>
            <a-checkbox value="docx">Word文档</a-checkbox>
            <a-checkbox value="xlsx">Excel表格</a-checkbox>
            <a-checkbox value="txt">文本文件</a-checkbox>
            <a-checkbox value="md">Markdown</a-checkbox>
            <a-checkbox value="mp3">音频文件</a-checkbox>
            <a-checkbox value="mp4">视频文件</a-checkbox>
            <a-checkbox value="jpg">图片文件</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
        <a-form-item>
          <a-checkbox v-model:checked="newIndex.recursive">
            包含子文件夹
          </a-checkbox>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'
import SimpleIcon from '@/components/SimpleIcon.vue'

// 模态框状态
const showCreateModal = ref(false)

// 新建索引
const newIndex = reactive({
  folderPath: '',
  fileTypes: ['pdf', 'docx', 'txt', 'md'],
  recursive: true
})

// 模拟索引数据
const mockIndexes = ref([
  {
    id: 1,
    folderPath: 'D:\\Work\\Documents',
    status: 'completed',
    totalFiles: 1234,
    processedFiles: 1234,
    totalSize: 2.3 * 1024 * 1024 * 1024, // 2.3GB
    updatedAt: '2024-11-20T10:30:00Z'
  },
  {
    id: 2,
    folderPath: 'C:\\Users\\Downloads',
    status: 'processing',
    totalFiles: 567,
    processedFiles: 234,
    totalSize: 1.8 * 1024 * 1024 * 1024, // 1.8GB
    currentFile: 'report_final.pdf',
    updatedAt: '2024-11-20T14:20:00Z'
  },
  {
    id: 3,
    folderPath: 'D:\\Study\\Materials',
    status: 'completed',
    totalFiles: 2890,
    processedFiles: 2890,
    totalSize: 5.6 * 1024 * 1024 * 1024, // 5.6GB
    updatedAt: '2024-11-18T09:15:00Z'
  }
])

// 获取状态颜色
const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    completed: 'success',
    processing: 'processing',
    failed: 'error',
    paused: 'warning'
  }
  return colorMap[status] || 'default'
}

// 获取状态标签
const getStatusLabel = (status: string): string => {
  const labelMap: Record<string, string> = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
    paused: '已暂停'
  }
  return labelMap[status] || status
}

// 获取进度条颜色
const getProgressColor = (): string => {
  return {
    '0%': '#00E5FF',
    '100%': '#4A148C'
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(1)}${units[unitIndex]}`
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 事件处理
const handleBatchOperation = () => {
  message.info('批量操作功能开发中')
}

const handleExportConfig = () => {
  message.info('导出配置功能开发中')
}

const handleCreateIndex = () => {
  if (!newIndex.folderPath.trim()) {
    message.warning('请输入文件夹路径')
    return
  }

  // 创建索引逻辑
  mockIndexes.value.push({
    id: Date.now(),
    folderPath: newIndex.folderPath,
    status: 'processing',
    totalFiles: 0,
    processedFiles: 0,
    totalSize: 0,
    updatedAt: new Date().toISOString()
  })

  showCreateModal.value = false
  message.success('索引任务已创建')

  // 重置表单
  newIndex.folderPath = ''
  newIndex.fileTypes = ['pdf', 'docx', 'txt', 'md']
  newIndex.recursive = true
}

const handleSelectFolder = () => {
  message.info('文件夹选择功能开发中')
}

const handleReindex = (index: any) => {
  index.status = 'processing'
  index.processedFiles = 0
  message.info(`正在重新索引: ${index.folderPath}`)
}

const handlePause = (index: any) => {
  index.status = 'paused'
  message.info('索引任务已暂停')
}

const handleViewDetails = (index: any) => {
  message.info(`查看索引详情: ${index.folderPath}`)
}

const handleDelete = (index: any) => {
  const indexIndex = mockIndexes.value.findIndex(item => item.id === index.id)
  if (indexIndex > -1) {
    mockIndexes.value.splice(indexIndex, 1)
    message.success('索引已删除')
  }
}
</script>

<style lang="scss" scoped>
.index-manage-page {
  min-height: 100vh;
  padding: var(--space-6);
  background: var(--surface-primary);
}

.index-container {
  max-width: 1200px;
  margin: 0 auto;
}

.index-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.index-title {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-3);
  font-family: var(--font-display);
}

.index-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.index-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.index-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.index-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-6);
}

.index-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
  transition: all 0.3s var(--ease-out-cubic);

  @include glass-morphism;

  &:hover {
    transform: translateY(-4px);
    border-color: rgba(0, 229, 255, 0.3);
    box-shadow: 0 12px 40px rgba(0, 229, 255, 0.2);
  }

  :deep(.ant-card-head) {
    background: rgba(37, 43, 78, 0.6);
    border-bottom: 1px solid var(--border-light);
  }

  :deep(.ant-card-head-title) {
    width: 100%;
  }

  :deep(.ant-card-body) {
    padding: var(--space-5);
  }
}

.card-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
}

.title-icon {
  color: var(--accent-cyan);
  font-size: 16px;
}

.title-text {
  flex: 1;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.index-stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.stat-value {
  color: var(--text-primary);
  font-weight: 500;
  font-family: var(--font-mono);
}

.progress-section {
  padding: var(--space-3);
  background: rgba(0, 229, 255, 0.05);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: var(--radius-lg);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.current-file {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  justify-content: flex-end;
}

// 响应式设计
@media (max-width: 768px) {
  .index-manage-page {
    padding: var(--space-4);
  }

  .index-actions {
    flex-direction: column;
    align-items: stretch;

    .ant-btn {
      width: 100%;
    }
  }

  .index-list {
    grid-template-columns: 1fr;
  }

  .card-title {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-1);
  }

  .title-text {
    white-space: normal;
    line-height: 1.4;
  }
}

@media (max-width: 480px) {
  .card-actions {
    justify-content: center;
  }
}
</style>