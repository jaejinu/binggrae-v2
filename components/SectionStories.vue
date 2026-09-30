<script setup lang="ts">
import gsap from 'gsap'
import { stories } from '~/data/content'

// 06. BINGGRAE STORIES — Magazine / Editorial
const root = ref<HTMLElement>()
onMounted(() => {
  gsap.from(root.value!.querySelectorAll('.story'), {
    y: 60,
    opacity: 0,
    stagger: 0.08,
    duration: 0.7,
    ease: 'power3.out',
    scrollTrigger: { trigger: root.value!.querySelector('.stories__grid'), start: 'top 75%' },
  })
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
      <a v-for="(s, i) in stories" :key="s.tag" href="#" class="story" :class="`--s${i}`" @click.prevent>
        <div class="story__cover" :style="{ background: s.color }">
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
  background: #fffdf6;
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
  .story,
  .story.--s0 {
    grid-column: auto;
    grid-row: auto;
  }
}
</style>
