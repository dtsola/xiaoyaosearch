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
              :value="formattedIndexSize.value"
              :precision="2"
              :suffix="formattedIndexSize.unit"
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
        :loading="loading"
        row-key="index_id"
        @change="handleTableChange"
      >
        <!-- 文件夹路径列 -->
        <template #folder_path="{ record }">
          <a-tooltip :title="record.folder_path" placement="topLeft">
            <span>{{ record.folder_path }}</span>
          </a-tooltip>
        </template>

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
              {{ record.processed_files || 0 }} / {{ record.total_files || 0 }}
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
            <a-checkbox value="image">图片 (png, jpg, jpeg)</a-checkbox>
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
            {{ selectedIndex.folder_path }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(selectedIndex.status)">
              {{ getStatusLabel(selectedIndex.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="总文件数">
            {{ selectedIndex.total_files || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="已处理文件">
            {{ selectedIndex.processed_files || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="错误数量">
            {{ selectedIndex.error_count || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ selectedIndex.started_at ? formatDate(selectedIndex.started_at) : '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="完成时间">
            {{ selectedIndex.completed_at ? formatDate(selectedIndex.completed_at) : '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="处理时间">
            {{ selectedIndex.completed_at && selectedIndex.started_at ? calculateDuration(selectedIndex.started_at, selectedIndex.completed_at) : '-' }}
          </a-descriptions-item>
        </a-descriptions>

        <!-- 错误信息 -->
        <div v-if="selectedIndex.error_message" class="error-section">
          <h4>错误信息</h4>
          <a-alert
            :message="selectedIndex.error_message"
            type="error"
            show-icon
          />
        </div>

              </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  SyncOutlined,
  DownOutlined,
  EyeOutlined,
  StopOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { IndexService } from '@/api/index'
import { getIndexStatusInfo, formatIndexSize } from '@/utils/indexUtils'

// 存储 electronAPI 引用，避免生命周期问题
let electronAPI: any = null

// 在组件挂载时保存 API 引用
onMounted(() => {
  electronAPI = (window as any).api
})

// 响应式数据
const showAddFolderModal = ref(false)
const showDetailsModal = ref(false)
const selectedIndex = ref(null)

// 统计数据 - 从API加载
const stats = reactive({
  totalFiles: 0,
  indexSize: 0,
  indexSizeBytes: 0, // 添加原始字节数
  activeTasks: 0,
  successRate: 0
})

// 计算属性：格式化的索引大小
const formattedIndexSize = computed(() => {
  if (stats.indexSizeBytes) {
    return formatIndexSize(stats.indexSizeBytes)
  }
  return { value: 0, unit: 'B' }
})

// 新建文件夹配置
const newFolder = reactive({
  path: '',
  fileTypes: ['document', 'audio', 'video', 'image']
})

// 索引列表 - 从API加载
const indexList = ref([])
const loading = ref(false)


// 表格配置
const indexColumns = [
  {
    title: '文件夹路径',
    dataIndex: 'folder_path',
    key: 'folder_path',
    ellipsis: true,
    slots: { customRender: 'folder_path' }
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
    dataIndex: 'total_files',
    key: 'total_files'
  },
  {
    title: '错误数',
    dataIndex: 'error_count',
    key: 'error_count'
  },
  {
    title: '创建时间',
    dataIndex: 'started_at',
    key: 'started_at',
    customRender: ({ text }) => text ? formatDate(text) : '-'
  },
  {
    title: '操作',
    key: 'action',
    slots: { customRender: 'action' }
  }
]

const pagination = reactive({
  current: 1,
  pageSize: 5,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  pageSizeOptions: ['5', '10', '20', '50'],
  showTotal: (total: number, range: [number, number]) =>
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
})

// 方法
const getStatusColor = (status: string) => {
  const statusInfo = getIndexStatusInfo(status)
  return statusInfo.antdColor
}

const getStatusLabel = (status: string) => {
  const statusInfo = getIndexStatusInfo(status)
  return statusInfo.label
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

// 数据加载方法
const loadSystemStatus = async () => {
  try {
    const response = await IndexService.getSystemStatus()
    if (response.success) {
      Object.assign(stats, response.data)
    }
  } catch (error) {
    console.error('加载系统状态失败:', error)
  }
}

const loadIndexList = async () => {
  try {
    loading.value = true
    // 计算偏移量
    const offset = (pagination.current - 1) * pagination.pageSize
    const response = await IndexService.getIndexList(undefined, pagination.pageSize, offset)
    if (response.success) {
      // 适配数据格式：后端返回的是 { indexes: [], total: x }
      indexList.value = response.data.indexes || []
      // 更新总数
      pagination.total = response.data.total || 0
    }
  } catch (error) {
    console.error('加载索引列表失败:', error)
    message.error('加载索引列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([
    loadSystemStatus(),
    loadIndexList()
  ])
}

const browseFolder = async () => {
  try {
    // 优先使用存储的API引用，避免生命周期问题
    const api = electronAPI || (window as any).api

    // 检查是否在 Electron 环境中
    if (!api || typeof api.selectFolder !== 'function') {
      message.warning('请在桌面应用中使用文件夹选择功能')
      // 降级到默认路径
      newFolder.path = 'D:\\Work\\Documents'
      return
    }

    // 调用 Electron 文件夹选择对话框
    const result = await api.selectFolder()

    if (result.success && result.folderPath) {
      newFolder.path = result.folderPath
      message.success(`已选择文件夹: ${result.folderPath}`)
    } else if (result.canceled) {
      // 用户取消选择，不显示错误信息
      console.log('用户取消了文件夹选择')
    } else {
      message.error(result.error || '选择文件夹失败')
    }
  } catch (error) {
    console.error('调用文件夹选择失败:', error)
    message.error('文件夹选择功能不可用')
    // 降级到默认路径
    newFolder.path = 'D:\\Work\\Documents'
  }
}

const handleAddFolder = async () => {
  if (!newFolder.path) {
    message.error('请选择文件夹路径')
    return
  }

  try {
    const response = await IndexService.createIndex({
      folder_path: newFolder.path,
      file_types: newFolder.fileTypes,
      recursive: true
    })

    if (response.success) {
      showAddFolderModal.value = false
      message.success('索引任务已创建')

      // 刷新系统状态和索引列表
      await refreshData()

      // 重置表单
      newFolder.path = ''
      newFolder.fileTypes = ['document', 'audio', 'video', 'image']
    } else {
      message.error(response.message || '创建索引失败')
    }
  } catch (error) {
    console.error('创建索引失败:', error)
    message.error('创建索引失败，请重试')
  }
}

const viewIndexDetails = (record: any) => {
  selectedIndex.value = record
  showDetailsModal.value = true
}

const smartUpdate = async (record: any) => {
  try {
    const response = await IndexService.updateIndex({
      folder_path: record.folder_path,
      file_types: ['document', 'audio', 'video', 'image'], // 默认所有类型
      recursive: true
    })

    if (response.success) {
      message.success('索引更新任务已创建')
      await refreshData() // 刷新系统状态和索引列表
    } else {
      message.error(response.message || '更新索引失败')
    }
  } catch (error) {
    console.error('更新索引失败:', error)
    message.error('更新索引失败，请重试')
  }
}

const stopIndex = async (record: any) => {
  try {
    const response = await IndexService.stopIndex(record.index_id || record.id)

    if (response.success) {
      message.success('索引任务已停止')
      await refreshData() // 刷新系统状态和索引列表
    } else {
      message.error(response.message || '停止索引失败')
    }
  } catch (error) {
    console.error('停止索引失败:', error)
    message.error('停止索引失败，请重试')
  }
}

const confirmDelete = (record: any) => {
  Modal.confirm({
    title: '确定要删除这个索引吗？',
    content: `删除索引"${record.folder_path}"后，需要重新创建才能搜索该文件夹的内容。`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk() {
      deleteIndex(record)
    }
  })
}

const deleteIndex = async (record: any) => {
  try {
    const response = await IndexService.deleteIndex(record.index_id || record.id)

    if (response.success) {
      message.success('索引已删除')
      await refreshData() // 刷新系统状态和索引列表

      // 如果删除后当前页没有数据了，返回第一页
      if (pagination.current > 1 && indexList.value.length === 0) {
        pagination.current = 1
        await loadIndexList()
      }
    } else {
      message.error(response.message || '删除索引失败')
    }
  } catch (error) {
    console.error('删除索引失败:', error)
    message.error('删除索引失败，请重试')
  }
}

const handleTableChange = async (pag: any) => {
  // 检查页面大小是否发生变化
  const pageSizeChanged = pagination.pageSize !== pag.pageSize

  // 更新分页参数
  pagination.current = pageSizeChanged ? 1 : pag.current // 如果页面大小改变，重置到第一页
  pagination.pageSize = pag.pageSize

  await loadIndexList()
}

// 组件挂载时加载数据
onMounted(() => {
  refreshData()

  // 设置15秒自动刷新
  const refreshInterval = setInterval(() => {
    refreshData()
  }, 15000) // 15秒 = 15000毫秒

  // 组件卸载时清理定时器
  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
})
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