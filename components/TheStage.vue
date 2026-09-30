<script setup lang="ts">
import * as THREE from 'three'
import gsap from 'gsap'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { products, type ProductKey } from '~/data/content'

/**
 * 페이지 전체에 하나뿐인 3D 스테이지.
 * 섹션의 제품 자리(`[data-stage="<productKey>"]`)를 매 프레임 읽어
 * 화면 중앙에 가까운 자리들로 제품을 부드럽게 옮기고, 제품이 바뀌면 교체 연출을 한다.
 *
 * 자리 속성
 *  - data-stage="bananaMilk"          표시할 제품
 *  - data-stage-anim="scale" | "x"    조립 애니메이션 진행도 (자리 크기 / 들어오는 패널의 가로 위치 기준)
 *  - data-stage-mode="featured"       브랜드북 챕터 연출 (data-stage-chapter="0..5")
 */

const canvasHost = ref<HTMLDivElement>()
let cleanup: (() => void) | undefined

onMounted(async () => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

  let renderer: THREE.WebGLRenderer
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  } catch {
    return // WebGL을 못 쓰면 렌더 이미지 그대로
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.NeutralToneMapping
  canvasHost.value!.appendChild(renderer.domElement)

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100)
  camera.position.set(0, 0, 10)
  const pmrem = new THREE.PMREMGenerator(renderer)
  const studio = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
  scene.environment = studio
  scene.add(new THREE.AmbientLight('#ffffff', 0.35))
  const key = new THREE.DirectionalLight('#ffffff', 1.5)
  key.position.set(-3, 6, 5)
  scene.add(key)

  const resize = () => {
    renderer.setSize(window.innerWidth, window.innerHeight)
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
  }
  resize()
  window.addEventListener('resize', resize)

  // ---- 제품 리그 ------------------------------------------------------------
  const keys = products.map((p) => p.key)
  const gltfs = await Promise.all(keys.map((k) => loadProductGLTF(k)))
  if (gltfs.some((g) => !g)) {
    renderer.dispose()
    renderer.domElement.remove()
    return // 모델이 없으면 렌더 이미지 그대로
  }
  const rigs = new Map<ProductKey, ProductRig>()
  keys.forEach((k, i) => {
    const rig = makeRig(gltfs[i]!, k, { cloneMaterials: k === 'bananaMilk' })
    rig.group.visible = false
    scene.add(rig.group)
    rigs.set(k, rig)
  })
  document.documentElement.classList.add('stage-ready')

  // ---- 브랜드북 챕터 연출용 오브젝트 -------------------------------------------
  const jar = rigs.get('bananaMilk')!
  // SHAPE: 와이어프레임 겹치기
  const wireMat = new THREE.MeshBasicMaterial({ color: '#1a1a1a', wireframe: true, transparent: true, opacity: 0, depthWrite: false })
  jar.meshes.forEach((m) => m.add(new THREE.Mesh(m.geometry, wireMat)))
  // COLOR: 몸통 색 변주
  const bodyMats = jar.meshes
    .filter((m) => /body/i.test(m.name) || /body/i.test(m.parent?.name ?? ''))
    .flatMap((m) => (Array.isArray(m.material) ? m.material : [m.material])) as THREE.MeshStandardMaterial[]
  const baseColors = bodyMats.map((m) => m.color.clone())
  // AD: 반짝이 입자
  const sparkCount = 90
  const sparkGeo = new THREE.BufferGeometry()
  const sparkPos = new Float32Array(sparkCount * 3)
  for (let i = 0; i < sparkCount; i++) {
    const a = Math.random() * Math.PI * 2
    const r = 1.6 + Math.random() * 1.4
    sparkPos.set([Math.cos(a) * r, (Math.random() - 0.5) * 3, Math.sin(a) * r], i * 3)
  }
  sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPos, 3))
  const sparkTex = (() => {
    const c = document.createElement('canvas')
    c.width = c.height = 64
    const g = c.getContext('2d')!
    g.translate(32, 32)
    g.fillStyle = '#fff6e0'
    g.beginPath()
    for (let i = 0; i < 8; i++) {
      const r = i % 2 === 0 ? 30 : 7
      const a = (i / 8) * Math.PI * 2
      g.lineTo(Math.cos(a) * r, Math.sin(a) * r)
    }
    g.fill()
    return new THREE.CanvasTexture(c)
  })()
  const sparkMat = new THREE.PointsMaterial({ size: 0.28, map: sparkTex, transparent: true, opacity: 0, depthWrite: false })
  const sparks = new THREE.Points(sparkGeo, sparkMat)
  jar.spin.add(sparks)
  // PEOPLE: 주위를 도는 작은 단지들
  const crowd = new THREE.Group()
  for (let i = 0; i < 10; i++) {
    const r = makeRig(gltfs[keys.indexOf('bananaMilk')]!, 'bananaMilk', { size: 0.9 })
    const a = (i / 10) * Math.PI * 2
    r.group.position.set(Math.cos(a) * 1.9, (i % 3) * 0.35 - 0.35, Math.sin(a) * 1.9)
    crowd.add(r.group)
  }
  crowd.scale.setScalar(0.0001)
  jar.group.add(crowd)

  // ---- 상태 -------------------------------------------------------------------
  const pointer = { x: 0, y: 0 }
  const onMove = (e: PointerEvent) => {
    pointer.x = (e.clientX / window.innerWidth) * 2 - 1
    pointer.y = (e.clientY / window.innerHeight) * 2 - 1
  }
  window.addEventListener('pointermove', onMove)

  const cur = { x: 0, y: 0, h: 0, progress: 1 }
  const swap = { s: 0 }
  let shown: ProductKey | null = null
  let wanted: ProductKey | null = null
  let spinY = 0
  let spinKick = 0
  const fx = [0, 0, 0, 0, 0, 0] // 챕터별 연출 강도

  const applyEnv = async (k: ProductKey) => {
    const tex = await loadProductEnv(renderer, pmrem, k)
    if (tex && shown === k) {
      scene.environment = tex
      scene.environmentRotation.set(0, envRotation(k), 0)
    }
  }

  const show = (k: ProductKey) => {
    wanted = k
    gsap.killTweensOf(swap)
    const enter = () => {
      if (shown) rigs.get(shown)!.group.visible = false
      shown = wanted
      rigs.get(shown!)!.group.visible = true
      spinKick += Math.PI
      applyEnv(shown!)
      gsap.to(swap, { s: 1, duration: 0.55, ease: 'back.out(1.7)' })
    }
    if (shown && swap.s > 0.01) gsap.to(swap, { s: 0, duration: 0.18, ease: 'power2.in', onComplete: enter })
    else enter()
  }

  const clamp01 = (v: number) => Math.min(1, Math.max(0, v))

  const tick = (_time: number, deltaMs: number) => {
    const dt = Math.min(deltaMs, 64) / 1000
    const k = 1 - Math.pow(0.0008, dt) // 프레임과 무관한 부드러운 따라가기
    const vw = window.innerWidth
    const vh = window.innerHeight
    const diag = Math.hypot(vw, vh) * 0.5

    // 1) 화면에 보이는 제품 자리들의 가중 평균
    let sw = 0
    let sx = 0
    let sy = 0
    let sh = 0
    let best: HTMLElement | null = null
    let bestW = 0
    let bestRect: DOMRect | null = null
    let featuredW = 0
    let chapter = 0
    for (const el of document.querySelectorAll<HTMLElement>('[data-stage]')) {
      const r = el.getBoundingClientRect()
      if (r.width < 2 || r.bottom < 0 || r.top > vh || r.right < 0 || r.left > vw) continue
      const cx = r.left + r.width / 2
      const cy = r.top + r.height / 2
      const centrality = Math.max(0, 1 - Math.hypot(cx - vw / 2, cy - vh / 2) / diag)
      const w = centrality ** 4
      if (w <= 0) continue
      sw += w
      sx += cx * w
      sy += cy * w
      sh += r.height * w
      if (el.dataset.stageMode === 'featured') {
        featuredW = w
        chapter = Number(el.dataset.stageChapter ?? 0)
      }
      if (w > bestW) {
        bestW = w
        best = el
        bestRect = r
      }
    }

    if (sw > 1e-4 && best && bestRect) {
      const el: HTMLElement = best
      const r: DOMRect = bestRect
      const tx = sx / sw
      const ty = sy / sw
      const th = sh / sw
      if (cur.h === 0) Object.assign(cur, { x: tx, y: ty })
      cur.x += (tx - cur.x) * k
      cur.y += (ty - cur.y) * k
      cur.h += (th - cur.h) * k

      const want = el.dataset.stage as ProductKey
      if (rigs.has(want) && want !== wanted) show(want)

      // 조립 애니메이션 진행도
      let p = 1
      if (el.dataset.stageAnim === 'scale') p = clamp01(r.height / Math.max(1, el.offsetHeight))
      else if (el.dataset.stageAnim === 'x') {
        // 가로로 들어오는 패널: 패널(offsetParent) 왼쪽이 화면 왼쪽에 닿으면 완성
        const panel = (el.offsetParent as HTMLElement | null) ?? el
        p = clamp01(1 - panel.getBoundingClientRect().left / (vw * 0.6))
      }
      cur.progress += (p - cur.progress) * Math.min(1, k * 1.6)
    } else {
      cur.h += (0 - cur.h) * k
    }

    // 2) 챕터 연출 강도
    const fw = sw > 0 ? featuredW / sw : 0
    fx.forEach((v, i) => (fx[i] = v + ((i === chapter ? fw : 0) - v) * k))

    if (!shown) return renderer.render(scene, camera)
    const rig = rigs.get(shown)!

    // 3) 화면 좌표 → 월드 좌표
    const visH = 2 * camera.position.z * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))
    const px2w = visH / vh
    rig.group.position.set((cur.x - vw / 2) * px2w, -(cur.y - vh / 2) * px2w, 0)
    const s = ((cur.h * px2w * 0.95) / 2.8) * swap.s * (1 + fx[5] * 0.12)
    rig.group.scale.setScalar(Math.max(s, 0.0001))
    rig.group.visible = s > 0.001

    // 4) 회전: 기본 천천히 + 교체 시 한 바퀴 + 포인터 + AD 챕터에서 빠르게
    spinY += dt * (0.35 + fx[3] * 2.2)
    spinKick *= Math.pow(0.02, dt)
    rig.spin.rotation.y = spinY + spinKick + pointer.x * 0.35
    rig.spin.rotation.x = pointer.y * 0.12

    // 5) 조립 애니메이션 + PACKAGE 챕터 분해
    rig.pose(cur.progress, shown === 'bananaMilk' ? fx[2] : 0)

    // 6) 브랜드북 연출 (바나나우유)
    if (shown === 'bananaMilk') {
      wireMat.opacity = fx[0] * 0.45
      const hue = new THREE.Color().setHSL((performance.now() / 1000) * 0.12 % 1, 0.85, 0.55)
      bodyMats.forEach((m, i) => m.color.copy(baseColors[i]).lerp(hue, fx[1] * 0.85))
      sparkMat.opacity = fx[3]
      sparks.rotation.y += dt * 0.6
      crowd.scale.setScalar(Math.max(fx[4], 0.0001))
      crowd.rotation.y += dt * 0.5
    }

    renderer.render(scene, camera)
  }
  gsap.ticker.add(tick)

  cleanup = () => {
    gsap.ticker.remove(tick)
    window.removeEventListener('resize', resize)
    window.removeEventListener('pointermove', onMove)
    document.documentElement.classList.remove('stage-ready')
    scene.traverse((o) => {
      const m = o as THREE.Mesh
      if (m.geometry) m.geometry.dispose()
    })
    pmrem.dispose()
    renderer.dispose()
    renderer.domElement.remove()
  }
})

onBeforeUnmount(() => cleanup?.())
</script>

<template>
  <div ref="canvasHost" class="stage" aria-hidden="true" />
</template>

<style scoped>
.stage {
  position: fixed;
  inset: 0;
  z-index: 40;
  pointer-events: none;
}
.stage :deep(canvas) {
  display: block;
}
</style>

<style>
/* 3D가 준비되면 자리의 렌더 이미지는 숨긴다 (3D를 못 쓰면 이미지가 그대로 보임) */
[data-stage] .product-art {
  transition: opacity 0.5s;
}
html.stage-ready [data-stage] .product-art {
  opacity: 0;
}
</style>
