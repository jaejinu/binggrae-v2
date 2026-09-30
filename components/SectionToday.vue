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
  if (prefersReducedMotion()) return
  gsap.fromTo(root.value!.querySelectorAll('.today__card'), {
    y: 100,
    rotate: (i: number) => [-5, 4, -3, 5, -4][i % 5],
    opacity: 0,
  }, {
    y: 0, rotate: 0, opacity: 1, clearProps: 'transform,opacity',
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
        <p class="body-l">{{ today.description }}</p>
      </div>
      <div class="today__cards">
        <article v-for="(item, i) in today.items" :key="item.tag" class="today__card card">
          <div class="today__thumb" :style="{ background: item.color }">
            <SparkleStar v-if="i % 2 === 0" class="today__spark" :size="26" />
            <img :src="item.image" :alt="item.alt" width="1000" height="1000" loading="lazy" decoding="async" />
          </div>
          <span class="kicker">{{ item.tag }}</span>
          <h3 class="ko-display today__product">{{ item.product }}</h3>
          <p class="body-m">{{ item.title }}</p>
        </article>
      </div>
      <p class="today__note body-m">브랜드 리뉴얼을 위해 제작한 콘셉트 이미지와 콘텐츠입니다.</p>
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
.today__thumb img { width: 100%; height: 100%; object-fit: cover; transition: transform .5s; }
.today__card:hover .today__thumb img { transform: scale(1.045); }
.today__product { font-size: clamp(22px, 2vw, 30px); }
.today__note { margin-top: 24px; font-size: 13px; }
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
