import * as THREE from 'three'
import { GLTFLoader, type GLTF } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { EXRLoader } from 'three/examples/jsm/loaders/EXRLoader.js'
import { products, type ProductKey } from '~/data/content'

// 블렌더에서 만든 제품 GLB를 한 번만 내려받아 여러 장면(스테이지·물리)에서 복제해 쓴다.

let gltfLoader: GLTFLoader | null = null
const gltfCache = new Map<ProductKey, Promise<GLTF | null>>()

export function loadProductGLTF(key: ProductKey): Promise<GLTF | null> {
  if (!gltfCache.has(key)) {
    gltfLoader ??= new GLTFLoader().setDRACOLoader(new DRACOLoader().setDecoderPath('/draco/'))
    const url = products.find((p) => p.key === key)!.model
    gltfCache.set(key, gltfLoader.loadAsync(url).catch(() => null))
  }
  return gltfCache.get(key)!
}

/** 눕혀서 모델링한 제품은 카메라 쪽으로 기울여 보여준다 */
export const VIEW_TILT: Partial<Record<ProductKey, number>> = { samanco: 0.95 }

export interface RigPart {
  obj: THREE.Object3D
  rest: THREE.Vector3
  explode: THREE.Vector3
}

export interface ProductRig {
  key: ProductKey
  /** 위치·크기를 조정하는 바깥 그룹 */
  group: THREE.Group
  /** 회전용 그룹 */
  spin: THREE.Group
  root: THREE.Object3D
  parts: RigPart[]
  mixer: THREE.AnimationMixer | null
  duration: number
  /** 0 = 조립 전, 1 = 완성. explode = 0..1 분해 정도 */
  pose(progress: number, explode?: number): void
  meshes: THREE.Mesh[]
}

/**
 * GLTF를 복제해 높이 기준으로 정규화한 리그를 만든다.
 * 블렌더에서 넣은 "완성되는" 애니메이션(마지막 프레임 = 완성)과 explode extras를 함께 다룬다.
 */
export function makeRig(gltf: GLTF, key: ProductKey, opts: { tilt?: boolean; cloneMaterials?: boolean; size?: number } = {}): ProductRig {
  const root = gltf.scene.clone(true)
  const meshes: THREE.Mesh[] = []
  root.traverse((o) => {
    const m = o as THREE.Mesh
    if (!m.isMesh) return
    if (opts.cloneMaterials) m.material = Array.isArray(m.material) ? m.material.map((x) => x.clone()) : m.material.clone()
    meshes.push(m)
  })

  // 블렌더는 오브젝트마다 애니메이션을 따로 내보낸다. 모두 같은 시점에서 시작하므로
  // 공통 시간 t를 각 애니메이션 길이 안으로 제한해 직접 지정한다.
  // (mixer.setTime은 한 번 끝난 LoopOnce 액션을 멈춘 채로 두기 때문에 쓰지 않는다)
  let mixer: THREE.AnimationMixer | null = null
  let duration = 0
  const actions: THREE.AnimationAction[] = []
  if (gltf.animations.length) {
    mixer = new THREE.AnimationMixer(root)
    gltf.animations.forEach((clip) => {
      const action = mixer!.clipAction(clip)
      action.setLoop(THREE.LoopOnce, 1)
      action.clampWhenFinished = true
      action.play()
      actions.push(action)
      duration = Math.max(duration, clip.duration)
    })
  }
  // glTF의 기본 자세는 첫 프레임(조립 전)이므로, 크기·기준 위치는 마지막 프레임(완성)에서 계산한다
  const settle = (t: number) => {
    actions.forEach((a) => {
      a.enabled = true
      a.paused = false
      a.time = Math.min(t, a.getClip().duration * 0.9999)
    })
    mixer?.update(0)
  }
  settle(duration)
  root.updateMatrixWorld(true)

  const box = new THREE.Box3().setFromObject(root)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const scale = (opts.size ?? 2.8) / Math.max(size.x, size.y, size.z)
  root.position.sub(center)

  const inner = new THREE.Group()
  inner.add(root)
  inner.scale.setScalar(scale)
  if (opts.tilt !== false) inner.rotation.x = VIEW_TILT[key] ?? 0
  const spin = new THREE.Group()
  spin.add(inner)
  const group = new THREE.Group()
  group.add(spin)

  const parts: RigPart[] = root.children.map((child) => {
    const e = child.userData.explode as number[] | undefined
    return {
      obj: child,
      rest: child.position.clone(),
      explode: Array.isArray(e) && e.length === 3 ? new THREE.Vector3(e[0], e[1], e[2]) : new THREE.Vector3(),
    }
  })

  const pose = (progress: number, explode = 0) => {
    parts.forEach((p) => p.obj.position.copy(p.rest))
    if (mixer) settle(THREE.MathUtils.clamp(progress, 0, 1) * duration)
    if (explode > 0) parts.forEach((p) => p.obj.position.addScaledVector(p.explode, explode))
  }
  pose(1)

  return { key, group, spin, root, parts, mixer, duration, pose, meshes }
}

// ---- 제품별 조명(HDRI) --------------------------------------------------------

const envCache = new WeakMap<THREE.WebGLRenderer, Map<ProductKey, Promise<THREE.Texture | null>>>()
let exrLoader: EXRLoader | null = null

/** 렌더러별로 PMREM 처리한 제품 HDRI를 캐시해서 돌려준다 */
export function loadProductEnv(renderer: THREE.WebGLRenderer, pmrem: THREE.PMREMGenerator, key: ProductKey): Promise<THREE.Texture | null> {
  let map = envCache.get(renderer)
  if (!map) envCache.set(renderer, (map = new Map()))
  if (!map.has(key)) {
    exrLoader ??= new EXRLoader()
    const url = products.find((p) => p.key === key)!.env
    map.set(
      key,
      exrLoader
        .loadAsync(url)
        .then((tex) => {
          const pm = pmrem.fromEquirectangular(tex).texture
          tex.dispose()
          return pm
        })
        .catch(() => null),
    )
  }
  return map.get(key)!
}

export function envRotation(key: ProductKey) {
  return THREE.MathUtils.degToRad(products.find((p) => p.key === key)!.envRotation)
}
