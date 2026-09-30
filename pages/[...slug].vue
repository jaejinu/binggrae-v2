<script setup lang="ts">
// 팀원 상세페이지 / 브랜드 스토리 / 브랜드북이 연결될 자리
const route = useRoute()
const path = computed(() => route.path)
</script>

<template>
  <main class="soon">
    <p class="kicker">Coming soon</p>
    <h1 class="ko-display size-xl sticker-text">준비 중인 페이지</h1>
    <p class="body-l"><code>{{ path }}</code> 에 상세 페이지가 연결될 예정입니다.</p>
    <NuxtLink to="/" class="btn">메인으로 →</NuxtLink>
  </main>
</template>

<style scoped>
.soon {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: var(--gutter);
  background: var(--banana);
  text-align: center;
}
</style>
