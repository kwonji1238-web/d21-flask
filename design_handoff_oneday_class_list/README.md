# Handoff: 원데이 클래스 목록 화면 (Oneday Class List)

## Overview
주말에 배울 원데이 클래스를 고르는 20대 직장인용 목록 화면. 상단 카테고리 칩 + 정렬, 하단 클래스 카드 그리드. 모바일 우선, PC까지 반응형.

## About the Design Files
`Class List v2.dc.html`은 HTML로 만든 **디자인 레퍼런스**(동작하는 프로토타입)이지 프로덕션 코드가 아닙니다. 대상 코드베이스의 기존 환경(React / Vue / RN / SwiftUI 등)과 패턴으로 **재구현**하세요. 환경이 없다면 적합한 프레임워크(예: Next.js + React)를 선택해 구현합니다. 파일은 브라우저로 바로 열립니다(`support.js`, `image-slot.js` 같은 폴더 필요).

## Fidelity
**High-fidelity.** 색·타이포·간격·인터랙션 모두 최종값. 픽셀 단위로 재현하세요. 사진만 플레이스홀더(회색 #ece8df 영역)입니다.

## Screens / Views
보드에 4개 화면이 있습니다. 01~03은 같은 모바일 화면의 상태, 04는 PC.

### 공통 모바일 화면 (375 × auto)
배경 `#faf9f6`. 위→아래 순서:
1. **Status bar** 44px.
2. **App bar** 52px, 좌우 패딩 20/12. 좌: 워드마크 `oneday` 20px/800, letter-spacing -0.8px. 우: 검색(search), 장바구니(shopping-bag) 아이콘 버튼 44×44, 아이콘 22px.
3. **헤드라인 블록** padding 20/20/28, gap 14.
   - "이번 주말엔" 30px/300 + 줄바꿈 + "뭘 배워볼까요?" 30px/700. line-height 1.25, letter-spacing -1px.
   - 지역 버튼: map-pin 15px + "서울 전체" 14px/600 + chevron-down(50% opacity). 테두리·배경 없음.
4. **필터 바** (position: sticky; top 0; 배경 #faf9f6) padding 4/0/14, 행 gap 14.
   - 카테고리 칩 가로 스크롤(스크롤바 숨김), 좌우 패딩 20, gap 6.
     - 칩: height 36, padding 0 14, radius 999, 13px, **테두리 없음**.
     - 기본: bg `#f0ede6`, text `#555`, 500. 선택: bg `#1d1d1f`, text `#fff`, 700.
     - 항목: 전체 · 공예 · 디지털 · 운동 · 요리 · 드로잉
   - 결과/정렬 행 (좌우 패딩 20, space-between):
     - 좌: "총 **N**개" 13px #7a7a7a, 숫자 600 #1d1d1f.
     - 우: 정렬 버튼 — bg `#f0ede6`, radius 6, padding 8 8 8 12, 13px/600, 라벨 + chevron-down 15px. **스트로크 없음, 영역(배경)만.**
5. **카드 리스트** 1열, gap 36, padding 8/20/48.
6. **탭 바** (sticky bottom) 4열: 홈 · 클래스(활성) · 찜 · 마이. 아이콘 22px, 라벨 10px. 비활성 opacity .35, 활성 700. 상단 1px rgba(0,0,0,.06), 하단 safe-area 28px.

### 클래스 카드
- 사진: aspect-ratio 4/3, radius 4, bg `#ece8df`.
  - 할인 중이면 좌하단 배지: bg `#1d1d1f`, #fff, 12px/700, padding 6 10, radius 0, 텍스트 "{할인율} 할인 중".
- 정보 블록 (gap 8, 사진과 gap 14):
  1. 메타 행: 카테고리 태그(bg `#dcf06a` 라임, 11px/700, padding 3 6, radius 2) + 지역 12px #7a7a7a. 우측 끝 찜 버튼(터치영역 36, 아이콘 20).
  2. 클래스명: 18px/600, letter-spacing -0.5px, line-height 1.35. (PC 17px)
  3. 가격
     - 할인: `{할인율}` 18px/800 `#e0461f` + 판매가 18px/800 + 정가 13px #9a9a9a **line-through**.
     - 정가만: 판매가 18px/800.
     - 가격 없음(null): **"가격 문의"** 16px/700 #555.
  4. 평점: star 13px + 평점(소수 1자리) 13px/700 #1d1d1f + "리뷰 {n}" 13px #7a7a7a (천 단위 콤마).
     - 리뷰 0건: **"아직 리뷰가 없어요"** 13px #9a9a9a.
- 할인율 = round((1 − 할인가/정가) × 100)%. 금액 = `toLocaleString('ko-KR') + '원'`.

### 01 목록 — 기본
정렬 = 추천순, 카테고리 = 전체. 프레임 높이 auto(전체 길이 노출).

### 02 정렬 바텀시트
- Dim: rgba(0,0,0,.45), 전체 덮음. 탭하면 닫힘.
- 시트: bg #fff, 상단 radius 16, 하단 padding 36.
  - 그래버 36×4, radius 2, #d9d6cf.
  - 헤더: "정렬" 18px/700 + 닫기(x) 44×44.
  - 옵션 행: min-height 64, padding 10 14, radius 10, 좌우 바깥 여백 12.
    - 라벨 16px(선택 700/기본 500) + 설명 12px #8a8a8a.
    - **선택 행은 bg `#f4f2ec` 영역만**(테두리 없음) + 우측 24px 라임(#dcf06a) 원 안 check 15px.
  - 옵션/설명:
    - 추천순 — 만족도와 최근 예약을 함께 반영해요
    - 평점 높은순 — 별점이 높은 클래스부터
    - 리뷰 많은순 — 후기가 많이 쌓인 클래스부터
    - 가격 낮은순 — 가격 문의 클래스는 맨 뒤로 가요
- 옵션 탭 → 정렬 적용 + 시트 닫힘(별도 확인 버튼 없음).

### 03 필터 적용
카테고리 = 공예, 정렬 = 가격 낮은순. 결과 수가 즉시 반영되는 상태 예시.

### 04 PC (1280)
- 컨테이너 bg #faf9f6, 좌우 패딩 48.
- GNB 72px: 워드마크 24px/800 · 메뉴(홈 / **클래스** / 이벤트) 15px · 검색 필드(280×42, radius 21, bg #f0ede6, placeholder "배우고 싶은 걸 검색해 보세요") · 찜·마이 아이콘.
- 헤드라인 한 줄 40px(300 + 700), 우측에 지역 선택.
- 툴바: 좌 카테고리 칩(height 40, 14px), 우 "총 N개" + 정렬 버튼 → 드롭다운(240px, bg #fff, radius 10, padding 8, shadow 0 12px 32px rgba(0,0,0,.12); 행 44px, 선택 행 bg #f4f2ec + check).
- 그리드 4열, gap 48(row) / 24(col).

## Responsive
| 폭 | 열 |
|---|---|
| < 640px | 1열 |
| 640–1023px | 2열 |
| 1024–1279px | 3열 |
| ≥ 1280px | 4열 |
모바일(<1024)은 정렬을 바텀시트로, PC는 드롭다운으로.

## Interactions & Behavior
- 칩 탭: 카테고리 필터 즉시 적용, 카운트 갱신. press 시 scale(.95) 200ms ease.
- 정렬:
  - rec: 기본 순서(서버 추천 점수)
  - rating: 평점 desc, 리뷰 없는 항목은 뒤
  - reviews: 리뷰 수 desc
  - price: 실판매가(할인가 ?? 정가) asc, 가격 문의는 맨 뒤
- 바텀시트: 열기/닫기(dim 탭, x, 옵션 선택). 권장 전환 opacity+translateY 250ms ease.
- 찜: 토글. 켜짐 = 채워진 하트 #e0461f. 카드 클릭 이벤트로 전파하지 않음(stopPropagation).
- 카드 탭 → 클래스 상세(이번 범위 밖).
- 필터 바는 스크롤 시 상단 고정, 탭 바는 하단 고정.
- 빈 결과 상태·로딩 스켈레톤은 미정의 — 필요 시 디자인 요청.

## State Management
- `category: '전체' | '공예' | '디지털' | '운동' | '요리' | '드로잉'`
- `sort: 'rec' | 'rating' | 'reviews' | 'price'`
- `isSortSheetOpen: boolean`
- `likedIds: Set<id>` (서버 동기화)
- 데이터: `GET /classes?category=&sort=` 권장. 항목 타입:
```ts
type OnedayClass = {
  id: string; category: string; area: string; name: string;
  price: number | null;      // 정가. null → '가격 문의'
  salePrice: number | null;  // 할인가. 있으면 정가 취소선
  rating: number | null; reviewCount: number; // 0 → '아직 리뷰가 없어요'
  imageUrl: string;
};
```

## Design Tokens
- 배경 `#faf9f6` · 면(칩/정렬/검색) `#f0ede6` · 선택 행 `#f4f2ec` · 사진 플레이스홀더 `#ece8df`
- 잉크 `#1d1d1f` · 보조 `#555` · 메타 `#7a7a7a` · 비활성/취소선 `#9a9a9a` · 설명 `#8a8a8a` · 그래버 `#d9d6cf`
- 라임 액센트 `#dcf06a`(태그·선택 체크, 위 텍스트는 항상 #1d1d1f) · 할인/찜 `#e0461f`
- 라인 rgba(0,0,0,.06) · Dim rgba(0,0,0,.45)
- 폰트: Pretendard Variable → -apple-system / SF Pro Text → Inter. 굵기 300/400/500/600/700/800.
- Radius: 사진 4 · 태그 2 · 정렬 버튼 6 · 시트 옵션 10 · 시트 16 · 칩 999
- 간격: 화면 좌우 20(모바일)/48(PC), 카드 간 36(모바일)/48(PC)
- 터치 타깃 최소 44px

## Assets
- 아이콘: Lucide static 0.469.0 (`https://unpkg.com/lucide-static@0.469.0/icons/<name>.svg`) — search, shopping-bag, map-pin, chevron-down, heart, star, x, check, house, layout-grid, user, signal, wifi, battery-full. 코드베이스 아이콘 세트가 있으면 대체.
- 사진: 미제공(플레이스홀더). 실제 클래스 사진 필요 — 따뜻하고 자연광 톤의 작업 사진 권장.
- 데이터: 라탄 바구니 / 노션 정리법 / 커플 클라이밍 체험은 실제 예시, 나머지 5개는 레이아웃 확인용 샘플.

## Files
- `Class List v2.dc.html` — 전체 보드(모바일 3상태 + PC). 로직은 파일 하단 `class Component` 참고(정렬·필터·가격 포맷).
- `support.js`, `image-slot.js` — 프로토타입 실행용 런타임. 구현 대상 아님.
