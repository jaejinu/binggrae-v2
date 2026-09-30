// public/ 에 파일이 있는지 확인. 있으면 실제 에셋, 없으면 기본 그래픽을 보여주기 위함.
const cache = new Map<string, Promise<boolean>>()

export function probeImage(src: string): Promise<boolean> {
  if (!cache.has(src)) {
    cache.set(
      src,
      new Promise((resolve) => {
        const img = new Image()
        img.onload = () => resolve(true)
        img.onerror = () => resolve(false)
        img.src = src
      }),
    )
  }
  return cache.get(src)!
}

/** src가 로드 가능하면 true가 되는 ref */
export function useImageAvailable(src: () => string | undefined) {
  const ok = ref(false)
  if (import.meta.client) {
    watch(
      src,
      async (s: string | undefined) => {
        ok.value = false
        if (s) ok.value = await probeImage(s)
      },
      { immediate: true },
    )
  }
  return ok
}
