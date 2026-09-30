import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

let lenis: Lenis | null = null
let nativeTouch = false
const tick = (time: number) => lenis?.raf(time * 1000)

export function useSmoothScroll() {
  function init() {
    if (lenis) return lenis
    nativeTouch = window.matchMedia('(pointer: coarse)').matches
    if (nativeTouch) return null
    lenis = new Lenis({ lerp: 0.09, smoothWheel: !prefersReducedMotion() })
    lenis.on('scroll', ScrollTrigger.update)
    gsap.ticker.add(tick)
    gsap.ticker.lagSmoothing(0)
    return lenis
  }

  function scrollTo(target: string | number) {
    const reduced = prefersReducedMotion()
    if (lenis) lenis.scrollTo(target, { offset: 0, duration: 1.2, immediate: reduced })
    else if (typeof target === 'string') document.querySelector(target)?.scrollIntoView({ behavior: reduced ? 'instant' : 'smooth' })
    else window.scrollTo({ top: target, behavior: reduced ? 'instant' : 'smooth' })
  }

  return {
    init,
    scrollTo,
    stop: () => { if (nativeTouch) document.documentElement.classList.add('touch-scroll-stopped'); else lenis?.stop() },
    start: () => { document.documentElement.classList.remove('touch-scroll-stopped'); lenis?.start() },
    destroy: () => { document.documentElement.classList.remove('touch-scroll-stopped'); gsap.ticker.remove(tick); lenis?.destroy(); lenis = null; nativeTouch = false },
  }
}
