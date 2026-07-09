---
title: 'Storyboard correctness — Gary deck-export cover-shift + brief→page cardinality fix (title-based page→slide_id matching)'
type: 'bugfix'
created: '2026-06-17'
status: 'done'
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
The normalization rules themselves are PINNED (the next silent bug hides here).

## Matching algorithm (RATIFIED amendment 2026-06-18 — deterministic bijective containment)
Replaces exact-after-normalization (T1 proved exact false-misses 2/5 on the real corpus). Steps:
1. **Normalize** both brief titles and page slugs per the frozen Normalization contract above → normalized strings.
2. **Tokenize + strip stopwords** (NEW frozen stopword list — enumerate explicitly, e.g. {the, a, an, and, or, of, for, to, in, on, with, case…}; pin it; NO library default). → distinctive token-set per brief and per page.
3. **Candidate containment edges:** for each (brief, page), an edge exists iff `brief_tokens ⊆ page_tokens` OR `page_tokens ⊆ brief_tokens` (bidirectional) AND the **smaller (contained) side has ≥2 distinctive tokens** (the token floor). A single-distinctive-token containment is NOT an edge.
4. **Compute ALL edges first** (no streaming/greedy/first-match). Then **bijective commit:** an edge (brief_i, page_j) is committed ONLY iff brief_i has exactly ONE candidate page AND page_j has exactly ONE candidate brief.
5. **Ambiguity is fatal:** any brief with >1 candidate page, or any page with >1 candidate brief → raise `gamma.export.title-ambiguous` (error-pause); surface ALL colliding pairs; NEVER pick. No tie-break, no longest-containment, no "best."
6. **After commit, classify the remainder (bijection assertion):** every brief is matched-once OR `gamma.export.brief-unmatched`; every page is matched OR leading-cover-dropped (DECISION 1) OR `gamma.export.page-unmatched` (DECISION 5, non-leading). No brief matched zero-or-twice; no page silently unaccounted. (This bijection assertion REPLACES the count-guard.)
7. **Gamma nudge (non-load-bearing):** add to `additional_instructions` a request to title each card exactly as briefed, emit no cover/title card, and not merge topics. Best-effort dampener ONLY — the matcher is the contract; never weaken the matcher because of the nudge.

Real-corpus proof (f8da20ae): slide-01→p2 (exact) · slide-02→p3 (page⊆brief: Gamma dropped "System") · slide-03→p4 · slide-04→p5 · slide-05→p6 (brief⊆page: Gamma appended merge text) · slide-06→unmatched (correctly; no page) · p1 cover→dropped. 5/5 renderable correct; bijective; no collisions.

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
**2026-06-18 (T1) — EMPIRICAL FINDING invalidates the exact-match amendment; party re-consult opened.** T1 check on the real f8da20ae corpus: Gamma not only injects a cover + merges topics, it REPHRASES titles. Exact-after-normalization matches only 3/5 renderable content slides: slide-02 brief "The Human Cost: System Waste & Burnout" vs Gamma slug "The-Human-Cost-Waste-and-Burnout" (Gamma DROPPED "System") → exact=FALSE → would spuriously `brief-unmatched` fail-loud on a perfectly-rendered slide (John's Trial-A-blocker criterion). slide-05 "The Leadership Gap" vs merged "The-Leadership-Gap-and-the-Case-for-Change" → exact=FALSE. Deterministic BIJECTIVE CONTAINMENT matching (token-set subset, unique) = 5/5 correct (slide-01→p2, 02→p3, 03→p4, 04→p5, 05→p6, 06→unmatched), cover→dropped — NOT threshold-fuzzy; silent-wrong-match still barred by bijection + ambiguity-fatal. Proposed amendment to the matching rule routed to party-mode 2026-06-18 (see below).
**RESOLVED 2026-06-18 — party-mode unanimous APPROVE-AMENDMENT (Winston/Amelia/Murat/John).** Matching rule changed from exact-after-normalization to **deterministic BIJECTIVE CONTAINMENT** (see "Matching algorithm" section). Convergent binding sub-amendments: (W1/A1) strip stopwords + **≥2-distinctive-token floor** on the contained side (a 1-distinctive-token containment is NOT a match — closes the "short brief supersets an unrelated page" hole; "the threshold barred, hidden in the word 'the'"); (A3/M3) bijection is **all-edges-then-uniqueness, NEVER greedy/max-matching** — commit an edge only if unique on BOTH sides; (W2/M3) **ties die loud** — multiplicity → `gamma.export.title-ambiguous` hard abort, NO longest-containment tie-break ("a tie-break is nearest-neighbor in a trenchcoat"; "if the implementation tie-breaks ambiguity even sensibly, automatic revert"); bidirectional containment (brief⊆page for Gamma-append, page⊆brief for Gamma-drop) is permitted, made safe by bijection+floor not by per-direction heuristic; normalization contract (above) stands UNDERNEATH unchanged; stopword list is a NEW frozen artifact (enumerate + pin, no library default). Gamma `additional_instructions` nudge (title-exactly/no-cover/no-merge) approved as an explicitly NON-LOAD-BEARING dampener (Gamma ignored num_cards=6; matcher carries 100% of correctness). John: in-scope (the pre-authorized conditional firing, not creep); Trial-A date holds; block any fuzzy/threshold riding in.

**2026-06-18 — party-mode green-light RATIFIED (Winston/Amelia/Murat/John, unanimous APPROVE-WITH-AMENDMENTS).** 4 decisions resolved: #1 drop+record leading-only · #2 fail-loud · #3 shared materializer additive-signature + generic key-spec/MatchResult · #4 DEFERRED (post-Trial-A spike). Added DECISION 5 (non-leading unmatched page → fail-loud) + 6 (ambiguity fatal). Gating amendments folded: frozen Normalization contract (exact-after-normalization, NO fuzzy); bijection assertion REPLACING the count-guard; kill-the-mutant pin on real f8da20ae filenames; standalone-lane byte-identical gate pin + gary-only off-ramp. Riders: Obs A FOLD IN, Obs B DEFER. MVP line drawn (John). T1 conditional: long-title-truncation demonstrated-vs-speculative check. Status → ready-for-dev.

## Review Findings (3-lane bmad-code-review, 2026-06-18)
Acceptance Auditor: **PASS** (all 6 decisions + both riders + bijection-replaces-count-guard + content-keyed kill-the-mutant + ≥2-token floor + frozen stopwords + full named battery; no deferred item leaked). Blind + Edge convergent findings, all remediated:
- [x] [MUST-FIX] Duplicate `page_index` silently dropped a page (dict last-wins keying). Fixed: `match_pages_to_slots` now keys pages by unique position, `page_index` retained only for leading-cover ordering; pinned `test_duplicate_page_index_does_not_silently_drop_a_page`.
- [x] [SHOULD-FIX] Leading-cover heuristic could drop a genuine retitled leading content page. Fixed: cap leading-cover drops at ONE; additional leading-unmatched → `page-unmatched` fail-loud; pinned `test_only_first_leading_unmatched_page_drops_rest_fail_loud`.
- [x] [SHOULD-FIX] gary integration tests near-vacuous on binding identity (identical fixture bytes + always-`_s1.png` name). Fixed: distinct per-page bytes + content-identity assertions; export-url test now uses REVERSE page order so a positional binder fails.
- [x] [NIT] `dropped_pages` accumulated but not surfaced. Fixed: emitted into the gary receipt (`dropped_pages` key) per Decision #1 provenance.
- Deferred NITs (loud/low-likelihood, not fixed): non-`{N}_`-prefixed cover sorts last → `page-unmatched` (loud, acceptable); all-unmatched cover mislabel (masked by `brief-unmatched`); `normalize_title` first-delimiter objective split (latent, slug convention strips dashes).
- Verified clean (Edge): positional `_materialize_exported_slide_paths` byte-identical (228 insertions / 0 deletions — purely additive); both standalone callers unaffected; dead `_paths_from_generation` removal clean; degenerate paths (empty/non-png/single-image/over/under-count) all fail loud.

Validation: 244 passed (gary + audit + marcus integration), 1 skipped; lockstep 0; lint-imports 13/13; ruff clean; kill-the-mutant verified (exact-only `_edge` revert reds the f8da20ae + bidirectional pins).

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

## Amendment 2026-07-07

- `normalize_title` apostrophe-family deletion-joining amendment (dual-pass pinned `_TITLE_APOSTROPHE_FAMILY`; live pair "Technology's Promise..." <-> "Technologys-Promise-..." from trial a18c2a86) ratified at party record §10, `_bmad-output/planning-artifacts/canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md`.
