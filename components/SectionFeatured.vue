<script setup lang="ts">
import gsap from 'gsap'
import { featured } from '~/data/content'

// 07. 단지, 50년의 이야기 — 스크롤 기반 Digital Brand Book 미리보기
const root = ref<HTMLElement>()
useSectionColor(root, () => ({ bg: '#ffd43b' }))
const pin = ref<HTMLElement>()
const active = ref(0)
let ctx: gsap.Context | undefined

onMounted(() => {
  ctx = gsap.context(() => {
    gsap.timeline({
      scrollTrigger: {
        trigger: pin.value,
        start: 'top top',
        end: () => `+=${window.innerHeight * 3}`,
        pin: true,
        scrub: 0.6,
        onUpdate: (self) => {
          active.value = Math.min(featured.chapters.length - 1, Math.floor(self.progress * featured.chapters.length * 0.999))
        },
      },
    })
      .fromTo('.featured__jar', { rotate: -12, scale: 0.8 }, { rotate: 12, scale: 1.05, ease: 'none' }, 0)
      .fromTo('.featured__year-fill', { scaleX: 0 }, { scaleX: 1, ease: 'none' }, 0)
  }, root.value)
})

onBeforeUnmount(() => ctx?.revert())
</script>

<template>
  <section id="featured" ref="root" class="featured">
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
          <span class="en-display featured__no">Chapter {{ c.no }}</span>
          <span class="en-display featured__title">{{ c.title }}</span>
          <span class="featured__q body-m">{{ c.q }}</span>
        </li>
      </ol>
    </div>
  </section>
</template>

<style scoped>
.featured__pin {
  position: relative;
  height: 100vh;
  height: 100svh;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: clamp(20px, 3vw, 56px);
  overflow: hidden;
  padding-top: 72px;
}
.featured__left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
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
  width: clamp(160px, 20vw, 300px);
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
.featured__chapters li {
  display: grid;
  grid-template-columns: 7.2em 1fr;
  gap: 2px 12px;
  padding: 10px 14px;
  border: 2px solid transparent;
  border-radius: 14px;
  opacity: 0.4;
  transition: opacity 0.3s, background-color 0.3s, border-color 0.3s, transform 0.3s;
}
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
  font-size: clamp(20px, 1.8vw, 28px);
}
.featured__q {
  grid-column: 2;
  display: none;
}
.--active .featured__q {
  display: block;
}
@media (max-width: 1000px) {
  .featured__pin {
    grid-template-columns: 1fr;
    align-content: center;
    gap: 16px;
  }
  .featured__jar {
    display: none;
  }
  .featured__chapters li {
    grid-template-columns: 6.5em 1fr;
    padding: 6px 10px;
  }
}
</style>
