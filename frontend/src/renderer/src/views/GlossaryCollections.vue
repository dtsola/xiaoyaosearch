<template>
  <div class="glossary-collections-page">
    <div class="glossary-header">
      <div class="header-title">
        <h2>{{ t('glossary.collections.title') }}</h2>
        <p>{{ t('glossary.collections.subtitle') }}</p>
      </div>
      <a-button type="primary" @click="showCreateModal">
        <template #icon><PlusOutlined /></template>
        {{ t('glossary.collections.create') }}
      </a-button>
    </div>

    <!-- 术语库列表 -->
    <a-card class="glossary-list" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="collections"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <!-- 名称列 -->
          <template v-if="column.key === 'name'">
            <a-space>
              <span v-if="record.icon" class="collection-icon">{{ record.icon }}</span>
              <span>{{ record.name }}</span>
              <a-tag v-if="record.is_system" color="blue">{{ $t('glossary.system') }}</a-tag>
            </a-space>
          </template>

          <!-- 描述列 -->
          <template v-else-if="column.key === 'description'">
            <a-typography-text :ellipsis="{ tooltip: record.description }">
              {{ record.description || '-' }}
            </a-typography-text>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'is_enabled'">
            <a-switch
              :checked="record.is_enabled"
              :disabled="record.is_system"
              @change="(checked) => handleToggleEnabled(record, checked)"
            />
          </template>

          <!-- 术语数量列 -->
          <template v-else-if="column.key === 'term_count'">
            <a-tag :color="record.term_count > 0 ? 'green' : 'default'">
              {{ record.term_count }}
            </a-tag>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="viewTerms(record)">
                {{ $t('glossary.viewTerms') }}
              </a-button>
              <a-button
                type="link"
                size="small"
                :disabled="record.is_system"
                @click="editCollection(record)"
              >
                {{ $t('common.edit') }}
              </a-button>
              <a-popconfirm
                :title="$t('glossary.collections.deleteConfirm')"
                :disabled="record.is_system"
                @confirm="deleteCollection(record)"
              >
                <a-button type="link" size="small" danger :disabled="record.is_system">
                  {{ $t('common.delete') }}
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 创建/编辑术语库对话框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item :label="$t('glossary.name')" name="name">
          <a-input
            v-model:value="formData.name"
            :placeholder="$t('glossary.namePlaceholder')"
            :disabled="isEditMode && currentCollection?.is_system"
          />
        </a-form-item>

        <a-form-item :label="$t('glossary.description')" name="description">
          <a-textarea
            v-model:value="formData.description"
            :placeholder="$t('glossary.descriptionPlaceholder')"
            :rows="3"
          />
        </a-form-item>

        <a-form-item :label="$t('glossary.icon')" name="icon">
          <a-input
            v-model:value="formData.icon"
            :placeholder="$t('glossary.iconPlaceholder')"
            maxlength="50"
          />
        </a-form-item>

        <a-form-item :label="$t('glossary.color')" name="color">
          <a-input
            v-model:value="formData.color"
            type="color"
            :placeholder="$t('glossary.colorPlaceholder')"
            style="width: 100px;"
          />
          <a-input
            v-model:value="formData.color"
            :placeholder="$t('glossary.colorPlaceholder')"
            style="width: 200px; margin-left: 10px;"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { GlossaryService, type GlossaryCollection, type GlossaryCollectionCreate } from '@/api/glossary'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()

// 数据
const collections = ref<GlossaryCollection[]>([])
const loading = ref(false)
const modalVisible = ref(false)
const modalLoading = ref(false)
const isEditMode = ref(false)
const currentCollection = ref<GlossaryCollection | null>(null)

// 表单
const formRef = ref()
const formData = reactive<GlossaryCollectionCreate>({
  name: '',
  description: '',
  icon: '',
  color: ''
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
    title: t('glossary.name'),
    key: 'name',
    width: 250
  },
  {
    title: t('glossary.description'),
    key: 'description',
    ellipsis: true
  },
  {
    title: t('glossary.status'),
    key: 'is_enabled',
    width: 100,
    align: 'center'
  },
  {
    title: t('glossary.termCount'),
    key: 'term_count',
    width: 100,
    align: 'center'
  },
  {
    title: t('common.actions'),
    key: 'actions',
    width: 200,
    align: 'center'
  }
])

// 表单验证规则
const formRules = computed(() => ({
  name: [
    { required: true, message: t('glossary.nameRequired'), trigger: 'blur' }
  ]
}))

const modalTitle = computed(() =>
  isEditMode.value ? t('glossary.collections.edit') : t('glossary.collections.create')
)

// 方法
const loadCollections = async () => {
  loading.value = true
  try {
    const response = await GlossaryService.getCollections(
      pagination.current,
      pagination.pageSize
    )

    if (response.success) {
      collections.value = response.data.items || []
      pagination.total = response.data.total || 0
    }
  } catch (error: any) {
    message.error(error.message || t('glossary.collections.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadCollections()
}

const showCreateModal = () => {
  isEditMode.value = false
  currentCollection.value = null
  Object.assign(formData, {
    name: '',
    description: '',
    icon: '',
    color: ''
  })
  modalVisible.value = true
}

const editCollection = (collection: GlossaryCollection) => {
  isEditMode.value = true
  currentCollection.value = collection
  Object.assign(formData, {
    name: collection.name,
    description: collection.description,
    icon: collection.icon,
    color: collection.color
  })
  modalVisible.value = true
}

const handleModalOk = async () => {
  try {
    await formRef.value.validate()

    modalLoading.value = true

    if (isEditMode.value && currentCollection.value) {
      await GlossaryService.updateCollection(currentCollection.value.id, formData)
      message.success(t('glossary.collections.updateSuccess'))
    } else {
      await GlossaryService.createCollection(formData)
      message.success(t('glossary.collections.createSuccess'))
    }

    modalVisible.value = false
    await loadCollections()
  } catch (error: any) {
    if (error.errorFields) {
      // 表单验证错误
      return
    }
    message.error(error.message || t('glossary.collections.saveFailed'))
  } finally {
    modalLoading.value = false
  }
}

const handleModalCancel = () => {
  modalVisible.value = false
  formRef.value?.resetFields()
}

const handleToggleEnabled = async (collection: GlossaryCollection, checked: boolean) => {
  try {
    await GlossaryService.updateCollection(collection.id, {
      is_enabled: checked
    })
    message.success(t('glossary.collections.statusUpdateSuccess'))
    await loadCollections()
  } catch (error: any) {
    message.error(error.message || t('glossary.collections.statusUpdateFailed'))
  }
}

const deleteCollection = async (collection: GlossaryCollection) => {
  try {
    await GlossaryService.deleteCollection(collection.id)
    message.success(t('glossary.collections.deleteSuccess'))
    await loadCollections()
  } catch (error: any) {
    message.error(error.message || t('glossary.collections.deleteFailed'))
  }
}

const viewTerms = (collection: GlossaryCollection) => {
  router.push({
    name: 'GlossaryTerms',
    params: { collectionId: collection.id },
    query: { collectionName: collection.name }
  })
}

// 生命周期
onMounted(() => {
  loadCollections()
})
</script>

<style scoped>
.glossary-collections-page {
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

.glossary-list {
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  background: var(--bg-primary);
}

.collection-icon {
  font-size: var(--text-lg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .glossary-collections-page {
    padding: var(--space-lg);
  }

  .glossary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }

  .header-title h2 {
    font-size: var(--text-xl);
  }
}
</style>
