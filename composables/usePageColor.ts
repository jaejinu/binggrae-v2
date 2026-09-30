import { ScrollTrigger } from 'gsap/ScrollTrigger'
import type { Ref } from 'vue'

// 페이지 전체 배경/글자색. 섹션이 화면 중앙에 오면 그 섹션 색으로 부드럽게 전환된다.
export function usePageColor() {
  const bg = useState('page-bg', () => '#ffd43b')
  const ink = useState('page-ink', () => '#1a1a1a')
  function set(b: string, i = '#1a1a1a') {
    bg.value = b
    ink.value = i
  }
  return { bg, ink, set }
}

interface SectionColor {
  bg: string
  ink?: string
}

/**
 * 섹션을 페이지 색 전환에 등록한다.
 * `trigger`는 기본적으로 섹션 루트이며, 자기 자신이 pin 되는 섹션은 pin-spacer를 넘겨준다.
 */
export function useSectionColor(root: Ref<HTMLElement | undefined>, colors: () => SectionColor, trigger?: () => Element | null | undefined) {
  const { set } = usePageColor()
  let st: ScrollTrigger | undefined
  let active = false

  const apply = () => {
    const c = colors()
    set(c.bg, c.ink)
  }

  onMounted(() => {
    st = ScrollTrigger.create({
      trigger: trigger?.() ?? root.value,
      start: 'top 55%',
      end: 'bottom 55%',
      // 레이아웃에 영향을 주지 않으므로 pin 계산이 끝난 뒤에 위치를 잡는다
      refreshPriority: -1,
      onToggle: (self) => {
        active = self.isActive
        if (active) apply()
      },
    })
  })

  // 섹션 안에서 선택이 바뀌어 색이 달라지는 경우
  watch(colors, () => active && apply(), { deep: true })

  onBeforeUnmount(() => st?.kill())
}
