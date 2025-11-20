<template>
  <div class="multi-modal-indicator">
    <div class="indicators">
      <div
        v-for="mode in modes"
        :key="mode.type"
        :class="[
          'indicator',
          `indicator-${mode.type}`,
          { active: currentMode === mode.type }
        ]"
        @click="onModeChange(mode.type)"
        :title="mode.title"
        :aria-label="mode.title"
        role="button"
        tabindex="0"
        @keydown.enter="onModeChange(mode.type)"
        @keydown.space.prevent="onModeChange(mode.type)"
      >
        <div class="indicator-icon">{{ mode.icon }}</div>
        <div v-if="mode.type === 'voice' && voiceActivity" class="activity-badge">
          {{ voiceActivity }}
        </div>
        <div v-if="currentMode === mode.type" class="active-dot"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/useAppStore'
import type { InputMode } from '@/types'

interface Props {
  voiceActivity?: number
}

interface Emits {
  (e: 'modeChange', mode: InputMode): void
}

const props = withDefaults(defineProps<Props>(), {
  voiceActivity: 0
})

const emit = defineEmits<Emits>()

const appStore = useAppStore()
const { currentMode } = storeToRefs(appStore)

const modes = [
  {
    type: 'voice' as InputMode,
    icon: '🔊',
    title: '语音输入'
  },
  {
    type: 'text' as InputMode,
    icon: '📝',
    title: '文本输入'
  },
  {
    type: 'image' as InputMode,
    icon: '🖼️',
    title: '图片输入'
  }
]

const onModeChange = (mode: InputMode) => {
  appStore.setInputMode(mode)
  emit('modeChange', mode)
}
</script>

<style scoped lang="scss">
.multi-modal-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-6);
}

.indicators {
  display: flex;
  gap: var(--space-8);
  align-items: center;
}

.indicator {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--surface-tertiary);
  border: 2px solid var(--border-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  user-select: none;

  &:hover {
    transform: translateY(-2px);
    border-color: var(--accent-cyan);
    box-shadow: 0 8px 32px rgba(var(--accent-cyan-rgb), 0.2);
  }

  &:active {
    transform: translateY(0);
  }

  &.active {
    background: linear-gradient(135deg, var(--primary-core), var(--primary-light));
    border-color: var(--accent-cyan);
    box-shadow: var(--shadow-glow-primary);
    animation: pulse 2s infinite;

    .indicator-icon {
      transform: scale(1.1);
    }
  }

  &.indicator-voice.active {
    animation: voicePulse 1.5s infinite;
  }

  &:focus-visible {
    outline: 2px solid var(--accent-cyan);
    outline-offset: 4px;
  }
}

.indicator-icon {
  transition: transform var(--transition-fast);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.activity-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--accent-magenta);
  color: white;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  min-width: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(var(--accent-magenta-rgb), 0.5);
  animation: bounce 1s infinite;
}

.active-dot {
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 8px;
  background: var(--accent-cyan);
  border-radius: 50%;
  animation: blink 1s infinite;
}

// 动画定义
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: var(--shadow-glow-primary);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 32px rgba(var(--accent-cyan-rgb), 0.8);
  }
}

@keyframes voicePulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(var(--accent-magenta-rgb), 0.7);
  }
  50% {
    box-shadow: 0 0 0 16px rgba(var(--accent-magenta-rgb), 0);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .indicators {
    gap: var(--space-6);
  }

  .indicator {
    width: 56px;
    height: 56px;
    font-size: 20px;
  }
}

// 高对比度模式
@media (prefers-contrast: high) {
  .indicator {
    border-width: 3px;
  }

  .activity-badge {
    border: 2px solid white;
  }
}

// 减少动画模式
@media (prefers-reduced-motion: reduce) {
  .indicator {
    animation: none !important;
    transition: none;
  }

  .activity-badge {
    animation: none;
  }

  .active-dot {
    animation: none;
  }
}
</style>