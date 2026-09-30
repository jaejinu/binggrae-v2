# 에셋 넣는 곳

파일을 아래 경로/이름으로 넣으면 자동으로 교체됩니다. 없으면 기본 그래픽이 보입니다.
경로를 바꾸고 싶으면 `data/content.ts`의 `image` / `model` 값을 수정하세요.

| 위치 | 파일 | 쓰이는 곳 |
|---|---|---|
| `public/products/` | `yoplait.png`, `samanco.png`, `bravo.png`, `banana-milk.png` | 제품 일러스트 전체 (배경 투명 PNG 권장, 세로 5:6 비율) |
| `public/models/` | `yoplait.glb`, `samanco.glb`, `bravo.glb`, `banana-milk.glb` | LOOK CLOSER 3D (파트가 분리된 모델이면 Explode 가능) |
| `public/images/` | `time-package.jpg`, `time-ad.jpg`, `time-photo.jpg`, `time-now.jpg` | TIME WITH BINGGRAE (4:5) |
| `public/images/` | `story-design.jpg`, `story-color.jpg`, `story-naming.jpg`, `story-memory.jpg`, `story-culture.jpg` | STORIES 커버 |
| `public/fonts/` | `Binggrae.(woff2\|otf\|ttf)`, `Binggrae-Bold.*`, `BinggraeSamanco-Bold.*` | 빙그레체(본문 보조) / 빙그레 싸만코체(한글 제목) — 공식 배포 파일을 **수정 없이** 파일명만 맞춰 넣기 |
| `public/images/` | `today-new-product.jpg`, `today-collaboration.jpg`, `today-campaign.jpg`, `today-popup.jpg`, `today-brand-film.jpg` | TODAY 카드 (1:1) |

## 폰트 라이선스 메모

빙그레 서체는 무료·상업적 사용이 가능하지만 **수정 및 재배포가 금지**되어 있습니다.
공식 배포처에서 직접 내려받아 사용하고, 폰트 파일을 공개 저장소에 올리는 것은 피하세요.
