# Migration Story 7c-housekeeping-4: Legacy Sidecar Cleanup — Vera + Dan (post-Trial-2 validation; bundled)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=2; **DISPATCH-DEFERRED** until Trial-2 validation evidence confirms the BMB-canonical sanctum paths are operationally validated for Vera + Dan cold activation. Operator-decision item; minimal Codex scope when authorized.)*
**Sprint key:** `migration-7c-housekeeping-4-legacy-sidecar-cleanup`
**Source:** Deferred-inventory entries `vera-sidecar-cleanup-post-trial-2-validation` (Story 7b.3 follow-on) + `dan-sidecar-cleanup-post-trial-2-validation` (Story 7b.10 follow-on). Bundled into one story since shape is identical (operator-gated archive + verification).
**Pts:** 1
**K-target:** 1.1×
**Estimated LOC:** ~50 (deferred-inventory entry closure + git-rm cleanup; minimal code)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R1
**T11-tier:** lite
**Lookahead-tier:** 2
**files_touched:** 0 new + 2-N modified (deferred-inventory.md + 2 sidecar directories archived/removed; possibly 2 doc-cross-reference updates)

---

## Story

As the dev-agent (post-operator-authorization),
I want legacy `_bmad/memory/vera-sidecar/` + `_bmad/memory/dan-sidecar/` cleaned up after Trial-2 validates BMB-canonical sanctum cold-activation paths at `_bmad/memory/bmad-agent-vera/` + `_bmad/memory/bmad-agent-dan/`,
So that the deferred-inventory entries `vera-sidecar-cleanup-post-trial-2-validation` + `dan-sidecar-cleanup-post-trial-2-validation` close cleanly + the legacy two-sanctum-mental-model debt retires.

This story is **Codex-light** — most of the work is conditional verification + a trivial `git rm` (or `git mv` to archive). Total dev-agent effort ~30 min.

---

## Predecessor / Dependency Context

- **Trial-2 validation evidence**: required precondition. Per the deferred-inventory entries: "Cleanup only after trial-2 validates Vera/Dan cold activation and SG-4 parity on `_bmad/memory/bmad-agent-{name}/`; then archive or remove the legacy sidecar by operator decision."
- **Vera BMB-canonical sanctum** at `_bmad/memory/bmad-agent-vera/` (6-file BMB pattern; INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES) — landed at Story 7b.3 close 2026-04-29.
- **Dan BMB-canonical sanctum** at `_bmad/memory/bmad-agent-dan/` (6-file BMB pattern) — landed at Story 7b.10 close 2026-04-30.
- **Legacy sidecars**:
  - `_bmad/memory/vera-sidecar/` (5-file pattern; pre-Slab-7b SG-4 enforcement)
  - `_bmad/memory/dan-sidecar/` (CD-lane; pre-BMB)

Both are operator-decision archive-or-remove targets per the deferred-inventory governance.

---

## Acceptance Criteria

### AC-1 — Trial-2 validation precondition (HARD GATE)

**Given** the deferred-inventory governance: "Cleanup only after trial-2 validates Vera/Dan cold activation and SG-4 parity"
**When** the dev-agent runs T1 readiness checks
**Then** the operator-supplied Trial-2 validation evidence MUST be present (operator-decision; document the evidence pointer in the dispatch context).
1. If evidence absent: HALT-AND-ESCALATE to operator. Do NOT proceed to AC-2.
2. If evidence present: proceed.

Acceptable evidence shapes:
- (a) Operator paste-in of Trial-2 cold-activation log showing Vera + Dan loading from `_bmad/memory/bmad-agent-vera/` + `_bmad/memory/bmad-agent-dan/` cleanly.
- (b) Trial-2 transcript artifact at `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` (or successor) containing per-specialist cold-activation evidence for Vera + Dan.
- (c) Direct operator authorization in commit message ("operator-authorized cleanup; Trial-2 validation skipped per ratified shortcut").

### AC-2 — Sidecar archive or removal (operator-choice)

**Given** Trial-2 validation evidence per AC-1
**When** the dev-agent executes the cleanup:
**Then** ONE of the following (operator-chooses at dispatch time):
1. **Archive path**: `git mv _bmad/memory/vera-sidecar/ _bmad/memory/_archive/vera-sidecar-pre-7b-3-2026-04-29/` + same for dan-sidecar. Files preserved under `_archive/` for audit-trail.
2. **Removal path**: `git rm -rf _bmad/memory/vera-sidecar/` + `git rm -rf _bmad/memory/dan-sidecar/`. Files removed entirely; pre-cleanup state in git history.

Default: **archive path** (operator-choice can override).

### AC-3 — Deferred-inventory entries CLOSED

**When** the cleanup completes:
**Then** `_bmad-output/planning-artifacts/deferred-inventory.md` is updated:
1. `vera-sidecar-cleanup-post-trial-2-validation` entry: status flipped to `~~CLOSED~~` (strikethrough) with closure date + commit SHA + path reference (archive or removal).
2. `dan-sidecar-cleanup-post-trial-2-validation` entry: same shape.

### AC-4 — Sanctum-alignment registry verification (no regression)

**Then** the existing sanctum-alignment infrastructure continues to PASS:
1. `tests/parity/test_skill_md_sanctum_alignment.py` PASS (Vera + Dan BMB sanctums intact at `bmad-agent-vera/` + `bmad-agent-dan/`).
2. Any test referencing the legacy `vera-sidecar/` or `dan-sidecar/` paths is also updated OR confirmed-not-existent.
3. Class-conformance UNCHANGED at 19.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks (AC-1)**
  - [ ] T1.1 Operator confirms Trial-2 validation evidence (one of three shapes).
  - [ ] T1.2 Confirm `_bmad/memory/bmad-agent-vera/` + `_bmad/memory/bmad-agent-dan/` BMB-canonical sanctums intact (6 files each).
  - [ ] T1.3 Inventory legacy sidecar contents (file count + last modification date) for archive provenance documentation.
  - [ ] T1.4 Choose archive vs removal path (operator-choice).
  - [ ] T1.5 Refresh broad-regression baseline.

- [ ] **T2 — Execute cleanup (AC-2)**
  - [ ] T2.1 If archive: `git mv` legacy sidecars to `_bmad/memory/_archive/<name>-pre-<story>-<date>/`.
  - [ ] T2.2 If removal: `git rm -rf` legacy sidecars.

- [ ] **T3 — Update deferred-inventory (AC-3)**
  - [ ] T3.1 Mark `vera-sidecar-cleanup-post-trial-2-validation` entry as CLOSED with closure provenance.
  - [ ] T3.2 Mark `dan-sidecar-cleanup-post-trial-2-validation` entry as CLOSED.

- [ ] **T4 — Verification battery (AC-4; R-tier R1; T11-tier lite)**
  - [ ] T4.1 Focused: `pytest tests/parity/test_skill_md_sanctum_alignment.py -p no:randomly -q --tb=short` PASS.
  - [ ] T4.2 Sanctum-alignment DSL non-regression: `pytest tests/parity/test_sanctum_alignment_dsl.py -p no:randomly -q --tb=short` PASS.
  - [ ] T4.3 Smoke 181/18 UNCHANGED.
  - [ ] T4.4 R1 broad: failure count delta ≤ 0.
  - [ ] T4.5 Class-conformance UNCHANGED at 19.
  - [ ] T4.6 Lint-imports 12 KEPT UNCHANGED.
  - [ ] T4.7 Sandbox-AC PASS.
  - [ ] T4.8 Ruff clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-housekeeping-4.ready-for-review.md` with: chosen path (archive vs removal) + Trial-2 evidence pointer + per-sidecar archived-at or removed-from-disk evidence + deferred-inventory closure entries.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/planning-artifacts/deferred-inventory.md` entries `vera-sidecar-cleanup-post-trial-2-validation` + `dan-sidecar-cleanup-post-trial-2-validation`.
3. `_bmad/memory/bmad-agent-vera/` + `_bmad/memory/bmad-agent-dan/` (verify BMB-canonical 6-file pattern intact).
4. `_bmad/memory/vera-sidecar/` + `_bmad/memory/dan-sidecar/` (legacy sidecar inventory).
5. Trial-2 validation evidence (operator-supplied).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

## Dispatch state

**DISPATCH-DEFERRED** until operator confirms Trial-2 validation evidence per AC-1. After confirmation: solo dispatch; ~30 min Codex effort.

---

## Why bundled (vera + dan together)

Both deferred-inventory entries have identical-shape closure paths: operator-gated post-Trial-2 archive-or-remove of legacy 4-5-file sidecars, with BMB-canonical 6-file sanctum already populated as the new path. No reason to dispatch separately. One story; two cleanups in lockstep.
