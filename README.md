# 빙그레할 틈 — Everyday moments of small joy

> 크게 웃을 일은 없어도, 빙그레할 틈은 있으니까.

빙그레를 ‘바쁜 일상 속 작은 즐거움의 틈을 만드는 브랜드’로 재해석한 **브랜드 리뉴얼 콘셉트 프로젝트**의 메인 페이지입니다.
공식 사이트가 아니며, 제품 그래픽은 실제 로고·패키지 대신 형태만 단순화한 오리지널 일러스트/3D입니다.

## 섹션

| # | 섹션 | 내용 |
|---|---|---|
| 01 | HERO | 빽빽한 일정 타이포 → 스크롤하면 글자 사이가 벌어지고 그 틈으로 제품 등장 |
| 02 | MOMENTS | 하루의 순간(아침/오후/기분 전환/하루의 끝)으로 제품 발견 |
| 03 | ICONS | 네 가지 대표 제품을 한 화면씩 가로로 넘기기 (팀원 상세페이지 연결) |
| 04 | LOOK CLOSER | 3D 제품 Rotate / Zoom / Explode / Detail |
| 05 | TIME WITH BINGGRAE | 패키지 → 광고 → 사진 → 현재 |
| 06 | STORIES | 브랜드 매거진 (Editorial) |
| 07 | FEATURED | 단지, 50년의 이야기 — 스크롤 기반 Digital Brand Book 미리보기 |
| 08 | TODAY | 현재 브랜드 활동 |
| 09 | YOUR MOMENT | 참여형 그래픽 카드 생성 + PNG 저장 |
| 10 | NEWS | 공지 / 기업 정보 |

## 실행

```sh
npm install
npm run dev          # http://localhost:3000
```

Docker:

```sh
docker compose up -d --build   # http://localhost:3300
```

## 수정 가이드

- 모든 문구·색·링크: `data/content.ts` (`[예시]` 표시된 항목은 실제 자료로 교체)
- 제품 일러스트: `components/ProductArt.vue`
- 3D 제품: `components/ProductScene.vue`
- 팀원 상세페이지 경로: `/icons/yoplait`, `/icons/samanco`, `/icons/bravo`, `/icons/banana-milk` (현재 `pages/[...slug].vue` 준비 중 페이지)

## Stack

Nuxt 3 · Three.js · GSAP (ScrollTrigger) · Lenis

### Labelled Blender model integration

The shared stage and product inspector now use the concept GLBs in `public/models/teum/`. Editable Blender sources are in the sibling `binggrae-teum/three/` project. The original models remain in place. Product fallback images are in `public/products/teum/`.

`productParts()` maps the named lid, front wafer and ice-cream groups to their separation offsets, preserving attached label meshes. Samanco uses its native upright orientation. The hero message has opaque cream panels and an earlier reveal for readability. Reverse labels and internal layers are original concept designs.

Validation: Nuxt typecheck and production build; local Chrome desktop/mobile start flow, shared 3D stage, four product selections and separation controls. The existing optional font-format warnings remain in the production build.

### Product play and archive pass

LOOK CLOSER includes product-specific progress controls: opening the Yoplait foil, choosing the Samanco wafer opening direction, sliding the Bravo sleeve, and finding the banana milk reverse label. The progress slider is keyboard-accessible; dragging in play mode adjusts the same progress. `useProductFinish.ts` supplies fine wafer bump variation and material roughness adjustments. The shared stage gives each product a different entrance and settles near the front label.

The last product chosen in LOOK CLOSER is available in the personal card form. Product and card color can be changed explicitly; PNG export includes both. Cards stay in browser local storage. `/brandbook` contains six scroll-linked editorial scenes, with official 2024 package/book images and direct source links. See `SOURCES.md` for provenance.
