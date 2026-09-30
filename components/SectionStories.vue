<script setup lang="ts">
import gsap from 'gsap'
import { stories } from '~/data/content'

// 06. BINGGRAE STORIES — Magazine / Editorial
const root = ref<HTMLElement>()
let ctx: gsap.Context | undefined
onBeforeUnmount(() => ctx?.revert())

// 커버에 마우스를 올리면 물결처럼 일렁이는 왜곡 (카드마다 별도 SVG 필터)
function ripple(i: number, on: boolean) {
  const disp = root.value?.querySelector<SVGFEDisplacementMapElement>(`#story-ripple-${i} feDisplacementMap`)
  const turb = root.value?.querySelector<SVGFETurbulenceElement>(`#story-ripple-${i} feTurbulence`)
  const cover = root.value?.querySelectorAll<HTMLElement>('.story__cover')[i]
  if (!disp || !turb || !cover) return
  const state = { s: Number(disp.getAttribute('scale')), f: 0.012 }
  gsap.killTweensOf(state)
  if (on) cover.style.filter = `url(#story-ripple-${i})`
  gsap.to(state, {
    s: on ? 22 : 0,
    f: on ? 0.02 : 0.012,
    duration: on ? 0.6 : 0.5,
    ease: on ? 'elastic.out(1, 0.5)' : 'power2.out',
    onUpdate: () => {
      disp.setAttribute('scale', state.s.toFixed(2))
      turb.setAttribute('baseFrequency', `${state.f.toFixed(4)} ${(state.f * 1.6).toFixed(4)}`)
    },
    onComplete: () => {
      if (!on) cover.style.filter = ''
    },
  })
}
useSectionColor(root, () => ({ bg: '#fffdf6' }))
onMounted(() => {
  ctx = gsap.context(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  gsap.from(root.value!.querySelectorAll('.story'), {
    y: 60,
    opacity: 0,
    stagger: 0.08,
    duration: 0.7,
    ease: 'power3.out',
    scrollTrigger: { trigger: root.value!.querySelector('.stories__grid'), start: 'top 75%' },
  })
  }, root.value)
})
</script>

<template>
  <section id="stories" ref="root" class="stories section container">
    <div class="stories__masthead">
      <span class="kicker">06 — Binggrae Stories</span>
      <h2 class="en-display size-xxl">Stories</h2>
      <p class="body-m">제품 · 디자인 · 문화에 관한 브랜드 매거진</p>
    </div>

    <div class="stories__grid">
      <svg width="0" height="0" class="stories__defs" aria-hidden="true">
        <filter v-for="(s, i) in stories" :id="`story-ripple-${i}`" :key="s.tag" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="2" seed="3" result="noise" />
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="0" xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </svg>
      <a
        v-for="(s, i) in stories"
        :key="s.tag"
        href="#"
        class="story"
        :class="`--s${i}`"
        data-cursor="READ"
        @click.prevent
        @mouseenter="ripple(i, true)"
        @mouseleave="ripple(i, false)"
      >
        <div class="story__cover" :style="{ background: s.color }">
          <MediaSlot :src="s.image" :alt="s.title"><span /></MediaSlot>
          <span class="story__issue en-display">No.{{ String(i + 1).padStart(2, '0') }}</span>
          <span class="story__big en-display" aria-hidden="true">{{ s.tag }}</span>
        </div>
        <div class="story__meta">
          <span class="kicker">{{ s.tag }}</span>
          <h3 class="story__title ko-display">{{ s.title }}</h3>
          <span class="story__read body-m">읽어보기 →</span>
        </div>
      </a>
    </div>
  </section>
</template>

<style scoped>
.stories {
  border-top: var(--stroke) solid var(--ink);
}
.stories__masthead {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: end;
  gap: 24px;
  padding-bottom: 20px;
  margin-bottom: clamp(32px, 5vh, 56px);
  border-bottom: 6px double var(--ink);
}
.stories__masthead h2 {
  line-height: 0.8;
}
.stories__defs {
  position: absolute;
}
.stories__grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: clamp(20px, 2.4vw, 36px);
}
.story {
  display: flex;
  flex-direction: column;
  gap: 14px;
  grid-column: span 2;
}
.story.--s0 {
  grid-column: span 4;
  grid-row: span 2;
}
.story.--s1,
.story.--s2 {
  grid-column: span 2;
}
.story__cover {
  position: relative;
  flex: 1;
  min-height: 200px;
  border: var(--stroke) solid var(--ink);
  border-radius: 6px;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}
.story:hover .story__cover {
  transform: translate(-3px, -3px);
  box-shadow: 6px 6px 0 var(--ink);
}
.story__issue {
  position: absolute;
  left: 14px;
  top: 12px;
  font-size: 14px;
}
.story__big {
  position: absolute;
  right: -0.06em;
  bottom: -0.14em;
  font-size: clamp(60px, 8vw, 150px);
  color: var(--cream);
  -webkit-text-stroke: 2px var(--ink);
}
.--s0 .story__big {
  font-size: clamp(90px, 14vw, 260px);
}
.story__title {
  font-size: clamp(20px, 1.8vw, 30px);
}
.--s0 .story__title {
  font-size: clamp(26px, 2.8vw, 46px);
}
.story__read {
  font-size: 13px;
  text-decoration: underline;
  text-underline-offset: 3px;
}
@media (max-width: 900px) {
  .stories__masthead {
    grid-template-columns: 1fr;
  }
  .stories__grid {
    grid-template-columns: 1fr;
  }
  .stories__grid > .story {
    grid-column: 1 / -1;
    grid-row: auto;
  }
}
</style>
