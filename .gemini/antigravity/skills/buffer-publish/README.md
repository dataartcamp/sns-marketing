# buffer-publish — Antigravity 스킬

Buffer API(GraphQL)로 Threads · Instagram · LinkedIn에 콘텐츠를 발행/예약하는
**Antigravity 스킬**입니다. 언어·프레임워크·프로젝트 구조에 무관하게 사용할 수 있는
일반화 버전입니다.

---

## 이 스킬이 하는 일

Antigravity 세션에서 Buffer API 관련 작업을 요청하면, 이 스킬이 자동으로 활성화되어
Buffer GraphQL API 패턴, 채널별 제약, 스케줄링 방법, 주의사항을 Antigravity에게 제공합니다.

```
사용자: "Threads에 3포스트 캐스케이딩 예약 발행 코드 만들어줘"
Antigravity: (buffer-publish 스킬 참조) → 정확한 GraphQL mutation + 예시 코드 제공
```

---

## 사전 준비

### 1. Buffer 계정 및 API 키
1. [buffer.com](https://buffer.com) 에서 무료 계정 생성
2. Buffer 대시보드 → **Settings → API** → API 키 발급
3. 대시보드 → **Channels** → 발행할 SNS 채널 연결 (Threads, Instagram 등)

### 2. API 키 설정
프로젝트 루트의 `.env.example` → `.env` 복사 후 키 입력:

```
BUFFER_API_KEY=여기에_붙여넣기
```

### 3. Python 실습 환경 (선택)
예제 코드를 직접 실행하려면 Python 3.9+ 필요 → [examples/](examples/) 참조

---

## 사용 방법

Antigravity 대화에서 아래 키워드가 포함된 요청을 하면 스킬이 자동 활성화됩니다.

| 요청 예시 | 스킬 활성화 여부 |
|----------|----------------|
| "Buffer API로 Threads 발행 코드 만들어줘" | ✅ |
| "Instagram 예약 발행 구현 방법 알려줘" | ✅ |
| "Buffer GraphQL createPost 예시 보여줘" | ✅ |
| "SNS 자동 발행 파이프라인 만들고 싶어" | ✅ |

---

## 파일 구조

```
buffer-publish/
├── README.md                        ← 이 문서
├── SKILL.md                         ← 스킬 메인 (Antigravity가 읽는 워크플로우 가이드)
├── references/
│   ├── graphql-mutations.md         ← Buffer GraphQL 쿼리/mutation 전체 스키마
│   ├── channel-constraints.md       ← 채널별 글자 수·미디어·해시태그 제약
│   ├── scheduling-patterns.md       ← 단일/멀티/배치 스케줄링 패턴
│   └── gotchas.md                   ← 공식 문서에 없는 함정 9가지
└── examples/
    ├── requirements.txt             ← 예제 실행에 필요한 Python 패키지
    └── quickstart.py                ← 최소 동작 예제 (Threads 단일 발행)
```

---

## Buffer 무료 플랜 한도

| 항목 | 값 |
|------|-----|
| 연결 채널 수 | 최대 3개 |
| 채널당 예약 슬롯 | 10개 |
| API 요청 | **100건/일** (API 키 단위) |

> ⚠️ API 요청 100건/일 한도는 테스트·개발 시 쉽게 소진됩니다.
> 채널 ID를 캐싱하면 절약 가능합니다. (`gotchas.md` #4 참조)

---

## 관련 자료

- [Buffer API 공식 문서](https://publish.buffer.com) (로그인 후 Settings → API)
- [Buffer GraphQL Explorer](https://api.buffer.com) (Bearer 토큰 필요)
