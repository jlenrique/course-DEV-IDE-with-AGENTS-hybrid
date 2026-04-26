# Slab 2a Retrospective — Specialist Scaffold Pilot

**Closed:** 2026-04-25
**Slab:** 2a (migration Epic 2a — Specialist Scaffold Pilot)
**Stories:** 2a.1 → 2a.2 → 2a.3 → 2a.4 (4 stories, 14 pts)
**Author:** Claude Opus 4.7 via `bmad-retrospective` at story 2a.4 close
**Authority:** This document is the canonical Slab 2a retrospective per CLAUDE.md "Deferred inventory governance" §1 (Epic-retrospective consultation point) and Story 2a.4 AC-M D12 slab-closing close stub.

---

## If you're reading this at Slab 2b T1, here's what you need

Five things:

1. **A12 generator auto-emit follow-on MUST land before 2b.1 TEMPLATE opens.** Three independent manual `pyproject.toml` C3 ignore-imports edits (Irene 2a.2 + Kira 2a.3 + Texas 2a.4) is the strongest evidence base in the deferred-inventory; do not let it become four. See [`_bmad-output/maps/deferred-work.md`](../maps/deferred-work.md) §A12.
2. **The 9-node scaffold survived three act-body categories.** Narration (Irene), LLM+tool-dispatch (Kira), pure-tool-dispatch (Texas) — same `SCAFFOLD_NODE_IDS` frozenset, same gate-decision binding, same resolution-trail contract. Slab 2b's 14-specialist tranche inherits the proven pattern.
3. **Cache-hit-rate (FR54) doesn't generalize.** It's narration-bound. Pure-tool-dispatch specialists have no LLM prefix to cache; the FR54 substrate stays gated for those categories. Substitute metric per Murat M4: `subprocess-dispatch-latency stability`.
4. **Three drifts vs. epic-text caught at every story T1.** A9 anti-pattern entry retitled to "Epic-doc structural-name drift" with four examples. Standing protocol works.
5. **AC-B-OP at Slab-3.** Live retrieval-provider dispatch evidence is deferred-pending-Slab-3 marcus.dispatch.contract forward-port. Pre-authored helper script + directive template ship uninvokable-on-hybrid-today; Slab-3 reactivates them.

---

## FR coverage closed across Slab 2a

| FR | Description | Story closure | Evidence |
|---|---|---|---|
| **FR9** | Lane-isolated specialist package | 2a.2 + 2a.3 + 2a.4 | `app/specialists/{irene,kira,texas}/` under `run_graph` lane; import-linter C1 KEPT |
| **FR10** | State-subclass discipline | 2a.2 + 2a.3 + 2a.4 | `{Irene,Kira,Texas}Envelope(SpecialistEnvelope)` + matching Returns; NFR-X1 round-trip |
| **FR11** | Per-specialist `model_config.yaml` | 2a.2 + 2a.3 + 2a.4 | Three configs shipped; cascade verified at AC-C of each |
| **FR12** | Per-specialist `expertise/` | 2a.2 + 2a.3 + 2a.4 | READMEs + dotted reference tables; pointer file for Texas's NFR-I5-protected contract |
| **FR13** | `bmad-create-specialist` generator | 2a.1 | Generator + canonical scaffold reference at `app/specialists/_scaffold/` |
| **FR14** | Scaffold conformance framework | 2a.1 | `tests/integration/scaffold_conformance/scaffold_contract.py` frozen |
| **FR15** | Sanctum cold-read | 2a.2 (empty baseline) + 2a.3 (graceful degrade) + 2a.4 (first real populated-and-locked) | sha256 manifest pinned; `SanctumLockViolation` named exception with two-sided trail observation |
| **FR16** | Resolution trail | 2a.2 + 2a.3 + 2a.4 (each appends `ModelResolutionEntry` at `_plan`) | `model_resolution_trail` populated even on Texas pure-tool-dispatch |
| **FR54** | Cache-hit-rate baseline | 2a.2 (empty-sanctum 95.33% median) + 2a.3 (deferred to graceful-degrade — sanctum dir absent) | M1 ACCEPT-WITH-GAP cache-hit-rate clause RETIRED |
| **NFR-I5** | Texas retrieval-contract preservation | 2a.4 | sha256 baseline `ac98ff62…` pinned with hard equality test |
| **NFR-I6** | Cache-prefix stability | 2a.3 (CRLF→LF normalization in `_read_sanctum_digest`) | Cross-platform digest determinism |
| **NFR-X3** | Sanctum fingerprint | 2a.4 (first real populated-and-locked) | 17-file manifest module-level constant |

**Substrate intact across three specialist migrations.** Slab-1 invariants (compile validator additive-only, scaffold-conformance frozen, gate-decision interrupt-binding) held through all four stories.

---

## Cumulative regression intelligence (303 → ~395 trajectory)

| Story | Migration-scoped pass count (placeholder-key) | Net delta | Notes |
|---|---|---|---|
| **Slab 1 close (1.7)** | 286 passed / 5 skipped / 1 deselected | +6 framework tests | scaffold-conformance framework added |
| **2a.1 close** | 303 passed / 1 skipped (305 with Slab-1 substrate) | +17 generator + scaffold-reference | `tests/specialists/` directory opens |
| **2a.2 close** | ~361 passed / 5 skipped (real-key) | +28 Irene tests | First real-LLM specialist |
| **2a.3 close** | 380 passed / 7 skipped / 2 deselected | +20 Kira tests | First tool-dispatch specialist |
| **2a.4 close (this story)** | Migration-scoped regression on the cleanly runnable suite (specialists + scaffold + agents + Texas contracts + Kira cache harness): **169 passed / 2 skipped** | +33 Texas tests over Texas baseline (28 → 36 Texas-only after G6 patches; +12 broader pickup) | Pure-tool-dispatch + first real populated-and-locked sanctum |

**Caveat on the post-2a.4 number.** The local environment has collection errors on optional-dep tests in `tests/contracts/test_33_*` and several `tests/test_*` modules (missing `responses` module + Pydantic v2 schema mismatches in unrelated workflow-runner tests). Those errors PRE-EXIST Texas migration and are unrelated to the Slab 2a scaffold pilot — filed in deferred-work.md as a Slab-2-cross-cutting environment-hygiene follow-on. The cleanly scoped migration regression is still the authoritative number for Slab 2a closure.

**Texas-only T8 evidence at story close:** `pytest tests/specialists/texas tests/integration/scaffold_conformance/test_scaffold_texas.py -q` → 36 passed (8 net new tests over the Codex landing baseline of 28, all from G6 PATCH cycle). Ruff clean. lint-imports 3/3 KEPT.

---

## Anti-pattern catalog state

**A9 — Epic-doc structural-name drift from Slab-1-hardened reality** (retitled at 2a.4 from "Epic-doc node-name drift"). Four concrete instances harvested across Slab 2a:

1. Story 2a.1 — node names `reason/act/validate/emit/return` vs canonical `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`
2. Story 2a.2 — same node-name drift, second occurrence
3. Story 2a.3 — node name "reason node" + model-ID `gpt-4o` + tier "multimodal"
4. **Story 2a.4 — test path `tests/bmad-agent-texas/...` vs reality `tests/agents/bmad-agent-texas/`**

**Title-broadening disposition:** RATIFIED at 2a.4 G6 review. Original title was node-name-specific; four-instance harvest spans node names AND test paths AND model-ID drift. Title broadened to capture the full pattern. Future single-instance drifts can augment as bullet examples without further title surgery.

**A10 — Epic-doc-vs-registry model-ID drift** — second example added at 2a.3 (Kira `gpt-4o` → `gpt-5-haiku` per registry). 2a.4 added no new model-ID drift (Texas `gpt-5-haiku` matches registry; tier `fast` mapping consistent with 2a.3 pattern).

**A11 — Epic-doc-vs-BMB sanctum-path drift** — first example at 2a.2 (Irene `bmad-agent-irene` per epic vs `bmad-agent-content-creator` per BMB convention). 2a.4 added no new sanctum-path drift (Texas's `bmad-agent-texas` matches skill-dir name).

**A12 — Procedural-coupling: generator does not auto-emit `pyproject.toml` C3 ignore-imports row** — three independent manual-edit instances (Irene 2a.2 + Kira 2a.3 + Texas 2a.4). **Strongest evidence base; binding gate for Slab 2b.1 TEMPLATE.**

**Harvest-gate retrospective on the 4-test sample.** Standing protocol "epic text vs framework reality, framework wins" worked at every story T1. Each drift was logged in T1 Readiness §E + resolved per the framework + harvested into `specialist-anti-patterns.md`. No drift slipped past T1; no drift required mid-story rework. The protocol scales.

---

## Deferred-inventory follow-ons surfaced at Slab 2a close

Updated in [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md):

**Reactivation-ready (consult at Slab 2b kickoff):**

- **A12 generator auto-emit** — BLOCKING for 2b.1 TEMPLATE
- **AC-B-OP Texas live retrieval-provider dispatch** — gated on Slab-3 marcus.dispatch.contract forward-port; pre-authored helper at `scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py`
- **Cache-hit-rate Kira populated-sanctum exercise** — fires when operator runs first-breath ceremony for `_bmad/memory/bmad-agent-kling/`
- **Envelope-carrier-hack retirement** — replace `cache_state.cache_prefix` payload-carrier with first-class RunState envelope field (Slab-3 architectural)
- **Gate-decision conditional-edge fix** — uniform Slab-3 remedy for the "routes around" spec-vs-implementation drift across Irene/Kira/Texas
- **Cold-cache-nonce-variant** — operator-path enhancement for FR54 second-data-point fidelity
- **`--require-live-llm-flag-wiring`** — operator-path enhancement for live-LLM gate enforcement

**Newly filed at 2a.4:**

- **Dispatch-wrapper extraction candidate** — `kira/kling_dispatch.py` + `texas/retrieval_dispatch.py` are two independent occurrences of the same dispatch-wrapper shape (subprocess seam + fixture short-circuit + wrapper kwargs). If 2b.1 (Gary) or 2b.2 surfaces a third occurrence, extract to `_bmad/scaffolds/dispatch_wrapper_template.py` for reuse.
- **`§12 size review** when subsection count exceeds 12** — readability check on `langgraph-migration-guide.md §12`. Not load-bearing today (currently 10 subsections); flag for review at 2b mid-slab.
- **`implementation-artifacts/` directory index** — file a README at `_bmad-output/implementation-artifacts/` if directory clutter starts to hinder newcomer triage at Slab 2b kickoff.
- **`SanctumLockViolation` cross-specialist refactor** — 2a.4 introduced the named exception class for Texas; Irene/Kira can be retrofitted via a Slab-2-cross-cutting follow-on so all three specialists share the same lock-and-verify protocol.
- **Local environment optional-dep hygiene** — `tests/contracts/test_33_*.py` + several `tests/test_*.py` modules error at collection with `ModuleNotFoundError: responses` and pydantic-v2 schema validation errors. Pre-existing (Texas migration didn't introduce these). File at Slab 2b open as a one-shot env-restore PR.

---

## §12 reference completeness

`docs/dev-guide/langgraph-migration-guide.md §12` is now structurally complete:

- §12.1 Five-step spine
- §12.2 Invocation (uv vs venv-direct, both first-class per DR-1)
- §12.3 Expected generated tree
- §12.4 Manual post-edit checklist (frozen)
- **Section-level framing sentence (Paige P2 add 2a.4):** §12.5–§12.7 cover three specialist-shape categories proven across Slab 2a; if a fourth shape emerges, add §12.x rather than restructure
- §12.5 Irene worked before/after — narration category, post-2a.2 close
- §12.6 Kira worked before/after — LLM+tool-dispatch category, post-2a.3 close (with sub-section framing sentence above the divergences-from-Irene table per Paige P4)
- §12.7 Texas worked before/after — pure-tool-dispatch category, post-2a.4 close (matches the actual post-G6 code shape: fail-loud cache-state guards + bundle.parsed.* tag emission + exit-10 graceful degrade + exit-30 hard raise)
- §12.8 Verification commands (Irene + Kira + Texas, single-call form per Amelia A4)
- §12.9 Governance notes
- §12.10 Slab 2a retrospective summary (with Murat M4 latency substitute metric + retro pointer + Slab 2b kickoff gate language)

Three worked-example categories ready for Slab 2b inheritance. Future fourth specialist-shape category becomes a §12.x ADD with cascade renumber, not §12 restructuring.

---

## Slab 2b kickoff readiness checklist

Before opening Story 2b.1 (Gary TEMPLATE), confirm:

**Hard gates (must land before 2b.1 opens):**

- [ ] **A12 generator auto-emit follow-on landed.** This is THE Slab-2a→2b binding gate. Three manual C3 ignore-imports edits is the evidence base; do not pay this debt a fourth time.
- [ ] **`bmad-create-specialist` generator dry-run succeeds for Gary's input skill** (`skills/bmad-agent-gary/` exists + has SKILL.md + reference tree).
- [ ] **Slab-1 substrate intact:** lint-imports 3/3 KEPT; scaffold-conformance framework tests all pass; compile validator additive-only.

**Soft gates (recommended but not blocking):**

- [ ] Operator first-breath ceremony for any 2b specialists whose sanctum ships unpopulated (graceful-degrade is acceptable; populated-and-locked is preferred).
- [ ] Dispatch-wrapper extraction decision: if 2b.1 Gary's act-body needs a wrapper, decide at T1 whether to inline-author or extract from kira/texas precedent.
- [ ] Local environment optional-dep hygiene PR (file as 2b.0 chore if collection errors are still present).
- [ ] §12 size review check (currently 10 subsections; trigger threshold 12).

**Process improvements baked into the 2b TEMPLATE story:**

- T1 Readiness `epic-doc-vs-framework cross-check` is mandatory (it caught drifts at every Slab-2a story).
- Pre-coding party-mode round is high-leverage (4/4 GREEN at every Slab-2a story; riders integrated up-front beat post-G6 retrofit).
- Independent G6 layered review (`bmad-code-review` skill, three subagents) catches doc-deliverable misses that self-conducted review skipped at Codex landings (2a.3 missed §12.6 + anti-pattern harvest; 2a.4 missed §12 framing sentences + parse-branch coverage + slab-retrospective.md before independent G6 caught them).
- Aggressive single-gate close rubric per [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md) keeps K within Murat anti-padding band; DEFER+DISMISS aggressively on cosmetic NITs.

---

## Closing note

Slab 2a was the proof that the scaffold-conformance framework + generator + sanctum-reference conventions (the Slab-1 substrate) actually work for real specialists, not just for hypothetical ones. Three categories landed cleanly. The one structural debt that didn't get paid down — A12 generator auto-emit — is queued with the strongest possible evidence base; Slab 2b.1 is gated on it.

The pure-tool-dispatch category (Texas) was the surprise: it forced an honest accounting of which Slab-2 invariants actually generalize across categories (FR54 doesn't; the discriminator-check pattern does; the byte-stable digest pattern does). That clarity feeds Slab 2b's 14-specialist tranche directly.

Slab 2b opens once A12 lands.

**2026-04-25 update:** A12 generator auto-emit shipped at Story 2a.5 close. Slab 2b kickoff hard gate 1 satisfied. Slab 2b.1 (Gary TEMPLATE) is now open to author.

---

## Slab 2b kickoff handoff (T1 decisions)

**Authored 2026-04-25 at Story 2b.1 spec close + party-mode amendment (Paige rider P-R6).** This subsection is a forward-looking T1→T1 bridge artifact — past slabs' retrospectives become the natural home for "what did the next slab decide at open" so future readers (Slab 2c+) don't have to reverse-engineer Slab 2b's TEMPLATE-establishing decisions from the 2b.1 spec body.

**Five TEMPLATE-establishing decisions made at Slab 2b open (Story 2b.1 + party-mode green-light + amendment 2026-04-25):**

1. **TEMPLATE doc home:** [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v1 — seven rules R1–R7 codified there. Inheritor stories 2b.2–2b.14 cite the doc; they do NOT inline-restate the rules. Updates require party-mode consensus + version bump.
2. **Bounded-scope rule (R1):** per-specialist 2b.x migrations cover ONLY the headless dispatch path. LLM-mediated parameter recommendation (PR), quality assessment (QA), exemplar study (ES), or any other LLM-using SKILL.md capabilities are OUT OF SCOPE unless the specialist materially needs them at the runtime layer. Filed as separate per-specialist enhancement stories only when concrete need surfaces.
3. **§12 cascade rule (R3):** category-novel specialists add new §12.x worked example; pure inheritors get one row in §12.12 inheritor catalog matrix (NEW at 2b.1 close). Forward-pointers from each §12.x worked example point to §12.12. Only category-novel specialists (a fifth or further specialist-shape category beyond the four established) add new §12.x.
4. **Anti-pattern harvest continuity (R6):** at every 2b.x T1, run epic-doc-vs-framework cross-check. Drifts harvest as augmented bullets under existing A9/A10/A11/A12 (per Paige harvest-gate rule). T1 Readiness section MUST split framework drifts (sub-subsection (a) — harvest as anti-pattern bullets) vs TEMPLATE scope decisions (sub-subsection (b) — codify in `specialist-migration-template.md`). At 2b.1 open: A11 retitled to "sanctum/sidecar contract drift" (parallel to A9 retitle at 2a.4); A10 third example added (Gary `gpt-4.1-mini`).
5. **Auto-emit C3 verification (R5):** every 2b.x story includes a positive regression test asserting Story-2a.5 generator auto-emit fired (NO manual `pyproject.toml` edits anywhere). Test uses `tests/specialists/generator/conftest.py::temp_repo_root` synthetic fixture (NOT live `pyproject.toml`) for hermetic order-independence across all 13 inheritor stories.

**Trail-entry-resolution-at-`_plan` discipline (R7, Winston W-R1 amendment):** for any tool-dispatch category specialist, `_plan` MUST resolve and append the `ModelResolutionEntry` even when `_act` will not invoke the chat handle. Without this rule, an inheritor dev agent may shortcut and skip resolution at `_plan` ("why resolve a model I never call?"); that breaks cache-prefix attribution per NFR-I6 + FR16 trail-entry contract uniformity + Winston W2 discriminator-check + Slab-3 middleware that walks the trail.

**Tag-namespace artifact-noun convention (Murat M-R2 amendment):** specialist tag namespaces follow the artifact-noun convention — Texas `bundle.parsed.*` (artifact = bundle); Gary `receipt.parsed.*` (artifact = receipt); future categories use the artifact-noun under parsing, NOT verb+vendor like `gamma.dispatch.*`. This generalizes downstream span-aggregation across specialists.

**Dispatch-wrapper extraction threshold (R2):** subprocess (Kira/Texas → 2 instances) vs REST-API (Gary → 1 instance) vs MCP-tool (Slab-3 forward-looking) — wrapper-extraction threshold is "third occurrence of the SAME seam category." Loader sub-mechanism per-specialist (importlib OK for narrow-import targets; direct package import required for heavy-side-effect targets like Gary's `gamma_operations`). Sanctum cross-cutting refactor (e.g., `SanctumLockViolation` extraction) follows the same third-occurrence rule.

**State-shape extension pattern (R4):** each per-specialist `XxxReturn` adds AT MOST ONE new field, loose-typed (`list[dict[str, Any]] | None` or similar). Strict-typing is owed at Story 2b.15 dispatch-contract-hardening, NOT in per-specialist migration stories. **Risk:** if 2b.15 slips, the loose-typing accumulates; 2b.15 must be named in deferred-inventory with hard reactivation gating ("opens immediately on 2b.14 close") to convert soft-defer into hard sequencing constraint.

A future Slab-2c reader hitting this section knows what 2b chose at open without having to read 2b.1's spec body. A 2b.7 dev agent at T1 reads `specialist-migration-template.md` (linked from §11 of the standing pre-flight items list) and applies R1–R7 to their story authoring.
