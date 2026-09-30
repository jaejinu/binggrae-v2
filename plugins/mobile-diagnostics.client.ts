export default defineNuxtPlugin({
  name: 'mobile-diagnostics',
  enforce: 'pre',
  setup(nuxtApp) {
    if (new URLSearchParams(location.search).get('diagnose') !== '1') return
    const errors = useState<string[]>('mobile-diagnostic-errors', () => [])
    const record = (error: unknown) => {
      errors.value = [...errors.value.slice(-3), String(error instanceof Error ? error.message : error).slice(0, 240)]
    }
    window.addEventListener('error', event => record(event.message))
    window.addEventListener('unhandledrejection', event => record(event.reason))
    nuxtApp.hook('vue:error', record)
  },
})
