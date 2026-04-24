<template>
  <div class="about-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">{{ t('about.title') }}</h1>
      <p class="page-subtitle">{{ t('about.subtitle') }}</p>
    </div>

    <!-- 作者信息 -->
    <div class="author-section">
      <a-card :title="t('about.author.cardTitle')" class="author-card">
        <div class="author-content">
          <div class="author-avatar">
            <img
              src="@/assets/images/author-avatar.jpg"
              :alt="t('about.author.avatarAlt')"
              class="avatar-image"
              @error="handleImageError"
              data-fallback="👨‍💻"
            />
          </div>
          <div class="author-info">
            <h4>dtsola</h4>
            <p>{{ t('about.author.description') }}</p>
            <div class="author-vision">
              <strong>{{ t('about.author.visionLabel') }}</strong>
              <span>{{ t('about.author.visionText') }}</span>
            </div>
            <div class="brand-mission">
              <strong>{{ t('about.author.missionLabel') }}</strong>
              <span>{{ t('about.author.missionText') }}</span>
            </div>
          </div>
        </div>

        <div class="author-links">
          <div class="contact-methods">
            <div class="contact-item">
              <div class="contact-info">
                <WechatOutlined class="contact-icon" />
                <div class="contact-text">
                  <h5>{{ t('about.author.wechatPublicAccount') }}</h5>
                  <p>{{ t('about.author.wechatAccountName') }}</p>
                </div>
              </div>
              <div class="qr-code">
                <img
                  src="@/assets/images/wechat-qr.png"
                  :alt="t('about.author.wechatQrAlt')"
                  class="qr-image"
                  @error="handleImageError"
                  data-fallback="📱 公众号"
                />
                <p class="qr-hint">{{ t('about.author.scanToFollow') }}</p>
              </div>
            </div>

            <div class="contact-item">
              <div class="contact-info">
                <UserOutlined class="contact-icon" />
                <div class="contact-text">
                  <h5>{{ t('about.author.addWechatTitle') }}</h5>
                  <p>{{ t('about.author.addWechatDesc') }}</p>
                </div>
              </div>
              <div class="qr-code">
                <img
                  src="@/assets/images/author-wechat-qr.png"
                  :alt="t('about.author.authorWechatQrAlt')"
                  class="qr-image"
                  @error="handleImageError"
                  data-fallback="👤 微信"
                />
                <p class="qr-hint">{{ t('about.author.scanToAdd') }}</p>
              </div>
            </div>
          </div>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  AudioOutlined,
  PictureOutlined,
  RobotOutlined,
  WechatOutlined,
  UserOutlined
} from '@ant-design/icons-vue'

const { t } = useI18n()

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
      <div class="qr-placeholder-text">${t('about.author.qrPreparing')}</div>
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
  padding: var(--space-xl);
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: var(--space-3xl);
}

.page-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-2xl);
  letter-spacing: -0.25px;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.page-subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
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
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: var(--border-standard);
  background: var(--bg-secondary);
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
  width: 100px;
  height: 100px;
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
  width: 100px;
  height: 100px;
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
  .about-container {
    padding: var(--space-lg);
  }

  .page-title {
    font-size: var(--text-xl);
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