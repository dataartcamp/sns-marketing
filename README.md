# AI 마케팅 에이전트 — 수강생 실습 Kit

**강의**: 나만의 AI 마케팅 에이전트, 오늘 첫 출근
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
| **contents-creator** | 원본 .md 또는 한 줄 주제 → Instagram · Threads · X.com 채널별 콘텐츠 자동 생성 |
| **buffer-publish** | Buffer API로 Threads · Instagram · LinkedIn 발행 / 예약 |

기본 흐름: `contents-creator`로 채널별 글 만들고 → 필요 시 이미지 생성·호스팅 → `buffer-publish`로 발행.

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
├── references/                             ← 공통 레퍼런스
│   ├── graphql-mutations.md                ← Buffer GraphQL 쿼리/mutation 스키마
│   ├── channel-constraints.md              ← 채널별 글자 수·미디어·해시태그 제약
│   ├── channel-image-specs.md              ← 채널별 이미지 사이즈·안전영역 + Google Drive URL 규칙
│   ├── scheduling-patterns.md              ← 단일/멀티/배치 스케줄링 패턴
│   └── gotchas.md                          ← 공식 문서에 없는 함정
├── .claude/skills/                         ← Claude Code 자동 인식
│   ├── buffer-publish/
│   └── contents-creator/
├── .gemini/antigravity/skills/             ← Antigravity 자동 인식
│   ├── buffer-publish/
│   └── contents-creator/
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
3. 이미지 모델은 `gemini-3.1-flash-image-preview` (기본값 — .env.example에 이미 들어 있음)
