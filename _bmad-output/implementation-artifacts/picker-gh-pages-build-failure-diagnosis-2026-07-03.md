# GitHub Pages build-failure diagnosis — picker live-proof blocker (2026-07-03, session 11)

Live-proof of the styleguide-picker gh-pages publish was BLOCKED: the real git push SUCCEEDS (files confirmed on `main` via GitHub API) but the **GitHub Pages BUILD errors** — new picker pages 404 while old paths still serve. Diagnosed via a web-research agent + a 3-seat BMAD debug party (Winston/Murat/Dr. Quinn) + a direct clone-and-measure of the public site.

## Root cause (cited, high-confidence)
The shared publish target `jlenrique.github.io` is **at/over GitHub Pages capacity ceilings**; the legacy build is refused at a **~2-second pre-flight check** (too fast to be content processing; `.nojekyll` present so Jekyll/Liquid is ruled out).
- **Published-site 1 GB hard cap:** measured **856 MB** of non-`.git` content (assets/storyboards 668M · video-style-picker 139M · gamma 17M · styleguide-picker 18M · root DALL·E PNGs ~9M), 991 files, **no symlinks, no files >50MB, no `:`/non-UTF8 filenames**. Under 1 GB but in the danger zone. (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- **Repository size limit:** every never-pruned PNG lives in `.git` FOREVER; full history far exceeds the 513 MB shallow `.git`. "Repository has exceeded size limits" is an enumerated legacy build-failure cause. (https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/troubleshooting-jekyll-build-errors-for-github-pages-sites)
- Both are the SAME underlying defect: **unbounded accumulation** — every publisher (storyboard, video-style-picker, picker) appends a new pack and nothing is ever pruned.
- **Definitive 60-sec confirmation (operator):** the "Page build failed" EMAIL GitHub sent the site owner's primary address names the reason verbatim. The REST `error.message` (GET /pages/builds/latest) was the generic "Page build failed."

## Signature ↔ cause fit (all facts explained by one cause)
2s fast-fail (pre-check refusal) · last good build 3 days ago (crossed a threshold since) · old build frozen-serving + new 404 (errored build never swaps in) · both pushes fail identically · `.nojekyll` present (Jekyll irrelevant).

## Critical reframe (Dr. Quinn)
**Storyboard A is NOT a healthy reference — it's a SURVIVOR** serving its old 06-30 artifact. Re-publishing it today would fail identically. The shared site is doomed for every publisher pointed at it. This is NOT a picker bug.

## Why the token couldn't force a rebuild
Fine-grained PAT lacks `Pages: write` (push uses `Contents: write`, which doesn't imply Pages access) → `POST /pages/builds` = 403. To force a rebuild: classic PAT w/ `repo`, or fine-grained w/ `Pages: write` + `Contents: read`.

## Fix plan
### Track 1 — publisher hardening (in-code, target-independent; dev RED-first this session)
1. **Verify-after-push + FAIL-LOUD** — after push, poll the Pages build to `built` (if the token can read the builds API) AND HEAD the NEW asset path for HTTP 200; on errored/timeout/404 RAISE `PickerPublishError`, NEVER return a dead URL. Would have caught this in 2s. Closes shadow SOP-205. Works with the current push-only token via the URL-200 poll fallback (Murat).
2. **Sanitize before commit** — reject/resolve symlinks (mode 120000) and filenames with `:` / non-UTF8 (cheap pre-flight killers).
### Track 2 — publish target (OPERATOR DECISION; blocked pending operator)
- **Recommended: dedicated picker repo/site** (fresh → builds instantly, unblocks live-proof, isolates from the doomed shared site, bounded by construction; new URL prefix; needs operator to create the repo or a repo-create-scoped token).
- Alt: migrate the shared site to GitHub Actions Pages deploy (`build_type: workflow`) — keeps the URL, visible logs, no PAT-to-build, tolerates symlinks, no 10-builds/hr limit — BUT still ~856MB and growing → must ALSO prune. (https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- Alt: prune the shared site now (deletes published content — client deliverables).
- **Replace-don't-accumulate** (`force_orphan` / Actions deploy) + **downsize thumbnails** (2MB→<150KB) land with whichever target so growth is bounded going forward.
### URGENT sibling flag
The shared site's capacity problem will break the NEXT storyboard/video-style-picker publish too. Storyboard A's publish path needs the same bounding/migration before its next real run.

## Status
Publish mechanism + page content + selection-code round-trip logic all PROVEN correct up to GitHub's build step (95 tests green, 4-lane review + patches, shadow Poll 4 concurrence). The ONLY blocker is the external Pages build (site capacity). Two liveproof subdirs left on the site (harmless, additive) pending cleanup.

---

## RESOLUTION — prune executed (2026-07-03, later same session)

Operator chose **Track 2 → prune the shared site** (not a new repo). Executed live against `jlenrique/jlenrique.github.io main` in two operator-approved passes, mirroring the publisher's own token/clone/commit/push path:

- **Root cause CONFIRMED by hard measurement:** published `assets/` measured **847.5 MB** at HEAD (the earlier 856 MB figure included root-level personal images outside `assets/`) — squarely in the 1 GB-cap danger zone, corroborating the capacity diagnosis. The prior `errored` builds fast-failed in ~2 s (pre-flight refusal).
- **Retention rule (operator-ratified 2026-07-03):** *nothing older than 10 days need sit in Git publish URLs unless a special exception is made.* Cutoff applied: 2026-06-23 (last-commit date per pack).
- **Pass A** (`ec08cb8`): 35 expired dated review/validation/Gamma-staging packs, 262 files → 847.5 → **642.5 MB**.
- **Pass B** (`0ffbe3c`): obsolete `video-style-picker/videos` (138.9 MB) + named `C1-M1-PRES-*` review decks, 98 files → **456.1 MB**. Kept `gamma/shared`+`gamma/courses` infra and the picker page shell.
- **Net: 847.5 → 456.1 MB (−391 MB / −46%).** All <10-day active surfaces preserved (today's picker liveproofs, `-chooser` surfaces, `concierge-part1-narrated-20260630`, recent storyboards). Reversible via git history.
- **Token note confirmed live:** the fine-grained `GITHUB_PAGES_TOKEN` **can** `GET /pages/builds/latest` (HTTP 200 → has Pages:read) but is `403` on `POST` — consistent with §"Why the token couldn't force a rebuild".

### UPDATE (2026-07-03 ~21:10Z) — prune reduced published size but did NOT cure the build
Build history (`GET /pages/builds`) shows the failure is **systematic, not size-alone**:
- Pre-prune (847 MB): errored (~96 s, then a 2 s fast-fail).
- Pass A `ec08cb8` (642 MB): **errored after ~9 min** ("Page build failed").
- Pass B `0ffbe3c` (456 MB): **stuck `building` for 73+ min** — never resolves (healthy builds on 2026-06-30 took 1.6–5.9 min; GitHub Pages is `operational`, no incident).
- Pattern: each prune got the build to run *longer* before failing (2 s → 9 min → hang), but never to `built`. Picker still 404s; live site still frozen at the last good build (2026-06-30).

**Revised root-cause weighting:** tree-pruning shrinks the *published tree* (847→456 MB) but does **NOT** shrink the **git history**, which still holds every PNG blob ever pushed (repo `.git` was already ~513 MB *shallow*; full history is far larger). The dominant residual blocker is therefore most likely **repository/history size** and/or **legacy-builder unreliability for this repo** — neither of which tree-pruning can address. The prune was still correct and necessary (published-tree headroom + operator's 10-day policy) but is **not sufficient** on its own.

Earlier recommendation was to migrate to GitHub Actions — see UPDATE-2, which supersedes this: the operator flipped to Actions and it STILL failed at the same stage, revealing the true cause.

### UPDATE-2 (2026-07-03 ~21:30Z) — REAL error obtained from the deploy log; SUPERSEDES the size/history hypotheses
The operator flipped Pages Source to **GitHub Actions** and shared the actual run (`actions/runs/28680891254`, the `pages build and deployment` deploy job). The REST `/pages/builds` "building/Page build failed" was **stale/misleading**; the real log shows:
- `actions/deploy-pages@v5`: artifact uploaded fine ("Found 1 artifact(s)", `artifact_id 8073978948`), deployment created for `0ffbe3c`, status `deployment_in_progress` → **`syncing_files`** → **`Error: Deployment failed, try again later.`** (failed in ~76 s, not a 73-min hang).

**Content is NOT the cause (measured on `0ffbe3c`):** **631 files / 43 storyboard packs / 464 MB**, largest blob 3.3 MB — comfortably within the 1 GB site cap, the 10 GB artifact cap, and any reasonable file-count. No symlinks / bad filenames. **So neither size, file count, nor git-history is the blocker** — the UPDATE-1 repo-history hypothesis and the original size-fast-fail weighting are **superseded**.

**True cause = known GitHub Pages BACKEND / config-state issue at `syncing_files`.** "Deployment failed, try again later" at `syncing_files` is a documented, largely platform-side failure (actions/deploy-pages [#406](https://github.com/actions/deploy-pages/issues/406) "Intermittent Deploy Failures", [#418](https://github.com/actions/deploy-pages/issues/418); community [#200823](https://github.com/orgs/community/discussions/200823)). Retrying for hours did not help affected users; **the fix that worked was TOGGLING the Pages Source setting** (Deploy-from-a-branch ⇄ GitHub Actions) to force GitHub to refresh apparently-corrupted Pages config state.

**Recommended operator action (in order):**
1. **Toggle Pages Source to force a config refresh:** Settings → Pages → Source → switch to **"Deploy from a branch"** (`main` / `/`), Save; then switch back to **"GitHub Actions"** (or leave on branch), Save. Then re-trigger a deploy (re-run the failed job, or push a trivial commit).
2. If still failing after a toggle + retry, **open a GitHub Support ticket** citing run `28680891254`, deployment ID `0ffbe3c`, repo `jlenrique/jlenrique.github.io`.

**What this means for our prior work:** the **prune (847→464 MB) was correct hygiene** (operator's 10-day policy + headroom) but was **not** the cause or the cure. The **maintenance routine** spec stands on its own merits (durable hygiene). The **Actions migration** is fine to keep but does NOT itself bypass `syncing_files`; its value here is that the *toggle* refreshes the broken config state.

### Follow-on: the fix is one-shot, not durable
Manual pruning restores headroom but the publishers still never prune → the site will re-approach 1 GB. The **standing maintenance routine** (retention-prune on publish + pre-push size guard + verify-build-after-publish fail-loud + consolidate the duplicated publish helper) is fully specced at [`gh-pages-site-maintenance-routine-spec-2026-07-03.md`](../planning-artifacts/gh-pages-site-maintenance-routine-spec-2026-07-03.md), queued for a next-session `bmad-quick-dev`. This supersedes Track-1's ad-hoc verify-after-push item by consolidating it into one shared helper. Deferred-inventory entries filed for the Actions migration, image-downsize, and history-shrink follow-ons.
