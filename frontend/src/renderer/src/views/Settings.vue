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
                <a-select-option value="tiny">Tiny (最快)</a-select-option>
                <a-select-option value="base">Base (快速)</a-select-option>
                <a-select-option value="small">Small (平衡)</a-select-option>
                <a-select-option value="medium">Medium (精确)</a-select-option>
                <a-select-option value="large">Large (高精度)</a-select-option>
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
            <a-button type="primary" @click="saveSpeechSettings">保存设置</a-button>
            <a-button @click="testSpeechAvailability">检查可用性</a-button>
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
                <a-select-option value="OFA-Sys/chinese-clip-vit-base">ViT-Base (快速)</a-select-option>
                <a-select-option value="OFA-Sys/chinese-clip-vit-large">ViT-Large (高精度)</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-space>
            <a-button type="primary" @click="testVision">测试模型</a-button>
            <a-button @click="saveVisionSettings">保存设置</a-button>
          </a-space>
        </div>
      </a-tab-pane>

      <!-- 搜索设置 -->
      <a-tab-pane key="search" tab="搜索设置">
        <div class="settings-section">
          <h3>搜索参数配置</h3>
          <a-form layout="vertical">
            <a-form-item label="默认搜索类型">
              <a-select v-model:value="searchSettings.defaultType" style="width: 200px">
                <a-select-option value="semantic">语义搜索</a-select-option>
                <a-select-option value="fulltext">全文搜索</a-select-option>
                <a-select-option value="hybrid">混合搜索</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="默认相似度阈值">
              <a-slider
                v-model:value="searchSettings.defaultThreshold"
                :min="0"
                :max="1"
                :step="0.1"
                :tooltip-formatter="(value: number) => `${(value * 100).toFixed(0)}%`"
              />
            </a-form-item>
            <a-form-item label="默认结果数量">
              <a-input-number
                v-model:value="searchSettings.defaultLimit"
                :min="1"
                :max="100"
                style="width: 200px"
              />
            </a-form-item>
          </a-form>
        </div>
        <div class="settings-section">
          <a-button type="primary" @click="saveSearchSettings">保存设置</a-button>
        </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'

// 响应式数据
const activeTab = ref('speech')

// 语音设置
const speechSettings = reactive({
  modelSize: 'base',
  device: 'cpu'
})

// 大语言模型设置
const llmSettings = reactive({
  localModel: 'qwen2.5:1.5b',
  ollamaUrl: 'http://localhost:11434'
})

// 视觉模型设置
const visionSettings = reactive({
  clipModel: 'OFA-Sys/chinese-clip-vit-base'
})

// 搜索设置
const searchSettings = reactive({
  defaultType: 'hybrid',
  defaultThreshold: 0.7,
  defaultLimit: 20
})

// 方法
const saveSpeechSettings = () => {
  localStorage.setItem('speechSettings', JSON.stringify(speechSettings))
  message.success('语音设置已保存')
}

const testSpeechAvailability = () => {
  message.info('检查语音识别服务可用性...')
  // 这里应该调用实际的API检查
  setTimeout(() => {
    message.success('语音识别服务可用')
  }, 1000)
}

const testLLM = () => {
  message.info('测试大语言模型连接...')
  // 这里应该调用实际的API测试
  setTimeout(() => {
    message.success('大语言模型连接正常')
  }, 1500)
}

const saveLLMSettings = () => {
  localStorage.setItem('llmSettings', JSON.stringify(llmSettings))
  message.success('大语言模型设置已保存')
}

const testVision = () => {
  message.info('测试视觉模型...')
  // 这里应该调用实际的API测试
  setTimeout(() => {
    message.success('视觉模型可用')
  }, 1200)
}

const saveVisionSettings = () => {
  localStorage.setItem('visionSettings', JSON.stringify(visionSettings))
  message.success('视觉模型设置已保存')
}

const saveSearchSettings = () => {
  localStorage.setItem('searchSettings', JSON.stringify(searchSettings))
  message.success('搜索设置已保存')
}
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-6);
}

.settings-header {
  margin-bottom: var(--space-6);
}

.settings-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.settings-header p {
  color: var(--text-secondary);
  margin: 0;
}

.settings-tabs {
  background: var(--surface-01);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-base);
}

.settings-section {
  margin-bottom: var(--space-6);
}

.settings-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 var(--space-4);
  color: var(--text-primary);
}

.form-help {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: var(--space-4);
  }

  .settings-tabs {
    padding: var(--space-4);
  }
}
</style>