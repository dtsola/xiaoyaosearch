<template>
  <div class="not-found-page">
    <div class="not-found-container">
      <!-- 404 图标 -->
      <div class="error-icon">
        <span class="icon-404">404</span>
        <div class="search-icon">
          <SimpleIcon type="search" />
        </div>
      </div>

      <!-- 错误信息 -->
      <div class="error-content">
        <h1 class="error-title">页面未找到</h1>
        <p class="error-description">
          抱歉，您访问的页面不存在或已被移除。
        </p>
        <p class="error-suggestion">
          您可以尝试返回首页，或使用搜索功能查找您需要的内容。
        </p>
      </div>

      <!-- 操作按钮 -->
      <div class="error-actions">
        <a-button type="primary" size="large" @click="goHome">
          <SimpleIcon type="home" />
          返回首页
        </a-button>
        <a-button size="large" @click="goBack">
          <SimpleIcon type="left" />
          返回上页
        </a-button>
        <a-button type="link" size="large" @click="goToHelp">
          <SimpleIcon type="question" />
          获取帮助
        </a-button>
      </div>

      <!-- 搜索建议 -->
      <div class="search-suggestion">
        <p class="suggestion-title">或者尝试搜索：</p>
        <div class="suggestion-tags">
          <a-tag
            v-for="tag in searchSuggestions"
            :key="tag"
            :color="getTagColor()"
            @click="searchTag(tag)"
          >
            {{ tag }}
          </a-tag>
        </div>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-orb orb-1"></div>
      <div class="floating-orb orb-2"></div>
      <div class="floating-orb orb-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import SimpleIcon from '@/components/SimpleIcon.vue'

const router = useRouter()

// 搜索建议
const searchSuggestions = ref([
  '人工智能',
  '机器学习',
  '数据分析',
  '算法优化',
  '深度学习'
])

// 获取随机标签颜色
const getTagColor = () => {
  const colors = ['cyan', 'blue', 'purple', 'geekblue', 'magenta']
  return colors[Math.floor(Math.random() * colors.length)]
}

// 导航方法
const goHome = () => {
  router.push('/')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

const goToHelp = () => {
  router.push('/help')
}

const searchTag = (tag: string) => {
  router.push({
    path: '/',
    query: { q: tag }
  })
  message.info(`搜索: ${tag}`)
}
</script>

<style lang="scss" scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
}

.not-found-container {
  max-width: 600px;
  text-align: center;
  z-index: 2;
  position: relative;
}

// 错误图标
.error-icon {
  position: relative;
  margin-bottom: var(--space-8);
  display: inline-block;
}

.icon-404 {
  font-size: 120px;
  font-weight: 900;
  font-family: var(--font-artistic);
  background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-magenta) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 8px 32px rgba(0, 229, 255, 0.3);
  display: block;
  line-height: 1;
}

.search-icon {
  position: absolute;
  bottom: -20px;
  right: -20px;
  width: 60px;
  height: 60px;
  background: var(--surface-secondary);
  border: 3px solid var(--accent-cyan);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-cyan);
  font-size: 24px;
  box-shadow: 0 8px 24px rgba(0, 229, 255, 0.3);
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

// 错误内容
.error-content {
  margin-bottom: var(--space-8);
}

.error-title {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
  font-family: var(--font-display);
}

.error-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
  line-height: 1.6;
}

.error-suggestion {
  font-size: var(--text-base);
  color: var(--text-tertiary);
  line-height: 1.5;
}

// 操作按钮
.error-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: var(--space-8);
}

// 搜索建议
.search-suggestion {
  padding: var(--space-6);
  background: rgba(37, 43, 78, 0.6);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(10px);

  @include glass-morphism;
}

.suggestion-title {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin-bottom: var(--space-4);
  font-weight: 500;
}

.suggestion-tags {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-tags :deep(.ant-tag) {
  cursor: pointer;
  transition: all 0.3s var(--ease-out-cubic);
  border: none;
  font-weight: 500;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 229, 255, 0.3);
  }
}

// 背景装饰
.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: float 20s ease-in-out infinite;

  &.orb-1 {
    top: -20%;
    left: -15%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, var(--accent-cyan) 0%, transparent 70%);
    animation-delay: 0s;
  }

  &.orb-2 {
    top: 60%;
    right: -10%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, var(--accent-magenta) 0%, transparent 70%);
    animation-delay: 5s;
  }

  &.orb-3 {
    bottom: -20%;
    left: 40%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, var(--primary-core) 0%, transparent 70%);
    animation-delay: 10s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -40px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 30px) scale(0.9);
  }
  75% {
    transform: translate(-30px, -20px) scale(1.05);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .not-found-page {
    padding: var(--space-4);
  }

  .icon-404 {
    font-size: 80px;
  }

  .search-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
    bottom: -15px;
    right: -15px;
  }

  .error-title {
    font-size: var(--text-3xl);
  }

  .error-description {
    font-size: var(--text-base);
  }

  .error-actions {
    flex-direction: column;
    align-items: center;
  }

  .search-suggestion {
    padding: var(--space-4);
  }
}

@media (max-width: 480px) {
  .icon-404 {
    font-size: 60px;
  }

  .search-icon {
    width: 32px;
    height: 32px;
    font-size: 14px;
    bottom: -10px;
    right: -10px;
  }

  .error-title {
    font-size: var(--text-2xl);
  }

  .floating-orb {
    filter: blur(60px);

    &.orb-1 {
      width: 300px;
      height: 300px;
    }

    &.orb-2 {
      width: 250px;
      height: 250px;
    }

    &.orb-3 {
      width: 200px;
      height: 200px;
    }
  }
}

// 无障碍
@media (prefers-reduced-motion: reduce) {
  .search-icon,
  .floating-orb {
    animation: none;
  }

  .suggestion-tags :deep(.ant-tag):hover {
    transform: none;
  }
}
</style>