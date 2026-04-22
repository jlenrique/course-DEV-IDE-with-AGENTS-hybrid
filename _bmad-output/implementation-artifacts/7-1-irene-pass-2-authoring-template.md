# Story §7.1: Irene Pass 2 Authoring Template (Schema-Validated Emission + Fail-Closed Lint)

**Status:** ready-for-dev (green-lit 2026-04-22 — riders applied below)
**Created:** 2026-04-22
**Epic:** Sprint #1 standalone story (Irene Pass 2 contract hardening — likely future Epic 23-extension "Irene Output Discipline")
**Sprint key:** `7-1-irene-pass-2-authoring-template`
**Sprint:** Sprint #1 (1 of 5 — opens POSITION 1 per D7 sequencing; trial-#2 blocker)
**Priority:** **HIGH** — "single highest-friction step in the pipeline this run" per trial reproducibility report §7.1 (2026-04-21).
**Points:** **3 pts firm** (ratified at green-light: 2 worked examples per Paige; cross-artifact fixture + happy-path atom per Murat; upstream-reference cross-validation retained per AC-B.3)
**Depends on:** None hard. Builds on existing `segment-manifest` schema (from Epic 23 / Wave 3) + existing Irene Pass 2 procedure reference. Implicit dependency on motion-walk artifact for §6.3 / §6.4 / §6.5 failure-mode test fixtures.
**Blocks:** Next Pass 2 run on any lesson (per reproducibility report trigger: "before next Pass 2 run on any lesson").
**Coordinates with:** Irene retrieval-intake (sibling Sprint #1 story — the intake contract extends Irene's Pass 2 emission surface; templates should cover intake-consuming narration segments).

## TL;DR

- **What:** Ship an **Irene Pass 2 authoring template** — a schema-validated emission contract + fail-closed lint that Pass 2 output MUST pass before Storyboard B rendering. Closes the three concrete failure modes harvested from trial `C1-M1-PRES-20260419B` (§7.1 of reproducibility report).
- **Why:** Pass 2 emission is the pipeline's single highest-friction step. Trial #1 lost material time to three distinct emission bugs that a schema + lint would catch in seconds. Every future Pass 2 run without this template will rediscover the same class of bugs.
- **Three concrete failure modes (from reproducibility report §7.1):**
  1. **§6.3** — Irene emitted BOTH `motion_asset` AND `motion_asset_path` keys (duplicate). Downstream tooling was ambiguous about which to honor. Durable fix: Pass 2 template emits ONLY `motion_asset_path`.
  2. **§6.4** — `visual_file` was missing on 13/14 segments (back-filled at §14 Compositor). Durable fix: Pass 2 MUST populate `visual_file` at emission, NOT at §14 back-fill.
  3. **§6.5** — `motion_duration_seconds` was null even though Motion Gate (§05) already captured it. Durable fix: Pass 2 carries the field forward from Motion Gate receipt, NOT null.
- **Novelty:** This story delivers the AUTHORING TEMPLATE + LINT discipline. Not Irene's cognitive / creative logic (still agent-driven). The template is the structural contract Pass 2 output conforms to.
- **Size:** 3–5 pts (scope-bounded at green-light).

## Background — Why This Story Exists

**Trial `C1-M1-PRES-20260419B` §6 fix-on-the-fly log:**

| Failure | Root cause | Fix-on-the-fly | Durable disposition |
|---------|------------|----------------|---------------------|
| §6.3 duplicate motion_asset keys | Irene Pass 2 emitted BOTH `motion_asset` (legacy) + `motion_asset_path` (canonical) | Marcus de-duplicated inline | Pass 2 template emits only `motion_asset_path` |
| §6.4 missing visual_file on 13/14 segments | Irene Pass 2 emitted visuals mostly as URL references without populating `visual_file` | §14 Compositor back-filled from gates | Pass 2 MUST populate `visual_file` at emission |
| §6.5 null motion_duration_seconds | Irene Pass 2 emitted null despite Motion Gate providing the value | Compositor reconstructed from motion receipts | Pass 2 carries it forward from Motion Gate receipt |

**Why a schema + lint is the right fix:** all three failures are STRUCTURAL — the schema can deterministically flag them. Irene's Pass 2 creative output (narration prose, segment ordering, behavioral-intent subordination) is NOT in scope for the template — creative-layer outputs remain LLM-driven + reviewed via Quinn-R / Vera. The TEMPLATE is for the structural envelope.

**Trigger:** before next Pass 2 run on any lesson (reproducibility report explicit). This story must land before trial #2 execution.

## Story

As the **Pass 2 author (Irene)** and as **the trial operator running Pass 2 through the pipeline**,
I want **a schema-validated Irene Pass 2 authoring template that lists exactly the fields Pass 2 output must populate, with a fail-closed lint that rejects emissions with duplicate keys, missing required fields, or null fields whose upstream source had values**,
So that **the three trial-#1 failure modes (§6.3 / §6.4 / §6.5) cannot recur silently, AND future Pass 2 runs discover schema-adherence errors in seconds rather than at §14 Compositor assembly, AND Irene's authoring-time discipline is documented in a single template that survives operator onboarding / skill iteration**.

## Acceptance Criteria (spine level — expand at green-light)

### Behavioral (AC-B.*)

1. **AC-B.1 — Authoring template file shipped.** New authoritative file at `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` (or similar location — decide at green-light). Contains:
   - Full `segment-manifest` schema with per-field annotations (REQUIRED / OPTIONAL / DERIVED-FROM-UPSTREAM).
   - Worked example covering a static segment AND a motion segment (both canonical shapes).
   - Explicit "do NOT emit these legacy keys" list (`motion_asset` and any other retired vocabulary).
   - Cross-reference to upstream gates (Motion Gate `motion_duration_seconds`, literal-visual gate `visual_file`, Gate 2 approvals).
2. **AC-B.2 — Segment-manifest schema tightened.** `state/config/schemas/segment-manifest.schema.json` updated to explicitly disallow `motion_asset` (the legacy duplicate); require `visual_file` on every segment with `visual_mode != null`; require `motion_duration_seconds` on every segment with `visual_mode == "video"`. Additive change with enforcement; schema version increment OR additive with strict validator (decide at green-light).
3. **AC-B.3 — Fail-closed Pass 2 lint.** New validator script (location TBD — likely `scripts/validators/pass_2_emission_lint.py`) that runs against any `segment-manifest.yaml` emitted by Irene Pass 2. Exits non-zero with clear error naming the offending segment + field when:
   - Duplicate keys detected (`motion_asset` + `motion_asset_path` coexist).
   - `visual_file` absent on segments with non-null `visual_mode`.
   - `motion_duration_seconds` null on motion segments when upstream Motion Gate receipt has a value (validator cross-references receipt).
4. **AC-B.4 — Pipeline integration.** Pass 2 pipeline wires the lint BEFORE Storyboard B rendering. Pack v4.2 prompt that invokes Pass 2 output-validation step honors lint exit code. Failing lint = blocked promotion to §08 Storyboard B.
5. **AC-B.5 — Worked-example gallery.** Template includes 2-3 worked examples covering (a) static-only deck, (b) motion-enabled deck, (c) retrieval-intake-consuming narration segment (coordination with Irene retrieval-intake sibling story). Each example annotated with "why this is correct" prose.
6. **AC-B.6 — Irene sanctum cross-reference.** Irene's sanctum `INDEX.md` OR relevant capability reference gains a pointer to the new template. First-breath authors land on the template before attempting emission.

### Test (AC-T.*)

1. **AC-T.1 — Schema-validation tests.** Parametrized fixtures covering the three failure modes (§6.3 / §6.4 / §6.5) — each asserts validator rejects the malformed manifest with expected error message prefix.
2. **AC-T.2 — Happy-path validation.** Canonical-shape manifest (trial-#1 post-fix structure) passes validator. Both static-only + motion-enabled variants.
3. **AC-T.3 — Trial-#1-regression fixture.** The actual (post-fix) manifest from trial `C1-M1-PRES-20260419B` passes validator unchanged. Proves the template doesn't regress real-world output.
4. **AC-T.4 — Upstream-reference cross-validation.** Fixture with Motion Gate receipt naming `motion_duration_seconds: 12.3` + manifest segment with same asset_path but null `motion_duration_seconds` → validator rejects with cross-reference-trace error message.
5. **AC-T.5 — Doc-parity lockstep.** Template's schema fields match `segment-manifest.schema.json`. Drift = CI fail (mirrors 27-2 AC-S6 transform-registry lockstep; retrieval-intake sibling story AC-T.5).
6. **AC-T.6 — Pipeline-integration smoke.** Pack v4.2 Pass 2 step invokes lint; lint-fail exit path prevents §08 Storyboard B render. (Integration-level; may be manual or automated — decide at green-light.)
7. **AC-T.7 — Suite regression floor pinned** (TBD at green-light, estimate ≥10 collecting).

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Template is authoring guidance + schema; not code.** Template file is markdown + embedded YAML schema snippets. Lint script is the code-side enforcer. Clean separation.
2. **AC-C.2 — Lint is deterministic.** Pydantic / JSON-schema-validator based; no inference; no LLM-in-the-loop.
3. **AC-C.3 — Schema evolution is versioned.** Any future change to segment-manifest fields requires schema version bump + migration notes (inherit 27-0 SCHEMA_CHANGELOG pattern).
4. **AC-C.4 — Retrofit of existing references coordinated.** Irene's existing `pass-2-procedure.md` + `cluster-head-pass-2.md` + related references are NOT rewritten in this story — they link to the new template where applicable. (Avoids scope creep.)
5. **AC-C.5 — Legacy keys explicitly forbidden.** `motion_asset` (legacy from pre-Storyboard-B era) is the initial list; template maintained as legacy vocabulary grows.

## File Impact (estimated — scope-bounded at green-light)

| File | Change | Lines (est.) |
|------|--------|-------|
| `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` | New — authoring-time template + worked examples | +300 |
| `state/config/schemas/segment-manifest.schema.json` | Touch — tighten field constraints + forbid legacy keys + version bump | +40 |
| `scripts/validators/pass_2_emission_lint.py` | New — fail-closed validator with upstream-reference cross-validation | +250 |
| `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` | Touch — §07 or §08 step invokes the lint before Storyboard B render | +15 |
| `skills/bmad-agent-content-creator/references/pass-2-procedure.md` | Touch — pointer to new template at §emission step (no rewrite) | +5 |
| `skills/bmad-agent-content-creator/INDEX.md` (sanctum) | Touch — add template to first-breath reading list | +3 |
| `tests/fixtures/irene/pass_2_emission/` | New — 5-6 fixtures (3 failure modes + 2 happy-path shapes + 1 trial-#1-regression) | ~6 files, +250 lines YAML |
| `tests/irene/test_pass_2_emission_lint.py` | New — AC-T.1/T.2/T.3/T.4/T.5 | +220 |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | Touch — segment-manifest version bump entry | +15 |

**No changes to:** Irene's cognitive / creative logic (cluster-head authoring, narration prose generation, behavioral-intent subordination); Gary's slide generation; Kira's motion generation; Motion Gate / literal-visual gate logic; §14 Compositor back-fill (will be NEARLY DEAD CODE after template enforcement — but explicitly preserved in-place per AC-C.4 no-retrofit).

## Tasks / Subtasks (spine — expand at green-light)

- [ ] T1 — Harvest trial-#1 fixtures — canonical post-fix manifest + 3 malformed variants (§6.3 / §6.4 / §6.5)
- [ ] T2 — Segment-manifest schema tightening (forbid `motion_asset`; require `visual_file` conditional on `visual_mode`; require `motion_duration_seconds` on motion segments)
- [ ] T3 — Schema version bump + `SCHEMA_CHANGELOG.md` entry
- [ ] T4 — Pass 2 emission lint validator script (deterministic; Pydantic-based)
- [ ] T5 — Upstream-reference cross-validation (Motion Gate receipt → manifest motion_duration_seconds)
- [ ] T6 — Authoring template markdown (full schema + worked examples + legacy-key forbidden list)
- [ ] T7 — Coordinate with Irene retrieval-intake sibling story for the 3rd worked example (retrieval-consuming segment)
- [ ] T8 — Wire lint into v4.2 pack Pass 2 step (blocks §08 Storyboard B on fail)
- [ ] T9 — Reference updates (pass-2-procedure.md pointer + Irene INDEX entry)
- [ ] T10 — Test suite (AC-T.1-T.5 + regression fixtures)
- [ ] T11 — Doc-parity lockstep test (AC-T.5) — may be combined with AC-T.1-T.4
- [ ] T12 — Pipeline-integration smoke (AC-T.6 — manual or automated per green-light)
- [ ] T(final) — Regression + pre-commit + review

## Risks (spine)

| Risk | Mitigation |
|------|------------|
| **Schema tightening breaks pre-existing manifests (e.g., archived trial runs)** | Schema version bump; lint runs only on NEW Pass 2 emissions; archived manifests stay on prior version (per AC-C.3 versioning). |
| **Lint too strict — rejects legitimate Irene creative variations** | Worked examples cover canonical shapes; any creative variation outside canonical shapes requires template update (+ party-mode for significant cases). Error messages reference specific template sections, not black-box rejections. |
| **Upstream-reference cross-validation (AC-B.3 third check) too brittle — Motion Gate receipt format may evolve** | Validator reads Motion Gate receipt via existing stable accessor (not raw file parsing); if receipt format changes, the accessor + this lint update in lockstep. |
| **§14 Compositor still wants to back-fill for safety (belt-and-suspenders)** | AC-C.4 explicitly preserves §14 back-fill code path. Over time the back-fill becomes dead code; removal is a separate follow-on story. |
| **Scope creep — retrofit pass-2-procedure.md + cluster-head-pass-2.md to the new template** | AC-C.4 forbids retrofit in this story; pointer-only updates. Retrofit is a separate follow-on story if operator / Paige deem it worth the scope. |
| **Coordination drift with retrieval-intake sibling story** | 3rd worked example depends on retrieval-intake's contract. If retrieval-intake lands first, this story picks up the contract. If parallel, green-light pins field names + enum values across both. |
| **Template becomes stale as Irene's creative capabilities evolve (Epic 20c / future)** | Version-bump discipline (AC-C.3) + doc-parity lockstep (AC-T.5) + retrospective review as part of every cluster-intelligence iteration. |

## Non-goals

- Changing Irene's cognitive / creative logic (narration prose, segment ordering, behavioral intent, cluster-boundary seams — all remain LLM-driven + Quinn-R/Vera-reviewed).
- Retrofitting existing Irene references (`pass-2-procedure.md`, `cluster-head-pass-2.md`, etc.) beyond pointer updates.
- Removing §14 Compositor back-fill (becomes dead code over time; separate cleanup follow-on).
- LLM-based lint (deterministic schema validation only; AC-C.2).
- Extending template to cover Pass 1 emission (Pass 1 has its own separate concerns; this story is Pass 2 only).
- Creative-layer quality gates (those are Quinn-R / Vera's job; this story is structural only).
- Voice / tone / dial parameters (those are narration-script-parameters.yaml territory; this story is segment-manifest structural only).

## Questions for Green-Light Round

1. **Template location:** `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` vs `docs/workflow/pass-2-authoring-template.md`? Recommend former (specialist-owned reference per skill conventions).
2. **Lint script location:** `scripts/validators/pass_2_emission_lint.py` vs `skills/bmad-agent-content-creator/scripts/emission_lint.py`? Paige / Winston's call.
3. **Schema version bump strategy:** major bump (2.0) for the forbidden-key + new-required-fields change vs additive with strict validator? Recommend major bump since enforcement is strictly-tighter.
4. **Pipeline integration point:** Pack v4.2 §07 (end of Pass 2) or §08 (start of Storyboard B)? Recommend §07 end so fail-closed blocks §08 open.
5. **AC-B.3 upstream-reference cross-validation:** in scope v1 (harder test; catches §6.5) or defer to hardening follow-on? Recommend in scope — §6.5 is one of three HIGH-priority failure modes.
6. **Retrofit existing Irene refs:** pointer-only (AC-C.4 default) vs inline-retrofit? Recommend pointer-only (avoid scope creep).
7. **Worked example count:** 2 (static + motion) or 3 (add retrieval-intake-consuming segment, coordination with sibling story)? Recommend 3 for completeness, budget-permitting.
8. **Points estimate:** 3 pts (template + schema + basic lint) / 4 pts (add upstream cross-validation + pipeline integration) / 5 pts (add doc-parity lockstep test + worked-example #3 + sanctum retrofit).
9. **Coordination with Irene retrieval-intake:** field-name alignment for segment-manifest.retrieval_provenance (sibling story's additive field). Green-light confirms.
10. **Trial #2 blocker status:** if THIS story is blocker for trial #2 (per reproducibility report trigger), schedule first in dev sequence after green-light. Green-light confirms.
11. **Sanctum retrofit depth:** Irene `INDEX.md` one-line pointer (minimal) vs dedicated sanctum section for authoring-time discipline? Recommend minimal; dedicated section if Epic 26-5 preservation semantics support it.

## References

- **Reproducibility report §7.1** ([run-reproducibility-report-c1m1-tejal-20260419b.md §230-237](./run-reproducibility-report-c1m1-tejal-20260419b.md)) — source of three failure modes + HIGH priority designation + "trigger: before next Pass 2 run."
- **Reproducibility report §6.3 / §6.4 / §6.5** (same file, lines ~181-216) — concrete failure-mode details with root cause + fix-on-the-fly + durable disposition.
- **Irene Pass 2 procedure** ([skills/bmad-agent-content-creator/references/pass-2-procedure.md](../../skills/bmad-agent-content-creator/references/pass-2-procedure.md)) — existing authoring flow; template extends discipline without rewriting.
- **Segment-manifest schema** ([state/config/schemas/segment-manifest.schema.json](../../state/config/schemas/segment-manifest.schema.json)) — the schema this story tightens.
- **Pack v4.2** ([docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)) — the pipeline this lint gates.
- **Deferred inventory §Named-But-Not-Filed** ([_bmad-output/planning-artifacts/deferred-inventory.md](../planning-artifacts/deferred-inventory.md)) — "Irene Pass 2 authoring template / schema contract" entry is the deferred follow-on this story graduates.
- **Irene retrieval-intake sibling story** ([irene-retrieval-intake.md](./irene-retrieval-intake.md)) — segment-manifest additive `retrieval_provenance` field; coordinate at green-light.
- **PR-R Marcus dispatch reshaping sibling story** ([PR-R-marcus-dispatch-reshaping.md](./PR-R-marcus-dispatch-reshaping.md)) — out-of-scope here (dispatch-side concern); this story is emission-side only.
- **27-0 SCHEMA_CHANGELOG pattern** ([SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md)) — schema versioning discipline template.
- **Epic 23 G4 narration script gates** — overlapping surface; G4 gates are content-quality (Quinn-R/Vera). This story is structural (Pydantic/schema). Clean separation.

---

## Green-Light Patches Applied (party-mode round 1, 2026-04-22)

Four-panelist roundtable: Winston (Architect) / Amelia (Dev) / Murat (Test) / Paige (Tech Writer). **Unanimous GREEN** with Murat's fixture-pinning rider as the one hard requirement.

### Verdict

- 🏗️ Winston: GREEN — "trial-#2 blocker designation earned; AC-B.3 upstream cross-validation against Motion Gate receipt is the right seam"
- 💻 Amelia: GREEN with 2 dev-feasibility riders (Motion Gate receipt reader separation; deterministic lint)
- 🧪 Murat: YELLOW → GREEN after cross-artifact fixture-pinning rider applied + happy-path coverage-gap filled
- 📚 Paige: GREEN — "pointer-only update to pass-2-procedure.md is exactly the no-retrofit discipline; authoring-template.md as full canonical home is SSOT-clean"

### Murat test-discipline riders applied (the yellow-resolving ones)

- **AC-T.4 cross-artifact fixture PINNED**: Commit a frozen Motion Gate receipt from trial `C1-M1-PRES-20260419B` at `tests/fixtures/motion_gate_receipts/trial_c1m1_§6_5.json`. AC-T.4 test reads the FIXTURE, not a live receipt. If Motion Gate schema changes, this test fails loudly and pins the impact.
- **AC-T.3 trial-#1 regression**: Commit the passing (post-fix) manifest from trial `C1-M1-PRES-20260419B` as fixture at `tests/fixtures/pass_2_emissions/trial_c1m1_canonical.yaml`. The canary.
- **Three failure-mode fixtures separated**: Each in its own test file or clearly-labeled test function. Don't bundle §6.3 / §6.4 / §6.5 into one parametrize unless they share assertion shape.
- **Happy-path coverage-gap filled (Murat intuition-check)**: Add a SECOND happy-path atom — synthetic minimal-valid manifest passes validator. Protects against AC-T.3 (trial-regression) drifting into accidental minimum spec. Two happy-paths, not one.
- **Regression floor pinned ≥12 collecting** (raised from ≥10 — cross-artifact AC-T.4 needs fixture-validation + receipt-parsing as separate atoms; happy-path +1).
- **Flake-gate NOT NEEDED** (validator tests with fixed fixtures = deterministic) — assuming fixture-pinning rider is honored. If anyone regenerates Motion Gate receipt live, flake gate becomes mandatory.

### Amelia dev-feasibility riders applied

- **Rider 1 (separation of concerns)**: Motion Gate receipt reader must live at `skills/bmad-agent-irene/scripts/motion_gate_receipt_reader.py` — NOT inlined in the lint. Separate concern, separate test surface. §6.5 null motion_duration_seconds is exactly the bug a dedicated reader catches.
- **Rider 2 (deterministic lint)**: Lint is pure-function, zero LLM, zero network, zero filesystem beyond inputs. Given §6.3/§6.4/§6.5 are all schema-deterministic, no excuse for non-determinism.
- **Task order (ratified)**: Template markdown → schema tightening → lint script → pack integration. Schema BEFORE lint (lint depends on schema). Pack integration LAST.
- **Scope-creep trigger**: Don't absorb §6.1/§6.2/§6.6 trial-run failures. Scope is §6.3 + §6.4 + §6.5 ONLY.

### Winston architectural riders applied

- **AC-B.3 upstream-reference cross-validation**: Motion Gate receipt read via published receipt contract, NOT sibling-file path lookup. If receipt contract isn't published as a stable artifact, publish it in §7.1 as a prerequisite AC. Stable artifact now = dedicated reader module at `skills/bmad-agent-irene/scripts/motion_gate_receipt_reader.py` (per Amelia rider 1).

### Paige docs riders applied

- **Worked-example count: 2 (static + motion)** — firm. NOT 3. Rationale:
  - Coupling: a 3rd example consuming retrieval intake creates hard dependency on irene-retrieval-intake sibling story; if intake slips, authoring template ships with gap-marker.
  - Redundancy: irene-retrieval-intake's contract doc (`retrieval-intake-contract.md`, per D4) carries its own worked examples of the intake-attached shape. Replicating them in the authoring template violates SSOT.
- **Pointer in authoring template at relevant shape**: "When a segment consumes retrieval intake, see [retrieval-intake-contract.md](../references/retrieval-intake-contract.md) for the attached-shape worked examples." Keeps §7.1 decoupled from intake-story slippage + preserves SSOT.
- **No-retrofit discipline (AC-C.4)**: Irene existing references (`pass-2-procedure.md`, `cluster-head-pass-2.md`) get pointer updates ONLY. NO inline retrofit. Sanctum `INDEX.md` one-line pointer to the new template.
- **Explicit "do NOT emit legacy keys" list**: `motion_asset` (the legacy duplicate from §6.3) is the initial ban-list. Template maintained as legacy vocabulary grows.
- **Doc-parity lockstep** (AC-T.5): IN SCOPE — matches 27-2 AC-S6 transform-registry lockstep pattern. Roster-level shared doc-parity pattern (Murat roster-rider) applies here + retrieval-intake + evidence-bolster.

### Sprint-level context

- **Trial-#2 blocker**: per reproducibility report trigger — "before next Pass 2 run on any lesson." Must land before trial-#2 opens.
- **Opens position 1** per D7 sequencing. No upstream dependencies; blocks nothing else in Sprint #1 (parallel-safe with 27-2.5 at position 2).
- **Pack version bump classification**: Tier-1 (patch) — schema tightening + validator addition to existing Pass 2 flow; NO new pipeline step introduced. Dev-agent authority gated by Cora's block-mode hook per CLAUDE.md pack versioning policy. (If Cora rules Tier-2 at T0, add 1 pt for party-mode consensus round; check at T0 readiness.)

### Cross-story coordination

- **retrieval-intake-consuming segment example**: pointer-only reference to `retrieval-intake-contract.md` (per Paige worked-example count ruling). Intake story owns those examples.
- **Canonical 3-param naming (D6)**: Not directly relevant to §7.1's schema surface; but if template's examples reference Irene's segment-manifest `retrieval_provenance` field (additive from intake story), use canonical names.

### Regression floor pinned (Murat)

**≥12 collecting additions.** Cumulative Sprint #1 target: ≥1220 passed.

### Dev sequence

**Opens position 1 (FIRST)** per D7. Parallel-safe with 27-2.5 (position 2). Trial-#2 blocker — no slipping allowed.

### Vote record

- 🏗️ Winston: GREEN
- 💻 Amelia: GREEN (after separation-of-concerns + deterministic-lint riders applied)
- 🧪 Murat: YELLOW → GREEN (after cross-artifact fixture-pinning + happy-path coverage-gap fill)
- 📚 Paige: GREEN (worked-example count 2, pointer-only retrofit discipline confirmed)

**Unanimous GREEN → dev-story cleared to start** at position 1.

---

**Dev-story expansion triggered at:** green-light ratification (now). Template location (specialist-owned reference per skill conventions) + lint location (TBD Paige/Winston at T0 between `scripts/validators/` vs specialist scripts/) + pipeline integration point (Pack v4.2 §07 end so fail-closed blocks §08 open) + AC-B.3 upstream cross-validation IN SCOPE + worked example count 2 + retrofit depth pointer-only + trial-#2 blocker position 1 all RATIFIED above.
