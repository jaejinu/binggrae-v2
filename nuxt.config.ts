export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      htmlAttrs: { lang: 'ko' },
      title: '빙그레할 틈 — Everyday moments of small joy',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '크게 웃을 일은 없어도, 빙그레할 틈은 있으니까. 빙그레 브랜드 리뉴얼 콘셉트 프로젝트.' },
        { name: 'theme-color', content: '#ffd43b' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css' },
      ],
    },
  },
  build: { transpile: ['three'] },
})
