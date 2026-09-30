// 메인 페이지의 모든 문구/데이터. 기획안 기준이며, [예시] 표시된 항목은 실제 자료로 교체하세요.

export type ProductKey = 'yoplait' | 'samanco' | 'bravo' | 'bananaMilk'

export interface Product {
  key: ProductKey
  no: string
  name: string
  nameKo: string
  moment: string
  momentTime: string
  momentNote: string
  bg: string
  accent: string
  ink: string
  question: string
  answer: string
  details: string[]
  href: string // 팀원 상세페이지 경로
}

export const brand = {
  name: '빙그레할 틈',
  nameEn: 'Everyday moments of small joy.',
  tagline: ['크게 웃을 일은 없어도,', '빙그레할 틈은 있으니까.'],
}

export const nav = [
  { label: 'Moments', href: '#moments' },
  { label: 'Icons', href: '#icons' },
  { label: 'Look Closer', href: '#look-closer' },
  { label: 'Stories', href: '#stories' },
  { label: 'Today', href: '#today' },
  { label: 'News', href: '#news' },
]

export const hero = {
  schedule: [
    ['08:30', '출근'],
    ['09:10', '메일'],
    ['10:00', '회의'],
    ['11:20', '보고'],
    ['12:30', '점심'],
    ['13:40', '정리'],
    ['14:00', '미팅'],
    ['15:30', '통화'],
    ['16:30', '수정'],
    ['17:50', '재수정'],
    ['19:00', '퇴근?'],
    ['21:00', '야근'],
  ] as [string, string][],
  question: '오늘, 빙그레할 틈 있었나요?',
}

export const products: Product[] = [
  {
    key: 'yoplait',
    no: '01',
    name: 'YOPLAIT',
    nameKo: '요플레',
    moment: '시작하기 힘든 아침',
    momentTime: 'AM 07:40',
    momentNote: '눈은 떴지만 마음은 아직 이불 속. 한 숟갈로 시작하는 아침.',
    bg: '#ff9ebd',
    accent: '#ffffff',
    ink: '#1a1a1a',
    question: '왜 숟가락으로 떠먹게 되었을까?',
    answer: '마시는 대신 떠먹는 방식. 한 숟갈씩 천천히 즐기게 되는 형태의 이유를 따라가 봅니다.',
    details: ['컵 모양의 용기', '벗겨내는 뚜껑', '작은 숟가락'],
    href: '/icons/yoplait',
  },
  {
    key: 'bananaMilk',
    no: '04',
    name: 'BANANA MILK',
    nameKo: '바나나맛우유',
    moment: '나른한 오후',
    momentTime: 'PM 03:30',
    momentNote: '졸음이 몰려오는 오후 세 시 반. 빨대 하나 꽂는 짧은 휴식.',
    bg: '#ffd43b',
    accent: '#fff6e0',
    ink: '#1a1a1a',
    question: '왜 단지 모양일까?',
    answer: '둥근 몸통과 좁은 입구. 손에 쥐었을 때 떠오르는 그 형태의 이유를 따라가 봅니다.',
    details: ['둥근 몸통', '좁아지는 목', '은박 뚜껑'],
    href: '/icons/banana-milk',
  },
  {
    key: 'bravo',
    no: '03',
    name: 'BRAVO',
    nameKo: '부라보콘',
    moment: '기분 전환이 필요한 순간',
    momentTime: 'PM 05:10',
    momentNote: '일이 잘 안 풀리는 날. 콘 하나 들고 잠깐 바깥 공기.',
    bg: '#3d63dd',
    accent: '#ffd43b',
    ink: '#fff6e0',
    question: '왜 콘 형태일까?',
    answer: '들고 걸으며 먹을 수 있는 형태. 콘과 아이스크림이 한 번에 완성되는 이유를 따라가 봅니다.',
    details: ['바삭한 콘', '감싸는 포장지', '토핑'],
    href: '/icons/bravo',
  },
  {
    key: 'samanco',
    no: '02',
    name: 'SAMANCO',
    nameKo: '붕어싸만코',
    moment: '수고한 하루의 끝',
    momentTime: 'PM 10:20',
    momentNote: '오늘도 버틴 나에게. 머리부터 먹을지 꼬리부터 먹을지 고민하는 밤.',
    bg: '#e8542f',
    accent: '#ffd43b',
    ink: '#fff6e0',
    question: '왜 붕어 모양일까?',
    answer: '겨울 길거리 간식이 차가운 아이스크림이 되기까지. 그 모양에 담긴 기억을 따라가 봅니다.',
    details: ['붕어 모양 과자', '가운데 아이스크림', '팥 필링'],
    href: '/icons/samanco',
  },
]

// ICONS 섹션은 기획안의 ICON 번호 순서대로
export const iconOrder: ProductKey[] = ['yoplait', 'samanco', 'bravo', 'bananaMilk']

export const timeline = {
  title: 'Time with Binggrae',
  titleKo: '빙그레와 함께한 시간',
  intro: '연혁이 아니라, 제품을 통해 지나온 시간.',
  steps: [
    { label: 'PACKAGE', title: '과거의 패키지', note: '[예시] 처음 우리 손에 들렸던 모습', color: '#ffd43b' },
    { label: 'AD', title: '광고', note: '[예시] 우리가 기억하는 그 장면과 노래', color: '#ff9ebd' },
    { label: 'PHOTO', title: '사진', note: '[예시] 누군가의 앨범 속 한 장면', color: '#7ed957' },
    { label: 'NOW', title: '현재의 제품', note: '[예시] 지금 편의점 냉장고 속 모습', color: '#8fd3ff' },
  ],
  cta: { label: '브랜드 스토리 보기', href: '/story' },
}

export const stories = [
  { tag: 'DESIGN', title: '왜 바나나맛우유는 단지 모양일까?', color: '#ffd43b' },
  { tag: 'COLOR', title: '메로나의 초록색은 어떻게 하나의 맛이 되었을까?', color: '#7ed957' },
  { tag: 'NAMING', title: '‘투게더’라는 이름은 어떻게 만들어졌을까?', color: '#8fd3ff' },
  { tag: 'MEMORY', title: '50년 동안 바나나맛우유를 마신 사람들의 이야기', color: '#ff9ebd' },
  { tag: 'CULTURE', title: '붕어빵은 어떻게 여름에 얼게 되었을까?', color: '#e8542f' },
]

export const featured = {
  kicker: 'FEATURED STORY',
  title: '단지, 50년의 이야기',
  range: ['1974', '2024+'],
  chapters: [
    { no: '01', title: 'THE SHAPE', q: '왜 단지인가?' },
    { no: '02', title: 'THE COLOR', q: '왜 노란색인가?' },
    { no: '03', title: 'THE PACKAGE', q: '50년 동안 어떻게 변화했는가?' },
    { no: '04', title: 'THE AD', q: '우리는 어떻게 바나나맛우유를 기억하게 되었는가?' },
    { no: '05', title: 'THE PEOPLE', q: '사람들에게 바나나맛우유는 어떤 기억인가?' },
    { no: '06', title: 'TODAY', q: '50년이 지나도 왜 여전히 같은 형태를 기억할까?' },
  ],
  cta: { label: 'Digital Brand Book 열기', href: '/brandbook' },
}

export const today = {
  title: '빙그레는 오늘도 새로운 틈을 만듭니다.',
  items: [
    { tag: 'NEW PRODUCT', title: '[예시] 새로운 맛 출시 소식', color: '#ffd43b' },
    { tag: 'COLLABORATION', title: '[예시] 브랜드 협업 프로젝트', color: '#ff9ebd' },
    { tag: 'CAMPAIGN', title: '[예시] 계절 캠페인', color: '#7ed957' },
    { tag: 'POP-UP', title: '[예시] 팝업 스토어 오픈', color: '#8fd3ff' },
    { tag: 'BRAND FILM', title: '[예시] 브랜드 필름 공개', color: '#e8542f' },
  ],
}

export const yourMoment = {
  title: '오늘 너를 빙그레하게 한 건?',
  reasons: [
    { label: '날씨가 좋아서', emoji: '☀️', color: '#8fd3ff' },
    { label: '친구가 웃겨서', emoji: '😆', color: '#ff9ebd' },
    { label: '퇴근해서', emoji: '🏃', color: '#7ed957' },
    { label: '맛있는 걸 먹어서', emoji: '🍌', color: '#ffd43b' },
  ],
  placeholder: '짧게 한 줄 남겨주세요 (최대 40자)',
}

export const news = [
  { date: '2026.09.00', cat: 'NOTICE', title: '[예시] 공지사항 제목이 들어갑니다' },
  { date: '2026.09.00', cat: 'NEWS', title: '[예시] 보도자료 제목이 들어갑니다' },
  { date: '2026.08.00', cat: 'IR', title: '[예시] 기업 정보 관련 소식이 들어갑니다' },
  { date: '2026.08.00', cat: 'NOTICE', title: '[예시] 공지사항 제목이 들어갑니다' },
]
