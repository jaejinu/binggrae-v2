export default defineNuxtPlugin({
  name: 'motion-preference',
  enforce: 'pre',
  setup() {
    const requested = new URLSearchParams(location.search).get('motion')
    let full = requested === 'full'
    try {
      if (requested === 'full' || requested === 'system') {
        localStorage.setItem('binggrae-motion', requested)
      } else {
        full = localStorage.getItem('binggrae-motion') === 'full'
      }
    } catch { /* Explicit URL selection also works when storage is unavailable. */ }
    document.documentElement.dataset.motion = full ? 'full' : 'system'
  },
})
