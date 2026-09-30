<script setup lang="ts">
import gsap from 'gsap'
import { products, iconOrder } from '~/data/content'

// 한 화면씩 크게 넘기는 제품 소개. 제품이 바뀔 때마다 배경색·타이포·도형·모션이 함께 바뀜.
const list = iconOrder.map((k) => products.find((p) => p.key === k)!)
const root = ref<HTMLElement>()
const track = ref<HTMLElement>()
const active = ref(0)
const touchLayout = ref(false)
let media: gsap.MatchMedia | undefined
function onSwipe() {
  if (!touchLayout.value || !track.value) return
  active.value = Math.max(0, Math.min(list.length - 1, Math.round(track.value.scrollLeft / track.value.clientWidth)))
}
function select(index: number) {
  track.value?.scrollTo({ left: index * track.value.clientWidth, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' })
}

// 제품별 그래픽 도형 (배경 장식)
const shapes: Record<string, string> = {
  yoplait: 'M100 10 C150 10 190 50 190 100 C190 150 150 190 100 190 C50 190 10 150 10 100 C10 50 50 10 100 10 Z',
  samanco: 'M10 100 C40 30 140 20 170 70 L195 45 L195 155 L170 130 C140 180 40 170 10 100 Z',
  bravo: 'M100 195 L20 40 C50 5 150 5 180 40 Z',
  bananaMilk: 'M70 10 H130 V30 C130 40 185 60 185 115 C185 165 150 195 100 195 C50 195 15 165 15 115 C15 60 70 40 70 30 Z',
}

onMounted(() => {
  media = gsap.matchMedia()
  media.add('(pointer: coarse), (max-width: 800px)', () => {
    touchLayout.value = true
    return () => { touchLayout.value = false; if (track.value) track.value.scrollLeft = 0 }
  })
  media.add('(pointer: fine) and (min-width: 801px) and (min-height: 701px) and (prefers-reduced-motion: no-preference)', () => {
    const panels = gsap.utils.toArray<HTMLElement>('.icon-panel')
    const scrollTween = gsap.to(track.value, {
      x: () => -(track.value!.scrollWidth - window.innerWidth),
      ease: 'none',
      scrollTrigger: {
        trigger: root.value,
        start: 'top top',
        end: () => `+=${track.value!.scrollWidth - window.innerWidth}`,
        pin: true,
        scrub: 0.6,
        snap: { snapTo: 1 / (panels.length - 1), duration: 0.5, ease: 'power2.inOut' },
        invalidateOnRefresh: true,
        onUpdate: (self) => {
          active.value = Math.round(self.progress * (panels.length - 1))
        },
      },
    })

    // 패널별 등장 모션
    panels.forEach((panel) => {
      gsap.fromTo(
        panel.querySelectorAll('.icon-panel__art, .icon-panel__shape'),
        { scale: 0.4, rotate: -20 },
        {
          scale: 1,
          rotate: 0,
          ease: 'back.out(1.6)',
          scrollTrigger: { trigger: panel, containerAnimation: scrollTween, start: 'left 80%', end: 'left 20%', scrub: true },
        },
      )
      gsap.fromTo(
        panel.querySelectorAll('.icon-panel__name'),
        { xPercent: 30, opacity: 0 },
        {
          xPercent: 0,
          opacity: 1,
          scrollTrigger: { trigger: panel, containerAnimation: scrollTween, start: 'left 70%', end: 'left 30%', scrub: true },
        },
      )
    })
  }, root.value)
})

useSectionColor(root, () => ({ bg: list[active.value].bg, ink: list[active.value].ink }), () => root.value?.parentElement?.classList.contains('pin-spacer') ? root.value.parentElement : root.value)

onBeforeUnmount(() => media?.revert())
</script>

<template>
  <section id="icons" ref="root" class="icons">
    <div class="icons__head container">
      <span class="kicker">03 — Binggrae Icons</span>
      <span class="icons__count en-display">{{ String(active + 1).padStart(2, '0') }} / {{ String(list.length).padStart(2, '0') }}</span>
    </div>
    <div ref="track" class="icons__track" @scroll.passive="onSwipe">
      <article
        v-for="(p, i) in list"
        :key="p.key"
        class="icon-panel"
        :style="{ background: p.bg, color: p.ink }"
      >
        <svg class="icon-panel__shape" viewBox="0 0 200 200" aria-hidden="true">
          <path :d="shapes[p.key]" :fill="p.accent" stroke="#1a1a1a" stroke-width="2" opacity=".9" />
        </svg>
        <div class="icon-panel__art" data-cursor="ICON" :data-stage="p.key" data-stage-anim="x">
          <ProductArt :product="p.key" />
        </div>
        <div class="icon-panel__text">
          <span class="kicker">ICON {{ String(i + 1).padStart(2, '0') }}</span>
          <h3 class="icon-panel__name en-display size-xxl sticker-text">{{ p.name }}</h3>
          <p class="ko-display size-md">{{ p.nameKo }}</p>
          <p class="body-m icon-panel__desc">오랫동안 우리의 일상에 함께해온 제품. {{ p.moment }}에 곁에 있던 그 맛.</p>
          <NuxtLink :to="p.href" class="btn">상세페이지 보기 →</NuxtLink>
        </div>
        <span class="icon-panel__no en-display" aria-hidden="true">{{ String(i + 1).padStart(2, '0') }}</span>
      </article>
    </div>
    <nav class="icons__touch-nav" aria-label="제품 넘기기">
      <p>옆으로 밀어 다음 제품을 만나보세요 ↔</p>
      <div><button v-for="(p,i) in list" :key="p.key" class="btn btn--sm" :aria-pressed="active===i" @click="select(i)">{{ String(i+1).padStart(2,'0') }} {{ p.nameKo }}</button></div>
    </nav>
  </section>
</template>

<style scoped>
.icons {
  position: relative;
  height: 100vh;
  height: 100svh;
  overflow: hidden;
}
.icons__head {
  position: absolute;
  top: 88px;
  left: 0;
  right: 0;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}
.icons__count {
  font-size: 18px;
}
.icons__touch-nav { display: none; }
.icons__track {
  display: flex;
  height: 100%;
  width: max-content;
  will-change: transform;
}
.icon-panel {
  position: relative;
  flex: none;
  width: 100vw;
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  padding: 120px var(--gutter) 60px;
  overflow: hidden;
}
.icon-panel__shape {
  position: absolute;
  left: 6%;
  top: 50%;
  width: min(52vw, 70vh);
  translate: 0 -50%;
}
.icon-panel__art {
  position: relative;
  justify-self: center;
  width: min(30vw, 44vh);
  aspect-ratio: 300 / 360;
}
.icon-panel__text {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
  z-index: 1;
}
.icon-panel__name {
  font-size: clamp(56px, 9vw, 168px);
  white-space: nowrap;
}
.icon-panel__desc {
  max-width: 360px;
}
.icon-panel__no {
  position: absolute;
  right: var(--gutter);
  bottom: -0.12em;
  font-size: clamp(120px, 22vw, 380px);
  opacity: 0.12;
  pointer-events: none;
}
@media (max-width: 800px) {
  .icon-panel {
    grid-template-columns: 1fr;
    align-content: center;
    gap: 24px;
  }
  .icon-panel__art {
    width: min(46vw, 30vh);
  }
  .icon-panel__shape {
    left: 50%;
    top: 36%;
    width: 90vw;
    translate: -50% -50%;
  }
  .icon-panel__name {
    font-size: clamp(48px, 15vw, 96px);
  }
}
</style>

<style scoped>
@media (pointer: coarse), (max-width: 800px) {
  .icons { height: auto; }
  .icons__head { top: 24px; }
  .icons__count { display: block; }
  .icons__track { width: 100%; height: auto; display: flex; overflow-x: auto; scroll-snap-type: x mandatory; overscroll-behavior-x: contain; scrollbar-width: none; will-change: auto; }
  .icons__track::-webkit-scrollbar { display: none; }
  .icon-panel { flex: 0 0 100%; min-height: 600px; height: auto; padding: 78px var(--gutter) 38px; scroll-snap-align: start; scroll-snap-stop: always; }
  .icon-panel__art { width: min(46vw, 220px); }
  .icons__touch-nav { display: block; padding: 16px var(--gutter) 28px; background: var(--cream); color: var(--ink); }
  .icons__touch-nav p { margin: 0 0 14px; font-size: 14px; }
  .icons__touch-nav > div { display: flex; flex-wrap: wrap; gap: 10px; }
}
</style>

<style scoped>
@media (pointer: fine) and (min-width: 801px) and (max-height: 700px), (pointer: fine) and (min-width: 801px) and (prefers-reduced-motion: reduce) {
  .icons { height: auto; }
  .icons__head { top: 28px; }
  .icons__track { display: block; width: 100%; }
  .icon-panel { min-height: max(700px, 100svh); height: auto; }
  .icons__count { display: none; }
}
</style>
