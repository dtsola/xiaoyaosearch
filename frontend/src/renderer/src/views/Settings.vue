<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2>设置</h2>
      <p>配置小遥搜索的基本参数</p>
    </div>

    <a-tabs type="card" class="settings-tabs">
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
              <a-select v-model:value="speechConfig.model_name" style="width: 100%">
                <a-select-option value="Systran/faster-whisper-base">Base (快速)</a-select-option>
                <a-select-option value="Systran/faster-whisper-small">Small (平衡)</a-select-option>
                <a-select-option value="Systran/faster-whisper-medium">Medium (精确)</a-select-option>
                <a-select-option value="Systran/faster-whisper-large-v3">Large (高精度)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="speechConfig.device" style="width: 200px">
                <a-select-option value="cpu">CPU</a-select-option>
                <a-select-option value="cuda">CUDA (GPU)</a-select-option>
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
              检查可用性
            </a-button>
            <a-button
              :loading="speechConfig.isLoading"
              @click="saveSpeechConfig"
            >
              保存设置
            </a-button>
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
                v-model:value="llmConfig.model_name"
                placeholder="例如: qwen2.5:1.5b"
                style="width: 100%"
              />
              <div class="form-help">输入已安装的Ollama模型名称，支持任何格式</div>
            </a-form-item>
            <a-form-item label="服务地址">
              <a-input v-model:value="llmConfig.service_url" placeholder="http://localhost:11434" />
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button
              type="primary"
              :loading="llmConfig.isTesting"
              @click="testLLMModel"
            >
              测试连接
            </a-button>
            <a-button
              :loading="llmConfig.isLoading"
              @click="saveLLMConfig"
            >
              保存设置
            </a-button>
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
              <a-select v-model:value="visionConfig.model_name" style="width: 100%">
                <a-select-option value="OFA-Sys/chinese-clip-vit-base-patch16">ViT-Base (快速)</a-select-option>
                <a-select-option value="OFA-Sys/chinese-clip-vit-large-patch14">ViT-Large (高精度)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="visionConfig.device" style="width: 200px">
                <a-select-option value="cpu">CPU</a-select-option>
                <a-select-option value="cuda">CUDA (GPU)</a-select-option>
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
              检测可用性
            </a-button>
            <a-button
              :loading="visionConfig.isLoading"
              @click="saveVisionConfig"
            >
              保存设置
            </a-button>
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
              <a-select v-model:value="embeddingConfig.model_name" style="width: 100%">
                <a-select-option value="BAAI/bge-m3">BGE-M3 (多语言)</a-select-option>
                <a-select-option value="BAAI/bge-small-zh">BGE-Small-zh (中文)</a-select-option>
                <a-select-option value="BAAI/bge-large-zh">BGE-Large-zh (中文)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="embeddingConfig.device" style="width: 200px">
                <a-select-option value="cpu">CPU</a-select-option>
                <a-select-option value="cuda">CUDA (GPU)</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button
              type="primary"
              :loading="embeddingConfig.isTesting"
              @click="testEmbeddingModel"
            >
              检测可用性
            </a-button>
            <a-button
              :loading="embeddingConfig.isLoading"
              @click="saveEmbeddingConfig"
            >
              保存设置
            </a-button>
          </a-space>
        </div>
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

// 各类型模型的配置状态
const speechConfig = reactive({
  model_name: 'Systran/faster-whisper-base',
  device: 'cpu',
  isLoading: false,
  isTesting: false
})

const llmConfig = reactive({
  model_name: 'qwen2.5:1.5b',
  service_url: 'http://localhost:11434',
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
  model_name: 'BAAI/bge-m3',
  device: 'cpu',
  isLoading: false,
  isTesting: false
})

// 存储所有AI模型配置
const aiModels = ref<AIModelInfo[]>([])

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
            llmConfig.model_name = model.model_name
            llmConfig.service_url = config.service_url || 'http://localhost:11434'
            break
          case 'vision':
            visionConfig.model_name = model.model_name
            visionConfig.device = config.device || 'cpu'
            break
          case 'embedding':
            embeddingConfig.model_name = model.model_name
            embeddingConfig.device = config.device || 'cpu'
            break
        }
      })
    }
  } catch (error) {
    console.error('加载AI模型配置失败:', error)
    message.error('加载AI模型配置失败')
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
      message.success('语音识别配置保存成功，重启应用后生效')
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error('保存语音识别配置失败')
    }
  } catch (error) {
    console.error('保存语音识别配置失败:', error)
    message.error('保存语音识别配置失败')
  } finally {
    speechConfig.isLoading = false
  }
}

// 测试语音识别模型
const testSpeechModel = async () => {
  const speechModel = aiModels.value.find(m => m.model_type === 'speech')
  if (!speechModel) {
    message.warning('请先保存语音识别配置')
    return
  }

  speechConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(speechModel.id)
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(`语音识别模型测试成功，响应时间: ${result.response_time}秒`)
      } else {
        message.error(`语音识别模型测试失败: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试语音识别模型失败:', error)
    message.error('测试语音识别模型失败')
  } finally {
    speechConfig.isTesting = false
  }
}

// 保存大语言模型配置
const saveLLMConfig = async () => {
  llmConfig.isLoading = true
  try {
    const response = await AIModelConfigService.updateAIModelConfig({
      model_type: 'llm',
      provider: 'local',
      model_name: llmConfig.model_name,
      config: {
        service_url: llmConfig.service_url
      }
    })

    if (response.success) {
      message.success('大语言模型配置保存成功，重启应用后生效')
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error('保存大语言模型配置失败')
    }
  } catch (error) {
    console.error('保存大语言模型配置失败:', error)
    message.error('保存大语言模型配置失败')
  } finally {
    llmConfig.isLoading = false
  }
}

// 测试大语言模型
const testLLMModel = async () => {
  const llmModel = aiModels.value.find(m => m.model_type === 'llm')
  if (!llmModel) {
    message.warning('请先保存大语言模型配置')
    return
  }

  llmConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(llmModel.id, {
      test_data: '你好，请介绍一下你自己'
    })
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(`大语言模型测试成功，响应时间: ${result.response_time}秒`)
      } else {
        message.error(`大语言模型测试失败: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试大语言模型失败:', error)
    message.error('测试大语言模型失败')
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
      message.success('视觉模型配置保存成功，重启应用后生效')
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error('保存视觉模型配置失败')
    }
  } catch (error) {
    console.error('保存视觉模型配置失败:', error)
    message.error('保存视觉模型配置失败')
  } finally {
    visionConfig.isLoading = false
  }
}

// 测试视觉模型
const testVisionModel = async () => {
  const visionModel = aiModels.value.find(m => m.model_type === 'vision')
  if (!visionModel) {
    message.warning('请先保存视觉模型配置')
    return
  }

  visionConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(visionModel.id)
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(`视觉模型测试成功，响应时间: ${result.response_time}秒`)
      } else {
        message.error(`视觉模型测试失败: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试视觉模型失败:', error)
    message.error('测试视觉模型失败')
  } finally {
    visionConfig.isTesting = false
  }
}

// 保存内嵌模型配置
const saveEmbeddingConfig = async () => {
  embeddingConfig.isLoading = true
  try {
    const response = await AIModelConfigService.updateAIModelConfig({
      model_type: 'embedding',
      provider: 'local',
      model_name: embeddingConfig.model_name,
      config: {
        device: embeddingConfig.device
      }
    })

    if (response.success) {
      message.success('内嵌模型配置保存成功，重启应用后生效')
      // 重新加载模型配置
      await loadAIModels()
    } else {
      message.error('保存内嵌模型配置失败')
    }
  } catch (error) {
    console.error('保存内嵌模型配置失败:', error)
    message.error('保存内嵌模型配置失败')
  } finally {
    embeddingConfig.isLoading = false
  }
}

// 测试内嵌模型
const testEmbeddingModel = async () => {
  const embeddingModel = aiModels.value.find(m => m.model_type === 'embedding')
  if (!embeddingModel) {
    message.warning('请先保存内嵌模型配置')
    return
  }

  embeddingConfig.isTesting = true
  try {
    const response = await AIModelConfigService.testAIModel(embeddingModel.id, {
      test_data: '这是一个测试文本，用于验证文本嵌入模型的功能。'
    })
    if (response.success) {
      const result = response.data
      if (result.test_passed) {
        message.success(`内嵌模型测试成功，响应时间: ${result.response_time}秒`)
      } else {
        message.error(`内嵌模型测试失败: ${result.test_message}`)
      }
    }
  } catch (error) {
    console.error('测试内嵌模型失败:', error)
    message.error('测试内嵌模型失败')
  } finally {
    embeddingConfig.isTesting = false
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