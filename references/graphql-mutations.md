# Buffer GraphQL API — Mutations & Queries

## 엔드포인트 & 인증

```
POST https://api.buffer.com
Authorization: Bearer <BUFFER_API_KEY>
Content-Type: application/json
```

모든 요청은 단일 엔드포인트로 전송. query/mutation 본문은 JSON body의 `query` 필드에 전달.

---

## Step 1 — account 쿼리 (organization ID 조회)

채널 목록 조회에 `organizationId`가 필요합니다.

```graphql
query Account {
  account {
    id
    email
    name
    timezone
    organizations {
      id
      name
    }
  }
}
```

```python
resp = httpx.post(
    "https://api.buffer.com",
    json={"query": "query Account { account { organizations { id name } } }"},
    headers={"Authorization": f"Bearer {API_KEY}"},
)
org_id = resp.json()["data"]["account"]["organizations"][0]["id"]
```

---

## Step 2 — channels 쿼리 (채널 ID 조회)

```graphql
query Channels($organizationId: OrganizationId!) {
  channels(input: { organizationId: $organizationId }) {
    id
    service        # "threads" | "instagram" | "instagram_business" | "linkedin"
    displayName
    isDisconnected
    isLocked
  }
}
```

```python
resp = httpx.post(
    "https://api.buffer.com",
    json={
        "query": "...",
        "variables": {"organizationId": org_id},
    },
    headers={"Authorization": f"Bearer {API_KEY}"},
)
channels = resp.json()["data"]["channels"]
threads_id = next(ch["id"] for ch in channels if ch["service"] == "threads")
```

`service` 값 참고:

| 채널 | service 값 |
|------|-----------|
| Threads | `threads` |
| Instagram | `instagram` 또는 `instagram_business` |
| LinkedIn 개인 | `linkedin` |
| LinkedIn 기업 | `linkedin_company` |

---

## Step 3 — createPost mutation

### 전체 input 구조

```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess {
      post {
        id
        status      # "draft" | "scheduled" | "sent"
        dueAt
        text
      }
    }
    ... on MutationError {
      message
    }
    ... on RestProxyError {
      link
    }
  }
}
```

### CreatePostInput 필드 참조

```python
input = {
    "channelId":      str,           # 필수 — channels 쿼리로 조회
    "schedulingType": "automatic",   # 항상 "automatic"
    "mode":           str,           # "shareNext" | "customScheduled"
    "text":           str,           # 포스트 본문
    "saveToDraft":    bool,          # True → draft 저장
    "dueAt":          str | None,    # UTC ISO8601, mode="customScheduled" 시 필수
    "metadata":       dict,          # 채널별 메타데이터 (아래 참조)
    "assets":         dict | None,   # 미디어 — 없을 때 키 자체를 생략 (null 불가)
    "source":         str,           # 출처 레이블 (임의 문자열, 선택)
}
```

### metadata — Threads

```python
# 단일 포스트
"metadata": {
    "threads": {
        "type": "post"
    }
}

# 캐스케이딩 스레드 (댓글 체인)
"metadata": {
    "threads": {
        "type": "post",
        "thread": [
            {"text": "두 번째 포스트"},
            {"text": "세 번째 포스트"},
        ]
    }
}
```

`text` 필드가 첫 번째 포스트, `metadata.threads.thread` 배열이 후속 포스트.

### metadata — Instagram

```python
# 피드 이미지
"metadata": {
    "instagram": {
        "type": "post",
        "shouldShareToFeed": True,
    }
}

# 릴스
"metadata": {
    "instagram": {
        "type": "reel",
        "shouldShareToFeed": True,   # False → 릴스탭 전용
    }
}

# 첫 번째 댓글 (유료 플랜 전용)
"metadata": {
    "instagram": {
        "type": "post",
        "firstComment": "#해시태그1 #해시태그2",
    }
}
```

### metadata — X.com (Twitter)

```python
# 단일 트윗
"metadata": {
    "twitter": {}      # 또는 metadata 자체 생략 가능
}

# 스레드 (캐스케이딩) — 2026-05-16 발행 검증됨
"metadata": {
    "twitter": {
        "thread": [
            {"text": "두 번째 트윗"},
            {"text": "세 번째 트윗"},
            # ... 최대 5~10개 권장
        ]
    }
}
```

Threads와 동일한 `thread` 배열 패턴이지만 **`type` 필드는 불필요.**
`text` 필드에 첫 트윗(Hook + 핵심 주장)이 들어가고,
`metadata.twitter.thread` 배열에 2번부터 마지막까지 순서대로 추가.

**서비스 식별자**: Buffer GraphQL에서 X 채널의 `service` 값은 X 리브랜딩 후에도
여전히 `"twitter"`로 유지된다. `channels` 쿼리 결과에서 그 값으로 필터.

**글자수 한도** (무료 계정):
- 각 트윗 **280 weight** (한국어 ≈ 140자, 영문 ≈ 280자)
- 영문·숫자·ASCII = 1 weight, CJK·이모지 = 2 weight, URL = 23 weight 고정
- **스레드 안의 각 포스트가 독립적으로 한도 적용** — 합산 아님

### assets — 미디어 첨부

```python
# 이미지 (단일 또는 캐러셀)
"assets": {
    "images": [
        {"url": "https://example.com/photo.jpg"},
        {"url": "https://example.com/photo2.jpg"},  # 캐러셀
    ]
}

# 영상
"assets": {
    "videos": [
        {"url": "https://example.com/video.mp4"}
    ]
}
```

⚠️ 미디어가 없을 때는 `assets` 키를 **완전히 생략**해야 합니다.
`"assets": null` 또는 `"assets": {}` 는 GraphQL 스키마 오류를 유발합니다.

---

## 완성된 요청 예시

### Threads 3포스트 캐스케이딩, 오늘 오후 9시(KST) 예약

```python
import httpx
from datetime import datetime, timezone, timedelta

API_KEY = "..."
CHANNEL_ID = "..."

# KST → UTC 변환
kst = datetime(2026, 5, 14, 21, 0, 0, tzinfo=timezone(timedelta(hours=9)))
due_utc = kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

variables = {
    "input": {
        "channelId": CHANNEL_ID,
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": due_utc,
        "text": "첫 번째 포스트 — 훅 문장\n\n#AI자소서",
        "saveToDraft": False,
        "metadata": {
            "threads": {
                "type": "post",
                "thread": [
                    {"text": "두 번째 포스트 — 본문 전개"},
                    {"text": "세 번째 포스트 — CTA"},
                ]
            }
        },
    }
}

resp = httpx.post(
    "https://api.buffer.com",
    json={"query": CREATE_POST_MUTATION, "variables": variables},
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=30,
)
data = resp.json()["data"]["createPost"]
if data["__typename"] == "PostActionSuccess":
    print(f"✓ post_id={data['post']['id']} status={data['post']['status']}")
```

### Instagram 피드, Draft 저장

```python
variables = {
    "input": {
        "channelId": INSTAGRAM_CHANNEL_ID,
        "schedulingType": "automatic",
        "mode": "shareNext",
        "text": "캡션 텍스트 #해시태그",
        "saveToDraft": True,
        "metadata": {
            "instagram": {"type": "post", "shouldShareToFeed": True}
        },
        "assets": {
            "images": [{"url": "https://example.com/image.jpg"}]
        },
    }
}
```
