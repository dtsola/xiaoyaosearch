<template>
  <div class="glossary-settings">
    <div class="settings-section">
      <h3>{{ t('glossary.settings.title') }}</h3>
      <a-form layout="vertical">
        <!-- 启用术语扩展 -->
        <a-form-item :label="t('glossary.settings.enableExpansion')">
          <a-switch
            v-model:checked="config.enable"
            @change="handleEnableChange"
          />
          <div class="form-help">
            {{ t('glossary.settings.enableExpansionHint') }}
          </div>
        </a-form-item>

        <!-- 扩展词数量 -->
        <a-form-item :label="t('glossary.settings.maxExpansionTerms')">
          <a-input-number
            v-model:value="config.max_expansion_terms"
            :min="1"
            :max="20"
            :disabled="!config.enable"
            style="width: 100%"
          />
          <div class="form-help">
            {{ t('glossary.settings.maxExpansionTermsHint') }}
          </div>
        </a-form-item>

        <!-- 选择术语库 -->
        <a-form-item :label="t('glossary.settings.selectCollections')">
          <a-select
            v-model:value="config.collection_ids"
            mode="multiple"
            :placeholder="t('glossary.settings.selectCollectionsPlaceholder')"
            :disabled="!config.enable"
            :options="collectionOptions"
            :filter-option="filterOption"
            show-search
            :virtual="true"
            :max-tag-count="3"
            style="width: 100%"
            @change="handleCollectionsChange"
          >
            <template #suffixIcon>
              <InfoCircleOutlined />
            </template>
            <template #notFoundContent>
              <a-empty :description="t('glossary.settings.noMatchingCollections')" />
            </template>
          </a-select>
          <div class="form-help">
            {{ t('glossary.settings.selectCollectionsHint') }}
          </div>
        </a-form-item>
      </a-form>
    </div>

    <!-- 可用术语库列表 -->
    <div class="settings-section">
      <h3>{{ t('glossary.settings.availableCollections') }}</h3>
      <a-list
        :data-source="paginatedCollections"
        :loading="loading"
        :pagination="listPagination"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #avatar>
                <span v-if="item.icon" class="collection-avatar">{{ item.icon }}</span>
                <a-avatar v-else style="background-color: #1890ff;">
                  {{ item.name.charAt(0) }}
                </a-avatar>
              </template>
              <template #title>
                {{ item.name }}
              </template>
              <template #description>
                {{ item.description || t('glossary.noDescription') }}
              </template>
            </a-list-item-meta>
            <template #actions>
              <a-tag>{{ item.term_count }} {{ t('glossary.termLabel') }}</a-tag>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <!-- 操作按钮 -->
    <div class="settings-section">
      <a-space>
        <a-button type="primary" @click="saveConfig" :loading="saving">
          {{ t('common.save') }}
        </a-button>
        <a-button @click="handleReset" :disabled="saving">
          {{ t('common.reset') }}
        </a-button>
      </a-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { InfoCircleOutlined } from '@ant-design/icons-vue'
import { GlossaryService, type GlossaryExpansionConfig } from '@/api/glossary'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 数据
const config = reactive<GlossaryExpansionConfig>({
  enable: false,
  collection_ids: [],
  max_expansion_terms: 3
})

const availableCollections = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const currentPage = ref(1)
const pageSize = 10

// 保存初始配置，用于重置
const initialConfig = ref<{
  enable: boolean
  collection_ids: number[] | null
  max_expansion_terms: number
}>({
  enable: false,
  collection_ids: null,
  max_expansion_terms: 3
})

// 计算属性
const collectionOptions = computed(() => {
  return availableCollections.value.map(c => ({
    label: `${c.icon ? c.icon + ' ' : ''}${c.name} (${c.term_count})`,
    value: c.id
  }))
})

// 列表分页配置
const listPagination = reactive({
  current: 1,
  pageSize: 10,
  total: computed(() => availableCollections.value.length),
  showSizeChanger: false,
  showTotal: (total: number) => t('glossary.total', { total }),
  onChange: (page: number) => {
    currentPage.value = page
    listPagination.current = page
  }
})

// 当前页显示的术语库
const paginatedCollections = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return availableCollections.value.slice(start, end)
})

// 下拉框搜索过滤
const filterOption = (input: string, option: any) => {
  const label = option.label.toLowerCase()
  const value = String(option.value).toLowerCase()
  return label.includes(input.toLowerCase()) || value.includes(input.toLowerCase())
}

// 方法
const loadConfig = async () => {
  loading.value = true
  try {
    const response = await GlossaryService.getExpansionConfig()

    if (response.success) {
      config.enable = response.data.enable || false
      config.collection_ids = response.data.collection_ids || []
      config.max_expansion_terms = response.data.max_expansion_terms || 3
      availableCollections.value = response.data.available_collections || []

      // 保存初始配置，用于重置
      initialConfig.value = {
        enable: config.enable,
        collection_ids: config.collection_ids ? [...config.collection_ids] : [],
        max_expansion_terms: config.max_expansion_terms
      }

      // 重置分页到第一页
      currentPage.value = 1
      listPagination.current = 1
    }
  } catch (error: any) {
    message.error(error.message || t('glossary.settings.loadConfigFailed'))
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await GlossaryService.updateExpansionConfig(config)
    message.success(t('glossary.settings.saveSuccess'))

    // 保存成功后，更新初始配置
    initialConfig.value = {
      enable: config.enable,
      collection_ids: config.collection_ids ? [...config.collection_ids] : [],
      max_expansion_terms: config.max_expansion_terms || 3
    }
  } catch (error: any) {
    message.error(error.message || t('glossary.settings.saveConfigFailed'))
  } finally {
    saving.value = false
  }
}

const handleEnableChange = (checked: boolean) => {
  if (!checked) {
    config.collection_ids = []
  }
}

const handleCollectionsChange = (value: number[]) => {
  config.collection_ids = value
}

const handleReset = () => {
  // 恢复到初始配置
  config.enable = initialConfig.value.enable
  config.collection_ids = initialConfig.value.collection_ids ? [...initialConfig.value.collection_ids] : []
  config.max_expansion_terms = initialConfig.value.max_expansion_terms
  currentPage.value = 1
  listPagination.current = 1
  message.success(t('common.resetSuccess'))
}

// 生命周期
onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.glossary-settings {
  /* 不需要额外的 padding，由父容器控制 */
}

.settings-section {
  padding: var(--space-6);
  border-bottom: 1px solid var(--border-light);
}

.settings-section:last-child {
  border-bottom: none;
}

.settings-section h3 {
  margin: 0 0 var(--space-4);
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.form-help {
  margin-top: var(--space-1);
  color: var(--text-tertiary);
  font-size: 0.875rem;
}

.collection-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  font-size: 20px;
  background-color: var(--surface-02);
  border-radius: var(--radius-base);
}
</style>
