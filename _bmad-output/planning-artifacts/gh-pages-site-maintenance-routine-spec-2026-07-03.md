# gh-pages Site Self-Maintenance Routine — Full Spec (for next-session bmad-quick-dev)

**Status:** ready-for-planning · **Authored:** 2026-07-03 · **Author:** research lane (Claude)
**Intended workflow:** `bmad-quick-dev` with sprint-governance gates (party greenlight → dev → `bmad-code-review`), Marcus-first.
**Trigger arc:** GitHub Pages legacy build fast-fail on `jlenrique/jlenrique.github.io` (2026-07-03). Root cause = published `assets/` at **847.5 MB**, brushing the **1 GB hard cap**; legacy build pre-flight fast-failed (~2 s) leaving the last good build frozen. Manual two-pass prune took the site to **456.1 MB** and eliminated the fast-fail. This routine makes that hygiene **automatic and fail-loud** so the site never silently re-approaches the cap.

---

## 1. Problem statement

The public asset-host repo `jlenrique/jlenrique.github.io` is a **transient staging surface** with two live uses:
1. **Storyboard-review publication** (`assets/storyboards/<uuid>[-b|-chooser]/`, `assets/styleguide-picker/<run_tag>/`).
2. **Gamma literal-slide support** — Gary stages PNGs under `assets/gamma/...` and passes their public URLs into Gamma API packets.

Every publish **accumulates** a new subdir (~9 MB: one `index.html` + several 0.6–2 MB PNGs). **Nothing is ever pruned.** Consequences already observed:
- Published site grew to **847.5 MB** → hit the GitHub Pages **1 GB published-site hard cap** → legacy build **fast-fails in ~2 s** with generic "Page build failed", **old build keeps serving**, new paths 404. (Cited: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- The failure is **silent to the publisher**: the bot's `git push` succeeds, so the publish routine reports success while the site is actually frozen/broken. (The fine-grained `GITHUB_PAGES_TOKEN` can push + read Pages builds, but is `403` on `POST /pages/builds`.)

**Operator policy (2026-07-03):** *"Nothing older than 10 days need ever sit in Git publish URLs unless we make a special exception."*

## 2. Goals / non-goals

**Goals**
- G1 — **Retention prune on every publish:** delete managed packs older than `retention_days` (default **10**), honoring a protected allowlist.
- G2 — **Pre-push size guard:** fail loud *before* pushing if the projected published size exceeds a threshold, so we never push a build that will hit the cap.
- G3 — **Verify-build-after-publish, fail-loud:** after push, confirm the Pages build reaches `built`; on `errored`/timeout raise with the real `error.message`. Never report a silent success again.
- G4 — **Consolidate the duplicated publish helper** into one shared module so G1–G3 are implemented once, not 4×.
- G5 — **Standalone prune script** for manual/scheduled runs decoupled from a publish.

**Non-goals (this arc)**
- Migrating Pages from `build_type: legacy` to `build_type: workflow` (GitHub Actions). Recommended as a *separate* follow-on — it would also bypass the legacy build and surface real logs — but it is out of scope here. File in deferred-inventory.
- Image downsizing/transcoding at publish time (WebP/quality caps). Worthwhile growth-slowing follow-on; out of scope here.
- Git *history* rewrite to shrink the repo `.git`. Retention prune only affects the **published tree** (which is what the 1 GB cap measures); history-shrink is a separate, riskier op — deferred.

## 3. Current-state findings (code)

The gh-pages clone→copy→commit→push logic is **duplicated**:
- `app/marcus/orchestrator/picker_publisher.py::_git_publish_dir` (read in full — canonical shape; token injected as `https://x-access-token:{token}@…`, commits as `app-marcus-bot`, scrubs token from errors).
- `app/marcus/orchestrator/chooser_publisher.py::_git_publish_dir` (explicit twin per picker docstring).
- `app/marcus/orchestrator/storyboard_publisher.py` (storyboard packs).
- `skills/gamma-api-mastery/scripts/gamma_operations.py` (Gamma PNG git-site staging).

Config already lives in `state/config/storyboard-publisher.yaml` (Winston MUST-FIX: env-specific publish targets in `state/config`, not app code): `site_repo_url`, `site_branch`, `publish_subdir`, `token_env_var: GITHUB_PAGES_TOKEN`.

Managed roots and pack shapes on the live site (2026-07-03):
- `assets/storyboards/<uuid>`, `<uuid>-b`, `<uuid>-chooser`, plus named `C1-M1-PRES-*`, `storyboard-b-*`, `SB-A-TRIAL-001`, `reviews/<date>`.
- `assets/styleguide-picker/<run_tag>`.
- `assets/gamma/<dated-run>` (e.g. `apc-c1m1-tejal-20260419b-motion`) — transient; PLUS `assets/gamma/shared`, `assets/gamma/courses` (shared infra — **protected**).
- `assets/kling-validation/*`, `assets/video-style-picker/*` (validation / legacy — treat per allowlist).

## 4. Design

### 4.1 Shared module (G4)
Create `app/marcus/orchestrator/gh_pages_publish.py` exposing:
- `git_publish_dir(local_dir, *, site_repo, subdir, token, retention=..., verify=...) -> PublishResult` — the consolidated clone/copy/commit/push, with retention (G1) + size guard (G2) + verify (G3) woven in. The four existing call sites become thin wrappers delegating here (strangler-fig; keep each module's public function name/signature stable so callers/tests don't churn).
- Token-scrubbing (`_scrub_token`) and `_git` moved here (currently duplicated).

### 4.2 Retention prune (G1)
On each publish, after clone + before commit:
```
for root in managed_roots:              # from config
  for pack in immediate children of root:
    if pack in protected_paths: continue
    age_days = today - last_commit_date(pack)      # git log -1 --format=%cs -- pack
    if age_days > retention_days:  git rm -r pack
```
- **Age source = last-commit date of the pack path** (authoritative "when published"), not dir mtime (checkout-time) and not the UUID.
- Deletions are committed **together with** the new pack in the same publish commit (one push).
- Requires a **full clone** (current code uses `--depth 1`, which cannot compute per-pack dates). Change clone to full, or `--filter=blob:none` partial clone (blobless — enough for `git log` dates, avoids downloading old blobs). **Prefer blobless partial clone** for speed.

### 4.3 Pre-push size guard (G2)
Before push, sum blob sizes of the post-prune index (`git ls-tree -r -l` / `git cat-file --batch-check`):
- `> size_fail_mb` (default **900**) → raise `PublishError("published assets ≈{n} MB — over {size_fail_mb} MB guard; prune/migrate before publishing")` and **do not push**.
- `> size_warn_mb` (default **750**) → log a loud WARN but proceed.

### 4.4 Verify-build-after-publish (G3)
After push, poll `GET /repos/{owner}/{repo}/pages/builds/latest` **using shipped `httpx`** (per "verify via shipped deps, not operator CLIs" — no `curl`):
- Poll until `status not in {building, queued}` or a `verify_timeout_s` (default **600**, matching the legacy 10-min deploy cap) elapses.
- `built` → success (record build id + duration in the receipt).
- `errored` → raise `PublishError` including `error.message`.
- timeout → raise `PublishError("Pages build did not complete within {t}s")`.
- **Graceful degrade:** if the token lacks Pages:read (`403`/`404`), do NOT hard-fail the publish on verify alone — emit a loud WARN "could not verify build (token lacks Pages:read)"; the G2 size guard remains the primary preventive. (Confirmed 2026-07-03 the current token *does* have Pages:read → HTTP 200.)

### 4.5 Standalone prune script (G5)
`scripts/utilities/prune_gh_pages_site.py [--retention-days 10] [--dry-run] [--yes]`
- Reuses §4.2 logic against a fresh clone; `--dry-run` prints the deletion set + reclaim MB (default), `--yes` commits+pushes. Suitable for cron / manual cleanup independent of a publish.

### 4.6 Config additions — `state/config/storyboard-publisher.yaml`
```yaml
retention_days: 10
size_warn_mb: 750
size_fail_mb: 900
verify_build: true
verify_timeout_s: 600
managed_roots:
  - assets/storyboards
  - assets/styleguide-picker
  - assets/gamma
  - assets/kling-validation
protected_paths:          # never auto-deleted regardless of age
  - assets/gamma/shared
  - assets/gamma/courses
  - assets/video-style-picker/index.html
  - assets/video-style-picker/catalog.json
```
`protected_paths` also serves as the "special exception" mechanism the operator reserved.

## 5. Acceptance criteria (dev-agent verifiable via shipped deps + temp bare repo)

- **AC1 (retention deletes):** given a temp origin with packs dated >`retention_days` and <`retention_days`, a publish deletes only the old, non-allowlisted packs; recent + allowlisted packs survive. (Extends the existing temp-bare-repo pattern in `tests/marcus/orchestrator/test_picker_publisher.py`.)
- **AC2 (allowlist honored):** an old pack whose path matches `protected_paths` is NOT deleted.
- **AC3 (size guard fail-loud):** with `size_fail_mb` set below the fixture's projected size, publish raises `PublishError` and performs **no push** (origin unchanged).
- **AC4 (size guard pass):** under threshold, publish proceeds normally.
- **AC5 (verify built):** with a stubbed Pages-builds HTTP response returning `built`, publish records success; returning `errored` raises `PublishError` carrying `error.message`; a never-completing response hits `verify_timeout_s` and raises. (Stub `httpx` transport — no live API in dev-agent ACs.)
- **AC6 (verify degrade):** a `403` from the builds endpoint yields a WARN, not a publish failure.
- **AC7 (consolidation):** all four call sites route through `gh_pages_publish.git_publish_dir`; their public signatures/receipts are unchanged; existing publisher tests still pass.
- **AC8 (standalone script):** `prune_gh_pages_site.py --dry-run` against a temp origin prints the correct deletion set + reclaim total and pushes nothing.
- **AC-O1 (operator-gated, evidence in Completion Notes):** one real publish against the live site shows retention prune in the commit, a `built` verify, and a receipt with the build id. (Live-CLI evidence pasted once; not a dev-agent AC.)

## 6. Governance / gates
- **Party greenlight before dev** (sprint-governance §2): Winston (architect — shared-module extraction + partial-clone choice), Amelia (dev), Murat (test — stubbed httpx + temp-repo ACs). Marcus routes.
- **`bmad-code-review` before done** (§3).
- **Pipeline lockstep:** none of these paths are in `pipeline-manifest.yaml::block_mode_trigger_paths` (publishers are orchestrator-side, not the v4.2 pack/generator/L1 set) — confirm at T1, but expect no block-mode hook.
- **SPOC-is-the-goal check:** this is a genuine production-codebase improvement — the publishers are live SPOC-runtime review surface; unbounded growth silently breaks the client-facing review loop. It earns its place independent of any proofing run. ✅

## 7. Risks / mitigations
- **Wrong-age deletion** → age from last-commit date + allowlist + `--dry-run` default on the standalone script.
- **Deleting an in-flight/active pack** (published <10 d) → retention only targets >`retention_days`; the current run's own pack is brand-new.
- **Full/partial clone cost** → blobless partial clone keeps it cheap while enabling `git log` dates.
- **Token lacks Pages:read** → verify degrades to WARN; size guard is the primary preventive.
- **Legacy 10-min deploy timeout on a still-large site** → size guard threshold (900 MB) keeps builds well clear; if timeouts persist, escalate the Actions-migration follow-on.

## 8. Deferred-inventory entries to file
1. `gh-pages-actions-migration` — migrate `build_type: legacy → workflow` (bypasses legacy build, real logs, no 10-builds/hr limit). Direction may flip if legacy proves adequate post-routine.
2. `gh-pages-image-downsize` — WebP/quality caps in the publish path to slow growth.
3. `gh-pages-history-shrink` — optional `.git` shrink (BFG/filter-repo) if repo size (not published size) becomes a problem. Risky; operator-gated.

## 9. Files touched (estimate)
- NEW `app/marcus/orchestrator/gh_pages_publish.py`
- EDIT `app/marcus/orchestrator/{picker,chooser,storyboard}_publisher.py` (delegate to shared helper)
- EDIT `skills/gamma-api-mastery/scripts/gamma_operations.py` (delegate for Gamma PNG staging)
- EDIT `state/config/storyboard-publisher.yaml` (config block §4.6)
- NEW `scripts/utilities/prune_gh_pages_site.py`
- EDIT/NEW tests under `tests/marcus/orchestrator/` (+ integration test for the shared helper)
