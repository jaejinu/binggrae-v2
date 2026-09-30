// 파일 없이 WebAudio로 합성한 부드러운 앰비언트 + UI 효과음.

let ctx: AudioContext | null = null
let master: GainNode | null = null

function ensureGraph() {
  if (ctx) return
  ctx = new AudioContext()
  master = ctx.createGain()
  master.gain.value = 0
  master.connect(ctx.destination)

  const filter = ctx.createBiquadFilter()
  filter.type = 'lowpass'
  filter.frequency.value = 900
  filter.connect(master)

  // C 메이저 패드 (도-미-솔-시)
  for (const [freq, detune] of [
    [130.81, -6],
    [164.81, 4],
    [196.0, -3],
    [246.94, 5],
  ] as const) {
    const osc = ctx.createOscillator()
    osc.type = 'sine'
    osc.frequency.value = freq
    osc.detune.value = detune
    const g = ctx.createGain()
    g.gain.value = 0.16
    osc.connect(g).connect(filter)
    osc.start()
  }
  const lfo = ctx.createOscillator()
  lfo.frequency.value = 0.08
  const lfoGain = ctx.createGain()
  lfoGain.gain.value = 300
  lfo.connect(lfoGain).connect(filter.frequency)
  lfo.start()
}

export function useSound() {
  const enabled = useState('sound-enabled', () => false)

  function set(on: boolean) {
    ensureGraph()
    if (!ctx || !master) return
    if (ctx.state === 'suspended') ctx.resume()
    enabled.value = on
    const now = ctx.currentTime
    master.gain.cancelScheduledValues(now)
    master.gain.setTargetAtTime(on ? 0.07 : 0, now, 0.8)
  }

  function toggle() {
    set(!enabled.value)
  }

  // 짧은 "뽁" 소리
  function blip(pitch = 1) {
    if (!enabled.value || !ctx) return
    const now = ctx.currentTime
    const osc = ctx.createOscillator()
    const g = ctx.createGain()
    osc.type = 'triangle'
    osc.frequency.setValueAtTime(660 * pitch, now)
    osc.frequency.exponentialRampToValueAtTime(1320 * pitch, now + 0.08)
    g.gain.setValueAtTime(0.0001, now)
    g.gain.exponentialRampToValueAtTime(0.1, now + 0.01)
    g.gain.exponentialRampToValueAtTime(0.0001, now + 0.18)
    osc.connect(g).connect(ctx.destination)
    osc.start(now)
    osc.stop(now + 0.2)
  }

  return { enabled, set, toggle, blip }
}
