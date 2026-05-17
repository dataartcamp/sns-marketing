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

## 4. API 요청 다층 rate limit (무료 플랜)

**증상:** 429 Too Many Requests

**원인:** API key 단위로 **3개 윈도우가 동시 적용**된다. 가장 빨리 차는 윈도우가 병목이다 — 단순 "100건/일" 한도가 아니다.

| 윈도우 | 한도 |
|--------|-----:|
| 15분 | 100 |
| 1일 | 100 |
| 30일 | 3,000 |

흔한 오해 두 가지:
1. "100건/일"만 신경 쓰다가 **15분 burst 한도**에 걸린다 — 디버깅 중 짧은 시간에 여러 번 호출 시 흔함
2. `x-ratelimit-remaining` 헤더만 보다가 안심한다 — 그 헤더는 **30일 윈도우 잔량만** 보여줘 misleading

### 정확한 측정 — 표준 `ratelimit` 헤더 사용

Buffer는 IETF RFC 9239 표준 `ratelimit` 헤더로 3개 윈도우 모두 노출한다. **이 헤더가 진짜다.**

```
ratelimit: "100-in-15min"; r=97; t=832,
           "100-in-1day";  r=82; t=12277,
           "3000-in-30days"; r=2982; t=2517878
```

- `r=` 잔량
- `t=` 리셋까지 남은 초

```python
import re

def parse_buffer_limits(resp):
    """Buffer의 다층 rate limit을 dict로 파싱."""
    h = resp.headers.get("ratelimit", "")
    out = {}
    for part in re.split(r',\s*(?=")', h):
        m = re.match(r'"([^"]+)";\s*r=(\d+);\s*t=(\d+)', part.strip())
        if m:
            out[m.group(1)] = {
                "remaining": int(m.group(2)),
                "reset_in_seconds": int(m.group(3)),
            }
    return out

# 사용
limits = parse_buffer_limits(resp)
print(limits["100-in-1day"])
# → {"remaining": 82, "reset_in_seconds": 12277}

# 가장 빠듯한 윈도우
tightest = min(limits.items(), key=lambda kv: kv[1]["remaining"])
print(f"가장 빠듯: {tightest[0]} — {tightest[1]['remaining']} 남음")
```

429 응답에는 `Retry-After` 헤더도 같이 옴 — 그대로 sleep하면 된다.

### 예방책

- **채널 ID 캐싱** — `account` + `channels` 쿼리는 1회만, 결과를 파일/DB에 저장
- **15분 burst 주의** — 짧은 시간 안에 발행 시도 여러 번 하지 말 것 (디버깅 중 흔한 함정)
- **테스트·eval 시 `saveToDraft=True`** — 실제 발행은 안 되지만 요청은 카운트되므로 호출 수는 사전에 계산
- **여러 에이전트가 같은 API key 공유 금지** — 한도가 합산되어 빠르게 소진

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

**증상:** Google Drive 공유 링크 또는 `uc?export=download` URL로 Instagram 이미지 발행 시 `Failed to fetch image dimensions: Not Found` 오류

**원인:** `drive.google.com/...` 패턴은 302 redirect 체인을 거쳐 결국 `lh3.googleusercontent.com`으로 가는 구조. 브라우저·`httpx`는 자동으로 redirect를 따라가지만 Buffer의 image fetcher는 redirect에 보수적이라 첫 redirect 응답에서 멈춰 이미지 파일로 인식하지 못한다.

```python
# ❌ 공유 링크 원본 — HTML 페이지로 인식
"https://drive.google.com/file/d/FILE_ID/view"

# △ uc 다운로드 — 일반 fetcher는 OK, Buffer는 redirect 미지원으로 실패 사례 있음
"https://drive.google.com/uc?export=download&id=FILE_ID"

# ✅ 검증된 안정 패턴 — redirect 없이 PNG 직접 응답
"https://lh3.googleusercontent.com/d/FILE_ID"
```

> 파일 ID 기반 `lh3.googleusercontent.com/d/<FILE_ID>` 형태는 안정적이다.
> 만료 위험이 있는 건 Google Photos preview에서 자동 발급되는 일회성 토큰 URL(`lh3.googleusercontent.com/A_...` 같은 알파벳·하이픈 토큰)이며, 형태가 다르다.

URL에 확장자가 없는 경우(lh3 URL이 그렇다): 확장자 기반 검증을 통과 못 할 수 있음
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

---

## 10. 이미지 8MB 한도 초과 — 휴대폰 원본 사진의 가장 흔한 함정

**증상:** 휴대폰에서 찍은 원본 사진을 Drive에 그대로 올려 발행 시도 → Buffer가 거부하거나 발행 단계에서 실패

**원인:** Buffer는 이미지에 **8MB 한도**를 적용한다. 휴대폰 카메라의 12MP 원본 JPG는 보통 5~12MB 사이라 한도 초과가 흔하다. Instagram이 자동 다운스케일하는 영역이 아니라 Buffer 단계에서 막힌다.

```python
# ❌ 휴대폰 원본 그대로 — 8MB 초과 가능
"https://lh3.googleusercontent.com/d/<원본_FILE_ID>"  # 8~12MB

# ✅ 업로드 전 Pillow로 1080×1350 4:5 + JPG 85% quality로 압축
from PIL import Image, ImageOps
img = Image.open("phone_original.jpg")
img = ImageOps.fit(img, (1080, 1350), method=Image.LANCZOS, centering=(0.5, 0.4))
img.save("instagram_ready.jpg", "JPEG", quality=85, optimize=True)
# → 보통 200~500KB로 압축, 화질 거의 동일
```

**예방책:**
- 업로드 전에 1080×1350 (Instagram 4:5) 또는 1080×1080 (1:1)로 미리 리사이즈
- JPG quality 85% 정도면 화질 거의 안 떨어지면서 파일 크기 1MB 이하로 압축
- Gemini로 생성한 이미지는 출력이 1~2MB 수준이라 한도 안전
- `centering=(0.5, 0.4)` 옵션으로 약간 위쪽 기준 크롭 → 인물 사진의 머리 보존
