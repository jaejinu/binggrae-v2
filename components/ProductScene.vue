<script setup lang="ts">
import * as THREE from 'three'
import gsap from 'gsap'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { EXRLoader } from 'three/examples/jsm/loaders/EXRLoader.js'
import { products, type ProductKey } from '~/data/content'

// 단순화한 오리지널 3D 형태(로고·실제 패키지 없음). Rotate / Zoom / Explode / Detail 모드 지원.
export type Mode = 'rotate' | 'zoom' | 'explode' | 'detail' | 'play'

const props = defineProps<{ product: ProductKey; mode: Mode; gesture?: number; side?: string }>()
const emit = defineEmits<{ 'update:gesture': [value: number] }>()
const host = ref<HTMLDivElement>()
const available = ref(true)
let disposed = false

let renderer: THREE.WebGLRenderer | undefined
let raf = 0
let ro: ResizeObserver | undefined
let io: IntersectionObserver | undefined
let kickLoop: (() => void) | undefined
const cleanups: (() => void)[] = []
const disposables: { dispose(): void }[] = []
const track = <T extends { dispose(): void }>(d: T) => (disposables.push(d), d)

const gradient = track(new THREE.DataTexture(new Uint8Array([95, 175, 255]), 3, 1, THREE.RedFormat))
gradient.minFilter = gradient.magFilter = THREE.NearestFilter
gradient.needsUpdate = true
const toon = (color: string, extra: THREE.MeshToonMaterialParameters = {}) =>
  track(new THREE.MeshToonMaterial({ color, gradientMap: gradient, ...extra }))

const outlineMat = track(new THREE.MeshBasicMaterial({ color: '#1a1a1a', side: THREE.BackSide }))
outlineMat.onBeforeCompile = (shader) => {
  shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', 'vec3 transformed = position + normal * 0.025;')
}
function mesh(geometry: THREE.BufferGeometry, material: THREE.Material, outline = true) {
  track(geometry)
  const m = new THREE.Mesh(geometry, material)
  if (outline) m.add(new THREE.Mesh(geometry, outlineMat))
  return m
}

interface Part {
  obj: THREE.Object3D
  explode: THREE.Vector3 // 분해 시 이동량
}
interface Built {
  group: THREE.Group
  parts: Part[]
}

const lathe = (pts: [number, number][], seg = 48) =>
  new THREE.LatheGeometry(pts.map(([x, y]) => new THREE.Vector2(x, y)), seg)

function buildBananaMilk(): Built {
  const group = new THREE.Group()
  // 단지 형태 프로파일 (반지름, 높이)
  const body = mesh(
    lathe([[0, -1.3], [0.7, -1.28], [1.05, -0.9], [1.18, -0.3], [1.1, 0.25], [0.8, 0.65], [0.5, 0.85], [0.46, 1.0]]),
    toon('#ffd43b'),
  )
  const cap = mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.22, 40), toon('#fff6e0'))
  cap.position.y = 1.1
  const foil = mesh(new THREE.CylinderGeometry(0.47, 0.47, 0.03, 40), toon('#d9d9d9'))
  foil.position.y = 1.23
  const band = mesh(new THREE.TorusGeometry(1.16, 0.04, 10, 64), toon('#fff6e0'), false)
  band.rotation.x = Math.PI / 2
  band.position.y = -0.3
  group.add(body, cap, foil, band)
  return {
    group,
    parts: [
      { obj: cap, explode: new THREE.Vector3(0, 0.9, 0) },
      { obj: foil, explode: new THREE.Vector3(0, 1.6, 0) },
      { obj: band, explode: new THREE.Vector3(0, -0.2, 0.9) },
    ],
  }
}

function buildYoplait(): Built {
  const group = new THREE.Group()
  const cup = mesh(lathe([[0, -1.1], [0.72, -1.1], [0.95, 0.9], [0.9, 0.9]]), toon('#fff6e0', { side: THREE.DoubleSide }))
  const yogurt = mesh(new THREE.CylinderGeometry(0.9, 0.9, 0.08, 40), toon('#ff9ebd'), false)
  yogurt.position.y = 0.72
  const lid = mesh(new THREE.CylinderGeometry(1.0, 1.0, 0.04, 40), toon('#ff5f8f'))
  lid.position.y = 0.94
  const spoon = new THREE.Group()
  const handle = mesh(new THREE.BoxGeometry(0.12, 1.4, 0.05), toon('#fff6e0'))
  const bowl = mesh(new THREE.SphereGeometry(0.22, 20, 12), toon('#fff6e0'))
  bowl.scale.set(1, 1.3, 0.35)
  bowl.position.y = 0.8
  spoon.add(handle, bowl)
  spoon.position.set(0.6, 1.1, 0)
  spoon.rotation.z = -0.5
  group.add(cup, yogurt, lid, spoon)
  return {
    group,
    parts: [
      { obj: lid, explode: new THREE.Vector3(0, 1.2, 0) },
      { obj: yogurt, explode: new THREE.Vector3(0, 0.5, 0) },
      { obj: spoon, explode: new THREE.Vector3(1.0, 0.4, 0) },
    ],
  }
}

function fishShape() {
  const s = new THREE.Shape()
  s.moveTo(-1.4, 0)
  s.bezierCurveTo(-1.2, 0.8, 0.2, 1.0, 0.8, 0.35)
  s.lineTo(1.4, 0.8)
  s.bezierCurveTo(1.3, 0.3, 1.3, -0.3, 1.4, -0.8)
  s.lineTo(0.8, -0.35)
  s.bezierCurveTo(0.2, -1.0, -1.2, -0.8, -1.4, 0)
  return s
}

function buildSamanco(): Built {
  const group = new THREE.Group()
  const ext = (depth: number) =>
    new THREE.ExtrudeGeometry(fishShape(), { depth, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 3, curveSegments: 32 })
  const top = mesh(ext(0.14), toon('#d98a3d'))
  top.position.z = 0.2
  const cream = mesh(ext(0.22), toon('#fff6e0'))
  cream.scale.set(0.93, 0.9, 1)
  cream.position.z = -0.08
  const bean = mesh(ext(0.1), toon('#7a3326'), false)
  bean.scale.set(0.6, 0.45, 1)
  bean.position.set(-0.15, 0, 0.0)
  const bottom = mesh(ext(0.14), toon('#d98a3d'))
  bottom.position.z = -0.4
  const eye = mesh(new THREE.SphereGeometry(0.08, 12, 10), toon('#1a1a1a'), false)
  eye.position.set(-0.95, 0.18, 0.24)
  top.add(eye)
  group.add(top, cream, bean, bottom)
  group.rotation.x = -0.25
  return {
    group,
    parts: [
      { obj: top, explode: new THREE.Vector3(0, 0, 1.0) },
      { obj: bean, explode: new THREE.Vector3(0, 0, 0.5) },
      { obj: bottom, explode: new THREE.Vector3(0, 0, -0.9) },
    ],
  }
}

function buildBravo(): Built {
  const group = new THREE.Group()
  const cone = mesh(new THREE.ConeGeometry(0.75, 2.2, 40, 1, true), toon('#e7a95b', { side: THREE.DoubleSide }))
  cone.rotation.x = Math.PI
  cone.position.y = -0.5
  const sleeve = mesh(new THREE.CylinderGeometry(0.8, 0.52, 0.8, 40, 1, true), toon('#3d63dd', { side: THREE.DoubleSide }))
  sleeve.position.y = -0.05
  const scoop = new THREE.Group()
  for (let i = 0; i < 4; i++) {
    const r = 0.72 - i * 0.16
    const ring = mesh(new THREE.TorusGeometry(r, 0.2, 14, 40), toon('#fff6e0'))
    ring.rotation.x = Math.PI / 2
    ring.position.y = 0.72 + i * 0.22
    scoop.add(ring)
  }
  const tip = mesh(new THREE.ConeGeometry(0.18, 0.3, 16), toon('#fff6e0'))
  tip.position.y = 1.62
  scoop.add(tip)
  const choco = mesh(new THREE.SphereGeometry(0.78, 32, 12, 0, Math.PI * 2, 0, Math.PI / 2.6), toon('#6b3a1e', { side: THREE.DoubleSide }), false)
  choco.position.y = 0.66
  group.add(cone, sleeve, scoop, choco)
  return {
    group,
    parts: [
      { obj: scoop, explode: new THREE.Vector3(0, 1.0, 0) },
      { obj: choco, explode: new THREE.Vector3(0, 0.45, 0) },
      { obj: sleeve, explode: new THREE.Vector3(0.9, -0.1, 0) },
    ],
  }
}

// public/models/*.glb 가 있으면 그 모델을 사용 (blender/build_products.py 로 생성).
// 블렌더에서 베이킹한 실사 재질(PBR)을 그대로 쓰고, 크기·중심만 맞춘다.
// 분해 방향은 Blender 커스텀 속성 "explode"(glTF extras)를 우선 사용한다.
// 눕혀서 모델링한 제품은 카메라 쪽으로 기울여 보여준다
const viewTilt: Partial<Record<ProductKey, number>> = {}

function fromGLB(root: THREE.Object3D, key: ProductKey): Built {
  prepareSleeve(root)
  finishProduct(root)
  root.traverse((o) => {
    const m = o as THREE.Mesh
    if (!m.isMesh) return
    track(m.geometry)
    const mats = Array.isArray(m.material) ? m.material : [m.material]
    mats.forEach((mat) => {
      track(mat)
      Object.values(mat).forEach((v) => (v as THREE.Texture)?.isTexture && track(v as THREE.Texture))
    })
  })
  const box = new THREE.Box3().setFromObject(root)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const scale = 2.8 / Math.max(size.x, size.y, size.z)
  root.position.sub(center)
  const inner = new THREE.Group()
  inner.add(root)
  inner.scale.setScalar(scale)
  inner.rotation.x = viewTilt[key] ?? 0
  const group = new THREE.Group()
  group.add(inner)
  const parts: Part[] = productParts(root)
  return { group, parts }
}

const builders: Record<ProductKey, () => Built> = {
  bananaMilk: buildBananaMilk,
  yoplait: buildYoplait,
  samanco: buildSamanco,
  bravo: buildBravo,
}

onMounted(() => {
  const el = host.value!
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100)
  camera.position.set(0, 0.5, 9.5)

  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }) }
  catch { available.value = false; return }
  const reduced = prefersReducedMotion()
  const mobile = window.matchMedia('(pointer: coarse)').matches || window.innerWidth <= 800
  const continuous = !mobile && !reduced
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, mobile ? 1 : 1.75))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  // 블렌더 렌더(Khronos PBR Neutral)와 같은 톤으로
  renderer.toneMapping = THREE.NeutralToneMapping
  el.appendChild(renderer.domElement)

  // 스튜디오 같은 환경 반사
  const pmrem = track(new THREE.PMREMGenerator(renderer))
  scene.environment = track(pmrem.fromScene(new RoomEnvironment(), 0.04).texture)

  scene.add(new THREE.AmbientLight('#ffffff', 0.35))
  const key = new THREE.DirectionalLight('#ffffff', 1.6)
  key.position.set(-3, 6, 5)
  scene.add(key)
  const rim = new THREE.DirectionalLight('#ffffff', 0.8)
  rim.position.set(2, 3, -5)
  scene.add(rim)

  // 제품 아래 부드러운 접지 그림자
  const shadowCanvas = document.createElement('canvas')
  shadowCanvas.width = shadowCanvas.height = 128
  const sg = shadowCanvas.getContext('2d')!
  const grad = sg.createRadialGradient(64, 64, 0, 64, 64, 64)
  grad.addColorStop(0, 'rgba(0,0,0,0.55)')
  grad.addColorStop(0.5, 'rgba(0,0,0,0.2)')
  grad.addColorStop(1, 'rgba(0,0,0,0)')
  sg.fillStyle = grad
  sg.fillRect(0, 0, 128, 128)
  const shadowTex = track(new THREE.CanvasTexture(shadowCanvas))
  const shadow = new THREE.Mesh(
    track(new THREE.PlaneGeometry(3.2, 3.2)),
    track(new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, depthWrite: false })),
  )
  shadow.rotation.x = -Math.PI / 2
  shadow.position.y = -1.55
  scene.add(shadow)

  const pivot = new THREE.Group()
  scene.add(pivot)

  const built = {} as Record<ProductKey, Built>
  const origins = new Map<THREE.Object3D, THREE.Vector3>()
  const rotations = new Map<THREE.Object3D, THREE.Euler>()
  const register = (k: ProductKey, b: Built) => {
    b.parts.forEach((p) => { origins.set(p.obj, p.obj.position.clone()); rotations.set(p.obj, p.obj.rotation.clone()) })
    b.group.traverse(o=>{if(o.name==='Sleeve_Assembly'){origins.set(o,o.position.clone());rotations.set(o,o.rotation.clone())}})
    b.group.visible = false
    b.group.scale.setScalar(0.0001)
    pivot.add(b.group)
    built[k] = b
  }
  ;(Object.keys(builders) as ProductKey[]).forEach((k) => register(k, builders[k]()))

  // 제품별 조명(HDRI) — 블렌더 렌더와 같은 분위기. 로드 전까지는 스튜디오 환경 유지
  const envCache = new Map<ProductKey, THREE.Texture>()
  const envLoading = new Set<ProductKey>()
  const exr = new EXRLoader()
  const applyEnv = (k: ProductKey) => {
    if (mobile) return
    const info = products.find((p) => p.key === k)!
    const cached = envCache.get(k)
    if (cached) {
      scene.environment = cached
      scene.environmentRotation.set(0, THREE.MathUtils.degToRad(info.envRotation), 0)
      return
    }
    if (envLoading.has(k)) return
    envLoading.add(k)
    exr.load(
      info.env,
      (tex) => {
        if (disposed) { tex.dispose(); return }
        const pm = track(pmrem.fromEquirectangular(tex).texture)
        tex.dispose()
        envCache.set(k, pm)
        if (current === k) {
          applyEnv(k)
          kickLoop?.()
        }
      },
      undefined,
      () => {
        /* HDRI가 없으면 기본 스튜디오 환경 */
      },
    )
  }

  // GLB(Draco 압축)는 섹션이 처음 화면에 들어올 때 내려받는다
  let modelsRequested = false
  const draco = new DRACOLoader().setDecoderPath('/draco/')
  cleanups.push(() => draco.dispose())
  const loadModels = () => {
    if (modelsRequested) return
    modelsRequested = true
    if (current) applyEnv(current)
    const loader = new GLTFLoader().setDRACOLoader(draco)
    products.forEach((p) => {
      loader.load(
        p.model,
        (gltf) => {
          if (disposed) return
          // glTF 기본 자세는 조립 전(첫 프레임)이라 마지막 프레임(완성)으로 맞춘다
          if (gltf.animations.length) {
            const mx = new THREE.AnimationMixer(gltf.scene)
            gltf.animations.forEach((clip) => {
              const action = mx.clipAction(clip)
              action.setLoop(THREE.LoopOnce, 1)
              action.clampWhenFinished = true
              action.play()
              action.time = clip.duration * 0.9999
            })
            mx.update(0)
            gltf.scene.updateMatrixWorld(true)
          }
          const old = built[p.key]
          pivot.remove(old.group)
          register(p.key, fromGLB(gltf.scene, p.key))
          el.dataset.model = p.key
          if (current === p.key) {
            current = null
            showProduct(p.key)
          }
        },
        undefined,
        () => {
          /* 모델 파일이 없으면 기본 3D 유지 */
        },
      )
    })
  }

  let current: ProductKey | null = null
  function showProduct(k: ProductKey) {
    if (disposed || current === k) return
    if (current) {
      const prev = built[current].group
      gsap.killTweensOf(prev.scale)
      gsap.to(prev.scale, { x: 0.0001, y: 0.0001, z: 0.0001, duration: 0.3, ease: 'back.in(2)', onComplete: () => { prev.visible = false } })
    }
    current = k
    const g = built[k].group
    gsap.killTweensOf(g.scale)
    gsap.killTweensOf(pivot.rotation)
    g.visible = true
    gsap.to(g.scale, { x: 1, y: 1, z: 1, duration: 0.7, delay: 0.2, ease: 'back.out(1.8)' })
    if (!reduced && props.mode !== 'play') gsap.fromTo(pivot.rotation, { y: pivot.rotation.y - Math.PI }, { y: pivot.rotation.y, duration: 0.9, ease: 'power3.out' })
    applyMode(props.mode)
    if (modelsRequested) applyEnv(k)
    kickLoop?.()
  }

  function applyMode(mode: Mode) {
    if (!current) return
    const exploded = mode === 'explode'
    built[current].parts.forEach((p) => {
      const o = origins.get(p.obj)!
      const t = exploded ? o.clone().add(p.explode) : o
      gsap.killTweensOf(p.obj.position)
      gsap.to(p.obj.position, { x: t.x, y: t.y, z: t.z, duration: 0.8, ease: exploded ? 'back.out(1.6)' : 'power3.inOut' })
    })
    applyGesture()
    kickLoop?.()
    const dist = mode === 'zoom' ? 5.4 : mode === 'detail' ? 6.6 : mode === 'explode' ? 8 : mode === 'play' ? 7.2 : 8
    gsap.to(camera.position, { z: dist, duration: reduced ? 0 : 0.9, ease: 'power3.inOut', overwrite: true })
  }

  function applyGesture() {
    if(!current)return
    const b=built[current],t=THREE.MathUtils.clamp((props.gesture??0)/100,0,1)
    const sleeve=b.group.getObjectByName('Sleeve_Assembly')
    if(sleeve&&origins.has(sleeve))sleeve.position.copy(origins.get(sleeve)!)
    b.parts.forEach(p=>p.obj.rotation.copy(rotations.get(p.obj)!))
    if(props.mode!=='play')return
    gsap.killTweensOf(pivot.rotation)
    pivot.rotation.set(.08,0,0)
    for(const p of b.parts){gsap.killTweensOf(p.obj.position);p.obj.position.copy(origins.get(p.obj)!)}
    if(current==='bananaMilk')pivot.rotation.y=Math.PI*t
    if(current==='yoplait'){
      const lid=b.group.getObjectByName('Foil_Lid');if(lid){lid.position.y+=.5*t;lid.rotation.x=-1.05*t}
    }
    if(current==='samanco'){
      const wafer=b.group.getObjectByName('Wafer_Front');if(wafer){wafer.position.z+=.5*t;wafer.position.x+=(props.side==='tail'?1:-1)*.35*t;wafer.rotation.y=(props.side==='tail'?-1:1)*.8*t}
    }
    if(current==='bravo'&&sleeve)sleeve.position.y-=.75*t
    el.dataset.gesture=String(Math.round(t*100));kickLoop?.()
  }
  watch([()=>props.gesture,()=>props.side],applyGesture)
  showProduct(props.product)
  watch(() => props.product, (k: ProductKey) => showProduct(k))
  watch(() => props.mode, (m: Mode) => applyMode(m))

  // 드래그로 회전
  let dragging = false
  let lastX = 0
  let lastY = 0
  let velY = 0
  const down = (e: PointerEvent) => {
    if((e.target as HTMLElement).closest('button,input'))return
    if (e.pointerType === 'mouse' && e.button !== 0) return
    dragging = true
    gsap.killTweensOf(pivot.rotation)
    velY = 0
    lastX = e.clientX
    lastY = e.clientY
    el.setPointerCapture(e.pointerId)
    kickLoop?.()
  }
  const move = (e: PointerEvent) => {
    if (!dragging) return
    if (e.cancelable) e.preventDefault()
    if(props.mode==='play'){emit('update:gesture',THREE.MathUtils.clamp((props.gesture??0)+(props.product==='bananaMilk'?e.clientX-lastX:lastY-e.clientY)*.6,0,100));lastX=e.clientX;lastY=e.clientY;return}
    velY = (e.clientX - lastX) * 0.01
    pivot.rotation.y += velY
    pivot.rotation.x = THREE.MathUtils.clamp(pivot.rotation.x + (e.clientY - lastY) * 0.006, -0.6, 0.6)
    lastX = e.clientX
    lastY = e.clientY
    kickLoop?.()
  }
  const up = () => { dragging = false; if (mobile) velY = 0; kickLoop?.() }
  el.addEventListener('pointerdown', down)
  el.addEventListener('pointermove', move)
  el.addEventListener('pointerup', up)
  el.addEventListener('pointercancel', up)
  cleanups.push(() => {
    el.removeEventListener('pointerdown', down)
    el.removeEventListener('pointermove', move)
    el.removeEventListener('pointerup', up)
    el.removeEventListener('pointercancel', up)
  })

  const resize = () => {
    renderer!.setSize(el.clientWidth, el.clientHeight)
    camera.aspect = el.clientWidth / el.clientHeight
    camera.updateProjectionMatrix()
    kickLoop?.()
  }
  ro = new ResizeObserver(resize)
  ro.observe(el)
  resize()

  const clock = new THREE.Clock()
  let visible = false
  let renderUntil = 0
  let renderCount = 0
  const kick = () => {
    if (disposed) return
    renderUntil = performance.now() + 1500
    cancelAnimationFrame(raf)
    tick()
  }
  kickLoop = kick
  io = new IntersectionObserver(([entry]) => {
    const was = visible
    visible = entry.isIntersecting
    if (visible) loadModels()
    if (visible && !was) kick()
  })
  io.observe(el)

  const tick = () => {
    if (disposed) return
    const dt = Math.min(clock.getDelta(), .05)
    const t = clock.getElapsedTime()
    if (!dragging && props.mode!=='play') {
      velY *= Math.pow(0.94, dt * 60)
      pivot.rotation.y += (props.mode === 'rotate' && continuous ? .72 * dt : 0) + velY
    }
    pivot.position.y = !continuous || props.mode === 'play' ? 0 : Math.sin(t * 1.4) * 0.08
    camera.lookAt(0, 0, 0)
    renderer!.render(scene, camera)
    el.dataset.frames = String(++renderCount)
    el.dataset.rotation = `${pivot.rotation.x.toFixed(3)},${pivot.rotation.y.toFixed(3)}`
    if (visible && (continuous || dragging || performance.now() < renderUntil)) raf = requestAnimationFrame(tick)
  }
  tick()
  cleanups.push(() => {
    kickLoop = undefined
    gsap.killTweensOf([pivot.rotation, camera.position])
    Object.values(built).forEach(b => { gsap.killTweensOf(b.group.scale); b.parts.forEach(p => gsap.killTweensOf(p.obj.position)) })
  })
})

onBeforeUnmount(() => {
  disposed = true
  cancelAnimationFrame(raf)
  cleanups.forEach((f) => f())
  ro?.disconnect()
  io?.disconnect()
  disposables.forEach((d) => d.dispose())
  renderer?.dispose()
  renderer?.domElement.remove()
})
</script>

<template>
  <div ref="host" class="product-scene" data-cursor="DRAG" data-lenis-prevent-touch style="touch-action: none">
    <div v-if="!available" class="product-scene__fallback"><ProductArt :product="product" /><p>이 환경에서는 제품 이미지로 보여드려요.</p></div>
  </div>
</template>

<style scoped>
.product-scene {
  position: absolute;
  inset: 0;
  touch-action: none;
  cursor: grab;
  touch-action: none;
}
.product-scene__fallback { height: 100%; display: grid; place-items: center; padding: 40px 50px 76px; }
.product-scene__fallback .product-art { height: 85%; width: 100%; }
.product-scene__fallback p { font-size: 12px; text-align: center; }
.product-scene:active {
  cursor: grabbing;
}
.product-scene :deep(canvas) {
  display: block;
}
</style>
