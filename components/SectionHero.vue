<script setup lang="ts">
import gsap from 'gsap'
import { brand, hero } from '~/data/content'

// 빽빽한 일정 타이포 → 스크롤하면 단어 사이가 벌어지며 가운데에 세로 틈이 생기고 → 그 틈으로 제품 등장
const props = defineProps<{ started: boolean }>()
const root = ref<HTMLElement>()
const pin = ref<HTMLElement>()
let ctx: gsap.Context | undefined

// 화면을 가득 채우도록 일정 목록을 반복
const tokens = [...hero.schedule, ...hero.schedule, ...hero.schedule].slice(0, 30)

useSectionColor(root, () => ({ bg: '#ffd43b' }))

/**
 * 각 토큰이 최종적으로 이동할 x값.
 * - 같은 줄에서 가운데를 기준으로 왼쪽/오른쪽 그룹으로 나눈다.
 * - 그룹 전체를 틈(gap) 밖으로 밀어낸 뒤, 중앙에서 멀수록 조금 더 밀어 단어 사이도 벌어지게 한다.
 */
function computeShifts(els: HTMLElement[]) {
  const cx = window.innerWidth / 2
  const gapHalf = Math.max(110, root.value!.querySelector<HTMLElement>('.hero__gap')!.offsetWidth * 0.62)
  const rows = new Map<number, HTMLElement[]>()
  els.forEach((el) => {
    const key = Math.round(el.offsetTop / 10)
    rows.set(key, [...(rows.get(key) ?? []), el])
  })
  const shifts = new Map<HTMLElement, number>()
  rows.forEach((row) => {
    const rects = row.map((el) => ({ el, left: el.offsetLeft, right: el.offsetLeft + el.offsetWidth }))
    const left = rects.filter((r) => (r.left + r.right) / 2 < cx)
    const right = rects.filter((r) => (r.left + r.right) / 2 >= cx)
    const pushL = Math.max(0, ...left.map((r) => r.right - (cx - gapHalf)))
    const pushR = Math.max(0, ...right.map((r) => cx + gapHalf - r.left))
    left.forEach((r) => shifts.set(r.el, -pushL - (cx - r.right) * 0.22))
    right.forEach((r) => shifts.set(r.el, pushR + (r.left - cx) * 0.22))
  })
  return shifts
}

onMounted(() => {
  ctx = gsap.context(() => {
    const els = gsap.utils.toArray<HTMLElement>('.hero__token')
    let shifts = computeShifts(els)

    gsap.set(els, { opacity: 0, yPercent: 60 })

    gsap
      .timeline({
        scrollTrigger: {
          trigger: pin.value,
          start: 'top top',
          end: () => `+=${window.innerHeight * 2.2}`,
          pin: true,
          scrub: 0.8,
          invalidateOnRefresh: true,
          onRefreshInit: () => {
            gsap.set(els, { x: 0 })
            shifts = computeShifts(els)
          },
        },
      })
      .to('.hero__intro', { opacity: 0, y: -40, duration: 0.25 }, 0)
      .to(els, { x: (_i: number, el: HTMLElement) => shifts.get(el) ?? 0, ease: 'power2.inOut', duration: 1 }, 0)
      .to(els, { opacity: 0.16, duration: 0.5 }, 0.45)
      .fromTo('.hero__product', { scale: 0, rotate: -30 }, { scale: 1, rotate: 0, ease: 'back.out(1.6)', duration: 0.6 }, 0.5)
      .fromTo('.hero__spark', { scale: 0 }, { scale: 1, stagger: 0.05, duration: 0.3, ease: 'back.out(3)' }, 0.75)
      .fromTo('.hero__tag-line', { yPercent: 100, opacity: 0 }, { yPercent: 0, opacity: 1, stagger: 0.12, duration: 0.4 }, 0.85)
  }, root.value)
})

// 프리로더가 닫히면 일정이 쏟아지듯 등장
watch(
  () => props.started,
  (on: boolean) => {
    if (!on) return
    gsap.to(root.value!.querySelectorAll('.hero__token'), { yPercent: 0, opacity: 1, duration: 0.7, stagger: { each: 0.02, from: 'random' }, ease: 'back.out(1.6)' })
    gsap.from(root.value!.querySelectorAll('.hero__intro > *'), { scale: 0.4, opacity: 0, delay: 0.5, stagger: 0.1, ease: 'back.out(2)' })
  },
)

onBeforeUnmount(() => ctx?.revert())
</script>

<template>
  <section id="top" ref="root" class="hero">
    <div ref="pin" class="hero__pin">
      <div class="hero__schedule" aria-hidden="true">
        <span v-for="(t, i) in tokens" :key="i" class="hero__token" :class="{ '--pop': i % 7 === 3 }">
          <small>{{ t[0] }}</small>{{ t[1] }}
        </span>
      </div>

      <div class="hero__intro">
        <h1 class="hero__question ko-display card">{{ hero.question }}</h1>
        <p class="hero__scroll kicker card">Scroll ↓</p>
      </div>

      <div class="hero__gap">
        <SparkleStar class="hero__spark" :size="40" style="left: -18%; top: 8%" />
        <SparkleStar class="hero__spark" :size="28" style="right: -14%; top: 30%" />
        <SparkleStar class="hero__spark" :size="32" style="left: -8%; bottom: 10%" />
        <div class="hero__product" data-stage="bananaMilk" data-stage-anim="scale">
          <ProductArt product="bananaMilk" />
        </div>
      </div>

      <p class="hero__tagline ko-display size-md">
        <span class="hero__tag-line --l sticker-text">{{ brand.tagline[0] }}</span>
        <span class="hero__tag-line --r sticker-text">{{ brand.tagline[1] }}</span>
      </p>
    </div>
  </section>
</template>

<style scoped>
.hero__pin {
  position: relative;
  height: 100vh;
  height: 100svh;
  overflow: hidden;
}
.hero__schedule {
  position: absolute;
  inset: 0;
  display: flex;
  flex-wrap: wrap;
  align-content: center;
  justify-content: center;
  gap: 0 clamp(10px, 1.4vw, 24px);
  padding: 76px 12px 150px;
}
.hero__token {
  display: inline-flex;
  align-items: flex-start;
  gap: 4px;
  font-family: var(--font-ko-display);
  font-size: clamp(34px, 7vw, 124px);
  line-height: 1;
  white-space: nowrap;
  will-change: transform;
}
.hero__token small {
  font-family: var(--font-en-display);
  font-size: 0.26em;
  letter-spacing: 0.04em;
  margin-top: 0.3em;
}
.hero__token.--pop {
  color: var(--cream);
  -webkit-text-stroke: 0.05em var(--ink);
  paint-order: stroke fill;
  text-shadow: 0.05em 0.06em 0 var(--ink);
}
.hero__intro {
  position: absolute;
  left: 50%;
  bottom: clamp(24px, 6vh, 64px);
  translate: -50% 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: calc(100% - var(--gutter) * 2);
  text-align: center;
}
.hero__question {
  padding: 0.3em 0.7em;
  font-size: clamp(22px, 3vw, 48px);
  transform: rotate(-2deg);
}
.hero__scroll {
  padding: 4px 12px;
  border-radius: 999px;
  animation: nudge 1.4s ease-in-out infinite;
}
@keyframes nudge {
  50% { transform: translateY(6px); }
}
.hero__gap {
  position: absolute;
  left: 50%;
  top: 46%;
  width: clamp(150px, 17vw, 270px);
  aspect-ratio: 300 / 360;
  translate: -50% -50%;
}
.hero__spark {
  position: absolute;
}
.hero__product {
  width: 100%;
  height: 100%;
  transform: scale(0);
}
.hero__tagline {
  position: absolute;
  inset: 0;
  pointer-events: none;
  margin: 0;
}
.hero__tag-line {
  position: absolute;
  top: 46%;
  translate: 0 -50%;
  display: block;
  opacity: 0;
  font-size: clamp(22px, 2.4vw, 40px);
}
.hero__tag-line.--l {
  right: calc(50% + clamp(100px, 11vw, 180px));
  text-align: right;
}
.hero__tag-line.--r {
  left: calc(50% + clamp(100px, 11vw, 180px));
}
@media (max-width: 760px) {
  .hero__schedule {
    padding: 64px 8px 170px;
    gap: 0 8px;
  }
  .hero__token {
    font-size: 11.5vw;
  }
  .hero__tag-line {
    left: 0 !important;
    right: 0 !important;
    text-align: center !important;
    translate: none;
  }
  .hero__tag-line.--l {
    top: 12%;
  }
  .hero__tag-line.--r {
    top: auto;
    bottom: 16%;
  }
}
</style>
