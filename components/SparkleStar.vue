<script setup lang="ts">
// Four-point twinkle with a black outline, used as scattered decoration.
defineProps<{ size?: number; delay?: number }>()
</script>

<template>
  <svg
    class="sparkle"
    :width="size ?? 28"
    :height="size ?? 28"
    viewBox="0 0 40 40"
    aria-hidden="true"
    :style="{ animationDelay: `${delay ?? 0}s` }"
  >
    <path
      d="M20 2 C21.5 13 27 18.5 38 20 C27 21.5 21.5 27 20 38 C18.5 27 13 21.5 2 20 C13 18.5 18.5 13 20 2 Z"
      fill="#fffdf6"
      stroke="#141414"
      stroke-width="2.5"
      stroke-linejoin="round"
    />
  </svg>
</template>

<style scoped>
.sparkle {
  display: block;
  filter: drop-shadow(2px 2px 0 #141414);
  animation: spin-pulse 3.2s ease-in-out infinite;
}
@keyframes spin-pulse {
  0%, 100% { transform: scale(0.85) rotate(0deg); }
  50% { transform: scale(1.1) rotate(20deg); }
}
</style>
