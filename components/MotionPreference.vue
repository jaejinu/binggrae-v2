<script setup lang="ts">
const entered = useState('entered-site', () => false)
const visible = ref(false)
const full = ref(false)
let preference: MediaQueryList | undefined
const refresh = () => {
  full.value = document.documentElement.dataset.motion === 'full'
  visible.value = !!preference?.matches || full.value
}
onMounted(() => {
  preference = matchMedia('(prefers-reduced-motion: reduce)')
  refresh()
  preference.addEventListener('change', refresh)
})
onBeforeUnmount(() => preference?.removeEventListener('change', refresh))
function toggle() {
  const url = new URL(location.href)
  url.searchParams.set('motion', full.value ? 'system' : 'full')
  url.hash = ''
  // Recreate all scenes consistently, including CSS, GSAP and WebGL.
  location.assign(url.toString())
}
</script>

<template>
  <div v-if="visible && entered" class="motion-choice" :class="{ 'motion-choice--diagnose': $route.query.diagnose === '1', 'motion-choice--full': full }">
    <span>{{ full ? '사이트 연출 켜짐' : '휴대폰 설정으로 연출이 꺼져 있어요' }}</span>
    <button @click="toggle">{{ full ? '휴대폰 설정 따르기' : '연출 켜기' }}</button>
  </div>
</template>

<style scoped>
.motion-choice { position: fixed; bottom: max(12px, env(safe-area-inset-bottom)); right: 12px; z-index: 900; max-width: calc(100vw - 24px); display: flex; align-items: center; gap: 10px; padding: 6px 6px 6px 12px; border: 1px solid #1a1a1a; border-radius: 14px; background: #fff6e0; color: #1a1a1a; box-shadow: 2px 3px 0 #1a1a1a; font-size: 12px; }
.motion-choice button { min-height: 44px; padding: 8px 12px; border-radius: 10px; background: #1a1a1a; color: #fff6e0; font-size: 12px; white-space: nowrap; }
.motion-choice--diagnose { bottom: 82px; }
.motion-choice.motion-choice--full { position: relative; right: auto; bottom: auto; width: fit-content; margin: 16px auto; z-index: auto; }
</style>
