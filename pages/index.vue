<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const entered = useState('entered-site', () => false)
const started = ref(false)
const { init, stop, start, destroy, scrollTo, resetToTop } = useSmoothScroll()
const { bg, ink } = usePageColor()
let ctx: gsap.Context | undefined
let disposed = false
let previousRestoration: ScrollRestoration | undefined

function resetEntrance() {
  // Entry always starts at the schedule, even from a saved #moments link.
  if (location.hash) history.replaceState(history.state, '', location.pathname + location.search)
  resetToTop()
}

onMounted(async () => {
  init()
  started.value = entered.value
  if (!started.value) {
    previousRestoration = history.scrollRestoration
    history.scrollRestoration = 'manual'
    stop()
    resetEntrance()
  }

  // 섹션 제목류는 화면에 들어올 때 톡 튀어나오게
  ctx = gsap.context(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  gsap.set('.section-head > *', { opacity: 0, y: 40 })
  ScrollTrigger.batch('.section-head > *', {
    start: 'top 88%',
    once: true,
    onEnter: (batch) => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.08, duration: 0.7, ease: 'back.out(1.7)' }),
  })
  })

  // 폰트가 로드되면 글자 폭이 달라지므로 위치 재계산
  await document.fonts.ready
  if (disposed) return
  ScrollTrigger.refresh()
  if (!started.value) resetEntrance()
  else if (entered.value && location.hash) scrollTo(location.hash)
})
onBeforeUnmount(() => {
  disposed = true
  if (previousRestoration !== undefined) history.scrollRestoration = previousRestoration
  ctx?.revert()
  destroy()
})

function onStart() {
  resetEntrance()
  ScrollTrigger.refresh()
  resetToTop()
  started.value = true
  entered.value = true
  start()
}
</script>

<template>
  <main class="page" :style="{ color: ink }">
    <div class="page__bg" :style="{ background: bg }" aria-hidden="true" />
    <ClientOnly>
      <TheLiquidBg />
      <TheStage />
    </ClientOnly>
    <ThePreloader v-if="!started" @start="onStart" />
    <div :inert="!started">
    <TheCursor />
    <TheHeader />
    <SectionHero :started="started" />
    <SectionMoments />
    <SectionIcons />
    <SectionLookCloser />
    <SectionTime />
    <SectionStories />
    <SectionFeatured />
    <SectionToday />
    <SectionYourMoment />
    <SectionNews />
    <TheFooter />
    </div>
  </main>
</template>

<style scoped>
.page {
  position: relative;
  overflow: clip;
  transition: color 0.6s;
}
.page__bg {
  position: fixed;
  inset: 0;
  z-index: -2;
  transition: background-color 0.7s ease;
}
</style>
