<script setup lang="ts">
import gsap from 'gsap'
import { brand, products } from '~/data/content'

// 입장 화면: 제품 스티커가 통통 튀다가 START 버튼 등장
const emit = defineEmits<{ start: [] }>()
const { set: setSound } = useSound()
const root = ref<HTMLElement>()
const ready = ref(false)
const starting = ref(false)
let ctx: gsap.Context | undefined
const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

onMounted(() => {
  if (reduced()) { ready.value = true; return }
  ctx = gsap.context(() => {
  gsap
    .timeline({ onComplete: () => (ready.value = true) })
    .from('.pre__item', { y: 80, scale: 0, rotate: -40, stagger: 0.1, duration: 0.6, ease: 'back.out(2.2)' })
    .to('.pre__item', { y: -20, duration: 0.3, ease: 'power1.out', yoyo: true, repeat: 1, stagger: 0.08 })
  }, root.value)
})
onBeforeUnmount(() => ctx?.revert())
watch(ready, async () => { await nextTick(); root.value?.querySelector<HTMLButtonElement>('button')?.focus({ preventScroll: true }) })

function trapFocus(event: KeyboardEvent) {
  const buttons = root.value?.querySelectorAll<HTMLButtonElement>('button')
  if (!buttons?.length) return
  const first = buttons[0]!, last = buttons[buttons.length - 1]!
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
}

function start(withSound: boolean) {
  if (starting.value) return
  starting.value = true
  setSound(withSound)
  if (reduced()) { emit('start'); return }
  ctx?.add(() => {
  gsap
    .timeline({ onComplete: () => emit('start') })
    .to('.pre__item', { y: -window.innerHeight, rotate: 60, stagger: 0.05, duration: 0.6, ease: 'back.in(1.4)' })
    .to('.pre__center', { scale: 0.6, opacity: 0, duration: 0.3 }, '<')
    .to(root.value!, { yPercent: -100, duration: 0.8, ease: 'expo.inOut' }, '-=0.2')
  })
}
</script>

<template>
  <div ref="root" class="pre" role="dialog" aria-modal="true" aria-label="빙그레할 틈 시작" @keydown.tab="trapFocus">
    <div class="pre__row" aria-hidden="true">
      <div v-for="p in products" :key="p.key" class="pre__item">
        <ProductArt :product="p.key" />
      </div>
    </div>
    <div class="pre__center">
      <p class="ko-display size-lg sticker-text">{{ brand.name }}</p>
      <Transition name="pop">
        <div v-if="ready" class="pre__buttons">
          <button class="btn btn--dark pre__start" @click="start(true)">소리와 함께 시작</button>
          <button class="btn" @click="start(false)">조용히 시작</button>
        </div>
      </Transition>
    </div>
    <p class="pre__hint body-m">🎧 소리와 함께하면 더 좋아요</p>
  </div>
</template>

<style scoped>
.pre {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(24px, 5vh, 48px);
  background: var(--banana);
  padding: var(--gutter);
}
.pre__row {
  display: flex;
  align-items: flex-end;
  gap: clamp(8px, 2vw, 28px);
}
.pre__item {
  width: clamp(56px, 8vw, 110px);
  aspect-ratio: 300 / 360;
}
.pre__center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  min-height: 130px;
}
.pre__buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}
.pre__start {
  min-height: 54px;
  padding: 0 28px;
  font-size: 17px;
}
.pre__hint {
  position: absolute;
  bottom: max(24px, env(safe-area-inset-bottom));
  font-size: 14px;
}
.pop-enter-active {
  transition: transform 0.4s cubic-bezier(0.3, 1.6, 0.6, 1), opacity 0.2s;
}
.pop-enter-from {
  transform: scale(0.4);
  opacity: 0;
}
</style>
