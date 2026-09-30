<script setup lang="ts">
import * as THREE from 'three'
import gsap from 'gsap'

// 섹션 색이 바뀔 때 새 색이 아래에서 물결치며 차오르는 배경 (WebGL 셰이더).
// WebGL을 못 쓰면 뒤에 있는 CSS 배경(.page__bg)이 그대로 전환된다.
const host = ref<HTMLDivElement>()
const { bg } = usePageColor()
let cleanup: (() => void) | undefined

const vertexShader = /* glsl */ `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position.xy, 0.0, 1.0);
}
`

const fragmentShader = /* glsl */ `
uniform vec3 uFrom;
uniform vec3 uTo;
uniform float uProgress;
uniform float uTime;
uniform float uAspect;
varying vec2 vUv;

void main() {
  float x = vUv.x * uAspect;
  // 겹친 사인파로 출렁이는 수면
  float wave = sin(x * 5.0 + uTime * 1.6) * 0.035
             + sin(x * 11.0 - uTime * 2.3) * 0.018
             + sin(x * 23.0 + uTime * 3.1) * 0.006;
  float level = uProgress * 1.25 - 0.12 + wave * (1.0 - uProgress) * 1.8;
  float d = vUv.y - level;
  float fill = smoothstep(0.004, -0.004, d);
  vec3 col = mix(uFrom, uTo, fill);
  // 수면 가장자리의 얇은 하이라이트
  float foam = smoothstep(0.018, 0.0, abs(d)) * (1.0 - step(0.999, uProgress));
  col = mix(col, vec3(1.0), foam * 0.35);
  gl_FragColor = vec4(col, 1.0);
}
`

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  let renderer: THREE.WebGLRenderer
  try {
    renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false })
  } catch {
    return
  }
  // 입력 색을 그대로 출력 (hex 값과 동일한 색)
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1))
  host.value!.appendChild(renderer.domElement)

  const color = (hex: string) => new THREE.Color().setStyle(hex, THREE.LinearSRGBColorSpace)
  const uniforms = {
    uFrom: { value: color(bg.value) },
    uTo: { value: color(bg.value) },
    uProgress: { value: 1 },
    uTime: { value: 0 },
    uAspect: { value: 1 },
  }
  const mat = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms, depthTest: false, depthWrite: false })
  mat.toneMapped = false
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat)
  const scene = new THREE.Scene()
  scene.add(quad)
  const camera = new THREE.Camera()

  const draw = () => renderer.render(scene, camera)
  const resize = () => {
    renderer.setSize(window.innerWidth, window.innerHeight)
    uniforms.uAspect.value = window.innerWidth / window.innerHeight
    draw()
  }
  resize()
  window.addEventListener('resize', resize)
  document.documentElement.classList.add('liquid-bg')

  // 전환 중에만 그린다
  let running = false
  const tick = (time: number) => {
    uniforms.uTime.value = time
    draw()
  }
  const stop = watch(bg, (next: string) => {
    const now = new THREE.Color().copy(uniforms.uFrom.value).lerp(uniforms.uTo.value, uniforms.uProgress.value)
    uniforms.uFrom.value.copy(now)
    uniforms.uTo.value.copy(color(next))
    uniforms.uProgress.value = 0
    if (!running) {
      gsap.ticker.add(tick)
      running = true
    }
    gsap.killTweensOf(uniforms.uProgress)
    gsap.to(uniforms.uProgress, {
      value: 1,
      duration: 1.1,
      ease: 'power2.inOut',
      onComplete: () => {
        gsap.ticker.remove(tick)
        running = false
        draw()
      },
    })
  })

  cleanup = () => {
    stop()
    gsap.ticker.remove(tick)
    window.removeEventListener('resize', resize)
    document.documentElement.classList.remove('liquid-bg')
    mat.dispose()
    quad.geometry.dispose()
    renderer.dispose()
    renderer.domElement.remove()
  }
})

onBeforeUnmount(() => cleanup?.())
</script>

<template>
  <div ref="host" class="liquid" aria-hidden="true" />
</template>

<style scoped>
.liquid {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
}
.liquid :deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>
