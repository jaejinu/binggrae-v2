// Site motion is enabled by default; visitors may choose to follow their OS preference.
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return document.documentElement.dataset.motion !== 'full'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function motionMediaQuery(): string {
  return document.documentElement.dataset.motion === 'full'
    ? 'all'
    : '(prefers-reduced-motion: no-preference)'
}
