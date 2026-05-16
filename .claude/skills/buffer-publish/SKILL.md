---
name: buffer-publish
description: >
  Buffer API(GraphQL)를 사용해 Threads · Instagram · LinkedIn 등 SNS 채널에
  콘텐츠를 발행/예약/드래프트 저장하는 워크플로우 스킬.
  언어·프레임워크·프로젝트 구조에 무관하게 적용 가능한 일반화 버전.
  사용자가 다음을 언급할 때 이 스킬을 사용하세요:
  "Buffer API", "Buffer로 발행", "SNS 자동 발행", "Threads 발행 구현",
  "Instagram 예약 발행", "Buffer GraphQL", "createPost", "채널 연동 구현".
---

# buffer-publish

Buffer API로 SNS 채널에 콘텐츠를 발행하는 범용 워크플로우.

- GraphQL API 스키마 → `../../../references/graphql-mutations.md`
- 채널별 제약 → `../../../references/channel-constraints.md`
- 스케줄링 패턴 → `../../../references/scheduling-patterns.md`
- 주의사항(함정) → `../../../references/gotchas.md`

## 사전 준비

1. **Buffer 계정** 생성: [buffer.com](https://buffer.com)
2. **API 키** 발급: Buffer 대시보드 → Settings → API
3. **채널 연결**: Buffer 대시보드 → Channels → Connect a Channel
4. **채널 ID 조회**: `account` → `channels` 쿼리 순서로 선조회 필요 (아래 참조)

```
BUFFER_API_KEY=your_key_here
```

## 3단계 워크플로우

```
1. 채널 ID 조회    account 쿼리 → channels 쿼리 → channel.id 저장
2. 콘텐츠 변환    채널별 글자 수 · 해시태그 · 미디어 규칙 적용
3. 발행           createPost mutation → draft | scheduled | sent
```

## 빠른 시작 — Threads 단일 포스트 발행

```python
import httpx

API_KEY = "your_buffer_api_key"
CHANNEL_ID = "your_threads_channel_id"  # channels 쿼리로 사전 조회

def buffer_post(text: str, channel_id: str, *, draft: bool = False):
    query = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        __typename
        ... on PostActionSuccess {
          post { id status dueAt }
        }
        ... on MutationError { message }
      }
    }
    """
    variables = {
        "input": {
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "shareNext",
            "text": text,
            "saveToDraft": draft,
            "metadata": {"threads": {"type": "post"}},
        }
    }
    resp = httpx.post(
        "https://api.buffer.com",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
```

## 발행 모드

| 목적 | mode | 추가 필드 |
|------|------|-----------|
| 다음 큐 슬롯 | `shareNext` | — |
| 특정 시각 예약 | `customScheduled` | `dueAt: "2026-05-14T00:00:00Z"` |
| Draft 저장 | `shareNext` | `saveToDraft: true` |

`dueAt`은 **UTC ISO8601** 형식: `"2026-05-14T00:00:00Z"`

## 채널별 핵심 차이

| 채널 | metadata 키 | 필수 필드 | 미디어 |
|------|-------------|-----------|--------|
| Threads | `threads` | `type: "post"` | 선택 |
| Threads 캐스케이딩 | `threads` | `type: "post"` + `thread: [{text}]` | 선택 |
| Instagram 피드 | `instagram` | `type: "post"` | **필수** |
| Instagram 릴스 | `instagram` | `type: "reel"` | **mp4/mov 필수** |
| LinkedIn | `linkedin` | — | 선택 |

> 채널별 글자 수 한도·해시태그 전략 → `../../../references/channel-constraints.md`
> 실수하기 쉬운 함정 → `../../../references/gotchas.md`

## 응답 처리

Buffer createPost는 **GraphQL Union 타입**을 반환합니다:

```python
data = resp.json().get("data", {})
result = data.get("createPost", {})
typename = result.get("__typename")

if typename == "PostActionSuccess":
    post = result["post"]
    print(f"성공: id={post['id']} status={post['status']}")
elif typename == "MutationError":
    print(f"실패: {result['message']}")
elif typename == "RestProxyError":
    print(f"채널 오류: {result['link']}")
```

## 무료 플랜 한도

| 항목 | 무료 | 유료 |
|------|------|------|
| 채널 수 | 3개 | 무제한 |
| 채널당 예약 슬롯 | 10개 | 무제한 |
| API 요청 | **100건/일** | 더 높음 |

> API 요청 100건/일 한도 관리 전략 → `../../../references/gotchas.md`
