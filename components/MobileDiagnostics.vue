<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const enabled = useRoute().query.diagnose === '1'
const expanded = ref(false)
const report = ref('진단 준비 중…')
const copied = ref(false)
const probe = ref<HTMLElement>()
const errors = useState<string[]>('mobile-diagnostic-errors', () => [])
let timer: ReturnType<typeof setInterval> | undefined
let tween: gsap.core.Tween | undefined
let test = '미실행'
function snapshot() {
  const triggers = ScrollTrigger.getAll()
  const active = triggers.filter(t => t.isActive).map(t => `${(t.trigger as HTMLElement)?.className?.toString().split(' ')[0]}:${Math.round(t.progress * 100)}%`)
  const stage = document.querySelector<HTMLElement>('.stage')
  report.value = [
    '모바일 진단 D1 · 개인정보 전송 없음',
    `모션 줄이기: ${matchMedia('(prefers-reduced-motion: reduce)').matches ? '켜짐' : '꺼짐'}`,
    `터치: ${navigator.maxTouchPoints} / 화면: ${innerWidth}×${innerHeight}`,
    `스크롤: ${Math.round(scrollY)} / GSAP: ${gsap.version} / 트리거: ${triggers.length}`,
    `현재 연출: ${active.join(', ') || '없음'}`,
    `3D: ${stage?.dataset.status || '미실행'} / 프레임: ${stage?.dataset.frames || '0'}`,
    `GSAP 버튼 테스트: ${test}`,
    `오류: ${errors.value.join(' | ') || '기록 없음'}`,
    navigator.userAgent,
  ].join('\n')
}
function runTest() {
  tween?.kill()
  test = '진행 중'
  tween = gsap.fromTo(probe.value!, { x: 0 }, { x: 180, duration: 1, repeat: 1, yoyo: true, onComplete: () => { test = '완료'; snapshot() } })
  snapshot()
}
async function copy() {
  try { await navigator.clipboard.writeText(report.value); copied.value = true }
  catch { copied.value = false }
}
onMounted(() => {
  if (!enabled) return
  snapshot()
  timer = setInterval(snapshot, 500)
})
onBeforeUnmount(() => { clearInterval(timer); tween?.kill() })
</script>

<template>
  <aside v-if="enabled" class="mobile-diag" aria-label="모바일 진단">
    <button class="mobile-diag__toggle" @click="expanded = !expanded">모바일 진단 {{ expanded ? '접기' : '펼치기' }}</button>
    <div v-show="expanded">
      <pre>{{ report }}</pre>
      <div class="mobile-diag__track"><span ref="probe" /></div>
      <div class="mobile-diag__actions">
        <button @click="runTest">움직임 테스트</button>
        <button @click="copy">{{ copied ? '복사됨' : '진단 복사' }}</button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.mobile-diag { position: fixed; z-index: 10000; bottom: max(8px, env(safe-area-inset-bottom)); left: 8px; width: min(370px, calc(100vw - 16px)); padding: 10px; background: #171717; color: white; border: 1px solid #aaa; border-radius: 12px; font: 12px/1.4 monospace; }
.mobile-diag pre { max-height: 190px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; user-select: text; margin: 8px 0; }
.mobile-diag button { min-height: 44px; padding: 8px 12px; background: white; color: #111; border-radius: 6px; font: bold 12px sans-serif; }
.mobile-diag__actions { display: flex; gap: 8px; }
.mobile-diag__track { height: 22px; margin-bottom: 6px; }
.mobile-diag__track span { display: block; width: 18px; height: 18px; border-radius: 50%; background: #ffd43b; }
</style>
