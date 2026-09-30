<script setup lang="ts">
import { brand, nav } from '~/data/content'

import { ScrollTrigger } from 'gsap/ScrollTrigger'

const { scrollTo, stop, start } = useSmoothScroll()
const { blip } = useSound()
const menuOpen = ref(false)
const hidden = ref(false)
let st: ScrollTrigger | undefined
const header = ref<HTMLElement>()
const burger = ref<HTMLButtonElement>()
watch(menuOpen, async (open: boolean) => {
  if (open) { hidden.value = false; stop(); await nextTick(); header.value?.querySelector<HTMLAnchorElement>('.header__mobile a')?.focus() }
  else { start(); burger.value?.focus({ preventScroll: true }) }
})
function onKey(event: KeyboardEvent) {
  if (!menuOpen.value) return
  if (event.key === 'Escape') { event.preventDefault(); menuOpen.value = false }
  if (event.key === 'Tab') {
    const nodes = Array.from((header.value as HTMLElement).querySelectorAll<HTMLElement>('a,button')).filter(e => e.getClientRects().length)
    const first = nodes[0]!, last = nodes[nodes.length - 1]!
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
  }
}

// 내려갈 때 숨고, 올라갈 때 다시 등장
onMounted(() => {
  st = ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => {
      hidden.value = self.direction === 1 && self.scroll() > window.innerHeight * 0.5 && !menuOpen.value
    },
  })
})
onBeforeUnmount(() => st?.kill())
const left = nav.slice(0, 3)
const right = nav.slice(3)

async function go(href: string) {
  blip(1.2)
  menuOpen.value = false
  await nextTick()
  scrollTo(href)
}
</script>

<template>
  <header ref="header" class="header" :class="{ '--hidden': hidden }" @keydown="onKey">
    <div class="header__bar container">
      <nav class="header__side --start" aria-label="주요 메뉴">
        <a v-for="l in left" :key="l.href" :href="l.href" class="header__link" @click.prevent="go(l.href)">{{ l.label }}</a>
      </nav>
      <a href="#top" class="header__logo ko-display sticker-text" @click.prevent="go('#top')">{{ brand.name }}</a>
      <nav class="header__side --end" aria-label="보조 메뉴">
        <a v-for="l in right" :key="l.href" :href="l.href" class="header__link" @click.prevent="go(l.href)">{{ l.label }}</a>
        <SoundSwitcher />
        <button ref="burger" class="header__burger btn btn--sm" :aria-expanded="menuOpen" aria-controls="mobile-menu" aria-label="메뉴" @click="menuOpen = !menuOpen">
          {{ menuOpen ? '닫기' : '메뉴' }}
        </button>
      </nav>
    </div>

    <Transition name="drop">
      <nav v-if="menuOpen" id="mobile-menu" class="header__mobile" aria-label="모바일 메뉴">
        <a v-for="l in nav" :key="l.href" :href="l.href" class="en-display size-lg sticker-text" @click.prevent="go(l.href)">{{ l.label }}</a>
      </nav>
    </Transition>
  </header>
</template>

<style scoped>
.header {
  position: fixed;
  inset: 0 0 auto;
  z-index: 100;
  padding-top: max(12px, env(safe-area-inset-top));
  pointer-events: none;
  transition: transform 0.45s cubic-bezier(0.6, 0, 0.2, 1);
}
.header.--hidden {
  transform: translateY(-120%);
}
.header__bar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: clamp(20px, 3vw, 56px);
  max-width: 1280px;
  margin: 0 auto;
}
.header__bar > *,
.header__mobile {
  pointer-events: auto;
}
.header__side {
  display: flex;
  align-items: center;
  gap: clamp(14px, 2vw, 32px);
}
.header__side.--end {
  justify-content: flex-end;
}
.header__link {
  position: relative;
  font-family: var(--font-en-display);
  font-size: 15px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 6px 12px;
  border: 2px solid var(--ink);
  border-radius: 999px;
  background: var(--cream);
  box-shadow: 2px 2px 0 var(--ink);
  translate: var(--mx, 0px) var(--my, 0px);
  transition: background-color 0.2s, transform 0.15s;
}
.header__link:hover {
  background: var(--banana);
  height: 100dvh;
  overflow-y: auto;
  transform: translateY(-2px);
}
.header__logo {
  font-size: clamp(26px, 2.4vw, 40px);
  white-space: nowrap;
  transition: transform 0.25s;
}
.header__logo:hover {
  transform: rotate(-3deg) scale(1.05);
}
.header__burger {
  display: none;
}
.header__mobile {
  position: fixed;
  inset: 0;
  z-index: -1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
  padding: 96px var(--gutter) var(--gutter);
  background: var(--banana);
}
.drop-enter-active,
.drop-leave-active {
  transition: clip-path 0.5s cubic-bezier(0.7, 0, 0.2, 1);
}
.drop-enter-from,
.drop-leave-to {
  clip-path: inset(0 0 100% 0);
}
.drop-enter-to,
.drop-leave-from {
  clip-path: inset(0 0 0 0);
}
@media (max-width: 1000px) {
  .header__side.--start,
  .header__link {
    display: none;
  }
  .header__bar {
    grid-template-columns: auto 1fr;
  }
  .header__burger {
    display: inline-flex;
  }
}
</style>
