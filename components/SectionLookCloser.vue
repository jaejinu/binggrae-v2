<script setup lang="ts">
import gsap from 'gsap'
import { products, iconOrder, type ProductKey } from '~/data/content'
import type { Mode } from './ProductScene.vue'

// 04. WHY WE REMEMBER — 제품에는 기억될 이유가 있다
const list = iconOrder.map((k) => products.find((p) => p.key === k)!)
const productKey = ref<ProductKey>('bananaMilk')
const mode = ref<Mode>('rotate')
const current = computed(() => products.find((p) => p.key === productKey.value)!)
const root = ref<HTMLElement>()

const modes: { key: Mode; label: string }[] = [
  { key: 'rotate', label: 'Rotate' },
  { key: 'zoom', label: 'Zoom' },
  { key: 'explode', label: 'Explode' },
  { key: 'detail', label: 'Detail' },
]

watch(productKey, async () => {
  mode.value = 'rotate'
  await nextTick()
  gsap.fromTo(root.value!.querySelectorAll('.look__q, .look__a'), { y: 20, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.08, duration: 0.5 })
})
</script>

<template>
  <section id="look-closer" ref="root" class="look section container" :style="{ background: current.bg, color: current.ink }">
    <div class="section-head">
      <span class="kicker">04 — Why We Remember</span>
      <h2 class="ko-display size-xl sticker-text">제품에는<br />기억될 이유가 있다</h2>
    </div>

    <div class="look__tabs" role="tablist">
      <button
        v-for="p in list"
        :key="p.key"
        class="btn btn--sm"
        role="tab"
        :aria-selected="p.key === productKey"
        :class="{ '--active': p.key === productKey }"
        @click="productKey = p.key"
      >
        {{ p.name }}
      </button>
    </div>

    <div class="look__grid">
      <div class="look__stage card">
        <ClientOnly>
          <ProductScene :product="productKey" :mode="mode" />
        </ClientOnly>
        <span class="look__hint body-m">드래그해서 돌려보세요</span>
        <div class="look__modes">
          <button
            v-for="m in modes"
            :key="m.key"
            class="btn btn--sm"
            :aria-pressed="m.key === mode"
            @click="mode = m.key"
          >
            {{ m.label }}
          </button>
        </div>
      </div>

      <div class="look__text">
        <span class="kicker">{{ current.name }}</span>
        <h3 class="look__q ko-display size-lg">{{ current.question }}</h3>
        <p class="look__a body-l">{{ current.answer }}</p>
        <Transition name="fade">
          <ul v-if="mode === 'detail' || mode === 'explode'" class="look__details">
            <li v-for="(d, i) in current.details" :key="d" class="card">
              <span class="en-display">{{ String(i + 1).padStart(2, '0') }}</span> {{ d }}
            </li>
          </ul>
        </Transition>
        <NuxtLink :to="current.href" class="btn btn--dark">상세 페이지 미리보기 →</NuxtLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.look {
  transition: background-color 0.6s, color 0.6s;
}
.look__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}
.look__grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: clamp(24px, 4vw, 64px);
  align-items: center;
}
.look__stage {
  position: relative;
  aspect-ratio: 1;
  max-height: 72vh;
  overflow: hidden;
  color: var(--ink);
}
.look__hint {
  position: absolute;
  left: 18px;
  top: 14px;
  font-size: 13px;
  opacity: 0.6;
  pointer-events: none;
}
.look__modes {
  position: absolute;
  left: 50%;
  bottom: 16px;
  translate: -50% 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  width: calc(100% - 32px);
}
.look__text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 18px;
}
.look__details {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.look__details li {
  padding: 10px 14px;
  font-weight: 700;
  color: var(--ink);
  border-radius: 12px;
}
.look__details .en-display {
  margin-right: 6px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
@media (max-width: 900px) {
  .look__grid {
    grid-template-columns: 1fr;
  }
}
</style>
