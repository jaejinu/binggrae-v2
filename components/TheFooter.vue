<script setup lang="ts">
import { brand } from '~/data/content'
const year = new Date().getFullYear()
</script>

<template>
  <footer class="footer container">
    <p class="footer__tag ko-display size-lg sticker-text">
      <span>{{ brand.tagline[0] }}</span>
      <span>{{ brand.tagline[1] }}</span>
    </p>
    <p class="en-display footer__en">{{ brand.nameEn }}</p>
    <div class="footer__bar body-m">
      <span>© {{ year }} {{ brand.name }}</span>
      <span>본 사이트는 빙그레 브랜드 리뉴얼 콘셉트 프로젝트이며, 공식 사이트가 아닙니다.</span>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding-block: clamp(80px, 14vh, 160px) max(24px, env(safe-area-inset-bottom));
  background: var(--red);
  color: var(--cream);
  text-align: center;
}
.footer__tag {
  display: flex;
  flex-direction: column;
}
.footer__en {
  font-size: clamp(18px, 1.6vw, 26px);
  letter-spacing: 0.04em;
}
.footer__bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  margin-top: clamp(40px, 8vh, 96px);
  padding-top: 18px;
  border-top: 2px solid rgba(255, 246, 224, 0.4);
  font-size: 13px;
}
</style>
