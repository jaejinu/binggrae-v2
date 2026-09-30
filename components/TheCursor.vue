<script setup lang="ts">
import gsap from 'gsap'

// 스티커 커서 + 클릭 반짝이 + 버튼 자석 효과. 마우스(정밀 포인터)에서만 커서를 켠다.
const ring = ref<HTMLElement>()
const label = ref('')
const hovering = ref(false)
const enabled = ref(false)
const { blip } = useSound()

const INTERACTIVE = 'a, button, [role="tab"], label, input'
const MAGNETIC = '.btn, .header__link, [data-magnetic]'

let magnetEl: HTMLElement | null = null
const cleanups: (() => void)[] = []

function on<K extends keyof WindowEventMap>(type: K, fn: (e: WindowEventMap[K]) => void, opts?: AddEventListenerOptions) {
  window.addEventListener(type, fn, opts)
  cleanups.push(() => window.removeEventListener(type, fn))
}

function burst(x: number, y: number) {
  const colors = ['#ffd43b', '#ff9ebd', '#7ed957', '#8fd3ff', '#fff6e0']
  for (let i = 0; i < 7; i++) {
    const s = document.createElement('span')
    s.className = 'cursor-spark'
    s.style.left = `${x}px`
    s.style.top = `${y}px`
    s.style.background = colors[i % colors.length]
    document.body.appendChild(s)
    const a = (i / 7) * Math.PI * 2 + Math.random() * 0.4
    const d = 36 + Math.random() * 34
    gsap.fromTo(
      s,
      { scale: 0.2, rotate: 0 },
      {
        x: Math.cos(a) * d,
        y: Math.sin(a) * d,
        scale: 1,
        rotate: 180,
        opacity: 0,
        duration: 0.6 + Math.random() * 0.2,
        ease: 'power3.out',
        onComplete: () => s.remove(),
      },
    )
  }
}

onMounted(() => {
  enabled.value = window.matchMedia('(pointer: fine)').matches
  const html = document.documentElement

  if (enabled.value) {
    html.classList.add('has-cursor')
    const xTo = gsap.quickTo(ring.value!, 'x', { duration: 0.25, ease: 'power3.out' })
    const yTo = gsap.quickTo(ring.value!, 'y', { duration: 0.25, ease: 'power3.out' })

    on('pointermove', (e) => {
      xTo(e.clientX)
      yTo(e.clientY)
      const t = e.target as HTMLElement
      const zone = t.closest<HTMLElement>('[data-cursor]')
      label.value = zone?.dataset.cursor ?? ''
      hovering.value = !!t.closest(INTERACTIVE)

      // 자석: 버튼이 포인터 쪽으로 살짝 끌려옴 (CSS translate 속성 사용 → hover transform과 충돌 없음)
      const m = t.closest<HTMLElement>(MAGNETIC)
      if (magnetEl && magnetEl !== m) {
        gsap.to(magnetEl, { '--mx': '0px', '--my': '0px', duration: 0.5, ease: 'elastic.out(1, 0.4)' })
        magnetEl = null
      }
      if (m) {
        const r = m.getBoundingClientRect()
        const dx = (e.clientX - (r.left + r.width / 2)) * 0.25
        const dy = (e.clientY - (r.top + r.height / 2)) * 0.35
        gsap.to(m, { '--mx': `${dx}px`, '--my': `${dy}px`, duration: 0.3, ease: 'power3.out' })
        magnetEl = m
      }
    })
    on('pointerdown', () => gsap.to(ring.value!, { scale: 0.7, duration: 0.15 }))
    on('pointerup', () => gsap.to(ring.value!, { scale: 1, duration: 0.4, ease: 'elastic.out(1, 0.4)' }))
    document.addEventListener('mouseleave', () => gsap.to(ring.value!, { opacity: 0 }))
    document.addEventListener('mouseenter', () => gsap.to(ring.value!, { opacity: 1 }))
  }

  // 클릭 반짝이 (터치 포함)
  on('click', (e) => {
    const t = e.target as HTMLElement
    if (t.closest(INTERACTIVE)) {
      burst(e.clientX, e.clientY)
      blip(1.4)
    }
  })
})

onBeforeUnmount(() => {
  cleanups.forEach((f) => f())
  document.documentElement.classList.remove('has-cursor')
})
</script>

<template>
  <div v-show="enabled" ref="ring" class="cursor" :class="{ '--hover': hovering, '--label': label }" aria-hidden="true">
    <span class="cursor__label">{{ label }}</span>
  </div>
</template>

<style scoped>
.cursor {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  margin: -11px 0 0 -11px;
  border: 2.5px solid var(--ink);
  border-radius: 50%;
  background: var(--cream);
  box-shadow: 2px 2px 0 var(--ink);
  pointer-events: none;
  transition: width 0.25s, height 0.25s, margin 0.25s, background-color 0.25s;
}
.cursor.--hover {
  width: 44px;
  height: 44px;
  margin: -22px 0 0 -22px;
  background: var(--banana);
}
.cursor.--label {
  width: 72px;
  height: 72px;
  margin: -36px 0 0 -36px;
  background: var(--ink);
}
.cursor__label {
  font-family: var(--font-en-display);
  font-size: 14px;
  letter-spacing: 0.08em;
  color: var(--cream);
  opacity: 0;
  transition: opacity 0.2s;
}
.--label .cursor__label {
  opacity: 1;
}
</style>

<style>
html.has-cursor,
html.has-cursor * {
  cursor: none !important;
}
html.has-cursor input {
  cursor: text !important;
}
.cursor-spark {
  position: fixed;
  z-index: 1999;
  width: 10px;
  height: 10px;
  margin: -5px 0 0 -5px;
  border: 2px solid #1a1a1a;
  pointer-events: none;
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  border-radius: 0;
}
</style>
