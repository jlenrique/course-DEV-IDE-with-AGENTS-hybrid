# Task 1b — CLOSE — bmad-code-review + RED-first fixes + LIVE PROOF

**Arc:** gh-pages publish-hardening + durable-deploy. **Date:** 2026-07-04 (~16:21Z).
**Checkpoint reviewed:** `e626a285` (gamma `publish_preintegration_literal_visuals` +
legacy-storyboard `cmd_publish` adopt the shared hygiene primitives around their own
`_git_auth_env` transport). **Class S. Sole Claude dev lane.** Codex shadow-monitor OFF
(ledger carried no unaddressed 1b findings; last session-12 poll reviewed).

## bmad-code-review (3 adversarial layers, Opus tier)
Blind Hunter + Edge Case Hunter + Acceptance Auditor, run in parallel on the exact
`e626a285` production diff. Acceptance verdict: the diff FAITHFULLY implements Task 1b
(both publishers run retention→size-guard(fail-loud)→verify; >10-day+allowlist config-driven;
RA1/RA2 satisfied; whole-repo/staged commit-gate; additive contract). No Critical/High real
bug. Two Blind-Hunter "High" items were FALSE POSITIVES (diff-only blindness):
`substituted_cards[0]` is co-populated with `url_map` in the same loop; `token` is bound at
gamma line 299.

### Findings fixed RED-first (fresh general-purpose dev agent; Claude reviewed+live-proved)
1. **Staged-only commit gate** (both publishers) — replaced whole-repo `git status --porcelain`
   with `git diff --cached --name-only`; still catches retention `git rm` deletes + new-pack
   adds, ignores unstaged/untracked worktree noise (Windows autocrlf abort risk).
2. **Gamma size-guard placement** — moved `project_published_size` inside the staged-changes
   gate (a no-op re-publish on an over-budget repo no longer fails loud), matching storyboard.
3. **`prune_retention` ancestor identity-protection** (shared primitive) — protect the current
   pack OR any ancestor of it (`rel_norm == current_norm or current_norm.startswith(rel_norm+"/")`),
   closing a latent sibling-part data-loss trap on multi-segment `current_subdir`. + golden test.
4. **Gamma `_github_pages_base_url` host-conditioned fallback** — raise for malformed
   github.com/github.io URLs; keep the lenient fallback only for non-github/local (offline seam).
5. **Retention-disabled WARN** (both publishers) — loud log when `retention is None`
   (fail-loud-never-silent; observability of a silent hygiene downgrade).

Tests after fixes (each root separately, `-n 0`): gamma hygiene **10**, storyboard hygiene **8**,
shared-primitive **24** — all green. Ruff: 20 pre-existing errors, **0 introduced**. `git diff --check` clean.

### Accepted (not defects)
- Age-based retention can reap a still-referenced pack → 404: the operator-ratified 10-day
  policy + `protected_paths` allowlist; durable packs must be allowlisted. Conscious acceptance.
- Malformed config aborts (fail-loud correct). Gamma retention-only push skips verify
  (no new pack URL to poll). Site-wide cross-root pruning (by-design whole-site hygiene).

## LIVE PROOF — 4 teeth, real remote (~474 MB `jlenrique/jlenrique.github.io`), scratch paths only
Driven through the ACTUAL 1b transports. Threshold injected via `load_hygiene_config`
monkeypatch (a config choice, not a behavior mock); `retention=None` forced so NO real client
pack was pruned. Harness: `scratchpad/task1b_liveprove.py`. Result: `result.json` (all_pass=true).

- **A — gamma size-guard fail-loud** (`publish_preintegration_literal_visuals`, `fail_mb=1`):
  `SizeGuardRefusal` tag `gh-pages.publish.size-guard` ("≈474 MB over the 1 MB guard"); scratch
  path 404 on the remote → **no push**.
- **B — verify catches a not-live build** (`verify_build_after_push` vs a guaranteed-404 URL):
  `GhPagesPublishError` tag `gamma.publish.not-live` (HTTP 404 after ~15s polling).
- **C — gamma HAPPY round-trip** (real push, `retention=None`, generous verify): `pushed=True`,
  `verified_live=True`, `card.png` served **HTTP 200** via the durable Actions deploy
  (independent visitor check 200). Scratch pack then **removed** (delete commit `b4555069`);
  live URL went 200→**404** as the cleanup Actions deploy propagated — no scratch content left
  on the client site.
- **D — storyboard size-guard fail-loud** (full `cmd_publish`: export→blobless clone→guard,
  `fail_mb=1`): `SizeGuardRefusal` tag `gh-pages.publish.size-guard` ("≈475 MB over 1 MB guard")
  → **no push**. (Bonus: the FIX-5 retention-disabled WARN fired live in A/C/D.)

## Outcome
Task 1b CLOSED: review clean (0 surviving real defects), 5 findings fixed RED-first, all four
failure/happy teeth proven live through the real transports on the real remote, scratch content
cleaned up. Party concurrence is deferred to the Task 4 goal done-signal per arc convention.
