<script setup lang="ts">
import * as THREE from 'three'
import * as CANNON from 'cannon-es'
import gsap from 'gsap'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { products, type ProductKey } from '~/data/content'

// "오늘의 틈 모으기": 카드를 만들 때마다 3D 제품이 떨어져 쌓이고, 커서로 밀 수 있다.
const host = ref<HTMLDivElement>()
const ready = ref(false)
const MAX = 22
const SIZE = 1.45 // 제품 높이 (월드 단위)

let dropImpl: ((key?: ProductKey, x?: number) => void) | undefined
let cleanup: (() => void) | undefined
let disposed = false
const unavailable = ref(false)

function drop(key?: ProductKey) {
  dropImpl?.(key)
}
defineExpose({ drop })

onMounted(async () => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { unavailable.value = true; return }
  const el = host.value!
  const mobile = window.matchMedia('(pointer: coarse)').matches || window.innerWidth <= 800
  let dirty = true
  let lastInteraction = performance.now()
  let renderer: THREE.WebGLRenderer
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  } catch {
    unavailable.value = true
    return
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, mobile ? 1 : 1.75))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.NeutralToneMapping
  renderer.shadowMap.enabled = !mobile
  renderer.shadowMap.type = THREE.PCFShadowMap
  el.appendChild(renderer.domElement)

  const scene = new THREE.Scene()
  const pmrem = new THREE.PMREMGenerator(renderer)
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
  scene.add(new THREE.AmbientLight('#ffffff', 0.4))
  const sun = new THREE.DirectionalLight('#ffffff', 1.6)
  sun.position.set(-3, 8, 6)
  sun.castShadow = true
  sun.shadow.mapSize.set(1024, 1024)
  Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 })
  scene.add(sun)

  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100)
  camera.position.set(0, 0.8, 9)
  camera.lookAt(0, 0, 0)

  // ---- 물리 세계 ----
  const world = new CANNON.World({ gravity: new CANNON.Vec3(0, -14, 0) })
  world.allowSleep = true
  const mat = new CANNON.Material('m')
  world.addContactMaterial(new CANNON.ContactMaterial(mat, mat, { friction: 0.35, restitution: 0.25 }))

  let halfW = 5
  let halfH = 2.2
  const walls: CANNON.Body[] = []
  const floorMesh = new THREE.Mesh(new THREE.PlaneGeometry(40, 6), new THREE.ShadowMaterial({ opacity: 0.18 }))
  floorMesh.rotation.x = -Math.PI / 2
  floorMesh.receiveShadow = true
  scene.add(floorMesh)

  const buildWalls = () => {
    walls.forEach((w) => world.removeBody(w))
    walls.length = 0
    const add = (shape: CANNON.Shape, pos: CANNON.Vec3, quat?: CANNON.Quaternion) => {
      const b = new CANNON.Body({ mass: 0, material: mat, shape })
      b.position.copy(pos)
      if (quat) b.quaternion.copy(quat)
      world.addBody(b)
      walls.push(b)
    }
    add(new CANNON.Box(new CANNON.Vec3(halfW + 2, 0.5, 2)), new CANNON.Vec3(0, -halfH - 0.5, 0)) // 바닥
    add(new CANNON.Box(new CANNON.Vec3(0.5, 20, 2)), new CANNON.Vec3(-halfW - 0.5, 0, 0))
    add(new CANNON.Box(new CANNON.Vec3(0.5, 20, 2)), new CANNON.Vec3(halfW + 0.5, 0, 0))
    add(new CANNON.Box(new CANNON.Vec3(halfW + 2, 20, 0.5)), new CANNON.Vec3(0, 0, -1.4)) // 뒤
    add(new CANNON.Box(new CANNON.Vec3(halfW + 2, 20, 0.5)), new CANNON.Vec3(0, 0, 1.4)) // 앞
    floorMesh.position.y = -halfH
  }

  const resize = () => {
    dirty = true
    const w = el.clientWidth
    const h = el.clientHeight
    renderer.setSize(w, h)
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    const visH = 2 * camera.position.z * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))
    halfH = visH / 2 - 0.4
    halfW = (visH * camera.aspect) / 2 - 0.3
    buildWalls()
  }
  const ro = new ResizeObserver(resize)
  ro.observe(el)
  resize()
  const disposeBase = () => {
    ro.disconnect()
    scene.environment?.dispose()
    floorMesh.geometry.dispose(); floorMesh.material.dispose(); sun.shadow.dispose()
    pmrem.dispose(); renderer.dispose(); renderer.domElement.remove()
  }
  cleanup = disposeBase

  // ---- 제품 ----
  const keys = products.map((p) => p.key)
  const gltfs = await Promise.all(keys.map((k) => loadProductGLTF(k)))
  if (disposed) return
  if (gltfs.some((g) => !g)) {
    unavailable.value = true
    disposeBase(); cleanup = undefined
    return
  }
  ready.value = true

  interface Item { body: CANNON.Body; obj: THREE.Object3D }
  const items: Item[] = []

  const makeItem = (key: ProductKey) => {
    const rig = makeRig(gltfs[keys.indexOf(key)]!, key, { size: SIZE, tilt: false })
    rig.group.traverse((o) => ((o as THREE.Mesh).isMesh ? ((o as THREE.Mesh).castShadow = true) : null))
    // 충돌체: 모델 크기에 맞춘 원기둥/상자
    const box = new THREE.Box3().setFromObject(rig.group)
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())
    rig.spin.position.sub(center)
    const shape =
      key === 'samanco'
        ? new CANNON.Box(new CANNON.Vec3(size.x / 2, size.y / 2, size.z / 2))
        : new CANNON.Cylinder(Math.min(size.x, size.z) * 0.42, Math.min(size.x, size.z) * 0.42, size.y, 12)
    const body = new CANNON.Body({ mass: 1, material: mat, shape, angularDamping: 0.3, linearDamping: 0.1, allowSleep: true, sleepSpeedLimit: .2, sleepTimeLimit: .6 })
    return { body, obj: rig.group }
  }

  dropImpl = (key, x) => {
    if (disposed) return
    dirty = true
    lastInteraction = performance.now()
    const k = key ?? keys[Math.floor(Math.random() * keys.length)]
    const it = makeItem(k)
    it.body.position.set(x ?? (Math.random() - 0.5) * halfW * 1.4, halfH + 2.5, (Math.random() - 0.5) * 0.6)
    it.body.quaternion.setFromEuler(Math.random() * 0.6, Math.random() * Math.PI, (Math.random() - 0.5) * 1.2)
    it.body.angularVelocity.set((Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4)
    world.addBody(it.body)
    scene.add(it.obj)
    gsap.from(it.obj.scale, { x: 0.3, y: 0.3, z: 0.3, duration: 0.4, ease: 'back.out(2)' })
    items.push(it)
    if (items.length > (mobile ? 8 : MAX)) {
      const old = items.shift()!
      world.removeBody(old.body)
      gsap.to(old.obj.scale, { x: 0, y: 0, z: 0, duration: 0.3, onComplete: () => scene.remove(old.obj) })
    }
  }

  // ---- 커서로 밀기 ----
  const pusher = new CANNON.Body({ mass: 0, type: CANNON.Body.KINEMATIC, shape: new CANNON.Sphere(0.55) })
  pusher.position.set(0, -50, 0)
  world.addBody(pusher)
  const ray = new THREE.Raycaster()
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)
  const hit = new THREE.Vector3()
  const toWorld = (e: PointerEvent) => {
    const r = el.getBoundingClientRect()
    ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera)
    return ray.ray.intersectPlane(plane, hit)
  }
  const onMove = (e: PointerEvent) => {
    dirty = true
    lastInteraction = performance.now()
    const p = toWorld(e)
    if (!p) return
    const prev = pusher.position.clone()
    pusher.position.set(p.x, p.y, 0)
    pusher.velocity.set((p.x - prev.x) * 30, (p.y - prev.y) * 30, 0)
    items.forEach((it) => it.body.wakeUp())
  }
  const onLeave = () => { pusher.position.set(0, -50, 0); pusher.velocity.setZero() }
  const onClick = (e: PointerEvent) => {
    const p = toWorld(e)
    dropImpl?.(undefined, p ? THREE.MathUtils.clamp(p.x, -halfW + 0.6, halfW - 0.6) : undefined)
  }
  el.addEventListener('pointermove', onMove)
  el.addEventListener('pointerleave', onLeave)
  el.addEventListener('click', onClick)

  // ---- 루프: 화면에 보일 때만 ----
  let visible = false
  let started = false
  const io = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting
    if (visible && !started) {
      started = true
      keys.forEach((k, i) => gsap.delayedCall(0.25 * i, () => dropImpl?.(k)))
    }
  })
  io.observe(el)

  const tick = (_time: number, deltaMs: number) => {
    if (!visible || document.hidden || disposed) return
    // Stop tiny residual collision oscillations after a mobile interaction has settled.
    // Dragging/tapping wakes the bodies again, so the pile remains interactive.
    if (mobile && performance.now() - lastInteraction > 6000) items.forEach(it => it.body.sleep())
    const awake = items.filter(it => it.body.sleepState !== CANNON.Body.SLEEPING).length
    el.dataset.awake = String(awake)
    if (!dirty && awake === 0) return
    // 1/60초 고정 간격, 프레임이 늦어지면 최대 10단계까지 따라잡는다
    world.step(1 / 60, Math.min(deltaMs / 1000, .05), 3)
    pusher.velocity.setZero()
    items.forEach(({ body, obj }) => {
      obj.position.set(body.position.x, body.position.y, body.position.z)
      obj.quaternion.set(body.quaternion.x, body.quaternion.y, body.quaternion.z, body.quaternion.w)
    })
    renderer.render(scene, camera)
    dirty = false
  }
  gsap.ticker.add(tick)

  cleanup = () => {
    dropImpl = undefined
    items.forEach(({ obj }) => { gsap.killTweensOf(obj.scale); obj.traverse(o => { const m = o as THREE.Mesh; if (m.isMesh) (Array.isArray(m.material) ? m.material : [m.material]).forEach(mat => mat.dispose()) }) })
    gsap.ticker.remove(tick)
    io.disconnect()
    el.removeEventListener('pointermove', onMove)
    el.removeEventListener('pointerleave', onLeave)
    el.removeEventListener('click', onClick)
    disposeBase()
  }
})

onBeforeUnmount(() => { disposed = true; cleanup?.() })
</script>

<template>
  <div v-show="!unavailable" class="phys card">
    <div ref="host" class="phys__canvas" data-cursor="PUSH" />
    <p class="phys__hint body-m">
      <span class="kicker">오늘의 틈 모으기</span>
      {{ ready ? '카드를 만들 때마다 하나씩 떨어져요. 클릭하면 더, 마우스로 밀어보세요.' : '불러오는 중…' }}
    </p>
  </div>
</template>

<style scoped>
.phys {
  position: relative;
  margin-top: clamp(32px, 5vh, 56px);
  overflow: hidden;
  background: linear-gradient(#fff6e0, #fdeec8);
}
.phys__canvas {
  height: clamp(280px, 38vh, 420px);
  touch-action: pan-y;
}
.phys__canvas :deep(canvas) {
  display: block;
}
.phys__hint {
  position: absolute;
  left: 18px;
  top: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: calc(100% - 36px);
  font-size: 13px;
  pointer-events: none;
}
</style>
