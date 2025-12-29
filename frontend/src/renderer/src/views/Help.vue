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
                <p><strong>{{ t('help.faq.panel2.content.checkTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel2.content.check1') }}</li>
                  <li>{{ t('help.faq.panel2.content.check2') }}</li>
                  <li>{{ t('help.faq.panel2.content.check3') }}</li>
                  <li>{{ t('help.faq.panel2.content.check4') }}</li>
                </ul>
                <p><strong>{{ t('help.faq.panel2.content.commandsTitle') }}</strong></p>
                <ul>
                  <li>{{ t('help.faq.panel2.content.command1') }}<code>ollama pull qwen2.5:1.5b</code></li>
                  <li>{{ t('help.faq.panel2.content.command2') }}<code>ollama list</code></li>
                  <li>{{ t('help.faq.panel2.content.command3') }}<code>ollama run qwen2.5:1.5b</code></li>
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
  padding: var(--space-6);
}

.help-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.help-header h2 {
  margin: 0 0 var(--space-3);
  color: var(--text-primary);
}

.help-header p {
  margin: 0;
  color: var(--text-secondary);
}

.help-tabs {
  background: var(--surface-01);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-base);
  overflow: hidden;
}

/* 快速入门样式 */
.guide-section {
  padding: var(--space-6);
}

.guide-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: var(--space-8);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  border-radius: 50%;
  margin-right: var(--space-6);
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.step-content p {
  margin: 0 0 var(--space-4);
  color: var(--text-secondary);
}

.feature-highlights {
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-light);
}

.feature-highlights h3 {
  text-align: center;
  margin-bottom: var(--space-6);
  color: var(--text-primary);
}

.feature-card {
  text-align: center;
  border-radius: var(--radius-lg);
  transition: transform var(--transition-base);
}

.feature-card:hover {
  transform: translateY(-2px);
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
  background: linear-gradient(135deg, var(--primary-50), var(--accent-light));
  font-size: 2rem;
  color: var(--primary-600);
}

/* 教程样式 */
.tutorial-section,
.faq-section {
  padding: var(--space-6);
}

.tutorial-content,
.faq-content {
  color: var(--text-secondary);
}

.tutorial-content h4,
.faq-content h4 {
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.tutorial-content ol,
.tutorial-content ul,
.faq-content ul {
  margin-bottom: var(--space-4);
  padding-left: var(--space-6);
}

.tutorial-content li,
.faq-content li {
  margin-bottom: var(--space-2);
}

.tip-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--warning-light);
  border-left: 4px solid var(--warning);
  border-radius: var(--radius-base);
  color: var(--warning-dark);
}

/* 关于样式 */
.about-section {
  padding: var(--space-6);
}

.about-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.app-logo {
  margin-bottom: var(--space-4);
}

.logo-text {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-600), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.about-header h3 {
  margin: var(--space-2) 0 var(--space-3);
  color: var(--text-primary);
  font-size: 1.5rem;
}

.app-description {
  max-width: 600px;
  margin: 0 auto var(--space-4);
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 1rem;
}

.tagline {
  margin-top: var(--space-4);
}

.highlight {
  background: linear-gradient(135deg, var(--primary-500), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
  font-size: 1.125rem;
  letter-spacing: 0.5px;
}

/* 核心特性展示 */
.features-showcase {
  margin-bottom: var(--space-8);
}

.feature-block {
  text-align: center;
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  transition: transform var(--transition-base);
}

.feature-block:hover {
  transform: translateY(-4px);
}

.feature-block .feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  background: linear-gradient(135deg, var(--primary-50), var(--accent-light));
  border-radius: 50%;
  font-size: 2rem;
  color: var(--primary-600);
}

.feature-block h4 {
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.feature-block p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* 技术特色 */
.tech-highlight {
  margin-bottom: var(--space-8);
}

.highlight-card {
  border-radius: var(--radius-lg);
  text-align: center;
  background: linear-gradient(135deg, var(--surface-01), var(--primary-50));
}

.highlight-card h4 {
  margin: 0 0 var(--space-3);
  color: var(--primary-600);
  font-size: 1.25rem;
  font-weight: 600;
}

.highlight-card p {
  margin: 0 0 var(--space-4);
  color: var(--text-secondary);
  line-height: 1.6;
}

.tech-tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* 作者信息 */
.author-section {
  margin-bottom: var(--space-8);
}

.author-card {
  border-radius: var(--radius-lg);
}

.author-content {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.author-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-light);
  background: var(--surface-01);
}

.avatar-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary-100), var(--accent-light));
  border-radius: 50%;
  font-size: 2rem;
}

.author-info {
  flex: 1;
}

.author-info h4 {
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.author-info p {
  margin: 0 0 var(--space-3);
  color: var(--text-secondary);
  line-height: 1.6;
}

.author-vision {
  padding-top: var(--space-2);
  border-top: 1px solid var(--border-light);
}

.author-vision strong {
  color: var(--text-primary);
}

.author-vision span {
  color: var(--primary-600);
  font-style: italic;
}

.brand-mission {
  padding-top: var(--space-2);
  margin-top: var(--space-2);
}

.brand-mission strong {
  color: var(--text-primary);
}

.brand-mission span {
  color: var(--accent-dark);
  font-weight: 500;
}

.author-links {
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.contact-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: var(--surface-02);
  border-radius: var(--radius-lg);
  transition: transform var(--transition-base);
}

.contact-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-base);
}

.contact-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
}

.contact-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #07c160, #00ae52);
  border-radius: 50%;
  color: white;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.contact-text h5 {
  margin: 0 0 var(--space-1);
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
}

.contact-text p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.qr-code {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.qr-image {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-base);
  border: 2px solid var(--border-light);
  background: var(--surface-01);
  object-fit: cover;
}

.qr-hint {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.75rem;
  text-align: center;
}

/* 二维码占位符 */
.qr-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-base);
  border: 2px dashed var(--border-light);
  background: var(--surface-01);
}

.qr-placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}

.qr-placeholder-icon {
  font-size: 1.5rem;
  color: var(--text-tertiary);
}

.qr-placeholder-text {
  font-size: 0.625rem;
  color: var(--text-tertiary);
  text-align: center;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .help-container {
    padding: var(--space-4);
  }

  .guide-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .step-number {
    margin-right: 0;
    margin-bottom: var(--space-4);
  }

  .author-content {
    flex-direction: column;
    text-align: center;
  }

  .contact-item {
    flex-direction: column;
    text-align: center;
    gap: var(--space-3);
  }

  .features-showcase .ant-col {
    margin-bottom: var(--space-4);
  }

  .feature-block {
    padding: var(--space-4);
  }

  .feature-block .feature-icon {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
  }

  .version-info {
    font-size: 0.875rem;
  }

  .separator {
    margin: 0 var(--space-1);
  }
}
</style>