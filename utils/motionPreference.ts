// Respect the OS preference unless the visitor explicitly enables this site's motion.
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
