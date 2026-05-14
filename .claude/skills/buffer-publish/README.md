# buffer-publish — Claude Code 스킬

Buffer API(GraphQL)로 Threads · Instagram · LinkedIn에 콘텐츠를 발행/예약하는
**Claude Code 스킬**입니다. 언어·프레임워크·프로젝트 구조에 무관하게 사용할 수 있는
일반화 버전입니다.

---

## 이 스킬이 하는 일

Claude Code 세션에서 Buffer API 관련 작업을 요청하면, 이 스킬이 자동으로 활성화되어
Buffer GraphQL API 패턴, 채널별 제약, 스케줄링 방법, 주의사항을 Claude에게 제공합니다.

```
사용자: "Threads에 3포스트 캐스케이딩 예약 발행 코드 만들어줘"
Claude: (buffer-publish 스킬 참조) → 정확한 GraphQL mutation + 예시 코드 제공
```

---

## 사전 준비

### 1. Claude Code 설치
```bash
npm install -g @anthropic/claude-code
```
또는 [claude.ai/code](https://claude.ai/code) 에서 설치

### 2. Buffer 계정 및 API 키
1. [buffer.com](https://buffer.com) 에서 무료 계정 생성
2. Buffer 대시보드 → **Settings → API** → API 키 발급
3. 대시보드 → **Channels** → 발행할 SNS 채널 연결 (Threads, Instagram 등)

### 3. Python 실습 환경 (선택)
예제 코드를 직접 실행하려면 Python 3.9+ 필요 → [examples/](examples/) 참조

---

## 설치

### 방법 A — Claude Code 전역 설치 (모든 프로젝트에서 사용)

```powershell
# Windows PowerShell
xcopy /E /I buffer-publish "%USERPROFILE%\.claude\skills\buffer-publish"
```

```bash
# Mac / Linux
cp -r buffer-publish ~/.claude/skills/buffer-publish
```

설치 후 Claude Code를 재시작하면 스킬이 자동 인식됩니다.

### 방법 B — Antigravity 전역 설치

```powershell
# Windows PowerShell
xcopy /E /I buffer-publish "%USERPROFILE%\.gemini\antigravity\skills\buffer-publish"
```

```bash
# Mac / Linux
cp -r buffer-publish ~/.gemini/antigravity/skills/buffer-publish
```

설치 후 Antigravity를 재시작하면 스킬이 자동 인식됩니다.

### 방법 C — 프로젝트 로컬 설치 (Claude Code)

```bash
cp -r buffer-publish <프로젝트루트>/.claude/skills/buffer-publish
```

> **경로 요약**
>
> | 도구 | Windows 경로 | Mac/Linux 경로 |
> |------|-------------|----------------|
> | Claude Code 전역 | `%USERPROFILE%\.claude\skills\` | `~/.claude/skills/` |
> | Antigravity 전역 | `%USERPROFILE%\.gemini\antigravity\skills\` | `~/.gemini/antigravity/skills/` |
> | 프로젝트 로컬 | `<프로젝트>\.claude\skills\` | `<프로젝트>/.claude/skills/` |

---

## 사용 방법

Claude Code 대화에서 아래 키워드가 포함된 요청을 하면 스킬이 자동 활성화됩니다.

| 요청 예시 | 스킬 활성화 여부 |
|----------|----------------|
| "Buffer API로 Threads 발행 코드 만들어줘" | ✅ |
| "Instagram 예약 발행 구현 방법 알려줘" | ✅ |
| "Buffer GraphQL createPost 예시 보여줘" | ✅ |
| "SNS 자동 발행 파이프라인 만들고 싶어" | ✅ |
| "Buffer 채널 연동 구현" | ✅ |

### 직접 요청 예시

```
# 단일 포스트 발행 코드 요청
"Threads에 텍스트 포스트 발행하는 Python 코드 작성해줘"

# 캐스케이딩 스레드
"Threads 3포스트 캐스케이딩 예약 발행 구현해줘. 내일 오전 9시 KST"

# 멀티채널
"Threads랑 Instagram에 같은 시각에 예약 발행하는 패턴 알려줘"

# 오류 처리
"Buffer API 429 rate limit 처리 어떻게 해?"
```

---

## 파일 구조

```
buffer-publish/
├── README.md                        ← 이 문서
├── SKILL.md                         ← 스킬 메인 (Claude가 읽는 워크플로우 가이드)
├── references/
│   ├── graphql-mutations.md         ← Buffer GraphQL 쿼리/mutation 전체 스키마
│   ├── channel-constraints.md       ← 채널별 글자 수·미디어·해시태그 제약
│   ├── scheduling-patterns.md       ← 단일/멀티/배치 스케줄링 패턴
│   └── gotchas.md                   ← 공식 문서에 없는 함정 9가지
└── examples/
    ├── requirements.txt             ← 예제 실행에 필요한 Python 패키지
    └── quickstart.py                ← 최소 동작 예제 (Threads 단일 발행)
```

### references 파일별 역할

| 파일 | 내용 |
|------|------|
| `graphql-mutations.md` | account · channels · createPost 쿼리 전문, 변수 구조, 응답 파싱 |
| `channel-constraints.md` | Threads(500자/캐스케이딩), Instagram(미디어 필수/릴스), LinkedIn 제약 |
| `scheduling-patterns.md` | 단일 예약, 멀티채널 동시 예약, 배치 스케줄링 3패턴 |
| `gotchas.md` | `assets:null` 오류, 채널 ID 사전조회, Google Drive URL, UTC변환 등 실전 함정 |

---

## Buffer 무료 플랜 한도

| 항목 | 값 |
|------|-----|
| 연결 채널 수 | 최대 3개 |
| 채널당 예약 슬롯 | 10개 |
| API 요청 | **100건/일** (API 키 단위) |
| 발행 횟수 | 무제한 |

> ⚠️ API 요청 100건/일 한도는 테스트·개발 시 쉽게 소진됩니다.
> 채널 ID를 캐싱하면 30개 발행 시 ~32건으로 절약 가능합니다. (`gotchas.md` #4 참조)

---

## 예제 코드 실행

```bash
cd examples
pip install -r requirements.txt
cp .env.example .env      # API 키 입력
python quickstart.py
```

---

## 이 스킬이 다루지 않는 것

- Buffer 웹 대시보드 조작 (UI 클릭 방법)
- 특정 프로젝트의 폴더 구조나 CLI 명령어
- Buffer 유료 기능 (Analytics, Team 협업 등)
- 콘텐츠 생성 (이 스킬은 발행만 담당)

---

## 관련 자료

- [Buffer API 공식 문서](https://publish.buffer.com) (로그인 후 Settings → API)
- [Buffer GraphQL Explorer](https://api.buffer.com) (Bearer 토큰 필요)
- Claude Code 공식 문서: [claude.ai/code](https://claude.ai/code)
