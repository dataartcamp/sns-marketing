# AI 마케팅 에이전트 — 수강생 실습 Kit

**강의**: 나만의 AI 마케팅 에이전트, 오늘 첫 출근  
**도구**: Claude Code · Antigravity · Buffer API

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

`.env` 파일을 열고 Buffer API 키 입력:

```
BUFFER_API_KEY=여기에_붙여넣기
```

**완료.** 에디터로 `sns-marketing/` 폴더를 열면 스킬이 자동 인식됩니다.

---

## 에디터별 스킬 인식

| 에디터 | 자동 인식 경로 |
|--------|--------------|
| Claude Code | `.claude/skills/buffer-publish/` |
| Antigravity | `.gemini/antigravity/skills/buffer-publish/` |

별도 설치 없이 폴더를 에디터로 열기만 하면 됩니다.

---

## 폴더 구조

```
sns-marketing/
├── .env.example                              ← API 키 템플릿 (공통)
├── .env                                      ← 내 API 키 (직접 생성, git 제외)
├── .claude/
│   └── skills/
│       └── buffer-publish/                   ← Claude Code 자동 인식
│           ├── SKILL.md
│           ├── README.md
│           ├── references/
│           └── examples/
│               ├── quickstart.py             ← 선택: API 연결 테스트
│               └── requirements.txt
├── .gemini/
│   └── antigravity/
│       └── skills/
│           └── buffer-publish/               ← Antigravity 자동 인식
│               ├── SKILL.md
│               ├── README.md
│               ├── references/
│               └── examples/
│                   ├── quickstart.py         ← 선택: API 연결 테스트
│                   └── requirements.txt
└── .gitignore
```

---

## Buffer 사전 준비

1. [buffer.com](https://buffer.com) 무료 가입
2. 대시보드 → **Settings → API** → API 키 발급
3. 대시보드 → **Channels** → SNS 채널 연결 (Instagram / X.com / Threads)
4. 발급받은 키 → `.env` 파일에 입력
