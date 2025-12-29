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
                <a-select value="tiny">Tiny (最快)</a-select>
                <a-select value="base">Base (快速)</a-select>
                <a-select value="small">Small (平衡)</a-select>
                <a-select value="medium">Medium (精确)</a-select>
                <a-select value="large">Large (高精度)</a-select>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="speechSettings.device" style="width: 200px">
                <a-select value="cpu">CPU</a-select>
                <a-select value="cuda">CUDA (GPU)</a-select>
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
                <a-select value="OFA-Sys/chinese-clip-vit-base">ViT-Base (快速)</a-select>
                <a-select value="OFA-Sys/chinese-clip-vit-large">ViT-Large (高精度)</a-select>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="visionSettings.device" style="width: 200px">
                <a-select value="cpu">CPU</a-select>
                <a-select value="cuda">CUDA (GPU)</a-select>
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
                <a-select value="BAAI/bge-m3">BGE-M3 (多语言)</a-select>
                <a-select value="BAAI/bge-large-zh-v1.5">BGE-Large-zh</a-select>
                <a-select value="BAAI/bge-small-zh-v1.5">BGE-Small-zh</a-select>
              </a-select>
            </a-form-item>
            <a-form-item label="运行设备">
              <a-select v-model:value="embeddingSettings.device" style="width: 200px">
                <a-select value="cpu">CPU</a-select>
                <a-select value="cuda">CUDA (GPU)</a-select>
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
                :max="100"
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
import { ref, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'

// 响应式数据
const activeTab = ref('speech')

// 语音设置
const speechSettings = reactive({
  modelSize: 'small',
  device: 'cpu'
})

// 大语言模型设置
const llmSettings = reactive({
  localModel: 'qwen2.5:1.5b',
  ollamaUrl: 'http://localhost:11434'
})

// 视觉模型设置
const visionSettings = reactive({
  clipModel: 'OFA-Sys/chinese-clip-vit-base',
  device: 'cpu'
})

// 内嵌模型设置
const embeddingSettings = reactive({
  modelName: 'BAAI/bge-m3',
  device: 'cpu'
})

// 通用设置
const generalSettings = reactive({
  defaultResults: 20,
  threshold: 0.7,
  maxFileSize: 50
})

// 方法
const saveSpeechSettings = () => {
  message.success('语音设置已保存')
}

const testSpeechAvailability = () => {
  message.info('语音服务可用性检查功能开发中...')
}

const saveGeneralSettings = () => {
  message.success('通用设置已保存')
}

const resetSettings = () => {
  Modal.confirm({
    title: '确认重置',
    content: '确定要重置所有设置为默认值吗？',
    onOk() {
      message.success('设置已重置')
    }
  })
}

// 大语言模型方法
const testLLM = () => {
  message.info('LLM连接测试功能开发中...')
}

const saveLLMSettings = () => {
  message.success('大语言模型设置已保存')
}

// 视觉模型方法
const testVision = () => {
  message.info('视觉服务可用性检查功能开发中...')
}

const saveVisionSettings = () => {
  message.success('视觉模型设置已保存')
}

// 内嵌模型方法
const testEmbedding = () => {
  message.info('BGE模型可用性检查功能开发中...')
}

const saveEmbeddingSettings = () => {
  message.success('内嵌模型设置已保存')
}

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