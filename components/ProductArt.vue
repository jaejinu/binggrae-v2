<script setup lang="ts">
import { products, type ProductKey } from '~/data/content'

// 기본값은 형태만 단순화한 오리지널 스티커 일러스트(로고·실제 패키지 없음).
// public/products/ 에 이미지를 넣으면 자동으로 그 이미지로 교체된다.
const props = defineProps<{ product: ProductKey }>()
const info = computed(() => products.find((p) => p.key === props.product)!)
const hasImage = useImageAvailable(() => info.value.image)
</script>

<template>
  <img v-if="hasImage" :src="info.image" :alt="info.nameKo" class="product-art product-art--img" draggable="false" />
  <svg v-else class="product-art" viewBox="0 0 300 360" aria-hidden="true">
    <g stroke="#1a1a1a" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
      <!-- 단지 모양 우유 -->
      <g v-if="product === 'bananaMilk'">
        <path d="M112 70 h76 v26 c0 14 44 34 50 90 c6 60 -14 118 -88 130 c-74 -12 -94 -70 -88 -130 c6 -56 50 -76 50 -90 z" fill="#1a1a1a" transform="translate(9 9)" />
        <path d="M112 70 h76 v26 c0 14 44 34 50 90 c6 60 -14 118 -88 130 c-74 -12 -94 -70 -88 -130 c6 -56 50 -76 50 -90 z" fill="#ffd43b" />
        <path d="M70 180 c40 18 120 18 160 0" fill="none" stroke-width="4" opacity=".55" />
        <rect x="104" y="52" width="92" height="24" rx="8" fill="#fff6e0" />
        <ellipse cx="150" cy="52" rx="46" ry="10" fill="#e9e9e9" />
        <path d="M96 120 c-14 20 -20 50 -16 76" fill="none" stroke="#fff6e0" stroke-width="9" />
        <path d="M200 42 l30 -34" stroke-width="8" />
      </g>
      <!-- 떠먹는 요거트 컵 -->
      <g v-else-if="product === 'yoplait'">
        <path d="M78 110 h144 l-18 200 h-108 z" fill="#1a1a1a" transform="translate(9 9)" />
        <path d="M78 110 h144 l-18 200 h-108 z" fill="#fff6e0" />
        <path d="M84 170 h132 l-4 44 h-124 z" fill="#ff9ebd" />
        <ellipse cx="150" cy="110" rx="80" ry="18" fill="#ff5f8f" />
        <path d="M150 104 c30 -40 90 -60 110 -40 c-10 10 -40 40 -104 50" fill="#e9e9e9" />
        <g transform="rotate(-28 90 80)">
          <rect x="60" y="20" width="16" height="90" rx="8" fill="#fff6e0" />
          <ellipse cx="68" cy="20" rx="20" ry="26" fill="#fff6e0" />
        </g>
      </g>
      <!-- 콘 아이스크림 -->
      <g v-else-if="product === 'bravo'">
        <path d="M86 160 L150 340 L214 160 Z" fill="#1a1a1a" transform="translate(9 9)" />
        <path d="M86 160 L150 340 L214 160 Z" fill="#e7a95b" />
        <path d="M104 210 l72 0 M116 250 l48 0 M110 180 l40 110 M190 180 l-40 110" stroke-width="3.5" fill="none" opacity=".6" />
        <path d="M94 196 L206 196 L196 232 L104 232 Z" fill="#3d63dd" />
        <path d="M78 164 c0 -40 30 -64 72 -64 c42 0 72 24 72 64 z" fill="#fff6e0" />
        <path d="M100 118 c14 -36 86 -36 100 0" fill="#fff6e0" />
        <path d="M84 150 c20 10 40 -8 60 4 c20 12 44 -6 70 2 l6 8 H78 z" fill="#6b3a1e" />
        <circle cx="120" cy="120" r="5" fill="#e8542f" /><circle cx="170" cy="112" r="5" fill="#ffd43b" /><circle cx="150" cy="96" r="5" fill="#7ed957" />
      </g>
      <!-- 붕어 모양 샌드 -->
      <g v-else>
        <path d="M40 180 c20 -70 110 -96 170 -60 l50 -40 c-6 40 -6 84 0 124 l-50 -40 c-60 40 -150 14 -170 -24 z" fill="#1a1a1a" transform="translate(9 9)" />
        <path d="M40 180 c20 -70 110 -96 170 -60 l50 -40 c-6 40 -6 84 0 124 l-50 -40 c-60 40 -150 14 -170 -24 z" fill="#d98a3d" />
        <path d="M46 186 c30 16 120 20 164 -4" fill="none" stroke="#fff6e0" stroke-width="10" />
        <circle cx="84" cy="160" r="9" fill="#1a1a1a" stroke="none" />
        <path d="M118 140 q10 14 0 28 M140 136 q10 18 0 36 M162 138 q10 16 0 32" fill="none" stroke-width="4" />
        <path d="M60 196 q10 6 20 4" fill="none" stroke-width="4" />
      </g>
    </g>
  </svg>
</template>

<style scoped>
.product-art {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
}
.product-art--img {
  object-fit: contain;
  filter: drop-shadow(0 18px 16px rgba(26, 26, 26, 0.22));
  animation: float 4.2s ease-in-out infinite;
}
/* 살짝 떠 있는 느낌 */
@keyframes float {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-6px) rotate(1deg); }
}
@media (pointer: coarse), (max-width: 800px) {
  .product-art--img { animation: none; }
}
</style>
