---
title: 'P2-1 — Fail-loud fidelity detector (RED-first vs the $5.2T evidence)'
type: 'feature'
created: '2026-06-19'
baseline_commit: '057155c'
status: 'done'
governance:
  workflow: 'bmad-create-story → NEW CYCLE Codex dispatch'
  gate_mode: 'dual'
  tier: 'Tier-3 (party green-light REQUIRED before dev)'
  cycle: 'NEW CYCLE — Claude pre-author → Codex T1-T10 → Claude T11'
  authority: 'beta-phase-1-closure-ratification-2026-06-19.md §7 (P2-1); epics-perception-reading-path-fidelity.md (Story P2-1)'
epic: 'P2 — Perception + Reading-Path Narrative-Grounding Restoration'
story_key: 'p2-1'
context:
  - '{project-root}/_bmad-output/planning-artifacts/prd-perception-reading-path-fidelity.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics-perception-reading-path-fidelity.md'
  - '{project-root}/_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem (disaster-level regression):** Irene Pass-2 grounds narration on the slide **brief**, not the rendered PNG. Confirmed evidence (`_bmad-output/implementation-artifacts/evidence/narration-hallucinates-illustration-slide01-2026-06-19.png`): slide-01 RENDERED `$4.5T / 74% / 3x` stat callouts + a building photo; NARRATION speaks of *"the upward line toward $5.2 trillion … the paired bars contrasting Independent Practice vs Hospital Employment"* — a dual-axis line+bar chart never rendered, wrong figure. **G5 is blind to it** (it checks WPM/VTT/coverage mechanics, not narration↔rendered-slide fidelity), so every "error-free" run *increases* the volume of confident-wrong narration. The success metric is anti-correlated with quality.

**Approach (this story — the detector, FIRST and RED):** Build a **deterministic, fail-loud fidelity detector** — a G5-class check that compares Pass-2 narration against a per-slide `PerceptionArtifact` and raises **Class-A** when a *fidelity-bearing* narration reference resolves to no perceived element, or a narrated numeric contradicts a perceived figure. It is **two-sided** (catches the bad, passes the good), **deterministic + no-retry** (a content defect, never absorbed as LLM variance), and consumes **only** the `PerceptionArtifact` (no independent vision inference). It lands **RED against the committed un-repaired $5.2T evidence as a frozen fixture, BEFORE the producer (P2-2) or the Pass-2 repair (P2-3) exist** — proving it catches the failure before any repair can turn it green (anti-vacuous-pass).

**Per the ratification §7 + the green-light party round, this story owns:** the detector logic, the **`PerceptionArtifact` *consumed contract* (a minimal typed schema the detector reads)**, the RED-first fixture (hand-authored from the committed evidence), the sized real green corpus + seeded-defect set, and the import-linter single-source contract. P2-2 builds the producer (vision node) + the full schema richness (provenance/confidence/coverage); P2-3 rewires Pass-2. **The detector is its own story and is NOT folded** into the repair.

## Boundaries & Constraints

**Always:** Detector is **deterministic** (no model call) and **no-retry** (not added to `_RETRYABLE_DISPATCH_TAGS`). It consumes ONLY the `PerceptionArtifact` (schema module), never a vision provider, never a PNG path, never the brief. The RED fixture is committed evidence (the buggy narration + a hand-authored perceived artifact) and lands RED on the un-repaired tree. Detector tests run offline against frozen fixtures (no live vision). Two-sided: a known-good fixture + the sized real green corpus must pass with FP rate 0.

**Ask First (party green-light items — see §Green-light questions):** the detector's module placement; the minimal `PerceptionArtifact` consumed-contract shape (alignment with the existing `perception_contract.py` artifact shape); whether the failure is a new typed error vs a blocking verdict; the green-corpus size/source.

**Never:** Do NOT build the vision producer here (that's P2-2). Do NOT modify Pass-2 grounding here (that's P2-3). Do NOT add the detector tag to the auto-retry set. Do NOT let the detector perform its own vision inference. Do NOT fold the detector into a later story. Do NOT tune the detector to the buggy output (RED-first is the guard).

## Substrate findings (grounded — Claude pre-author 2026-06-19)

- **Existing perception shape (align the consumed contract to this):** `skills/bmad-agent-content-creator/scripts/perception_contract.py` produces artifacts with `{confidence: HIGH|LOW, visual_elements: list, extracted_text, layout_description, slide_title, text_blocks, artifact_path, slide_id, card_number}`; `perception_artifacts` already appear in the context envelope (`envelope.get("perception_artifacts")`). **But this is in the `skills/` tree and is NOT wired into the LangGraph production path / not consumed by Pass-2** (the regression). The detector's minimal contract should be a typed subset of this shape so P2-2's producer and the legacy shape converge, not fork (avoid a third perception vocabulary).
- **G5 home:** `app/specialists/quinn_r/_act.py::run_g5_checks` runs the mechanics checks; G5 content errors are built in `quinn_r/quality_control_dispatch.py` as dual-based `(SpecialistDispatchError, ValueError)` with `quinn_r.g5.*` tags. The fidelity detector is a new G5-class check in the quinn_r family.
- **Class-A vs retry:** the auto-retry keystone (`_invoke_specialist_with_retry` + `_RETRYABLE_DISPATCH_TAGS`, commit `e9d20be`) absorbs Class-B LLM variance. The fidelity failure is a **content defect (Class-A)** — it MUST NOT be added to `_RETRYABLE_DISPATCH_TAGS`; it surfaces as a blocking fail-loud verdict (operator fixes the real cause; it is not auto-absorbed).
- **Import-linter:** contracts live in `pyproject.toml` (`[tool.importlinter]`, 13 contracts). Add the single-source contract here.
- **$5.2T evidence:** narration text documented in run Pass-1 files (e.g., `runs/d7ad4dac.../irene-pass1.md`: "dual-axis data visualization … $5.2 trillion … declining independent practice with growing hospital employment"); rendered reality in the evidence PNG ($4.5T/74%/3x + building photo).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| **RED-first (the bug)** | committed $5.2T narration + frozen perceived artifact ($4.5T callouts+photo) | **Class-A FAIL** naming slide-01 + the orphan "$5.2T line+bars" reference | `FidelityError`, tag `quinn_r.g5.fidelity-orphan-reference`; blocking; NOT retryable |
| Contradicted numeric | narration "$5.2 trillion" vs perceived figure "$4.5T" | Class-A FAIL | tag `quinn_r.g5.fidelity-figure-contradiction` |
| Known-good (two-sided) | narration ⊆ perceived elements; figures match | PASS (clean) | N/A |
| Green corpus | ≥20–30 faithful real slides (paraphrase/rounding/synonym/multi-figure) | PASS, FP rate 0 | N/A — FP ceiling is a merge gate |
| Seeded defects | figure-swap / element-drop / magnitude-drift fixtures | Class-A FAIL on each (recall) | as above |
| Non-visual reference | "as we discussed", abstract concept, prior-slide callback | NOT flagged (typed classifier excludes non-fidelity-bearing refs) | N/A |
| Low-confidence / not-covered perception | perceived element marked `low-confidence`/`not-covered` | treated as **non-conformance** (not a clean pass) | Class-A FAIL (uncertainty never conforms) |
| Single-source violation | detector handed a contradictory raw PNG | verdict tracks the artifact, not the pixels | contradiction test; import-linter forbids provider import |
| Determinism | identical (artifact, narration) twice | identical verdict; no retry | N/A |

</frozen-after-approval>

## Code Map (proposed — confirm at green-light)

- `app/models/perception/perception_artifact.py` — **NEW (minimal consumed contract; C1).** Typed `PerceptionArtifact` / per-slide entry (per-slide-addressable; legacy-identical field names: `confidence, visual_elements, extracted_text, layout_description, slide_title, text_blocks, artifact_path, slide_id, card_number`; + a `coverage` state). Pydantic-v2 `extra="forbid"`. Lives in `app/models/` (peer of `app/models/state/`) so detector (P2-1), producer (P2-2), and Pass-2 (P2-3) all import it — no specialist→specialist dependency. Provider-free (import contract target).
- `app/specialists/quinn_r/fidelity_detector.py` — **NEW.** `detect_fidelity(narration_segments: list[dict], perception_artifacts) -> verdict` (pure, deterministic; takes plain dicts — matches the real `run_g5_checks` payload). Houses the typed fidelity-bearing-vs-non-visual classifier + orphan/contradiction checks. Imports only `app.models.perception` + stdlib; no vision provider, no PNG path. Ground-truth = perceived (PNG-derived); narration = claimant (C3).
- `app/specialists/quinn_r/quality_control_dispatch.py` — add `FidelityError` via the existing `_content_error` factory → dual base `(SpecialistDispatchError, ValueError)` (M1: gives recoverable fail-loud error-pause, NOT a crash); tags `quinn_r.g5.fidelity-orphan-reference` / `quinn_r.g5.fidelity-figure-contradiction`. **Do NOT modify `_RETRYABLE_DISPATCH_TAGS`** — non-retryable = absence from the allowlist.
- `app/specialists/quinn_r/_act.py::run_g5_checks` — invoke `detect_fidelity`; **absent `perception_artifacts` is itself a non-conformance** (do not silently pass; M/C6); `low-confidence`/`not-covered` never conform. Verdict names slide + reference; pauses + blocks publish (FR15).
- `pyproject.toml [tool.importlinter]` — add `forbidden` contract (G2): source `app.specialists.quinn_r.fidelity_detector`, forbidden `app.specialists.quinn_r.sensory_bridges_dispatch`; schema module provider-free. 13 → 14 contracts.
- `tests/specialists/quinn_r/test_fidelity_detector.py` — **NEW.** RED-first (vs cited committed evidence, F5/F6) + two-sided + classifier confusion-metric (CL1) + idempotent re-eval (M3) + determinism + single-source (contradiction + second-inference-injection) pins.
- `tests/fixtures/specialists/quinn_r/fidelity/` — **NEW, all committed + content-hash frozen (F1/F3).** `slide01-red.json` (perceived leg PNG-derived; narration cites `irene-pass1.md:8`; shape-test-pinned to the contract); `green-corpus/` (fixture-scale faithful slides) + `green-corpus-manifest.json` (entry → run id + slide id + artifact hash + curator + faithful-criterion); `seeded-defects/` generated as programmatic single-mutations over the green corpus (F4). Curator-of-record = operator/party (NOT dev).
- **Pipeline-lockstep:** P2-1 paths are **NOT** in `block_mode_trigger_paths` (verified) → no L1 block-mode regime, no pack bump for P2-1. Dev runs the L1 check at T1 as confirmation only. (Tier-3 pack/manifest governance lands at P2-2.)

## Tasks & Acceptance

**Execution (Codex T1-T9):**
- [ ] `app/models/perception/perception_artifact.py` — typed `PerceptionArtifact` (legacy-identical field names + `coverage` state ∈ {perceived, low-confidence, not-covered}); Pydantic-v2 `extra="forbid"`; provider-free; single-source (C1).
- [ ] `fidelity_detector.detect_fidelity(narration_segments: list[dict], perception_artifacts)` — deterministic, pure; ground-truth=perceived (PNG-derived), narration=claimant (C3); typed fidelity-bearing-vs-non-visual classifier; orphan-reference + numeric-contradiction checks; low-confidence/not-covered/absent ⇒ non-conformance.
- [ ] `FidelityError` via `_content_error` (dual base; M1); tags pinned; **do NOT modify `_RETRYABLE_DISPATCH_TAGS`** (non-retryable by absence).
- [ ] Wire `detect_fidelity` into `run_g5_checks`; verdict names slide + reference; pauses + blocks publish; **idempotent re-eval** (clean on corrected artifact, no latched state; M3).
- [ ] Import-linter `forbidden` contract: `fidelity_detector` ⊄ `quinn_r.sensory_bridges_dispatch` (G2; 13→14).
- [ ] Fixtures — **all committed + content-hash frozen** (F1/F3): `slide01-red.json` (perceived leg PNG-derived; narration cites `irene-pass1.md:8`; shape-test-pinned, C2/F5); `green-corpus/` (fixture-scale faithful slides, curator-signed) + `green-corpus-manifest.json` (run id + slide id + hash + curator + criterion); `seeded-defects/` as programmatic single-mutations over the green corpus (F4).
- [ ] Tests (see ACs) — all offline against frozen fixtures (no live vision; no untracked `runs/`).
- [ ] §6 DoD (P2-1 scope): cross-trial-learnings harvest entry (construct-invalidity finding + RED fixture citations), bidirectionally linked to the grounding-leg deferred-inventory entry **WITHOUT striking it** (strike waits for P2-3; G4). sprint-status entry annotated `done (guard armed; real corpus intentionally RED until P2-3)` (G3).

**Codex implementation note (2026-06-19):** T1-T10 implementation is complete and ready for Claude T11 review. The detailed completion/verification record is `_bmad-output/implementation-artifacts/_codex-handoff/p2-1-fidelity-detector-red-first.ready-for-review.md`.

**Acceptance Criteria:**
- **AC-1 (RED-first, BINDING):** on the un-repaired tree, the detector raises `FidelityError` (`quinn_r.g5.fidelity-orphan-reference`) against the committed $5.2T fixture, naming slide-01 + the orphan reference — demonstrated RED before P2-2/P2-3 land. (FR10, FR21)
- **AC-2 (two-sided):** a known-good fixture + the sized real green corpus PASS with **FP rate 0**. (FR22, NFR3)
- **AC-3 (recall):** every seeded-defect fixture (figure-swap, element-drop, magnitude-drift) raises Class-A. (FR22)
- **AC-4 (numeric contradiction):** narrated figure contradicting a perceived figure raises `quinn_r.g5.fidelity-figure-contradiction`. (FR11)
- **AC-5 (typed classifier):** non-visual references (prior-slide callbacks, abstract concepts) are NOT flagged; only fidelity-bearing references are checked. (FR12)
- **AC-6 (uncertainty ≠ conformance):** `low-confidence`/`not-covered` perception → non-conformance, never a clean pass; absent perception_artifacts → non-conformance. (FR13)
- **AC-7 (single-source):** import-linter passes (detector ⊄ provider); a contradiction test proves the verdict tracks the artifact (not a mismatched PNG); a second-inference injection makes the invariant test RED. (FR14, NFR8)
- **AC-8 (deterministic, no-retry):** identical inputs → identical verdict; the tag is absent from `_RETRYABLE_DISPATCH_TAGS`. (FR16, NFR1)
- **AC-9 (surfacing + audit):** a fidelity failure pauses the run, blocks publish, and records the verdict + evidence (perceived elements vs narrated refs). (FR15, FR24, NFR6)
- **AC-10 (test isolation):** detector tests consume only frozen fixtures; no live vision; detector tests are blocking. (NFR10)
- **AC-11 (regression-green left to P2-3):** this story does NOT make a full run green — that is P2-3. The detector remains RED on the committed-evidence fixture until Pass-2 is repaired; the green corpus stays GREEN (distinct artifacts). (sequence integrity)
- **AC-12 (RED on real committed evidence; F6, non-negotiable):** a standing test asserts the detector is RED on the **actual committed evidence** — the real narration string cited from `runs/d7ad4dac.../irene-pass1.md:8` + the PNG-derived perceived leg — distinct from any tidy reconstruction. (The fully-real *produced-artifact* RED test is deferred to P2-2, where the producer exists.)
- **AC-13 (idempotent re-evaluation; M3, non-negotiable):** re-invoking the detector on a corrected artifact returns clean with no latched/sticky state — establishing P2-3's clearing contract.
- **AC-14 (classifier confusion-metric; CL1):** the fidelity-bearing-vs-non-visual classifier has its own two-sided test — a labeled set of fidelity-bearing AND non-visual references with asserted confusion counts (its false-negative rate is the silent-pass vector), separate from the whole-detector FP gate.
- **AC-15 (versioned green corpus + manifest; F1, HARD):** the green corpus + seeded-defect set are committed fixtures (not pointers into untracked `runs/`); a `green-corpus-manifest.json` maps each entry → source run id + slide id + content hash + curator + faithful-criterion; a clean-clone CI run finds the corpus. Tests are offline/frozen (AC-10 covers the green corpus).
- **AC-16 (contract single-source + additive-extension; C1/C2):** the `PerceptionArtifact` lives at `app/models/perception/`; a shape-pin test fixes the contract P2-2 will extend; the contract uses `extra="forbid"`; field names are legacy-identical (no third vocabulary).

## Tier-3 Green-Light Disposition (party-mode, 2026-06-19) — RATIFIED

**Verdict: APPROVE-WITH-AMENDMENTS, unanimous 5/5** (🏗️ Winston, 🧪 Murat, 💻 Amelia, 📋 John, 📊 Mary). All amendments below are **binding dev requirements** folded into the Tasks/AC; the Codex prompt enforces them. This round also satisfies the Tier-3 "party green-light before dev" gate for P2-1.

### Resolved green-light questions
1. **Detector placement** → `app/specialists/quinn_r/fidelity_detector.py` (G5 family) — unanimous. Pure dependency-light leaf; `run_g5_checks` calls into it; not its own manifest node.
2. **Consumed-contract home** → **`app/models/perception/perception_artifact.py`** (Amelia, binding) — NOT under `quinn_r/` (avoids specialist→specialist import + P2-2/P2-3 churn). Minimal-now / additive-extend-later.
3. **Class-A mechanics** → keep the `(SpecialistDispatchError, ValueError)` dual base (Amelia, binding): error-pause ≠ auto-retry. Non-retryable = **not added to** the allowlist `_RETRYABLE_DISPATCH_TAGS` (do NOT modify that frozenset). Hard-stop at runtime; recoverable only across a code/content-fix boundary (P2-3 / corpus fix), never by re-run.
4. **Green corpus** → **fixture-scale, committed as versioned fixtures, NOT the untracked production `runs/`** (Mary, HARD BLOCKER: `git ls-files runs/` = 1 file; all run dirs untracked). Curator-of-record = operator/party (NOT the dev); per-entry source manifest (run id + slide id + artifact hash) + "faithful" criterion. Real-corpus faithful-labeling is P2-3, not P2-1 (John).
5. **Lockstep exposure** → **P2-1 is lockstep-CLEAN.** Verified: `quinn_r/_act.py`, `quality_control_dispatch.py`, `pyproject.toml`, `app/models/perception/`, and the new test/detector paths are **NOT in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`** → no L1 block-mode regime fires for P2-1, and **no pack-version bump** (P2-1 adds no manifest node / no pack prose). The Tier-3 pack/manifest governance + version bump lands at **P2-2** (vision node + PerceptionArtifact schema family + manifest node). Dev still runs the L1 lockstep check at T1 as a cheap confirmation.

### Binding amendments (consolidated — fold ALL into dev)
**Contract/schema:**
- **C1 (Amelia/Winston):** typed `PerceptionArtifact` at `app/models/perception/perception_artifact.py`; field-name-identical subset of legacy `skills/bmad-agent-content-creator/scripts/perception_contract.py` keys (`confidence, visual_elements, extracted_text, layout_description, slide_title, text_blocks, artifact_path, slide_id, card_number`); skills/ = producer-of-record; single-source (P2-1 defines, P2-2/P2-3 import, never fork); P2-2 extension strictly additive (Optional/defaulted, no rename/make-required), Pydantic-v2 `extra="forbid"`.
- **C2 (Murat):** RED fixture pinned to the typed contract via a shape test (the same contract P2-2 builds against) — not a loose dict.
- **C3 (Mary, deep):** the contract's **ground-truth leg = rendered values from the PNG (authority); narration = claimant.** The perceived leg must derive from the rendered slide ($4.5T/74%/3x + building photo), NEVER from a Pass-1/plan markdown — else the detector inherits the blindness it exists to catch.

**Class-A mechanics:**
- **M1 (Amelia):** "not added to" `_RETRYABLE_DISPATCH_TAGS`; keep dual base; correct the spec's prior "excluded from" wording.
- **M2 (John/Winston):** hard-stop + recoverable only across a fix boundary.
- **M3 (Murat, non-negotiable):** **idempotent re-evaluation** — re-invoking the detector on a corrected artifact returns clean (no latched/sticky state); establishes P2-3's clearing contract now.

**Fixtures/corpus:**
- **F1 (Mary, HARD BLOCKER):** commit green-corpus seed slides as versioned fixtures under `tests/fixtures/specialists/quinn_r/fidelity/`; a manifest mapping each entry → source run id + slide id + committed artifact hash; named curator + "faithful" criterion (rendered callouts match narrated callouts, no orphan asset refs). Do NOT point tests at untracked `runs/`.
- **F2 (John):** green corpus = fixture-scale, curated within P2-1, NOT the production corpus.
- **F3 (Winston/Murat/Mary):** curator ≠ dev; per-entry rationale; content-hash frozen; AC-10 offline-frozen guarantee explicitly covers the green corpus.
- **F4 (Murat):** seeded defects = programmatic single-mutation injections over the frozen green corpus (one defect-class per mutation), not bespoke fixtures.
- **F5 (Mary):** RED fixture cites exact provenance — `runs/d7ad4dac.../irene-pass1.md:8` (narration string) + the committed evidence PNG path + the rendered callouts as ground-truth contrast.
- **F6 (Murat, non-negotiable):** a standing test asserts the detector is RED on the **actual committed evidence** (the cited real narration string + the PNG-derived perceived leg), distinct from a tidy reconstruction; the fully-real *produced-artifact* RED test is a P2-2 AC (no producer exists yet).

**Classifier:**
- **CL1 (Murat):** the typed fidelity-bearing-vs-non-visual classifier carries its **own two-sided confusion-count micro-metric** (labeled fidelity-bearing AND non-visual refs), separate from the whole-detector FP gate — its false-negative rate is the most likely silent-pass vector.

**Governance:**
- **G2 (Amelia):** import-linter `forbidden` contract — source `app.specialists.quinn_r.fidelity_detector`, forbidden `app.specialists.quinn_r.sensory_bridges_dispatch`; detector imports only `app.models.perception` + stdlib; schema module provider-free. 13→14.
- **G3 (John):** sprint-status entry annotated `done (guard armed; real corpus intentionally RED until P2-3)`.
- **G4 (John/Mary):** the grounding-leg deferred-inventory entry **stays OPEN** through P2-1/P2-2; struck only at P2-3. P2-1's DoD = a **scoped cross-trial harvest** (the construct-invalidity finding + the RED fixture's evidence citations), bidirectionally linked to the inventory entry **without striking it**.

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/quinn_r/test_fidelity_detector.py -q` — RED-first proven; two-sided green; recall; boundary; determinism; single-source.
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/quinn_r/ tests/contracts/ -q -p no:randomly` — no regression in the G5 family.
- `.\.venv\Scripts\lint-imports.exe` — expected: 14 kept (new single-source contract), 0 broken.
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` — exit 0 (if lockstep-touching).
- `.\.venv\Scripts\ruff.exe check app/specialists/quinn_r/ tests/specialists/quinn_r/test_fidelity_detector.py` — clean.

## T11 Review & Close (2026-06-19) — DONE

**`bmad-code-review` 3-lane (Blind / Edge / Auditor) + Claude T11.** Acceptance Auditor: all 16 ACs PASS. Blind + Edge surfaced real bugs the AC tests didn't exercise; all remediated at T11:
- **Blind #1 (CRITICAL) FIXED:** money normalization no longer force-casts bare `$5` onto `$5 trillion` (distinct `money-bare` class; billion→trillion conversion retained). +test.
- **Blind #6 (MEDIUM) FIXED:** dropped idiom-risky bare visual terms (`bar`/`line`/`table`/`building`/`stat`); the blocking check no longer fires on "raise the bar"/"bottom line". +test.
- **Edge #2 / Blind #7 (HIGH) FIXED:** `_artifact_map` wraps `ValidationError`→tagged `FidelityError` (error-pause-able); single-artifact-dict accepted. +test.
- **Blind #3 / Edge #4 (HIGH) FIXED:** duplicate `slide_id` raises (no silent last-wins). +test.
- **Regression caught (Codex missed `tests/parity/`): FIXED** — parity G5 payload given perception; TW-7c-4 allowlist extended for P2-1 paths.
- Dismissed: Blind #5 (values-only stringify already correct), #2/#4/#10/#11 (Edge confirmed unfounded), #8/#9 (acceptable fail-on-first).

**Edge #1 — posture RATIFIED (party 2026-06-19, operator-ratified): Winston B+tripwire.** This **reverses the green-lit AC-6 "absent ⇒ fail."** New posture: absent `perception_artifacts` is a typed **`UNVERIFIED (perception-not-wired)` dormant status — NOT a Class-A fail** — so live trials keep running mechanics-only (the "fidelity unverified" rebrand) through the P2 arc. The detector ENFORCES Class-A only when perception is **present** (contradiction / low-confidence / not-covered / per-slide-missing). A **standing tripwire test** (`test_tripwire_g5_manifest_does_not_yet_supply_perception`) asserts the production G5 node does not yet project `perception_artifacts`; it **fails the instant P2-2 wires perception**, forcing the flip from dormant-skip to enforce (dormancy cannot silently rot). Panel: Winston B+tripwire, John B, Murat synthesis(distinct-categorization) — 2:1 for non-blocking + unanimous on distinct-category + forcing-function.

**Green-corpus sign-off — DISPOSITION (operator-ratified 2026-06-19):** the 8 green fixtures are **synthetic, dev-authored, internally-consistent** (faithful by construction) — they prove the detector's two-sided MECHANICS (FP=0 on internally-faithful pairs), NOT real-content fidelity. The operator faithful-label sign-off is **not a meaningful gate for synthetic data** and is **deferred to P2-3** (real-content faithful curation + slide/PNG review, where rendered slides exist). The RED case remains anchored in real committed evidence (slide-01 PNG). Manifest curator field records this.

**§6 DoD:** cross-trial-learnings P2-1 harvest entry present (construct-invalidity finding + RED citations); grounding-leg deferred-inventory entry **NOT struck** (stays open through P2-2/P2-3). **Sprint annotation:** `P2-1 done (guard armed; real corpus intentionally RED/UNVERIFIED until P2-3)`.

**Validation:** 107 in-scope passed (quinn_r + parity + audio + taxonomy + TW-7c-4) + integration 193/1-skip; ruff clean; lint-imports 14/0; lockstep exit 0.

## Spec Change Log

- 2026-06-19 — authored (Claude pre-author, NEW CYCLE). Awaiting Tier-3 party green-light before Codex dispatch.
- 2026-06-19 — **Tier-3 party green-light: APPROVE-WITH-AMENDMENTS, unanimous 5/5** (Winston/Murat/Amelia/John/Mary). Applied: contract → `app/models/perception/` (C1); ground-truth-from-PNG (C3); dual-base + non-retryable-by-absence (M1); idempotent re-eval (M3); committed/versioned green corpus + manifest (F1, Mary's hard blocker — `runs/` untracked); seeded defects as programmatic mutations (F4); RED-on-real-committed-evidence (F6); classifier confusion-metric (CL1); import-linter forbidden vs `sensory_bridges_dispatch` (G2); lockstep-clean for P2-1 (Tier-3 bites at P2-2); DoD harvest-not-strike (G4) + sprint-status asterisk (G3). Status → `ready-for-dev`.
