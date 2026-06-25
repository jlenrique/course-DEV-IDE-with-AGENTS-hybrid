# Braid Green-Light Ratification — 2026-06-24 (party-mode, sprint-governance §2/§4)

**Outcome:** **GREEN-WITH-AMENDMENTS, 6/6, no impasse.** The braid (Marcus-interlocutor + research-foundations + lesson-planning-with-workbook-companion) is **one coherent arc** — do not split. Spec-readiness is conditional on the consolidated amendments below landing in the specs.
**Round:** tailored party — John (PM), Winston (Architect), Murat (TEA), Mary (Analyst), Marcus (orchestrator), Irene (content-creator). Each spawned as an independent subagent.
**Strawman under test:** `braid-strawman-2026-06-24.md`. **This file supersedes its §3 recommendations where amended below.**
**Authority chain:** operator vision 2026-06-24; `forward-development-sequence-2026-06-24.md`; CLAUDE.md sprint-governance.

---

## 1. Verdicts (all six)

| Voice | Verdict | Load-bearing contribution |
|---|---|---|
| John (PM) | GREEN-W-AMEND | Resequence **client-value-first**: ship the workbook before any Marcus net-new build |
| Mary (Analyst) | GREEN-W-AMEND | Missing honesty gate: audit the workbook **body/prose**, not just citations; same resequence; named dissent if overridden |
| Murat (TEA) | GREEN-W-AMEND | Make the soft policies **checkable**: DP6 path-intersection gate; live-graph-derived overlay; L2 fail-mode; adversarial over-promise probe |
| Winston (Arch) | GREEN-W-AMEND | Substrate is real: workbook = 4th `ModalityProducer` sibling; DOCX free / **no PDF lib**; overlay generated from manifest |
| Marcus (orch) | GREEN-W-AMEND | **DP2 inverted** — no collision, one Tracy already built; capability-overlay derived+CI-tested; v1 Marcus = scripted-confirm not elicitor |
| Irene (author) | GREEN-W-AMEND | Workbook **content model** (not a shopping list); transcript = scaffold needing re-voice; body-fidelity gate |

No voice defended the strawman's Marcus-first sequence. The resequence is a clean Pareto improvement → adopted without impasse.

---

## 2. LOCKED decisions

**DP1 — Marcus capability-self-model: GENERATED, not authored.** The overlay is **derived from `state/config/pipeline-manifest.yaml` + `state/config/dispatch-registry.yaml`** (+ on-disk `app/specialists/<id>/` not-stub check + registry `status`), emitted as a **closed-enum `capability-state` artifact** with four mechanical states: `wired` (manifest node + dispatch entry) · `present-but-unrouted` (dispatch entry, no manifest node — e.g. Tracy/Wanda today) · `partial` (in-manifest, contract gap — e.g. CD) · `shelf` (skill on disk, not in dispatch-registry). A **CI parity test** (mirroring `tests/parity/test_skill_md_sanctum_alignment.py`) fails red if the narratable claim diverges from what the manifest routes. Marcus **reads it as fact; never generates capability claims** from model knowledge. Manifest is already a `block_mode_trigger_paths` member → lockstep regime carries enforcement. (Murat #2/#3 + Winston DP1 + Marcus DP1 — unanimous.)

**DP2 — REFRAMED: no collision, no rename.** There is exactly **one Tracy** (research-shaped-intent enricher) and **Texas** (retrieval dispatcher); the boundary is already built and module-tested (Irene→Tracy→Texas bridge `emit_plan_lock_fanout`/`IreneTracyBridge`; Epic 27-0 retrieval closed). The "typography" label is a **single stale line at `specialist-registry.yaml:130-136`** — a registry-truth bug, the canonical DP1 smoking gun. DP2 deliverable: **(a) correct the stale registry line** (Claude-direct hygiene, no blast radius) + **(b) wire the already-built bridge through `production_runner.py`** (the `tracy_bridge` kwarg `app/marcus/facade.py:238,305` already exposes but the trial CLI never passes — the filed `tracy-gap-fill-lane-not-adopted-by-production-runner`). Defer Epic 17 (hypothesis-mode). NOT a naming decision. (Marcus, independently corroborated by Winston: the producer ABC docstring already pre-commits "Tracy research".)

**DP3 — workbook render-target: (b) deterministic producer, scoped Markdown→DOCX for v1.** `python-docx>=1.1` is already in `pyproject`; **no PDF library exists on disk** (no pandoc/weasyprint/reportlab) → PDF is a real new dependency, **deferred + named** as a future additive leg. Markdown is the canonical artifact + citation-injection substrate; DOCX is the client-facing deliverable. Producer = a `ModalityProducer` subclass in `app/marcus/lesson_plan/` (4th sibling to `blueprint`; `leader-guide`/`handout`/`classroom-exercise` already reserved-pending). Adding `"workbook"` to the closed `MODALITY_REGISTRY` is a **schema-version bump + amendment per the registry's AC-C.4 rule**, not a free edit. Gamma doc-mode (a) foreclosed on evidence (memory `reference_gamma_generations_401_throttle`: Classic-cards-only). (Winston DP3, concurred Irene/Marcus/Mary/John.)

**DP4 — lesson-plan-as-driver: Irene Pass-1 additive emission of a real workbook CONTENT MODEL** (not a shopping list). Each workbook section binds a `learning_objective_id` (asset-lesson pairing invariant extended to collateral); carries an explicit **per-section depth-delta contract** (what depth is deferred OFF the glance-slide INTO the workbook — this is what legitimizes the tight VO); exercises carry **Bloom level + source-grounded answer key**; research-enrichment goals expressed as **pedagogical intent** ("learner needs the primary-source basis for the 23% figure"), not raw fetch queries. Empty case = explicit **`collateral: none`** declaration (decision on record, not an absent key). Additive / no-regression. (Irene A4-1/A4-4.)

**DP5 — minimal first-run slice (LOCKED, tightened):** predefined workbook spec + predefined research-enrichment goals on the **frozen `tejal-apc-c1-m1-p2-trends`** deck; deck pipeline unchanged (clustered, per-sub-slide A/B, tight VO, no ghost numbers); workbook produced as a paired durable DOCX with **≥1 cited research entry traced to a real `source_ref` linked to slide content**. **Honesty rider (Marcus):** on the first run **Marcus is the scripted-confirm narrator, NOT the conversational elicitor** (the elicitation REPL is the arc finale). v1 prose must not imply live elicitation. The open-ended "state purpose → agents design the asset" pattern is **v-next, in ink**. (John A1 + Mary + Marcus DP5.)

**DP6 — frozen-Gamma reuse: a CHECKABLE path-intersection gate, not a policy sentence.** Define a **`slide_production_paths`** set in `pipeline-manifest.yaml` (v4.2 pack + generator, Pass-1 clustering/chunking, per-sub-slide A/B chooser, VO figure-grounding gate, Gamma adapter, numCards/text_mode). Pre-run predicate: `fresh_gamma_required := (git diff --name-only <base>..<head>) ∩ slide_production_paths ≠ ∅`. Non-empty → **frozen reuse BLOCKED**, run must generate fresh + pass the deck no-regression suite. Empty → reuse permitted AND the run record **stamps `gamma: frozen, reuse_justified_by: empty-intersection@<sha>`**. **Stale-pack reuse counts as non-empty** (frozen deck pack version < HEAD pack version → fresh required). **Frozen-reuse runs are ineligible to assert deck no-regression** (recorded by construction). (Murat DP6 — codifies the operator's stated rule into a gate.)

**DP7 — RESEQUENCED client-value-first (supersedes strawman §3 DP7).**

> **Story 0 (hygiene, Claude-direct, immediate):** correct the stale Tracy registry line. *(DP2a)*
>
> **Slice 1 — CLIENT VALUE (the workbook the client asked for):**
> - **S1 — Lesson-plan collateral+research spec** (Irene Pass-1 additive emission; the DP4 content model). *(additive, no-regression)*
> - **S2 — Workbook producer** (`ModalityProducer` subclass `workbook`; Markdown→DOCX; figure-embedding in v1; prose-delegation step; L2 audit hook in place). *(consumes transcript + S1 spec)*
> - **S3 — Thin research wiring** (pass the existing Irene→Tracy→Texas bridge through `production_runner.py`; cited entries land in the workbook; L2 fail-mode for citations). *(DP2b; gated only by Story 0)*
>
> **Slice 2 — HONEST INTERLOCUTOR (Marcus):**
> - **S4 — Marcus capability-overlay** (generated + closed-enum + CI parity + adversarial over-promise probe). **Parallelizable with Slice 1** (independent, small; also catches the Tracy bug class). Not a Slice-1 blocker.
> - **S5 — Marcus interlocution loop** (the LLM stop-and-chat REPL replacing the scripted narrator; reads `capability-state` as fact). The arc finale.

Slice 1 ships the client's workbook; Marcus-as-interlocutor is the finale, not the foundation. (John A2 + Mary A2, adopted unanimously.)

---

## 3. Consolidated honesty gates (binding; ride alongside every story)

- **G1 — Workbook body-assertion fidelity (Mary A1 + Irene A4-2, sharpened by Winston).** The "fuller narrative" composes freely in voice but asserts only **deck-traceable or `source_ref`-traceable** claims. ⚠️ **Honest scope:** the L2 engine (`source_fidelity_audit.py`) is **numeric-only + warn-only today** (semantic leg is a stub). So v1 = **L2 over workbook numerals run in FAIL mode** (`unsourced_numeric == 0`) + a **NAMED operator spot-check** for non-numeric claim↔source faithfulness. The general semantic claim-citation audit is **net-new/deferred** — file it; do NOT claim L2 already covers it.
- **G2 — Citation fidelity (Murat #4 + Mary).** Every workbook citation resolves to a real `source_ref` in this run's retrieval set; **L2 fail-mode, `unsourced_citations == 0`**; L2 report + citation→source_ref→source-hash manifest attached to the run record. Claim↔source *support* faithfulness = the named operator spot-check (G1), not silently assumed.
- **G3 — Exercise fidelity (Irene).** Exercises authored backward from sourced content + objectives; answer keys cite `source_ref`; audited like the body.
- **G4 — No reading-path halo (Mary, all-honored).** This arc does **NOT** advance the reading-path fresh-naive-holdout; close-out states so explicitly. No generalization claim rides on workbook work.
- **G5 — Marcus over-promise probe (Murat #1/#3).** A fixed, version-controlled probe corpus targeting `present-but-unrouted`/`partial`/`shelf` capabilities; gate asserts Marcus's structured intent makes **zero false-`wired` claims** (mechanical judge on the intent payload, cross-checked vs the live dispatch graph); **first-run-stands, single false-`wired` = RED**. Gating on every Marcus story revision.
- **G6 — Believed-green discipline:** per-story acceptance is the **artifact witness**, never a green unit suite (anti-patterns G1/H1–H4). No mocks; live APIs; first-run-stands; no retry-to-green.

---

## 4. One OPEN sequencing question — RESOLVED by evidence (recorded per Marcus's flag)

Marcus flagged: does this braid run concurrent-with / after / displacing the ratified **clustering-trial-first** pathway (`forward-development-sequence-2026-06-24.md` made clustering the centerpiece gating the next trial, with the real Marcus SPOC as Phase 4 "after the clustering trial delivers near-term value")?

**Resolution:** clustering **terminal-(b) is already ACHIEVED** (trial `c2c6dcbf`, banked by the operator) — so Phase-4's gate ("after clustering delivers near-term value") **is met**. The operator's `/goal` this session explicitly launched THIS braid. Therefore the braid is the **legitimate next arc, not a displacement** of the ratified pathway. Residual: clustering-1.3 polish (chunk directive / keep-dense marker / transition timing) remains parked and **may run concurrently or fold into a later trial** — low-stakes, non-blocking. Recorded; no operator pause required.

---

## 5. Spec-authoring contract (what "ready-to-implement" requires)

Per voice convergence, the specs to author are: **Story 0** (Claude-direct hygiene), **S1–S3** (Slice 1, the client workbook), **S4** (capability-overlay, parallelizable), **S5** (interlocution REPL, finale). Each substrate story: **party green-light (this doc) → NEW CYCLE (dev T1–T10 → Claude T11 `bmad-code-review` + close) → small-scale live run → iterate.** Slice-1 first-run validates on frozen-Gamma reuse (DP6 empty-intersection); S2/S3 that touch nothing slide-affecting reuse the frozen tejal deck; any clustering/A-B-touching change triggers fresh Gamma per DP6.

**Concurrence to obtain:** after S0–S3 specs are authored to these amendments, a light party concurrence pass confirms ready-to-implement → launch dev.

---

## 6. Concurrence outcome (2026-06-24 PM-2) — UNANIMOUS CONCUR, ready to implement

Specs S1–S4 authored to the amendments and re-read by a 3-voice concurrence panel (the owners of the hardest amendments):
- **Murat — CONCUR-WITH-NIT.** All five of his amendments landed as *mechanically checkable contracts with RED proofs*: DP6 path-intersection predicate + stamp (S2 §DP6; S3 §3.5/AC-D9/AC-O3); artifact-witness acceptance (S1 AC-10/11, S2 AC-12, S3 AC-O1, S4 AC-2/7); L2 FAIL-mode (S3 AC-D6/O2 `unsourced_citations==0`; S2 AC-9 `unsourced_numeric==0`) with the semantic-scope fence held; generated overlay + injected-drift RED (S4 AC-6) + zero-false-`wired` mechanical-judge probe (S4 AC-7/10); the over-promise probe as a *recurring* contract test on every Marcus revision.
- **Mary — CONCUR.** No honesty gate missing, no v1 scope unfenced. G1 body-fidelity split (numeric L2 fail-mode + named operator prose spot-check) present and the general semantic audit honestly marked net-new/deferred in *three* places (S2 G1 + v-next fence + deferred-inventory; S3 §5). G4 no-halo in S1/S2/S3; every carve-out (asset-design pattern, Epic 17, PDF, worksheet affordances, Marcus REPL) in ink with a deferred-inventory home; client-value-first + S4-parallelizable honored; G3 exercise/answer-key fidelity present.
- **Marcus — CONCUR-WITH-NIT.** S4 overlay is generated-not-authored (substrate-verified Tracy derives `present-but-unrouted`); S3 passes the bridge through BOTH walks; the DP5 scripted-confirm-not-elicitor rider is honored (S3 §6, S4 v1 fence); the overlay gives him honest vocabulary ("research exists but isn't on the run path until S3").

**Carried NITS (non-blocking for dev LAUNCH; address at T1 / fold into dev-prompts):**
1. **WorkbookSpec single-source-of-truth (Murat+Mary, same nit).** S1's `app/marcus/lesson_plan/collateral_spec.py` is the canonical home; **S2 imports `WorkbookSpec` from it, does not re-derive.** Add this one-liner to the S1/S2 dev-prompts. Pin one shape, one run-record key (reconcile S2 `research_supplements` arg vs S3 `research_entries` run-record key at the S2↔S3 contract check).
2. **DP6-enablement — define `slide_production_paths` (Marcus).** The DP6 set does NOT yet exist in `pipeline-manifest.yaml`; offline dev ACs test the predicate against *fixture* diffs (so dev is NOT blocked), but the **live-run** DP6 stamp (S2 AC-12 / S3 AC-O3) needs the real set defined first. **Disposition: a Story-0b DP6-enablement task** — a Tier-1 *additive* append of `slide_production_paths` to the manifest (it touches a `block_mode_trigger_paths` member → under the lockstep regime, but additive/governance-light), landing **before the live-run legs of S2/S3**. Not a blocker for the offline dev work.
3. **Code-review watch-items (Murat):** S3 two-walk attach should *default to both-walks* and prove single-walk-reachability by executing a real continuation (not assert); S4 add a dedicated AC pinning the `partial`-before-`wired` decision-table ordering. Harvest at T11.

**VERDICT: the braid specs (S0 done; S1–S4 authored) are READY TO IMPLEMENT.** Party (6/6 green-light + 3/3 concurrence, no impasse) concurs. Dev launch path: NEW CYCLE per story (dev T1–T10 → Claude T11 `bmad-code-review` + party close) → small-scale live run → iterate; Story-0b (DP6 set) before S2/S3 live legs; S5 (interlocution REPL) spec authored when S4 closes.
