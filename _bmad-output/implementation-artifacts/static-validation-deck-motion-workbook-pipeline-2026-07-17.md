# Static validation — deck + motion + workbook production pipeline

**Date:** 2026-07-17  
**Scope:** Composed workflow `narrated-deck-with-workbook` = **deck + motion + workbook**  
**Method:** Read-only code/manifest/registry inspection + hermetic `compose_manifest` prune check. **No production code edited.**  
**Branch context:** `dev/workbook-wave-3940-2026-07-15` (live trial paused for G0-directive HIL remediation).  
**Authority files:** `state/config/pipeline-manifest.yaml`, `app/marcus/lesson_plan/composition.py`, `bundle_catalog.py`, `collateral_selection.py`, `app/marcus/cli/trial.py`, `app/marcus/orchestrator/workbook_wiring.py`, `state/config/dispatch-registry.yaml`.

---

## 0. Executive verdict

| Area | Verdict |
|---|---|
| Composition model (deck / motion / workbook fragments) | **OK** — typed DAG; full selection is byte-identical no-op on 52-node manifest |
| Specialist graphs + dispatch-registry for paid band | **OK** — all named specialists present and registered |
| Workbook band seams (`07W.1`–`07W.4`) | **PARTIAL by design** — orchestrator factories in `workbook_wiring.py`, not dispatch-registry specialists |
| Bundle honesty catalog vs live evidence | **STALE** — workbook still `mechanism_only_never_produced` / bundle readiness `not_yet` despite live workbook trials |
| Operator HIL at G0 directive confirm | **FAIL (known)** — raw `directive.yaml` dump; 42-1 projector not wired (remediation story in flight) |
| Unchained orchestration nodes | **PARTIAL** — present in node list; real work often on start-time / wake-gated side paths |
| End-to-end live claim for this composition | **Not asserted here** — static only |

**Bottom line:** The graph composition and specialist wiring for deck+motion+workbook are structurally coherent. The honesty/front-door catalog understates workbook readiness. The first operator review surface on `trial start` (G0 directive) remains a known display defect and will gate any steered paid walk until remediated.

---

## 1. What “deck + motion + workbook” means in code

### 1.1 Selection record

`ComponentSelection` (`app/models/state/component_selection.py`):

| Flag | Full workbook bundle | Production default |
|---|---|---|
| `deck` | True | True |
| `motion` | True | True |
| `workbook` | True | **False** |

`production_default()` is **deck+motion only**. The full triple is catalog id `narrated-deck-with-workbook`.

### 1.2 Bundle catalog

| Bundle id | Selection | `bundle_readiness()` (computed 2026-07-17) |
|---|---|---|
| `narrated-deck` | deck | `fully_proven` |
| `narrated-deck-with-motion` | deck+motion | `partial` |
| `narrated-deck-with-workbook` | **deck+motion+workbook** | **`not_yet`** |

Per-component tiers (`CAPABILITY_TIERS`):

| Component | Tier (catalog text) |
|---|---|
| deck | `proven_wired` |
| motion | `proven_regressed_repairable` |
| workbook | **`mechanism_only_never_produced`** — note still claims “no real producer has emitted a workbook artifact yet” |

**Finding S-1 (STALE honesty):** Catalog workbook tier / bundle readiness disagree with post–Epic 36–40 live evidence (governed workbook trials completed). Front door greys the workbook bundle unless `--allow-unproven-bundle` (or selection arrives via ratified collateral, which bypasses the grey-out path depending on start resolution). This is an honesty/ops hazard, not a missing graph node.

### 1.3 How selection reaches the runner

Precedence in `trial.py` `_resolve_start_component_selection` (summarized):

1. `--lesson-plan-collateral-intent` when `source=ratified` → closed catalog selection  
2. `--lesson-plan-json` auto-derive (`collateral.declaration == present` ⇒ workbook bundle)  
3. `--bundle` / front door / defaults  

Plan-dialogue writes `ratified-collateral-intent.yaml` with workflow ∈  
`{narrated-deck, narrated-deck-with-motion, narrated-deck-with-workbook}`.  
Workbook workflow requires collateral declaration present.

**There is no catalog entry for deck+workbook without motion.** Full workbook bundle always includes motion nodes.

### 1.4 Composer fragments (runtime prune units)

Do **not** confuse with `COMPONENT_TYPE_REGISTRY` (Lesson-Planner modality composites). Runtime prune uses `COMPONENT_FRAGMENTS`:

| Fragment | Owned node IDs | Depends on |
|---|---|---|
| `deck` | base remainder (everything not owned by motion/workbook) | — |
| `motion` | `{07D, 07D.5, 07E, 07F}` | deck |
| `workbook` | `{07W.1, 07W.2, 07W.3, 07W.4, 07W}` | deck |

Optional cross-component input: `motion_receipts` on compositor (`OPTIONAL_PROJECTION_KEYS`) — pruned when motion deselected.

---

## 2. Verified prune matrix (hermetic compose)

Executed 2026-07-17 against live `pipeline-manifest.yaml` via `compose_manifest`:

| Selection | Node count | Pruned IDs | Edge bridges observed |
|---|---:|---|---|
| deck+motion+workbook | **52** | *(none)* | `15 → 07W.1`, `07C → 07D` |
| deck+motion | **47** | `07W.1`–`07W.4`, `07W` | `15 → __end__` |
| deck-only | **43** | motion set + workbook set | `07C → 07G`, `15 → __end__` |

---

## 3. Ordered walk — full composition (52 nodes)

Edge spine (compiled):  
`__start__ → pre-walk-settings-gate → g0-enrichment-gate → g0-ratify-gate → 01 → … → 07C → 07D → 07D.5 → 07E → 07F → 07G → 08 → … → 15 → 07W.1 → 07W.2 → 07W.3 → 07W.4 → 07W → __end__`

**Legend:** `M` = motion fragment · `W` = workbook fragment · Gate codes as declared in manifest.

| # | id | Band | specialist_id | Gate | Notes |
|---|---|---|---|---|---|
| 1 | `pre-walk-settings-gate` | Kickoff | null | **G0S** | Pause only when woken (default-ON wake sentinel / env) |
| 2 | `directive-composer` | Kickoff | null | — | **Unchained**; real compose at `trial start` |
| 3 | `pre-gate-marcus` | Kickoff | null | — | Unchained |
| 4 | `per-slide-subgraph` | Deck support | null | — | Unchained |
| 5 | `html-review-pack-emitter` | Deck support | null | — | Unchained |
| 6 | `g0-enrichment` | G0 enrich | null | — | Unchained; woken w/ G0E |
| 7 | `g0-enrichment-gate` | G0 enrich | null | **G0E** | Wake-gated |
| 8 | `irene-refinement` | G0 enrich | null | — | Unchained |
| 9 | `g0-ratify-gate` | G0 enrich | null | **G0R** | Wake-gated |
| 10 | `01` | Kickoff | marcus | **G0** | Activation |
| 11 | `02` | Texas | texas | **G0A** | Source authority |
| 12 | `02A` | Kickoff | marcus | **G0B** | Operator directives |
| 13 | `03` | Texas | texas | — | Ingestion |
| 14 | `04` | Fidelity | vera | **G1** | Packet gate |
| 15 | `04A` | Irene P1 | irene-pass1 | **G1A** | Plan coauthor |
| 16 | `04.5` | Plan | marcus | — | Parent slide count |
| 17 | `04.55` | Research / constants | marcus | — | Estimator + research dispatch |
| 18 | `4.75` | CD | cd | — | Creative directive |
| 19 | `05` | Irene P1 | irene-pass1 | **G2** | Pass-1 + fidelity |
| 20 | `05B` | Irene P1 | irene-pass1 | **G1.5** | Cluster plan |
| 21 | `06` | Package | marcus | — | Pre-dispatch package |
| 22 | `6.2` | Cluster | marcus | — | Label “Conditional” |
| 23 | `6.3` | Cluster | marcus | — | Label “Conditional” |
| 24 | `06B` | Package | marcus | — | Literal-visual |
| 25 | `07` | Gary / deck | gary | — | Dispatch + export |
| 26 | `7.5` | Fidelity | vera | **G2.5** | Cluster coherence |
| 27 | `07B` | Variant | quinn-r | — | Variant selection |
| 28 | `07B-gate` | Variant | null | **G2B** | HIL |
| 29 | `07C` | Storyboard A | quinn-r | **G2C** | Winner auth |
| 30 | `07D` **M** | Motion | marcus | **G2M** | Motion designation |
| 31 | `07D.5` **M** | Motion | motion_planner | — | Motion plan |
| 32 | `07E` **M** | Motion | kira | — | Kling / import |
| 33 | `07F` **M** | Motion | quinn-r | **G2F** | Motion gate |
| 34 | `07G` | Perception | vision | — | PNG-grounded; may batch-pause |
| 35 | `08` | Pass-2 | irene | — | Detective gate if flag ON |
| 36 | `08B` | Storyboard B | quinn-r | **G3B** | HIL |
| 37 | `09` | Lock | marcus | **G3** | Four-artifact lock |
| 38 | `10` | Fidelity | vera | **G4** | Pre-spend |
| 39 | `11` | Audio | elevenlabs→enrique | — | Alias in compiler |
| 40 | `11-gate` | Audio | null | **G4A** | Voice HIL |
| 41 | `11B` | Audio | elevenlabs→enrique | — | Input package |
| 42 | `11B-gate` | Audio | null | **G4B** | HIL |
| 43 | `12` | Audio | elevenlabs→enrique | — | Generation |
| 44 | `13` | QA | quinn-r | **G5** | Pre-composition |
| 45 | `14` | Compositor | compositor | — | Optional `motion_receipts` |
| 46 | `14.5` | Desmond | desmond | — | Operator brief |
| 47 | `15` | Handoff | marcus | — | Descript-ready |
| 48 | `07W.1` **W** | Workbook | null (wiring) | — | Brief seam |
| 49 | `07W.2` **W** | Workbook | null (wiring) | — | Ask-A seam |
| 50 | `07W.3` **W** | Workbook | null (wiring) | — | Review seam |
| 51 | `07W.4` **W** | Workbook | null (wiring) | — | Ask-B seam |
| 52 | `07W` **W** | Workbook | workbook_producer | — | MD+DOCX producer |

---

## 4. Static validation by band

| Band | On-disk module(s) | Dispatch-registry | Runner / wiring | Verdict |
|---|---|---|---|---|
| Manifest + compose | `pipeline-manifest.yaml`, `composition.py` | n/a | `production_runner` compose-before-freeze | **OK** |
| Selection edge | `bundle_catalog.py`, `collateral_selection.py`, `front_door.py`, `trial.py` | n/a | start_trial threads selection; resume rehydrates | **OK** |
| Texas | `app/specialists/texas/graph.py` | `texas` | directive / corpus | **OK** |
| Vera | `app/specialists/vera/graph.py` | `vera` | G1 / G2.5 / G4 | **OK** |
| Irene Pass-1 | `app/specialists/irene_pass1/graph.py` | `irene_pass1` | `04A` / `05` / `05B` | **OK** |
| CD | `app/specialists/cd/graph.py` | `cd` | node `4.75` | **OK** |
| Gary | `app/specialists/gary/graph.py` | `gary` | node `07` | **OK** |
| Quinn-R | `app/specialists/quinn_r/graph.py` | `quinn_r` | multi-gate | **OK** |
| Motion planner | `app/specialists/motion_planner/graph.py` | `motion_planner` | `07D.5` | **OK** |
| Kira | `app/specialists/kira/graph.py` | `kira` | `07E` → `motion_receipts` | **OK** |
| Vision | `app/specialists/vision/graph.py` | `vision` | `07G` (+ batch pause) | **OK** |
| Irene Pass-2 | `app/specialists/irene/graph.py` | `irene` | `08` + detective hook | **OK** |
| Enrique / audio | `app/specialists/enrique/graph.py` | `enrique` only | manifest id `elevenlabs` aliased | **OK** (alias) |
| Compositor | `app/specialists/compositor/graph.py` | `compositor` | `14` | **OK** |
| Desmond | `app/specialists/desmond/graph.py` | `desmond` | `14.5` | **OK** |
| Workbook producer | `app/specialists/workbook_producer/graph.py` | `workbook_producer` | `07W` | **OK** |
| Workbook seams | **no** `app/specialists/workbook_*` packages for 07W.1–4 | **absent** (intentional) | `workbook_wiring.py` factories | **PARTIAL** |
| G0 directive confirm UI | `trial.py::_confirm_or_edit_directive` | n/a | dumps `directive_path.read_text()` | **FAIL** |
| Tabular HIL (42-1) | `hil_tabular_projector.py` | n/a | only `_emit_gate_surface_if_paused` (`paused-at-gate`) | **PARTIAL** — wrong seam for G0 directive |
| `COMPONENT_TYPE_REGISTRY` | modality composites | n/a | not used for prune | **STALE naming overlap** only |

Dispatch registry `_status: production`. Alias map: `app/manifest/compiler.py` `SPECIALIST_ALIASES` (`elevenlabs`→`enrique`, `irene-pass1`→`irene_pass1`, `quinn-r`→`quinn_r`).

---

## 5. Step-by-step routine notes (static)

### Phase A — Start / kickoff (before frozen walk spends)

1. **Env + CLI** — `trial start` with corpus dir, optional collateral intent, `--hud on`, quality/execution flags.  
2. **Compose directive** — `compose_and_write` → `runs/<id>/directive.yaml`.  
3. **Styleguide picker** — interactive confirm (worked in trial `5169a872`).  
4. **G0 directive confirm** — `_confirm_or_edit_directive`: **raw YAML dump** + `[c/e/s/x]`.  
   - **S-2 FAIL:** Evidence requirement lists this printout; Story 42-1 closed inventory without migrating this path.  
5. **G0S** — pre-walk settings confirm (default-ON wake). Tabular/settings readout is Epic 42 substrate; distinct from directive dump.  
6. **Selection freeze** — composed manifest for `deck+motion+workbook` keeps all 52 nodes.

### Phase B — Ingest + enrichment + plan

7. Texas `02`/`03` + Vera `04` + Irene Pass-1 plan gates (`04A`/`05`/`05B`).  
8. G0E / G0R wake-gated enrichment + LO ratify (`MARCUS_G0_DISPATCH_LIVE` / enrichment flags).  
9. Research at `04.55` — dispatch default ON; detective default **OFF**.  
10. CD at `4.75` — required upstream for §06 package builder (Epic 41 fixed silent-skip starvation).

### Phase C — Deck + motion + perception

11. Gary `07` → variant/storyboard gates → **motion band** `07D`–`07F` → vision `07G` (batch pause possible).  
12. Optional `motion_receipts` into compositor only if motion ran.

### Phase D — Pass-2 + audio + assembly

13. Irene `08` (+ detective hard-pause if ON) → Storyboard B / G3 lock → Vera G4 → Enrique voice/audio → Quinn-R G5 → compositor `14` → Desmond `14.5` → handoff `15`.

### Phase E — Workbook band (full composition only)

14. `07W.1` brief → `07W.2` Ask-A → `07W.3` review → `07W.4` Ask-B → `07W` producer.  
15. Seams short-circuit via `workbook_wiring.run_workbook_band_node`; producer uses normal specialist dispatch.  
16. Resume-skip trap historically documented; reconcile-not-skip set covers `07W.2`–`07W.4`.

---

## 6. Findings register (static)

| ID | Severity | Finding |
|---|---|---|
| **S-1** | HIGH (honesty) | Workbook capability tier + `narrated-deck-with-workbook` readiness still `mechanism_only_never_produced` / `not_yet` while live workbook pipeline has produced real MD+DOCX. Catalog note is outdated. |
| **S-2** | HIGH (operator surface) | G0 directive confirm dumps entire `directive.yaml` (`trial.py` L364). 42-1 projector never called; no directive table renderer exists. Remediation story in flight (2026-07-17). |
| **S-3** | MEDIUM | Unchained orchestration nodes (`directive-composer`, `g0-enrichment`, `irene-refinement`, …) live in the 52-node list but real behavior is start-time / wake-gated — easy to misread as “walk visits composer.” |
| **S-4** | MEDIUM | No deck+workbook-without-motion catalog path; product forces motion nodes whenever workbook is selected. |
| **S-5** | LOW (by design) | `07W.1`–`07W.4` absent from dispatch-registry; wiring module is the authority. |
| **S-6** | LOW | Motion modality still a composer `_STUB_MODALITIES` binding (not in `MODALITY_REGISTRY`) — prune works; registry hygiene incomplete. |
| **S-7** | INFO | Production default selection omits workbook — operators must pass ratified collateral / bundle / plan-json to get the full triple. |
| **S-8** | INFO | Feature-flag asymmetry: research dispatch default ON; detective default OFF; G0 enrichment / G0S wake-gated. |

---

## 7. What this validation does **not** claim

- Live dollar spend, gate timings, or quality of Tejal C1M1-P1 artifacts  
- That recovering cancelled trial `5169a872` is safe  
- That HUD / public tunnel / G0S were witnessed on the aborted start  
- That LO-overlay or workbook cover-art debts are closed  

---

## 8. Recommended follow-ons (governance only — not implemented here)

1. Land the G0-directive tabular remediation story (closes S-2).  
2. Party-ratify a catalog honesty bump for workbook tier / `narrated-deck-with-workbook` readiness (closes S-1) — do not silently edit tiers without party.  
3. Optionally document unchained-node semantics in operator swimlane (S-3).  
4. Re-run this static check after remediation; then a steered live proof of the full triple.

---

## 9. Reproduction commands (read-only)

```powershell
# Specialist / wiring presence
Test-Path app\specialists\{texas,vera,irene_pass1,cd,gary,quinn_r,motion_planner,kira,vision,irene,enrique,compositor,desmond,workbook_producer}\graph.py
Test-Path app\marcus\orchestrator\workbook_wiring.py

# Compose prune matrix
.venv\Scripts\python.exe -c "from pathlib import Path; from app.manifest import load; from app.marcus.lesson_plan.composition import compose_manifest; from app.models.state.component_selection import ComponentSelection; m=load(Path('state/config/pipeline-manifest.yaml')); print(len(compose_manifest(m, ComponentSelection(deck=True,motion=True,workbook=True)).nodes))"
```

---

*End of static validation report.*
