<template>
  <div class="settings-page">
    <div class="settings-container">
      <div class="settings-header">
        <h1 class="settings-title">设置</h1>
        <p class="settings-description">配置小遥搜索的各项参数和偏好设置</p>
      </div>

      <div class="settings-content">
        <a-row :gutter="[24, 24]">
          <a-col :xs="24" :lg="16">
            <!-- AI模型设置 -->
            <div class="settings-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="bulb" />
                  AI模型配置
                </h2>
                <p class="section-description">选择和配置用于搜索的AI模型</p>
              </div>
              <div class="section-content">
                <a-card class="settings-card">
                  <a-form layout="vertical">
                    <a-form-item label="文本嵌入模型">
                      <a-select
                        v-model:value="settings.embeddingModel"
                        placeholder="选择文本嵌入模型"
                      >
                        <a-select-option value="bge-m3">BGE-M3 (推荐)</a-select-option>
                        <a-select-option value="text-embedding-ada-002">OpenAI Ada-002</a-select-option>
                        <a-select-option value="sentence-transformers">Sentence Transformers</a-select-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="语音识别模型">
                      <a-select
                        v-model:value="settings.speechModel"
                        placeholder="选择语音识别模型"
                      >
                        <a-select-option value="fast-whisper">Fast Whisper (本地)</a-select-option>
                        <a-select-option value="whisper-openai">OpenAI Whisper</a-select-option>
                        <a-select-option value="aliyun-asr">阿里云语音识别</a-select-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="图像理解模型">
                      <a-select
                        v-model:value="settings.visionModel"
                        placeholder="选择图像理解模型"
                      >
                        <a-select-option value="cn-clip">CN-CLIP (推荐)</a-select-option>
                        <a-select-option value="openai-clip">OpenAI CLIP</a-select-option>
                        <a-select-option value="aliyun-vision">阿里云视觉理解</a-select-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="大语言模型">
                      <a-select
                        v-model:value="settings.llmModel"
                        placeholder="选择大语言模型"
                      >
                        <a-select-option value="qwen2.5">Qwen2.5 (本地Ollama)</a-select-option>
                        <a-select-option value="gpt-4">OpenAI GPT-4</a-select-option>
                        <a-select-option value="claude-3">Anthropic Claude-3</a-select-option>
                        <a-select-option value="gemini-pro">Google Gemini Pro</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-form>
                </a-card>
              </div>
            </div>

            <!-- 搜索设置 -->
            <div class="settings-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="search" />
                  搜索配置
                </h2>
                <p class="section-description">调整搜索行为和结果展示</p>
              </div>
              <div class="section-content">
                <a-card class="settings-card">
                  <a-form layout="vertical">
                    <a-row :gutter="16">
                      <a-col :span="12">
                        <a-form-item label="默认搜索类型">
                          <a-select v-model:value="settings.searchType">
                            <a-select-option value="hybrid">混合搜索 (推荐)</a-select-option>
                            <a-select-option value="semantic">语义搜索</a-select-option>
                            <a-select-option value="fulltext">全文搜索</a-select-option>
                          </a-select>
                        </a-form-item>
                      </a-col>
                      <a-col :span="12">
                        <a-form-item label="相似度阈值">
                          <a-slider
                            v-model:value="settings.threshold"
                            :min="0.1"
                            :max="1.0"
                            :step="0.1"
                            :marks="{ 0.1: '0.1', 0.5: '0.5', 1.0: '1.0' }"
                          />
                        </a-form-item>
                      </a-col>
                    </a-row>
                    <a-row :gutter="16">
                      <a-col :span="12">
                        <a-form-item label="结果数量限制">
                          <a-input-number
                            v-model:value="settings.resultLimit"
                            :min="10"
                            :max="100"
                            style="width: 100%"
                          />
                        </a-form-item>
                      </a-col>
                      <a-col :span="12">
                        <a-form-item label="搜索超时时间(秒)">
                          <a-input-number
                            v-model:value="settings.searchTimeout"
                            :min="5"
                            :max="60"
                            style="width: 100%"
                          />
                        </a-form-item>
                      </a-col>
                    </a-row>
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.enableAutoSuggest">
                        启用搜索建议
                      </a-checkbox>
                    </a-form-item>
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.saveSearchHistory">
                        保存搜索历史
                      </a-checkbox>
                    </a-form-item>
                  </a-form>
                </a-card>
              </div>
            </div>
          </a-col>

          <a-col :xs="24" :lg="8">
            <!-- 界面设置 -->
            <div class="settings-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="theme" />
                  界面设置
                </h2>
                <p class="section-description">自定义界面外观和体验</p>
              </div>
              <div class="section-content">
                <a-card class="settings-card">
                  <a-form layout="vertical">
                    <a-form-item label="主题模式">
                      <a-radio-group v-model:value="settings.theme" button-style="solid">
                        <a-radio-button value="dark">
                          <SimpleIcon type="moon" /> 深色
                        </a-radio-button>
                        <a-radio-button value="light">
                          <SimpleIcon type="sun" /> 浅色
                        </a-radio-button>
                      </a-radio-group>
                    </a-form-item>
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.enableAnimations">
                        启用动画效果
                      </a-checkbox>
                    </a-form-item>
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.enableSoundEffects">
                        启用音效
                      </a-checkbox>
                    </a-form-item>
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.compactMode">
                        紧凑模式
                      </a-checkbox>
                    </a-form-item>
                    <a-form-item label="语言">
                      <a-select v-model:value="settings.language">
                        <a-select-option value="zh-CN">简体中文</a-select-option>
                        <a-select-option value="en-US">English</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-form>
                </a-card>
              </div>
            </div>

            <!-- 高级设置 -->
            <div class="settings-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="settings" />
                  高级设置
                </h2>
                <p class="section-description">开发者选项和实验性功能</p>
              </div>
              <div class="section-content">
                <a-card class="settings-card">
                  <a-form layout="vertical">
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.debugMode">
                        调试模式
                      </a-checkbox>
                    </a-form-item>
                    <a-form-item>
                      <a-checkbox v-model:checked="settings.enableBeta">
                        启用测试版功能
                      </a-checkbox>
                    </a-form-item>
                    <a-form-item label="日志级别">
                      <a-select v-model:value="settings.logLevel">
                        <a-select-option value="error">仅错误</a-select-option>
                        <a-select-option value="warn">警告及以上</a-select-option>
                        <a-select-option value="info">信息及以上</a-select-option>
                        <a-select-option value="debug">调试模式</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-form>
                </a-card>
              </div>
            </div>
          </a-col>
        </a-row>
      </div>

      <!-- 操作按钮 -->
      <div class="settings-actions">
        <a-space>
          <a-button type="primary" size="large" @click="handleSave">
            <SimpleIcon type="save" />
            保存设置
          </a-button>
          <a-button size="large" @click="handleReset">
            <SimpleIcon type="refresh" />
            重置默认
          </a-button>
          <a-button size="large" @click="handleExport">
            <SimpleIcon type="download" />
            导出配置
          </a-button>
          <a-button size="large" @click="handleImport">
            <SimpleIcon type="upload" />
            导入配置
          </a-button>
        </a-space>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'
import SimpleIcon from '@/components/SimpleIcon.vue'

// 设置数据
const settings = reactive({
  // AI模型
  embeddingModel: 'bge-m3',
  speechModel: 'fast-whisper',
  visionModel: 'cn-clip',
  llmModel: 'qwen2.5',

  // 搜索配置
  searchType: 'hybrid',
  threshold: 0.7,
  resultLimit: 20,
  searchTimeout: 30,
  enableAutoSuggest: true,
  saveSearchHistory: true,

  // 界面设置
  theme: 'dark',
  enableAnimations: true,
  enableSoundEffects: true,
  compactMode: false,
  language: 'zh-CN',

  // 高级设置
  debugMode: false,
  enableBeta: false,
  logLevel: 'info'
})

// 事件处理
const handleSave = () => {
  // 这里保存设置到本地存储或后端
  localStorage.setItem('xiaoyao-search-settings', JSON.stringify(settings))
  message.success('设置已保存')
}

const handleReset = () => {
  // 重置为默认设置
  Object.assign(settings, {
    embeddingModel: 'bge-m3',
    speechModel: 'fast-whisper',
    visionModel: 'cn-clip',
    llmModel: 'qwen2.5',
    searchType: 'hybrid',
    threshold: 0.7,
    resultLimit: 20,
    searchTimeout: 30,
    enableAutoSuggest: true,
    saveSearchHistory: true,
    theme: 'dark',
    enableAnimations: true,
    enableSoundEffects: true,
    compactMode: false,
    language: 'zh-CN',
    debugMode: false,
    enableBeta: false,
    logLevel: 'info'
  })
  message.info('设置已重置为默认值')
}

const handleExport = () => {
  const dataStr = JSON.stringify(settings, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'xiaoyao-search-settings.json'
  link.click()
  URL.revokeObjectURL(url)
  message.success('配置已导出')
}

const handleImport = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target?.result as string)
          Object.assign(settings, importedSettings)
          message.success('配置已导入')
        } catch (error) {
          message.error('配置文件格式错误')
        }
      }
      reader.readAsText(file)
    }
  }
  input.click()
}
</script>

<style lang="scss" scoped>
.settings-page {
  min-height: 100vh;
  padding: var(--space-6);
  background: var(--surface-primary);
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}

.settings-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.settings-title {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-3);
  font-family: var(--font-display);
}

.settings-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.settings-content {
  margin-bottom: var(--space-8);
}

.settings-section {
  margin-bottom: var(--space-6);
}

.section-header {
  margin-bottom: var(--space-4);
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-2);

  .anticon {
    color: var(--accent-cyan);
  }
}

.section-description {
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: 1.5;
}

.settings-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);

  @include glass-morphism;

  :deep(.ant-card-body) {
    padding: var(--space-6);
  }

  :deep(.ant-form-item-label > label) {
    color: var(--text-secondary);
    font-weight: 500;
  }

  :deep(.ant-input),
  :deep(.ant-select-selector),
  :deep(.ant-input-number) {
    background: var(--surface-tertiary);
    border-color: var(--border-medium);
    color: var(--text-primary);

    &:hover {
      border-color: var(--accent-cyan);
    }

    &:focus,
    &.ant-select-focused .ant-select-selector {
      border-color: var(--accent-cyan);
      box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.2);
    }
  }

  :deep(.ant-slider) {
    .ant-slider-rail {
      background: var(--border-light);
    }

    .ant-slider-track {
      background: var(--accent-cyan);
    }

    .ant-slider-handle {
      border-color: var(--accent-cyan);
    }
  }

  :deep(.ant-checkbox-wrapper) {
    color: var(--text-secondary);

    .ant-checkbox-checked .ant-checkbox-inner {
      background-color: var(--accent-cyan);
      border-color: var(--accent-cyan);
    }
  }
}

.settings-actions {
  display: flex;
  justify-content: center;
  padding: var(--space-6);
  background: var(--surface-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);

  @include glass-morphism;
}

// 响应式设计
@media (max-width: 768px) {
  .settings-page {
    padding: var(--space-4);
  }

  .settings-title {
    font-size: var(--text-3xl);
  }

  .settings-description {
    font-size: var(--text-base);
  }

  .settings-card :deep(.ant-card-body) {
    padding: var(--space-4);
  }

  .settings-actions {
    padding: var(--space-4);
  }

  .settings-actions :deep(.ant-space) {
    flex-direction: column;
    width: 100%;

    .ant-btn {
      width: 100%;
    }
  }
}

@media (max-width: 480px) {
  .section-title {
    font-size: var(--text-xl);
  }

  .settings-card :deep(.ant-form-item) {
    margin-bottom: var(--space-3);
  }
}
</style>