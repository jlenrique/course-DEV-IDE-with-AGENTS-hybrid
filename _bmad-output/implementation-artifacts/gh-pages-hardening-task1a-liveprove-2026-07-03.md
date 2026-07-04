# Task 1a — gh-pages hardening LIVE-PROVE evidence (RA8)

**Date:** 2026-07-03 (UTC ts 20260704T034640Z) · **Commit under test:** `6fc7960e` · **Remote:** `jlenrique/jlenrique.github.io`
**Raw evidence:** `_bmad-output/implementation-artifacts/evidence/gh-pages-hardening-liveproof-20260704T034640Z/liveprove-result.json`
**Verdict:** ✅ all four teeth proven live; both failure paths bite; real site left unchanged (Marcus C3 + C6 honored).

Design was SAFE-by-construction: retention proof was DRY-RUN (read-only); the size-guard teeth measured the real cloned tree with a low threshold and never pushed; the happy-path publish used a NON-managed scratch path with retention DISABLED (deleted zero client content) and was CLEANED UP; the verify teeth was a read-only GET of a 404.

## Results

| Teeth | Live result |
|---|---|
| **G1 retention** (dry-run on real data) | Would delete **15 packs (~62.8 MB)** older than 10 days by `%ct` committer date; kept **2 protected** (`assets/gamma/courses`, `assets/gamma/shared`); 0 current-run; 0 unknown-age. `assets/kling-validation` absent → benign no-op (RA7c confirmed live). **Nothing deleted.** |
| **G2 size-guard teeth** | `SizeGuardRefusal` **raised** on the real **473.6 MB** tree vs a 100 MB fail threshold — **no push** ("refusing to push a build that would breach the GitHub Pages 1 GB cap"). Fail-loud proven on the real site. |
| **transport + G3 verify (happy path)** | Scratch pack published to `assets/hardening-liveproof/20260704T034640Z` → **verified live HTTP 200** → scratch **cleaned up** (site net-zero). Full clone→prune-skip→copy→size-check→commit→push→verify chain exercised end-to-end against the real remote. |
| **G3 verify teeth (dead URL)** | Pointed verify at a guaranteed-404 path → **raised `GhPagesPublishError` `tag=gh-pages.publish.not-live`**. The verify gate bites live — a `git push` succeeding does not fool it. |

## Operational finding (for the operator)
The live published-site tree is **473.6 MB and accumulating** (up from the ~456 MB post-manual-prune baseline). Retention would reclaim **62.8 MB** by removing 15 storyboard packs older than 10 days (all `assets/storyboards/<uuid>[-b|-chooser]`). Not auto-executed — a real deletion of client-facing URLs is left to operator invocation via `python scripts/utilities/prune_gh_pages_site.py --yes` (the >10-day operator policy sanctions it; surfacing it rather than silently mutating live content per Marcus C6).

## Gate status
Task 1a: greenlit (4/4) → built → 3-lane adversarial code-review (0 MUST-FIX; all SHOULD-FIX folded) → **live-proven (this doc)** → committed + pushed (`6fc7960e`). CLOSED.
Remaining in the arc: Task 1b (gamma + legacy-storyboard primitive adoption), then goal Tasks 2 (Actions deploy) / 3 (picker #4) / 4 (prove hardened path).
