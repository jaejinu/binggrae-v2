<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const started = ref(false)
const { init, stop, start } = useSmoothScroll()
const { bg, ink } = usePageColor()

onMounted(async () => {
  init()
  stop()

  // 섹션 제목류는 화면에 들어올 때 톡 튀어나오게
  gsap.set('.section-head > *', { opacity: 0, y: 40 })
  ScrollTrigger.batch('.section-head > *', {
    start: 'top 88%',
    once: true,
    onEnter: (batch) => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.08, duration: 0.7, ease: 'back.out(1.7)' }),
  })

  // 폰트가 로드되면 글자 폭이 달라지므로 위치 재계산
  await document.fonts.ready
  ScrollTrigger.refresh()
})

function onStart() {
  started.value = true
  start()
}
</script>

<template>
  <main class="page" :style="{ color: ink }">
    <div class="page__bg" :style="{ background: bg }" aria-hidden="true" />
    <ThePreloader v-if="!started" @start="onStart" />
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
  z-index: -1;
  transition: background-color 0.7s ease;
}
</style>
