# gh-pages Publish-Hardening — Task 1 GREENLIGHT Party Record

**Date:** 2026-07-03 · **Gate:** greenlight (pre-dev) for Task 1 of the gh-pages publish-hardening + durable-deploy arc
**Spec:** `_bmad-output/planning-artifacts/gh-pages-site-maintenance-routine-spec-2026-07-03.md`
**Goal:** `_bmad-output/planning-artifacts/goal-gh-pages-publish-hardening-arc-2026-07-03.md`
**Verdict:** **CONSENSUS GO** (4/4 GO-WITH-AMENDMENTS; all amendments folded below)
**Team:** Marcus (orchestrator) · Winston (architect) · Amelia (dev) · Murat (test architect) — canonical core + arc specialists per sprint-governance §2.

---

## Verdicts (each voice, in brief)

- **Marcus — GO-WITH-AMENDMENTS (6 conditions).** Product-boundary CLEAN PASS: publishers are literal Marcus-SPOC client-facing review surfaces; the defect is SPOC handing a client a live-looking URL that 404s while `git push` reports success — SPOC lying to a client through its own runtime. **G3 verify-after-publish is priority-1** (detects the failure class regardless of cause); G2 second; G1 + shared-helper consolidation as the universal-coverage carrier. Retention must be justified by the client review loop, not concierge decluttering. **Live-prove the FAILURE paths (teeth-witness), on a scratch path, never endangering live client URLs.**
- **Winston — GO-WITH-AMENDMENTS (5 conditions).** **Option B**: transport ≠ hygiene. Consolidate transport for picker+chooser; extract three auth-agnostic hygiene primitives gamma+storyboard call around their own contracts. Blobless clone **with checkout**, full history; size accounting by **filesystem walk of the checked-out post-prune tree + staged adds**, never `cat-file`/`ls-tree -l` on blobs (promisor lazy-refetch trap). Size guard is fail-loud (raise + non-zero + no push). Chooser token-leak fix rides in-arc + forcing test.
- **Amelia — GO-WITH-AMENDMENTS (3 amendments).** AC7 "all four through one signature" is a trap; split gamma+storyboard to a fast-follow. Sequence **T1 move+test → T2 G1+G2 → T3 picker wrapper → T4 chooser wrapper (fixes token-leak+adds verify) → T5 standalone prune CLI → T6 G3 verify**. Pin retention to committer Unix epoch `%ct` vs UTC `time.time()`. Preserve gamma's `url_map` return + trace storyboard receipt consumers before touching them.
- **Murat — GO-WITH-AMENDMENTS (3 binding).** Date fixtures MUST set `GIT_COMMITTER_DATE`+`GIT_AUTHOR_DATE` in subprocess `env=` (`git commit --date=` sets only author date → `%cs`/`%ct` unchanged → retention theater), with a self-check reading the date back. Keep injectable `pages_build_checker`/`url_checker`/`sleep`/`clock` seams for orchestration tests; httpx-stub only ONE adapter-mapping test. **Highest-severity test: never delete the current-run pack (by identity, not date).** Boundary tests for `>` semantics; allowlist exact-match (no false-neighbor); receipt-golden for consolidation.

## Empirical spike (facilitator, before synthesis) — settles the two disagreements

Ran a git spike (git 2.49) against a temp bare origin with packs backdated via `GIT_COMMITTER_DATE`:

- **`%ct` epoch** gives correct per-pack ages (20d / 3d) cross-platform — adopt over `%cs` string.
- **Size metric (Winston vs Amelia):** after `git rm` of a 6MB pack + commit, working-tree `du` dropped 10.48MB→4.19MB but `git count-objects` **size-pack stayed 10.01 MiB** (deleted blob retained in history). → **`count-objects`/pack-size does NOT respond to retention prune → wrong metric.** Measure the **published working tree** (what the GitHub Pages 1GB *published-site* cap actually measures). **Winston's position ratified; Amelia's `count-objects -vH` rejected with evidence.**
- **Blobless dates:** `%ct` survives a blobless clone (dates are on commit objects, not blobs). The promisor-refetch trap is avoided because we `du` the checked-out tree (materialized HEAD blobs), never `cat-file` historical OIDs.

---

## RATIFIED AMENDMENTS (binding before dev opens)

- **RA1 — Scope / Option B (D1).** Task **1a** = picker+chooser route through shared `git_publish_dir` (transport) + three auth-agnostic hygiene primitives in `app/marcus/orchestrator/gh_pages_publish.py`: `prune_retention(clone_dir, *, managed_roots, max_age_days=10, protected_allowlist, now)`, `project_published_size(clone_dir, *, staged_adds, refuse_at_mb=900, warn_at_mb=750)`, `verify_build_after_push(site_slug, *, token, ...)`. Gamma (`publish_preintegration_literal_visuals`) + legacy-storyboard (`generate-storyboard.py::publish_snapshot_tree`) adopt the **primitives around their own transport/auth/copy contracts** as **Task 1b (in-arc fast-follow, NOT deferred-inventory)**. **AC7 rewritten** to this boundary; "all four through one signature" framing rejected.
- **RA2 — Clone + size metric (D2).** `git clone --filter=blob:none` **WITH checkout**, full history. Size = **filesystem walk of the checked-out post-prune working tree + freshly-stat'd staged adds**. NEVER `git count-objects`/pack-size; NEVER `cat-file`/`ls-tree -l` on blobs. (Empirically confirmed.) Add a Dev Note flagging the promisor lazy-fetch behavior so no one "optimizes" back into it.
- **RA3 — Date semantics.** Retention keys on committer date as **`%ct` epoch** compared to `time.time()` (UTC). No string/tz parsing. Fixtures set BOTH `GIT_COMMITTER_DATE`+`GIT_AUTHOR_DATE` in subprocess `env=` with a read-back self-check (test-the-harness).
- **RA4 — Chooser token-leak (D3).** Fixed in-arc by inheriting picker's scrub; blocking forcing-test asserts no `x-access-token:` substring in any raised message on a forced push failure.
- **RA5 — Size guard fail-loud.** Raises `SizeGuardRefusal` (non-zero, NO push) at 900MB; loud WARN at 750MB. No WARN-only path on the refuse threshold. Gamma covered via Task 1b + the standalone prune (RA-G5) gives interim site-wide protection regardless of caller.
- **RA6 — G3 seam + priority.** G3 is priority-1 (Marcus). Keep injectable callable seams for all orchestration/verify-behavior tests; httpx lives only inside the DEFAULT `pages_build_checker`; exactly ONE adapter-mapping test uses a stubbed `httpx.MockTransport`.
- **RA7 — Retention safety tests (blocking).** (a) NEVER delete the current-run pack — by identity, not date (highest severity). (b) Boundary: age == `retention_days` survives, `+1` deletes (`>` semantics). (c) Empty managed_root → clean no-op; absent managed_root → benign WARN skip, not a raise. (d) Allowlist exact-match (false-neighbor `foo` vs `foo-2` not protected). (e) Nested/loose non-pack entries ignored, no throw. (f) Dry-run inert: origin ref byte-identical before/after. (g) AC7 receipt-golden: each former call site produces the same receipt shape + commit content as a captured golden.
- **RA8 — Live proof (Marcus C3/C6).** Live-prove BOTH failure paths (size-guard trips fail-loud pre-push; verify catches a broken build and refuses success) via teeth-witness, on a **scratch path**, never endangering live client URLs or blowing the cap. AC-O1 evidence must show **committer-date retention firing on a real old pack**, not just "a prune ran."
- **RA9 — Product boundary (Marcus C1).** Retention policy is "keep the client review loop live" — not concierge/proofing-run decluttering.
- **RA10 — Governance.** Codex shadow-monitor consulted at each gate as first-class review input; `bmad-code-review` before close; fail-loud-never-silent (RA5 pattern) is the universal acceptance bar for every guard.

## Reconciliation with the goal's task numbering
The goal's **Task 2** remains the GitHub Actions durable-deploy path. The gamma+storyboard primitive-adoption the party split out is **Task 1b (in-arc fast-follow)**, sequenced after Task 1a and independent of the goal's Task 2. Goal task numbering is unchanged.

## Route (confirmed)
party greenlight (DONE) → `bmad-quick-dev` for Task 1a (T1→T6, RED-first) → gamma+storyboard adoption Task 1b → `bmad-code-review` → live-prove failure paths on scratch path → close. Marcus-first throughout.
