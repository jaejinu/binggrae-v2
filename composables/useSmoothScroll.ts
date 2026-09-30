import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

let lenis: Lenis | null = null

export function useSmoothScroll() {
  function init() {
    if (lenis) return lenis
    lenis = new Lenis({ lerp: 0.09 })
    lenis.on('scroll', ScrollTrigger.update)
    gsap.ticker.add((time) => lenis?.raf(time * 1000))
    gsap.ticker.lagSmoothing(0)
    return lenis
  }

  function scrollTo(target: string | number) {
    if (lenis) lenis.scrollTo(target, { offset: 0, duration: 1.6 })
    else if (typeof target === 'string') document.querySelector(target)?.scrollIntoView({ behavior: 'smooth' })
  }

  return {
    init,
    scrollTo,
    stop: () => lenis?.stop(),
    start: () => lenis?.start(),
  }
}
