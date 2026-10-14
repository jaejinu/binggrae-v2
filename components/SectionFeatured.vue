<script setup lang="ts">
import gsap from 'gsap'
import { featured } from '~/data/content'

// 07. 단지, 50년의 이야기 — 스크롤 기반 Digital Brand Book 미리보기
const root = ref<HTMLElement>()
useSectionColor(root, () => ({ bg: '#ffd43b' }))
const pin = ref<HTMLElement>()
const active = ref(0)
let media: gsap.MatchMedia | undefined
let timeline: gsap.core.Timeline | undefined
const { scrollTo } = useSmoothScroll()
function selectChapter(index: number) {
  const st = timeline?.scrollTrigger
  if (st) scrollTo(st.start + (st.end - st.start) * (index + .5) / featured.chapters.length)
  else active.value = index
}

onMounted(() => {
  media = gsap.matchMedia()
  media.add(motionMediaQuery(), () => {
    pin.value!.classList.add('featured--animated')
    timeline = gsap.timeline({
      scrollTrigger: {
        trigger: pin.value,
        start: 'top top',
        end: () => `+=${pin.value!.clientHeight * 1.5}`,
        pin: true,
        scrub: 0.6,
        onUpdate: (self) => {
          active.value = Math.min(featured.chapters.length - 1, Math.floor(self.progress * featured.chapters.length * 0.999))
        },
      },
    })
      .fromTo('.featured__jar', { rotate: -12, scale: 0.8 }, { rotate: 12, scale: 1.05, ease: 'none' }, 0)
      .fromTo('.featured__year-fill', { scaleX: 0 }, { scaleX: 1, ease: 'none' }, 0)
    return () => { timeline = undefined; pin.value?.classList.remove('featured--animated') }
  }, root.value)
})

onBeforeUnmount(() => media?.revert())
</script>

<template>
  <section id="featured" ref="root" class="content-section featured">
    <div ref="pin" class="featured__pin container">
      <div class="featured__left">
        <span class="kicker">07 — {{ featured.kicker }}</span>
        <h2 class="ko-display size-xl sticker-text">{{ featured.title }}</h2>
        <div class="featured__years en-display">
          <span>{{ featured.range[0] }}</span>
          <span class="featured__year-bar"><span class="featured__year-fill" /></span>
          <span>{{ featured.range[1] }}</span>
        </div>
        <NuxtLink :to="featured.cta.href" class="btn">{{ featured.cta.label }} →</NuxtLink>
      </div>

      <div class="featured__jar" aria-hidden="true" data-stage="bananaMilk" data-stage-mode="featured" :data-stage-chapter="active">
        <ProductArt product="bananaMilk" />
      </div>

      <ol class="featured__chapters">
        <li v-for="(c, i) in featured.chapters" :key="c.no" :class="{ '--active': i === active, '--past': i < active }">
          <button :aria-pressed="i === active" @click="selectChapter(i)">
          <span class="en-display featured__no">Chapter {{ c.no }}</span>
          <span class="en-display featured__title">{{ c.title }}</span>
          <span class="featured__q body-m">{{ c.q }}</span>
          </button>
        </li>
      </ol>
      <p class="featured__touch-note body-m" role="status">{{ featured.chapters[active]!.q }}<br><small>스크롤하거나 챕터를 눌러보세요.</small></p>
    </div>
  </section>
</template>

<style scoped>
.featured__pin {
  position: relative;
  height: 100vh;
  height: 100svh;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(120px, .65fr) minmax(0, 1.2fr);
  align-items: center;
  gap: clamp(20px, 2vw, 32px);
  overflow: hidden;
  padding-top: 72px;
}
.featured__left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
}
.featured__left h2 {
  font-size: clamp(28px, calc(var(--content-unit) * 3), 40px);
}
.featured__years {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  width: 100%;
  max-width: 360px;
}
.featured__year-bar {
  flex: 1;
  height: 10px;
  border: 2px solid var(--ink);
  border-radius: 10px;
  background: var(--cream);
  overflow: hidden;
}
.featured__year-fill {
  display: block;
  height: 100%;
  background: var(--ink);
  transform-origin: left;
}
.featured__jar {
  width: 100%;
  max-width: 170px;
  justify-self: center;
  aspect-ratio: 300 / 360;
}
.featured__chapters {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.featured__touch-note { display: none; }
.featured__chapters li {
  border: 2px solid transparent;
  border-radius: 14px;
  opacity: 0.4;
  transition: opacity 0.3s, background-color 0.3s, border-color 0.3s, transform 0.3s;
}
.featured__chapters button { display: grid; grid-template-columns: minmax(0, 1fr); gap: 2px 12px; padding: 10px 14px; width: 100%; min-height: 48px; text-align: left; border-radius: 12px; }
.featured__chapters li.--past {
  opacity: 0.7;
}
.featured__chapters li.--active {
  opacity: 1;
  background: var(--cream);
  border-color: var(--ink);
  box-shadow: var(--shadow);
  transform: translateX(-8px);
}
.featured__no {
  font-size: 13px;
  letter-spacing: 0.06em;
  align-self: center;
}
.featured__title {
  font-size: clamp(18px, 1.6vw, 24px);
}
.featured__q {
  grid-column: 1;
  display: none;
}
.--active .featured__q {
  display: block;
}
@media (max-width: 1000px) {
  .featured__pin {
    grid-template-columns: 1fr;
    align-content: center;
    gap: 12px;
  }
  .featured__left {
    gap: 12px;
    position: relative;
    z-index: 41;
  }
  .featured__left h2 {
    font-size: clamp(34px, 9vw, 56px);
  }
  /* 모바일에서도 3D 단지 자리를 남겨 둔다 (제목과 챕터 사이) */
  .featured__jar {
    justify-self: center;
    width: auto;
    height: clamp(120px, 22svh, 220px);
  }
  .featured__chapters button {
    grid-template-columns: 6.5em 1fr;
    padding: 5px 10px;
  }
}
@media (pointer: coarse), (max-width: 1000px), (max-height: 700px), (prefers-reduced-motion: reduce) {
  .featured__pin { height: auto; min-height: 100svh; padding-block: 80px; overflow: visible; }
  .featured__chapters li { opacity: .7; }
  .featured__chapters li.--active { opacity: 1; }
  .featured__jar { height: 220px; max-width: 70vw; }
}
@media (pointer: coarse), (max-width: 1000px) {
  .featured__chapters { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; width: 100%; }
  .featured__chapters button { grid-template-columns: 1fr; gap: 7px; padding: 10px 8px; min-height: 70px; }
  .featured__no { font-size: 10px; }
  .featured__title { font-size: 17px; }
  .featured__q { display: none !important; }
  .featured__chapters li.--active { transform: none; }
  .featured__touch-note { display: block; min-height: 64px; }
  .featured__touch-note small { font-size: 12px; opacity: .75; }
}
</style>

<style scoped>
.featured__pin.featured--animated { height: 100svh; min-height: 0; overflow: hidden; }
@media (pointer: coarse), (max-width: 1000px) {
  .featured__pin.featured--animated { padding-block: 68px 16px; gap: 8px; }
  .featured--animated .featured__left { gap: 8px; }
  .featured--animated .featured__left h2 { font-size: 30px; }
  .featured--animated .featured__left .kicker { font-size: 11px; }
  .featured--animated .featured__left .btn { min-height: 40px; padding: 6px 12px; }
  .featured--animated .featured__years { font-size: 18px; }
  .featured--animated .featured__jar { height: clamp(100px, 23svh, 180px); }
  .featured--animated .featured__chapters { position: relative; z-index: 45; }
  .featured--animated .featured__chapters button { min-height: 58px; padding: 6px; gap: 3px; }
  .featured--animated .featured__touch-note { min-height: 42px; margin: 0; font-size: 14px; }
}
@media (max-height: 500px) and (orientation: landscape) {
  .featured__pin.featured--animated { grid-template-columns: 1fr .5fr 1.2fr; grid-template-rows: auto auto; padding-block: 68px 12px; gap: 8px 20px; }
  .featured--animated .featured__left { grid-column: 1; grid-row: 1; }
  .featured--animated .featured__left h2 { font-size: 28px; }
  .featured--animated .featured__jar { position: relative; grid-column: 2; grid-row: 1; height: 110px; }
  .featured--animated .featured__chapters { grid-column: 3; grid-row: 1; }
  .featured--animated .featured__touch-note { grid-column: 1 / -1; grid-row: 2; }
}
</style>

<style scoped>
@media (min-width: 1001px) and (min-height: 701px) {
  .featured__pin.featured--animated {
    height: clamp(600px, 80svh, 760px);
    padding-block: 40px;
  }
}
</style>
