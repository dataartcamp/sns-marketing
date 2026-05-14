# 채널별 제약 & 전략

## Threads

| 항목 | 값 |
|------|-----|
| 포스트당 최대 글자 수 | 500자 |
| 캐스케이딩 최대 깊이 | 25개 포스트 |
| 해시태그 권장 수 | **1~2개** (많으면 알고리즘 불이익) |
| 미디어 | 선택 (텍스트 only 발행 가능) |
| 링크 미리보기 | 지원 |

### 캐스케이딩 전략
```python
# 첫 포스트 = text 필드
# 이후 포스트 = metadata.threads.thread 배열
{
    "text": "훅 문장 — 독자를 끌어당기는 첫 줄\n\n#AI자소서",  # ← 해시태그는 여기에
    "metadata": {
        "threads": {
            "type": "post",
            "thread": [
                {"text": "두 번째 포스트 — 본문 전개"},
                {"text": "세 번째 포스트 — CTA. 댓글로 알려주세요 👇"},
            ]
        }
    }
}
```

### 해시태그 위치
- **첫 번째 포스트**에 붙일 것: Threads 주제(Topic) 피드에 훅 문장이 노출됨
- 마지막 포스트에 붙이면: CTA만 주제 피드에 노출 → 클릭 유인 약함

---

## Instagram

| 항목 | 값 |
|------|-----|
| 캡션 최대 글자 수 | 2,200자 (알고리즘 유리 구간: 138~150자) |
| 해시태그 권장 수 | 3~10개 (30개까지 가능하나 효과 감소) |
| 미디어 | **필수** (텍스트 only 불가) |
| 미디어 형식 | HTTPS 공개 URL (로컬 파일 불가) |
| 캐러셀 | 이미지 여러 개 → `assets.images` 배열 |
| 릴스 | mp4/mov URL 필수, 세로형(9:16) 권장 |

### post_type 별 metadata
```python
# 피드 게시물
"metadata": {"instagram": {"type": "post", "shouldShareToFeed": True}}

# 릴스 (피드에도 표시)
"metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True}}

# 릴스 (릴스탭 전용)
"metadata": {"instagram": {"type": "reel", "shouldShareToFeed": False}}
```

### 해시태그 전략
```python
# 본문에 포함 (기본)
text = "캡션 내용\n\n#해시태그1 #해시태그2"

# 첫 번째 댓글에 분리 (유료 플랜 전용)
"metadata": {
    "instagram": {
        "type": "post",
        "firstComment": "#해시태그1 #해시태그2 #해시태그3"
    }
}
```

### 미디어 URL 준비
| 서비스 | 비용 | 용도 |
|--------|------|------|
| Cloudinary | 무료 25GB | 이미지/영상 변환·리사이즈 |
| imgbb | 무료 | 이미지 빠른 업로드 |
| GitHub raw | 무료 | 이미지 (공개 저장소만) |
| Google Drive | 무료 | `uc?export=download&id=` URL 패턴 |

---

## LinkedIn

| 항목 | 값 |
|------|-----|
| 포스트 최대 글자 수 | 3,000자 |
| 해시태그 권장 수 | 3~5개 |
| 미디어 | 선택 |
| 링크 미리보기 | 지원 |
| 캐스케이딩 | **미지원** (단일 포스트만) |

```python
# LinkedIn 단일 포스트
variables = {
    "input": {
        "channelId": LINKEDIN_CHANNEL_ID,
        "schedulingType": "automatic",
        "mode": "shareNext",
        "text": "본문 내용\n\n#LinkedIn #커리어",
        "saveToDraft": False,
        # LinkedIn은 metadata 생략 가능
    }
}
```

---

## 공통 — Buffer 무료 플랜 제약

| 항목 | 값 |
|------|-----|
| 채널 수 | 3개 |
| 채널당 예약 슬롯 | 10개 |
| API 요청 | **100건/일** (API key 단위) |
| 발행 횟수 | 무제한 |

### API 요청 절약 전략
```
채널 ID는 변경되지 않으므로 최초 1회 조회 후 파일/DB에 캐시.
30개 포스트 발행 시:
  캐시 없음: account(1) + channels(1) + createPost(30) = 32회  ← 권장
  캐시 없이 매번 조회: (account + channels) × 30 + createPost × 30 = 90회  ← 비추
```

```python
# 채널 ID 캐시 예시 (JSON 파일)
import json
from pathlib import Path

CACHE_FILE = Path(".buffer_channel_cache.json")

def get_channel_id(service: str, api_key: str) -> str:
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text())
        if service in cache:
            return cache[service]

    # 캐시 미스 → API 조회 후 저장
    org_id = fetch_org_id(api_key)
    channels = fetch_channels(org_id, api_key)
    cache = {ch["service"]: ch["id"] for ch in channels if not ch.get("isDisconnected")}
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    return cache[service]
```
