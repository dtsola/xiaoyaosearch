<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { SystemService } from '@/api/system'
import XiHeader from './components/common/XiHeader.vue'
import XiFooter from './components/common/XiFooter.vue'

// 国际化支持
import { useI18n } from 'vue-i18n'
import { setLocale } from './i18n/setup'

const router = useRouter()
const route = useRoute()
const { locale, t } = useI18n()

// Ant Design Vue 语言状态
const antdLocale = ref(setLocale(locale.value))

// 监听语言切换，同步更新 Ant Design 和 Day.js 语言
watch(locale, (newLocale) => {
  antdLocale.value = setLocale(newLocale)
  localStorage.setItem('locale', newLocale)
})

// 监听路由变化，更新页面标题
watch(
  () => route.meta.titleKey,
  (titleKey) => {
    if (titleKey) {
      document.title = t(titleKey as string)
    }
  },
  { immediate: true }
)

// 响应式数据
const indexCount = ref(0)
const dataSize = ref(0)
const searchCount = ref(0)
const lastUpdate = ref(new Date())
const loading = ref(false)
const refreshTimer = ref<NodeJS.Timeout>()

// 获取系统状态数据
const fetchSystemStatus = async () => {
  if (loading.value) return

  loading.value = true
  try {
    const response = await SystemService.getStatus()

    if (response.success) {
      const data = response.data

      // 更新索引文件数量
      if (typeof data.data_count === 'number') {
        indexCount.value = data.data_count
      }

      // 更新数据大小（直接使用 running-status 接口返回的 data_size）
      if (typeof data.data_size === 'number') {
        dataSize.value = data.data_size
      }

      // 更新今日搜索次数
      if (typeof data.today_searches === 'number') {
        searchCount.value = data.today_searches
      }

      // 更新最后更新时间
      if (data.last_update) {
        lastUpdate.value = new Date(data.last_update)
      }
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
    message.warning(t('status.statusUpdateFailed'))
  } finally {
    loading.value = false
  }
}

// 组件挂载
onMounted(() => {
  // 立即获取一次系统状态
  fetchSystemStatus()

  // 设置定时刷新（每60秒更新一次）
  refreshTimer.value = setInterval(() => {
    fetchSystemStatus()
  }, 60 * 1000)

  // 每分钟更新最后更新时间显示
  setInterval(() => {
    lastUpdate.value = new Date()
  }, 60 * 1000)
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
})
</script>

<template>
  <a-config-provider :locale="antdLocale">
    <a-layout class="app-layout">
      <!-- 顶部导航 -->
      <XiHeader />

    <!-- 主内容区 -->
    <a-layout-content class="app-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </a-layout-content>

    <!-- 底部状态栏 -->
    <XiFooter
      :index-count="indexCount"
      :search-count="searchCount"
      :data-size="dataSize"
      :last-update="lastUpdate"
    />
  </a-layout>
  </a-config-provider>
</template>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  overflow: hidden;
  background: var(--bg-secondary);
}

.content-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-6);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
