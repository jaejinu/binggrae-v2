<script setup lang="ts">
import gsap from 'gsap'
import { products, iconOrder, type ProductKey } from '~/data/content'
import type { Mode } from './ProductScene.vue'

// 04. WHY WE REMEMBER — 제품에는 기억될 이유가 있다
const list = iconOrder.map((k) => products.find((p) => p.key === k)!)
const productKey = ref<ProductKey>('bananaMilk')
const mode = ref<Mode>('rotate')
const gesture=ref(0)
const side=ref('head')
const selected=useState<ProductKey>('chosen-product',()=> 'bananaMilk')
const actions={yoplait:'뚜껑을 열어볼까요?',samanco:'어디부터 열어볼까요?',bravo:'포장지를 내려볼까요?',bananaMilk:'단지 뒤의 한마디 찾기'}
const actionTitle=computed(()=>actions[productKey.value as ProductKey])
const touchAction=computed(()=>({yoplait:'뚜껑 열기',samanco:'붕어 열기',bravo:'포장 내리기',bananaMilk:'뒷면 보기'})[productKey.value as ProductKey])
function play(){mode.value='play';gesture.value=gesture.value>0?0:100}
const current = computed(() => products.find((p) => p.key === productKey.value)!)
const root = ref<HTMLElement>()
const { blip } = useSound()
function tabKey(event: KeyboardEvent) {
  const index = list.findIndex(p => p.key === productKey.value)
  const next = event.key === 'ArrowRight' ? (index + 1) % list.length : event.key === 'ArrowLeft' ? (index + list.length - 1) % list.length : event.key === 'Home' ? 0 : event.key === 'End' ? list.length - 1 : -1
  if (next < 0) return
  event.preventDefault()
  productKey.value = list[next]!.key
  root.value?.querySelector<HTMLButtonElement>(`#look-tab-${productKey.value}`)?.focus()
}

useSectionColor(root, () => ({ bg: current.value.bg, ink: current.value.ink }))
watch([productKey, mode], () => blip(1.2))

const modes: { key: Mode; label: string }[] = [
  { key: 'rotate', label: 'Rotate' },
  { key: 'zoom', label: 'Zoom' },
  { key: 'explode', label: 'Explode' },
  { key: 'detail', label: 'Detail' },
]

watch(productKey, async () => {
  mode.value = 'rotate'
  gesture.value=0
  selected.value=productKey.value
  await nextTick()
  if (!root.value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  gsap.fromTo(root.value!.querySelectorAll('.look__q, .look__a'), { y: 20, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.08, duration: 0.5 })
})
</script>

<template>
  <section id="look-closer" ref="root" class="look section container">
    <div class="section-head">
      <span class="kicker">04 — Why We Remember</span>
      <h2 class="ko-display size-xl sticker-text">제품에는<br />기억될 이유가 있다</h2>
    </div>

    <div class="look__tabs" role="tablist" aria-label="탐험할 제품" @keydown="tabKey">
      <button
        v-for="p in list"
        :key="p.key"
        class="btn btn--sm"
        role="tab"
        :id="`look-tab-${p.key}`"
        aria-controls="look-panel"
        :tabindex="p.key === productKey ? 0 : -1"
        :aria-selected="p.key === productKey"
        :class="{ '--active': p.key === productKey }"
        @click="productKey = p.key"
      >
        {{ p.name }}
      </button>
    </div>

    <div id="look-panel" class="look__grid" role="tabpanel" :aria-labelledby="`look-tab-${productKey}`">
      <div class="look__stage card">
        <ClientOnly>
          <ProductScene :product="productKey" :mode="mode" :gesture="gesture" :side="side" @update:gesture="gesture=$event" />
        </ClientOnly>
        <span class="look__hint body-m">{{ mode==='play' ? '제품을 움직이거나 아래 슬라이더로 조작해보세요' : '제품을 손가락으로 돌려보세요 · 바깥쪽은 스크롤' }}</span>
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
        <div class="look__touch-controls" data-lenis-prevent-touch>
          <button class="btn btn--dark btn--sm" @click="play">{{ gesture>0 && mode==='play' ? '되돌리기' : touchAction }}</button>
          <input type="range" min="0" max="100" :value="gesture" aria-label="제품 바로 조작" @input="mode='play';gesture=Number(($event.target as HTMLInputElement).value)" />
        </div>
      </div>

      <div class="look__text">
        <div class="look__play card">
          <h3 class="ko-display">{{ actionTitle }}</h3>
          <div v-if="productKey==='samanco'" class="look__sides"><button class="btn btn--sm" :aria-pressed="side==='head'" @click="side='head';mode='play';gesture=100">머리부터</button><button class="btn btn--sm" :aria-pressed="side==='tail'" @click="side='tail';mode='play';gesture=100">꼬리부터</button></div>
          <button class="btn btn--dark" @click="play">{{ gesture>0&&mode==='play'?'처음 모습으로':'직접 해보기' }}</button>
          <label>나만의 속도로 <input type="range" min="0" max="100" :value="gesture" aria-label="제품 체험 진행도" @input="mode='play';gesture=Number(($event.target as HTMLInputElement).value)" /></label>
          <p v-if="productKey==='bananaMilk'&&gesture>85&&mode==='play'" role="status">잠깐, 빙그레. 크게 웃을 일은 없어도, 빙그레할 틈은 있으니까.</p>
        </div>
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
.look__play{display:grid;gap:14px;padding:22px;color:#1a1a1a;width:100%}.look__play h3{font-size:24px}.look__play label{display:grid;gap:10px}.look__play input{width:100%;accent-color:#ed3025}.look__sides{display:flex;gap:8px}.look__play p{line-height:1.6}
.look__touch-controls { display: none; }
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

<style scoped>
@media (pointer: coarse), (max-width: 800px) {
  .look__stage { aspect-ratio: auto; height: 430px; max-height: none; }
  .look__stage :deep(.product-scene) { bottom: 112px; }
  .look__modes { bottom: 64px; gap: 5px; }
  .look__modes .btn { padding-inline: 10px; }
  .look__touch-controls { position: absolute; bottom: 12px; left: 14px; right: 14px; display: flex; gap: 12px; align-items: center; }
  .look__touch-controls button { flex-shrink: 0; min-height: 44px; }
  .look__touch-controls input { min-width: 0; width: 100%; height: 44px; accent-color: #ed3025; touch-action: none; }
  .look__hint { font-size: 11px; }
}
</style>
