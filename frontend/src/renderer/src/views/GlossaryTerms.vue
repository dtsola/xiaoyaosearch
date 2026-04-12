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
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 19 }"
      >
        <a-form-item :label="$t('glossary.term')" name="term">
          <a-input
            v-model:value="formData.term"
            :placeholder="$t('glossary.termPlaceholder')"
          />
        </a-form-item>

        <a-form-item :label="$t('glossary.synonyms')" name="synonyms">
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
      @cancel="importModalVisible = false"
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
  DownloadOutlined
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
    'API,应用程序接口|接口,应用程序编程接口',
    'PRD,产品需求文档|需求文档,产品需求文档',
    'SQL,结构化查询语言|查询语言,结构化查询语言'
  ] : [
    'term,synonyms,description',
    'API,application programming interface|interface,application programming interface',
    'PRD,product requirements document|requirements document,product requirements document',
    'SQL,structured query language|query language,structured query language'
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
  padding: var(--space-6);
}

.glossary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.back-button {
  padding: var(--space-2);
  height: auto;
}

.header-title h2 {
  margin: 0;
  color: var(--text-primary);
}

.header-title p {
  margin: var(--space-1) 0 0;
  color: var(--text-secondary);
}

.terms-list {
  border-radius: var(--radius-xl);
}

.term-name {
  font-weight: 500;
}

.template-download {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.template-hint {
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>
