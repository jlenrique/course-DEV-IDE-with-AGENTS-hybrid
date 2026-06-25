# Spec — Braid Slice 1 / Story S2: Workbook producer

**Status:** ready-for-dev
**Class:** S (substrate — new `ModalityProducer` subclass + closed-registry widening + schema-version bump)
**Arc:** Braid (Marcus-interlocutor + research-foundations + lesson-planning-with-workbook-companion). One coherent arc; **Slice 1 — CLIENT VALUE**, story S2.
**Gate mode:** dual-gate (closed-set widening of `MODALITY_REGISTRY` = governed change per AC-C.4 + a schema-version bump + a new render dependency surface (DOCX) + an honesty-gate hook → not a focused single-module change).
**Authority:** `_bmad-output/planning-artifacts/braid-green-light-ratification-2026-06-24.md` (DP3, DP4-consumer, DP5, DP6, G1/G2/G3/G6; party-mode GREEN-WITH-AMENDMENTS 6/6, no impasse). Strawman context: `_bmad-output/planning-artifacts/braid-strawman-2026-06-24.md`. CLAUDE.md sprint-governance + Lesson-Planner dev-agent references.
**Execution model:** NEW CYCLE — dev agent runs T1–T10 (RED-first) → Claude T11 (`bmad-code-review` 3-layer + commit + flip done). Per `feedback_new_cycle_codex_dev_handoff`.
**r_tier:** R2 · **t11_tier:** standard · **lookahead_tier:** 2 · **files_touched (new + ~3 edits):** new `app/marcus/lesson_plan/workbook_producer.py`, new `app/marcus/lesson_plan/workbook_spec.py` (the S1-spec input shape consumed here), edit `app/marcus/lesson_plan/modality_registry.py` (+`ModalityRef` literal, +registry entry, +`SCHEMA_VERSION` bump), edit `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` (amendment entry), + new tests. NO `state/config/pipeline-manifest.yaml` / pack / L1 / lockstep path → **not block-mode**.

---

## Problem / Why this story

The braid's client deliverable is a **workbook/worksheet companion** to the narrated deck: it carries the **transcript + a fuller narrative** (the depth deliberately kept OFF the glance-slides and out of heard-only narration — the dual-coding partner to the tight VO the clustering arc just delivered), **exercises**, and **research + citations**. DP3 locked the render path: a **deterministic `ModalityProducer` subclass**, NOT Gamma doc-mode (foreclosed on evidence — `reference_gamma_generations_401_throttle`: Gamma API is Classic-cards-only, doc/page mode is API-inaccessible).

The substrate is real and mostly already built:
- `app/marcus/lesson_plan/modality_producer.py::ModalityProducer` — the ABC every producer subclasses (confirmed: `__init_subclass__` enforces `modality_ref`/`status` ClassVars at class-definition time; `produce(plan_unit, context) -> ProducedAsset`).
- `app/marcus/lesson_plan/blueprint_producer.py::BlueprintProducer` — the **first concrete sibling** (the pattern this story mirrors: deterministic, offline, markdown emit, repo-relative output under `_bmad-output/artifacts`, `ProducedAsset` return with `fulfills`).
- `app/marcus/lesson_plan/modality_registry.py::MODALITY_REGISTRY` — the closed `MappingProxyType`. Confirmed reserved-pending entries: **`leader-guide`, `handout`, `classroom-exercise` (all `status="pending"`, `producer_class_path=None`)**. `"workbook"` is **NOT** among them — it is a **new key**, so adding it is a closed-set widening per **AC-C.4**.
- `app/specialists/_shared/source_fidelity_audit.py::audit_numeric_provenance` — the **L2 numeric leg**, WARN-ONLY/NON-GATING today (semantic leg is an explicit STUB; `SEMANTIC_TRIPWIRE = None`). This is the L2 hook the workbook producer wires in from S2.

**Substrate facts confirmed (Winston's findings — verified in this spec):**
- ✅ `python-docx>=1.1,<2` IS in `pyproject.toml` (line 24) → DOCX render is a free, already-shipped dependency.
- ✅ **NO PDF library on disk** — grep for `pandoc|weasyprint|reportlab|fpdf|pdfkit` in `pyproject.toml` returns nothing. PDF is a real new dependency → **DEFERRED + named** (see v-next fence). This is exactly why DP3 scopes v1 to **Markdown→DOCX**.
- ✅ `MODALITY_REGISTRY` reserved-pending entries are `leader-guide`/`handout`/`classroom-exercise`; `"workbook"` is net-new.

The S1 collateral content model (Irene Pass-1 additive emission — DP4) is the **upstream sibling story**: it produces the per-section workbook spec (sections bound to `learning_objective_id`, per-section depth-delta contract, exercises with Bloom level + answer key, research-enrichment goals as pedagogical intent, `collateral: none` empty case). **S2 consumes that spec as input.** Because S1 lands in lockstep with S2 in Slice 1, this story defines the **minimal consumed shape** (`WorkbookSpec`) it needs and treats S1 as the producer of that shape; the spec input is a typed Pydantic model, not a free dict.

---

## Decision encoding (ratification DP3 + Irene's amendments + gates — all binding)

1. **Producer = new `ModalityProducer` subclass.** Class `WorkbookProducer(ModalityProducer)` in `app/marcus/lesson_plan/workbook_producer.py`, `modality_ref = "workbook"`, `status = "ready"`. 4th concrete sibling to `BlueprintProducer`. **Adding `"workbook"` to the closed `MODALITY_REGISTRY` is a schema-version bump + amendment per AC-C.4** — NOT a free edit. Concretely: (a) widen the `ModalityRef` Literal with `"workbook"`; (b) add the `ModalityEntry(modality_ref="workbook", status="ready", producer_class_path="app.marcus.lesson_plan.workbook_producer.WorkbookProducer", description=...)`; (c) bump `modality_registry.SCHEMA_VERSION` `"1.0" → "1.1"` (minor — additive new enum value, v1.0-compatible); (d) add a `SCHEMA_CHANGELOG.md` entry. (`produced_asset.py::ModalityRef` is imported from `modality_registry`, so `ProducedAsset.modality_ref="workbook"` becomes valid automatically once the Literal is widened — assert this round-trips.)

2. **Render: Markdown (canonical) → DOCX (client deliverable) via python-docx.** Markdown is the **canonical artifact + the citation-injection substrate** (S3 injects cited entries into the Markdown). DOCX is the **client-facing deliverable**, rendered FROM the Markdown via `python-docx`. Two artifacts, one source of truth. **Do NOT author "PDF/DOCX" as a single target.** **PDF is explicitly DEFERRED to v-next** (named, with the owned-dependency-decision note — see fence). Both artifacts written repo-relative under `_bmad-output/artifacts/workbooks/` (mirroring `DEFAULT_BLUEPRINT_OUTPUT_ROOT` discipline + the `_resolve_output_root` repo-root containment guard).

3. **Prose-delegation step (Irene A4-3) — DO NOT collapse "transcript backbone" into "transcript = workbook text".** The Pass-2 transcript is the workbook's **SCAFFOLD, not its text.** Pass-2 narration is written for a *listener watching a slide* — it is full of slide-deixis ("here you see…", "as this chart shows…", "notice on the right…"). The workbook is **read prose**: each transcript segment must be **re-voiced into self-contained read-prose** that stands without the slide. This is a **named writer step**: the **writer (Paige / Sophia) produces prose against Irene's per-section brief; Irene validates behavioral intent at handoff.** In v1 the producer is deterministic, so the prose-delegation step is modeled as an **injectable re-voicer seam** (`prose_revoicer: ProseRevoicer | None`) with a deterministic default that (i) embeds each segment verbatim under its `segment_id` AND (ii) emits an explicit per-segment **`<!-- REVOICE-REQUIRED: writer (Paige/Sophia) → self-contained read-prose; Irene validates -->` review marker** (same review-marker discipline as `BlueprintProducer`'s `HUMAN_REVIEW_SECTION_HEADING` / `IRENE_REVIEW_MARKER`). The seam lets the live writer step replace the default without a producer change. **The default MUST NOT silently pass deixis-laden transcript text off as finished read-prose** — the review marker is the honesty guard that "transcript backbone" did not collapse into "workbook text".

4. **Figure-embedding in v1** (image + caption + `source_ref`). For each Pass-2 segment that references a slide figure/image, the workbook **embeds the image** (via `python-docx` `add_picture` for DOCX; a Markdown image ref `![caption](path)` for the canonical MD) **with a caption AND the `source_ref`** that grounds it. **Worksheet fill-in affordances (blank answer lines, response boxes, interactive form fields) are explicitly DEFERRED to v-next** (see fence).

5. **L2 audit HOOK in place from S2** (Irene's coordination note: do NOT bolt it on after S3). The producer calls `audit_numeric_provenance(...)` over the workbook body text against the run's source set as part of `produce()` and **attaches the report to the run record / returns it on a sidecar**. In S2 it runs over a **thin citation/source set** (S3 fills the real research set) — that is acceptable; the *wiring must exist now* so S3 only adds data, not plumbing. **Honesty-mode wrapper:** S2 converts the WARN-ONLY return into a **FAIL-mode gate** at the *workbook* boundary: assert `report["buckets"]["unsourced_numeric"]["count"] == 0` (G1). The underlying module stays warn-only/non-gating (do NOT mutate `source_fidelity_audit.py` — it is a frozen-neck reader per its own F4 amendment); the FAIL-mode decision lives in the producer/gate wrapper.

6. **Dual-coding non-redundancy (Murat #2).** The workbook depth MUST NOT be a verbatim copy of the VO script. Acceptance includes (a) a **diff/superset check** proving the workbook narrative is a **proper superset** of the VO script (`workbook_narrative ⊋ VO_script` — strictly more content than the heard narration alone) AND (b) a **transcript-segment-id coverage map** (every Pass-2 `segment_id` appears in the workbook, line-level traceable; no segment dropped, no phantom segment invented). The depth-delta IS the legitimization of the tight VO (DP4): what's deferred OFF the glance-slide lands HERE.

---

## Honesty gates (binding; ride alongside this story — from ratification §3)

- **G1 — Workbook body-assertion fidelity.** v1 = **L2 over workbook numerals in FAIL mode** (`unsourced_numeric == 0`, per #5 above) **+ a NAMED operator spot-check for non-numeric prose↔source faithfulness** (the operator reads N prose claims and confirms each is deck-traceable or `source_ref`-traceable; recorded in Completion Notes). ⚠️ **Honest scope:** the L2 engine is **numeric-only + warn-only today** (semantic leg is a stub). **The general semantic claim-citation audit is net-new / DEFERRED — file it as a follow-on; do NOT claim L2 already covers it.** (See Deferred-inventory follow-on below.)
- **G2 — Citation fidelity.** Every workbook citation resolves to a real `source_ref` in this run's retrieval set; **L2 FAIL-mode `unsourced_citations == 0`**; report + citation→`source_ref`→source-hash manifest attached to the run record. In S2 the citation set is thin (S3 fills it) — the **wiring + the assertion path exist now**; claim↔source *support* faithfulness = the named operator spot-check (G1), not silently assumed.
- **G3 — Exercise / answer-key fidelity.** Exercises authored backward from sourced content + objectives; answer keys cite `source_ref`; audited like the body. v1 produces ≥1 exercise carrying a Bloom level + a source-grounded answer key (consumed from the S1 spec); the producer asserts each answer key's `source_ref` is present.
- **G4 — No reading-path halo.** This story does **NOT** advance the reading-path fresh-naive-holdout. Close-out states so explicitly. No generalization claim rides on workbook work.
- **G6 — Believed-green discipline.** Per-story acceptance is the **artifact witness** (the produced DOCX+MD on the frozen tejal deck), never a green unit suite. No mocks; live deps; first-run-stands; no retry-to-green.

(G5 — Marcus over-promise probe — is a Slice-2 / Marcus-story gate; N/A here, noted for completeness.)

---

## DP6 — frozen-Gamma reuse (applies; note it)

This story is **slide-independent**: it consumes the *already-produced* transcript + figures of the frozen **`tejal-apc-c1-m1-p2-trends`** deck and produces a paired durable workbook. The frozen deck bundle is on disk at `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/` (run id `C1-M1-PRES-20260419B`), containing `segment-manifest.yaml` (schema 1.1, ~32 segments, each a unique `id`), `narration-script.md`, `authorized-storyboard.json`, and `assembly-bundle/visuals/` (slide PNGs) — these are the read-only inputs. It touches **nothing in `slide_production_paths`** (no v4.2 pack/generator, no Pass-1 clustering, no per-sub-slide A/B chooser, no VO figure-grounding gate, no Gamma adapter, no numCards/text_mode). Therefore per **DP6**: `fresh_gamma_required := (git diff <base>..<head>) ∩ slide_production_paths = ∅` → **frozen reuse PERMITTED**; the first-run record **stamps `gamma: frozen, reuse_justified_by: empty-intersection@<sha>`** and is, by construction, **ineligible to assert deck no-regression** (this story makes no deck-regression claim). Reuse the frozen tejal deck artifacts (storyboard, narration/segment-manifest, slide images) as read-only inputs.

---

## T1 Readiness (dev agent reads BEFORE any code)

Per CLAUDE.md Lesson-Planner dev-agent references + the substrate this story extends:
1. `docs/dev-guide/pydantic-v2-schema-checklist.md` — the 14 schema idioms (`WorkbookSpec` + any sidecar models are Pydantic v2: `extra="forbid"`, `frozen=True`, `validate_assignment=True`, tz-aware datetimes, closed enums with triple-layer red-rejection, `Field(exclude=True)+SkipJsonSchema` for internal audit fields).
2. `docs/dev-guide/dev-agent-anti-patterns.md` — schema / test-authoring / Marcus-duality traps.
3. `docs/dev-guide/story-cycle-efficiency.md` — K-floor discipline (target 1.2–1.5× K), DISMISS rubric for cosmetic NITs.
4. **Substrate reads (verify, don't assume):** `app/marcus/lesson_plan/blueprint_producer.py` (the sibling pattern — output-root containment, deterministic body renderer seam, review markers, `ProducedAsset` return), `app/marcus/lesson_plan/modality_producer.py` (`__init_subclass__` contract), `app/marcus/lesson_plan/produced_asset.py` (`ProducedAsset` fields + `fulfills` regex `^[a-z0-9._-]+@(?:0|[1-9]\d*)$` + Q-R2-A `source_plan_unit_id == fulfills.split("@",1)[0]` cross-field invariant), `app/marcus/lesson_plan/modality_registry.py` (the AC-C.4 widening rule + `SCHEMA_VERSION` + the `MappingProxyType` immutability), `app/specialists/_shared/source_fidelity_audit.py` (`audit_numeric_provenance` signature + WARN-ONLY contract — DO NOT mutate it).
5. **Reference precedent (deterministic doc producer):** `app/specialists/compositor/_act.py` (Class-D2 deterministic assembly pipeline) + `skills/compositor/SKILL.md` — cite as the "deterministic regenerate-a-doc" precedent for offline, hash-stable, repo-relative artifact emission.
6. **Transcript backbone source:** the Pass-2 segment manifest. The structured per-segment shape is `app/specialists/irene/authoring/pass_2_template.py::SegmentManifestSegment` — per-segment id field is **`id`** (`min_length=1`; e.g. `apc-c1m1-tejal-20260419b-motion-card-01`), with `slide_id`, `narration_text`, `behavioral_intent`, `visual_file` (the PNG path), and **`visual_references: list[VisualReference]`** (each carries `element`, `location_on_slide`, `narration_cue`, `perception_source`). `visual_references` + `visual_file` are the figure-embed source for AC-7; `narration_text` per `id` is the transcript-scaffold source for AC-5/AC-6. (The JSON-schema fragment at `state/config/schemas/segment-manifest.schema.json` is the reading-path lockstep slice; the Pydantic model above is the full shape.)
7. **Run the Lesson-Planner governance validators** before finalize and before dev: `python scripts/utilities/validate_lesson_planner_story_governance.py <this-spec>` (self-remediate first, escalate second per CLAUDE.md). Since this is a braid (non-migration) story, the migration sandbox-AC validator does not apply; ACs still follow "verify via shipped deps, not operator CLIs".

**Build contract:** new code under `app/marcus/lesson_plan/`; tests under `tests/` mirroring the lesson_plan test layout; invoke `.venv/Scripts/python.exe -m pytest`, `ruff`, `lint-imports` freely (allowed per `feedback_venv_python_allowed`). RED-first: write the failing ACs first (T1–T2), implement to green (T3–T9), self-review (T10).

---

## Acceptance Criteria (RED-first; ARTIFACT-level on the frozen tejal deck; all dev-agent verifiable via shipped deps — no operator CLIs)

**Schema / registry-widening ACs:**
- **AC-1 (registry widening = governed):** `ModalityRef` Literal includes `"workbook"`; `MODALITY_REGISTRY["workbook"]` is a `ModalityEntry(status="ready", producer_class_path="app.marcus.lesson_plan.workbook_producer.WorkbookProducer")`; `list_ready_modalities()` now contains `"workbook"`; the `MappingProxyType` immutability is preserved (mutation still raises). `modality_registry.SCHEMA_VERSION == "1.1"`. A `SCHEMA_CHANGELOG.md` entry titled `Modality Registry v1.1 — <date> — Braid S2 Workbook Producer` exists and names the additive `"workbook"` value + the AC-C.4 rationale.
- **AC-2 (producer contract):** `WorkbookProducer` subclasses `ModalityProducer`, `modality_ref="workbook"`, `status="ready"`; `__init_subclass__` accepts it (class-definition succeeds); `produce(plan_unit, context)` returns a `ProducedAsset` whose `modality_ref=="workbook"`, `fulfills == f"{plan_unit.unit_id}@{context.lesson_plan_revision}"`, and `source_plan_unit_id == plan_unit.unit_id` (Q-R2-A passes). `produce` does not mutate `plan_unit`/`context`.

**Render ACs (Markdown canonical → DOCX deliverable):**
- **AC-3 (dual artifact, MD canonical):** `produce(...)` writes BOTH a `.md` (canonical) and a `.docx` (deliverable) under `_bmad-output/artifacts/workbooks/`, repo-relative; the output-root containment guard rejects an absolute / traversal output root (mirror `BlueprintProducer._resolve_output_root`). The DOCX is rendered FROM the canonical Markdown (assert the DOCX section/heading text is derived from the MD, not independently composed). `ProducedAsset.asset_path` points at the canonical `.md` (the citation-injection substrate S3 consumes); the DOCX path is recorded on the returned sidecar/asset record.
- **AC-4 (DOCX opens + has every spec'd section):** the produced `.docx` opens via `python-docx` (`docx.Document(path)`); every section named in the `WorkbookSpec` (e.g. Overview, Transcript-narrative, Figures, Exercises, References) is present as a heading; assert by reading the document's paragraphs/headings back. **(No PDF assertion — PDF is out of scope.)**

**Transcript / prose-delegation ACs:**
- **AC-5 (segment-id traceability, line-level):** every Pass-2 `segments[].id` from the frozen tejal segment manifest appears in the canonical MD as a traceable anchor; build a coverage map `{segment_id: present}` and assert 100% coverage, zero phantom (no MD segment anchor that is not a real manifest `id`).
- **AC-6 (prose-delegation seam, no silent passthrough):** the default deterministic build emits, per transcript segment, the verbatim segment text AND an explicit `REVOICE-REQUIRED: writer (Paige/Sophia) → self-contained read-prose; Irene validates` review marker (assert the marker is present for every segment). An injected `prose_revoicer` replaces the default body for a segment WITHOUT a producer-class change (assert the seam is honored). The producer never asserts deixis-laden transcript text is finished read-prose (the marker is the guard).

**Figure ACs:**
- **AC-7 (figure embed in v1):** for ≥1 frozen tejal segment that references a slide figure/image, the workbook embeds the image (DOCX `add_picture` succeeds → the docx contains an image part; MD carries `![caption](path)`) WITH a caption AND the `source_ref`. Assert the embedded image part exists in the DOCX and the caption+`source_ref` strings are present. **(Worksheet fill-in affordances NOT asserted — deferred.)**

**Dual-coding / non-redundancy ACs:**
- **AC-8 (workbook ⊋ VO script):** a superset/diff check proves the workbook narrative body is a **proper superset** of the VO script text (strictly more content; not a verbatim copy) — assert `len(workbook_narrative_tokens - vo_script_tokens) > 0` AND `vo_script` content is represented (coverage) so it's a true superset, not a disjoint rewrite. The depth-delta is non-empty.

**Honesty-gate ACs:**
- **AC-9 (L2 hook in place, FAIL-mode):** `produce(...)` calls `audit_numeric_provenance(workbook_body_text, source_text, research_supplements=...)` and the producer/gate wrapper asserts `report["buckets"]["unsourced_numeric"]["count"] == 0` (G1 FAIL-mode) before the asset is accepted; the report is attached to the run record / returned on the sidecar. `source_fidelity_audit.py` is UNMODIFIED (assert no edit to that file in the diff). Over the thin S2 source set this runs and passes; the wiring is the deliverable.
- **AC-10 (citation fidelity wiring, G2):** every citation present in the workbook (thin set in S2) resolves to a real `source_ref` with an attached `source_ref`→hash manifest; the FAIL-mode assertion path (`unsourced_citations == 0`) exists and runs (even if the set is small in S2). The path is the deliverable; S3 fills the data.
- **AC-11 (exercise fidelity, G3):** the produced workbook contains ≥1 exercise carrying a Bloom level and a source-grounded answer key; the producer asserts each answer key's `source_ref` is present (non-null, resolvable).

**Witness / non-regression:**
- **AC-12 (artifact witness on frozen tejal):** running the producer on the frozen `tejal-apc-c1-m1-p2-trends` deck inputs (DP6 frozen reuse, empty-intersection stamp) produces a real DOCX+MD pair on disk satisfying AC-3..AC-11 — this paired durable artifact IS the per-story acceptance witness (G6), not a green unit suite.
- **AC-13 (non-regression):** existing `app/marcus/lesson_plan` tests + the modality-registry / produced-asset / modality-producer suites stay green; `BlueprintProducer` and the `slides`/`blueprint`/`leader-guide`/`handout`/`classroom-exercise` registry entries are unchanged; `ruff` + `lint-imports` green. Additive only.

---

## v1 ⟷ v-next fence (in ink)

**v1 (THIS story):**
- Markdown (canonical) → DOCX (deliverable) via `python-docx`.
- Figure embed: image + caption + `source_ref`.
- Prose-delegation seam with deterministic default + `REVOICE-REQUIRED` markers.
- L2 numeric audit hook in place, FAIL-mode at the workbook boundary, over a thin source set.
- Citation-fidelity + exercise-fidelity wiring + assertion paths present (data thin until S3).
- Frozen tejal deck, frozen-Gamma reuse (DP6 empty-intersection).

**v-next (DEFERRED — named, do not build here):**
- **PDF render leg.** *Owned-dependency-decision note:* PDF requires a real new dependency (pandoc / weasyprint / reportlab — NONE present on disk). Adding it is a deliberate dependency choice, NOT a free additive edit; it gets its own story + dependency-governance decision. Markdown→DOCX ships first precisely because both are already on disk.
- **Worksheet fill-in affordances** (blank answer lines, response boxes, interactive DOCX form fields).
- **Live prose-delegation** (the writer step — Paige/Sophia — actually running against Irene's brief in the production flow, replacing the deterministic-default `REVOICE-REQUIRED` markers). The *seam* ships in v1; the *live writer wiring* is v-next (and couples to the Marcus-interlocutor finale, Slice 2).
- **The general semantic claim-citation audit** (the L2 semantic leg — net-new; the `source_fidelity_audit.py` semantic stub `SEMANTIC_TRIPWIRE=None` is deliberately un-tuned until ≥3 tracked runs). v1 covers numerals only (FAIL-mode) + named operator spot-check for prose. **File this as a follow-on; do NOT claim L2 covers it.**
- The open-ended "state purpose → agents design the asset" pattern (v1 is a predefined workbook spec; DP5).

---

## Out of scope (explicit)

- **S1 (Irene Pass-1 collateral+research spec emission)** — the upstream sibling that *produces* the `WorkbookSpec`. S2 defines + consumes the minimal `WorkbookSpec` shape; it does NOT implement Pass-1 emission. (If S1 lands first, S2 imports its shape; if co-developed, S2 owns the consumed-shape contract and S1 conforms.)
- **S3 (thin research wiring)** — passing the Irene→Tracy→Texas bridge through `production_runner.py` so real cited entries land in the workbook. S2 builds the *injection substrate* (canonical MD) + the *citation-fidelity assertion path*; S3 fills the data.
- **Slice 2 (Marcus capability-overlay S4 + interlocution REPL S5)** — entirely separate arc; G5 over-promise probe lives there.
- No `pipeline-manifest.yaml` / pack / L1 / lockstep edits (not block-mode). No deck-regression claim (frozen reuse, by construction).

---

## Deferred-inventory follow-ons (file per CLAUDE.md §"Every new story spec that names a follow-on")

Add to `_bmad-output/planning-artifacts/deferred-inventory.md §Named-But-Not-Filed Follow-Ons`:
1. `braid-workbook-pdf-render-leg` — PDF deliverable; requires a deliberate new-dependency governance decision (pandoc/weasyprint/reportlab); reactivate when a client needs PDF + the dependency is ratified.
2. `braid-workbook-worksheet-fillin-affordances` — fill-in lines / response boxes / DOCX form fields; reactivate post-v1 client feedback.
3. `braid-workbook-l2-semantic-claim-citation-audit` — the general (non-numeric) semantic claim↔source faithfulness audit (the L2 semantic leg); blocked on ≥3 tracked runs before the tripwire is tunable; v1 leans on the named operator spot-check. *(direction may flip if substrate evolves — re-validate at reactivation.)*
4. `braid-workbook-live-prose-delegation` — live writer step (Paige/Sophia against Irene's brief) replacing the deterministic-default revoice markers; couples to the Marcus-interlocutor finale.

---

## Dev notes

- **Mirror `BlueprintProducer` exactly** for the deterministic skeleton: `_resolve_output_root` repo-root containment, `_relative_asset_path`, a default body renderer + an injectable renderer seam, `ProducedAsset` return with `fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}"`. Do NOT re-derive — extend the proven pattern.
- **Do NOT mutate `source_fidelity_audit.py`.** It is a frozen-neck reader (its own F4 amendment). The FAIL-mode wrapper + the `unsourced_numeric==0` assertion live in `WorkbookProducer` (or a thin gate helper in the lesson_plan package), calling the module read-only.
- **`ModalityRef` is single-sourced** in `modality_registry.py` and imported by `produced_asset.py` — widening the Literal there makes `ProducedAsset.modality_ref="workbook"` valid automatically. Add an AC asserting the round-trip so the two surfaces can't drift.
- **Registry widening is a minor (1.X) bump** per the SCHEMA_CHANGELOG semver-for-schemas rule (additive new enum value, v1.0-compatible) — `"1.0" → "1.1"`, not a major. Mirror the existing `Modality Registry v1.0` changelog entry format.
- **DOCX from MD, not parallel.** Keep one composition path (compose the MD model, then render DOCX from that same model) so the canonical artifact and the deliverable cannot diverge — this is what makes S3's MD citation-injection automatically flow into the DOCX on the next produce.
- Keep `produce()` pure of network I/O; deterministic + hash-stable like the compositor Class-D2 precedent. The only "live" surface is the operator spot-check (G1) recorded in Completion Notes, not in code.
- The `WorkbookSpec` consumed shape (this story's input contract): `sections[]` (each binds `learning_objective_id`, a depth-delta string, an ordered list of `segment_id`s it draws from), `exercises[]` (Bloom level + `answer_key` with `source_ref`), `research_enrichment_goals[]` (pedagogical-intent strings — S3 consumes), and the `collateral: none` empty-case sentinel. Pydantic v2, `extra="forbid"`, frozen.

---

## NEW CYCLE handoff

After this spec reaches ready-for-dev and the light party concurrence pass confirms (ratification §5): author `codex-dev-prompt-braid-s2-workbook-producer.md` (per `feedback_new_cycle_codex_dev_handoff`). Dev runs T1–T10 (RED-first, all 13 ACs); Claude T11 reproduces the battery (first-run-stands), runs `bmad-code-review` (3-layer: Blind Hunter / Edge Case Hunter / Acceptance Auditor), remediates MAJORs, commits, and flips status `done`. Then the Slice-1 first-run validates the produced workbook on the frozen tejal deck (DP6 frozen reuse) before S3 wires research.
