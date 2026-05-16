# 이미지 발행 전 Pre-flight 검증

Buffer로 Instagram·Threads에 이미지 발행 전에 다음 4가지를 점검한다.
SPEC 통과면 그대로 발행, 위반이면 사용자에게 보고 후 결정 받기.

이 검증은 특히 **학생이 본인 사진을 Drive에 직접 업로드한 경우**에 가치가 크다.
Gemini로 SPEC에 맞춰 생성한 이미지는 4가지 모두 통과해 추가 시간 없이 그대로 발행.

## 4가지 체크 기준

| 항목 | 통과 기준 | 위반 시 결과 |
|------|---------|-----------|
| 파일 크기 | ≤ 8MB | Buffer가 발행 거부 |
| 비율 | 0.8 ~ 1.91 사이 (Instagram 허용 범위) | Instagram이 자동 크롭 — 의도 안 한 잘림 |
| 해상도 (긴 변) | ≥ 1080px | Instagram 다운스케일 영역 아님 — 화질 저하 |
| 포맷 | JPEG, PNG | 그 외 거부 |

> **해상도는 긴 변 기준.** 가로 1600×900(16:9)이나 세로 900×1600(9:16) 모두
> `max(w, h) >= 1080` 이면 통과. `w` 와 `h` 를 각각 1080 이상으로 요구하면
> 정상 16:9·9:16 이미지가 잘못 "부족"으로 분류된다.

## 검증 코드 (Python + Pillow)

```python
import httpx
from PIL import Image
from io import BytesIO

def preflight(image_url: str) -> dict:
    """이미지 URL을 받아 4가지 SPEC 검증 결과 반환."""
    r = httpx.get(image_url, follow_redirects=True, timeout=15)
    img = Image.open(BytesIO(r.content))
    w, h = img.size
    size_bytes = len(r.content)
    ratio = w / h
    long_side = max(w, h)

    issues = []
    if size_bytes > 8 * 1024 * 1024:
        issues.append(f"파일 {size_bytes/1024/1024:.1f}MB > 8MB 한도")
    if not (0.8 <= ratio <= 1.91):
        issues.append(f"비율 {ratio:.2f} 위반 (Instagram 허용 0.8~1.91)")
    if long_side < 1080:
        issues.append(f"해상도 {w}×{h} 부족 (긴 변 < 1080)")
    if img.format not in ("JPEG", "PNG"):
        issues.append(f"포맷 {img.format} 비지원")

    return {
        "width": w, "height": h, "ratio": ratio,
        "size_mb": size_bytes / 1024 / 1024,
        "format": img.format,
        "issues": issues,
    }
```

## 위반 시 — 3선택지로 사용자 결정 받기

```
이미지 검증 위반:
  - 파일 7.8MB > 8MB 한도

어떻게 할까요?
  [1] 그대로 진행 — Buffer가 거부할 가능성 큼
  [2] 재업로드 — 보정 후 새 URL 제공 (1080×1350 4:5 권장)
  [3] 취소
```

자동 보정(Pillow로 강제 크롭 + Drive 자동 재업로드)은 학생 사진을 임의로 자르는 위험 +
OAuth 흐름 부담이 있어 기본 동작에 넣지 않는다 — **학생이 결과를 보고 직접 결정**하는 게 안전.

## 호출 위치

`buffer-publish` 발행 코드의 `createPost` 호출 직전에 끼운다:

```python
check = preflight(image_url)
print(f"검증: {check['width']}×{check['height']}, "
      f"{check['size_mb']:.2f}MB, ratio {check['ratio']:.2f}, {check['format']}")

if check["issues"]:
    print("⚠️ 위반:")
    for i in check["issues"]:
        print(f"  - {i}")
    # → 사용자에게 3선택지 보고 후 결정
else:
    print("✓ SPEC 통과 — 발행 진행")
```

## 실측 예시

| 입력 | 결과 |
|------|------|
| Gemini 산출물 (1080×1350, 4:5, 1.4MB, PNG) | ✓ 4가지 모두 통과 → 그대로 발행 |
| 휴대폰 가공 사진 (1600×900, 16:9, 0.25MB, JPEG) | ✓ 통과 (단 그리드 1:1 썸네일에서 좌우 크롭) |
| 휴대폰 원본 (4032×3024, 4:3, 8MB+) | ⚠️ 파일 크기 위반 → 1080×1350 리사이즈 권장 |
| 세로 사진 (1080×1920, 0.56) | ⚠️ 비율 위반 → 4:5로 크롭 권장 |
| 작은 이미지 (800×600, 0.5MB) | ⚠️ 해상도 부족 → 더 큰 원본으로 재업로드 |
