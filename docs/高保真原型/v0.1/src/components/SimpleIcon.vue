<template>
  <span class="simple-icon" :class="className">
    {{ iconText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type: string
}

const props = defineProps<Props>()

const iconMap: Record<string, string> = {
  // 搜索相关
  'search': '🔍',
  'loading': '⏳',

  // 导航相关
  'home': '🏠',
  'settings': '⚙️',
  'database': '📊',
  'help': '❓',
  'file': '📄',

  // 用户相关
  'user': '👤',
  'logout': '🚪',
  'profile': '👤',

  // 通知相关
  'bell': '🔔',
  'notification': '🔔',

  // 主题相关
  'sun': '☀️',
  'moon': '🌙',
  'bulb': '💡',
  'theme': '🎨',

  // 操作相关
  'down': '▼',
  'up': '▲',
  'left': '◀',
  'right': '▶',
  'close': '✕',
  'check': '✓',
  'info': 'ℹ️',
  'question': '❓',

  // 媒体相关
  'audio': '🎤',
  'pause': '⏸️',
  'camera': '📷',
  'image': '🖼️',

  // 文件操作
  'preview': '👁️',
  'open': '📂',
  'favorite': '⭐',
  'delete': '🗑️',
  'edit': '✏️',
  'save': '💾',
  'download': '⬇️',
  'upload': '⬆️',

  // 状态相关
  'success': '✅',
  'error': '❌',
  'warning': '⚠️',
  'info-circle': 'ℹ️',

  // 其他
  'plus': '+',
  'minus': '-',
  'plus-circle': '⊕',
  'minus-circle': '⊖',
  'menu': '☰',
  'more': '⋯',
  'filter': '🔽',
  'sort': '↕',
  'refresh': '🔄',
  'copy': '📋',
  'paste': '📋',
  'cut': '✂️',
  'history': '📜',
  'video': '🎬'
}

const iconText = computed(() => {
  return iconMap[props.type.toLowerCase()] || '?'
})

const className = computed(() => {
  return `icon-${props.type.toLowerCase()}`
})
</script>

<style lang="scss" scoped>
.simple-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  user-select: none;

  // 禁止选择和拖拽
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;

  // 特定图标样式
  &.icon-loading {
    animation: spin 1s linear infinite;
  }

  &.icon-success {
    color: #52c41a;
  }

  &.icon-error {
    color: #ff4d4f;
  }

  &.icon-warning {
    color: #faad14;
  }

  &.icon-info,
  &.icon-info-circle {
    color: #1890ff;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>