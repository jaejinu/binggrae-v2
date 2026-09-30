export default defineNuxtPlugin({
  name: 'motion-preference',
  enforce: 'pre',
  setup() {
    const requested = new URLSearchParams(location.search).get('motion')
    // New visitors see the complete experience; preserve an explicit system choice.
    let full = requested !== 'system'
    try {
      if (requested === 'full' || requested === 'system') {
        localStorage.setItem('binggrae-motion', requested)
      } else {
        full = localStorage.getItem('binggrae-motion') !== 'system'
      }
    } catch { /* Explicit URL selection also works when storage is unavailable. */ }
    document.documentElement.dataset.motion = full ? 'full' : 'system'
  },
})
