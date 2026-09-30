<script setup lang="ts">
import * as THREE from 'three'
import gsap from 'gsap'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { products, type ProductKey } from '~/data/content'

// 단순화한 오리지널 3D 형태(로고·실제 패키지 없음). Rotate / Zoom / Explode / Detail 모드 지원.
export type Mode = 'rotate' | 'zoom' | 'explode' | 'detail'

const props = defineProps<{ product: ProductKey; mode: Mode }>()
const host = ref<HTMLDivElement>()

let renderer: THREE.WebGLRenderer | undefined
let raf = 0
let ro: ResizeObserver | undefined
let io: IntersectionObserver | undefined
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

// public/models/*.glb 가 있으면 그 모델을 사용. 크기·중심을 맞추고, 최상위 자식들을 분해 파트로 사용.
function fromGLB(root: THREE.Object3D): Built {
  const box = new THREE.Box3().setFromObject(root)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const scale = 2.8 / Math.max(size.x, size.y, size.z)
  root.position.sub(center)
  const inner = new THREE.Group()
  inner.add(root)
  inner.scale.setScalar(scale)
  const group = new THREE.Group()
  group.add(inner)
  const children = root.children.length > 1 ? root.children : root.children[0]?.children ?? []
  const parts: Part[] = children.map((child, i) => {
    const c = new THREE.Box3().setFromObject(child).getCenter(new THREE.Vector3())
    const dir = c.sub(center)
    if (dir.lengthSq() < 1e-6) dir.set(0, 1, 0).applyAxisAngle(new THREE.Vector3(0, 0, 1), i * 0.9)
    return { obj: child, explode: dir.normalize().multiplyScalar(0.9 / scale) }
  })
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

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  el.appendChild(renderer.domElement)

  scene.add(new THREE.AmbientLight('#ffffff', 1.1))
  const key = new THREE.DirectionalLight('#ffffff', 2.2)
  key.position.set(3, 5, 6)
  scene.add(key)

  const pivot = new THREE.Group()
  scene.add(pivot)

  const built = {} as Record<ProductKey, Built>
  const origins = new Map<THREE.Object3D, THREE.Vector3>()
  const register = (k: ProductKey, b: Built) => {
    b.parts.forEach((p) => origins.set(p.obj, p.obj.position.clone()))
    b.group.visible = false
    b.group.scale.setScalar(0.0001)
    pivot.add(b.group)
    built[k] = b
  }
  ;(Object.keys(builders) as ProductKey[]).forEach((k) => register(k, builders[k]()))

  const loader = new GLTFLoader()
  products.forEach((p) => {
    loader.load(
      p.model,
      (gltf) => {
        const old = built[p.key]
        pivot.remove(old.group)
        register(p.key, fromGLB(gltf.scene))
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

  let current: ProductKey | null = null
  function showProduct(k: ProductKey) {
    if (current) {
      const prev = built[current].group
      gsap.to(prev.scale, { x: 0.0001, y: 0.0001, z: 0.0001, duration: 0.3, ease: 'back.in(2)', onComplete: () => { prev.visible = false } })
    }
    current = k
    const g = built[k].group
    g.visible = true
    gsap.to(g.scale, { x: 1, y: 1, z: 1, duration: 0.7, delay: 0.2, ease: 'back.out(1.8)' })
    gsap.fromTo(pivot.rotation, { y: pivot.rotation.y - Math.PI }, { y: pivot.rotation.y, duration: 0.9, ease: 'power3.out' })
    applyMode(props.mode)
  }

  function applyMode(mode: Mode) {
    if (!current) return
    const exploded = mode === 'explode'
    built[current].parts.forEach((p) => {
      const o = origins.get(p.obj)!
      const t = exploded ? o.clone().add(p.explode) : o
      gsap.to(p.obj.position, { x: t.x, y: t.y, z: t.z, duration: 0.8, ease: exploded ? 'back.out(1.6)' : 'power3.inOut' })
    })
    const dist = mode === 'zoom' ? 5.4 : mode === 'detail' ? 6.6 : mode === 'explode' ? 11 : 9.5
    gsap.to(camera.position, { z: dist, duration: 0.9, ease: 'power3.inOut' })
  }

  showProduct(props.product)
  watch(() => props.product, (k: ProductKey) => showProduct(k))
  watch(() => props.mode, (m: Mode) => applyMode(m))

  // 드래그로 회전
  let dragging = false
  let lastX = 0
  let lastY = 0
  let velY = 0
  const down = (e: PointerEvent) => {
    dragging = true
    lastX = e.clientX
    lastY = e.clientY
    el.setPointerCapture(e.pointerId)
  }
  const move = (e: PointerEvent) => {
    if (!dragging) return
    velY = (e.clientX - lastX) * 0.01
    pivot.rotation.y += velY
    pivot.rotation.x = THREE.MathUtils.clamp(pivot.rotation.x + (e.clientY - lastY) * 0.006, -0.6, 0.6)
    lastX = e.clientX
    lastY = e.clientY
  }
  const up = () => (dragging = false)
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
  }
  ro = new ResizeObserver(resize)
  ro.observe(el)
  resize()

  const clock = new THREE.Clock()
  let visible = false
  io = new IntersectionObserver(([entry]) => {
    const was = visible
    visible = entry.isIntersecting
    if (visible && !was) {
      cancelAnimationFrame(raf)
      tick()
    }
  })
  io.observe(el)

  const tick = () => {
    const t = clock.getElapsedTime()
    if (!dragging) {
      velY *= 0.94
      pivot.rotation.y += props.mode === 'rotate' ? 0.012 + velY : velY
    }
    pivot.position.y = Math.sin(t * 1.4) * 0.08
    camera.lookAt(0, 0, 0)
    renderer!.render(scene, camera)
    if (visible) raf = requestAnimationFrame(tick)
  }
  tick()
})

onBeforeUnmount(() => {
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
  <div ref="host" class="product-scene" data-cursor="DRAG" />
</template>

<style scoped>
.product-scene {
  position: absolute;
  inset: 0;
  touch-action: pan-y;
  cursor: grab;
  touch-action: pan-y;
}
.product-scene:active {
  cursor: grabbing;
}
.product-scene :deep(canvas) {
  display: block;
}
</style>
