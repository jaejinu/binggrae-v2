<script setup lang="ts">
import gsap from 'gsap'
import { timeline } from '~/data/content'

// 05. LONG LIFE ICONS — 과거 패키지 → 광고 → 사진 → 현재 제품
const root = ref<HTMLElement>()

onMounted(() => {
  gsap.from(root.value!.querySelectorAll('.time__item'), {
    y: 80,
    rotate: (i: number) => (i % 2 ? 6 : -6),
    opacity: 0,
    stagger: 0.12,
    duration: 0.8,
    ease: 'back.out(1.6)',
    scrollTrigger: { trigger: root.value!.querySelector('.time__list'), start: 'top 75%' },
  })
  gsap.fromTo(root.value!.querySelector('.time__line'), { scaleX: 0 }, {
    scaleX: 1,
    ease: 'none',
    scrollTrigger: { trigger: root.value!.querySelector('.time__list'), start: 'top 80%', end: 'bottom 40%', scrub: true },
  })
})
</script>

<template>
  <section id="time" ref="root" class="time section container">
    <div class="section-head">
      <span class="kicker">05 — Long Life Icons</span>
      <h2 class="en-display size-xl sticker-text">{{ timeline.title }}</h2>
      <p class="ko-display size-md">{{ timeline.titleKo }}</p>
      <p class="body-l">{{ timeline.intro }}</p>
    </div>

    <div class="time__list">
      <span class="time__line" aria-hidden="true" />
      <article v-for="(s, i) in timeline.steps" :key="s.label" class="time__item">
        <div class="time__frame card" :style="{ background: s.color }">
          <span class="time__placeholder body-m">이미지 · 아카이브 자료 자리</span>
          <span class="time__badge en-display">{{ s.label }}</span>
        </div>
        <span class="time__arrow en-display" aria-hidden="true">{{ i < timeline.steps.length - 1 ? '→' : '' }}</span>
        <h3 class="ko-display size-md">{{ s.title }}</h3>
        <p class="body-m">{{ s.note }}</p>
      </article>
    </div>

    <NuxtLink :to="timeline.cta.href" class="btn btn--dark time__cta">{{ timeline.cta.label }} →</NuxtLink>
  </section>
</template>

<style scoped>
.time {
  background: var(--cream);
}
.time__list {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(16px, 2.4vw, 36px);
}
.time__line {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(50% - 60px);
  height: 3px;
  background: var(--ink);
  transform-origin: left;
  z-index: 0;
}
.time__item {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1;
}
.time__frame {
  position: relative;
  display: grid;
  place-items: center;
  aspect-ratio: 4 / 5;
  padding: 16px;
  text-align: center;
}
.time__item:nth-child(odd) .time__frame {
  transform: rotate(-2deg);
}
.time__item:nth-child(even) .time__frame {
  transform: rotate(2deg);
}
.time__placeholder {
  opacity: 0.6;
  font-size: 13px;
}
.time__badge {
  position: absolute;
  left: 12px;
  top: 12px;
  padding: 4px 10px;
  border: 2px solid var(--ink);
  border-radius: 999px;
  background: var(--cream);
  font-size: 14px;
  letter-spacing: 0.06em;
}
.time__arrow {
  position: absolute;
  right: -0.9em;
  top: calc(50% - 90px);
  font-size: 28px;
}
.time__cta {
  margin-top: clamp(32px, 6vh, 64px);
}
@media (max-width: 900px) {
  .time__list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .time__line,
  .time__arrow {
    display: none;
  }
}
</style>
