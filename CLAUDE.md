# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **student lab kit** for the course "나만의 AI 마케팅 에이전트, 오늘 첫 출근" — not a runtime application. Its purpose is to ship agent skills that teach Claude Code / Antigravity the SNS marketing workflow:

- **`buffer-publish`** — publish to Threads/Instagram/LinkedIn via Buffer GraphQL API
- **`contents-creator`** — OSMU rewriter that turns one source into channel-specific `instagram_post.md` / `threads_post.md` / `x_post.md`

The two compose: `contents-creator` writes the posts, `buffer-publish` ships them. Students clone the repo, open it in either editor, and both skills auto-load.

User-facing language is **Korean**. Keep doc edits, error messages, and commit messages in Korean to match the course.

## Dual-editor layout (the most important thing)

Every skill is mirrored at two paths so both editors auto-discover it:

```
.claude/skills/<skill>/SKILL.md              ← Claude Code reads this
.gemini/antigravity/skills/<skill>/SKILL.md  ← Antigravity reads this
```

**Rule: when you edit one SKILL.md, mirror the change to the other.** Drifting the two copies is the main failure mode in this repo.

**Rule: write both files as UTF-8 *without* BOM.** Antigravity (and some other readers) can mis-parse YAML frontmatter or render a corrupted first character when a UTF-8 BOM (`EF BB BF`) precedes the file. Python's `path.write_text(s, encoding="utf-8")` writes BOM-less by default; the trap is GUI editors or `cp` operations from a BOM-prefixed source. To verify: open in binary mode and confirm the file does not start with `EF BB BF`.

### Where shared assets live

`buffer-publish` pulls from repo-root `references/` and `examples/` (kept at the root so `quickstart.py` is one-click for students). `contents-creator` is **self-contained** — only `SKILL.md` + `README.md` inside each skill folder, no external links — so its two copies can be byte-identical clones.

| Skill | references 위치 | Mirror strategy |
|-------|---------------|-----------------|
| `buffer-publish` — 채널·API SPEC | repo-root `references/*.md` | Content identical, **relative-path depth differs** (.claude `../../../`, .gemini `../../../../../`) |
| `buffer-publish` — 발행 검증 (`image-preflight.md`) | 스킬 안 `references/` | Byte-identical — 두 미러 모두 같은 `references/...` 상대경로 |
| `contents-creator` | (외부 references 없음) | Byte-identical (`cp` works) |

### `buffer-publish` relative-path quirk

The two SKILL.md copies sit at different depths, so their `../` prefixes to repo-root `references/` differ:

| File | Relative path to `references/` |
|------|--------------------------------|
| `.claude/skills/buffer-publish/SKILL.md` | `../../../references/` (3 levels up) |
| `.gemini/antigravity/skills/buffer-publish/SKILL.md` | `../../../../../references/` (5 levels up) |

When editing either file, keep content identical but adjust `../` depth. The `.claude/skills/buffer-publish/README.md` also describes a self-contained `buffer-publish/references/...` layout for downstream copy-install — that's a different shape from how this repo is organized, don't conflate them.

## Commands

There is no build / lint / test pipeline. The only executable is the smoke-test example:

```bash
cd examples
pip install -r requirements.txt
cp ../.env.example ../.env   # then edit BUFFER_API_KEY
python quickstart.py         # publishes a Threads draft (saveToDraft=True)
```

`quickstart.py` walks the full 3-step Buffer flow (`account` → `channels` → `createPost`) and is the canonical reference for new examples.

## Buffer API — non-obvious essentials

The skill files cover the API in depth. The traps most likely to bite when generating new code (all detailed in [references/gotchas.md](references/gotchas.md)):

- **`assets` must be omitted entirely** when there is no media. `null` and `{}` both produce GraphQL schema errors.
- **`channelId` must be pre-fetched** via `account.organizations[].id` → `channels(organizationId)`. Cache it; channel IDs don't change until reconnection.
- **`dueAt` is UTC ISO8601 with `Z` suffix.** KST inputs need explicit conversion or you get a 9-hour offset.
- **`createPost` returns a GraphQL Union** (`PostActionSuccess | MutationError | RestProxyError`). Always branch on `__typename` before reading `.post`.
- **Free plan = 100 API requests/day** per API key (UTC reset). On 429, read `Retry-After` and `x-ratelimit-*` headers. Cache the channel-ID lookup or you'll burn the quota in testing.
- **Instagram requires HTTPS public media URLs.** Local paths and Google Drive `/view` share links fail — use the `uc?export=download&id=` form for Drive.

## Editing the skill content

- The skill `description` (front-matter in SKILL.md) is what triggers auto-activation. The Korean trigger phrases listed there ("Buffer API", "Threads 발행 구현", "createPost", etc.) are intentional — preserve them when rewriting.
- `references/*.md` are the source of truth for API details. Both SKILL.md files should stay thin and delegate to them rather than duplicating tables.
- `.env` is gitignored; `.env.example` is the template students copy. Don't add real keys to either.
