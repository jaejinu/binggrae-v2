<script setup lang="ts">
const { enabled, toggle } = useSound()
</script>

<template>
  <button class="sound" :aria-pressed="enabled" :aria-label="enabled ? '소리 끄기' : '소리 켜기'" @click="toggle">
    <span class="sound__label">Sound {{ enabled ? 'on' : 'off' }}</span>
    <span class="sound__bars" :class="{ '--on': enabled }" aria-hidden="true">
      <i v-for="n in 4" :key="n" :style="{ animationDelay: `${n * -0.18}s` }" />
    </span>
  </button>
</template>

<style scoped>
.sound {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 6px 5px 12px;
  border: 2px solid var(--ink);
  border-radius: 999px;
  background: var(--cream);
  box-shadow: 2px 2px 0 var(--ink);
  font-family: var(--font-en-display);
  font-size: 14px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.sound__bars {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--ink);
}
.sound__bars i {
  width: 2.5px;
  height: 4px;
  border-radius: 2px;
  background: var(--cream);
}
.sound__bars.--on i {
  background: var(--banana);
  animation: eq 0.8s ease-in-out infinite alternate;
}
@keyframes eq {
  to { height: 14px; }
}
@media (max-width: 1000px) {
  .sound__label {
    display: none;
  }
  .sound {
    padding: 4px;
  }
}
</style>
