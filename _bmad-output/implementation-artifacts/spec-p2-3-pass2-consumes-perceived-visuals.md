---
story_key: p2-3-pass2-consumes-perceived-visuals
epic: P2 — Perception + Reading-Path Narrative-Grounding Restoration
status: ready-for-dev
gate_mode: dual
tier: Tier-3 (party green-light required BEFORE dev)
baseline_commit: 3a0ad22
authority: epics-perception-reading-path-fidelity.md §Story P2-3; prd-perception-reading-path-fidelity.md FR7–FR9
sequence: after P2-2 (DONE 3a0ad22); turns the detector FULLY regression-green
r_tier: R2
t11_tier: standard
lookahead_tier: 2
files_touched: [app/specialists/irene/graph.py, app/specialists/irene/authoring/pass_2_template.py, state/config/pipeline-manifest.yaml, docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md, tests/specialists/irene/*, _bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md]
---

# P2-3: Pass-2 consumes perceived visuals — the regression fix

## Frozen Intent

Make Irene's Pass-2 narration ground on the **perceived `PerceptionArtifact`** (the vision node's PNG-grounded reality) as the **sole visual authority**, demoting Gary's brief-derived `visual_description` to a secondary expectation signal. This closes the disaster-level confident-wrong regression: narration will describe what the slide *renders* (slide-01 = `$4.5T` callouts + building photo), not what the brief *expected* (`$5.2T` line+bars). With P2-1's detector already enforcing refs⊆perceived at G5, P2-3 turns the detector **fully regression-green**.

P2-3 changes the GROUNDING INPUT to Pass-2. The detector (P2-1) is the OUTPUT guard and is unchanged. Reading-path scan-order is **out of scope** (P2-4, Growth).

## Substrate grounding (verified against `3a0ad22`)

- **Manifest gap.** Node `08` (irene Pass-2) `dependency_projections` (`state/config/pipeline-manifest.yaml:571-583`) deliver `bundle_reference`, `lesson_plan`, `slide_briefs`, `gary_slide_output` — but **not `perception_artifacts`**. The vision node `07G` (`:539-545`) produces `perception_artifacts`; only node `13`/G5 (quinn-r) currently consumes them. Node `08` runs after `07G` (`insertion_after: "07G"`), so the artifact is available to project.
- **Runtime gap.** `_act_pass_2` (`app/specialists/irene/graph.py:395-453`) calls `_slide_roster` (`:97-131`) → builds `{slide_id, visual_description}` from `gary_slide_output` (the **brief**), then `_assemble_pass_2_prompt` (`:228-280`) renders `- {slide_id}: {visual_description}` under "## Real slide roster (narrate THESE slides…)". `perception_artifacts` is never read by the runtime path.
- **Post-check.** `_assert_narration_joins_roster` (`:134-163`) only checks each `visual_reference.perception_source` is a roster **slide_id** — it does not check refs ⊆ perceived elements (that is the detector's job at G5).
- **🔴 Latent two-source-of-truth fork (A23-class) — party decision required.** Two `PerceptionArtifact` models exist: (1) `app/models/perception/perception_artifact.py` — rich, vision-produced + detector-consumed (`visual_elements`, `extracted_text`, `layout_description`, `slide_title`, `text_blocks`, `coverage`, `confidence`); (2) `app/specialists/irene/authoring/pass_2_template.py::PerceptionArtifact` — minimal authoring-time model (`slide_id`, `source_image_path`, `visual_elements`) inside `IrenePass2AuthoringEnvelope`, whose `perception_artifacts` field + cross-validators **already anticipate perception but are NOT wired to the runtime `_act_pass_2` path.** P2-3 must rule on how these reconcile (see Open Decision D1).

## Acceptance Criteria

- **AC-1 (FR7 — projection).** **Given** the vision node emits `perception_artifacts`, **When** the manifest is loaded, **Then** node `08` (irene Pass-2) `dependency_projections` delivers `perception_artifacts` from `vision`; a manifest-payload contract test pins the new edge; lockstep L1 exits 0 and the `-gen` witness regenerates. (`pipeline-manifest.yaml:571-583`)
- **AC-2 (FR7 — sole visual authority).** **Given** a slide's perceived `PerceptionArtifact`, **When** `_assemble_pass_2_prompt` builds the prompt, **Then** the perceived elements/text/figures are presented as **the** visual authority Pass-2 must narrate, under an explicit "what the slide actually shows (perceived)" header. Offline test: assemble against a frozen perceived fixture and assert the prompt contains the perceived figures (`$4.5T`) in the authority position. (`graph.py:228-280`)
- **AC-3 (FR8 — Vera/brief demotion).** **Given** Gary's `visual_description` (brief) and Vera's brief-derived perception, **When** the prompt is assembled, **Then** they appear only under a clearly-labelled **secondary "expected (may be stale; defer to perceived)"** section — never as the primary visual authority. Offline test asserts the demotion labelling + ordering.
- **AC-4 (FR9 — fidelity, the regression proof).** **Given** the repaired Pass-2 grounding on the slide-01 perceived artifact (`$4.5T` callouts + building photo) and the frozen corpus, **When** a Pass-2 run completes and the P2-1 detector runs at G5, **Then** references ⊆ perceived elements and narrated numerics match perceived figures (slide-01 narrates **$4.5T, not $5.2T**) and the detector is **GREEN** (regression-green). [Live/operator-gated leg + an offline prompt-grounding leg per the sandbox-AC split.]
- **AC-5 (FR6/FR13 — no silent brief-fallback).** **Given** a slide whose perception is `not-covered` or `low-confidence`, **When** Pass-2 grounds, **Then** it does **not** silently substitute the brief as visual authority; behaviour is the party-ratified D2 disposition (conservative narration / explicit uncovered marker / fail-loud), with a test.
- **AC-6 (regression-green merge gate / §6 DoD).** **Given** the frozen corpus + ≥1 held-out slide, **When** the full run completes, **Then** detector GREEN is the merge gate; on close, the grounding-leg deferred entry `fidelity-metric-blind-to-perception-regression` is **struck** and the cross-trial harvest filed.
- **AC-7 (no scope creep).** P2-1 stays green (detector unchanged); P2-2 schema unchanged; reading-path (`reading_path` field, scan-order) is **NOT** introduced (P2-4). `_assert_narration_joins_roster`'s slide_id join is preserved (element-subset remains the detector's job).
- **AC-8 (governance).** dp version bumps `dp-v1.3 → dp-v1.4` (additive vision→Pass-2 projection); `pack_version` stays `v4.2` (no v4.3); `-gen` witness regenerated; SCHEMA_CHANGELOG updated; lint-imports 0-broken; sandbox-AC validator PASS.

## Open decisions for the Tier-3 green-light

- **D1 (two-PerceptionArtifact fork).** Recommend: runtime `_act_pass_2` grounds directly on the **rich** `app/models/perception.PerceptionArtifact` (vision-produced); the `pass_2_template.py` authoring-envelope model stays a separate guidance contract (or is populated from the rich one). File the fork in deferred-inventory either way. Alternatives: unify the two models (larger blast radius) — party calls it.
- **D2 (not-covered/low-confidence grounding).** What does Pass-2 narrate when perception is absent/low-confidence? Options: (a) narrate conservatively from corpus text only + mark the slide; (b) fail-loud `Pass2GroundingError`; (c) explicit "unverified visual" narration. Must honour FR6 "no silent brief-fallback."
- **D3 (`perception_source` semantics).** Keep `perception_source = slide_id` for P2-3 (recommended; detector enforces element-subset), or promote it to a perceived-element reference now (scope creep into P2-4 territory)?
- **D4 (dp bump + lockstep).** Confirm `dp-v1.4` additive bump + `-gen` regen is the right governance (vs. staying dp-v1.3). Tier-3 pipeline-lockstep applies (manifest + `-gen` pack touched).
- **D5 (regression-green testability).** AC-4's live leg needs an LLM Pass-2 run (operator-gated, evidence in Completion Notes); the offline leg asserts the assembled prompt grounds on perceived elements + demotes brief. Confirm the split satisfies the sandbox-AC rule.

## Tier-3 Green-Light Disposition

**Fully-spawned party-mode (Winston/John/Murat/Mary/Amelia) — UNANIMOUS 5/5 GREEN-WITH-AMENDMENTS, no impasse, no block.** Quinn→John chain not triggered.

### Open-decision verdicts
- **D1 (two-model fork) — RESOLVED:** runtime `_act_pass_2`/`_assemble_pass_2_prompt` grounds on the **rich** `app/models/perception/perception_artifact.py::PerceptionArtifact` (vision-produced). The minimal `pass_2_template.py::PerceptionArtifact` is populated **from** the rich model at the envelope boundary, or left untouched — **never the grounding source**. Do NOT unify in P2-3. (Amelia's trap: grounding on the field-poor model silently reverts to brief while tests go green.)
- **D2 (not-covered/low-confidence) — RESOLVED: fail-loud / explicit-unverified, no silent brief-fallback (ever, in merged code).** Per-slide perception is either authoritative (covered + above confidence threshold) or routes to an explicit detector-visible **"UNVERIFIED — no perceived authority"** token; the brief NEVER occupies the authority position. No third "best-effort blend with brief" mode. Conservative-from-corpus synthesis is **deferred** (John: net-new generation = creep). Every grounding decision records its source (`perceived-high | perceived-low | unverified`), auditable.
- **D3 — RESOLVED:** `perception_source=slide_id` frozen for P2-3; element-reference promotion → P2-4 follow-on (filed).
- **D4 — CONFIRMED:** `dp-v1.3 → dp-v1.4` additive bump + `-gen` witness regen; `pack_version` stays `v4.2`; pipeline-lockstep regime (dev reads `docs/dev-guide/pipeline-manifest-regime.md` at T1).
- **D5 — CONFIRMED:** AC-4 split = hard-blocking offline grounding/detector leg (every CI pass) + operator-gated live regression-green leg (Completion Notes evidence).

### Binding amendments (all must land before/within the Codex cycle)
- **A1 (D1 rich-model authority):** spec + Codex prompt pin rich-model-as-sole-grounding-source. Authoring-envelope model becomes a strict subset projection populated from the rich model, with a **field-compatibility contract test** that fails loud if the rich model drops a field the envelope reads (Winston); module docstring names the rich model as sole upstream.
- **A2 (D1 fork filing — Mary BLOCKS without it):** file deferred-inventory `perception-artifact-two-model-fork` with explicit CLEANUP DIRECTION + "direction may flip if substrate evolves" caveat; add an in-spec/in-code **decoy note** at the wiring site. AC-6 strike references it bidirectionally; reactivation trigger tied to P2-4.
- **A3 (anti-vacuity test gate — Murat, non-negotiable):** (a) **contradiction fixture** mandatory — perceived `$4.5T` + photo/bar vs brief `$5.2T` + "line+bars"; (b) assert by **section/region** via a structural delimiter the assembler emits — authority region **contains** perceived figures + the perceived chart type AND **excludes** `$5.2T`/"line+bars"; brief content appears **only** in an explicitly-subordinate demoted region; (c) **two mutation runs** must turn the tests RED — **M1 source-revert** (ground on brief → authority carries `$5.2T`) and **M2 section-collapse** (flat blob → positional assertion can't locate `$4.5T` as authority); mutation evidence required in Completion Notes.
- **A4 (AC-4 detector-as-judge):** the regression-green pass criterion is the **P2-1 detector returning clean** against the rendered slide, NOT a narration string match. Codex confirms at T1 the P2-1 detector is **headlessly invokable** on Pass-2 output; if not, surface as a blocker NOW, not at T11.
- **A5 (RED-first regression proof):** a committed test reproduces the exact failure (`$5.2T line+bars` narration vs a `$4.5T`+photo perceived slide) that is RED pre-fix and GREEN post-fix; named **held-out** seed-contradicted slide (not tuned against) for the anti-overfit leg.
- **A6 (STRIKE gate — Mary, AC-6):** strike `fidelity-metric-blind-to-perception-regression` ONLY on (a) detector-GREEN across the **full frozen corpus**, (b) detector-GREEN on **≥1 held-out slide**, (c) a **cited reproduced pre-fix RED baseline**. Bidirectional inventory↔cross-trial-harvest linkage on strike.
- **A7 (process guard — Mary, carry P2-2 Category-F forward):** the Codex prompt requires **baseline-diff attestation** — pre-fix RED + post-fix GREEN detector output pasted to Completion Notes + an explicit attestation that the green assertion is bound to perceived/rendered-PNG elements, not the brief. T11 verifies the green assertion is the load-bearing one.
- **A8 (NFR-I6 cache-prefix — Amelia):** preserve cache-prefix byte-stability — canonical sorted-keys JSON for injected perception data (match the existing pinned `json.dumps` signature; deterministic element ordering by a stable key), inject the perceived-authority block at a **fixed seam** (preserve the prefix byte-identity as far down as possible), no incidental reformatting of pinned text, and **deliberately re-pin** the named cache-prefix stability fixture with a one-line rationale (never `xfail`/skip).
- **A9 (D3 deferral):** file `perception-source-element-reference-promotion` to deferred-inventory (P2-4 successor).

### AC deltas folded from amendments
- **AC-2/AC-3** adopt A3 (contradiction fixture + section/region assertion + mutation gate) and A1 (rich-model authority).
- **AC-4** adopts A4 (detector-as-judge) + A5 (RED-first + held-out) + the D5 split.
- **AC-5** adopts D2/A-D2 (explicit-unverified token; no silent brief-fallback; source recorded).
- **AC-6** adopts A6 (tightened strike gate, bidirectional linkage).
- **New AC-9 (fork hygiene):** authoring-envelope model is subset-projection-from-rich with a field-compatibility contract test + decoy note; fork filed (A1/A2).
- **New AC-10 (cache-prefix):** A8 invariants honored; named stability fixture re-pinned deliberately.

**Status → ready-for-dev.** Codex driver: `codex-dev-prompt-p2-3-pass2-consumes-perceived-visuals.md`.
