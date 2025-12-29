<template>
  <div class="about-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">关于作者</h1>
      <p class="page-subtitle">小遥搜索开发者信息</p>
    </div>

    <!-- 作者信息 -->
    <div class="author-section">
      <a-card title="关于作者" class="author-card">
        <div class="author-content">
          <div class="author-avatar">
            <img
              src="/images/author-avatar.jpg"
              alt="作者头像"
              class="avatar-image"
              @error="handleImageError"
              data-fallback="👨‍💻"
            />
          </div>
          <div class="author-info">
            <h4>dtsola</h4>
            <p>
              IT解决方案架构师 | 一人公司实践者。专注于AI驱动的生产力工具开发，致力于为知识工作者打造更智能、更安全的本地搜索解决方案。
              倡导数据主权和隐私保护，相信优秀的工具应该赋能个人而非监控用户。
            </p>
            <div class="author-vision">
              <strong>开发理念：</strong>
              <span>简约而不简单，智能而不 invasive</span>
            </div>
            <div class="brand-mission">
              <strong>品牌使命：</strong>
              <span>打造真正为个人用户服务的AI工具，让技术赋能而非监控，守护您的数据主权</span>
            </div>
          </div>
        </div>

        <div class="author-links">
          <div class="contact-methods">
            <div class="contact-item">
              <div class="contact-info">
                <WechatOutlined class="contact-icon" />
                <div class="contact-text">
                  <h5>微信公众号</h5>
                  <p>小遥搜索</p>
                </div>
              </div>
              <div class="qr-code">
                <img
                  src="/images/wechat-qr.png"
                  alt="微信公众号二维码"
                  class="qr-image"
                  @error="handleImageError"
                  data-fallback="📱 公众号"
                />
                <p class="qr-hint">扫码关注</p>
              </div>
            </div>

            <div class="contact-item">
              <div class="contact-info">
                <UserOutlined class="contact-icon" />
                <div class="contact-text">
                  <h5>添加作者微信</h5>
                  <p>交流产品体验</p>
                </div>
              </div>
              <div class="qr-code">
                <img
                  src="/images/author-wechat-qr.png"
                  alt="作者微信二维码"
                  class="qr-image"
                  @error="handleImageError"
                  data-fallback="👤 微信"
                />
                <p class="qr-hint">扫码添加</p>
              </div>
            </div>
          </div>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  AudioOutlined,
  PictureOutlined,
  RobotOutlined,
  WechatOutlined,
  UserOutlined
} from '@ant-design/icons-vue'

// 图片错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  const fallback = img.getAttribute('data-fallback') || '📷'

  // 创建一个占位符div
  const placeholder = document.createElement('div')
  placeholder.className = 'qr-placeholder'
  placeholder.innerHTML = `
    <div class="qr-placeholder-content">
      <div class="qr-placeholder-icon">${fallback}</div>
      <div class="qr-placeholder-text">二维码准备中</div>
    </div>
  `

  // 复制样式
  const computedStyle = window.getComputedStyle(img)
  placeholder.style.width = computedStyle.width
  placeholder.style.height = computedStyle.height
  placeholder.style.borderRadius = computedStyle.borderRadius
  placeholder.style.border = computedStyle.border
  placeholder.style.background = computedStyle.background

  // 替换图片
  img.parentNode?.replaceChild(placeholder, img)
}
</script>

<style scoped>
.about-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--space-6);
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  background: linear-gradient(135deg, var(--primary-600), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin: 0;
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
  .about-container {
    padding: var(--space-4);
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