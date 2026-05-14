"""Buffer API 최소 동작 예제 — Threads 단일 포스트 발행.

실행 전:
    pip install -r requirements.txt
    cp .env.example .env  # BUFFER_API_KEY 입력

실행:
    python quickstart.py
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["BUFFER_API_KEY"]
API_URL = "https://api.buffer.com"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

CREATE_POST = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id status dueAt } }
    ... on MutationError     { message }
    ... on RestProxyError    { link }
  }
}
"""


def gql(query: str, variables: dict = None) -> dict:
    resp = httpx.post(API_URL, json={"query": query, "variables": variables or {}}, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", {})


# ── Step 1: organization ID 조회 ──────────────────────────────────────────────
data = gql("query { account { organizations { id name } } }")
org_id = data["account"]["organizations"][0]["id"]
print(f"organization: {org_id}")

# ── Step 2: Threads 채널 ID 조회 ──────────────────────────────────────────────
data = gql(
    "query Channels($organizationId: OrganizationId!) { channels(input:{organizationId:$organizationId}) { id service isDisconnected } }",
    {"organizationId": org_id},
)
channels = data["channels"]
threads_ch = next((c for c in channels if c["service"] == "threads" and not c["isDisconnected"]), None)
if not threads_ch:
    raise SystemExit("연결된 Threads 채널을 찾을 수 없습니다.")
print(f"threads channel_id: {threads_ch['id']}")

# ── Step 3: Draft 발행 (실제 게시 안 됨) ─────────────────────────────────────
variables = {
    "input": {
        "channelId": threads_ch["id"],
        "schedulingType": "automatic",
        "mode": "shareNext",
        "text": "Buffer API 테스트 포스트 🚀\n\n#버퍼테스트",
        "saveToDraft": True,  # ← Draft 저장 (실제 발행하려면 False)
        "metadata": {"threads": {"type": "post"}},
    }
}
result = gql(CREATE_POST, variables)["createPost"]

if result["__typename"] == "PostActionSuccess":
    post = result["post"]
    print(f"✓ 성공: id={post['id']} status={post['status']}")
elif result["__typename"] == "MutationError":
    print(f"✗ 오류: {result['message']}")
else:
    print(f"✗ 채널 오류: {result.get('link')}")
