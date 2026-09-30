<script setup lang="ts">
import { archive } from '~/data/archive'
const active=ref(0)
let observer:IntersectionObserver|undefined
useHead({title:'단지, 기록으로 만나는 50년 — 빙그레할 틈'})
onMounted(()=>{observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting)active.value=Number((e.target as HTMLElement).dataset.chapter)},{rootMargin:'-25% 0px -45% 0px'});document.querySelectorAll('.book__chapter').forEach(e=>observer!.observe(e))})
onBeforeUnmount(()=>observer?.disconnect())
</script>
<template>
 <main class="book">
  <header class="book__nav"><NuxtLink to="/" class="btn btn--sm">← 빙그레할 틈</NuxtLink><span class="en-display">THE DANJI ARCHIVE</span><span>{{ active+1 }} / 06</span></header>
  <div class="book__intro"><p class="kicker">1974 → TODAY</p><h1 class="ko-display">작은 단지에<br>담긴 큰 시간.</h1><p>공식 기록과 이미지로 다시 만나는 바나나맛우유.<br>스크롤하며 여섯 장면을 펼쳐보세요.</p><a href="#chapter-0" class="btn btn--dark">이야기 펼치기 ↓</a></div>
  <div class="book__layout">
   <figure class="book__image"><Transition name="archive" mode="out-in"><img :key="active" :src="archive[active]!.image" :alt="archive[active]!.caption" /></Transition><figcaption>{{ archive[active]!.caption }}</figcaption></figure>
   <div><section v-for="(item,i) in archive" :id="`chapter-${i}`" :key="item.no" class="book__chapter" :data-chapter="i"><span class="book__number en-display">{{ item.no }}</span><p class="kicker">{{ item.tag }}</p><h2 class="ko-display">{{ item.title }}</h2><p>{{ item.text }}</p><a :href="item.source" target="_blank" rel="noopener">공식 기록 읽기 ↗</a><NuxtLink v-if="i===5" to="/#your-moment" class="btn btn--dark">나의 틈 카드 만들기 →</NuxtLink></section></div>
  </div>
  <footer>사진·자료: 빙그레 공식 제품 소개 및 2024년 보도자료. 과거 패키지를 임의로 재현하지 않았습니다.</footer>
 </main>
</template>
<style scoped>
.book{background:#fff6e0;color:#1a1a1a;min-height:100vh}.book__nav{position:sticky;top:0;z-index:5;background:#fff6e0f2;border-bottom:2px solid;padding:16px 5%;display:flex;align-items:center;justify-content:space-between}.book__intro{padding:10vh 8%;background:#ffd43b;display:grid;gap:24px}.book__intro h1{font-size:clamp(52px,8vw,120px);line-height:1.15}.book__intro p{line-height:1.8}.book__intro .btn{justify-self:start}.book__layout{display:grid;grid-template-columns:1fr 1fr;gap:7vw;padding:0 7vw}.book__image{position:sticky;top:110px;height:70vh;align-self:start;display:flex;flex-direction:column;justify-content:center;margin:0}.book__image img{width:100%;height:85%;object-fit:contain;border-radius:18px}.book__image figcaption{font-size:13px;line-height:1.7;padding-top:16px}.book__chapter{min-height:85vh;scroll-margin-top:100px;display:flex;flex-direction:column;align-items:start;justify-content:center;gap:24px;padding:48px 0}.book__number{font-size:90px;color:#ed3025}.book__chapter h2{font-size:clamp(32px,3vw,48px);line-height:1.35}.book__chapter>p:not(.kicker){font-size:18px;line-height:1.85}.book__chapter>a:not(.btn){text-decoration:underline}.book footer{padding:40px 7%;border-top:2px solid;font-size:14px;line-height:1.7}.archive-enter-active,.archive-leave-active{transition:opacity .25s,transform .25s}.archive-enter-from,.archive-leave-to{opacity:0;transform:translateY(15px)}
@media(max-width:760px){.book__nav .en-display{display:none}.book__layout{grid-template-columns:1fr;gap:0}.book__image{height:36svh;top:78px;z-index:2;background:#fff6e0;padding:12px 0}.book__image figcaption{font-size:11px}.book__chapter{min-height:75svh;padding-top:70px;scroll-margin-top:44svh}.book__number{font-size:56px}}
@media(prefers-reduced-motion:reduce){.archive-enter-active,.archive-leave-active{transition:none}}
</style>
