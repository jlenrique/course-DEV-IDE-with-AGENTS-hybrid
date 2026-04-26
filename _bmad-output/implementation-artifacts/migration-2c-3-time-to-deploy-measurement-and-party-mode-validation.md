# Migration Story 2c.3: Time-to-Deploy Measurement + Party-Mode Validation (M2 acceptance gate)

**Status:** done
**Sprint key:** `migration-2c-3-time-to-deploy-measurement-and-party-mode-validation`
**Epic:** Slab 2c (migration Epic 2c â€” Wondercraft Pilot + Generator Validation) â€” **third story; M2 acceptance gate**.
**Pts:** 1 | **Gate:** single (per governance JSON `2c-3.expected_gate_mode = "single-gate"`, rationale: null â€” measurement + roll-up + 5-agent party-mode validation; no schema-shape, no lane-boundary, no invariant-preservation; the M2 verdict-recording artifact). **K-target:** ~1.2Ã— (target 6 / floor 5; documentation-heavy + measurement-roll-up + party-mode evidence; minimal new test surface).

**M2 acceptance framing:** Story 2c.3 is the **measurement-and-verdict story** that closes M2 ("Plug-and-play specialist claim validated"). It ROLLS UP evidence from 2c.1 (Path B generator-validation) + 2c.2 (Path A live-API artifact) into a single time-to-deploy measurement + convenes a 5-agent party-mode (Winston + Murat + Paige + Quinn-R + Amelia) for the M2 GREEN-LIGHT verdict. **2c.3 produces NO new specialist code**; it produces measurement evidence + party-mode verdict-recording artifact at `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`.

**Authoring queue position (per Amelia A-R1-2c.3 BLOCKER B2):** 2c.3 spec is authored AFTER 2c.2 spec but BEFORE either 2c.1 or 2c.2 has reached `done`. Per operator directive 2026-04-25 ("create stories 2c.1 - 2c.4 until each ready-for-dev; then batch-dev"), this is **drafted-for-queue** authoring â€” the spec stays at `ready-for-dev` status BUT will not enter dev until both predecessor stories close. Sprint-status filing for 2c.2-2c.4 is batched per task list. Predecessors at authoring time: 2c.1 = `ready-for-dev`; 2c.2 = filing-pending; 2c.3 = filing-pending (this spec); 2c.4 = pending-author.

**Lean party-mode amendments applied 2026-04-26 (Murat + Amelia):** 3 BLOCKERs RESOLVED + 5 RIDERs integrated:
- **A-R1-2c.3 BLOCKER B1 (15-invariant audit matrix file does not exist) RESOLVED-BY-DEFERRAL:** No `15-invariant-audit-matrix.md` exists in repo (verified 2026-04-26); prior Slab close artifacts mention invariants in prose only. **Matrix creation scoped to Slab 5a "Invariant Audit" epic** per `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` Â§"Epic 5a â€” ... Invariant Audit â€” M5 ship/iterate/rollback gate." 2c.3 AC-D NARROWED to: produce `_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md` with the 2 row-stubs (`wanda` + `wanda_validation`) that Slab 5a will absorb at matrix creation time. Keeps 2c.3 at 1pt scope.
- **A-R2-2c.3 BLOCKER B2 (predecessor sprint-status state) RESOLVED-WITH-NOTE:** Authoring queue position header above documents the drafted-for-queue state. Spec STAYS at `ready-for-dev` per operator directive but will not enter dev until 2c.1 + 2c.2 close.
- **A-R3-2c.3 BLOCKER B3 (`tests/specialists/slab_2c/` violates convention) RESOLVED:** Test paths moved from `tests/specialists/slab_2c/test_m2_*.py` â†’ `tests/migration/test_slab_2c_m2_*.py` (4 flat files) per existing `tests/migration/test_bmb_scaffold.py` precedent. NO `slab_2c/` subdirectory.
- **A-R4-2c.3 (party-mode authoring mechanics):** AC-C extended with explicit T-task sequence: (1) invoke `bmad-party-mode` skill with AC-C-specified prompt + 5-agent roster; (2) capture each subagent text response from tool result; (3) write each verbatim into `slab-2c-m2-acceptance-verdict.md` under `### <agent>` headers; (4) synthesize consensus verdict line from 5 individual verdicts.
- **A-R5-2c.3 (5-voice viability):** T1 sub-task added â€” verify each named agent has voice on M2-acceptance question. If Quinn-R abstains ("outside lane"), 4-of-5 consensus path is acceptable; not a defect.
- **A-R6-2c.3 (conditional-green outliving 2c.4 close):** AC-D-PARTIAL extended with hard-gate clause â€” if 2c.4 reaches dev-close before operator-window completes, Slab 2c closes as `CLOSED-WITH-CONDITIONAL-M2`, NOT `CLOSED-GREEN`. M2 milestone remains `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` until operator pastes addendum.
- **M-R1-2c.3 (AC-A math assertion strengthen):** AC-A test extended â€” assert (a) cumulative-active-hours numeric value matches sum of STRUCTURED TIMER deltas within Â±0.1h tolerance, AND (b) verdict-band line in report matches the band the cumulative-hours value falls into per AC-A GREEN/YELLOW/RED thresholds. K-floor +1 firm.
- **M-R2-2c.3 (AC-C verdict-token enum):** AC-C test sharpened â€” replace â‰¥50-char body check with: each agent sub-header section contains exactly one line matching `^Verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED|ABSTAIN)$` AND section body â‰¥150 chars excluding that line.
- **M-R3-2c.3 (4-enum verdict regex audit):** AC-A verdict-band regex AND AC-C verdict-token regex BOTH whitelist CONDITIONAL-GREEN explicitly. Spec audit applied below at AC-A + AC-C.
- **M-R4-2c.3 (T_first_real_artifact semantic pin):** Decision #2 footnote â€” `T_first_real_artifact â‰¡ wall-clock instant LIVE_ARTIFACT_METADATA.md is written-to-disk with all required schema fields populated, after artifact-assembly returns success exit code. Operator-validation is a downstream gate, not included in time-to-deploy budget.`
- **M-R5-2c.3 (K-floor disclosure rewording):** Reframed honestly â€” "5 firm + 1 conditional-rider-absorbed-via-AC-C-verdict-line = 6, exactly target. No padding."

**Predecessor dependencies (HARD):**
- Story 2c.1 must be `done` with diff-evidence Markdown landed at `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md` (per 2c.1 AC-G PERSISTENT artifact).
- Story 2c.2 must be `done` with sanctum populated + L5/L6 expertise wired + live artifact landed in `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/` (per 2c.2 AC-D-OP).
- **Soft fallback:** if 2c.2 AC-D-OP is `DEFERRED-PENDING-OPERATOR-WINDOW` at 2c.3 open, 2c.3 may still proceed with **PARTIAL-VERDICT** at AC-D (see AC-D-PARTIAL clause below); M2 verdict transitions GREEN-LIGHT â†’ CONDITIONAL-GREEN with `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` deferred-inventory entry.

---

## T1 Readiness Block

**Before writing any code or measurement-evidence rollup**, the dev agent reads in order:

### Standing Pre-Flight items

1. **Governance lookup** â€” `docs/dev-guide/migration-story-governance.json` confirms `2c-3.expected_gate_mode = "single-gate"` (rationale: null). Do not relitigate.
2. **Predecessor close evidence** â€” Stories 2c.1 + 2c.2 expected `done` per sprint-status.yaml. Verify via `grep "2c-1.*done\|2c-2.*done" sprint-status.yaml` before proceeding. If either is `in-progress` or `ready-for-dev`, abort 2c.3 and surface to operator.
3. **2c.1 diff-evidence anchor** â€” `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md` (per 2c.1 AC-G PERSISTENT contract). Verify present + structurally valid (parses as Markdown + has expected sections per 2c.1 AC-C two-tier diff format).
4. **2c.2 live-artifact anchor** â€” `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/<sha256>.mp3` + `LIVE_ARTIFACT_METADATA.md` companion (per 2c.2 AC-D-OP). Verify present OR confirm DEFERRED-PENDING-OPERATOR-WINDOW state from 2c.2 close notes (triggers AC-D-PARTIAL).
5. **2c.1 + 2c.2 timer evidence** â€” Dev Agent Records of 2c.1 (T8 STRUCTURED TIMER TABLE per Murat M-R3) + 2c.2 (T8 measurement evidence). Verify the timestamp tables are populated.
6. **TEMPLATE doc** â€” [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v2.4 R1â€“R14. Most rules N/A (no migration in scope; this is measurement + verdict). Applicable: R1 bounded scope; R6 framework drift (none expected); R8 K-floor recalibration.
7. **Party-mode roster pin** â€” Epic 2c.3 binding requires Winston + Murat + Paige + Quinn-R + Amelia (5 voices). Roster is HARD; do NOT substitute.
8. **Severance posture** â€” hybrid working tree is sole input surface.
9. **Invariant-stub anchor (NARROWED per A-R1 BLOCKER B1):** No `15-invariant-audit-matrix.md` exists in repo (verified 2026-04-26). Matrix creation deferred to **Slab 5a "Invariant Audit" epic** per epic spec. 2c.3 produces a `slab-2c-wondercraft-invariant-stub.md` 2-row stub artifact instead, which Slab 5a absorbs. NO matrix backfill in scope for 2c.3.

### Slab 2c.3 artifact-existence sweep (5-point)

- **A** `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md` exists (per 2c.1 AC-G).
- **B** `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/<sha256>.mp3` exists OR 2c.2 AC-D-OP DEFERRED state confirmed in 2c.2 Completion Notes.
- **C** `_bmad/memory/wanda-sidecar/` populated per 2c.2 AC-A close + operator-content-population per A-R5-2c.2.
- **D** `app/specialists/wanda/graph.py` `WANDA_REFERENCES` is 14-tuple post-2c.2 AC-B.
- **E** Sprint-status.yaml has `migration-2c-1-...: done` AND `migration-2c-2-...: done`.

### Epic-doc-vs-evidence cross-check (per R6)

#### (a) Framework drifts

**NONE expected at 2c.3.** Story is pure measurement + verdict; no code substrate touched.

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** scope is (a) time-to-deploy roll-up across 2c.1 + 2c.2 timer evidence; (b) 5-agent party-mode convene + verdict recording; (c) 15-invariant audit matrix Wondercraft entries (FR63 incremental roll-up); (d) M2 verdict artifact at `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`. NOT in scope: re-running 2c.1 or 2c.2 measurements; modifying Wanda runtime; producing additional live artifacts; re-litigating Path A vs Path B decision.

**Decision #2 â€” Time-to-deploy roll-up methodology:** roll-up ANCHORS on **2c.1 T0 â†’ 2c.2 first-real-artifact** end-to-end window. The 2c.1 T0 timestamp is the dev-story-open anchor (per 2c.1 AC-E); 2c.2 first-real-artifact is the operator-paste timestamp (per 2c.2 AC-D-OP LIVE_ARTIFACT_METADATA.md `end_timestamp`). Active dev-work hours computed by SUMMING active intervals from 2c.1 + 2c.2 STRUCTURED TIMER tables (excluding paused intervals per Murat M-R3 sub-table convention). Per epic 2c.3 binding: â‰¤1 dev-day = â‰¤8 active clock hours.

> **Semantic pin per Murat M-R4-2c.3 (binding):** `T_first_real_artifact â‰¡ wall-clock instant LIVE_ARTIFACT_METADATA.md is written-to-disk with all required schema fields populated, after artifact-assembly returns success exit code.` Operator-validation (e.g., listening to MP3, judging quality) is a downstream gate and is **NOT** included in the time-to-deploy budget. This pin prevents M2 re-litigation 6 months later when "what counted as first-real-artifact?" surfaces.

**Decision #3 â€” PARTIAL-VERDICT path if 2c.2 AC-D-OP defers:** if 2c.2 closed with AC-D-OP DEFERRED, 2c.3 cannot fully measure end-to-end time-to-deploy. **PARTIAL-VERDICT clause activates at AC-D-PARTIAL:** measure 2c.1 T0 â†’ 2c.2 dev-story-close; party-mode verdict transitions to CONDITIONAL-GREEN with the 2c.2 deferred operator-window as the conditional resolution gate. M2 closes "conditionally" at 2c.3 close; FULL M2 closure pending operator-window completion + addendum at `slab-2c-m2-acceptance-verdict.md` Â§"Operator-Window Addendum."

**Decision #4 â€” Party-mode artifact persistence:** 5-agent party-mode verdict + each agent's individual response recorded VERBATIM in `slab-2c-m2-acceptance-verdict.md`. Do NOT summarize â€” full verbatim per agent so the verdict is traceable and any future M2 retrospection can audit the consensus path.

---

## Story

As an **operator validating the M2 plug-and-play innovation claim**,
I want **end-to-end time-to-deploy measurement (2c.1 T0 â†’ 2c.2 first-real-artifact) rolled up from STRUCTURED TIMER evidence + a 5-agent party-mode (Winston + Murat + Paige + Quinn-R + Amelia) verdict recorded verbatim + 15-invariant audit matrix Wondercraft entries (FR63 incremental roll-up) + M2 GREEN-LIGHT (or CONDITIONAL-GREEN if 2c.2 AC-D-OP deferred) verdict-recording artifact at `slab-2c-m2-acceptance-verdict.md`**,
So that **M2 Required Evidence "Wondercraft time-from-open to first-real-artifact < 1 dev-day" + "Plug-and-play specialist claim validated" has its defensible measurement + recorded multi-agent consensus verdict supporting the milestone close**.

---

## Acceptance Criteria

All ACs are dev-agent-executable except AC-2c.3-C (party-mode convene with 5 named agents â€” runs through bmad-party-mode skill). Sandbox-AC compliant.

### AC-2c.3-A â€” Time-to-deploy roll-up table assembled

- **Given** 2c.1 + 2c.2 Dev Agent Record T8 STRUCTURED TIMER tables are populated (per 2c.1 M-R3 + 2c.2 M-R3 inheritance)
- **When** the dev agent assembles the roll-up table at `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md` Â§"Time-to-Deploy Measurement"
- **Then** the table includes:
  | Anchor | Source | Timestamp | Cumulative Active Hours from 2c.1 T0 |
  |---|---|---|---|
  | T_2c1_open | 2c.1 Dev Agent Record T8 | (paste from 2c.1) | 0.00 |
  | T_2c1_emit | 2c.1 Dev Agent Record T8 | (paste; â‰¤30 sec from T0) | (computed) |
  | T_2c1_conformance_green | 2c.1 Dev Agent Record T8 | (paste; â‰¤5 min from T0) | (computed) |
  | T_2c1_diff_evidence | 2c.1 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c1_dev_close | 2c.1 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c2_open | 2c.2 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c2_sanctum_populated | 2c.2 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c2_l5_authored | 2c.2 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c2_l6_authored | 2c.2 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c2_live_test_authored | 2c.2 Dev Agent Record T8 | (paste) | (computed) |
  | T_2c2_dev_close | 2c.2 Dev Agent Record T8 | (paste) | (computed) |
  | **T_first_real_artifact** | 2c.2 LIVE_ARTIFACT_METADATA.md `end_timestamp` | (paste OR DEFERRED-OPERATOR-WINDOW) | **(computed; KEY METRIC)** |
- **And** total active-clock-hours computed as SUM of (T_anchor[i+1] - T_anchor[i]) excluding paused intervals from 2c.1 + 2c.2 sub-tables.
- **And** measurement compared against epic 2c.3 binding: **â‰¤1 dev-day = â‰¤8 active clock hours**. Verdict per (4-enum band per Murat M-R3 audit):
  - **GREEN-LIGHT:** â‰¤6 hours (well within budget)
  - **YELLOW:** 6-8 hours (within budget; tight)
  - **RED:** >8 hours (over budget; root-cause documented in Â§"Time-to-Deploy Overrun RCA" + filed as `2c-3-time-to-deploy-overrun-rca` follow-on)
  - **CONDITIONAL-GREEN:** verdict of GREEN-LIGHT for dev-cycle window but T_first_real_artifact deferred per AC-D-PARTIAL (DEFERRED-PENDING-OPERATOR-WINDOW); time-to-deploy budget verdict is conditional on operator-window addendum
- **Test pin per Murat M-R1-2c.3 (strengthened from structural smoke to math-asserting):** `tests/migration/test_slab_2c_m2_verdict_artifact_present.py` â€” 1 test asserting:
  1. `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md` exists.
  2. Â§"Time-to-Deploy Measurement" section header present.
  3. Filled-in row count â‰¥ 12 in the time-to-deploy table (or â‰¥ 11 + `T_first_real_artifact` row marked `DEFERRED-PENDING-OPERATOR-WINDOW` if AC-D-PARTIAL active).
  4. **MATH ASSERTION (M-R1):** parse the table; sum the per-row active-hour deltas (excluding rows with paused-interval markers); assert the cumulative-hours value at the bottom of the table is within Â±0.1h tolerance of the computed sum.
  5. **VERDICT-BAND ASSERTION (M-R1):** parse the verdict-band line at top of Â§"M2 Required Evidence Summary"; assert it matches the band the cumulative-hours value falls into per the GREEN-LIGHT/YELLOW/RED/CONDITIONAL-GREEN thresholds (4-enum regex per M-R3 audit).

### AC-2c.3-B â€” Time-to-deploy verdict line + cost-summary line

- **Given** AC-A roll-up table assembled
- **When** dev agent appends to `slab-2c-m2-acceptance-verdict.md` Â§"M2 Required Evidence Summary":
  - **Time-to-deploy verdict:** GREEN / YELLOW / RED per AC-A bands; total active-clock-hours numeric value
  - **Cost summary:** 2c.1 AC-B-OP smoke-test ($0.00 to $0.50 actual) + 2c.2 AC-D-OP production-quality ($X.XX actual per Wondercraft response, scripted OR simple-fallback per A-R4-2c.2 enum); cumulative cost â‰¤ $5.50 if scripted-path; â‰¤ $2.50 if simple-fallback-path
  - **Diff-evidence verdict:** PASS (â‰¥60% file-presence + â‰¥40% skeleton-line per 2c.1 AC-C two-tier) / FAIL with score values
  - **Conformance-green verdict:** PASS (auto-discovery picked up `wanda_validation` with ZERO framework changes per 2c.1 AC-B + Wanda passes 14-rule conformance per 2b.8 close) / FAIL
- **Test pin:** `tests/migration/test_slab_2c_m2_required_evidence_section_complete.py` â€” 1 test asserting Â§"M2 Required Evidence Summary" exists + contains the 4 required verdict lines (regex-pinned: `^Time-to-deploy verdict:`, `^Cost summary:`, `^Diff-evidence verdict:`, `^Conformance-green verdict:`); time-to-deploy verdict line whitelist matches `(GREEN-LIGHT|CONDITIONAL-GREEN|YELLOW|RED)` per M-R3 4-enum audit.

### AC-2c.3-C â€” 5-agent party-mode convene + verbatim verdict recording

- **Given** the bmad-party-mode skill is available (`.claude/skills/bmad-party-mode/`); roster pinned to **Winston (architect) + Murat (test architect) + Paige (tech writer) + Quinn-R (quality reviewer) + Amelia (dev)**
- **And** T1 sub-task per A-R5-2c.3 has verified each named agent has voice on M2-acceptance question (Quinn-R may legitimately respond ABSTAIN if "outside lane"; 4-of-5 consensus path is valid per Decision #4; not a defect)
- **When** the dev agent (or operator) executes the explicit T-task sequence per A-R4-2c.3:
  1. Invoke `bmad-party-mode` skill with the AC-C-specified prompt + 5-agent roster
  2. Capture each subagent's full text response from the tool result
  3. Write each verbatim into `slab-2c-m2-acceptance-verdict.md` under `### <agent>` headers
  4. Synthesize consensus verdict line from the 5 individual verdicts
- **And** the convene prompt: "M2 acceptance verdict review for Slab 2c (Wondercraft Pilot + Generator Validation). Full evidence: 2c.1 diff-evidence Markdown + 2c.2 live artifact + 2c.3 time-to-deploy roll-up table at `slab-2c-m2-acceptance-verdict.md`. Verdict (one of 6 enum tokens): GREEN-LIGHT / GREEN-WITH-RIDERS / CONDITIONAL-GREEN (if 2c.2 deferred) / YELLOW (issues) / RED (cannot close) / ABSTAIN (outside lane). Each agent: verdict-token-on-its-own-line in format `Verdict: <TOKEN>` + reasoning + any riders. Roster fixed at 5; do not add or substitute."
- **Then** each agent's response is recorded **verbatim** in `slab-2c-m2-acceptance-verdict.md` Â§"Party-Mode Verdict (5 agents)" under sub-headers `### Winston`, `### Murat`, `### Paige`, `### Quinn-R`, `### Amelia` per Decision #4. **Do NOT summarize.**
- **And** consensus verdict recorded at top of Â§"Party-Mode Verdict" matching `^Consensus verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED)$` (4-enum decision band per Murat M-R3 audit; ABSTAIN is per-agent only, not a consensus-level verdict) with vote breakdown per agent.
- **And** any agent-named riders aggregated under Â§"Riders" with `<agent>-R<n>-2c.3` notation; each rider classified as (a) APPLIES-TO-2c.3-CLOSE (resolve before close), (b) APPLIES-TO-2c.4 (defer to slab-close story), (c) DEFERRED-INVENTORY (file as follow-on).
- **Test pin per Murat M-R2-2c.3 (sharpened from â‰¥50-char weak check to verdict-token-enum + 150-char body):** `tests/migration/test_slab_2c_m2_party_mode_5_agent_recording.py` â€” 1 test asserting:
  1. Â§"Party-Mode Verdict (5 agents)" section exists.
  2. Sub-headers `### Winston`, `### Murat`, `### Paige`, `### Quinn-R`, `### Amelia` all present.
  3. **VERDICT-TOKEN ASSERTION (M-R2):** each agent sub-header section contains exactly ONE line matching `^Verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED|ABSTAIN)$` (6-enum per-agent).
  4. **BODY-LENGTH ASSERTION (M-R2):** each sub-header section body â‰¥150 chars EXCLUDING the verdict-token line (deterministic; no LLM-output semantic-content assertion).
  5. Consensus verdict line at top of Â§"Party-Mode Verdict" matches `^Consensus verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED)$` (4-enum consensus-level).

### AC-2c.3-D â€” Wondercraft invariant-stub artifact for Slab 5a absorption (NARROWED per A-R1 BLOCKER B1)

- **Given** no `15-invariant-audit-matrix.md` exists in repo (verified 2026-04-26); matrix creation deferred to Slab 5a "Invariant Audit" epic per epic spec
- **When** the dev agent authors `_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md`
- **Then** the file contains 2 row-stubs (one per Wondercraft specialist) with the metadata Slab 5a will need to absorb at matrix creation time:
  - **`wanda`** (production specialist; Path A; closed 2b.8 + 2c.2): specialist-name, slab-of-origin (`2b.8`), shape-category (`Â§12.11 REST-API tool-dispatch inheritor`), expertise-tier (`L4-podcast-production` extended to L5 at 2c.2), sanctum-status (`populated 2c.2`), live-API-status (`exercised 2c.2 AC-D-OP` OR `DEFERRED-PENDING-OPERATOR-WINDOW`), evidence-anchor (`2c.2 LIVE_ARTIFACT_METADATA.md`)
  - **`wanda_validation`** (transient validation tree; Path B; closed 2c.1 then retired): specialist-name, slab-of-origin (`2c.1`), shape-category (`Â§12.11 REST-API tool-dispatch via generator`), expertise-tier (`L5-podcast-production stub`), retirement-disposition (`retired-to-fixtures at tests/fixtures/generator_validation/wanda_baseline/2026-04-25/`), evidence-anchor (`2c-1-wondercraft-path-b-diff-evidence.md`)
- **And** the file headers note "STUB FOR SLAB 5A INVARIANT AUDIT EPIC ABSORPTION â€” created 2c.3 to capture Wondercraft-specific facts at M2 close before Slab 5a matrix creation."
- **Test pin:** `tests/migration/test_slab_2c_m2_wondercraft_invariant_stub.py` â€” 1 test asserting `_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md` exists + contains rows for both `wanda` and `wanda_validation` + each row has the 6-7 metadata fields populated above.

### AC-2c.3-D-PARTIAL â€” Conditional-green path if 2c.2 AC-D-OP defers

- **Given** 2c.2 closed with AC-D-OP DEFERRED-PENDING-OPERATOR-WINDOW (no live artifact yet); per Decision #3 PARTIAL-VERDICT clause
- **When** 2c.3 proceeds with partial measurement
- **Then**:
  - AC-A T_first_real_artifact row marked `DEFERRED-PENDING-OPERATOR-WINDOW`; total active-clock-hours computed using T_2c2_dev_close as terminal anchor instead of T_first_real_artifact (call it `T_partial_close`)
  - AC-B time-to-deploy verdict uses `CONDITIONAL-GREEN` enum token (no `PARTIAL-` prefix; CONDITIONAL-GREEN is the dedicated 4-enum slot per M-R3 audit)
  - AC-C party-mode prompt amended to "verdict CONDITIONAL-GREEN expected pending 2c.2 AC-D-OP completion"
  - AC-C consensus verdict transitions GREEN-LIGHT â†’ CONDITIONAL-GREEN
  - **Auto-file follow-on:** `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` in deferred-inventory; reactivation gate "operator completes 2c.2 AC-D-OP and pastes addendum to slab-2c-m2-acceptance-verdict.md Â§Operator-Window Addendum"
  - **Hard-gate clause per A-R6-2c.3 (BINDING):** if Slab 2c.4 SLAB-CLOSING reaches dev-close before operator-window completes, Slab 2c closes as `CLOSED-WITH-CONDITIONAL-M2`, **NOT** `CLOSED-GREEN`. M2 milestone remains `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` until operator pastes addendum to `slab-2c-m2-acceptance-verdict.md` Â§"Operator-Window Addendum" + dev runs `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` reactivation cleanup. Slab 2 (parent) closes as `CLOSED-WITH-CONDITIONAL-M2` if Slab 2c carries that state through close.
  - Slab 2c.4 SLAB-CLOSING inherits the conditional-resolution responsibility (verifies addendum landed before D12 close protocol; honors hard-gate above).
- **Test pin:** None new â€” AC-D-PARTIAL is a conditional branch of AC-A through AC-C ACs; the AC-A and AC-C verdict-band/verdict-token regexes BOTH whitelist `CONDITIONAL-GREEN` per M-R3 4-enum audit (verified inline in AC-A point 5 + AC-C point 5).

### AC-2c.3-E â€” Anti-pattern catalog harvest (per R6)

- **Given** the catalog is final-form post-2b.17 with A1â€“A13
- **When** 2c.3 close runs
- **Then** **NO new anti-pattern signals expected** at this story (measurement + verdict-recording is mechanical). If party-mode round at AC-C surfaces a candidate (e.g., "deferred-OP cascade leaks across stories" or "M2 verdict format ambiguity"), file as candidate A14 anti-pattern and consult party-mode for inclusion vs. defer to 2c.4 final harvest.

### AC-2c.3-F â€” TEMPLATE compliance (per R1â€“R14 v2.4)

R1â€“R14 v2.4 honored where applicable. **Most rules N/A** (no migration; this is measurement + verdict recording). Applicable: R1 bounded scope (Decision #1); R6 framework-drift harvest (none expected at this story per (a) above); R8 K-floor recalibration (~1.2Ã— = target 6 / floor 5 honored).

### AC-2c.3-G â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** No code substrate touched at 2c.3; only documentation evidence + audit-matrix entries; FR63 incremental roll-up validated.
2. **Anti-pattern harvest:** N/A unless surfaced (per AC-E).
3. **Migration-guide update:** none direct; `slab-2c-m2-acceptance-verdict.md` becomes the M2 evidence anchor referenced by Slab-2 retrospective at 2c.4 close.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors recorded: total-active-clock-hours from 2c.1 T0 to T_first_real_artifact (or T_partial_close); cost-summary cumulative; conformance-green PASS; diff-evidence two-tier scores.

### AC-2c.3-H â€” Sprint-status state-flips at filing AND at close

At filing: `migration-2c-3-time-to-deploy-measurement-and-party-mode-validation: ready-for-dev`. At close: `migration-2c-3-...: done`; epic stays `in-progress` (closes at 2c.4 SLAB-CLOSING). `last_updated` field updated.

---

## File Structure Requirements

### NEW files (PERSISTENT)

```
_bmad-output/implementation-artifacts/
â”œâ”€â”€ slab-2c-m2-acceptance-verdict.md             # M2 verdict-recording artifact (NEW per AC-A/B/C)
â””â”€â”€ slab-2c-wondercraft-invariant-stub.md        # 2-row stub for Slab 5a absorption (NEW per AC-D)

tests/migration/                                  # FLAT layout per Amelia A-R3 BLOCKER B3 (no slab_2c/ subdir)
â”œâ”€â”€ test_slab_2c_m2_verdict_artifact_present.py            # 1 test (AC-A; math + verdict-band assertions per M-R1)
â”œâ”€â”€ test_slab_2c_m2_required_evidence_section_complete.py  # 1 test (AC-B; 4-line regex + 4-enum verdict)
â”œâ”€â”€ test_slab_2c_m2_party_mode_5_agent_recording.py        # 1 test (AC-C; verdict-token enum + 150-char body per M-R2)
â””â”€â”€ test_slab_2c_m2_wondercraft_invariant_stub.py          # 1 test (AC-D; 2-row stub presence + metadata fields)
```

### MODIFIED files

- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-H.
- `_bmad-output/planning-artifacts/deferred-inventory.md` â€” `2c-3-time-to-deploy-overrun-rca` filed if AC-A verdict RED. `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` auto-filed if AC-D-PARTIAL fires.

### NOT modified (per A-R1 BLOCKER B1 RESOLVED-BY-DEFERRAL)

- No `15-invariant-audit-matrix.md` exists; matrix creation is **Slab 5a "Invariant Audit" epic** scope, not 2c.3. 2c.3 produces `slab-2c-wondercraft-invariant-stub.md` for Slab 5a absorption only.

### NOT modified

- Wanda runtime (`app/specialists/wanda/`) â€” DO NOT TOUCH (2c.2 close pin).
- 2c.1 diff-evidence Markdown â€” READ-ONLY input (per 2c.1 AC-G PERSISTENT contract).
- 2c.2 live artifact + LIVE_ARTIFACT_METADATA.md â€” READ-ONLY input.
- Generator (`skills/bmad_create_specialist/`) â€” DO NOT TOUCH (2c.4 polish-scope).
- All 14 other specialist runtimes â€” out of scope.

---

## Testing Requirements

**K-target ~1.2Ã— (target 6 / floor 5).** Test count and K-floor accounting per Murat M-R18 honest-count + M-R5-2c.3 rewording:

| AC | Test | Honest K-floor units |
|---|---|---|
| A | `test_slab_2c_m2_verdict_artifact_present.py` (5 assertion-bullets: file exists + section header + row count + math assertion + verdict-band assertion per M-R1) | **2** (file/structure + math + verdict-band-correctness are 2 orthogonal properties; structure is 1 unit, math+band-correctness collapse to 1 unit per AC) |
| B | `test_slab_2c_m2_required_evidence_section_complete.py` (4-regex-pin + 4-enum verdict line) | **1** |
| C | `test_slab_2c_m2_party_mode_5_agent_recording.py` (5 assertion-bullets: section + sub-headers + verdict-token-enum + body-length + consensus-line per M-R2) | **2** (structure + verdict-token-enum are 2 orthogonal properties) |
| D | `test_slab_2c_m2_wondercraft_invariant_stub.py` (file present + 2 rows + metadata fields) | **1** |
| **Total** | **4 collected at file level** | **6 K-floor units (5 firm + 1 from M-R1 verdict-band-correctness which is independently falsifiable)** |

**Honest K-floor: 6** at target. M-R1's math + verdict-band assertions are independently falsifiable (the math can be wrong while the structure is correct, and vice versa) and legitimately count as separate K-floor units within the same test file per M-R18 multi-property-per-test convention. M-R2's verdict-token-enum is similarly orthogonal to the structural section presence. **No padding; not borderline.** Per Murat M-R5-2c.3: "5 firm + 1 conditional-rider-absorbed-via-AC-C-verdict-line = 6, exactly target."

**Regression target at T8:** â‰¥562 passed / â‰¥7 skipped placeholder-key (Slab 2b close baseline preserved); +4 collected at file level. Import-linter 3/3 KEPT throughout. Ruff clean. Sandbox-AC PASS (no live API calls in 2c.3 dev-agent ACs; reads from 2c.1 + 2c.2 evidence files only).

---

## Dev Agent Record

_(Populated during T1â€“T9 execution.)_

### T1 Readiness

- 2026-04-26: Loaded BMAD config, `CLAUDE.md`, project context, full 2c.3 spec, sprint status, governance JSON, 2c.1 diff-evidence anchor, 2c.1 and 2c.2 close records, Wanda runtime, Wanda sidecar, L5 reference tuple, and party-mode roster requirements.
- Predecessor gate passed: sprint status has `migration-2c-1...: done` and `migration-2c-2...: done`; commits `6ddf338` and `ecf2f47` landed.
- Artifact sweep passed: 2c.1 diff evidence exists; Wanda sidecar exists; `WANDA_REFERENCES` has 14 entries; no live Wanda MP3 or `LIVE_ARTIFACT_METADATA.md` exists because 2c.2 AC-D-OP is explicitly DEFERRED-PENDING-OPERATOR-WINDOW.
- Conditional branch active: AC-D-PARTIAL applies; M2 verdict path is `CONDITIONAL-GREEN` pending operator live artifact addendum.
- Invariant-matrix check passed: no `15-invariant-audit-matrix.md` exists; 2c.3 will emit only the Slab 5a absorption stub.
- Party roster viability confirmed: Winston, Murat, Paige, Quinn-R, and Amelia all have an M2 acceptance-review lane; Quinn-R may abstain without invalidating 4-of-5 consensus.
- Sandbox-AC validator passed: `.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2c-3-time-to-deploy-measurement-and-party-mode-validation.md`.
- T1 disposition: PASS; no halt condition.

### T2-T7 Implementation Notes

- AC-A/AC-B: Authored `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md` with conditional time-to-deploy roll-up, required evidence summary, cost/diff/conformance lines, and T_first_real_artifact marked DEFERRED-PENDING-OPERATOR-WINDOW.
- AC-C: Convened five parallel party-mode reviews for Winston, Murat, Paige, Quinn-R, and Amelia; all returned `CONDITIONAL-GREEN`. Each response is preserved in the verdict artifact under the required agent headers.
- AC-D: Authored `_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md` with `wanda` and `wanda_validation` rows for Slab 5a absorption.
- AC-D-PARTIAL: Filed `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` in deferred inventory. M2 remains conditional pending 2c.2 live artifact and operator addendum.
- AC-E/AC-F/AC-G: No new anti-pattern harvested; TEMPLATE R1/R6/R8 honored; no runtime code touched.

### T8 Roll-up Evidence + Party-Mode Convene Log

- PASS: `.venv\Scripts\python.exe -m pytest tests/migration -k slab_2c_m2 -q` -> 4 passed, 48 deselected.
- PASS: scoped ruff over the four new `tests/migration/test_slab_2c_m2_*.py` files.
- PASS: `.venv\Scripts\python.exe -m pytest tests/integration/scaffold_conformance/ -q` -> 58 passed.
- PASS: `.venv\Scripts\lint-imports.exe --config pyproject.toml` -> 3/3 contracts KEPT.
- PASS: sandbox-AC validator for 2c.3.
- PARTY-MODE: Winston, Murat, Paige, Quinn-R, and Amelia all returned `CONDITIONAL-GREEN`; common rider is that Slab 2c must not claim full green until 2c.2 live artifact, metadata, sha256 round-trip, and operator addendum land.
- OPERATOR-ACCEPTED BASELINE DRIFT: `.venv\Scripts\python.exe -m pytest -q --tb=short` still fails during collection on pre-existing pipeline-manifest schema errors and missing `marcus.dispatch.contract` imports in Texas legacy tests.
- OPERATOR-ACCEPTED BASELINE DRIFT: `.venv\Scripts\python.exe -m ruff check app/ tests/ skills/ scripts/` still reports the broad pre-existing lint backlog outside the 2c.3 diff.
- TOOLING DRIFT: `.venv\Scripts\python.exe -m lint_imports --config pyproject.toml` fails because `lint_imports` is not an importable module; executable form passes.

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

- Blind Hunter: 2c.3 touches only evidence/docs/tests/status; no Wanda runtime, generator, or dispatch substrate changed.
- Edge Case Hunter: verdict tests cover conditional enum, row math, required evidence lines, five party-mode sections, per-agent verdict tokens, and invariant stub rows.
- Acceptance Auditor: AC-A through AC-H satisfied under AC-D-PARTIAL; conditional follow-on filed and the hard gate is explicit in the verdict artifact.
- `bmad-code-review` scoped result: no MUST-FIX findings in the 2c.3 diff. Residual risk is intentionally carried as `CONDITIONAL-GREEN` pending operator live artifact addendum.

### D12 Close Stub

1. **Invariant preservation:** No code substrate touched at 2c.3; only evidence artifacts, tests, deferred inventory, and status files changed.
2. **Anti-pattern harvest:** N/A; conditional live-artifact state is tracked as deferred inventory and a 2c.4 hard-gate rider.
3. **Migration-guide update:** None direct; `slab-2c-m2-acceptance-verdict.md` is the M2 evidence anchor for 2c.4 slab close.
4. **TEMPLATE compliance:** R1, R6, and R8 honored; total active-clock-hours recorded as 1.50 partial hours with M2 verdict `CONDITIONAL-GREEN`.

### Completion Notes

- BMAD-CLOSED 2026-04-26T01:31:03-04:00. M2 verdict artifact is complete with unanimous five-agent `CONDITIONAL-GREEN` verdict.
- `T_first_real_artifact` remains DEFERRED-PENDING-OPERATOR-WINDOW because 2c.2 AC-D-OP did not run; M2 milestone is `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM`.
- `slab-2c-wondercraft-invariant-stub.md` is ready for Slab 5a invariant audit absorption.
- Deferred-inventory count is now 34 named follow-ons after the 2c.3 conditional verdict entry.

### File List

- `_bmad-output/implementation-artifacts/migration-2c-3-time-to-deploy-measurement-and-party-mode-validation.md`
- `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`
- `_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `tests/migration/test_slab_2c_m2_verdict_artifact_present.py`
- `tests/migration/test_slab_2c_m2_required_evidence_section_complete.py`
- `tests/migration/test_slab_2c_m2_party_mode_5_agent_recording.py`
- `tests/migration/test_slab_2c_m2_wondercraft_invariant_stub.py`