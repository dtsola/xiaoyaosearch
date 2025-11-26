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
                  @click="rebuildIndex(record)"
                >
                  <RedoOutlined />
                  重建
                </a-menu-item>
                <a-menu-item
                  v-if="record.status === 'processing'"
                  @click="pauseIndex(record)"
                >
                  <PauseOutlined />
                  暂停
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="deleteIndex(record)" class="danger-item">
                  <DeleteOutlined />
                  删除
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </template>
      </a-table>
    </a-card>

    <!-- 添加文件夹模态框 -->
    <a-modal
      v-model:open="showAddFolderModal"
      title="添加文件夹到索引"
      @ok="handleAddFolder"
      :confirm-loading="isAdding"
    >
      <a-form layout="vertical">
        <a-form-item label="文件夹路径" required>
          <a-input
            v-model:value="newFolder.path"
            placeholder="请输入文件夹路径，如：D:\Documents"
          />
        </a-form-item>
        <a-form-item label="递归索引">
          <a-switch v-model:checked="newFolder.recursive" />
          <div class="form-help">是否包含子文件夹</div>
        </a-form-item>
        <a-form-item label="文件类型">
          <a-checkbox-group v-model:value="newFolder.fileTypes">
            <a-checkbox value="document">文档文件</a-checkbox>
            <a-checkbox value="audio">音频文件</a-checkbox>
            <a-checkbox value="video">视频文件</a-checkbox>
            <a-checkbox value="image">图片文件</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  SyncOutlined,
  EyeOutlined,
  RedoOutlined,
  PauseOutlined,
  DeleteOutlined,
  DownOutlined
} from '@ant-design/icons-vue'

// 响应式数据
const showAddFolderModal = ref(false)
const isAdding = ref(false)

// 统计数据
const stats = reactive({
  totalFiles: 12345,
  indexSize: 8.7,
  activeTasks: 2,
  successRate: 98.5
})

// 新建文件夹
const newFolder = reactive({
  path: '',
  recursive: true,
  fileTypes: ['document', 'audio', 'video', 'image']
})

// 索引列表
const indexList = ref([
  {
    id: 1,
    folderPath: 'D:\\Documents',
    status: 'completed',
    progress: 100,
    totalFiles: 5432,
    processedFiles: 5432,
    fileTypes: ['document', 'image'],
    createdAt: '2024-01-15 10:30:00',
    updatedAt: '2024-01-15 11:45:00'
  },
  {
    id: 2,
    folderPath: 'D:\\Downloads',
    status: 'processing',
    progress: 67,
    totalFiles: 2100,
    processedFiles: 1407,
    fileTypes: ['document', 'audio', 'video'],
    createdAt: '2024-01-16 09:15:00',
    updatedAt: '2024-01-16 10:20:00'
  },
  {
    id: 3,
    folderPath: 'D:\\Projects',
    status: 'pending',
    progress: 0,
    totalFiles: 0,
    processedFiles: 0,
    fileTypes: ['document'],
    createdAt: '2024-01-16 11:00:00',
    updatedAt: '2024-01-16 11:00:00'
  }
])

// 表格列定义
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
    slots: { customRender: 'progress' },
    width: 200
  },
  {
    title: '文件数量',
    dataIndex: 'totalFiles',
    key: 'totalFiles'
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt'
  },
  {
    title: '操作',
    key: 'action',
    slots: { customRender: 'action' },
    width: 100
  }
]

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 3,
  showTotal: (total: number) => `共 ${total} 条记录`,
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

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
}

const viewIndexDetails = (record: any) => {
  message.info(`查看索引详情: ${record.folderPath}`)
}

const rebuildIndex = (record: any) => {
  message.info(`重建索引: ${record.folderPath}`)
}

const pauseIndex = (record: any) => {
  message.info(`暂停索引: ${record.folderPath}`)
}

const deleteIndex = (record: any) => {
  message.warning(`删除索引: ${record.folderPath}`)
}

const handleAddFolder = async () => {
  if (!newFolder.path.trim()) {
    message.error('请输入文件夹路径')
    return
  }

  isAdding.value = true
  try {
    // 模拟添加API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 添加到列表
    const newIndex = {
      id: indexList.value.length + 1,
      folderPath: newFolder.path,
      status: 'pending',
      progress: 0,
      totalFiles: 0,
      processedFiles: 0,
      fileTypes: newFolder.fileTypes,
      createdAt: new Date().toLocaleString(),
      updatedAt: new Date().toLocaleString()
    }

    indexList.value.unshift(newIndex)

    // 重置表单
    newFolder.path = ''
    newFolder.recursive = true
    newFolder.fileTypes = ['document', 'audio', 'video', 'image']

    showAddFolderModal.value = false
    message.success('文件夹已添加到索引队列')
  } catch (error) {
    message.error('添加失败，请重试')
  } finally {
    isAdding.value = false
  }
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
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.index-header p {
  color: var(--text-secondary);
  margin: 0;
}

.stats-cards {
  margin-bottom: var(--space-6);
}

.stats-card {
  text-align: center;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
}

.index-list {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-base);
}

.progress-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.progress-info {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-align: center;
}

.form-help {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

.danger-item {
  color: var(--error);
}

.danger-item:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .index-container {
    padding: var(--space-4);
  }

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