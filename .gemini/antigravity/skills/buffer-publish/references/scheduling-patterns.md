# 스케줄링 패턴

## 1. 단일 포스트 예약

```python
# KST → UTC 변환 후 dueAt 전달
from datetime import datetime, timezone, timedelta

kst = datetime(2026, 5, 14, 9, 0, 0, tzinfo=timezone(timedelta(hours=9)))
due_utc = kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

variables["input"]["mode"] = "customScheduled"
variables["input"]["dueAt"] = due_utc  # "2026-05-14T00:00:00Z"
```

## 2. 멀티채널 예약 (같은 시각, 다른 채널)

채널마다 createPost를 한 번씩 호출합니다.

```python
channels = {
    "threads":   {"id": THREADS_ID,   "media": []},
    "instagram": {"id": INSTAGRAM_ID, "media": ["https://...image.jpg"]},
}

for service, cfg in channels.items():
    post_to_buffer(
        channel_id=cfg["id"],
        text=content[service]["text"],
        media_urls=cfg["media"],
        due_utc=due_utc,
    )
```

## 3. 배치 예약 (콘텐츠 여러 개 → 채널 슬롯 채우기)

```python
schedule = [
    {"text": "월요일 포스트", "due": "2026-05-13T00:00:00Z"},
    {"text": "수요일 포스트", "due": "2026-05-15T00:00:00Z"},
    {"text": "금요일 포스트", "due": "2026-05-17T00:00:00Z"},
]

for item in schedule:
    post_to_buffer(channel_id=THREADS_ID, text=item["text"], due_utc=item["due"])
    # 무료 플랜: 채널당 슬롯 10개 한도
```

## 슬롯 한도 계산

```
무료 플랜: 채널당 10개 슬롯
3채널 × 10개 = 30개 예약 가능
API 호출: 채널 ID 캐싱 시 30회 (createPost × 30)
```
