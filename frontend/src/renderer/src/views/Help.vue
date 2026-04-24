<template>
  <div class="help-container">
    <div class="help-header">
      <h2>{{ t('help.title') }}</h2>
      <p>{{ t('help.subtitle') }}</p>
    </div>

    <a-tabs v-model:activeKey="activeTab" type="card" class="help-tabs">
      <!-- 快速入门 -->
      <a-tab-pane key="guide" :tab="t('help.tabGuide')">
        <div class="guide-section">
          <div class="guide-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>{{ t('help.guide.step1.title') }}</h3>
              <p>{{ t('help.guide.step1.description') }}</p>
              <a-button type="primary">{{ t('help.guide.step1.button') }}</a-button>
            </div>
          </div>

          <div class="guide-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>{{ t('help.guide.step2.title') }}</h3>
              <p>{{ t('help.guide.step2.description') }}</p>
              <a-button type="primary">{{ t('help.guide.step2.button') }}</a-button>
            </div>
          </div>

          <div class="guide-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>{{ t('help.guide.step3.title') }}</h3>
              <p>{{ t('help.guide.step3.description') }}</p>
              <a-button type="primary">{{ t('help.guide.step3.button') }}</a-button>
            </div>
          </div>
        </div>

        <div class="feature-highlights">
          <h3>{{ t('help.features.title') }}</h3>
          <a-row :gutter="16">
            <a-col :span="8">
              <a-card class="feature-card">
                <template #cover>
                  <div class="feature-icon">
                    <AudioOutlined />
                  </div>
                </template>
                <a-card-meta :title="t('help.features.voice.title')" :description="t('help.features.voice.description')" />
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card class="feature-card">
                <template #cover>
                  <div class="feature-icon">
                    <PictureOutlined />
                  </div>
                </template>
                <a-card-meta :title="t('help.features.image.title')" :description="t('help.features.image.description')" />
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card class="feature-card">
                <template #cover>
                  <div class="feature-icon">
                    <RobotOutlined />
                  </div>
                </template>
                <a-card-meta :title="t('help.features.semantic.title')" :description="t('help.features.semantic.description')" />
              </a-card>
            </a-col>
          </a-row>
        </div>
      </a-tab-pane>

      <!-- 使用教程 -->
      <a-tab-pane key="tutorial" :tab="t('help.tabTutorial')">
        <div class="tutorial-section">
          <a-collapse v-model:activeKey="tutorialActiveKeys" :bordered="false">
            <a-collapse-panel key="1" :header="t('help.tutorial.panel1.header')">
              <div class="tutorial-content">
                <h4>{{ t('help.tutorial.panel1.content.stepsTitle') }}</h4>
                <ol>
                  <li><strong>{{ t('help.tutorial.panel1.content.step1.label') }}</strong>{{ t('help.tutorial.panel1.content.step1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel1.content.step2.label') }}</strong>{{ t('help.tutorial.panel1.content.step2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel1.content.step3.label') }}</strong>{{ t('help.tutorial.panel1.content.step3.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel1.content.step4.label') }}</strong>{{ t('help.tutorial.panel1.content.step4.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel1.content.step5.label') }}</strong>{{ t('help.tutorial.panel1.content.step5.text') }}</li>
                </ol>
                <div class="tip-box">
                  <BulbOutlined />
                  <span>{{ t('help.tutorial.panel1.content.tip') }}</span>
                </div>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="2" :header="t('help.tutorial.panel2.header')">
              <div class="tutorial-content">
                <h4>{{ t('help.tutorial.panel2.content.modesTitle') }}</h4>
                <ul>
                  <li><strong>{{ t('help.tutorial.panel2.content.mode1.label') }}</strong>{{ t('help.tutorial.panel2.content.mode1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel2.content.mode2.label') }}</strong>{{ t('help.tutorial.panel2.content.mode2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel2.content.mode3.label') }}</strong>{{ t('help.tutorial.panel2.content.mode3.text') }}</li>
                </ul>
                <h4>{{ t('help.tutorial.panel2.content.fileTypesTitle') }}</h4>
                <ul>
                  <li><strong>{{ t('help.tutorial.panel2.content.fileType1.label') }}</strong>{{ t('help.tutorial.panel2.content.fileType1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel2.content.fileType2.label') }}</strong>{{ t('help.tutorial.panel2.content.fileType2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel2.content.fileType3.label') }}</strong>{{ t('help.tutorial.panel2.content.fileType3.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel2.content.fileType4.label') }}</strong>{{ t('help.tutorial.panel2.content.fileType4.text') }}</li>
                </ul>
              </div>
              <div class="tip-box">
                  <BulbOutlined />
                  <span>{{ t('help.tutorial.panel2.content.note') }}</span>
                </div>
            </a-collapse-panel>

            <a-collapse-panel key="3" :header="t('help.tutorial.panel3.header')">
              <div class="tutorial-content">
                <h4>{{ t('help.tutorial.panel3.content.guideTitle') }}</h4>
                <ul>
                  <li><strong>{{ t('help.tutorial.panel3.content.guide1.label') }}</strong>{{ t('help.tutorial.panel3.content.guide1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel3.content.guide2.label') }}</strong>{{ t('help.tutorial.panel3.content.guide2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel3.content.guide3.label') }}</strong>{{ t('help.tutorial.panel3.content.guide3.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel3.content.guide4.label') }}</strong>{{ t('help.tutorial.panel3.content.guide4.text') }}</li>
                </ul>
                <h4>{{ t('help.tutorial.panel3.content.statusTitle') }}</h4>
                <ul>
                  <li><strong>{{ t('help.tutorial.panel3.content.status1.label') }}</strong>{{ t('help.tutorial.panel3.content.status1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel3.content.status2.label') }}</strong>{{ t('help.tutorial.panel3.content.status2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel3.content.status3.label') }}</strong>{{ t('help.tutorial.panel3.content.status3.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel3.content.status4.label') }}</strong>{{ t('help.tutorial.panel3.content.status4.text') }}</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="4" :header="t('help.tutorial.panel4.header')">
              <div class="tutorial-content">
                <h4>{{ t('help.tutorial.panel4.content.tipsTitle') }}</h4>
                <ul>
                  <li><strong>{{ t('help.tutorial.panel4.content.tip1.label') }}</strong>{{ t('help.tutorial.panel4.content.tip1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel4.content.tip2.label') }}</strong>{{ t('help.tutorial.panel4.content.tip2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel4.content.tip3.label') }}</strong>{{ t('help.tutorial.panel4.content.tip3.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel4.content.tip4.label') }}</strong>{{ t('help.tutorial.panel4.content.tip4.text') }}</li>
                </ul>
                <h4>{{ t('help.tutorial.panel4.content.resultsTitle') }}</h4>
                <ul>
                  <li><strong>{{ t('help.tutorial.panel4.content.result1.label') }}</strong>{{ t('help.tutorial.panel4.content.result1.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel4.content.result2.label') }}</strong>{{ t('help.tutorial.panel4.content.result2.text') }}</li>
                  <li><strong>{{ t('help.tutorial.panel4.content.result3.label') }}</strong>{{ t('help.tutorial.panel4.content.result3.text') }}</li>
                </ul>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </div>
      </a-tab-pane>

      <!-- 常见问题 -->
      <a-tab-pane key="faq" :tab="t('help.tabFaq')">
        <div class="faq-section">
          <a-collapse v-model:activeKey="faqActiveKeys" :bordered="false">
            <a-collapse-panel key="1" :header="t('help.faq.panel1.header')">
              <div class="faq-content">
                <p><strong>{{ t('help.faq.panel1.content.causesTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel1.content.cause1') }}</li>
                  <li>{{ t('help.faq.panel1.content.cause2') }}</li>
                  <li>{{ t('help.faq.panel1.content.cause3') }}</li>
                  <li>{{ t('help.faq.panel1.content.cause4') }}</li>
                </ul>
                <p><strong>{{ t('help.faq.panel1.content.solutionsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel1.content.solution1') }}</li>
                  <li>{{ t('help.faq.panel1.content.solution2') }}</li>
                  <li>{{ t('help.faq.panel1.content.solution3') }}</li>
                  <li>{{ t('help.faq.panel1.content.solution4') }}</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="2" :header="t('help.faq.panel2.header')">
              <div class="faq-content">
                <!-- 本地 Ollama 服务 -->
                <p><strong>{{ t('help.faq.panel2.content.ollamaTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel2.content.ollama1') }}</li>
                  <li>{{ t('help.faq.panel2.content.ollama2') }}</li>
                  <li>{{ t('help.faq.panel2.content.ollama3') }}</li>
                  <li>{{ t('help.faq.panel2.content.ollama4') }}</li>
                </ul>
                <p><strong>{{ t('help.faq.panel2.content.ollamaCommandsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel2.content.ollamaCommand1') }}<code>ollama pull qwen2.5:1.5b</code></li>
                  <li>{{ t('help.faq.panel2.content.ollamaCommand2') }}<code>ollama list</code></li>
                  <li>{{ t('help.faq.panel2.content.ollamaCommand3') }}<code>ollama run qwen2.5:1.5b</code></li>
                </ul>

                <!-- 云端大模型服务 -->
                <p><strong>{{ t('help.faq.panel2.content.cloudLlmTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel2.content.cloudLlm1') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudLlm2') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudLlm3') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudLlm4') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudLlm5') }}</li>
                </ul>

                <!-- 云端嵌入模型服务 -->
                <p><strong>{{ t('help.faq.panel2.content.cloudEmbeddingTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel2.content.cloudEmbedding1') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudEmbedding2') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudEmbedding3') }}</li>
                  <li>{{ t('help.faq.panel2.content.cloudEmbedding4') }}</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="3" :header="t('help.faq.panel3.header')">
              <div class="faq-content">
                <p><strong>{{ t('help.faq.panel3.content.reasonsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel3.content.reason1') }}</li>
                  <li>{{ t('help.faq.panel3.content.reason2') }}</li>
                  <li>{{ t('help.faq.panel3.content.reason3') }}</li>
                  <li>{{ t('help.faq.panel3.content.reason4') }}</li>
                </ul>
                <p><strong>{{ t('help.faq.panel3.content.tipsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel3.content.tip1') }}</li>
                  <li>{{ t('help.faq.panel3.content.tip2') }}</li>
                  <li>{{ t('help.faq.panel3.content.tip3') }}</li>
                  <li>{{ t('help.faq.panel3.content.tip4') }}</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="4" :header="t('help.faq.panel4.header')">
              <div class="faq-content">
                <p><strong>{{ t('help.faq.panel4.content.factorsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel4.content.factor1') }}</li>
                  <li>{{ t('help.faq.panel4.content.factor2') }}</li>
                  <li>{{ t('help.faq.panel4.content.factor3') }}</li>
                  <li>{{ t('help.faq.panel4.content.factor4') }}</li>
                </ul>
                <p><strong>{{ t('help.faq.panel4.content.methodsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel4.content.method1') }}</li>
                  <li>{{ t('help.faq.panel4.content.method2') }}</li>
                  <li>{{ t('help.faq.panel4.content.method3') }}</li>
                  <li>{{ t('help.faq.panel4.content.method4') }}</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="5" :header="t('help.faq.panel5.header')">
              <div class="faq-content">
                <p><strong>{{ t('help.faq.panel5.content.improvementsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel5.content.improvement1') }}</li>
                  <li>{{ t('help.faq.panel5.content.improvement2') }}</li>
                  <li>{{ t('help.faq.panel5.content.improvement3') }}</li>
                  <li>{{ t('help.faq.panel5.content.improvement4') }}</li>
                  <li>{{ t('help.faq.panel5.content.improvement5') }}</li>
                </ul>
                <p><strong>{{ t('help.faq.panel5.content.advancedTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel5.content.advanced1') }}</li>
                  <li>{{ t('help.faq.panel5.content.advanced2') }}</li>
                  <li>{{ t('help.faq.panel5.content.advanced3') }}</li>
                </ul>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </div>
      </a-tab-pane>

      <!-- 关于 -->
      <a-tab-pane key="about" :tab="t('help.tabAbout')">
        <div class="about-section">
          <!-- 应用介绍 -->
          <div class="about-header">
            <div class="app-logo">
              <span class="logo-text">{{ t('app.name') }}</span>
            </div>
            <img src="@/assets/images/icon.png" width="256" height="256" />
            <p class="app-description">
              {{ t('help.about.appDescription') }}
            </p>
            <div class="tagline">
              <span class="highlight">{{ t('help.about.tagline') }}</span>
            </div>
          </div>

          <!-- 核心特性 -->
          <div class="features-showcase">
            <a-row :gutter="24">
              <a-col :span="8">
                <div class="feature-block">
                  <div class="feature-icon">
                    <AudioOutlined />
                  </div>
                  <h4>{{ t('help.about.features.voice.title') }}</h4>
                  <p>{{ t('help.about.features.voice.description') }}</p>
                </div>
              </a-col>
              <a-col :span="8">
                <div class="feature-block">
                  <div class="feature-icon">
                    <PictureOutlined />
                  </div>
                  <h4>{{ t('help.about.features.image.title') }}</h4>
                  <p>{{ t('help.about.features.image.description') }}</p>
                </div>
              </a-col>
              <a-col :span="8">
                <div class="feature-block">
                  <div class="feature-icon">
                    <RobotOutlined />
                  </div>
                  <h4>{{ t('help.about.features.semantic.title') }}</h4>
                  <p>{{ t('help.about.features.semantic.description') }}</p>
                </div>
              </a-col>
            </a-row>
          </div>

          <!-- 技术特色 -->
          <div class="tech-highlight">
            <a-card class="highlight-card">
              <h4>{{ t('help.about.techHighlight.title') }}</h4>
              <p>{{ t('help.about.techHighlight.description') }}</p>
              <div class="tech-tags">
                <a-tag color="blue">FastWhisper</a-tag>
                <a-tag color="green">Ollama</a-tag>
                <a-tag color="orange">CN-CLIP</a-tag>
                <a-tag color="purple">BGE-M3</a-tag>
                <a-tag color="cyan">OpenAI API</a-tag>
                <a-tag color="magenta">Cloud Embedding</a-tag>
                <a-tag color="volcano">MCP & Agent Skills</a-tag>
              </div>
            </a-card>
          </div>

          </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  AudioOutlined,
  PictureOutlined,
  RobotOutlined,
  BulbOutlined
} from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'

// 国际化
const { t } = useI18n()

// 响应式数据
const activeTab = ref('guide')
const tutorialActiveKeys = ref(['1'])
const faqActiveKeys = ref(['1'])
</script>

<style scoped>
.help-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--space-xl);
}

.help-header {
  text-align: center;
  margin-bottom: var(--space-3xl);
}

.help-header h2 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-2xl);
  letter-spacing: -0.25px;
  color: var(--text-primary);
  margin: 0 0 var(--space-sm);
}

.help-header p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

.help-tabs {
  background: var(--bg-primary);
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

/* 快速入门样式 */
.guide-section {
  padding: var(--space-xl);
}

.guide-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: var(--space-3xl);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: var(--brand-blue);
  color: white;
  font-size: var(--text-2xl);
  font-weight: 600;
  border-radius: 50%;
  margin-right: var(--space-lg);
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-sm);
}

.step-content p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--space-md);
}

.feature-highlights {
  margin-top: var(--space-3xl);
  padding-top: var(--space-xl);
  border-top: var(--border-standard);
}

.feature-highlights h3 {
  text-align: center;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-xl);
  margin-bottom: var(--space-xl);
  color: var(--text-primary);
}

.feature-card {
  text-align: center;
  border-radius: var(--radius-xl);
  border: var(--border-standard);
  padding: var(--space-lg);
  background: var(--bg-primary);
  transition: all var(--transition-base);
}

.feature-card:hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-2px);
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
  background: var(--brand-blue-light);
  font-size: var(--text-2xl);
  color: var(--brand-blue);
  border-radius: var(--radius-lg);
}

/* 教程样式 */
.tutorial-section,
.faq-section {
  padding: var(--space-xl);
}

.tutorial-content,
.faq-content {
  color: var(--text-secondary);
  line-height: 1.6;
}

.tutorial-content h4,
.faq-content h4 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.tutorial-content ol,
.tutorial-content ul,
.faq-content ul {
  margin-bottom: var(--space-lg);
  padding-left: var(--space-xl);
}

.tutorial-content li,
.faq-content li {
  margin-bottom: var(--space-sm);
}

.tip-box {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background: var(--brand-blue-light);
  border-left: 4px solid var(--brand-blue);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
}

/* 关于样式 */
.about-section {
  padding: var(--space-xl);
}

.about-header {
  text-align: center;
  margin-bottom: var(--space-3xl);
}

.app-logo {
  margin-bottom: var(--space-lg);
}

.logo-text {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--brand-blue);
}

.about-header h3 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: var(--space-sm) 0 var(--space-md);
  color: var(--text-primary);
  font-size: var(--text-xl);
}

.app-description {
  max-width: 600px;
  margin: 0 auto var(--space-lg);
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: var(--text-base);
}

.tagline {
  margin-top: var(--space-lg);
}

.highlight {
  color: var(--brand-blue);
  font-weight: 600;
  font-size: var(--text-lg);
  letter-spacing: 0.25px;
}

/* 核心特性展示 */
.features-showcase {
  margin-bottom: var(--space-3xl);
}

.feature-block {
  text-align: center;
  padding: var(--space-xl);
  border-radius: var(--radius-xl);
  border: var(--border-standard);
  background: var(--bg-primary);
  transition: all var(--transition-base);
}

.feature-block:hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-4px);
}

.feature-block .feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-lg);
  background: var(--brand-blue-light);
  border-radius: 50%;
  font-size: var(--text-2xl);
  color: var(--brand-blue);
}

.feature-block h4 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: 0 0 var(--space-sm);
  color: var(--text-primary);
  font-size: var(--text-lg);
}

.feature-block p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
}

/* 技术特色 */
.tech-highlight {
  margin-bottom: var(--space-3xl);
}

.highlight-card {
  border-radius: var(--radius-xl);
  border: var(--border-standard);
  text-align: center;
  background: var(--bg-secondary);
  padding: var(--space-xl);
}

.highlight-card h4 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: 0 0 var(--space-md);
  color: var(--brand-blue);
  font-size: var(--text-xl);
}

.highlight-card p {
  margin: 0 0 var(--space-lg);
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: var(--text-base);
}

.tech-tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

/* 作者信息 */
.author-section {
  margin-bottom: var(--space-3xl);
}

.author-card {
  border-radius: var(--radius-xl);
  border: var(--border-standard);
  background: var(--bg-primary);
  padding: var(--space-xl);
}

.author-content {
  display: flex;
  align-items: flex-start;
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.author-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: var(--border-standard);
  background: var(--bg-secondary);
}

.avatar-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: var(--brand-blue-light);
  border: var(--border-standard);
  border-radius: 50%;
  font-size: var(--text-2xl);
  color: var(--brand-blue);
}

.author-info {
  flex: 1;
}

.author-info h4 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: 0 0 var(--space-sm);
  color: var(--text-primary);
  font-size: var(--text-lg);
}

.author-info p {
  margin: 0 0 var(--space-md);
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: var(--text-base);
}

.author-vision {
  padding-top: var(--space-sm);
  border-top: var(--border-standard);
}

.author-vision strong {
  color: var(--text-primary);
  font-weight: 600;
}

.author-vision span {
  color: var(--brand-blue);
  font-style: italic;
}

.brand-mission {
  padding-top: var(--space-sm);
  margin-top: var(--space-sm);
}

.brand-mission strong {
  color: var(--text-primary);
  font-weight: 600;
}

.brand-mission span {
  color: var(--accent-purple);
  font-weight: 500;
}

.author-links {
  padding-top: var(--space-lg);
  border-top: var(--border-standard);
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.contact-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg);
  background: var(--bg-secondary);
  border: var(--border-standard);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
}

.contact-item:hover {
  box-shadow: var(--shadow-elevated);
  transform: translateY(-2px);
}

.contact-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  flex: 1;
}

.contact-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--success-green);
  border-radius: 50%;
  color: white;
  font-size: var(--text-xl);
  flex-shrink: 0;
}

.contact-text h5 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: 0 0 var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-base);
}

.contact-text p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.qr-code {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.qr-image {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-lg);
  border: var(--border-standard);
  background: var(--bg-secondary);
  object-fit: cover;
}

.qr-hint {
  margin: 0;
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  text-align: center;
}

/* 二维码占位符 */
.qr-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-lg);
  border: var(--border-standard);
  background: var(--bg-secondary);
}

.qr-placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
}

.qr-placeholder-icon {
  font-size: var(--text-xl);
  color: var(--text-tertiary);
}

.qr-placeholder-text {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-align: center;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .help-container {
    padding: var(--space-lg);
  }

  .help-header h2 {
    font-size: var(--text-xl);
  }

  .guide-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .step-number {
    margin-right: 0;
    margin-bottom: var(--space-md);
  }

  .author-content {
    flex-direction: column;
    text-align: center;
  }

  .contact-item {
    flex-direction: column;
    text-align: center;
    gap: var(--space-md);
  }

  .features-showcase .ant-col {
    margin-bottom: var(--space-lg);
  }

  .feature-block {
    padding: var(--space-lg);
  }

  .feature-block .feature-icon {
    width: 60px;
    height: 60px;
    font-size: var(--text-xl);
  }

  .version-info {
    font-size: var(--text-sm);
  }

  .separator {
    margin: 0 var(--space-xs);
  }
}
</style>