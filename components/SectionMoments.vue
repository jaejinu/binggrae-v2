<script setup lang="ts">
import gsap from 'gsap'
import { products } from '~/data/content'

// 제품 카테고리가 아니라 "하루의 순간"으로 제품을 발견
const active = ref(0)
const root = ref<HTMLElement>()
let ctx: gsap.Context | undefined
onBeforeUnmount(() => ctx?.revert())
const current = computed(() => products[active.value])
const { blip } = useSound()

useSectionColor(root, () => ({ bg: current.value.bg, ink: current.value.ink }))

watch(active, (i: number) => blip(1 + i * 0.12))

watch(active, async () => {
  await nextTick()
  if (!root.value || prefersReducedMotion()) return
  ctx?.add(() => {
  gsap.fromTo(root.value!.querySelector('.moments__art'), { scale: 0.6, rotate: -14, y: 40 }, { scale: 1, rotate: 0, y: 0, duration: 0.7, ease: 'back.out(2)' })
  gsap.fromTo(root.value!.querySelectorAll('.moments__detail > *'), { y: 16, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.06, duration: 0.4, overwrite: true })
  })
})

onMounted(() => {
  ctx = gsap.context(() => {
  if (prefersReducedMotion()) return
  gsap.from(root.value!.querySelectorAll('.moments__list li'), {
    x: -60,
    opacity: 0,
    stagger: 0.08,
    duration: 0.6,
    ease: 'back.out(1.6)',
    scrollTrigger: { trigger: root.value, start: 'top 65%' },
  })
  }, root.value)
})
</script>

<template>
  <section id="moments" ref="root" class="content-section moments section container">
    <div class="section-head">
      <span class="kicker">02 — Your Binggrae Moment</span>
      <h2 class="moments__title ko-display">하루의 순간으로<br />제품 발견하기</h2>
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
        <div class="moments__art" :key="current.key" :data-stage="current.key">
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
.moments {
  color: var(--ink);
  padding-block: clamp(64px, 9vh, 104px);
}
.moments .section-head {
  gap: 12px;
  margin-bottom: clamp(24px, 3.5vh, 40px);
}
.moments__title {
  font-family: var(--font-brand);
  font-size: clamp(30px, calc(var(--content-unit) * 4.4), 56px);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.04em;
}
.moments__grid {
  display: grid;
  grid-template-columns: minmax(0, 48%) minmax(0, 1fr);
  gap: clamp(24px, 3vw, 48px);
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
  grid-template-columns: 5.5em minmax(0, 1fr) auto;
  align-items: baseline;
  gap: 12px;
  padding: clamp(12px, 1.6vh, 16px) 0;
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
  font-family: var(--font-ko-sub);
  font-size: clamp(21px, calc(var(--content-unit) * 2.4), 28px);
  font-weight: 500;
  line-height: 1.25;
}
.moments__name {
  font-family: var(--font-body);
  font-size: clamp(12px, 0.95vw, 15px);
  font-weight: 500;
  line-height: 1.3;
  letter-spacing: 0.06em;
}
.moments__panel {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 40%) minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  padding: clamp(20px, 2vw, 28px);
  color: var(--ink);
  min-height: 270px;
  border-width: 2px;
  box-shadow: 3px 3px 0 var(--ink);
}
.moments__spark {
  position: absolute;
  right: -14px;
  top: -14px;
}
.moments__art {
  width: 85%;
  max-width: 150px;
  justify-self: center;
  aspect-ratio: 300 / 360;
}
.moments__detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.moments__detail .ko-display {
  font-family: var(--font-ko-sub);
  font-size: clamp(22px, 1.8vw, 28px);
  font-weight: 500;
  line-height: 1.25;
}
.moments__note {
  margin-top: 20px;
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
  .moments__spark {
    right: -6px;
  }
  .moments__panel {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }
  .moments__art {
    width: 52%;
    max-width: 150px;
  }
}
</style>
