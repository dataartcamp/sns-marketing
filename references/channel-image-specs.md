# 채널별 이미지 SPEC

SNS 발행용 이미지 사이즈·안전영역 가이드. Buffer API는 HTTPS 공개 URL을 요구하므로 마지막에 Google Drive 호스팅 URL 규칙을 정리한다.

## 빠른 매핑

| 용도 | 사이즈 | 비율 |
|------|--------|------|
| **Instagram 피드 (기본)** | **1080×1350** | **4:5** |
| Instagram 피드 정사각형 | 1080×1080 | 1:1 |
| Instagram Reel · Story | 1080×1920 | 9:16 |
| Threads 이미지 | 1080×1350 또는 1080×1080 | 4:5 또는 1:1 |
| X.com 이미지 | 1600×900 | 16:9 |
| LinkedIn 이미지 | 1200×627 | 1.91:1 |

---

## Instagram

### 피드 — 1080×1350 (4:5) 기본

4:5 세로형이 모바일 화면 점유율이 가장 높고 engagement도 가장 좋다. 인스타 피드 기본값.
정사각형(1:1, 1080×1080)은 캐러셀 슬라이드에 적합.

**안전영역:** 가장자리 60px 패딩 + 4:5 세로는 상하 80px 추가. 텍스트·로고는 그 안에 배치.

### Reel · Story — 1080×1920 (9:16)

| 영역 | 픽셀 |
|------|------|
| 상단 UI 가림 | 약 250px (프로필 표시) |
| 하단 UI 가림 | 약 350px (캡션·버튼·음악) |
| 안전 중앙 영역 | **1080 × 1320** — 핵심 텍스트는 여기에 |

> Reel 커버는 피드 그리드에서 4:5로도 노출된다.
> 9:16 본 영역 + 4:5 그리드 크롭의 공통 안전영역(가로 1080 전체 + 세로 중앙 1350)에 핵심 배치.

### 파일 형식

- JPG 또는 PNG, sRGB
- **파일 크기: 8MB 이하 (Buffer 한도)** ⚠️ 휴대폰 원본 사진(12MP, 5~12MB)은 자주 초과 — 업로드 전 1080×1350 리사이즈 권장
- HTTPS 공개 URL (로컬 파일·인증 URL 거부)

---

## Threads · X.com · LinkedIn

| 채널 | 사이즈 | 비고 |
|------|--------|------|
| Threads | 1080×1350 또는 1080×1080 | 이미지 선택 (텍스트만 가능) |
| X.com | 1600×900 (16:9) | 최대 4장 |
| LinkedIn | 1200×627 (1.91:1) | 정사각형도 허용 |

---

## 호스팅 — Google Drive HTTPS URL 만들기

Buffer API는 발행 시 이미지에 HTTPS 공개 URL을 요구한다. Google Drive 사용 시 다음 규칙을 따른다.

### URL 패턴

| 용도 | URL | Buffer 동작 |
|------|-----|------------|
| 공유 링크 원본 | `https://drive.google.com/file/d/FILE_ID/view?usp=sharing` | ❌ HTML 페이지로 인식 |
| **직접 PNG URL (권장)** | `https://lh3.googleusercontent.com/d/FILE_ID` | ✅ **redirect 없음, Buffer 통과 검증** |
| 다이렉트 다운로드 | `https://drive.google.com/uc?export=download&id=FILE_ID` | △ 브라우저·일반 fetcher OK, Buffer는 redirect 미지원으로 `Failed to fetch image dimensions` 실패 사례 있음 |
| 다이렉트 뷰 | `https://drive.google.com/uc?export=view&id=FILE_ID` | △ uc 다운로드와 같은 redirect 체인 |
| 썸네일 | `https://drive.google.com/thumbnail?id=FILE_ID&sz=w1080` | △ 사이즈 강제 변환, 원본 비율 보장 X |

**기본 규칙: `https://lh3.googleusercontent.com/d/<FILE_ID>` 사용.**

**왜 lh3가 안정적인가**: `drive.google.com/...` 패턴은 302 redirect 체인을 거쳐 결국 lh3로 가는 구조. 브라우저·`httpx`는 자동으로 추적하지만 Buffer의 image fetcher는 redirect 처리에 보수적이라 첫 redirect에서 멈춰 "Not Found"로 판정. lh3 URL은 체인의 끝이라 redirect 없이 PNG를 바로 응답한다.

> 만료 위험이 있는 건 Google Photos preview에서 자동 발급되는 일회성 토큰 URL(`lh3.googleusercontent.com/A_...` 같은 알파벳·하이픈 토큰)이며, **파일 ID 기반 `/d/<FILE_ID>` 형태와는 다르다.** 후자는 안정적.

### FILE_ID 추출

```
https://drive.google.com/file/d/1Ab2Cd3Ef4Gh5Ij/view?usp=sharing
                              └── FILE_ID ──┘
                              ↓
https://lh3.googleusercontent.com/d/1Ab2Cd3Ef4Gh5Ij
```

### 권한 설정 (필수)

1. Drive에서 파일 우클릭 → **공유**
2. 일반 액세스 → **링크가 있는 모든 사용자**
3. 역할 → **뷰어**

권한이 "제한됨"이면 Buffer가 401/403을 받아 발행 실패한다.

### 한계

- Drive는 원본을 그대로 서빙한다 (사이즈·포맷 변환 없음) → **업로드 전에 SPEC에 맞춰 만들 것**
- 100MB 이상은 "다운로드 확인" 페이지가 끼어들어 발행 실패. 인스타 이미지 8MB 한도라 무관
- 단기간 다운로드 폭증 시 24시간 일시 차단 사례 있음 — 1회성 발행은 안전, 광고 트래픽 노출용으론 부적합

### 워크플로우

```
1. SPEC에 맞춰 이미지 생성 (예: 1080×1350)
2. Google Drive에 업로드
3. 공유 권한을 "링크가 있는 모든 사용자, 뷰어"로 변경
4. 공유 링크에서 FILE_ID 추출
5. URL 조립: https://lh3.googleusercontent.com/d/<FILE_ID>
6. Buffer createPost의 assets.images[].url 에 전달
```
