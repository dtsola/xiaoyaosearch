<template>
  <div class="help-page">
    <div class="help-container">
      <div class="help-header">
        <h1 class="help-title">帮助与关于</h1>
        <p class="help-description">了解如何使用小遥搜索，获取帮助和技术支持</p>
      </div>

      <div class="help-content">
        <a-row :gutter="[24, 24]">
          <a-col :xs="24" :lg="16">
            <!-- 快速入门 -->
            <div class="help-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="bulb" />
                  快速入门
                </h2>
                <p class="section-description">3分钟上手小遥搜索</p>
              </div>
              <div class="section-content">
                <a-steps direction="vertical" size="small">
                  <a-step title="配置AI模型" description="在设置页面选择或配置AI模型，支持本地和云端模型" />
                  <a-step title="添加索引文件夹" description="在索引管理页面添加需要搜索的文件夹路径" />
                  <a-step title="开始搜索" description="使用语音、文本或图片进行搜索，查看智能搜索结果" />
                </a-steps>
              </div>
            </div>

            <!-- 功能教程 -->
            <div class="help-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="file" />
                  功能教程
                </h2>
                <p class="section-description">深入学习各项功能的使用方法</p>
              </div>
              <div class="section-content">
                <a-collapse v-model:activeKey="activeKey" accordion>
                  <a-collapse-panel key="1" header="多模态搜索使用指南">
                    <div class="tutorial-content">
                      <h4>🎤 语音搜索</h4>
                      <p>点击语音指示器开始录音，最长30秒。系统会自动将语音转换为文字并进行搜索。</p>

                      <h4>📝 文本搜索</h4>
                      <p>在搜索框中输入关键词，支持中英文混合搜索。可以使用引号进行精确匹配。</p>

                      <h4>📷 图片搜索</h4>
                      <p>上传图片进行视觉搜索，系统会分析图片内容并找到相关文件。</p>
                    </div>
                  </a-collapse-panel>

                  <a-collapse-panel key="2" header="索引管理详解">
                    <div class="tutorial-content">
                      <h4>创建索引</h4>
                      <p>选择要搜索的文件夹，系统会自动扫描并创建文件索引。</p>

                      <h4>索引更新</h4>
                      <p>当文件夹内容发生变化时，可以手动触发重新索引。</p>

                      <h4>索引优化</h4>
                      <p>定期优化索引以提高搜索性能和准确性。</p>
                    </div>
                  </a-collapse-panel>

                  <a-collapse-panel key="3" header="高级搜索技巧">
                    <div class="tutorial-content">
                      <h4>搜索语法</h4>
                      <ul>
                        <li>使用引号进行精确匹配：`"人工智能"`</li>
                        <li>使用AND/OR进行逻辑组合：`AI AND 机器学习`</li>
                        <li>使用减号排除关键词：`搜索 -测试`</li>
                      </ul>

                      <h4>过滤搜索</h4>
                      <p>可以按文件类型、大小、修改时间等条件过滤搜索结果。</p>
                    </div>
                  </a-collapse-panel>
                </a-collapse>
              </div>
            </div>
          </a-col>

          <a-col :xs="24" :lg="8">
            <!-- 快捷键 -->
            <div class="help-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="edit" />
                  快捷键
                </h2>
                <p class="section-description">提高搜索效率的快捷操作</p>
              </div>
              <div class="section-content">
                <div class="shortcut-list">
                  <div class="shortcut-item">
                    <kbd class="key">Ctrl</kbd> + <kbd class="key">K</kbd>
                    <span class="shortcut-desc">快速聚焦搜索框</span>
                  </div>
                  <div class="shortcut-item">
                    <kbd class="key">Enter</kbd>
                    <span class="shortcut-desc">执行搜索</span>
                  </div>
                  <div class="shortcut-item">
                    <kbd class="key">↑</kbd> / <kbd class="key">↓</kbd>
                    <span class="shortcut-desc">选择搜索建议</span>
                  </div>
                  <div class="shortcut-item">
                    <kbd class="key">Esc</kbd>
                    <span class="shortcut-desc">清空搜索</span>
                  </div>
                  <div class="shortcut-item">
                    <kbd class="key">Ctrl</kbd> + <kbd class="key">/</kbd>
                    <span class="shortcut-desc">显示快捷键帮助</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 常见问题 -->
            <div class="help-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="question" />
                  常见问题
                </h2>
                <p class="section-description">解答用户常见疑问</p>
              </div>
              <div class="section-content">
                <div class="faq-list">
                  <div class="faq-item" v-for="faq in faqs" :key="faq.id">
                    <div class="faq-question" @click="toggleFaq(faq.id)">
                      {{ faq.question }}
                      <SimpleIcon type="down" :class="{ 'expanded': faq.expanded }" />
                    </div>
                    <div class="faq-answer" v-show="faq.expanded">
                      {{ faq.answer }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 技术支持 -->
            <div class="help-section">
              <div class="section-header">
                <h2 class="section-title">
                  <SimpleIcon type="help" />
                  技术支持
                </h2>
                <p class="section-description">获取帮助和反馈问题</p>
              </div>
              <div class="section-content">
                <div class="support-options">
                  <div class="support-option">
                    <SimpleIcon type="copy" class="support-icon" />
                    <div class="support-info">
                      <h4>GitHub Issues</h4>
                      <p>提交问题和功能请求</p>
                      <a href="#" target="_blank">github.com/xiaoyao-search</a>
                    </div>
                  </div>
                  <div class="support-option">
                    <SimpleIcon type="copy" class="support-icon" />
                    <div class="support-info">
                      <h4>邮件支持</h4>
                      <p>发送邮件获取技术支持</p>
                      <a href="mailto:support@xiaoyao-search.com">support@xiaoyao-search.com</a>
                    </div>
                  </div>
                  <div class="support-option">
                    <SimpleIcon type="copy" class="support-icon" />
                    <div class="support-info">
                      <h4>微信交流群</h4>
                      <p>加入用户交流群</p>
                      <span>扫码加入微信群</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </a-col>
        </a-row>
      </div>

      <!-- 关于信息 -->
      <div class="about-section">
        <div class="section-header">
          <h2 class="section-title">
            <SimpleIcon type="info-circle" />
            关于小遥搜索
          </h2>
        </div>
        <div class="section-content">
          <div class="about-content">
            <div class="about-logo">
              <span class="logo-text">◤小遥搜索◢</span>
              <span class="version-badge">v2.0</span>
            </div>
            <div class="about-info">
              <p class="about-description">
                小遥搜索是一款支持多模态AI智能搜索的本地桌面应用，
                为知识工作者、内容创作者和技术开发者提供语音、文本、图像输入的智能文件检索能力。
              </p>
              <div class="about-details">
                <div class="detail-item">
                  <span class="detail-label">开发团队:</span>
                  <span class="detail-value">小遥搜索开发组</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">技术栈:</span>
                  <span class="detail-value">Vue 3 + Electron + FastAPI</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">开源协议:</span>
                  <span class="detail-value">MIT License</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">更新日期:</span>
                  <span class="detail-value">2024年11月24日</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import SimpleIcon from '@/components/SimpleIcon.vue'

const activeKey = ref(['1'])

// FAQ数据
const faqs = reactive([
  {
    id: 1,
    question: '如何提高搜索准确性？',
    answer: '可以通过调整相似度阈值、选择合适的搜索类型（语义/全文/混合）、确保索引文件夹内容完整等方式提高搜索准确性。',
    expanded: false
  },
  {
    id: 2,
    question: '支持哪些文件格式？',
    answer: '支持PDF、Word、Excel、PowerPoint、文本文件、Markdown、图片、音频、视频等多种格式。完整的支持列表请参考文档。',
    expanded: false
  },
  {
    id: 3,
    question: '如何备份数据？',
    answer: '应用数据主要存储在本地，可以定期备份索引文件和配置文件。备份路径通常在用户目录下的.xiaoyao-search文件夹中。',
    expanded: false
  },
  {
    id: 4,
    question: '语音识别准确率如何提升？',
    answer: '建议在安静环境中录音，说话清晰，使用高质量的麦克风。也可以尝试不同的语音识别模型来获得最佳效果。',
    expanded: false
  }
])

// 切换FAQ展开状态
const toggleFaq = (id: number) => {
  const faq = faqs.find(item => item.id === id)
  if (faq) {
    faq.expanded = !faq.expanded
  }
}
</script>

<style lang="scss" scoped>
.help-page {
  min-height: 100vh;
  padding: var(--space-6);
  background: var(--surface-primary);
}

.help-container {
  max-width: 1200px;
  margin: 0 auto;
}

.help-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.help-title {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-3);
  font-family: var(--font-display);
}

.help-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.help-content {
  margin-bottom: var(--space-8);
}

.help-section {
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  backdrop-filter: blur(10px);

  @include glass-morphism;
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

.section-content {
  color: var(--text-secondary);
}

// 快捷键样式
.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  border-radius: var(--radius-base);
  transition: background-color 0.3s var(--ease-out-cubic);

  &:hover {
    background: rgba(0, 229, 255, 0.05);
  }
}

.key {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  background: var(--surface-tertiary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--text-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.shortcut-desc {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

// FAQ样式
.faq-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.faq-item {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-base);
  overflow: hidden;
  transition: all 0.3s var(--ease-out-cubic);
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-tertiary);
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
  transition: all 0.3s var(--ease-out-cubic);

  &:hover {
    background: rgba(0, 229, 255, 0.1);
  }

  .anticon {
    transition: transform 0.3s var(--ease-out-cubic);

    &.expanded {
      transform: rotate(180deg);
    }
  }
}

.faq-answer {
  padding: var(--space-4);
  background: var(--surface-secondary);
  color: var(--text-secondary);
  line-height: 1.6;
}

// 技术支持样式
.support-options {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.support-option {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-base);
  transition: background-color 0.3s var(--ease-out-cubic);

  &:hover {
    background: rgba(0, 229, 255, 0.05);
  }
}

.support-icon {
  font-size: 20px;
  color: var(--accent-cyan);
  margin-top: 2px;
}

.support-info h4 {
  font-size: var(--text-base);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.support-info p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.support-info a,
.support-info span {
  font-size: var(--text-sm);
  color: var(--accent-cyan);
}

// 教程内容样式
.tutorial-content {
  color: var(--text-secondary);
  line-height: 1.6;

  h4 {
    color: var(--text-primary);
    margin: var(--space-3) 0 var(--space-2);
    font-size: var(--text-base);
  }

  p {
    margin-bottom: var(--space-3);
  }

  ul {
    padding-left: var(--space-4);
    margin-bottom: var(--space-3);

    li {
      margin-bottom: var(--space-1);
    }
  }
}

// 关于部分样式
.about-section {
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  backdrop-filter: blur(10px);

  @include glass-morphism;
}

.about-content {
  display: flex;
  gap: var(--space-8);
  align-items: flex-start;
}

.about-logo {
  flex-shrink: 0;
  text-align: center;
}

.logo-text {
  font-size: var(--text-4xl);
  font-weight: 900;
  font-family: var(--font-artistic);
  @include gradient-text;
  display: block;
  margin-bottom: var(--space-2);
}

.version-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  background: rgba(0, 229, 255, 0.2);
  color: var(--accent-cyan);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  font-family: var(--font-mono);
}

.about-info {
  flex: 1;
}

.about-description {
  font-size: var(--text-lg);
  line-height: 1.8;
  margin-bottom: var(--space-6);
  color: var(--text-secondary);
}

.about-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.detail-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-weight: 500;
}

.detail-value {
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: 500;
}

// 响应式设计
@media (max-width: 768px) {
  .help-page {
    padding: var(--space-4);
  }

  .help-section {
    padding: var(--space-4);
  }

  .about-content {
    flex-direction: column;
    gap: var(--space-4);
    align-items: center;
    text-align: center;
  }

  .about-details {
    grid-template-columns: 1fr;
  }

  .support-option {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .logo-text {
    font-size: var(--text-3xl);
  }
}
</style>