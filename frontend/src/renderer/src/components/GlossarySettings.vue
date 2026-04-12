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

        <!-- 选择术语库 -->
        <a-form-item :label="t('glossary.settings.selectCollections')">
          <a-select
            v-model:value="config.collection_ids"
            mode="multiple"
            :placeholder="t('glossary.settings.selectCollectionsPlaceholder')"
            :disabled="!config.enable"
            :options="collectionOptions"
            style="width: 100%"
            @change="handleCollectionsChange"
          >
            <template #suffixIcon>
              <InfoCircleOutlined />
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
        :data-source="availableCollections"
        :loading="loading"
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
              <a-tag>{{ item.term_count }} {{ t('glossary.terms') }}</a-tag>
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
        <a-button @click="loadConfig">
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
  collection_ids: []
})

const availableCollections = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)

// 计算属性
const collectionOptions = computed(() => {
  return availableCollections.value.map(c => ({
    label: `${c.icon ? c.icon + ' ' : ''}${c.name} (${c.term_count})`,
    value: c.id
  }))
})

// 方法
const loadConfig = async () => {
  loading.value = true
  try {
    const response = await GlossaryService.getExpansionConfig()

    if (response.success) {
      config.enable = response.data.enable || false
      config.collection_ids = response.data.collection_ids || []
      availableCollections.value = response.data.available_collections || []
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
