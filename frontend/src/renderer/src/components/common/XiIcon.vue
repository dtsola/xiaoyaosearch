<template>
  <Icon
    :icon="icon"
    :width="size"
    :height="size"
    :color="color"
    :class="['xi-icon', className]"
  />
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'

/**
 * XiIcon 组件 Props
 */
interface Props {
  /** 图标ID（格式: lucide:home） */
  icon: string
  /** 图标尺寸 */
  size?: number | string
  /** 图标颜色 */
  color?: string
  /** 自定义类名 */
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 20,
  color: 'currentColor',
  className: ''
})
</script>

<style scoped>
.xi-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color var(--transition-base), opacity var(--transition-base);
}
</style>
