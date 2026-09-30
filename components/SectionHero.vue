<script setup lang="ts">
import gsap from 'gsap'
import { brand, hero } from '~/data/content'

// 빽빽한 일정 타이포 → 스크롤하면 글자 사이가 벌어지고 → 그 틈으로 제품 등장
const root = ref<HTMLElement>()
const pin = ref<HTMLElement>()
let ctx: gsap.Context | undefined

// 화면을 가득 채우도록 일정 목록을 반복
const tokens = [...hero.schedule, ...hero.schedule, ...hero.schedule].slice(0, 30)

onMounted(() => {
  ctx = gsap.context(() => {
    const els = gsap.utils.toArray<HTMLElement>('.hero__token')
    // 화면 중앙 기준 왼쪽/오른쪽 판단 (좌우로 밀려나며 가운데 틈이 생김)
    const side = (el: HTMLElement) => {
      const r = el.getBoundingClientRect()
      return r.left + r.width / 2 < window.innerWidth / 2 ? -1 : 1
    }
    const push = (el: HTMLElement) => {
      const r = el.getBoundingClientRect()
      const dist = Math.abs(r.left + r.width / 2 - window.innerWidth / 2)
      // 가운데 가까운 글자일수록 더 멀리
      return side(el) * (window.innerWidth * 0.22 + (window.innerWidth / 2 - dist) * 0.55)
    }

    gsap.from(els, { yPercent: 60, opacity: 0, duration: 0.7, stagger: 0.025, ease: 'back.out(1.6)' })

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: pin.value,
        start: 'top top',
        end: () => `+=${window.innerHeight * 2.2}`,
        pin: true,
        scrub: 0.8,
        invalidateOnRefresh: true,
      },
    })
    tl.to('.hero__intro', { opacity: 0, y: -40, duration: 0.25 }, 0)
      .to(els, { x: (_i: number, el: HTMLElement) => push(el), letterSpacing: '0.18em', ease: 'power2.inOut', duration: 1 }, 0)
      .to(els, { opacity: 0.12, duration: 0.6 }, 0.35)
      .fromTo('.hero__product', { scale: 0, rotate: -30 }, { scale: 1, rotate: 0, ease: 'back.out(1.6)', duration: 0.6 }, 0.45)
      .fromTo('.hero__spark', { scale: 0 }, { scale: 1, stagger: 0.05, duration: 0.3, ease: 'back.out(3)' }, 0.7)
      .fromTo('.hero__tag-line', { yPercent: 100, opacity: 0 }, { yPercent: 0, opacity: 1, stagger: 0.12, duration: 0.4 }, 0.8)
  }, root.value)
})

onBeforeUnmount(() => ctx?.revert())
</script>

<template>
  <section id="top" ref="root" class="hero">
    <div ref="pin" class="hero__pin">
      <div class="hero__schedule" aria-hidden="true">
        <span v-for="(t, i) in tokens" :key="i" class="hero__token en-display" :class="{ '--pop': i % 7 === 3 }">
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
        <div class="hero__product">
          <ProductArt product="bananaMilk" />
        </div>
      </div>

      <p class="hero__tagline ko-display size-md">
        <span class="hero__tag-line --l">{{ brand.tagline[0] }}</span>
        <span class="hero__tag-line --r">{{ brand.tagline[1] }}</span>
      </p>
    </div>
  </section>
</template>

<style scoped>
.hero {
  background: var(--banana);
}
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
  padding: 80px 12px 40px;
}
.hero__token {
  display: inline-flex;
  align-items: flex-start;
  gap: 4px;
  font-family: var(--font-ko-display);
  font-size: clamp(40px, 7.4vw, 132px);
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
  font-size: clamp(24px, 3vw, 48px);
  transform: rotate(-2deg);
}
.hero__scroll {
  padding: 4px 12px;
  border-radius: 999px;
}
.hero__scroll {
  animation: nudge 1.4s ease-in-out infinite;
}
@keyframes nudge {
  50% { transform: translateY(6px); }
}
.hero__gap {
  position: absolute;
  left: 50%;
  top: 50%;
  width: clamp(160px, 18vw, 280px);
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
  top: 50%;
  display: block;
  opacity: 0;
}
.hero__tag-line.--l {
  right: calc(50% + clamp(110px, 12vw, 190px));
  text-align: right;
}
.hero__tag-line.--r {
  left: calc(50% + clamp(110px, 12vw, 190px));
}
@media (max-width: 760px) {
  .hero__tag-line {
    left: 0 !important;
    right: 0 !important;
    text-align: center !important;
  }
  .hero__tag-line.--l {
    top: 14%;
  }
  .hero__tag-line.--r {
    top: auto;
    bottom: 14%;
  }
}
</style>
