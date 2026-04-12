<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2>{{ t('settings.title') }}</h2>
      <p>{{ t('settings.subtitle') }}</p>
    </div>

    <a-tabs type="card" class="settings-tabs">
      <!-- 语音设置 -->
      <a-tab-pane key="speech" :tab="t('settingsSpeech.title')">
        <div class="settings-section">
          <h3>{{ t('settingsSpeech.voiceRecognitionSettings') }}</h3>
          <a-form layout="vertical">
            <a-form-item :label="t('settingsSpeech.voiceRecognition')">
              <a-alert
                :message="t('settingsSpeech.localFastWhisperService')"
                :description="t('settingsSpeech.localFastWhisperDesc')"
                type="info"
                show-icon
              />
            </a-form-item>

            <a-form-item :label="t('settingsSpeech.modelVersion')">
              <a-select v-model:value="speechConfig.model_name" style="width: 100%">
                <a-select-option value="Systran/faster-whisper-base">{{ t('settingsSpeech.modelBase') }}</a-select-option>
                <a-select-option value="Systran/faster-whisper-small">{{ t('settingsSpeech.modelSmall') }}</a-select-option>
                <a-select-option value="Systran/faster-whisper-medium">{{ t('settingsSpeech.modelMedium') }}</a-select-option>
                <a-select-option value="Systran/faster-whisper-large-v3">{{ t('settingsSpeech.modelLarge') }}</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item :label="t('settingsSpeech.runningDevice')">
              <a-select v-model:value="speechConfig.device" style="width: 200px">
                <a-select-option value="cpu">{{ t('settingsSpeech.deviceCpu') }}</a-select-option>
                <a-select-option value="cuda">{{ t('settingsSpeech.deviceCuda') }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button
              type="primary"
              :loading="speechConfig.isTesting"
              @click="testSpeechModel"
            >
              {{ t('settingsSpeech.checkAvailability') }}
            </a-button>
            <a-button
              :loading="speechConfig.isLoading"
              @click="saveSpeechConfig"
            >
              {{ t('settingsSpeech.saveSettings') }}
            </a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 大语言模型设置 -->
      <a-tab-pane key="llm" :tab="t('settingsLLM.title')">
        <div class="settings-section">
          <h3>{{ t('settingsLLM.title') }}</h3>
          <a-form layout="vertical">
            <!-- 模型类型选择器 -->
            <a-form-item :label="t('settingsLLM.modelType')">
              <a-select
                v-model:value="llmConfig.provider"
                style="width: 200px"
                @change="handleProviderChange"
              >
                <a-select-option value="local">
                  {{ t('settingsLLM.modelTypeOllama') }}
                </a-select-option>
                <a-select-option value="cloud">
                  {{ t('settingsLLM.modelTypeOpenAI') }}
                </a-select-option>
              </a-select>
            </a-form-item>

            <!-- Ollama 本地服务配置表单 -->
            <template v-if="llmConfig.provider === 'local'">
              <a-form-item>
                <a-alert
                  :message="t('settingsLLM.localOllamaService')"
                  :description="t('settingsLLM.localOllamaDesc')"
                  type="info"
                  show-icon
                />
              </a-form-item>

              <a-form-item :label="t('settingsLLM.modelName')">
                <a-input
                  v-model:value="llmConfig.model_name_local"
                  :placeholder="t('settingsLLM.modelNamePlaceholder')"
                  style="width: 100%"
                />
                <div class="form-help">{{ t('settingsLLM.modelNameHelp') }}</div>
              </a-form-item>

              <a-form-item :label="t('settingsLLM.serviceUrl')">
                <a-input
                  v-model:value="llmConfig.base_url"
                  :placeholder="t('settingsLLM.serviceUrlPlaceholder')"
                />
              </a-form-item>
            </template>

            <!-- OpenAI 兼容云端服务配置表单 -->
            <template v-else>
              <!-- 云端服务说明卡片 -->
              <a-form-item>
                <a-alert
                  type="info"
                  show-icon
                  class="cloud-service-info"
                >
                  <template #message>
                    <span>{{ t('settingsLLM.cloudServiceInfo.title') }}</span>
                  </template>
                  <template #description>
                    <div class="cloud-service-info-content">
                      <p>{{ t('settingsLLM.cloudServiceInfo.description') }}</p>
                      <ul class="info-list">
                        <li class="info-item-success">
                          <span>{{ t('settingsLLM.cloudServiceInfo.localDataSafe') }}</span>
                        </li>
                        <li class="info-item-warning">
                          <span>{{ t('settingsLLM.cloudServiceInfo.querySent') }}</span>
                        </li>
                        <li class="info-item-tip">
                          <span>{{ t('settingsLLM.cloudServiceInfo.betterUnderstanding') }}</span>
                        </li>
                      </ul>
                      <p class="info-notice">
                        {{ t('settingsLLM.cloudServiceInfo.recommendation') }}
                      </p>
                    </div>
                  </template>
                </a-alert>
              </a-form-item>

              <a-form-item :label="t('settingsLLM.apiKey')">
                <a-input-password
                  v-model:value="llmConfig.api_key"
                  :placeholder="t('settingsLLM.apiKeyPlaceholder')"
                />
              </a-form-item>

              <a-form-item :label="t('settingsLLM.endpoint')">
                <a-input
                  v-model:value="llmConfig.endpoint"
                  :placeholder="t('settingsLLM.endpointPlaceholder')"
                />
                <div class="form-help">{{ t('settingsLLM.endpointHelp') }}</div>
              </a-form-item>

              <a-form-item :label="t('settingsLLM.modelName')">
                <a-input
                  v-model:value="llmConfig.model_name_cloud"
                  :placeholder="t('settingsLLM.modelNamePlaceholderCloud')"
                />
                <div class="form-help">{{ t('settingsLLM.modelNameHelpCloud') }}</div>
              </a-form-item>
            </template>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button
              type="primary"
              :loading="llmConfig.isTesting"
              @click="testLLMModel"
            >
              {{ t('settingsLLM.testConnection') }}
            </a-button>
            <a-button
              :loading="llmConfig.isLoading"
              @click="saveLLMConfig"
            >
              {{ t('settingsLLM.saveSettings') }}
            </a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 视觉模型设置 -->
      <a-tab-pane key="vision" :tab="t('settingsVision.title')">
        <div class="settings-section">
          <h3>{{ t('settingsVision.title') }}</h3>
          <a-form layout="vertical">
            <a-form-item :label="t('settingsVision.visionModel')">
              <a-alert
                :message="t('settingsVision.localCNClipService')"
                :description="t('settingsVision.localCNClipDesc')"
                type="info"
                show-icon
              />
            </a-form-item>

            <a-form-item :label="t('settingsVision.modelVersion')">
              <a-select v-model:value="visionConfig.model_name" style="width: 100%">
                <a-select-option value="OFA-Sys/chinese-clip-vit-base-patch16">ViT-Base ({{ t('settingsSpeech.modelBase') }})</a-select-option>
                <a-select-option value="OFA-Sys/chinese-clip-vit-large-patch14">ViT-Large ({{ t('settingsSpeech.modelLarge') }})</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item :label="t('settingsVision.runningDevice')">
              <a-select v-model:value="visionConfig.device" style="width: 200px">
                <a-select-option value="cpu">{{ t('settingsVision.deviceCpu') }}</a-select-option>
                <a-select-option value="cuda">{{ t('settingsVision.deviceCuda') }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button
              type="primary"
              :loading="visionConfig.isTesting"
              @click="testVisionModel"
            >
              {{ t('settingsVision.testConnection') }}
            </a-button>
            <a-button
              :loading="visionConfig.isLoading"
              @click="saveVisionConfig"
            >
              {{ t('settingsSpeech.saveSettings') }}
            </a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 内嵌模型设置 -->
      <a-tab-pane key="embedding" :tab="t('settingsEmbedding.title')">
        <!-- 模型变化提示 -->
        <a-alert
          v-if="embeddingModelChanged"
          type="warning"
          show-icon
          closable
          class="model-change-alert"
          @close="embeddingModelChanged = false"
        >
          <template #message>
            <div class="alert-content">
              <span>{{ t('settingsEmbedding.modelChanged') }}</span>
              <div class="alert-actions">
                <a-button type="primary" size="small" @click="restartApp">
                  {{ t('settingsEmbedding.restartApp') }}
                </a-button>
                <a-button size="small" @click="goToIndexManagement">
                  {{ t('settingsEmbedding.goToIndexManagement') }}
                </a-button>
              </div>
            </div>
          </template>
          <template #description>
            <p>{{ t('settingsEmbedding.rebuildTip') }}</p>
          </template>
        </a-alert>

        <div class="settings-section">
          <h3>{{ t('settingsEmbedding.title') }}</h3>
          <a-form layout="vertical">
            <!-- 模型类型选择器 -->
            <a-form-item :label="t('settingsEmbedding.modelType')">
              <a-select
                v-model:value="embeddingConfig.provider"
                style="width: 200px"
                @change="handleEmbeddingProviderChange"
              >
                <a-select-option value="local">
                  {{ t('settingsEmbedding.modelTypeLocal') }}
                </a-select-option>
                <a-select-option value="cloud">
                  {{ t('settingsEmbedding.modelTypeCloud') }}
                </a-select-option>
              </a-select>
            </a-form-item>

            <!-- 本地配置表单 -->
            <template v-if="embeddingConfig.provider === 'local'">
              <a-form-item>
                <a-alert
                  :message="t('settingsEmbedding.localBgeM3Service')"
                  :description="t('settingsEmbedding.localBgeM3Desc')"
                  type="info"
                  show-icon
                />
              </a-form-item>

              <a-form-item :label="t('settingsEmbedding.modelVersion')">
                <a-select v-model:value="embeddingConfig.model_name_local" style="width: 100%">
                  <a-select-option value="BAAI/bge-m3">{{ t('settingsEmbedding.modelBgeM3') }}</a-select-option>
                  <a-select-option value="BAAI/bge-small-zh">BGE-Small-zh ({{ t('fileType.text') }})</a-select-option>
                  <a-select-option value="BAAI/bge-large-zh">BGE-Large-zh ({{ t('fileType.text') }})</a-select-option>
                </a-select>
              </a-form-item>
              <a-form-item :label="t('settingsEmbedding.runningDevice')">
                <a-select v-model:value="embeddingConfig.device" style="width: 200px">
                  <a-select-option value="cpu">{{ t('settingsEmbedding.deviceCpu') }}</a-select-option>
                  <a-select-option value="cuda">{{ t('settingsEmbedding.deviceCuda') }}</a-select-option>
                </a-select>
              </a-form-item>
            </template>

            <!-- 云端配置表单 -->
            <template v-else>
              <!-- 云端服务说明卡片 -->
              <a-form-item>
                <a-alert
                  type="warning"
                  show-icon
                  class="cloud-service-info"
                >
                  <template #message>
                    <span>{{ t('settingsEmbedding.cloudServiceInfo.title') }}</span>
                  </template>
                  <template #description>
                    <div class="cloud-service-info-content">
                      <ul class="info-list">
                        <li class="info-item-success">
                          <span>{{ t('settingsEmbedding.cloudServiceInfo.localDataSafe') }}</span>
                        </li>
                        <li class="info-item-warning">
                          <span>{{ t('settingsEmbedding.cloudServiceInfo.querySent') }}</span>
                        </li>
                        <li class="info-item-tip">
                          <span>{{ t('settingsEmbedding.cloudServiceInfo.allCompatible') }}</span>
                        </li>
                        <li class="info-item-tip">
                          <span>{{ t('settingsEmbedding.cloudServiceInfo.needRebuild') }}</span>
                        </li>
                      </ul>
                      <p class="info-notice">
                        {{ t('settingsEmbedding.cloudServiceInfo.privacyTip') }}
                      </p>
                    </div>
                  </template>
                </a-alert>
              </a-form-item>

              <a-form-item :label="t('settingsEmbedding.apiKey')">
                <a-input-password
                  v-model:value="embeddingConfig.api_key"
                  :placeholder="'sk-*****************************************'"
                />
              </a-form-item>

              <a-form-item :label="t('settingsEmbedding.endpoint')" required>
                <a-input
                  v-model:value="embeddingConfig.endpoint"
                  :placeholder="t('settingsEmbedding.endpointPlaceholder')"
                />
                <div class="form-help">{{ t('settingsEmbedding.endpointHelp') }}</div>
              </a-form-item>

              <a-form-item :label="t('settingsEmbedding.modelVersion')">
                <a-input
                  v-model:value="embeddingConfig.model_name_cloud"
                  :placeholder="t('settingsEmbedding.modelPlaceholderCloud')"
                />
                <div class="form-help">{{ t('settingsEmbedding.modelHelpCloud') }}</div>
              </a-form-item>

              <a-form-item :label="t('settingsEmbedding.batchSize')">
                <a-input-number
                  v-model:value="embeddingConfig.batch_size"
                  :min="1"
                  :max="100"
                  :step="1"
                  style="width: 200px"
                />
                <div class="form-help">{{ t('settingsEmbedding.batchSizeHelp') }}</div>
              </a-form-item>

              <a-form-item :label="t('settingsEmbedding.concurrentRequests')">
                <a-input-number
                  v-model:value="embeddingConfig.concurrent_requests"
                  :min="1"
                  :max="10"
                  :step="1"
                  style="width: 200px"
                />
                <div class="form-help">{{ t('settingsEmbedding.concurrentRequestsHelp') }}</div>
              </a-form-item>
            </template>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button
              type="primary"
              :loading="embeddingConfig.isTesting"
              @click="testEmbeddingModel"
            >
              {{ t('settingsEmbedding.testConnection') }}
            </a-button>
            <a-button
              :loading="embeddingConfig.isLoading"
              @click="saveEmbeddingConfig"
            >
              {{ t('settingsSpeech.saveSettings') }}
            </a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 术语库设置 -->
      <a-tab-pane key="glossary" :tab="t('glossary.settings.title')">
        <GlossarySettings />
      </a-tab-pane>

      <!-- 通用设置 -->
      <!-- <a-tab-pane key="general" tab="通用设置">
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
            <a-button type="primary" @click="saveGeneralSettings" :loading="isLoading">保存设置</a-button>
            <a-button @click="resetSettings">重置默认</a-button>
          </a-space>
        </div>
      </a-tab-pane> -->
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { AIModelConfigService } from '@/api/config'
import type { AIModelInfo, AIModelTestResult } from '@/types/api'
import { useI18n } from 'vue-i18n'
import GlossarySettings from '@/components/GlossarySettings.vue'

// 国际化
const { t } = useI18n()

// 各类型模型的配置状态
const speechConfig = reactive({
  model_name: 'Systran/faster-whisper-base',
  device: 'cpu',
  isLoading: false,
  isTesting: false
})

const llmConfig = reactive({
  provider: 'local',      // 'local' | 'cloud'（新增）
  model_name_local: 'qwen2.5:1.5b',   // local 专用
  model_name_cloud: 'gpt-3.5-turbo',  // cloud 专用
  base_url: 'http://localhost:11434',
  api_key: '',            // 新增
  endpoint: '',           // 新增
  isLoading: false,
  isTesting: false
})

const visionConfig = reactive({
  model_name: 'OFA-Sys/chinese-clip-vit-base-patch16',
  device: 'cpu',
  isLoading: false,
  isTesting: false
})

const embeddingConfig = reactive({
  provider: 'local',        // 'local' | 'cloud'
  model_name_local: 'BAAI/bge-m3',
  model_name_cloud: 'text-embedding-3-small',
  device: 'cpu',
  api_key: '',
  endpoint: 'https://api.openai.com/v1',
  batch_size: 10,           // 云端API批处理大小
  concurrent_requests: 4,   // 并发请求数量
  isLoading: false,
  isTesting: false
})

// 模型切换状态追踪
const embeddingModelChanged = ref(false)
const originalEmbeddingProvider = ref('local')
const originalEmbeddingModel = ref('')

// 存储所有AI模型配置
const aiModels = ref<AIModelInfo[]>([])

// 类型切换处理（新增）
const handleProviderChange = (value: string) => {
  // 只需要切换 provider，model_name 已经分开存储了
  llmConfig.provider = value
}

// Embedding provider 切换处理
const handleEmbeddingProviderChange = (value: string) => {
  embeddingConfig.provider = value
}

// 加载所有AI模型配置
const loadAIModels = async () => {
  try {
    const response = await AIModelConfigService.getAIModels()
    if (response.success) {
      aiModels.value = response.data

      // 将后端配置映射到前端表单
      response.data.forEach(model => {
        const config = AIModelConfigService.parseModelConfig(model.config_json)

        switch (model.model_type) {
          case 'speech':
            speechConfig.model_name = model.model_name
            speechConfig.device = config.device || 'cpu'
            break
          case 'llm':
            llmConfig.provider = model.provider || 'local'
            if (model.provider === 'cloud') {
              llmConfig.model_name_cloud = model.model_name
              llmConfig.api_key = config.api_key || ''
              llmConfig.endpoint = config.endpoint || 'https://api.openai.com/v1'
            } else {
              llmConfig.model_name_local = model.model_name
              llmConfig.base_url = config.base_url || 'http://localhost:11434'
            }
            break
          case 'vision':
            visionConfig.model_name = model.model_name
            visionConfig.device = config.device || 'cpu'
            break
          case 'embedding':
            embeddingConfig.provider = model.provider || 'local'
            if (model.provider === 'cloud') {
              embeddingConfig.model_name_cloud = model.model_name
              embeddingConfig.api_key = config.api_key || ''
              embeddingConfig.endpoint = config.endpoint || 'https://api.openai.com/v1'
              embeddingConfig.batch_size = config.batch_size || 10
              embeddingConfig.concurrent_requests = config.concurrent_requests || 4
              // 保存原始配置用于变化检测
              originalEmbeddingProvider.value = model.provider || 'local'
              originalEmbeddingModel.value = model.model_name
            } else {
              embeddingConfig.model_name_local = model.model_name
              embeddingConfig.device = config.device || 'cpu'
              // 保存原始配置用于变化检测
              originalEmbeddingProvider.value = model.provider || 'local'
              originalEmbeddingModel.value = model.model_name
            }
            break
        }
      })
    }
  } catch (error) {
    console.error('加载AI模型配置失败:', error)
    message.error(t('error.configLoadFailed'))
  }
}

// 保存语音识别配置
const saveSpeechConfig = async () => {
  speechConfig.isLoading = true
  try {
    const response = await AIModelConfigService.updateAIModelConfig({
      model_type: 'speech',
      provider: 'local',
      model_name: speechConfig.model_name,
      config: {
        device: speechConfig.device
      }
    })

    if (response.success) {
      message.success(t('settingsSpeech.saveSuccessRestart'))
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error(t('error.speechConfigSaveFailed'))
    }
  } catch (error) {
    console.error('保存语音识别配置失败:', error)
    message.error(t('error.speechConfigSaveFailed'))
  } finally {
    speechConfig.isLoading = false
  }
}

// 测试语音识别模型
const testSpeechModel = async () => {
  const speechModel = aiModels.value.find(m => m.model_type === 'speech')
  if (!speechModel) {
    message.warning(t('settingsSpeech.pleaseSaveFirst'))
    return
  }

  speechConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(speechModel.id)
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(t('aiModel.testSuccess'))
      } else {
        message.error(t('error.speechModelTestFailed') + `: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试语音识别模型失败:', error)
    message.error(t('error.speechModelTestFailed'))
  } finally {
    speechConfig.isTesting = false
  }
}

// 保存大语言模型配置
const saveLLMConfig = async () => {
  llmConfig.isLoading = true
  try {
    const config: any = {
      model_type: 'llm',
      provider: llmConfig.provider,
      model_name: llmConfig.provider === 'cloud' ? llmConfig.model_name_cloud : llmConfig.model_name_local,
      config: {}
    }

    // ========== 新增：根据 provider 添加不同配置 ==========
    if (llmConfig.provider === 'local') {
      config.config = {
        base_url: llmConfig.base_url
      }
    } else {
      config.config = {
        api_key: llmConfig.api_key,
        endpoint: llmConfig.endpoint
      }
    }
    // =========================================================

    const response = await AIModelConfigService.updateAIModelConfig(config)

    if (response.success) {
      message.success(t('settingsLLM.saveSuccessRestart'))
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error(t('error.llmConfigSaveFailed'))
    }
  } catch (error) {
    console.error('保存大语言模型配置失败:', error)
    message.error(t('error.llmConfigSaveFailed'))
  } finally {
    llmConfig.isLoading = false
  }
}

// 测试大语言模型
const testLLMModel = async () => {
  const llmModel = aiModels.value.find(m => m.model_type === 'llm')
  if (!llmModel) {
    message.warning(t('settingsLLM.pleaseSaveFirst'))
    return
  }

  llmConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(llmModel.id, {
      test_data: t('settingsLLM.testData')
    })
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(t('aiModel.testSuccess'))
      } else {
        message.error(t('error.llmModelTestFailed') + `: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试大语言模型失败:', error)
    message.error(t('error.llmModelTestFailed'))
  } finally {
    llmConfig.isTesting = false
  }
}

// 保存视觉模型配置
const saveVisionConfig = async () => {
  visionConfig.isLoading = true
  try {
    const response = await AIModelConfigService.updateAIModelConfig({
      model_type: 'vision',
      provider: 'local',
      model_name: visionConfig.model_name,
      config: {
        device: visionConfig.device
      }
    })

    if (response.success) {
      message.success(t('settingsVision.saveSuccessRestart'))
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error(t('error.visionConfigSaveFailed'))
    }
  } catch (error) {
    console.error('保存视觉模型配置失败:', error)
    message.error(t('error.visionConfigSaveFailed'))
  } finally {
    visionConfig.isLoading = false
  }
}

// 测试视觉模型
const testVisionModel = async () => {
  const visionModel = aiModels.value.find(m => m.model_type === 'vision')
  if (!visionModel) {
    message.warning(t('settingsVision.pleaseSaveFirst'))
    return
  }

  visionConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(visionModel.id)
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(t('aiModel.testSuccess'))
      } else {
        message.error(t('error.visionModelTestFailed') + `: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试视觉模型失败:', error)
    message.error(t('error.visionModelTestFailed'))
  } finally {
    visionConfig.isTesting = false
  }
}

// 保存内嵌模型配置
const saveEmbeddingConfig = async () => {
  embeddingConfig.isLoading = true
  try {
    const config: any = {
      model_type: 'embedding',
      provider: embeddingConfig.provider,
      model_name: embeddingConfig.provider === 'cloud' ? embeddingConfig.model_name_cloud : embeddingConfig.model_name_local,
      config: {}
    }

    // 根据提供商添加不同配置
    if (embeddingConfig.provider === 'local') {
      config.config = {
        device: embeddingConfig.device
      }
    } else {
      config.config = {
        api_key: embeddingConfig.api_key,
        endpoint: embeddingConfig.endpoint,
        batch_size: embeddingConfig.batch_size,
        concurrent_requests: embeddingConfig.concurrent_requests
      }
    }

    const response = await AIModelConfigService.updateAIModelConfig(config)

    if (response.success) {
      message.success(t('settingsEmbedding.saveSuccessRestart'))

      // 检测模型是否发生变化
      const currentModelName = embeddingConfig.provider === 'cloud' ? embeddingConfig.model_name_cloud : embeddingConfig.model_name_local
      if (originalEmbeddingProvider.value !== embeddingConfig.provider || originalEmbeddingModel.value !== currentModelName) {
        embeddingModelChanged.value = true
      }

      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error(t('error.embeddingConfigSaveFailed'))
    }
  } catch (error) {
    console.error('保存内嵌模型配置失败:', error)
    message.error(t('error.embeddingConfigSaveFailed'))
  } finally {
    embeddingConfig.isLoading = false
  }
}

// 测试内嵌模型
const testEmbeddingModel = async () => {
  const embeddingModel = aiModels.value.find(m => m.model_type === 'embedding')
  if (!embeddingModel) {
    message.warning(t('settingsEmbedding.pleaseSaveFirst'))
    return
  }

  embeddingConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(embeddingModel.id, {
      test_data: t('settingsEmbedding.testData')
    })
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(t('aiModel.testSuccess'))
      } else {
        message.error(t('error.embeddingModelTestFailed') + `: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试内嵌模型失败:', error)
    message.error(t('error.embeddingModelTestFailed'))
  } finally {
    embeddingConfig.isTesting = false
  }
}

// 重启应用
const restartApp = () => {
  const api = (window as any).api
  if (api && typeof api.restartApp === 'function') {
    api.restartApp()
  } else {
    message.info(t('settingsEmbedding.manualRestart'))
  }
}

// 前往索引管理页面
const goToIndexManagement = () => {
  // 使用路由跳转到索引页面
  const router = (window as any).$router
  if (router) {
    router.push('/index')
  } else {
    message.info(t('settingsEmbedding.manualNavigate'))
  }
}

// 页面加载时获取AI模型配置
onMounted(() => {
  loadAIModels()
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

/* 模型变化警告框样式 */
.model-change-alert {
  margin-bottom: var(--space-4);
}

.model-change-alert .alert-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.model-change-alert .alert-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

/* 云端服务说明卡片样式 */
.cloud-service-info {
  margin-bottom: var(--space-4);
}

.cloud-service-info-content {
  line-height: 1.6;
}

.cloud-service-info-content p {
  margin-bottom: var(--space-2);
}

.cloud-service-info-content .info-list {
  list-style: none;
  padding: 0;
  margin: var(--space-3) 0;
}

.cloud-service-info-content .info-list li {
  padding: var(--space-2) 0;
  display: flex;
  align-items: flex-start;
}

.cloud-service-info-content .info-item-success {
  color: var(--color-success);
}

.cloud-service-info-content .info-item-warning {
  color: var(--color-warning);
}

.cloud-service-info-content .info-item-tip {
  color: var(--color-info);
}

.cloud-service-info-content .info-notice {
  margin-top: var(--space-3);
  padding: var(--space-2);
  background: var(--surface-02);
  border-radius: var(--radius-md);
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