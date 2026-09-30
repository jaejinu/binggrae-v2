<script setup lang="ts">
import gsap from 'gsap'
import { products } from '~/data/content'

// 제품 카테고리가 아니라 "하루의 순간"으로 제품을 발견
const active = ref(0)
const root = ref<HTMLElement>()
const current = computed(() => products[active.value])
const { blip } = useSound()

useSectionColor(root, () => ({ bg: current.value.bg, ink: current.value.ink }))

watch(active, (i: number) => blip(1 + i * 0.12))

watch(active, async () => {
  await nextTick()
  gsap.fromTo(root.value!.querySelector('.moments__art'), { scale: 0.6, rotate: -14, y: 40 }, { scale: 1, rotate: 0, y: 0, duration: 0.7, ease: 'back.out(2)' })
  gsap.fromTo(root.value!.querySelectorAll('.moments__detail > *'), { y: 16, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.06, duration: 0.4 })
})

onMounted(() => {
  gsap.from(root.value!.querySelectorAll('.moments__list li'), {
    x: -60,
    opacity: 0,
    stagger: 0.08,
    duration: 0.6,
    ease: 'back.out(1.6)',
    scrollTrigger: { trigger: root.value, start: 'top 65%' },
  })
})
</script>

<template>
  <section id="moments" ref="root" class="moments section container">
    <div class="section-head">
      <span class="kicker">02 — Your Binggrae Moment</span>
      <h2 class="ko-display size-xl sticker-text">하루의 순간으로<br />제품 발견하기</h2>
    </div>

    <div class="moments__grid">
      <ol class="moments__list">
        <li v-for="(p, i) in products" :key="p.key">
          <button
            class="moments__item"
            :class="{ '--active': i === active }"
            :aria-pressed="i === active"
            @click="active = i"
            @mouseenter="active = i"
          >
            <span class="moments__time en-display">{{ p.momentTime }}</span>
            <span class="moments__label ko-display">{{ p.moment }}</span>
            <span class="moments__name en-display">{{ p.name }}</span>
          </button>
        </li>
      </ol>

      <div class="moments__panel card">
        <SparkleStar class="moments__spark" :size="36" />
        <div class="moments__art" :key="current.key">
          <ProductArt :product="current.key" />
        </div>
        <div class="moments__detail" :key="`d-${current.key}`">
          <span class="kicker">{{ current.momentTime }}</span>
          <p class="ko-display size-md">{{ current.nameKo }}</p>
          <p class="body-m">{{ current.momentNote }}</p>
        </div>
      </div>
    </div>
    <p class="moments__note body-m">효능이 아니라, 이런 순간에 작은 즐거움으로 함께할 수 있다는 이야기.</p>
  </section>
</template>

<style scoped>
.moments__grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: clamp(24px, 4vw, 72px);
  align-items: center;
}
.moments__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}
.moments__item {
  width: 100%;
  display: grid;
  grid-template-columns: 7.5em 1fr auto;
  align-items: baseline;
  gap: 16px;
  padding: clamp(14px, 2vh, 22px) 0;
  border-top: var(--stroke) solid currentColor;
  text-align: left;
  opacity: 0.55;
  transition: opacity 0.3s, padding 0.35s cubic-bezier(0.3, 1.4, 0.6, 1);
}
li:last-child .moments__item {
  border-bottom: var(--stroke) solid currentColor;
}
.moments__item.--active {
  opacity: 1;
  padding-left: 14px;
}
.moments__time {
  font-size: 15px;
  letter-spacing: 0.06em;
}
.moments__label {
  font-size: clamp(24px, 2.8vw, 46px);
}
.moments__name {
  font-size: clamp(14px, 1.1vw, 18px);
  letter-spacing: 0.06em;
}
.moments__panel {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 16px;
  padding: clamp(20px, 3vw, 40px);
  color: var(--ink);
  min-height: 380px;
}
.moments__spark {
  position: absolute;
  right: -14px;
  top: -14px;
}
.moments__art {
  aspect-ratio: 300 / 360;
}
.moments__detail {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.moments__note {
  margin-top: 32px;
  opacity: 0.8;
}
@media (max-width: 900px) {
  .moments__grid {
    grid-template-columns: 1fr;
  }
  .moments__item {
    grid-template-columns: 1fr auto;
  }
  .moments__time {
    grid-column: 1 / -1;
  }
}
@media (max-width: 480px) {
  .moments__panel {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }
  .moments__art {
    width: 60%;
  }
}
</style>
