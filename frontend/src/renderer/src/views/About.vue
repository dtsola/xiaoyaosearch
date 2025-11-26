<template>
  <div class="about-container">
    <div class="about-header">
      <div class="app-logo">
        <div class="logo-circle">
          <span class="logo-text">小遥搜索</span>
        </div>
        <div class="version-badge">v2.0</div>
      </div>
      <h1 class="app-title">小遥搜索 XiaoyaoSearch</h1>
      <p class="app-subtitle">多模态AI智能搜索桌面应用</p>
    </div>

    <!-- 产品介绍 -->
    <a-card class="feature-card" title="🎯 产品定位">
      <div class="feature-description">
        <p>
          小遥搜索是一款专为知识工作者、内容创作者和技术开发者设计的本地桌面应用。
          通过整合多种AI模型，提供语音、文本、图像的多模态智能搜索能力，让文件检索更加智能、高效、便捷。
        </p>
      </div>
    </a-card>

    <!-- 核心特性 -->
    <a-card class="feature-card" title="✨ 核心特性">
      <a-row :gutter="16">
        <a-col :span="12">
          <div class="feature-item">
            <div class="feature-icon">🔍</div>
            <h4>多模态智能搜索</h4>
            <p>支持语音输入（30秒内）、文本输入、图片输入，通过AI转换为语义进行搜索</p>
          </div>
        </a-col>
        <a-col :span="12">
          <div class="feature-item">
            <div class="feature-icon">📁</div>
            <h4>本地文件深度检索</h4>
            <p>支持视频、音频、文档的内容和文件名搜索，完全本地化，保护隐私</p>
          </div>
        </a-col>
        <a-col :span="12">
          <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <h4>灵活的AI模型配置</h4>
            <p>支持云端API和本地模型的自由切换，满足不同使用场景需求</p>
          </div>
        </a-col>
        <a-col :span="12">
          <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <h4>高性能搜索引擎</h4>
            <p>基于Faiss向量搜索和Whoosh全文搜索，实现毫秒级响应</p>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- 技术架构 -->
    <a-card class="feature-card" title="🏗️ 技术架构">
      <div class="tech-grid">
        <div class="tech-section">
          <h4>前端技术栈</h4>
          <div class="tech-tags">
            <a-tag color="blue">Electron</a-tag>
            <a-tag color="green">Vue 3</a-tag>
            <a-tag color="purple">TypeScript</a-tag>
            <a-tag color="orange">Ant Design Vue</a-tag>
          </div>
        </div>
        <div class="tech-section">
          <h4>后端技术栈</h4>
          <div class="tech-tags">
            <a-tag color="red">Python 3.10</a-tag>
            <a-tag color="cyan">FastAPI</a-tag>
            <a-tag color="geekblue">Uvicorn</a-tag>
            <a-tag color="lime">SQLite</a-tag>
          </div>
        </div>
        <div class="tech-section">
          <h4>AI模型</h4>
          <div class="tech-tags">
            <a-tag color="gold">BGE-M3</a-tag>
            <a-tag color="volcano">FasterWhisper</a-tag>
            <a-tag color="magenta">CN-CLIP</a-tag>
            <a-tag color="blue">Ollama</a-tag>
          </div>
        </div>
        <div class="tech-section">
          <h4>搜索引擎</h4>
          <div class="tech-tags">
            <a-tag color="purple">Faiss</a-tag>
            <a-tag color="green">Whoosh</a-tag>
          </div>
        </div>
      </div>
    </a-card>

    <!-- 开发信息 -->
    <a-row :gutter="24">
      <a-col :span="12">
        <a-card title="📋 开发信息">
          <div class="info-item">
            <span class="info-label">版本：</span>
            <span class="info-value">v2.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">构建时间：</span>
            <span class="info-value">{{ buildTime }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">运行环境：</span>
            <span class="info-value">{{ runtimeInfo }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">许可证：</span>
            <span class="info-value">MIT License</span>
          </div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="👨‍💻 开发者">
          <div class="developer-info">
            <div class="developer-avatar">
              <UserOutlined style="font-size: 3rem; color: var(--primary-600)" />
            </div>
            <div class="developer-details">
              <h4>独立开发者</h4>
              <p>专注于AI驱动的工具软件开发</p>
              <div class="contact-links">
                <a-button type="link" size="small">
                  <GithubOutlined />
                  GitHub
                </a-button>
                <a-button type="link" size="small">
                  <MailOutlined />
                  联系邮箱
                </a-button>
              </div>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 更新日志 -->
    <a-card class="feature-card" title="🚀 更新日志">
      <a-timeline>
        <a-timeline-item color="green">
          <div class="changelog-item">
            <h4>v2.0.0 - 当前版本</h4>
            <ul>
              <li>✨ 全新的多模态搜索界面</li>
              <li>🎯 优化的搜索算法和相关性排序</li>
              <li>🔧 改进的索引管理和状态监控</li>
              <li>💫 现代化的UI设计和交互体验</li>
            </ul>
          </div>
        </a-timeline-item>
        <a-timeline-item color="blue">
          <div class="changelog-item">
            <h4>v1.5.0</h4>
            <ul>
              <li>🎵 音频内容搜索支持</li>
              <li>🎬 视频字幕提取和搜索</li>
              <li>📈 批量索引优化</li>
            </ul>
          </div>
        </a-timeline-item>
        <a-timeline-item>
          <div class="changelog-item">
            <h4>v1.0.0</h4>
            <ul>
              <li>🎉 首个正式版本发布</li>
              <li>📄 基础文档搜索功能</li>
              <li>🤖 AI模型集成</li>
            </ul>
          </div>
        </a-timeline-item>
      </a-timeline>
    </a-card>

    <!-- 致谢 -->
    <a-card class="thanks-card">
      <div class="thanks-content">
        <h3>🙏 致谢</h3>
        <p>
          感谢所有开源社区的贡献者，正是因为你们的努力，才让这样的工具成为可能。
          特别感谢以下开源项目：
        </p>
        <div class="thanks-list">
          <a-tag>Vue.js</a-tag>
          <a-tag>Electron</a-tag>
          <a-tag>FastAPI</a-tag>
          <a-tag>Ant Design</a-tag>
          <a-tag>BGE-M3</a-tag>
          <a-tag>FasterWhisper</a-tag>
          <a-tag>CN-CLIP</a-tag>
          <a-tag>Ollama</a-tag>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  UserOutlined,
  GithubOutlined,
  MailOutlined
} from '@ant-design/icons-vue'

// 构建信息
const buildTime = ref('2024-01-20 15:30:00')
const runtimeInfo = computed(() => {
  return `${navigator.platform} - ${navigator.userAgent.split(' ').pop()}`
})
</script>

<style scoped>
.about-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--space-6);
}

.about-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.app-logo {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.logo-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-600), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
}

.logo-text {
  color: white;
  font-weight: 600;
  font-size: 1.125rem;
}

.version-badge {
  background: var(--primary-100);
  color: var(--primary-600);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: 0.875rem;
}

.app-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 var(--space-2);
  background: linear-gradient(135deg, var(--primary-600), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.app-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin: 0;
}

.feature-card {
  margin-bottom: var(--space-6);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
}

.feature-description {
  line-height: 1.6;
  color: var(--text-secondary);
}

.feature-item {
  text-align: center;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.feature-item:hover {
  background: var(--surface-02);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: var(--space-2);
}

.feature-item h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.feature-item p {
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}

.tech-section h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.info-value {
  color: var(--text-primary);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
}

.developer-info {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.developer-avatar {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--surface-02);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-light);
}

.developer-details h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 var(--space-1);
  color: var(--text-primary);
}

.developer-details p {
  color: var(--text-secondary);
  margin: 0 0 var(--space-3);
}

.contact-links {
  display: flex;
  gap: var(--space-2);
}

.changelog-item h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.changelog-item ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.changelog-item li {
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: var(--space-1);
}

.thanks-card {
  text-align: center;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
  background: linear-gradient(135deg, var(--surface-01), var(--surface-02));
}

.thanks-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 var(--space-3);
  color: var(--text-primary);
}

.thanks-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-4);
}

.thanks-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .about-container {
    padding: var(--space-4);
  }

  .about-header {
    margin-bottom: var(--space-6);
  }

  .app-title {
    font-size: 1.5rem;
  }

  .app-subtitle {
    font-size: 1rem;
  }

  .feature-item {
    padding: var(--space-3);
  }

  .developer-info {
    flex-direction: column;
    text-align: center;
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }

  .contact-links {
    justify-content: center;
  }
}
</style>