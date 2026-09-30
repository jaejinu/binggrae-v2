<script setup lang="ts">
import gsap from 'gsap'
import { today } from '~/data/content'

// 08. BINGGRAE TODAY — 현재 브랜드 활동
const root = ref<HTMLElement>()
let ctx: gsap.Context | undefined
onBeforeUnmount(() => ctx?.revert())
useSectionColor(root, () => ({ bg: '#8fd3ff' }))
onMounted(() => {
  ctx = gsap.context(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  gsap.from(root.value!.querySelectorAll('.today__card'), {
    y: 100,
    rotate: (i: number) => [-5, 4, -3, 5, -4][i % 5],
    opacity: 0,
    stagger: 0.1,
    duration: 0.8,
    ease: 'back.out(1.5)',
    scrollTrigger: { trigger: root.value!.querySelector('.today__cards'), start: 'top 80%' },
  })
  }, root.value)
})
</script>

<template>
  <section id="today" ref="root" class="today section">
    <div class="today__marquee" aria-hidden="true">
      <div class="today__marquee-inner en-display">
        <span v-for="n in 2" :key="n">NEW PRODUCT ✦ COLLABORATION ✦ CAMPAIGN ✦ POP-UP ✦ BRAND FILM ✦&nbsp;</span>
      </div>
    </div>

    <div class="container">
      <div class="section-head">
        <span class="kicker">08 — Binggrae Today</span>
        <h2 class="ko-display size-xl sticker-text">{{ today.title }}</h2>
      </div>
      <div class="today__cards">
        <a v-for="(item, i) in today.items" :key="item.tag" href="#" class="today__card card" data-cursor="VIEW" @click.prevent>
          <div class="today__thumb" :style="{ background: item.color }">
            <SparkleStar v-if="i % 2 === 0" class="today__spark" :size="26" />
            <MediaSlot :src="item.image" :alt="item.title" />
          </div>
          <span class="kicker">{{ item.tag }}</span>
          <p class="body-m">{{ item.title }}</p>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.today {
  overflow: hidden;
}
.today__marquee {
  margin-bottom: clamp(48px, 8vh, 96px);
  border-block: var(--stroke) solid var(--ink);
  background: var(--banana);
  overflow: hidden;
}
.today__marquee-inner {
  display: flex;
  width: max-content;
  font-size: clamp(28px, 3.4vw, 56px);
  padding-block: 10px;
  animation: marquee 22s linear infinite;
}
@keyframes marquee {
  to { transform: translateX(-50%); }
}
.today__cards {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: clamp(14px, 1.6vw, 24px);
}
.today__card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  transition: transform 0.2s;
}
.today__card:hover {
  transform: translateY(-6px) rotate(-1deg);
}
.today__thumb {
  position: relative;
  display: grid;
  place-items: center;
  aspect-ratio: 1;
  border: 2px solid var(--ink);
  border-radius: 12px;
  overflow: hidden;
}
.today__thumb .body-m {
  font-size: 12px;
  opacity: 0.55;
}
.today__spark {
  position: absolute;
  z-index: 1;
  right: 8px;
  top: 8px;
}
@media (max-width: 1000px) {
  .today__cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
