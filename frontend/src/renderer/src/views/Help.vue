<template>
  <div class="help-container">
    <div class="help-header">
      <h2>帮助中心</h2>
      <p>了解如何使用小遥搜索的各项功能</p>
    </div>

    <a-row :gutter="24">
      <!-- 快速入门 -->
      <a-col :span="8">
        <a-card class="help-card" title="🚀 快速入门">
          <div class="help-section">
            <h4>基础使用</h4>
            <ul>
              <li>在搜索框中输入关键词</li>
              <li>支持中文、英文搜索</li>
              <li>按回车键或点击搜索按钮</li>
            </ul>
          </div>
          <div class="help-section">
            <h4>搜索技巧</h4>
            <ul>
              <li>使用更具体的关键词</li>
              <li>调整相似度阈值</li>
              <li>选择合适的文件类型</li>
            </ul>
          </div>
        </a-card>
      </a-col>

      <!-- 功能说明 -->
      <a-col :span="8">
        <a-card class="help-card" title="💡 功能说明">
          <div class="help-section">
            <h4>搜索类型</h4>
            <ul>
              <li><strong>语义搜索</strong>：理解含义的智能搜索</li>
              <li><strong>全文搜索</strong>：基于关键词的传统搜索</li>
              <li><strong>混合搜索</strong>：结合两种方式的优势</li>
            </ul>
          </div>
          <div class="help-section">
            <h4>支持的文件</h4>
            <ul>
              <li>📄 文档：txt, md, pdf, office系列</li>
              <li>🎵 音频：mp3, wav（内容搜索）</li>
              <li>🎬 视频：mp4, avi（内容搜索）</li>
              <li>🖼️ 图片：jpg, png（文件名搜索）</li>
            </ul>
          </div>
        </a-card>
      </a-col>

      <!-- 常见问题 -->
      <a-col :span="8">
        <a-card class="help-card" title="❓ 常见问题">
          <div class="help-section">
            <h4>搜索无结果？</h4>
            <ul>
              <li>检查文件夹是否已添加到索引</li>
              <li>尝试降低相似度阈值</li>
              <li>使用更通用的关键词</li>
            </ul>
          </div>
          <div class="help-section">
            <h4>索引很慢？</h4>
            <ul>
              <li>大文件需要更多处理时间</li>
              <li>可以暂停不重要的任务</li>
              <li>建议在空闲时间进行索引</li>
            </ul>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 详细帮助 -->
    <div class="help-details">
      <a-card title="📖 详细使用指南">
        <a-tabs type="card">
          <!-- 搜索指南 -->
          <a-tab-pane key="search" tab="搜索指南">
            <div class="guide-section">
              <h3>基础搜索</h3>
              <p>在首页的搜索框中输入您要查找的内容，支持以下搜索方式：</p>
              <div class="code-example">
                <div class="example-title">示例：</div>
                <ul>
                  <li><code>技术文档</code> - 搜索包含"技术文档"的文件</li>
                  <li><code>Python 编程</code> - 搜索包含"Python"和"编程"的文件</li>
                  <li><code>项目计划</code> - 搜索与项目计划相关的文档</li>
                </ul>
              </div>
            </div>

            <div class="guide-section">
              <h3>高级选项</h3>
              <p>点击搜索框右侧的设置按钮可以打开高级选项：</p>
              <ul>
                <li><strong>搜索类型</strong>：选择语义搜索、全文搜索或混合搜索</li>
                <li><strong>相似度阈值</strong>：调整结果的相关性要求（0-100%）</li>
                <li><strong>文件类型</strong>：限制搜索特定的文件类型</li>
              </ul>
            </div>
          </a-tab-pane>

          <!-- 索引指南 -->
          <a-tab-pane key="index" tab="索引指南">
            <div class="guide-section">
              <h3>添加文件夹</h3>
              <p>在索引管理页面，点击"添加文件夹"按钮：</p>
              <ul>
                <li>输入要索引的文件夹路径</li>
                <li>选择是否递归包含子文件夹</li>
                <li>选择要索引的文件类型</li>
                <li>点击确定开始索引</li>
              </ul>
            </div>

            <div class="guide-section">
              <h3>索引状态</h3>
              <p>索引过程中有以下状态：</p>
              <ul>
                <li><strong>等待中</strong>：任务已创建，等待处理</li>
                <li><strong>处理中</strong>：正在扫描和索引文件</li>
                <li><strong>已完成</strong>：索引成功完成</li>
                <li><strong>失败</strong>：索引过程中出现错误</li>
              </ul>
            </div>
          </a-tab-pane>

          <!-- 设置指南 -->
          <a-tab-pane key="settings" tab="设置指南">
            <div class="guide-section">
              <h3>AI模型配置</h3>
              <p>在设置页面可以配置各种AI模型：</p>
              <ul>
                <li><strong>语音设置</strong>：配置FastWhisper语音识别模型</li>
                <li><strong>大语言模型</strong>：配置Ollama服务地址和模型</li>
                <li><strong>视觉模型</strong>：配置CN-CLIP图像理解模型</li>
              </ul>
            </div>

            <div class="guide-section">
              <h3>搜索参数</h3>
              <p>调整搜索的默认行为：</p>
              <ul>
                <li><strong>默认搜索类型</strong>：设置默认的搜索方式</li>
                <li><strong>相似度阈值</strong>：设置默认的相关性要求</li>
                <li><strong>结果数量</strong>：设置默认的搜索结果数量</li>
              </ul>
            </div>
          </a-tab-pane>
        </a-tabs>
      </a-card>
    </div>

    <!-- 快捷键 -->
    <div class="shortcuts">
      <a-card title="⌨️ 快捷键">
        <a-row :gutter="16">
          <a-col :span="12">
            <div class="shortcut-item">
              <kbd>Ctrl</kbd> + <kbd>K</kbd>
              <span>快速聚焦搜索框</span>
            </div>
            <div class="shortcut-item">
              <kbd>Enter</kbd>
              <span>执行搜索</span>
            </div>
          </a-col>
          <a-col :span="12">
            <div class="shortcut-item">
              <kbd>Esc</kbd>
              <span>清空搜索框</span>
            </div>
            <div class="shortcut-item">
              <kbd>Ctrl</kbd> + <kbd>/</kbd>
              <span>显示帮助</span>
            </div>
          </a-col>
        </a-row>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { message } from 'ant-design-vue'

// 可以在这里添加一些交互逻辑
const showExample = () => {
  message.info('这是一个示例功能')
}
</script>

<style scoped>
.help-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6);
}

.help-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.help-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.help-header p {
  color: var(--text-secondary);
  margin: 0;
}

.help-card {
  height: 100%;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
  transition: all var(--transition-base);
}

.help-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.help-section {
  margin-bottom: var(--space-4);
}

.help-section:last-child {
  margin-bottom: 0;
}

.help-section h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--text-primary);
}

.help-section ul {
  margin: 0;
  padding-left: var(--space-4);
}

.help-section li {
  margin-bottom: var(--space-1);
  color: var(--text-secondary);
  line-height: 1.5;
}

.help-details {
  margin-top: var(--space-8);
}

.guide-section {
  margin-bottom: var(--space-6);
}

.guide-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 var(--space-3);
  color: var(--text-primary);
}

.guide-section p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-3);
}

.guide-section ul {
  color: var(--text-secondary);
  line-height: 1.6;
}

.guide-section li {
  margin-bottom: var(--space-1);
}

.code-example {
  background: var(--surface-02);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  margin: var(--space-3) 0;
}

.example-title {
  font-weight: 600;
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.code-example ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.code-example li {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  margin-bottom: var(--space-1);
}

.code-example code {
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary-600);
  padding: 2px 6px;
  border-radius: var(--radius-base);
}

.shortcuts {
  margin-top: var(--space-6);
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.shortcut-item kbd {
  background: var(--surface-03);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-base);
  padding: var(--space-1) var(--space-2);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.1);
}

.shortcut-item span {
  color: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .help-container {
    padding: var(--space-4);
  }

  .help-header {
    margin-bottom: var(--space-6);
  }

  .help-card {
    margin-bottom: var(--space-4);
  }
}
</style>