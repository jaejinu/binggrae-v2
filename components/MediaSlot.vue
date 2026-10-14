<script setup lang="ts">
// 이미지가 있으면 보여주고, 없으면 "이미지 자리" 플레이스홀더를 보여준다.
const props = defineProps<{ src?: string; alt?: string; label?: string }>()
const ok = useImageAvailable(() => props.src)
</script>

<template>
  <img v-if="ok" :src="src" :alt="alt ?? ''" class="media-slot__img" loading="lazy" />
  <span v-else class="media-slot__placeholder">
    <slot>{{ label ?? '이미지 자리' }}</slot>
  </span>
</template>

<style scoped>
.media-slot__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.media-slot__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  opacity: 0.55;
  text-align: center;
}
.media-slot__path {
  font-size: 10px;
  opacity: 0.8;
}
</style>
