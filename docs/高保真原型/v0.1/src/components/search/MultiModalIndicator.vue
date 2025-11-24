<template>
  <div class="multimodal-indicator">
    <div class="indicator-container">
      <!-- 语音输入指示器 -->
      <div
        class="indicator-item voice"
        :class="{
          'active': activeMode === 'voice',
          'recording': isRecording
        }"
        @click="handleModeChange('voice')"
      >
        <div class="indicator-circle">
          <div class="indicator-icon">
            <SimpleIcon type="audio" v-if="!isRecording" />
            <SimpleIcon type="pause" v-else />
          </div>
          <div class="recording-wave" v-if="isRecording">
            <div class="wave-bar bar-1"></div>
            <div class="wave-bar bar-2"></div>
            <div class="wave-bar bar-3"></div>
            <div class="wave-bar bar-4"></div>
            <div class="wave-bar bar-5"></div>
          </div>
          <div class="active-number" v-if="activeMode === 'voice'">5</div>
        </div>
        <div class="indicator-label">语音</div>
      </div>

      <!-- 文本输入指示器 -->
      <div
        class="indicator-item text"
        :class="{ 'active': activeMode === 'text' }"
        @click="handleModeChange('text')"
      >
        <div class="indicator-circle">
          <div class="indicator-icon">
            <SimpleIcon type="file" />
          </div>
          <div class="active-dot" v-if="activeMode === 'text'">•</div>
        </div>
        <div class="indicator-label">文本</div>
      </div>

      <!-- 图片输入指示器 -->
      <div
        class="indicator-item image"
        :class="{ 'active': activeMode === 'image' }"
        @click="handleModeChange('image')"
      >
        <div class="indicator-circle">
          <div class="indicator-icon">
            <SimpleIcon type="camera" v-if="activeMode !== 'image'" />
            <SimpleIcon type="check" v-else />
          </div>
          <div class="active-cross" v-if="activeMode === 'image'">✗</div>
        </div>
        <div class="indicator-label">图片</div>
      </div>
    </div>

    <!-- 模式说明 -->
    <div class="mode-description" v-if="modeDescription">
      {{ modeDescription }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SimpleIcon from '@/components/SimpleIcon.vue'
import type { InputType } from '@/types/api'

interface Props {
  activeMode: InputType
  isRecording: boolean
}

interface Emits {
  (e: 'modeChange', mode: InputType): void
  (e: 'voiceToggle'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算属性
const modeDescription = computed(() => {
  if (props.isRecording) {
    return '正在录音，请说出您的搜索内容...'
  }

  switch (props.activeMode) {
    case 'voice':
      return '点击开始语音录制，最长30秒'
    case 'text':
      return '在搜索框中输入文字内容'
    case 'image':
      return '上传图片进行视觉搜索'
    default:
      return ''
  }
})

// 处理模式切换
const handleModeChange = (mode: InputType) => {
  if (mode === 'voice') {
    emit('voiceToggle')
  } else {
    emit('modeChange', mode)
  }
}
</script>

<style lang="scss" scoped>
.multimodal-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.indicator-container {
  display: flex;
  gap: var(--space-8);
  align-items: center;
  justify-content: center;
}

.indicator-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  transition: all 0.3s var(--ease-out-cubic);
  position: relative;

  &:hover {
    transform: translateY(-2px);

    .indicator-circle {
      box-shadow: 0 8px 24px rgba(0, 229, 255, 0.3);
      border-color: var(--accent-cyan);
    }
  }

  &.active {
    .indicator-circle {
      border-color: var(--accent-cyan);
      background: rgba(0, 229, 255, 0.1);
      box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
      transform: scale(1.1);
    }

    .indicator-label {
      color: var(--accent-cyan);
      font-weight: 600;
    }
  }

  &.recording {
    .indicator-circle {
      border-color: var(--error);
      background: rgba(239, 68, 68, 0.1);
      box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
      animation: recording-pulse 1.5s ease-in-out infinite;
    }

    .indicator-label {
      color: var(--error);
      font-weight: 600;
    }
  }
}

.indicator-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid var(--border-medium);
  background: var(--surface-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s var(--ease-out-cubic);
  overflow: hidden;

  @include glass-morphism;
}

.indicator-icon {
  font-size: 32px;
  color: var(--text-secondary);
  transition: color 0.3s var(--ease-out-cubic);
  z-index: 2;
  position: relative;
}

.active .indicator-icon {
  color: var(--accent-cyan);
}

.recording .indicator-icon {
  color: var(--error);
}

// 录音波形动画
.recording-wave {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 20px;
  z-index: 1;
}

.wave-bar {
  width: 3px;
  background: var(--error);
  border-radius: 2px;
  animation: wave-animation 0.6s ease-in-out infinite;

  &.bar-1 { animation-delay: 0s; height: 8px; }
  &.bar-2 { animation-delay: 0.1s; height: 12px; }
  &.bar-3 { animation-delay: 0.2s; height: 16px; }
  &.bar-4 { animation-delay: 0.3s; height: 12px; }
  &.bar-5 { animation-delay: 0.4s; height: 8px; }
}

@keyframes wave-animation {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.5); }
}

@keyframes recording-pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.6);
  }
}

// 活跃状态指示器
.active-number,
.active-dot,
.active-cross {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 14px;
  font-weight: bold;
  color: var(--accent-cyan);
  background: var(--surface-primary);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
}

.active-dot {
  font-size: 16px;
  line-height: 1;
}

.active-cross {
  color: var(--accent-cyan);
  font-size: 12px;
}

.indicator-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  transition: color 0.3s var(--ease-out-cubic);
  font-weight: 500;
  text-align: center;
  min-width: 40px;
}

// 模式说明
.mode-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-align: center;
  max-width: 400px;
  line-height: 1.4;
  animation: fadeIn 0.3s var(--ease-out-cubic);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

// 响应式设计
@media (max-width: 768px) {
  .indicator-container {
    gap: var(--space-6);
  }

  .indicator-circle {
    width: 60px;
    height: 60px;
  }

  .indicator-icon {
    font-size: 24px;
  }

  .recording-wave {
    bottom: 6px;
    height: 16px;
  }

  .wave-bar {
    width: 2px;

    &.bar-1 { height: 6px; }
    &.bar-2 { height: 10px; }
    &.bar-3 { height: 14px; }
    &.bar-4 { height: 10px; }
    &.bar-5 { height: 6px; }
  }

  .active-number,
  .active-dot,
  .active-cross {
    width: 16px;
    height: 16px;
    font-size: 12px;
    top: 6px;
    right: 6px;
  }

  .indicator-label {
    font-size: var(--text-xs);
  }

  .mode-description {
    font-size: var(--text-xs);
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .indicator-container {
    gap: var(--space-4);
  }

  .indicator-circle {
    width: 50px;
    height: 50px;
  }

  .indicator-icon {
    font-size: 20px;
  }

  .recording-wave {
    bottom: 4px;
    height: 12px;
  }

  .wave-bar {
    width: 1.5px;

    &.bar-1 { height: 4px; }
    &.bar-2 { height: 8px; }
    &.bar-3 { height: 12px; }
    &.bar-4 { height: 8px; }
    &.bar-5 { height: 4px; }
  }
}

// 无障碍
@media (prefers-reduced-motion: reduce) {
  .indicator-item {
    transition: none;

    &:hover {
      transform: none;
    }
  }

  .indicator-circle {
    transition: none;
  }

  .wave-bar {
    animation: none;
  }

  .recording .indicator-circle {
    animation: none;
  }

  .mode-description {
    animation: none;
  }
}
</style>