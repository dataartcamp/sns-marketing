# contents-creator — Claude Code / Antigravity 스킬

원본 콘텐츠 1개를 받아 Instagram · Threads · X.com 각 채널 알고리즘과 UX에 맞춰
publish-ready Markdown 파일 3개를 생성하는 **OSMU(One Source Multi Use)
콘텐츠 워크플로우 스킬**입니다.

---

## 이 스킬이 하는 일

세션에서 다음과 같은 요청을 하면 자동 활성화되어 채널별 콘텐츠 파일을 생성합니다.

```
"이 블로그 초안 SNS 채널별로 다시 써줘"
"AI 시대 브랜드 전략 주제로 멀티채널 콘텐츠 만들어줘"
"Instagram · Threads · X 동시 발행용으로 OSMU 해줘"
```

**생성 결과:**

| 파일 | 길이 | 구조 |
|------|------|------|
| `instagram_post.md` | 1,000~1,800자 | Hook · Caption · CTA · Hashtags |
| `threads_post.md` | 300~700자 | Hook · Body · Discussion Question · CTA |
| `x_post.md` | 단일 220~260자 + 5~10개 스레드 | Single Post · Thread Version · Key Takeaway |

---

## 트리거 표현 (한국어)

| 요청 예시 | 활성화 |
|----------|------|
| "OSMU 콘텐츠 만들어줘" | ✅ |
| "이 글 SNS 채널별로 다시 써줘" | ✅ |
| "Instagram · Threads · X 동시 발행 글" | ✅ |
| "멀티채널 콘텐츠 재가공" | ✅ |
| "AEO 최적화 SNS 글 작성" | ✅ |
| "캐러셀·스레드·트윗 동시 생성" | ✅ |
| "블로그 글 SNS로 분해" | ✅ |

---

## 입력 두 가지

- **TYPE A** — 기존 `.md` 원본 (블로그 초안, 리서치 문서, 강의노트, 유튜브 스크립트 등)
- **TYPE B** — 한 줄 주제 (예: "AI 시대 검색 유입 감소와 브랜드 전략")
  → 스킬이 핵심 주제 · 타겟 · Pain Point · 메시지 · 키워드 · AEO 질문을 먼저 추론

---

## 3단계 워크플로우

```
STEP 1 ─ 콘텐츠 분석     핵심주제 · 타겟 · 목적 · Pain · 인사이트 · 키워드 · AEO 질문
STEP 2 ─ OSMU 유형 선택  교육형 / 체크리스트형 / 비교형 / 반박형 / 실패사례형 /
                          스토리형 / 실험형 / 트렌드형 / 프레임워크형
STEP 3 ─ 채널별 작성     Instagram · Threads · X — 각각 별개 .md 파일
```

---

## 출력 규칙 핵심

1. 채널마다 **처음부터 다시 쓴다** (복붙 금지)
2. **publish-ready** — 복사해서 그대로 게시 가능
3. **SEO/AEO 반영** — 키워드, 검색형 질문, AI 인용 가능한 압축 문장
4. 사용자의 **원본 의도 유지** (새 주장 추가 금지)
5. 과장·허위 표현 금지

자세한 채널별 SPEC · 구조 · SEO/AEO 규칙은 [`SKILL.md`](SKILL.md) 참조.

---

## 설치

이 리포 자체에는 dual-editor 레이아웃으로 두 경로에 동일 스킬이 들어 있습니다:

| 도구 | 경로 |
|------|------|
| Claude Code | `.claude/skills/contents-creator/` |
| Antigravity | `.gemini/antigravity/skills/contents-creator/` |

리포를 에디터로 열면 자동 인식됩니다. **별도 설치 필요 없음.**

다른 프로젝트에 전역 설치하려면:

```bash
# Claude Code (Mac/Linux)
cp -r .claude/skills/contents-creator ~/.claude/skills/contents-creator

# Antigravity (Mac/Linux)
cp -r .gemini/antigravity/skills/contents-creator ~/.gemini/antigravity/skills/contents-creator
```

```powershell
# Claude Code (Windows)
xcopy /E /I .claude\skills\contents-creator "%USERPROFILE%\.claude\skills\contents-creator"

# Antigravity (Windows)
xcopy /E /I .gemini\antigravity\skills\contents-creator "%USERPROFILE%\.gemini\antigravity\skills\contents-creator"
```

---

## 연관 스킬 — 흐름 예시

```
contents-creator   → instagram_post.md · threads_post.md · x_post.md 생성
       ↓
buffer-publish     → 각 파일을 채널별 Buffer 큐에 예약/발행
```

`buffer-publish` 스킬이 Threads · Instagram · LinkedIn 채널에 실제 발행을 담당합니다.
이 스킬은 **콘텐츠 생성**까지만 책임집니다.
