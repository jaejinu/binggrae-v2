# 에셋 넣는 곳

파일을 아래 경로/이름으로 넣으면 자동으로 교체됩니다. 없으면 기본 그래픽이 보입니다.
경로를 바꾸고 싶으면 `data/content.ts`의 `image` / `model` 값을 수정하세요.

| 위치 | 파일 | 쓰이는 곳 |
|---|---|---|
| `public/products/` | `yoplait.webp`, `samanco.webp`, `bravo.webp`, `banana-milk.webp` | 제품 이미지 전체 (투명 배경, 세로 5:6). 현재 `blender/build_products.py` 렌더 결과 |
| `public/models/` | `yoplait.glb`, `samanco.glb`, `bravo.glb`, `banana-milk.glb` | LOOK CLOSER 3D (Draco 압축 지원, 파트가 분리된 모델이면 Explode 가능) |
| `public/env/` | `sunrise.exr`, `courtyard.exr`, `city.exr`, `interior.exr` | LOOK CLOSER 제품별 조명 (Poly Haven CC0) |
| `public/images/` | `time-package.jpg`, `time-ad.jpg`, `time-photo.jpg`, `time-now.jpg` | TIME WITH BINGGRAE (4:5) |
| `public/images/` | `story-design.jpg`, `story-color.jpg`, `story-naming.jpg`, `story-memory.jpg`, `story-culture.jpg` | STORIES 커버 |
| `public/fonts/` | `Binggrae.(woff2\|otf\|ttf)`, `Binggrae-Bold.*`, `BinggraeSamanco-Bold.*` | 빙그레체(본문 보조) / 빙그레 싸만코체(한글 제목) — 공식 배포 파일을 **수정 없이** 파일명만 맞춰 넣기 |
| `public/images/` | `today-new-product.jpg`, `today-collaboration.jpg`, `today-campaign.jpg`, `today-popup.jpg`, `today-brand-film.jpg` | TODAY 카드 (1:1) |

## 폰트 라이선스 메모

빙그레 서체는 무료·상업적 사용이 가능하지만 **수정 및 재배포가 금지**되어 있습니다.
공식 배포처에서 직접 내려받아 사용하고, 폰트 파일을 공개 저장소에 올리는 것은 피하세요.

## TODAY / 참여 카드 확장 (2026-09-30)

TODAY의 `today-*.jpg` 5장은 built-in image_gen으로 제작한 콘셉트 이미지이며, 실제 출시·협업·팝업 행사 사진이 아닙니다. 최종 프롬프트: `public/images/today-prompts.json`. 원본 생성 파일은 Codex generated_images에 보존하고 사이트에는 1000px JPEG를 저장했습니다.

참여 카드에 사용한 추가 제품 이미지는 빙그레 공식 제품 목록에서 가져왔습니다. 생성 이미지가 아닙니다. 출처: https://www.bing.co.kr/search/search_product (제품·상표 권리는 원 권리자에게 있습니다.)

- `products/more/melona.png`: https://www.bing.co.kr/upload/product/taste_melona_original.png
- `products/more/together.png`: https://www.bing.co.kr/upload/product/taste_together_original.png
- `products/more/excellent.png`: https://www.bing.co.kr/upload/product/taste_excellent_original.png
- `products/more/kkotgerang.png`: https://www.bing.co.kr/upload/brand/2024/04/0e3470bd-b06a-4e7d-8e29-c71c5d33b245.png

추가 참여/물리 인터랙션 제품:

- `/products/more/bibibig.png`: https://www.bing.co.kr/upload/product/taste_bibibig_original.png
- `/products/more/bbangtttoa.png`: https://www.bing.co.kr/upload/brand/2024/05/e8efd75a-9524-4c03-8928-84155e8d9302.png
- `/products/more/yomamte.png`: https://www.bing.co.kr/upload/brand/2024/05/a79e51dd-ea20-41b5-a4ff-8aff32fcf161.png
- `/products/more/cledor.png`: https://www.bing.co.kr/upload/brand/2026/08/3a60be14-397d-46ea-b3cf-65160c88ad10.png
- `/products/more/deowisanyang.png`: https://www.bing.co.kr/upload/brand/2026/05/172c4ad2-0bea-41d5-b008-690ce019bcac.png
- `/products/more/ttaom.png`: https://www.bing.co.kr/upload/brand/2026/05/3a2cb47b-9f49-444f-827c-b2c552a45d87.png
- `/products/more/acafela.png`: https://www.bing.co.kr/upload/brand/2026/05/640e42ff-e2b3-4759-afd8-e0ed7078cd9e.png
- `/products/more/jucyCool.png`: https://www.bing.co.kr/upload/brand/2026/09/642ba2f3-5e8e-428a-a3bd-26db5247d585.png
