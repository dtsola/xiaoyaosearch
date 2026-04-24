<template>
  <div class="glossary-terms-page">
    <div class="glossary-header">
      <div class="header-left">
        <a-button type="text" @click="handleBack" class="back-button">
          <template #icon><ArrowLeftOutlined /></template>
        </a-button>
        <div class="header-title">
          <h2>{{ t('glossary.terms.title') }}</h2>
          <p>{{ collectionName }}</p>
        </div>
      </div>
      <a-space>
        <a-button @click="showImportModal">
          <template #icon><ImportOutlined /></template>
          {{ t('glossary.import') }}
        </a-button>
        <a-button @click="exportToCSV">
          <template #icon><ExportOutlined /></template>
          {{ t('glossary.export') }}
        </a-button>
        <a-button type="primary" @click="showCreateModal">
          <template #icon><PlusOutlined /></template>
          {{ t('glossary.terms.create') }}
        </a-button>
      </a-space>
    </div>

    <!-- 术语列表 -->
    <a-card class="terms-list" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="terms"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <!-- 术语列 -->
          <template v-if="column.key === 'term'">
            <a-space direction="vertical" :size="0">
              <span class="term-name">{{ record.term }}</span>
              <a-typography-text type="secondary" :ellipsis="{ tooltip: record.description }">
                {{ record.description || '-' }}
              </a-typography-text>
            </a-space>
          </template>

          <!-- 同义词列 -->
          <template v-else-if="column.key === 'synonyms'">
            <a-space wrap>
              <a-tag v-for="(synonym, index) in record.synonyms.slice(0, 3)" :key="index">
                {{ synonym }}
              </a-tag>
              <a-tag v-if="record.synonyms.length > 3">
                +{{ record.synonyms.length - 3 }}
              </a-tag>
            </a-space>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'is_enabled'">
            <a-switch
              :checked="record.is_enabled"
              @change="(checked) => handleToggleEnabled(record, checked)"
            />
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="editTerm(record)">
                {{ $t('common.edit') }}
              </a-button>
              <a-popconfirm
                :title="$t('glossary.terms.deleteConfirm')"
                @confirm="deleteTerm(record)"
              >
                <a-button type="link" size="small" danger>
                  {{ $t('common.delete') }}
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 创建/编辑术语对话框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      width="600px"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-form-item name="term">
          <template #label>
            {{ $t('glossary.term') }} <span class="required-mark">*</span>
          </template>
          <a-input
            v-model:value="formData.term"
            :placeholder="$t('glossary.termPlaceholder')"
          />
        </a-form-item>

        <a-form-item name="synonyms">
          <template #label>
            {{ $t('glossary.synonyms') }} <span class="required-mark">*</span>
          </template>
          <a-select
            v-model:value="formData.synonyms"
            mode="tags"
            :placeholder="$t('glossary.synonymsPlaceholder')"
            :options="synonymOptions"
          />
        </a-form-item>

        <a-form-item :label="$t('glossary.description')" name="description">
          <a-textarea
            v-model:value="formData.description"
            :placeholder="$t('glossary.descriptionPlaceholder')"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- CSV导入对话框 -->
    <a-modal
      v-model:open="importModalVisible"
      :title="$t('glossary.importTitle')"
      @ok="handleImport"
      @cancel="handleImportCancel"
      :ok-button-props="{ disabled: !uploadFile }"
    >
      <a-upload-dragger
        :before-upload="beforeUpload"
        :show-upload-list="false"
        accept=".csv"
      >
        <p class="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p class="ant-upload-text">{{ $t('glossary.uploadText') }}</p>
        <p class="ant-upload-hint">
          {{ $t('glossary.uploadHint') }}
        </p>
      </a-upload-dragger>

      <!-- 已选择的文件 -->
      <div v-if="uploadFile" class="selected-file">
        <a-tag color="blue" closable @close="clearSelectedFile">
          <FileOutlined />
          {{ uploadFile.name }}
        </a-tag>
      </div>

      <div class="template-download">
        <span class="template-hint">{{ t('glossary.noTemplate') }}</span>
        <a-button type="link" @click="downloadTemplate">
          <DownloadOutlined />
          {{ t('glossary.downloadTemplate') }}
        </a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  ImportOutlined,
  ExportOutlined,
  InboxOutlined,
  ArrowLeftOutlined,
  DownloadOutlined,
  FileOutlined
} from '@ant-design/icons-vue'
import { GlossaryService, type GlossaryTerm, type GlossaryTermCreate } from '@/api/glossary'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()

const collectionId = computed(() => parseInt(route.params.collectionId as string))
const collectionName = computed(() => (route.query.collectionName as string) || '')

// 数据
const terms = ref<GlossaryTerm[]>([])
const loading = ref(false)
const modalVisible = ref(false)
const importModalVisible = ref(false)
const modalLoading = ref(false)
const isEditMode = ref(false)
const currentTerm = ref<GlossaryTerm | null>(null)
const uploadFile = ref<File | null>(null)

// 表单
const formRef = ref()
const formData = reactive<GlossaryTermCreate>({
  term: '',
  synonyms: [],
  description: ''
})

// 同义词选项
const synonymOptions = computed(() => {
  return formData.synonyms.map(s => ({ label: s, value: s }))
})

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => t('glossary.total', { total })
})

// 表格列
const columns = computed(() => [
  {
    title: t('glossary.term'),
    key: 'term',
    width: 300
  },
  {
    title: t('glossary.synonyms'),
    key: 'synonyms',
    ellipsis: true
  },
  {
    title: t('glossary.status'),
    key: 'is_enabled',
    width: 100,
    align: 'center'
  },
  {
    title: t('common.actions'),
    key: 'actions',
    width: 150,
    align: 'center'
  }
])

// 表单验证规则
const formRules = computed(() => ({
  term: [
    { required: true, message: t('glossary.termRequired'), trigger: 'blur' }
  ],
  synonyms: [
    { required: true, message: t('glossary.synonymsRequired'), trigger: 'change' }
  ]
}))

const modalTitle = computed(() =>
  isEditMode.value ? t('glossary.terms.edit') : t('glossary.terms.create')
)

// 方法
const loadTerms = async () => {
  loading.value = true
  try {
    const response = await GlossaryService.getTerms(
      collectionId.value,
      pagination.current,
      pagination.pageSize
    )

    if (response.success) {
      terms.value = response.data.items || []
      pagination.total = response.data.total || 0
    }
  } catch (error: any) {
    message.error(error.message || t('glossary.terms.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadTerms()
}

const showCreateModal = () => {
  isEditMode.value = false
  currentTerm.value = null
  Object.assign(formData, {
    term: '',
    synonyms: [],
    description: ''
  })
  modalVisible.value = true
}

const editTerm = (term: GlossaryTerm) => {
  isEditMode.value = true
  currentTerm.value = term
  Object.assign(formData, {
    term: term.term,
    synonyms: term.synonyms,
    description: term.description
  })
  modalVisible.value = true
}

const handleModalOk = async () => {
  try {
    await formRef.value.validate()

    modalLoading.value = true

    if (isEditMode.value && currentTerm.value) {
      await GlossaryService.updateTerm(collectionId.value, currentTerm.value.id, formData)
      message.success(t('glossary.terms.updateSuccess'))
    } else {
      await GlossaryService.createTerm(collectionId.value, formData)
      message.success(t('glossary.terms.createSuccess'))
    }

    modalVisible.value = false
    await loadTerms()
  } catch (error: any) {
    if (error.errorFields) {
      return
    }
    message.error(error.message || t('glossary.terms.saveFailed'))
  } finally {
    modalLoading.value = false
  }
}

const handleModalCancel = () => {
  modalVisible.value = false
  formRef.value?.resetFields()
}

const handleToggleEnabled = async (term: GlossaryTerm, checked: boolean) => {
  try {
    await GlossaryService.updateTerm(collectionId.value, term.id, {
      is_enabled: checked
    })
    message.success(t('glossary.terms.statusUpdateSuccess'))
    await loadTerms()
  } catch (error: any) {
    message.error(error.message || t('glossary.terms.statusUpdateFailed'))
  }
}

const deleteTerm = async (term: GlossaryTerm) => {
  try {
    await GlossaryService.deleteTerm(collectionId.value, term.id)
    message.success(t('glossary.terms.deleteSuccess'))
    await loadTerms()
  } catch (error: any) {
    message.error(error.message || t('glossary.terms.deleteFailed'))
  }
}

const showImportModal = () => {
  importModalVisible.value = true
}

const beforeUpload = (file: File) => {
  uploadFile.value = file
  return false // 阻止自动上传
}

const clearSelectedFile = () => {
  uploadFile.value = null
}

const handleImportCancel = () => {
  importModalVisible.value = false
  clearSelectedFile()
}

const handleImport = async () => {
  if (!uploadFile.value) {
    message.warning(t('glossary.selectFile'))
    return
  }

  try {
    const response = await GlossaryService.importFromCSV(collectionId.value, uploadFile.value)

    if (response.data.failed_count > 0) {
      message.warning(
        t('glossary.importPartialSuccess', {
          imported: response.data.imported_count,
          failed: response.data.failed_count
        })
      )
    } else {
      message.success(
        t('glossary.importSuccess', { count: response.data.imported_count })
      )
    }

    importModalVisible.value = false
    clearSelectedFile()
    await loadTerms()
  } catch (error: any) {
    message.error(error.message || t('glossary.importFailed'))
  }
}

const exportToCSV = async () => {
  try {
    await GlossaryService.exportToCSV(collectionId.value, locale.value)
    message.success(t('glossary.exportSuccess'))
  } catch (error: any) {
    message.error(error.message || t('glossary.exportFailed'))
  }
}

const downloadTemplate = () => {
  // 根据当前语言生成不同的模板内容
  const isZhCN = locale.value === 'zh-CN'

  const templateContent = isZhCN ? [
    'term,synonyms,description',
    'API,应用程序接口;接口,应用程序编程接口',
    'PRD,产品需求文档;需求文档,产品需求文档',
    'SQL,结构化查询语言;查询语言,结构化查询语言'
  ] : [
    'term,synonyms,description',
    'API,application programming interface;interface,application programming interface',
    'PRD,product requirements document;requirements document,product requirements document',
    'SQL,structured query language;query language,structured query language'
  ]

  const csvContent = templateContent.join('\n')

  // 创建Blob对象
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })

  // 创建下载链接
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'glossary_template.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  message.success(t('glossary.templateDownloadSuccess'))
}

const handleBack = () => {
  router.push({ name: 'GlossaryCollections' })
}

// 生命周期
onMounted(() => {
  loadTerms()
})
</script>

<style scoped>
.glossary-terms-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-xl);
}

.glossary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3xl);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.back-button {
  padding: var(--space-xs);
  height: auto;
}

.header-title h2 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-2xl);
  letter-spacing: -0.25px;
  color: var(--text-primary);
  margin: 0 0 var(--space-xs);
}

.header-title p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

.terms-list {
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  background: var(--bg-primary);
}

.term-name {
  font-weight: 600;
  color: var(--text-primary);
}

.selected-file {
  margin-top: var(--space-lg);
  padding: var(--space-md);
  background: var(--bg-secondary);
  border: var(--border-standard);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.template-download {
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: var(--border-standard);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.template-hint {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* 模态框样式 */
:deep(.ant-modal-content) {
  border-radius: var(--radius-xl);
  border: var(--border-standard);
  box-shadow: var(--shadow-elevated);
  background: var(--bg-primary);
}

:deep(.ant-modal-header) {
  border-bottom: var(--border-standard);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  padding: var(--space-lg) var(--space-xl);
  background: var(--bg-secondary);
}

:deep(.ant-modal-title) {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-lg);
  color: var(--text-primary);
}

:deep(.ant-modal-body) {
  padding: var(--space-xl);
  color: var(--text-primary);
}

:deep(.ant-modal-footer) {
  border-top: var(--border-standard);
  padding: var(--space-md) var(--space-xl);
  background: var(--bg-secondary);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

:deep(.ant-form-item) {
  margin-bottom: var(--space-lg);
}

:deep(.ant-form-item-label > label) {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

/* 隐藏 Ant Design 默认的必填标记 */
:deep(.ant-form-item-required::before) {
  display: none !important;
}

/* 必填标记红色 */
.required-mark {
  color: #ff4d4f;
  margin-left: 4px;
}

:deep(.ant-input),
:deep(.ant-textarea) {
  border-radius: var(--radius-sm);
  border: var(--border-standard);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

:deep(.ant-input::placeholder),
:deep(.ant-textarea::placeholder) {
  color: var(--text-tertiary);
}

:deep(.ant-input:focus),
:deep(.ant-input-focused),
:deep(.ant-textarea:focus),
:deep(.ant-textarea-focused) {
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 2px rgba(0, 117, 222, 0.1);
}

:deep(.ant-select-selector) {
  border-radius: var(--radius-sm) !important;
  border: var(--border-standard) !important;
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  font-size: var(--text-sm) !important;
}

:deep(.ant-select-focused .ant-select-selector) {
  border-color: var(--brand-blue) !important;
  box-shadow: 0 0 0 2px rgba(0, 117, 222, 0.1) !important;
}

:deep(.ant-select-dropdown) {
  border-radius: var(--radius-lg);
  border: var(--border-standard);
  box-shadow: var(--shadow-elevated);
  background: var(--bg-primary);
}

:deep(.ant-select-item) {
  color: var(--text-primary);
  font-size: var(--text-sm);
}

:deep(.ant-select-item-option-selected) {
  background: var(--bg-secondary);
  color: var(--brand-blue);
}

:deep(.ant-upload-dragger) {
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border-standard);
  background: var(--bg-secondary);
  padding: var(--space-3xl);
}

:deep(.ant-upload-dragger:hover) {
  border-color: var(--brand-blue);
}

:deep(.ant-upload-drag-icon) {
  color: var(--brand-blue);
  font-size: 48px;
}

:deep(.ant-btn-link) {
  color: var(--brand-blue);
  font-weight: 500;
}

:deep(.ant-btn-link:hover) {
  color: #0056b3;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .glossary-terms-page {
    padding: var(--space-lg);
  }

  .glossary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }

  .header-left {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }

  .header-title h2 {
    font-size: var(--text-xl);
  }

  .template-download {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
}
</style>
