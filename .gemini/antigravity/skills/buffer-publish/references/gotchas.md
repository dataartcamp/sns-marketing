# Buffer API — 함정과 해결책

공식 문서에 없거나 실제 구현 중 발견한 문제들. 강의/실습 시 자주 막히는 포인트.

---

## 1. `assets: null` GraphQL 스키마 오류

**증상:** 미디어 없는 draft 저장 시 `GraphQL error: assets는 null일 수 없습니다`

**원인:** `assets` 필드의 타입이 `[AssetInput!]!` — 비어있어도 null 불가

```python
# ❌ 잘못된 방법
variables["input"]["assets"] = None  # GraphQL 오류 발생
variables["input"]["assets"] = {}    # 오류 발생

# ✅ 올바른 방법: 키 자체를 생략
if media_urls:
    variables["input"]["assets"] = build_assets(media_urls)
# media 없으면 assets 키 미포함
```

---

## 2. 채널 ID는 사전 조회 필수

**증상:** `channel not found` 또는 발행 실패

**원인:** Buffer API는 채널 ID가 필요하며 service 이름으로 직접 발행 불가

```python
# ❌ 잘못된 방법
variables["input"]["channelId"] = "threads"  # service 이름 불가

# ✅ 올바른 방법: account → channels 쿼리로 id 조회
# 조회 흐름: account.organizations[0].id → channels(organizationId) → channel.id
```

조회 비용: API 요청 2회 → **캐싱 필수** (채널 ID는 재연결 전까지 불변)

---

## 3. Instagram은 로컬 파일 업로드 불가

**증상:** 로컬 파일 경로 전달 시 발행 실패

**원인:** Buffer는 미디어를 직접 수신하지 않음 — **HTTPS 공개 URL**만 수락

```python
# ❌ 잘못된 방법
"assets": {"images": [{"url": "/Users/me/photo.jpg"}]}
"assets": {"images": [{"url": "file:///Users/me/photo.jpg"}]}

# ✅ 올바른 방법: 호스팅 서비스 이용
# Cloudinary, imgbb, GitHub raw, Google Drive 등
"assets": {"images": [{"url": "https://res.cloudinary.com/..."}]}
```

---

## 4. API 요청 100건/일 한도 (무료 플랜)

**증상:** 429 Too Many Requests, `Retry-After` 헤더에 남은 초 표시

**원인:** API key 단위로 하루 100회 제한. 자정(UTC)에 초기화.

```python
# Retry-After 헤더 파싱
resp = httpx.post(...)
if resp.status_code == 429:
    retry_after = int(resp.headers.get("retry-after", 3600))
    print(f"{retry_after // 3600}시간 {(retry_after % 3600) // 60}분 후 재시도 가능")

# 현재 한도 확인
remaining = resp.headers.get("x-ratelimit-remaining")  # 남은 횟수
reset_ts = resp.headers.get("x-ratelimit-reset")       # Unix timestamp
```

**예방책:**
- 채널 ID 캐싱 (조회 횟수 감소)
- eval/테스트 시 mock 사용 또는 요청 수 사전 계산
- 한 번에 많은 에이전트를 동시 실행하지 말 것

---

## 5. Threads 해시태그 위치와 Discovery 노출

**증상:** 해시태그를 붙였는데 Threads 주제 피드에 원하는 포스트가 노출되지 않음

**원인:** Threads는 해시태그가 포함된 **해당 포스트**를 주제 피드에 노출
캐스케이딩 스레드에서 마지막 포스트에 붙이면 CTA 포스트만 주제 피드에 노출됨

```python
# ❌ 마지막에 붙이면: CTA 포스트가 주제 피드에 노출 → 클릭 유인 약함
thread_posts[-1] += "\n\n#AI자소서"

# ✅ 첫 번째에 붙이면: 훅 포스트가 주제 피드에 노출 → 클릭 유인 강함
thread_posts[0] += "\n\n#AI자소서"
```

---

## 6. Google Drive URL 패턴

**증상:** Google Drive 공유 링크로 Instagram Reels 발행 시 `영상 URL 필요` 오류

**원인:** 공유 링크 형식 `drive.google.com/file/d/ID/view`는 직접 다운로드 URL이 아님

```python
# ❌ 공유 링크 (Buffer가 파일로 인식 못 함)
"https://drive.google.com/file/d/128V3jUY.../view"

# ✅ 직접 다운로드 URL
"https://drive.google.com/uc?export=download&id=128V3jUY..."
```

URL에 확장자가 없는 경우: 확장자 기반 검증을 통과 못 할 수 있음
→ 검증 로직에서 알 수 없는 확장자는 허용하고 Buffer에 위임하는 것이 안전

```python
def is_video_url(url: str) -> bool:
    VIDEO_EXTS = {"mp4", "mov", "avi", "mkv", "webm"}
    IMAGE_EXTS = {"jpg", "jpeg", "png", "gif", "webp"}
    ext = url.rsplit(".", 1)[-1].split("?")[0].lower() if "." in url.split("/")[-1] else ""
    if ext in VIDEO_EXTS: return True
    if ext in IMAGE_EXTS: return False
    return True  # 확장자 불명 → Buffer에게 위임
```

---

## 7. `schedulingType` vs `mode` 관계

**증상:** 예약이 의도한 시각에 발행되지 않거나 즉시 발행됨

**원인:** `schedulingType`과 `mode`를 함께 올바르게 설정해야 함

```python
# 다음 큐 슬롯
{"schedulingType": "automatic", "mode": "shareNext"}

# 특정 시각 예약
{"schedulingType": "automatic", "mode": "customScheduled", "dueAt": "2026-05-14T00:00:00Z"}

# Draft (시각 무관)
{"schedulingType": "automatic", "mode": "shareNext", "saveToDraft": True}
```

`dueAt`은 반드시 **UTC ISO8601** (`Z` 또는 `+00:00` suffix). KST 그대로 전달 시 9시간 오차 발생.

```python
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
kst_dt = datetime(2026, 5, 14, 9, 0, 0, tzinfo=KST)
utc_str = kst_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
# → "2026-05-14T00:00:00Z"
```

---

## 8. Instagram 텍스트 only 발행 불가

**증상:** 미디어 없이 Instagram 발행 시 오류

**원인:** Instagram 정책상 텍스트 only 포스트 불가 (Buffer draft는 예외 — 미디어는 나중에 추가 가능)

```python
# Draft는 미디어 없이 저장 가능 → Buffer 웹 UI에서 미디어 추가 후 발행
if save_to_draft:
    pass  # 미디어 없어도 OK
else:
    assert media_urls, "Instagram 발행에는 미디어 URL이 필요합니다"
```

---

## 9. Union 타입 응답 처리 누락

**증상:** 발행 성공 응답에서 `KeyError: 'post'`

**원인:** createPost는 `PostActionSuccess | MutationError | RestProxyError` Union 반환
`__typename` 확인 없이 `data["createPost"]["post"]`에 직접 접근하면 오류

```python
# ❌ 잘못된 방법
post_id = resp.json()["data"]["createPost"]["post"]["id"]  # MutationError 시 KeyError

# ✅ typename 분기 처리
result = resp.json()["data"]["createPost"]
if result["__typename"] == "PostActionSuccess":
    post_id = result["post"]["id"]
elif result["__typename"] == "MutationError":
    raise Exception(result["message"])
elif result["__typename"] == "RestProxyError":
    raise Exception(f"채널 오류: {result['link']}")
```
