<script setup lang="ts">
import gsap from 'gsap'
import { brand, momentProducts, yourMoment, type ProductKey } from '~/data/content'

const root = ref<HTMLElement>()
useSectionColor(root, () => ({ bg: '#7ed957' }))

// 10. 참여형 콘텐츠 — 이유 하나 고르고 한 줄 쓰면 그래픽 카드 생성
const reason = ref(0)
const text = ref('')
const primaryChosen = useState<ProductKey>('chosen-product', () => 'bananaMilk')
const ownChoice = ref<string>()
const chosen = computed({ get: () => ownChoice.value ?? primaryChosen.value, set: (key: string) => { ownChoice.value = key } })
const colors=['#fff6e0','#ffd43b','#ff9ebd','#8fd3ff']
const color=ref(colors[0]!)
const downloadStatus=ref('')
const card = ref<{ reason: number; text: string; product: number; date: string; color?: string } | null>(null)
const cardEl = ref<HTMLElement>()
const saved = ref<typeof card.value[]>([])
const physics = ref<{ drop: (key?: string) => void }>()

const STORAGE_KEY = 'binggrae-moments'

onMounted(() => {
  try {
    const stored: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    saved.value = Array.isArray(stored) ? stored.filter(s => s && Number.isInteger(s.reason) && yourMoment.reasons[s.reason] && Number.isInteger(s.product) && momentProducts[s.product] && typeof s.text === 'string' && typeof s.date === 'string').slice(0, 6) : []
  } catch {
    saved.value = []
  }
})

async function make() {
  downloadStatus.value = ''
  const now = new Date()
  card.value = {
    reason: reason.value,
    text: text.value.trim().slice(0, 40) || '그냥, 오늘은 괜찮은 날.',
    product: Math.max(0,momentProducts.findIndex(p=>p.key===chosen.value)),
    color:color.value,
    date: `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, '0')}.${String(now.getDate()).padStart(2, '0')}`,
  }
  saved.value = [card.value, ...saved.value].slice(0, 6)
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved.value))
  } catch {
    /* 저장 불가 환경은 무시 */
  }
  physics.value?.drop(momentProducts[card.value.product].key)
  await nextTick()
  gsap.fromTo(cardEl.value!, { scale: 0.4, rotate: -20, opacity: 0 }, { scale: 1, rotate: -3, opacity: 1, duration: prefersReducedMotion() ? 0 : 0.7, ease: 'back.out(2)', overwrite: true })
}

// 카드를 PNG로 저장 (캔버스에 직접 그림)
async function download() {
  if (!card.value) return
  await document.fonts.ready
  const c = document.createElement('canvas')
  const W = 1080
  const H = 1350
  c.width = W
  c.height = H
  const g = c.getContext('2d')!
  const r = yourMoment.reasons[card.value.reason]
  g.fillStyle = r.color
  g.fillRect(0, 0, W, H)
  g.fillStyle = '#1a1a1a'
  g.fillRect(90, 110, W - 160, H - 200)
  g.fillStyle = card.value.color || '#fff6e0'
  g.fillRect(80, 100, W - 160, H - 200)
  g.strokeStyle = '#1a1a1a'
  g.lineWidth = 8
  g.strokeRect(80, 100, W - 160, H - 200)
  g.fillStyle = '#1a1a1a'
  g.font = '64px Anton, sans-serif'
  g.fillText('MY BINGGRAE MOMENT', 140, 220)
  g.font = '40px "Pretendard Variable", sans-serif'
  g.fillText(card.value.date, 140, 290)
  g.font = '150px "Black Han Sans", sans-serif'
  g.fillText(r.emoji, 140, 540)
  g.font = '84px "Black Han Sans", sans-serif'
  g.fillText(r.label, 140, 680)
  g.font = '500 48px "Pretendard Variable", sans-serif'
  wrap(g, `“${card.value.text}”`, 140, 790, W - 280, 68)
  g.font = '44px "Black Han Sans", sans-serif'
  g.fillText(brand.name, 140, H - 160)
  const img=new Image();img.src=momentProducts[card.value.product]!.image
  try{await img.decode();const scale=Math.min(245/img.naturalWidth,255/img.naturalHeight);const w=img.naturalWidth*scale,h=img.naturalHeight*scale;g.drawImage(img,690+(245-w)/2,1000+(255-h)/2,w,h)}catch{downloadStatus.value='제품 이미지 로드에 실패했어요. 다시 저장해 주세요.';return}
  const a = document.createElement('a')
  a.href = c.toDataURL('image/png')
  a.download = 'binggrae-moment.png'
  a.click()
  downloadStatus.value='제품과 문구가 담긴 카드를 저장했어요.'
}

function wrap(g: CanvasRenderingContext2D, s: string, x: number, y: number, max: number, lh: number) {
  let line = ''
  for (const ch of s) {
    if (g.measureText(line + ch).width > max) {
      g.fillText(line, x, y)
      line = ch
      y += lh
    } else line += ch
  }
  g.fillText(line, x, y)
}
</script>

<template>
  <section id="your-moment" ref="root" class="ym section container">
    <div class="section-head">
      <span class="kicker">09 — Your Binggrae Moment</span>
      <h2 class="ko-display size-xl sticker-text">{{ yourMoment.title }}</h2>
    </div>

    <div class="ym__grid">
      <form class="ym__form card" @submit.prevent="make">
        <fieldset class="ym__reasons">
          <legend class="kicker">01. 하나 골라주세요</legend>
          <button
            v-for="(r, i) in yourMoment.reasons"
            :key="r.label"
            type="button"
            class="btn"
            :aria-pressed="i === reason"
            :style="i === reason ? { background: r.color } : undefined"
            @click="reason = i"
          >
            <span aria-hidden="true">{{ r.emoji }}</span> {{ r.label }}
          </button>
        </fieldset>
        <label class="ym__label">
          <span class="kicker">02. 한 줄 남기기</span>
          <input v-model="text" class="ym__input" maxlength="40" :placeholder="yourMoment.placeholder" />
          <span class="ym__count body-m">{{ text.length }}/40</span>
        </label>
        <fieldset class="ym__reasons"><legend class="kicker">03. 함께할 제품</legend><button v-for="p in momentProducts" :key="p.key" type="button" class="btn btn--sm" :aria-pressed="chosen===p.key" :style="chosen===p.key?{background:p.bg,color:p.ink}:undefined" @click="chosen=p.key">{{ p.nameKo }}</button></fieldset>
        <fieldset class="ym__reasons"><legend class="kicker">04. 오늘의 색</legend><button v-for="(c,i) in colors" :key="c" type="button" class="ym__swatch" :aria-label="['크림','노랑','핑크','파랑'][i]" :aria-pressed="color===c" :style="{background:c}" @click="color=c">{{ color===c?'✓':'' }}</button></fieldset>
        <button type="submit" class="btn btn--dark">카드 만들기 ✦</button><small>최근 카드는 이 브라우저에만 저장됩니다.</small>
      </form>

      <div class="ym__result">
        <div
          v-if="card"
          ref="cardEl"
          class="ym__card card"
          :style="{ '--c': yourMoment.reasons[card.reason].color, background:card.color||'#fff6e0' }"
        >
          <span class="en-display ym__card-kicker">My Binggrae Moment</span>
          <span class="body-m">{{ card.date }}</span>
          <span class="ym__emoji" aria-hidden="true">{{ yourMoment.reasons[card.reason].emoji }}</span>
          <p class="ko-display size-md">{{ yourMoment.reasons[card.reason].label }}</p>
          <p class="body-l">“{{ card.text }}”</p>
          <div class="ym__card-art" aria-hidden="true">
            <img :src="momentProducts[card.product].image" :alt="momentProducts[card.product].nameKo" class="ym__product-image" />
          </div>
          <span class="ym__card-product body-m">함께한 맛 · {{ momentProducts[card.product].nameKo }}</span>
          <span class="ko-display ym__card-brand">{{ brand.name }}</span>
        </div>
        <p v-else class="ym__empty body-m">오늘의 순간을 골라보세요.<br />작은 카드가 만들어져요.</p>
        <button v-if="card" class="btn" @click="download">이미지로 저장 ↓</button><p role="status">{{ downloadStatus }}</p>
      </div>
    </div>

    <ClientOnly>
      <MomentPhysics ref="physics" />
    </ClientOnly>

    <div v-if="saved.length > 1" class="ym__wall">
      <span class="kicker">최근에 만든 카드</span>
      <ul>
        <li v-for="(s, i) in saved.slice(1)" :key="i" class="card" :style="{ background: yourMoment.reasons[s!.reason].color }">
          <span aria-hidden="true">{{ yourMoment.reasons[s!.reason].emoji }}</span> {{ s!.text }}
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.ym__swatch{width:44px;height:44px;border:2px solid #1a1a1a;border-radius:50%;font-size:22px;color:#1a1a1a}.ym__swatch[aria-pressed="true"]{outline:2px solid #1a1a1a;outline-offset:3px}
.ym__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(24px, 4vw, 64px);
  align-items: start;
}
.ym__form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: clamp(20px, 3vw, 36px);
}
.ym__reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
}
.ym__reasons legend {
  margin-bottom: 12px;
}
.ym__label {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ym__input {
  min-height: 56px;
  padding: 0 64px 0 18px;
  border: var(--stroke) solid var(--ink);
  border-radius: 14px;
  background: #fff;
  font-size: 17px;
  font-weight: 500;
  outline: none;
}
.ym__input:focus {
  box-shadow: 0 0 0 4px var(--banana);
}
.ym__count {
  position: absolute;
  right: 16px;
  bottom: 16px;
  font-size: 12px;
  opacity: 0.5;
}
.ym__result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}
.ym__card {
  position: relative;
  width: min(100%, 380px);
  aspect-ratio: 4 / 5;
  min-height: 480px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 28px;
  background: var(--cream);
  box-shadow: 10px 10px 0 var(--c), 12px 12px 0 var(--ink);
  transform: rotate(-3deg);
  overflow: hidden;
}
.ym__card-kicker {
  font-size: 20px;
}
.ym__emoji {
  font-size: 56px;
  margin-top: 12px;
}
.ym__card-art {
  position: absolute;
  right: -20px;
  bottom: -30px;
  width: 42%;
  aspect-ratio: 300 / 360;
  transform: rotate(12deg);
}
.ym__product-image { width: 100%; height: 100%; object-fit: contain; }
.ym__card-product { position: relative; z-index: 1; font-size: 12px; }
.ym__card-brand {
  margin-top: auto;
  font-size: 20px;
}
.ym__card > .body-l { overflow-wrap: anywhere; word-break: break-word; padding-bottom: 72px; }
.ym__empty {
  display: grid;
  place-items: center;
  width: min(100%, 380px);
  aspect-ratio: 4 / 5;
  border: var(--stroke) dashed var(--ink);
  border-radius: 18px;
  text-align: center;
}
.ym__wall {
  margin-top: clamp(40px, 6vh, 72px);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.ym__wall ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.ym__wall li {
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 14px;
}
@media (max-width: 900px) {
  .ym__swatch{width:44px;height:44px;border:2px solid #1a1a1a;border-radius:50%;font-size:22px;color:#1a1a1a}.ym__swatch[aria-pressed="true"]{outline:2px solid #1a1a1a;outline-offset:3px}
.ym__grid {
    grid-template-columns: 1fr;
  }
}
</style>
