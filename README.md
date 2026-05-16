# AI 마케팅 에이전트 — 수강생 실습 Kit

**저작**: dataartcamp ｜ **강의**: 나만의 AI 마케팅 에이전트, 오늘 첫 출근
**도구**: Claude Code · Antigravity · Buffer API · Gemini API

---

## 설치 (2단계)

### Step 1 — 클론

```bash
git clone https://github.com/dataartcamp/sns-marketing.git
cd sns-marketing
```

클론하면 `sns-marketing/` 폴더가 자동 생성됩니다.
클론 위치(경로)는 어디든 상관없습니다.

### Step 2 — API 키 설정

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

`.env` 파일을 열고 키 입력:

```
BUFFER_API_KEY=여기에_붙여넣기
GEMINI_API_KEY=여기에_붙여넣기
GEMINI_IMAGE_MODEL=gemini-3.1-flash-image-preview
```

**완료.** 에디터로 `sns-marketing/` 폴더를 열면 스킬이 자동 인식됩니다.

---

## 자동 인식되는 두 스킬

| 스킬 | 역할 |
|------|------|
| **contents-creator** | 원본 .md 또는 한 줄 주제 → Instagram · Threads · X.com 채널별 콘텐츠 자동 생성 (OSMU) |
| **buffer-publish** | Buffer API로 Threads · Instagram · LinkedIn 발행 / 예약 (이미지 pre-flight 검증 포함) |

### 기본 흐름

```
원본 .md (또는 한 줄 주제)
    ↓ contents-creator
채널별 publish-ready 글 (instagram_post.md · threads_post.md · x_post.md)
    ↓ (선택) Gemini로 인스타 피드 이미지 생성 → Google Drive 업로드
    ↓ buffer-publish
Buffer 큐 등록 → 예약 시각에 자동 발행
```

### 에디터별 자동 인식 경로

| 에디터 | 경로 |
|--------|------|
| Claude Code | `.claude/skills/` |
| Antigravity | `.gemini/antigravity/skills/` |

별도 설치 없이 폴더를 에디터로 열기만 하면 됩니다.

---

## 폴더 구조

```
sns-marketing/
├── .env.example                            ← API 키 템플릿 (공통)
├── .env                                    ← 내 API 키 (직접 생성, git 제외)
├── examples/
│   ├── quickstart.py                       ← 선택: Buffer API 연결 테스트
│   └── requirements.txt
├── references/                             ← 공통 채널·API 레퍼런스
│   ├── graphql-mutations.md                ← Buffer GraphQL 쿼리/mutation 스키마
│   ├── channel-constraints.md              ← 채널별 글자 수·미디어·해시태그 제약
│   ├── channel-image-specs.md              ← 채널별 이미지 사이즈·안전영역 + Google Drive URL 규칙
│   ├── scheduling-patterns.md              ← 단일/멀티/배치 스케줄링 패턴
│   └── gotchas.md                          ← 공식 문서에 없는 함정 (8MB 한도, Drive URL redirect 등)
├── .claude/skills/                         ← Claude Code 자동 인식
│   ├── buffer-publish/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── image-preflight.md          ← 발행 전 이미지 검증 (사이즈·비율·파일 크기)
│   └── contents-creator/
│       └── SKILL.md
├── .gemini/antigravity/skills/             ← Antigravity 자동 인식 (.claude 미러)
│   ├── buffer-publish/                     (SKILL.md + references/image-preflight.md)
│   └── contents-creator/                   (SKILL.md)
└── .gitignore
```

---

## 사전 준비 — 외부 서비스 키 발급

### Buffer (SNS 발행)

1. [buffer.com](https://buffer.com) 무료 가입
2. 대시보드 → **Settings → API** → API 키 발급
3. 대시보드 → **Channels** → SNS 채널 연결 (Instagram / X.com / Threads 등)
4. 발급받은 키 → `.env` 의 `BUFFER_API_KEY`

### Gemini (이미지 생성)

1. [Google AI Studio](https://aistudio.google.com/apikey) 에서 API 키 발급 (무료)
2. 키 → `.env` 의 `GEMINI_API_KEY`
3. 이미지 모델은 `gemini-3.1-flash-image-preview` (기본값 — `.env.example`에 이미 들어 있음)

### Google Drive (이미지 호스팅)

Buffer는 이미지 발행 시 HTTPS 공개 URL을 요구합니다. Google Drive를 호스팅으로 쓸 때:

1. 이미지를 Drive에 업로드
2. 우클릭 → **공유** → "링크가 있는 모든 사용자" → 뷰어
3. 공유 링크에서 `FILE_ID` 추출 → `https://lh3.googleusercontent.com/d/<FILE_ID>` 형식으로 변환
4. 변환된 URL을 `buffer-publish`에 전달

자세한 URL 규칙은 [references/channel-image-specs.md](references/channel-image-specs.md) 참조.
