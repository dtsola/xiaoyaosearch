<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2>设置</h2>
      <p>配置小遥搜索的基本参数</p>
    </div>

    <a-tabs v-model:activeKey="activeTab" type="card" class="settings-tabs">
      <!-- 语音设置 -->
      <a-tab-pane key="speech" tab="语音设置">
        <div class="settings-section">
          <h3>语音识别设置</h3>
          <a-form layout="vertical">
            <a-form-item label="语音识别">
              <a-alert
                message="本地FastWhisper服务"
                description="使用本地部署的FastWhisper模型进行语音识别"
                type="info"
                show-icon
              />
            </a-form-item>

            <a-form-item label="模型版本">
              <a-select v-model:value="speechSettings.modelSize" style="width: 100%">
                <a-select-option value="Systran/faster-whisper-base">Base (快速)</a-select-option>
                <a-select-option value="Systran/faster-whisper-small">Small (平衡)</a-select-option>
                <a-select-option value="Systran/faster-whisper-medium">Medium (精确)</a-select-option>
                <a-select-option value="Systran/faster-whisper-large">Large (高精度)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="speechSettings.device" style="width: 200px">
                <a-select-option value="cpu">CPU</a-select-option>
                <a-select-option value="cuda">CUDA (GPU)</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button type="primary" @click="testSpeechAvailability">检查可用性</a-button>
            <a-button @click="saveSpeechSettings">保存设置</a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 大语言模型设置 -->
      <a-tab-pane key="llm" tab="大语言模型">
        <div class="settings-section">
          <h3>大语言模型配置</h3>
          <a-form layout="vertical">
            <a-form-item label="LLM服务">
              <a-alert
                message="本地Ollama服务"
                description="使用本地部署的Ollama服务运行大语言模型"
                type="info"
                show-icon
              />
            </a-form-item>

            <a-form-item label="模型名称">
              <a-input
                v-model:value="llmSettings.localModel"
                placeholder="例如: qwen2.5:1.5b"
                style="width: 100%"
              />
              <div class="form-help">输入已安装的Ollama模型名称，支持任何格式</div>
            </a-form-item>
            <a-form-item label="服务地址">
              <a-input v-model:value="llmSettings.ollamaUrl" placeholder="http://localhost:11434" />
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button type="primary" @click="testLLM">测试连接</a-button>
            <a-button @click="saveLLMSettings">保存设置</a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 视觉模型设置 -->
      <a-tab-pane key="vision" tab="视觉模型">
        <div class="settings-section">
          <h3>视觉理解模型配置</h3>
          <a-form layout="vertical">
            <a-form-item label="视觉模型">
              <a-alert
                message="本地CN-CLIP模型"
                description="使用本地部署的中文CLIP模型进行图像理解"
                type="info"
                show-icon
              />
            </a-form-item>

            <a-form-item label="模型版本">
              <a-select v-model:value="visionSettings.clipModel" style="width: 100%">
                <a-select-option value="OFA-Sys/chinese-clip-vit-base-patch16">ViT-Base (快速)</a-select-option>
                <a-select-option value="OFA-Sys/chinese-clip-vit-large-patch16">ViT-Large (高精度)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="visionSettings.device" style="width: 200px">
                <a-select-option value="cpu">CPU</a-select-option>
                <a-select-option value="cuda">CUDA (GPU)</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button type="primary" @click="testVision">检测可用性</a-button>
            <a-button @click="saveVisionSettings">保存设置</a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 内嵌模型设置 -->
      <a-tab-pane key="embedding" tab="内嵌模型">
        <div class="settings-section">
          <h3>文本内嵌模型配置</h3>
          <a-form layout="vertical">
            <a-form-item label="文本内嵌模型">
              <a-alert
                message="本地BGE-M3模型"
                description="使用本地部署的BGE-M3模型生成文本向量嵌入"
                type="info"
                show-icon
              />
            </a-form-item>

            <a-form-item label="模型版本">
              <a-select v-model:value="embeddingSettings.modelName" style="width: 100%">
                <a-select-option value="BAAI/bge-m3">BGE-M3 (多语言)</a-select-option>
                <a-select-option value="BAAI/bge-small-zh">BGE-Small-zh (中文)</a-select-option>
                <a-select-option value="BAAI/bge-large-zh">BGE-Large-zh (中文)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="embeddingSettings.device" style="width: 200px">
                <a-select-option value="cpu">CPU</a-select-option>
                <a-select-option value="cuda">CUDA (GPU)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-space>
                <a-button type="primary" @click="testEmbedding">检测可用性</a-button>
                <a-button @click="saveEmbeddingSettings">保存设置</a-button>
              </a-space>
            </a-form-item>
          </a-form>
        </div>
      </a-tab-pane>

      <!-- 通用设置 -->
      <a-tab-pane key="general" tab="通用设置">
        <div class="settings-section">
          <h3>搜索设置</h3>
          <a-form layout="vertical">
            <a-form-item label="默认返回结果数">
              <a-slider
                v-model:value="generalSettings.defaultResults"
                :min="10"
                :max="100"
                :step="10"
                :marks="{ 10: '10', 50: '50', 100: '100' }"
              />
            </a-form-item>
            <a-form-item label="相似度阈值">
              <a-slider
                v-model:value="generalSettings.threshold"
                :min="0"
                :max="1"
                :step="0.1"
                :tooltip-formatter="(value) => `${(value * 100).toFixed(0)}%`"
              />
            </a-form-item>
            <a-form-item label="最大文件大小">
              <a-input-number
                v-model:value="generalSettings.maxFileSize"
                :min="10"
                :max="500"
                addon-after="MB"
                style="width: 200px"
              />
            </a-form-item>
          </a-form>
        </div>

        <div class="settings-section">
          <a-space>
            <a-button type="primary" @click="saveGeneralSettings">保存设置</a-button>
            <a-button @click="resetSettings">重置默认</a-button>
          </a-space>
        </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { SettingsService } from '@/api/settings'

// 响应式数据
const activeTab = ref('speech')
const isLoading = ref(false)

// 系统设置状态
const systemSettings = reactive({
  search: {
    default_results: 20,
    similarity_threshold: 0.7,
    max_file_size: 50
  },
  ai_models: {} as any,
  system_status: 'healthy' as 'healthy' | 'degraded' | 'unhealthy',
  last_updated: ''
})

// 可用的AI模型列表
const availableModels = ref<any[]>([])

// 语音设置
const speechSettings = reactive({
  modelSize: 'small',
  device: 'cpu',
  enabled: true
})

// 大语言模型设置
const llmSettings = reactive({
  localModel: 'qwen2.5:1.5b',
  ollamaUrl: 'http://localhost:11434',
  enabled: true
})

// 视觉模型设置
const visionSettings = reactive({
  clipModel: 'OFA-Sys/chinese-clip-vit-base-patch16',
  device: 'cpu',
  enabled: true
})

// 内嵌模型设置
const embeddingSettings = reactive({
  modelName: 'BAAI/bge-m3',
  device: 'cpu',
  enabled: true
})

// 通用设置
const generalSettings = reactive({
  defaultResults: 20,
  threshold: 0.7,
  maxFileSize: 50
})

// 数据获取方法
const loadSystemSettings = async () => {
  isLoading.value = true
  try {
    const response = await SettingsService.getSettings()
    if (response.success) {
      Object.assign(systemSettings, response.data)
      updateLocalSettingsFromSystem()
    }
  } catch (error) {
    console.error('加载系统设置失败:', error)
    message.error('加载系统设置失败')
  } finally {
    isLoading.value = false
  }
}

const loadAvailableModels = async () => {
  try {
    const response = await SettingsService.getAvailableModels()
    if (response.success) {
      availableModels.value = response.data.available_models
    }
  } catch (error) {
    console.error('加载可用模型失败:', error)
  }
}

const updateLocalSettingsFromSystem = () => {
  // 从系统设置中更新本地设置状态
  if (systemSettings.search) {
    // 使用后端返回的标准键名格式
    generalSettings.defaultResults = systemSettings.search.default_results || 20
    generalSettings.threshold = systemSettings.search.similarity_threshold || 0.7
    generalSettings.maxFileSize = systemSettings.search.max_file_size || 50
  }

  // 更新AI模型设置
  if (systemSettings.ai_models) {
    // 语音识别模型
    if (systemSettings.ai_models.whisper) {
      speechSettings.modelSize = systemSettings.ai_models.whisper.model_size || 'small'
      speechSettings.device = systemSettings.ai_models.whisper.device || 'cpu'
      speechSettings.enabled = systemSettings.ai_models.whisper.enabled !== false
    }

    // 大语言模型
    if (systemSettings.ai_models.ollama) {
      llmSettings.localModel = systemSettings.ai_models.ollama.local_model || 'qwen2.5:1.5b'
      llmSettings.ollamaUrl = systemSettings.ai_models.ollama.ollama_url || 'http://localhost:11434'
      llmSettings.enabled = systemSettings.ai_models.ollama.enabled !== false
    }

    // 视觉模型
    if (systemSettings.ai_models.clip) {
      visionSettings.clipModel = systemSettings.ai_models.clip.model_name || 'OFA-Sys/chinese-clip-vit-base-patch16'
      visionSettings.device = systemSettings.ai_models.clip.device || 'cpu'
      visionSettings.enabled = systemSettings.ai_models.clip.enabled !== false
    }

    // 内嵌模型
    if (systemSettings.ai_models.bge) {
      embeddingSettings.modelName = systemSettings.ai_models.bge.model_name || 'BAAI/bge-m3'
      embeddingSettings.device = systemSettings.ai_models.bge.device || 'cpu'
      embeddingSettings.enabled = systemSettings.ai_models.bge.enabled !== false
    }
  }
}

// 设置操作方法
const saveSpeechSettings = async () => {
  isLoading.value = true
  try {
    const response = await SettingsService.updateAIModelByType('whisper', {
      model_size: speechSettings.modelSize,
      device: speechSettings.device,
      enabled: speechSettings.enabled
    })

    if (response.success) {
      message.success('语音设置已保存')
      await loadSystemSettings()
    } else {
      message.error(response.error?.message || '保存语音设置失败')
    }
  } catch (error) {
    console.error('保存语音设置失败:', error)
    message.error('保存语音设置失败')
  } finally {
    isLoading.value = false
  }
}

const testSpeechAvailability = async () => {
  try {
    const response = await SettingsService.testAIModelByType('whisper')
    if (response.success) {
      message.success(`语音服务可用 - ${response.data.test_message}`)
    } else {
      message.error(response.error?.message || '语音服务测试失败')
    }
  } catch (error) {
    console.error('测试语音服务失败:', error)
    message.error('测试语音服务失败')
  }
}

const saveGeneralSettings = async () => {
  isLoading.value = true
  try {
    const response = await SettingsService.updateSettings({
      search: {
        default_results: generalSettings.defaultResults,
        similarity_threshold: generalSettings.threshold,
        max_file_size: generalSettings.maxFileSize
      }
    })

    if (response.success) {
      message.success('通用设置已保存')
      await loadSystemSettings()
    } else {
      message.error(response.error?.message || '保存通用设置失败')
    }
  } catch (error) {
    console.error('保存通用设置失败:', error)
    message.error('保存通用设置失败')
  } finally {
    isLoading.value = false
  }
}

const resetSettings = () => {
  Modal.confirm({
    title: '确认重置',
    content: '确定要重置所有设置为默认值吗？',
    async onOk() {
      try {
        const response = await SettingsService.resetSystemSettings()
        if (response.success) {
          message.success('设置已重置')
          await loadSystemSettings()
        } else {
          message.error(response.error?.message || '重置设置失败')
        }
      } catch (error) {
        console.error('重置设置失败:', error)
        message.error('重置设置失败')
      }
    }
  })
}

// 大语言模型方法
const testLLM = async () => {
  try {
    const response = await SettingsService.testAIModelByType('ollama')
    if (response.success) {
      message.success(`LLM服务可用 - ${response.data.test_message}`)
    } else {
      message.error(response.error?.message || 'LLM连接测试失败')
    }
  } catch (error) {
    console.error('测试LLM服务失败:', error)
    message.error('测试LLM服务失败')
  }
}

const saveLLMSettings = async () => {
  isLoading.value = true
  try {
    const response = await SettingsService.updateAIModelByType('ollama', {
      local_model: llmSettings.localModel,
      ollama_url: llmSettings.ollamaUrl,
      enabled: llmSettings.enabled
    })

    if (response.success) {
      message.success('大语言模型设置已保存')
      await loadSystemSettings()
    } else {
      message.error(response.error?.message || '保存大语言模型设置失败')
    }
  } catch (error) {
    console.error('保存大语言模型设置失败:', error)
    message.error('保存大语言模型设置失败')
  } finally {
    isLoading.value = false
  }
}

// 视觉模型方法
const testVision = async () => {
  try {
    const response = await SettingsService.testAIModelByType('clip')
    if (response.success) {
      message.success(`视觉服务可用 - ${response.data.test_message}`)
    } else {
      message.error(response.error?.message || '视觉服务测试失败')
    }
  } catch (error) {
    console.error('测试视觉服务失败:', error)
    message.error('测试视觉服务失败')
  }
}

const saveVisionSettings = async () => {
  isLoading.value = true
  try {
    const response = await SettingsService.updateAIModelByType('clip', {
      model_name: visionSettings.clipModel,
      device: visionSettings.device,
      enabled: visionSettings.enabled
    })

    if (response.success) {
      message.success('视觉模型设置已保存')
      await loadSystemSettings()
    } else {
      message.error(response.error?.message || '保存视觉模型设置失败')
    }
  } catch (error) {
    console.error('保存视觉模型设置失败:', error)
    message.error('保存视觉模型设置失败')
  } finally {
    isLoading.value = false
  }
}

// 内嵌模型方法
const testEmbedding = async () => {
  try {
    const response = await SettingsService.testAIModelByType('bge')
    if (response.success) {
      message.success(`BGE服务可用 - ${response.data.test_message}`)
    } else {
      message.error(response.error?.message || 'BGE模型测试失败')
    }
  } catch (error) {
    console.error('测试BGE服务失败:', error)
    message.error('测试BGE服务失败')
  }
}

const saveEmbeddingSettings = async () => {
  isLoading.value = true
  try {
    const response = await SettingsService.updateAIModelByType('bge', {
      model_name: embeddingSettings.modelName,
      device: embeddingSettings.device,
      enabled: embeddingSettings.enabled
    })

    if (response.success) {
      message.success('内嵌模型设置已保存')
      await loadSystemSettings()
    } else {
      message.error(response.error?.message || '保存内嵌模型设置失败')
    }
  } catch (error) {
    console.error('保存内嵌模型设置失败:', error)
    message.error('保存内嵌模型设置失败')
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadSystemSettings()
  loadAvailableModels()
})

</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-6);
}

.settings-header {
  margin-bottom: var(--space-8);
}

.settings-header h2 {
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.settings-header p {
  margin: 0;
  color: var(--text-secondary);
}

.settings-tabs {
  background: var(--surface-01);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-base);
  overflow: hidden;
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
  margin-left: var(--space-2);
  color: var(--text-tertiary);
  font-size: 0.875rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: var(--space-4);
  }

  .settings-section {
    padding: var(--space-4);
  }
}
</style>