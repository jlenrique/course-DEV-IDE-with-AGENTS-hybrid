---
title: 'Status-Surface Consolidation — 3 SSOTs + 2 generated views + archived cold history'
type: 'refactor'
created: '2026-07-17'
status: 'in-progress'
review_loop_iteration: 0
baseline_commit: '6d87f35b'
context:
  - '{project-root}/bmad-session-protocol-session-START.md'
  - '{project-root}/bmad-session-protocol-session-WRAPUP.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 7 overlapping status surfaces are hand-maintained and interleave current truth with accumulated history, so every session START/WRAPUP pays a growing coherence tax and they have drifted once already. Worst offenders: `bmm-workflow-status.yaml` (37.7KB comment-blob in 7 top lines, zero machine consumers), `docs/project-context.md` (132KB, auto-loaded into ~59 skills' context every invocation, mostly duplicate addendum history), and `SESSION-HANDOFF.md` (3,174 lines / 86 sections).

**Approach:** Establish 3 authored SSOTs — `sprint-status.yaml` (Kanban), `SESSION-HANDOFF.md` (chronology), `STATE-OF-THE-APP.md` (product truth) — plus `deferred-inventory.md` (governance register, semantics untouched). Demote `next-session-start-here.md` and `project-context.md` to **fail-loud generated views**. Archive cold history to dated `*.history.md` siblings with a standardized pointer, add a mechanical WRAPUP roll-down step, and rewrite the START/WRAPUP context-transfer contract table (the SSOT-of-SSOTs) to match. Sequence so each step is reversible before the risky one; reconcile `sprint-status.yaml` last.

## Boundaries & Constraints

**Always:**
- Preserve every machine contract found in the consumer audit: `sprint-status.yaml`'s `development_status` mapping (2-space indent, `epic-*`/`migration-epic-*` prefixes, `#`-comment tolerance) AND its top-level `tripwire_events:` list; the `progress_map.py` heading strings `## What is next` / `## Unresolved issues` (HANDOFF) and `## Immediate Next Action` / `## Key Risks / Unresolved Issues` (next-session); `deferred-inventory.md`'s `| **…` row shape and named entry-IDs.
- `docs/project-context.md` stays at its exact path (glob-loaded by ~59 skills); its archive sibling must NOT be named `project-context.md` anywhere in the tree.
- Generators are fail-loud + fixture-gated and are convenience views: if generation fails or a required field/heading is missing, they raise (non-zero exit) rather than emit a truncated file; the authored SSOT remains the fallback authority.
- Archive == move, never delete: cold history goes to a dated `*.history.md` sibling; each trimmed hot file carries a `> History archived to <sibling>` pointer.
- Retention line: hot files keep the current arc + 1 prior; older rolls to the archive.

**Ask First:**
- Any change to a `sprint-status.yaml` `development_status` STATUS VALUE whose SOTA-§11 truth is ambiguous (surface it, don't guess).
- Renaming/moving any of the 7 files, or changing any load-bearing heading/field/entry-ID.
- Changing what a ledger *means* (deferred-inventory semantics, sprint-status schema).

**Never:**
- Reformat `sprint-status.yaml` structurally (reindent, YAML-normalize, reorder keys) — 3 consumers are line-regex, not YAML parsers. Value-level edits + whole-block moves only.
- Touch `tripwire_events:` content.
- Delete history. Introduce a second `project-context.md` anywhere. Fix sprint-status CONTENT and structure in the same commit as the archive (sprint-status is its own last, reviewed step).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| generate next-session (happy) | SESSION-HANDOFF latest section + `git log` + deferred counts | `next-session-start-here.md` with `**Expected class…`, `## Immediate Next Action`, `## Key Risks / Unresolved Issues`, `Deferred inventory status` lines, branch + HEAD sha | N/A |
| generate next-session (missing input) | HANDOFF latest section lacks a required heading | non-zero exit, named error; file NOT overwritten | fail-loud; fall back to authored |
| generate project-context (happy) | HANDOFF latest + SOTA §11 + preserved base-doc block | thin current-state header + base doc verbatim below a stable marker, at `docs/project-context.md` | N/A |
| generate project-context (base marker absent) | base-doc marker not found in existing file | non-zero exit; file NOT overwritten | fail-loud; do not drop the base doc |
| archive roll-down | hot file with sections older than current arc + 1 prior | old sections appended to dated `*.history.md`; hot file trimmed + pointer added | idempotent; re-run is a no-op |
| sprint-status reconcile | stale status strings vs SOTA §11; done-epic blocks | corrected values + done blocks moved to history sibling; all parsers + audit tests green | any parser/test RED ⇒ revert that move, HALT |

</frozen-after-approval>

## Code Map

**Authored SSOTs (hand-maintained):**
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Kanban. HARD contract: `development_status` (progress_map.py + `trial_run_preflight`/`m5_pre_vote_audit`/`audit_done_bmad_coverage` line-regex + `tests/test_sprint_status_yaml.py`) and `tripwire_events` (written by `validate_parity_test_class_conformance.py`, hashed by `tests/audit/test_audit_ac_*`).
- `SESSION-HANDOFF.md` — chronology. `progress_map.py::_extract_section` keys on `## What is next` / `## Unresolved issues` (prefix match). 86 sections; current arc = the three 2026-07-17 sections (L1–127), +1 prior = 2026-07-16 EVE (L128–171).
- `docs/STATE-OF-THE-APP.md` — product truth. ZERO machine consumers. Two banner stacks: top synthesis (L8–79), §11 you-are-here (L235–306) + a §11.5 one at ~L531; `(SUPERSEDED …)` marks archival blocks.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — governance register (untouched semantics). Count-parsed by `migration_health_dashboard.py`; the mandated `## Closed Entries — Archived` section does NOT exist yet.

**Demote to generated views:**
- `next-session-start-here.md` (gitignored) — already overwritten each session; heading contract above + CLAUDE.md-mandated `**Expected class**` + `Deferred inventory status` lines.
- `docs/project-context.md` — glob-loaded by ~59 skills. L1–306 addendum stack (regenerable dup) over L307–607 unique base doc (planning decisions, tool universe, composition arch, key files). Authored today by `bmad-generate-project-context`.

**Zero-consumer, safe to trim:**
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` — blob at L2–8 (37.7KB); structured YAML L10–434 intact; ZERO parsers.

**Protocol (SSOT-of-SSOTs):**
- `bmad-session-protocol-session-START.md` / `bmad-session-protocol-session-WRAPUP.md` — the context-transfer contract table (START §1/§4 reads, WRAPUP §3/§4a/§5/§7/§8 writes).

**New:**
- `scripts/utilities/generate_next_session.py`, `scripts/utilities/generate_project_context.py` (+ `tests/utilities/test_generate_*.py` fixtures).

## Tasks & Acceptance

**Execution (ordered — reversible steps before the risky one):**

- [x] **T1 — Archive cold history (bmm-workflow-status).** `bmm-workflow-status.yaml`: move blob L4–8 (keep title L1 + newest 2 entries L2–3) to `bmm-workflow-status.history.md`; add `> History archived to …` pointer. Leave structured YAML (L10–434) untouched. **DONE `497eb4dc`** (36.7KB archived).
- [x] **T2 — Archive cold history (SESSION-HANDOFF).** Move sections older than current-arc-+1-prior (archive L172–3174) to `SESSION-HANDOFF.history.md`; keep L1–171; preserve the two contract headings in the current section; add pointer. **DONE `497eb4dc`** (82 sections; 547KB → 20KB).
- [x] **T3 — Archive cold history (STATE-OF-THE-APP).** Move `(SUPERSEDED …)` blocks beyond current+1-prior in both stacks to `STATE-OF-THE-APP.history.md`; keep the numbered body §1–§10 + §11 structure; add pointer; fix any prose links. **DONE `497eb4dc`** (122KB → 81KB; FRAMING PRINCIPLE kept).
- [x] **T4 — deferred-inventory archive-section sweep. DESCOPED (operator-approved 2026-07-18).** The `## Closed Entries — Archived` section ALREADY EXISTS (L1051; the audit's "doesn't exist" was wrong). Per the file's own maintenance rule the closed-entry sweep belongs at a retrospective / multi-slab milestone, not a structural pass — deferred there. No deferred-inventory changes this pass.
- [ ] **T5 — Build `generate_next_session.py`** — reads HANDOFF latest section + `git log -1` + deferred counts; emits parser-EXACT Title-Case headings (`## Immediate Next Action`, `## Key Risks / Unresolved Issues`) + Expected-class + deferred lines; fail-loud on missing input. + fixture test. *(delegated; in progress)*
- [ ] **T6 — Build `generate_project_context.py`** — emits thin current-state header (from HANDOFF latest + SOTA §11.1) ABOVE a stable `<!-- BASE-DOC (hand-authored, preserved) -->` marker; preserves the base doc (current L307–607, starts `# Project Context: Multi-Agent…`) verbatim; writes to `docs/project-context.md`; fail-loud if the base marker/heading is absent. + fixture test. Archives the L1–306 addendum stack to `project-context.history.md`. *(delegated; in progress)*
- [x] **T7 — Rewrite the START/WRAPUP contract table + roll-down step.** Updated both protocol context-transfer tables (generated views vs SSOTs + history siblings); added the "Status-surface SSOT & retention contract" block; WRAPUP §5 → `generate_project_context.py`, §7 → `generate_next_session.py`, §3 bmm-blob note; added the arc-close roll-down under §8 + the pointer pattern. CLAUDE.md/Cursor/Copilot mirrors left as-is (they reference files by name; nothing moved/renamed). **DONE** (protocol docs).
- [x] **T8 — Reconcile `sprint-status.yaml` (own reviewed step). DONE — safe reconcile + honesty pointer (operator-scoped 2026-07-18).** Discovery: epics 41/42/43 were already `done`; the staleness was comments + one wrong value + ~10 ambiguous pre-Epic-35 rows SOTA says track elsewhere. Applied: `epic-concierge-substrate` in-progress→done (SOTA §11.5 unambiguous); corrected epic-41 comment (41-4 budget-brake done `cf7df4fd`), epic-43 comment (master consolidated `12775df6`), `last_updated`; added a TRACKER-REALITY NOTE atop `development_status` codifying that pre-Epic-35 arcs track via SOTA §11 + SESSION-HANDOFF; fixed `progress_map.py::WAVE_LABELS` for 41/42/43. **No structural reformat; no done-row archival; `tripwire_events` untouched; ambiguous epics NOT guessed** (per frozen Ask-First). Gate GREEN: 48/48 targeted tests pass (incl. the WAVE_LABELS + tripwire audits); YAML valid; `progress_map`/`audit_done_bmad_coverage` nonzero confirmed PRE-EXISTING (baseline-stash verified).

**Acceptance Criteria:**
- Given a trimmed hot file, when a session opens, then its current truth is intact and a `> History archived to …` pointer resolves to the moved content (nothing deleted).
- Given `generate_next_session.py`/`generate_project_context.py`, when a required input heading/field is missing, then it exits non-zero and does NOT overwrite the target (authored fallback preserved).
- Given `generate_project_context.py` output, when ~59 skills glob-load `docs/project-context.md`, then they load the thin header + preserved base doc (no 132KB addendum stack) at the unchanged path.
- Given the sprint-status reconcile, when the full parser + audit suite runs, then `progress_map.py`, `test_sprint_status_yaml.py`, the 3 line-regex consumers, and `test_audit_ac_*` (tripwire hash) all pass.
- Given the rewritten protocol, when a session runs START then WRAPUP, then every file in the contract table has a corresponding read and write and the roll-down step is a named WRAPUP action.

## Spec Change Log

- **T4 premise corrected (discovery during impl).** The structure audit reported the `## Closed Entries — Archived` section "does not exist"; it DOES (deferred-inventory L1051, with 24+ entries already archived at the 2026-05-07 S1 sweep). The file's own maintenance rule assigns closed-entry sweeps to retrospective / multi-slab-close milestones. → T4 revised: no section to create; recommend descoping the bulk post-S6 sweep to the next retrospective rather than folding it into this structural pass. Avoids a risky governance-register churn for hygiene-only value.
- **progress_map heading-case drift (latent bug surfaced).** `progress_map.py` matches section headings CASE-SENSITIVELY (`_extract_section` / `_qualify_markdown`, no `IGNORECASE`), expecting Title-Case `## Immediate Next Action` / `## Key Risks / Unresolved Issues` / `## What Is Next` / `## Unresolved Issues`. The live files have used sentence-case (`## Immediate next action`, `## What is next`), so the parser has silently extracted nothing for these → `next_up_source` empty. Fix folded into T5: `generate_next_session.py` emits the parser-EXACT Title-Case headings, repairing the contract for the generated file. SESSION-HANDOFF hot-section heading alignment is left to hand-authoring per T7 (not retitling 82 archived sections).

## Design Notes

**Frozen per-file contract:**

| File | Role | Fate | Hard constraint |
|---|---|---|---|
| sprint-status.yaml | Kanban SSOT | value-reconcile + archive done rows | preserve dev_status indent/`epic-*`/comments + `tripwire_events`; all parsers green |
| SESSION-HANDOFF.md | chronology SSOT | keep L1–171, archive rest | keep `## What is next` / `## Unresolved issues` in current section |
| STATE-OF-THE-APP.md | product-truth SSOT | keep current+1-prior banners, archive rest | pure prose; fix links |
| deferred-inventory.md | governance register | add `## Closed Entries — Archived`, move struck entries | keep `| **…` rows + entry-IDs |
| bmm-workflow-status.yaml | BMAD phase | archive blob L4–8, keep YAML | ZERO consumers; keep L10–434 |
| next-session-start-here.md | hot-start cache | GENERATED (fail-loud) | emit the 4 required headings/lines |
| project-context.md | current-state card + base ref | GENERATED thin header + PRESERVE base | stays at `docs/project-context.md`; sibling ≠ that name |

Retention rule (mechanical, WRAPUP-enforced): hot = current arc + 1 prior; older rolls to `*.history.md`.

## Verification

**Commands:**
- `.venv/Scripts/python.exe -m pytest tests/test_progress_map.py tests/test_sprint_status_yaml.py -q` -- expected: PASS (heading + Kanban contracts intact)
- `.venv/Scripts/python.exe -m pytest tests/utilities/test_generate_next_session.py tests/utilities/test_generate_project_context.py -q` -- expected: PASS (fail-loud fixtures)
- `.venv/Scripts/python.exe -m pytest tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py tests/audit/test_audit_ac_shape_pins_class_conformance.py -q` -- expected: PASS (tripwire ledger preserved) — run after T8
- `.venv/Scripts/python.exe scripts/utilities/progress_map.py` -- expected: renders (consumes reconciled sprint-status + trimmed HANDOFF/next-session without error)
- `.venv/Scripts/python.exe scripts/utilities/generate_next_session.py && .venv/Scripts/python.exe scripts/utilities/generate_project_context.py` -- expected: both emit; re-run is idempotent

**Manual checks:**
- Each trimmed hot file opens with a resolvable `> History archived to …` pointer; the sibling holds the moved content byte-for-byte.
- `grep -rc "project-context.md" .` unchanged except the new generator/protocol references; no second `project-context.md` created.
