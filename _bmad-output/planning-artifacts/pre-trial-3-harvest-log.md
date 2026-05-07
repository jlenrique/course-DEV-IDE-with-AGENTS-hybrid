---
title: Pre-Trial-3 Cleanup Harvest Log
authoredAt: 2026-05-07
purpose: Capture session-by-session harvest items (new anti-patterns, deferred entries, ADR candidates, scope discoveries) so cross-session learnings don't leak. Rolled up at S6 close into permanent registers (specialist-anti-patterns.md, deferred-inventory.md, ADRs).
governance: Mary AM-6 amendment to pre-Trial-3 cleanup plan, ratified pre-S1 party-mode review 2026-05-07.
---

# Pre-Trial-3 Cleanup Harvest Log

Each session's post-review captures harvest items below. S6 close: distribute entries into permanent registers (anti-pattern catalog / deferred-inventory / ADRs / governance JSON) and mark this file historical-archive.

---

## Pre-S1 review harvest (2026-05-07)

Items surfaced during the 4-agent pre-S1 review that should be remembered (not lost between sessions):

1. **(Mary)** Pattern signal: when "renumber" appears in a remediation spec, ALWAYS read the actual file — renumbering rarely captures the full structural defect. Surfaced in P0-4 anti-pattern dedup (zombie heading + zombie placeholders existed beyond the bare numbering issue). **Filing target:** new harvest candidate for `specialist-anti-patterns.md` at S6 — "P5. Remediation specs that say 'renumber' without reading actual file state."

2. **(Amelia)** Discovery: legacy `marcus/` is NOT a shim — it's a partial migration. `app/marcus/lesson_plan/` and `app/marcus/intake/` do not exist; the lesson-planner / 4A foundation lives only in legacy `marcus/`. **Filing target:** post-S2 (after collapse closes), capture the migration-completeness anti-pattern: "shim packages should EITHER fully shadow legacy OR be explicitly partial with sub-package presence-check." Possible A21 / D14 Slab-7 architectural decision append.

3. **(Murat)** Discovery: `state/config/run-constants.yaml` does NOT exist at top level — confirmed during pre-S1 verification. v4.2 §04.55 lock semantics may expect a per-run-only file or a top-level template. **Filing target:** P1-25 spike already names this; resolution at S5 should produce a definitive answer. If absent-by-design, document the convention in PP-3c (S1) + Composition Spec §10 (S5).

4. **(Murat)** Discovery: `scripts/health/` directory does NOT exist; the real preflight-check substrate lives at `skills/pre-flight-check/scripts/preflight_runner.py` + `scripts/utilities/app_session_readiness.py` + `scripts/heartbeat_check.mjs` + `scripts/smoke_*.mjs`. The original cleanup plan referenced a phantom path. **Filing target:** PP-3b body cites real paths; harvest into Composition Spec §10 (S5) as "preflight surface inventory."

5. **(Paige)** Discovery: PP-2 disposition (v4.2 Marcus-module column legacy-frozen vs runtime-path-replace) is a load-bearing precondition for S4 v5 authoring. Originally framed as a P1 item; surfaced as needing pre-S4 resolution. **Filing target:** mid-S1 PP-2 disposition vote captures the policy; no permanent-register filing needed.

6. **(Mary)** Pattern signal: 11+ governance gates risks review fatigue. Asymmetric weighting (lightweight pre-review ~15 min / 2-3 voices; heavier post-review ~30 min / 4 voices) protects party-mode capacity without compromising operator's mandate. **Filing target:** governance pattern; potential CLAUDE.md amendment at S5 if proven over 6 sessions.

---

## Post-S1 review harvest (PENDING — populate after S1 close)

_(Empty until S1 closes)_

---

## Pre-S2 review harvest (PENDING)

_(Empty until S1 closes and pre-S2 review fires)_

---

## Post-S2 review harvest (PENDING)

_(Empty)_

---

## Pre-S3 / Post-S3 / Pre-S4 / Post-S4 / Pre-S5 / Post-S5 / Pre-S6 / Post-S6 review harvests

_(Empty; populated session-by-session)_

---

## S6 close — roll-up distribution

_(At S6 close, this section enumerates each harvest item's filing destination: anti-pattern catalog entry / deferred-inventory entry / ADR / governance JSON / CLAUDE.md amendment. After distribution, this file is marked historical-archive.)_
