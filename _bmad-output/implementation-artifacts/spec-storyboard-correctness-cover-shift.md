---
title: 'Storyboard correctness — Gary deck-export cover-shift + brief→page cardinality fix (title-based page→slide_id matching)'
type: 'bugfix'
created: '2026-06-17'
status: 'ready-for-dev'
baseline_commit: '98ffb58'
checkpoint_1: 'RATIFIED 2026-06-18 — bmad-party-mode green-light, unanimous APPROVE-WITH-AMENDMENTS (Winston/Amelia/Murat/John). All 4 design decisions resolved; MVP line drawn by John; gating amendments folded below.'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/content-review-cycle-6-f8da20ae.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
  - '{project-root}/SESSION-HANDOFF.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem (root-caused via the cycle-6 operator review — ONE bug, both storyboards = operator Glitch #1 + #2):** Gary maps Gamma-exported deck pages onto briefed `slide_id`s **positionally**, at TWO layers, while Gamma autonomously (a) inserts a title/cover page and (b) can merge/drop briefed topics. The result on run `f8da20ae`: Gamma was asked for `num_cards=6`, returned 6 pages = **1 cover + 5 content** (Leadership + Summary merged into one), the positional zip put the cover on `slide-01`, and **every content image shifted down one slot**; the Summary&Knowledge-Check brief got no image. Storyboard A shows each slide's Script Notes/Script one row down; Storyboard B's (correct, cleanly-1:1-matched) narration narrates the *next* image's content and references items absent from the shown image.

The two positional layers and why the existing guard misses it:
1. `skills/gamma-api-mastery/scripts/gamma_operations.py::_materialize_exported_slide_paths` — extracts the export zip, sorts pages by their leading number (`_gamma_export_sort_key`; Gamma names pages `{N}_{Title}.png`), guards with a **count-only** assertion (`len(extracted) == len(expected_card_numbers)`), then maps `zip(extracted_images, expected_card_numbers)` **positionally**. Gamma's cover-insertion + merge keeps the COUNT equal (6 pages == 6 cards) so the guard passes while content is shifted.
2. `app/specialists/gary/_act.py::generate_gamma_variants` — zips the returned `paths` to the briefs again positionally: `file_path = paths[index-1]`.

**Approach — title-based page→slide_id matching (replaces positional zip at both layers).** Each Gamma export page filename carries its title (`2_The-Economic-and-Structural-Reality.png`); each brief carries `title` (from `package_builders.build_gary_briefs`). Match each brief to the export page whose normalized title matches, instead of by position. Consequences this surfaces correctly:
- The **cover** ("The Case for Physician Leadership") matches NO brief → it is an *extra, unbriefed* page (disposition = DESIGN DECISION 1).
- A **briefed topic with no matching page** (the merged-away Summary) → a *missing* slide (disposition = DESIGN DECISION 2).

This is a **production-walk behavior change by design** — unlike WAVE-0 tranches 1/2 (zero-behavior-change hardening), the storyboard-correctness item *intends* to change the slide↔image mapping. It is the gating fix the operator review unblocked; it must land before Trial A.

## RATIFIED DESIGN DECISIONS (party-mode 2026-06-18, unanimous; John drew the MVP line)

1. **Cover-page disposition → DROP + RECORD, LEADING-ONLY.** Drop the unmatched cover from the slide-mapping; record the discard as a structured provenance entry (e.g. `gamma_export.dropped_pages: [{page_index, slug, detected_title, reason: "unmatched-leading-page"}]`) — a one-line structured field, NOT a new artifact format with its own schema review. **Only contiguous LEADING unmatched pages are auto-droppable**; any mid-deck or trailing unmatched page is fail-loud (DECISION 5).
2. **Missing-brief disposition → FAIL-LOUD.** A brief with no matching page raises `GammaDispatchError(tag="gamma.export.brief-unmatched")` → **error-pause + `trial recover`** (recoverable family per re-based taxonomy `37f8323`, NOT crash). The error payload names BOTH the unmatched brief(s) AND the unmatched page(s) side by side (the merge story, not just "a brief is missing"). Degrade-blank is REJECTED — it is the same silent-failure class as the bug.
3. **Fix layer → SHARED MATERIALIZER, ADDITIVE SIGNATURE, GENERIC KEY-SPEC.** Kill BOTH positional zips at the source. The materializer does NOT take "gary briefs" — it takes a generic `expected_slots: list[(slide_id, normalized_title)]` key-spec and returns a `MatchResult` (slide-keyed mapping + `unmatched_pages` + `unmatched_keys` + `dropped_pages`). gary builds the key-spec from its briefs; the match POLICY (fail-loud, cover-drop, bijection) lives in the shared layer because it is a property of the Gamma-export contract. **Signature is ADDITIVE:** when no key-spec is supplied (standalone Gamma lane, brief-less), the function falls back to byte-identical current positional behavior. (Implementation may instead add a thin slide-keyed wrapper over a positional primitive — dev's choice — but the standalone lane's observable behavior MUST NOT change; see the gate AC.)
4. **Upstream Gamma cover-suppression → DEFERRED (separate post-Trial-A spike; ZERO dev time in this dispatch).** John's hard ruling: the title-match + cover-drop backstop is permanent and load-bearing regardless of Gamma; investigating suppression now is pure schedule risk against a frozen-engine trial with zero payoff to Trial A. File the spike; route post-Trial-A. The backstop never weakens because suppression "usually works."
5. **(falls out of the bijection) Extra / mid-deck / trailing unmatched page → FAIL-LOUD** `gamma.export.page-unmatched`. Do NOT blanket-drop unmatched pages — only the leading cover (DECISION 1). A non-leading unmatched page means a merge/drop already violated positional assumptions.
6. **Title ambiguity → FATAL.** Two briefs normalizing to the same key, or one brief matching two pages → raise `gamma.export.title-ambiguous` (error-pause), surface both, NEVER best-guess. No fuzzy / nearest-neighbor / similarity-threshold matching anywhere — match is exact-after-normalization only.

### Riders (party-ratified)
- **Observation A — FOLD IN:** wire the real slide title into `display_title` (currently the slide-id). The title-match work has the real titles in hand at the exact emitting layer; near-zero marginal cost, directly adjacent.
- **Observation B — DEFER:** `source_ref` provenance is a separate concern (provenance plumbing, not the alignment contract); file as its own item.

### MVP line (John) — IN this dispatch vs deferred
**IN (must-ship):** title-match (normalized, exact, no-fuzzy) at both layers via the additive materializer; the bijection assertion replacing the count-guard; fail-loud on `brief-unmatched` + `title-ambiguous` + `page-unmatched`; leading-only cover drop+record; the kill-the-mutant pin on the real f8da20ae filenames; the standalone-lane byte-identical gate pin; Observation A.
**DEFERRED (file as riders):** #4 Gamma cover-suppression spike; Observation B (source_ref); any over-count *recovery* logic beyond fail-loud.
**CONDITIONAL (T1 15-min check):** Gamma long-title truncation — dev confirms whether Gamma truncates titles in our actual export path. If DEMONSTRATED in the f8da20ae corpus or a Trial-A deck → in scope with a deterministic truncated-prefix match rule (else it would spuriously fail-loud on a deck we expect to pass — a Trial-A blocker). If only SPECULATIVE → out; file a follow-on rider. No truncation-tolerance engine for a hypothetical.

## Normalization contract (FROZEN — party-gating; Amelia/Winston)
Exact-after-normalization match ONLY. Two jobs, applied in order:
1. **Brief-side reduction (strip the objective):** take everything BEFORE the first em/en-dash-with-surrounding-spaces run (` — `, ` – `, ` -- `). Split on that delimiter token ONLY — NEVER split on a bare hyphen (a title may legitimately contain one).
2. **Symmetric normalization** applied to BOTH the reduced brief title AND the page slug (after stripping the `{N}_` prefix): Unicode NFKC + strip accents/smart-quotes/em-dash; lowercase; word-substitutions enumerated explicitly (`&`/`&amp;`→`and`; decide+enumerate `+`, `@`, `%`); strip all punctuation; collapse whitespace AND hyphens to one canonical separator (Gamma slug uses `-`, brief uses spaces — both → the same token); trim.
The normalization rules themselves are PINNED (the next silent bug hides here). Match is bijective + exact on the normalized form; ambiguity/duplicate → DECISION 6 fatal; no-match → DECISION 2 fail-loud.

## Boundaries & Constraints

**Always:** Replace positional correspondence with title-keyed matching at both layers. Normalization must be robust (case, punctuation, slug-dashes, the `{N}_` prefix, and the brief's `title — objective` suffix form vs the page's title-only slug). Preserve the recoverable fail-loud family (any unrecoverable mismatch → `GammaDispatchError`/`SpecialistDispatchError` → error-pause, never a silent positional fill). Keep `dispatch_variant` A/B handling intact.

**Ask First (party-mode):** the 4 design decisions above. Any change to the Gamma request contract (`num_cards`, export format). Folding the two low-severity review riders (below).

**Never:** No manifest / gate-engine / pack changes. No new silent fixture fallback. Do not "fix" by trimming the first page unconditionally (that assumes exactly-one-cover and breaks if Gamma emits 0 or 2 chrome pages — match by title, don't slice by index).

**Adjacent review riders (party decides fold-vs-defer):** Observation A — `display_title` shows the slide-id not the real title (the title-match work has the real titles in hand; cheap to wire). Observation B — `source_ref` blank (provenance link brief→corpus). Parked OUT OF SCOPE: Observation C (VO "$5.2T" vs slide "$4.5T" — content/QA, agents' later pass).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Cover + N content, counts equal | 6 pages (cover+5) vs 6 briefs | Each brief matched to its title's page; cover handled per DECISION 1; **no shift** | n/a |
| Briefed topic merged/dropped | brief has no title-matching page | per DECISION 2 (rec: fail-loud `gamma.export.brief-unmatched`, recoverable) | error-pause + recover |
| Extra unbriefed page (cover) | page matches no brief | per DECISION 1 (rec: drop + record) | n/a |
| Clean 1:1 (no cover, no merge) | N pages == N briefs, titles all match | identical to a correct positional map | n/a |
| Title ambiguity (two pages match one brief, or fuzzy) | normalization collision | refuse-loud (`gamma.export.title-ambiguous`) rather than guess | error-pause |
| Non-PNG / single-image export | degenerate path | preserve current behavior or fail-loud; do not silently broadcast one image to all briefs | per DECISION 3 review |

## Code Map

- `app/specialists/gary/_act.py:222-231` — the consumer positional zip (`paths[index-1]`); the `slide` briefs carry `slide_id` + `title`.
- `app/specialists/gary/_act.py:132-175` — `_paths_from_generation` (calls `download_export` + `_materialize_exported_slide_paths`).
- `skills/gamma-api-mastery/scripts/gamma_operations.py:1338-~1410` — `_materialize_exported_slide_paths` (zip extract → `_gamma_export_sort_key` sort → count-assert → positional zip). **Primary fix surface.**
- `skills/gamma-api-mastery/scripts/gamma_operations.py:1323-1335` — `_gamma_export_sort_key` (parses `{N}_{Title}` — the title is right here; reuse for title extraction).
- `scripts/api_clients/gamma_client.py` — `generate_deck` (DECISION 4: cover-suppression option?).
- Evidence: `state/config/runs/f8da20ae-3ed7-44b1-a054-794b0c5e09a0/exports/gary/gary_A/` (raw pages: `1_The-Case-for-Physician-Leadership` + 5 content) + `gary-dispatch-payload.json` (6 briefed slide_ids).

## Tasks & Acceptance (party-ratified MVP)

**T1 readiness (do first):** 15-min Gamma long-title-truncation check (CONDITIONAL above) — inspect a real export path; record DEMONSTRATED (→ deterministic truncated-prefix rule in scope) vs SPECULATIVE (→ out, file rider). Read the standalone-lane call sites of `_materialize_exported_slide_paths` (grep every caller; cite file:line; document its current return contract).

**Execution (must-ship):**
- [ ] **Frozen normalization helper** (per the Normalization-contract section) — brief-side objective strip on the em/en-dash-spaces token only; symmetric NFKC/casefold/`&`→`and`/punct-strip/separator-collapse. Unit-tested via the parametrized normalization table.
- [ ] **`_materialize_exported_slide_paths` (shared materializer)** — ADDITIVE signature: optional `expected_slots: list[(slide_id, normalized_title)]`; when present, return a `MatchResult` (slide-keyed map + `unmatched_pages` + `unmatched_keys` + `dropped_pages`) via bijective exact-after-normalization matching; when ABSENT, byte-identical current positional behavior. Match POLICY (cover-drop leading-only, fail-loud, bijection) lives here.
- [ ] **`gary/_act.py::generate_gamma_variants`** — consume the slide-keyed `MatchResult` by `slide_id`; REMOVE `paths[index-1]`. (Both positional zips dead.)
- [ ] **Fail-loud raises** (recoverable `GammaDispatchError`/`SpecialistDispatchError` family → error-pause): `gamma.export.brief-unmatched` (payload names unmatched briefs AND pages), `gamma.export.page-unmatched` (non-leading unmatched page), `gamma.export.title-ambiguous` (duplicate/two-way match; surface both).
- [ ] **Bijection assertion REPLACES the count-guard** — every brief matched exactly once AND every page consumed-or-classified (matched / leading-cover-dropped / fail-loud). Old `len(pages)==len(briefs)` guard REMOVED (count value retained only as an error-message diagnostic, not a passing gate).
- [ ] **Cover drop+record** (leading-only) — structured `dropped_pages` provenance entry.
- [ ] **Observation A (FOLD IN)** — emit the real slide title into `display_title` (no longer the slide-id).
- [ ] **Governance:** TW-7c-4 allowlist for new app-layer test paths; confirm `gamma_operations.py` (skills/) scope handling; lockstep + lint-imports + ruff.

**Deferred (file as riders, NOT in this dispatch):** #4 Gamma cover-suppression spike (post-Trial-A); Observation B (`source_ref` provenance); over-count *recovery* logic beyond fail-loud.

**Test battery (named ACs — Amelia's 8 + Murat's kill-the-mutant + John's gate):**
1. **f8da20ae regression / kill-the-mutant pin** — reconstruct the EXACT failing input (6 briefs; 6 pages = `1_The-Case-for-Physician-Leadership` cover + 5 content with Leadership+Summary merged, literal slugs). Assert each brief binds to its CORRECT image BY TITLE IDENTITY (`slide_for("Economic").image == page("...Economic-and-Structural-Reality")`), the cover is recorded-dropped, and the Summary brief raises `brief-unmatched`. **Documented kill-the-mutant step: reverting to positional mapping MUST turn this red** (it asserts content identity, not `len()` — the old count-guard passed on this exact input; the AC bar is "catches what `len==len` could not").
2. **Normalization unit-table** (parametrized): `&`→`and`, em-dash/en-dash/`--` objective strip, a title with a LEGIT hyphen (must NOT be destroyed), accents/smart-quotes, NFKC, trailing whitespace, Gamma-truncated long title (match-or-fail per T1 finding). Each row asserts normalized-equal / not-equal.
3. **Ambiguity** — two briefs reducing to the same normalized title → `title-ambiguous`, both surfaced, no silent first-pick.
4. **Standalone-lane byte-identical GATE pin (John)** — call the materializer with NO `expected_slots`; assert byte-identical pre-fix behavior (ordering, count-assert, return shape). If this pin is not cheap to stand up, that is the signal to fall back to the documented **gary-only re-key off-ramp** for Trial A (migrate to the shared materializer as a fast-follow).
5. **Over-count** — cover + 1 trailing chrome page + N content → leading cover dropped, trailing page → `page-unmatched` fail-loud (NOT silently dropped).
6. **Under-count / merge** — N briefs, N-1 pages → clean `brief-unmatched` (not a confusing double-match).
7. **Clean happy path** — N pages == N briefs, no cover, titles all match → correct keyed mapping, no regression vs a correct positional map.
8. **Both-layers code assertion** — no positional index access (`paths[index-1]`, `zip(pages, …)`) survives on the gary content path (read both sites post-change).
- Re-bless (not rubber-stamp) existing gary export pins that move: `test_gary_export_url_materialization.py`, `test_gary_generation_id_fail_loud.py`, and any downstream consumer that read gary output positionally.

**Acceptance Criteria:**
- Given the f8da20ae-shaped export, each briefed `slide_id` binds to the title-matching image (ZERO shift); cover recorded-dropped; Summary brief → `brief-unmatched` error-pause.
- Reverting the title-match to positional turns the regression pin RED (kill-the-mutant).
- Standalone Gamma lane (no `expected_slots`) is byte-identical pre/post (gate pin), OR the gary-only off-ramp is taken with rationale.
- Ambiguous/unmatched/non-leading-unmatched → recoverable error-pause (never silent fill or blank gate slide).
- Bijection holds (every brief once; every page classified); no `len==len`-only gate remains.
- Full battery green (gary suite + gamma_operations + marcus integration + lockstep + lint-imports 13/13 + ruff), no new failures vs the ambient roster.

## Spec Change Log
**2026-06-18 — party-mode green-light RATIFIED (Winston/Amelia/Murat/John, unanimous APPROVE-WITH-AMENDMENTS).** 4 decisions resolved: #1 drop+record leading-only · #2 fail-loud · #3 shared materializer additive-signature + generic key-spec/MatchResult · #4 DEFERRED (post-Trial-A spike). Added DECISION 5 (non-leading unmatched page → fail-loud) + 6 (ambiguity fatal). Gating amendments folded: frozen Normalization contract (exact-after-normalization, NO fuzzy); bijection assertion REPLACING the count-guard; kill-the-mutant pin on real f8da20ae filenames; standalone-lane byte-identical gate pin + gary-only off-ramp. Riders: Obs A FOLD IN, Obs B DEFER. MVP line drawn (John). T1 conditional: long-title-truncation demonstrated-vs-speculative check. Status → ready-for-dev.

## Verification
**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/gary/ tests/integration/marcus/ -q`
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py`
- `.\.venv\Scripts\lint-imports.exe`
- `.\.venv\Scripts\ruff.exe check <touched files>`

## Suggested Review Order
1. The two positional zips (the bug) — `gamma_operations._materialize_exported_slide_paths` + `gary/_act.py:231`.
2. The title-match helper + normalization (the fix's hinge; test against real `gary_A` filenames).
3. The fail-loud raises (DECISION 2) — family membership + recoverability.
4. The behavior pin (cover-shift export → correct title-keyed mapping) — the regression that proves the fix.
