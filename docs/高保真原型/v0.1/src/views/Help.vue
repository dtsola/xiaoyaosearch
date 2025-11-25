<template>
  <div class="help-container">
    <div class="help-header">
      <h2>帮助与关于</h2>
      <p>了解如何使用小遥搜索，解决常见问题</p>
    </div>

    <a-tabs v-model:activeKey="activeTab" type="card" class="help-tabs">
      <!-- 快速入门 -->
      <a-tab-pane key="guide" tab="快速入门">
        <div class="guide-section">
          <div class="guide-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>配置AI模型</h3>
              <p>进入设置页面配置本地AI模型服务，确保所有服务正常运行</p>
              <a-button type="primary">前往设置</a-button>
            </div>
          </div>

          <div class="guide-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>添加索引文件夹</h3>
              <p>进入索引管理页面，添加需要搜索的文件夹并创建文件索引</p>
              <a-button type="primary">前往索引</a-button>
            </div>
          </div>

          <div class="guide-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>开始多模态搜索</h3>
              <p>在主页面使用语音、文本、图片多种方式进行智能搜索</p>
              <a-button type="primary">开始搜索</a-button>
            </div>
          </div>
        </div>

        <div class="feature-highlights">
          <h3>核心功能介绍</h3>
          <a-row :gutter="16">
            <a-col :span="8">
              <a-card class="feature-card">
                <template #cover>
                  <div class="feature-icon">
                    <AudioOutlined />
                  </div>
                </template>
                <a-card-meta title="语音搜索" description="支持最长30秒的语音输入，FastWhisper本地识别" />
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card class="feature-card">
                <template #cover>
                  <div class="feature-icon">
                    <PictureOutlined />
                  </div>
                </template>
                <a-card-meta title="图片搜索" description="上传PNG/JPG图片，CN-CLIP模型理解内容" />
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card class="feature-card">
                <template #cover>
                  <div class="feature-icon">
                    <RobotOutlined />
                  </div>
                </template>
                <a-card-meta title="语义理解" description="BGE-M3向量嵌入 + Ollama大语言模型理解" />
              </a-card>
            </a-col>
          </a-row>
        </div>
      </a-tab-pane>

      <!-- 使用教程 -->
      <a-tab-pane key="tutorial" tab="使用教程">
        <div class="tutorial-section">
          <a-collapse v-model:activeKey="tutorialActiveKeys" :bordered="false">
            <a-collapse-panel key="1" header="如何配置本地AI模型？">
              <div class="tutorial-content">
                <h4>本地模型配置步骤：</h4>
                <ol>
                  <li><strong>语音识别模型</strong>：设置 → 语音设置 → 选择FastWhisper模型版本</li>
                  <li><strong>大语言模型</strong>：设置 → 大语言模型 → 配置Ollama服务地址</li>
                  <li><strong>视觉理解模型</strong>：设置 → 视觉模型 → 选择CN-CLIP模型</li>
                  <li><strong>文本内嵌模型</strong>：设置 → 内嵌模型 → 选择BGE-M3模型</li>
                  <li><strong>设备选择</strong>：根据硬件选择CPU或CUDA加速</li>
                </ol>
                <div class="tip-box">
                  <BulbOutlined />
                  <span>建议：首次使用时建议先用CPU模式，确保功能正常后再启用GPU加速</span>
                </div>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="2" header="如何进行多模态搜索？">
              <div class="tutorial-content">
                <h4>多模态搜索方式：</h4>
                <ul>
                  <li><strong>文本搜索</strong>：直接在搜索框输入关键词，支持自然语言</li>
                  <li><strong>语音搜索</strong>：点击麦克风按钮，说出搜索内容（30秒内）</li>
                  <li><strong>图片搜索</strong>：上传PNG/JPG图片，AI理解图片内容后搜索相关文件</li>
                </ul>
                <h4>支持的文件类型：</h4>
                <ul>
                  <li><strong>文档</strong>：txt, markdown, pdf, xls/xlsx, ppt/pptx, doc/docx</li>
                  <li><strong>音频</strong>：mp3, wav</li>
                  <li><strong>视频</strong>：mp4, avi</li>
                  <li><strong>图片</strong>：png, jpg</li>
                </ul>
                <div class="tip-box">
                  <BulbOutlined />
                  <span>注意：当前版本仅支持一级目录索引，不会递归索引子文件夹</span>
                </div>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="3" header="如何管理文件索引？">
              <div class="tutorial-content">
                <h4>索引管理指南：</h4>
                <ul>
                  <li><strong>添加文件夹</strong>：索引管理 → 添加文件夹 → 选择文件类型</li>
                  <li><strong>监控进度</strong>：查看索引状态、进度、错误信息</li>
                  <li><strong>智能更新</strong>：自动判断是否需要增量更新或完全重建</li>
                  <li><strong>查看详情</strong>：了解索引统计信息、处理时间、错误日志</li>
                </ul>
                <h4>索引状态说明：</h4>
                <ul>
                  <li><strong>等待中</strong>：索引任务已创建，等待处理</li>
                  <li><strong>处理中</strong>：正在扫描文件和建立索引</li>
                  <li><strong>已完成</strong>：索引构建完成，可以搜索</li>
                  <li><strong>失败</strong>：索引过程中出现错误</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="4" header="搜索技巧与优化">
              <div class="tutorial-content">
                <h4>搜索优化技巧：</h4>
                <ul>
                  <li><strong>自然语言</strong>：使用日常语言描述要搜索的内容</li>
                  <li><strong>关键词组合</strong>：使用多个相关关键词提高准确性</li>
                  <li><strong>文件类型过滤</strong>：指定特定文件类型缩小搜索范围</li>
                  <li><strong>相似度调节</strong>：设置 → 通用设置 → 调整相似度阈值</li>
                </ul>
                <h4>结果理解：</h4>
                <ul>
                  <li><strong>相关度分数</strong>：显示文件与查询的匹配程度</li>
                  <li><strong>内容摘要</strong>：展示文件中的相关内容片段</li>
                  <li><strong>文件路径</strong>：显示文件完整路径便于定位</li>
                </ul>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </div>
      </a-tab-pane>

      <!-- 常见问题 -->
      <a-tab-pane key="faq" tab="常见问题">
        <div class="faq-section">
          <a-collapse v-model:activeKey="faqActiveKeys" :bordered="false">
            <a-collapse-panel key="1" header="语音识别不工作怎么办？">
              <div class="faq-content">
                <p><strong>可能的原因：</strong></p>
                <ul>
                  <li>FastWhisper模型未正确安装或配置</li>
                  <li>麦克风权限未授予应用</li>
                  <li>环境噪音过大影响识别</li>
                  <li>模型版本与设备不兼容</li>
                </ul>
                <p><strong>解决方法：</strong></p>
                <ul>
                  <li>设置 → 语音设置 → 检查可用性</li>
                  <li>尝试不同的模型版本（tiny/base/small）</li>
                  <li>在安静环境下进行语音输入</li>
                  <li>检查系统麦克风权限设置</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="2" header="Ollama连接失败？">
              <div class="faq-content">
                <p><strong>检查步骤：</strong></p>
                <ul>
                  <li>确认Ollama服务已启动：http://localhost:11434</li>
                  <li>检查模型是否已安装：ollama list</li>
                  <li>验证服务地址配置是否正确</li>
                  <li>测试网络连接和防火墙设置</li>
                </ul>
                <p><strong>常用命令：</strong></p>
                <ul>
                  <li>安装模型：<code>ollama pull qwen2.5:1.5b</code></li>
                  <li>查看模型：<code>ollama list</code></li>
                  <li>运行模型：<code>ollama run qwen2.5:1.5b</code></li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="3" header="图片搜索无结果？">
              <div class="faq-content">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>CN-CLIP模型未正确加载</li>
                  <li>图片格式不支持（仅支持PNG/JPG）</li>
                  <li>图片内容过于复杂或不清晰</li>
                  <li>索引中没有相关内容的文件</li>
                </ul>
                <p><strong>优化建议：</strong></p>
                <ul>
                  <li>设置 → 视觉模型 → 检测可用性</li>
                  <li>使用清晰、内容明确的图片</li>
                  <li>尝试包含文字或明显特征的图片</li>
                  <li>确保已索引相关类型的文件</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="4" header="索引构建速度慢？">
              <div class="faq-content">
                <p><strong>影响因素：</strong></p>
                <ul>
                  <li>文件数量和大小</li>
                  <li>选择的文件类型</li>
                  <li>硬件性能（CPU/GPU）</li>
                  <li>模型加载时间</li>
                </ul>
                <p><strong>优化方法：</strong></p>
                <ul>
                  <li>分批建立索引，避免一次处理过多文件</li>
                  <li>选择必要的文件类型，减少处理负担</li>
                  <li>启用GPU加速（如果有）</li>
                  <li>在系统空闲时进行大量文件索引</li>
                </ul>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="5" header="搜索结果不准确？">
              <div class="faq-content">
                <p><strong>改进方法：</strong></p>
                <ul>
                  <li>使用更具体、更详细的描述</li>
                  <li>尝试不同的表达方式</li>
                  <li>调整相似度阈值（设置 → 通用设置）</li>
                  <li>确保相关文件已正确索引</li>
                  <li>检查BGE-M3模型是否正常工作</li>
                </ul>
                <p><strong>进阶技巧：</strong></p>
                <ul>
                  <li>结合多种模态输入（如语音+文字）</li>
                  <li>使用同义词或相关概念</li>
                  <li>针对文件类型优化搜索词</li>
                </ul>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </div>
      </a-tab-pane>

      <!-- 关于 -->
      <a-tab-pane key="about" tab="关于">
        <div class="about-section">
          <!-- 应用介绍 -->
          <div class="about-header">
            <div class="app-logo">
              <span class="logo-text">◤小遥搜索◢</span>
            </div>
            <h3>XiaoyaoSearch v0.1</h3>
            <p class="app-description">
              支持多模态AI智能搜索的本地桌面应用，通过语音、文本、图像多种输入方式，为知识工作者提供更智能的文件检索体验。
            </p>
            <div class="tagline">
              <span class="highlight">本地优先 · AI增强 · 隐私安全</span>
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
                  <h4>语音搜索</h4>
                  <p>30秒语音输入，FastWhisper本地识别</p>
                </div>
              </a-col>
              <a-col :span="8">
                <div class="feature-block">
                  <div class="feature-icon">
                    <PictureOutlined />
                  </div>
                  <h4>图像理解</h4>
                  <p>上传图片，CN-CLIP智能分析内容</p>
                </div>
              </a-col>
              <a-col :span="8">
                <div class="feature-block">
                  <div class="feature-icon">
                    <RobotOutlined />
                  </div>
                  <h4>语义搜索</h4>
                  <p>BGE-M3向量嵌入，理解查询意图</p>
                </div>
              </a-col>
            </a-row>
          </div>

          <!-- 技术特色 -->
          <div class="tech-highlight">
            <a-card class="highlight-card">
              <h4>完全本地化，隐私无忧</h4>
              <p>所有AI模型均本地部署，您的数据永远不会离开您的设备。支持离线使用，确保信息安全和隐私保护。</p>
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