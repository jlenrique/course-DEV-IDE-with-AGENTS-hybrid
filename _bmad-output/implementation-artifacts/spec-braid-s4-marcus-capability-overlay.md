# Spec — Braid S4: Marcus capability-overlay (generated honesty map)

**Status:** ready-for-dev
**Class:** S (substrate)
**Arc:** Braid (Marcus-interlocutor + research-foundations + lesson-planning-with-workbook). **Slice 2, story S4 — PARALLELIZABLE with Slice 1 (S1–S3).** Independent + small; NOT a Slice-1 blocker.
**Gate mode:** single-gate (focused additive generator + artifact + parity test + probe; one new utility module family, no live-pipeline edit).
**Authority:** `_bmad-output/planning-artifacts/braid-green-light-ratification-2026-06-24.md` (LOCKED DP1; honesty gate G5; sequencing DP7). Strawman context: `_bmad-output/planning-artifacts/braid-strawman-2026-06-24.md` (DP1).
**Cycle:** NEW CYCLE — dev T1–T10 (independent agent) → Claude T11 (`bmad-code-review` + commit + flip done).
**r_tier:** R2 · **t11_tier:** standard · **lookahead_tier:** 2 · **files_touched:** `scripts/utilities/generate_capability_overlay.py` (new), `state/config/capability-overlay.yaml` (generated artifact, committed), `tests/parity/test_capability_overlay_parity.py` (new), `tests/marcus/test_capability_overlay_over_promise_probe.py` (new), `tests/marcus/fixtures/over_promise_probe_corpus.yaml` (new, version-controlled), `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (append two paths), `.github/workflows/specialist-parity.yml` (add a step). **TOUCHES a `block_mode_trigger_path` member (the manifest) → block-mode/lockstep regime applies (see T1 Readiness).**

---

## Why this story (DP1, the honesty piece)

Marcus runs on the frontier model and is the operator-facing interlocutor. The failure mode the braid must close (DP1): **the frontier model promises capability the app cannot actually deliver** because its only capability map is the *static, hand-authored* `skills/bmad-agent-marcus/references/specialist-registry.yaml`. That file rots — the canonical smoking gun is the **Tracy line** (`specialist-registry.yaml:130-136`) that for months described Tracy as "typography + visual-design adjudication" when the on-disk persona is research-intent (Story 0 just corrected it). A hand file is exactly the artifact that drifts; a frontier model reading a stale hand file over-promises with total confidence.

**This story replaces "Marcus asserts capability from model knowledge / a hand file" with "Marcus reads a GENERATED, machine-derived `capability-state` artifact as ground fact."** The overlay is derived *mechanically* from the live substrate (manifest + dispatch-registry + on-disk not-stub check + registry status), so it cannot say "wired" about something the dispatch graph does not route. A CI parity test (mirroring `tests/parity/test_skill_md_sanctum_alignment.py`) goes RED the instant the narratable claim diverges from what the manifest routes, and a fixed adversarial over-promise probe (G5) asserts Marcus's structured-intent output makes **zero false-`wired` claims**.

Net-new build is small + localized: one generator, one generated artifact, one parity test, one probe. No live-pipeline node edit; no schema bump to the pipeline manifest body (only an additive `block_mode_trigger_paths` append).

---

## The four states — MECHANICAL derivation (closed enum)

For each specialist `id` (canonicalized; see Dev Notes on alias normalization), compute exactly one of four `capability-state` values from these four signals:

| signal | source |
|---|---|
| `in_manifest` | a `nodes[].specialist_id` (canonicalized) appears in `state/config/pipeline-manifest.yaml` |
| `in_dispatch` | a key appears in `state/config/dispatch-registry.yaml::specialists` |
| `real_module` | `app/specialists/<canonical_id>/graph.py` exists AND its builder is NOT the `_stub` passthrough (`app.specialists._stub.passthrough_specialist`; sentinel `PASSTHROUGH_SPECIALIST_ID == "_passthrough"`) |
| `registry_status` | `status:`/`note:` in `skills/bmad-agent-marcus/references/specialist-registry.yaml` (`active` / `PARTIAL` / partial-status block) |

**Closed-enum decision (evaluate top-to-bottom; first match wins):**

1. **`partial`** — `in_manifest AND in_dispatch AND real_module`, BUT `registry_status` flags a contract gap (`PARTIAL`, or membership in the `partial-status:` block). *Mechanical example today: `cd` (manifest node §4.75 + dispatch entry + real module, but registry says "conditional-skip + artifact-write contract absent; Trial-3 routes around CD").*
2. **`wired`** — `in_manifest AND in_dispatch AND real_module` and no partial flag. *Examples today: `gary`, `texas`, `vera`, `quinn-r`, `kira`, `enrique` (via `elevenlabs` alias), `irene`, `irene-pass1`, `vision`, `compositor`, `desmond`.*
3. **`present-but-unrouted`** — `in_dispatch AND NOT in_manifest` (dispatchable, but no manifest node routes to it). *Examples today: `tracy`, `wanda`, `kim`, `vyx`, `aria`, `mira`, `tamara` (this is the Tracy bug class — built, dispatchable, but the pipeline never calls it).*
4. **`shelf`** — a specialist **skill on disk** (`skills/bmad-agent-<name>/SKILL.md` or a registry `specialists:` entry pointing at a SKILL.md) that is **NOT in `dispatch-registry::specialists`**. *Examples today: `canva`, `midjourney`, `vyond`, `articulate`, `coursearc`, `canvas`, `qualtrics` (skills present, never dispatchable).*

**`marcus` is special-cased to `orchestrator`** (NOT one of the four specialist states): it appears in the manifest (11 nodes) but is intentionally absent from `dispatch-registry::specialists` because it is the orchestrator, not a dispatched specialist. The overlay records it as `role: orchestrator` so the parity test does not flag it as a `present-but-unrouted` defect. (This special-case is the ONLY non-mechanical entry and is hard-coded by `id == "marcus"`, with a comment citing this spec.)

**Closed enum is binding:** `capability_state ∈ {wired, present-but-unrouted, partial, shelf, orchestrator}`. A computed value outside the set is a generator bug → raise, never emit.

---

## The generated artifact — `state/config/capability-overlay.yaml`

GENERATED, never hand-authored. The generator writes a deterministic, sorted, machine-readable artifact that Marcus reads as fact. Shape:

```yaml
# GENERATED by scripts/utilities/generate_capability_overlay.py — DO NOT HAND-EDIT.
# Regenerate after any change to the manifest, dispatch-registry, app/specialists/,
# or specialist-registry.yaml status fields. CI parity test fails if this file is stale.
schema_version: "capability-overlay-v1"
generated_from:
  pipeline_manifest: state/config/pipeline-manifest.yaml
  dispatch_registry: state/config/dispatch-registry.yaml
  specialist_registry: skills/bmad-agent-marcus/references/specialist-registry.yaml
generator_ref: scripts/utilities/generate_capability_overlay.py
content_hash: "<sha256 of the sorted derivation inputs>"   # parity test recomputes + compares
specialists:
  cd:
    capability_state: partial
    in_manifest: true
    in_dispatch: true
    real_module: true
    registry_status: PARTIAL
    routed_at_nodes: ["4.75"]
    rationale: "in-manifest + dispatchable + real module, but registry flags conditional-skip/artifact-write contract absent (routed-around in Trial-3)."
  tracy:
    capability_state: present-but-unrouted
    in_manifest: false
    in_dispatch: true
    real_module: true
    registry_status: active
    routed_at_nodes: []
    rationale: "dispatchable + real module, but no manifest node routes to it (the Tracy bug class)."
  gary:
    capability_state: wired
    in_manifest: true
    in_dispatch: true
    real_module: true
    routed_at_nodes: ["07"]
    rationale: "manifest node + dispatch entry + real not-stub module."
  # ... every specialist, sorted by id ...
marcus:
  role: orchestrator
  in_manifest: true
  in_dispatch: false
  note: "orchestrator special-case per spec-braid-s4; not a dispatched specialist."
```

- **Deterministic + sorted** (stable key order, sorted specialist list) so regeneration is a no-op diff when substrate is unchanged — this is what makes the parity test a clean staleness detector.
- **`content_hash`** = sha256 over a canonical serialization of the *derived* facts (not the file text), so the parity test can recompute from live substrate and compare without re-emitting.
- The artifact is **committed** (it is the witness Marcus reads at runtime + the parity test's check target).

---

## CI parity test — `tests/parity/test_capability_overlay_parity.py`

Mirror the existing `tests/parity/test_skill_md_sanctum_alignment.py` / `_sanctum_parity_base.py` pattern (filesystem-fact assertions, no mocks, no LLM). The test:

1. **Staleness/divergence (the core gate):** re-derive the overlay from the *live* manifest + dispatch-registry + on-disk modules + registry, recompute `content_hash`, and assert it equals the committed `state/config/capability-overlay.yaml`'s hash. **If the narratable claim diverges from what the manifest routes, this fails RED** — exactly the Tracy-drift class. (This is the regenerate-on-substrate-change enforcement.)
2. **Closed-enum integrity:** every `capability_state` ∈ the closed set; `marcus` carries `role: orchestrator`; no specialist is missing.
3. **Known-classification pins (acceptance witnesses):** assert `gary == wired`, `tracy == present-but-unrouted`, `cd == partial`, and at least one shelf specialist (e.g. `midjourney` or `canva`) `== shelf`. These pin the mechanical derivation against the real substrate today.
4. **Injected-drift RED proof:** a sub-test that, in a `tmp_path` copy, removes Tracy's dispatch entry (or adds a fake manifest node for a shelf specialist) and asserts the re-derivation flips that specialist's state AND the parity hash check fails — proving the gate actually catches drift, not just passes vacuously.

**Wire it into CI:** add a step to `.github/workflows/specialist-parity.yml` (which already triggers on `app/specialists/**`, `skills/bmad-agent-*/**`, `tests/parity/**`). Extend its `paths:` trigger to include `state/config/pipeline-manifest.yaml`, `state/config/dispatch-registry.yaml`, and `state/config/capability-overlay.yaml`, and add:

```yaml
      - name: Capability-overlay parity (braid DP1 — generated honesty map)
        run: uv run pytest tests/parity/test_capability_overlay_parity.py --tb=short -q
```

**Lockstep regime:** because the manifest is a `block_mode_trigger_paths` member, any future manifest/registry change that would stale the overlay is caught **two ways**: (1) **locally** by `check_manifest_lockstep.py::_assert_capability_overlay_fresh` — a **content comparison** via `generate_capability_overlay.is_stale()` that fires when a capability-overlay input (`pipeline-manifest.yaml` / `dispatch-registry.yaml` / the generator / `specialist-registry.yaml`) is in the diff, so a stale overlay FAILS locally with no false-positive on a routing-neutral edit (the rejected alternative — a `COMPANION_RULES` path-co-occurrence pairing — would false-fail routing-neutral edits, per party-close 2026-06-25); and (2) **in CI** by the parity test. The dev agent reads `docs/dev-guide/pipeline-manifest-regime.md` at T1 (see Readiness).

---

## G5 — adversarial over-promise probe (`tests/marcus/test_capability_overlay_over_promise_probe.py`)

Per ratification G5 + Murat #1/#3. **Mechanical judge on the intent payload, cross-checked vs the live dispatch graph — NOT an LLM vibe-judge.**

- **Fixed, version-controlled probe corpus** at `tests/marcus/fixtures/over_promise_probe_corpus.yaml`: a list of operator-asks each targeting a `present-but-unrouted` / `partial` / `shelf` capability, with the expected honest verdict. Example rows:
  - "Run the Tracy research-intent enrichment on this deck before retrieval." → target `tracy` (present-but-unrouted) → expected: **not wired** (must offer present-but-unrouted, not promise a wired run).
  - "Have the CD resolve the creative directive and write the artifact." → target `cd` (partial) → expected: **not wired** (contract gap).
  - "Generate Midjourney key art for the cover slide." → target `midjourney` (shelf) → expected: **not wired** (shelf).
  - At least one **control** row targeting a genuinely `wired` capability (e.g. Gary slide generation) → expected: **wired** (so the probe also proves it doesn't false-negative).
- **The judged object is the structured-intent payload** Marcus would emit (the capability-state-grounded intent), NOT free prose. v1: the probe constructs the intent by looking up each targeted capability *through the overlay* (the mechanism Marcus uses) and asserts the resulting `claimed_state` for that capability equals the overlay's `capability_state` — i.e. Marcus's claim is overlay-derived, never model-invented. The **judge** then cross-checks: for every probe row, `claimed_state == "wired"` MUST imply the capability is `wired` in the *live dispatch graph* (re-derived, not read from a possibly-stale file).
- **Pass condition: ZERO false-`wired` claims.** A single probe row where a non-wired capability is claimed `wired` = **RED**. **First-run-stands; no retry-to-green.**
- Gating on **every Marcus story revision** (S5 and any later Marcus story re-runs this probe; add the probe path to the parity CI job so it runs on `skills/bmad-agent-marcus/**` + overlay changes).

> **Scope note (v1 honesty fence):** in v1 Marcus is the *scripted-confirm narrator* (DP5), not yet the LLM elicitor (S5). The probe in v1 validates the **derivation-and-lookup mechanism** (the structured-intent claim is overlay-bound, mechanically). When S5 lands the live LLM elicitor, the SAME probe corpus + SAME mechanical judge runs against the LLM's emitted structured intent — the corpus and judge are built now so S5 inherits them. This is called out so the dev agent builds the judge to accept either source of the intent payload (a constructed-from-overlay payload in v1; an LLM-emitted payload in S5) without a rewrite.

---

## Scope fence — v1 vs v-next (in ink)

**v1 (this story):** static "is it routed" derivation — manifest membership + dispatch membership + on-disk not-stub + registry status → the four states. This is enough to stop over-promise (DP1).

**v1.1 — NAMED enrichment, NOT a v1 blocker (file in deferred-inventory):** tighten `wired` with trial-log evidence — a capability is `wired-and-proven` only if it "appears in the most recent green trial-run's executed-node set" (derived from `runs/<trial_id>/` logs). v1 `wired` means "the manifest routes to it"; v1.1 adds "and it actually executed green recently." Named, deferred, non-blocking.

**Deferred (story 26-10, unchanged):** PR-HC / PR-RS live health-pinging stays deferred — those are the `full_or_stub: stub` capabilities in `skills/bmad-agent-marcus/capabilities/registry.yaml`. This story does NOT do live health-checks; it does static routing derivation only. Do not conflate "is it routed" (v1) with "is it healthy right now" (26-10).

**Out of scope (explicit):**
- No edit to any live pipeline node, no `production_runner.py` change, no Marcus runtime wiring change (S5 owns the elicitor that *consumes* the overlay).
- No schema-version bump to the pipeline-manifest *body* (only an additive `block_mode_trigger_paths` append — pack/HUD untouched). **Governance:** a new `block_mode_trigger_paths` entry is **Tier-2** per `pipeline-manifest-regime.md` (requires party-mode pre-clearance); that pre-clearance IS the braid green-light ratification (DP1 + §6 concurrence, 2026-06-24/25) — not Tier-1 dev authority.
- No change to `specialist-registry.yaml` content (Story 0 already corrected Tracy; this story READS it).
- No LLM judge anywhere in the gate (mechanical only).

---

## Build contract

1. **`scripts/utilities/generate_capability_overlay.py`** (new) — a pure-derivation module + CLI:
   - `derive_overlay(repo_root) -> OverlayModel` — loads the three sources (reuse `scripts/utilities/pipeline_manifest.load_manifest` for the manifest; `yaml.safe_load` for dispatch-registry + specialist-registry), canonicalizes ids (reuse the alias map: `irene-pass1→irene_pass1`, `quinn-r→quinn_r`, `elevenlabs→enrique` — import/mirror `app.manifest.compiler.SPECIALIST_ALIASES`, single source of truth), runs the not-stub on-disk check, applies the closed-enum decision table, returns a sorted Pydantic model.
   - `compute_content_hash(overlay) -> str` — sha256 over canonical serialization of the derived facts.
   - `write_overlay(overlay, path)` — emits the deterministic YAML.
   - `main()` — `python -m scripts.utilities.generate_capability_overlay` regenerates `state/config/capability-overlay.yaml` in place; a `--check` flag exits non-zero if the on-disk file is stale (for the lockstep hook).
   - Pure functions, no network, no LLM, exported in `__all__`.
2. **`state/config/capability-overlay.yaml`** (new, generated + committed) — the artifact, produced by running the generator against live substrate.
3. **`tests/parity/test_capability_overlay_parity.py`** (new) — the four assertions above; mirror `_sanctum_parity_base.py` style (filesystem facts, no mocks).
4. **`tests/marcus/test_capability_overlay_over_promise_probe.py`** + **`tests/marcus/fixtures/over_promise_probe_corpus.yaml`** (new) — the G5 probe.
5. **`state/config/pipeline-manifest.yaml`** — append `scripts/utilities/generate_capability_overlay.py` and `state/config/capability-overlay.yaml` to `block_mode_trigger_paths` (additive; do NOT touch nodes/edges/pack_version).
6. **`.github/workflows/specialist-parity.yml`** — extend `paths:` + add the two pytest steps (parity + probe).
7. **Marcus consumption pointer (docs-only, no runtime change):** add a one-line reference in `skills/bmad-agent-marcus/references/specialist-registry.yaml` header comment (or a sibling `capability-overlay.md` note) stating that `state/config/capability-overlay.yaml` is the GENERATED ground-truth Marcus reads for "is it wired right now," and the static `specialists:`/`personas:` maps are the org-chart, NOT the routing-truth. (The static registry stays; the overlay is the authority for routing claims.)

---

## T1 Readiness (dev agent reads BEFORE any code)

- **Block-mode/lockstep:** this story's diff touches `state/config/pipeline-manifest.yaml` (a `block_mode_trigger_paths` member). Per CLAUDE.md "Pipeline lockstep regime," read [`docs/dev-guide/pipeline-manifest-regime.md`](../../docs/dev-guide/pipeline-manifest-regime.md) at T1 before code. The change here is **additive `block_mode_trigger_paths` only** (**Tier-2** per the regime — new trigger-path entry; pre-cleared by the braid green-light ratification, NOT Tier-1 dev authority; no pack version bump; pack/HUD byte-invariant) — confirm the lockstep checker (`scripts/utilities/check_pipeline_manifest_lockstep.py`) stays green after the append.
- **Parity pattern to mirror:** `tests/parity/test_skill_md_sanctum_alignment.py` + `tests/parity/_sanctum_parity_base.py` (REPO_ROOT-rooted, filesystem-fact assertions, no mocks/LLM) and the CI shape in `.github/workflows/specialist-parity.yml`.
- **Substrate readings:** `state/config/dispatch-registry.yaml` (19 dispatchable specialists), `state/config/pipeline-manifest.yaml` (`nodes[].specialist_id`), `scripts/utilities/pipeline_manifest.py::load_manifest`, `app/specialists/_stub/passthrough_specialist.py` (stub sentinel), `app/manifest/compiler.py::SPECIALIST_ALIASES` (canonicalization), `skills/bmad-agent-marcus/references/specialist-registry.yaml` (status fields; Story 0's corrected Tracy line at 130-136), `skills/bmad-agent-marcus/capabilities/registry.yaml` (PR-HC/PR-RS stubs — confirm OUT of scope).
- **No mocks; real files; first-run-stands.**

---

## Acceptance criteria (ARTIFACT-level; all dev-agent verifiable via shipped deps, no operator CLIs)

- **AC-1 (generator derives the closed enum):** `derive_overlay(repo_root)` over the live substrate returns a model where every `capability_state ∈ {wired, present-but-unrouted, partial, shelf}` for specialists and `role == orchestrator` for `marcus`; a derived value outside the closed set raises (assert the guard).
- **AC-2 (known-classification correctness — the acceptance witness):** the generated `state/config/capability-overlay.yaml` classifies, against today's substrate: `gary == wired`, `texas == wired`, `tracy == present-but-unrouted`, `cd == partial`, and a known shelf specialist (e.g. `midjourney`) `== shelf`. (These are the mechanically-correct values for the current app state.)
- **AC-3 (not-stub check real):** a specialist whose `app/specialists/<id>/graph.py` builder resolves to the `_stub` passthrough is NOT classified `wired` even if in-manifest + in-dispatch (assert via a `tmp_path` fixture that points a registry entry at the passthrough). The live set has no such case today; the test proves the check is live, not vacuous.
- **AC-4 (generated, deterministic, no-op regen):** running `main()` twice produces a byte-identical file; `--check` exits 0 when fresh and non-zero when a derivation input is mutated.
- **AC-5 (parity staleness gate):** `test_capability_overlay_parity.py` re-derives from live substrate and asserts the committed artifact's `content_hash` matches; passes on the committed artifact.
- **AC-6 (parity fails on injected drift — the RED proof):** in a `tmp_path` copy, removing Tracy's dispatch entry (or adding a fake manifest node for a shelf specialist) re-derives a CHANGED state for that specialist AND the parity hash check FAILS. (Proves the Tracy-drift class is actually caught.)
- **AC-7 (G5 over-promise probe — zero false-wired):** `test_capability_overlay_over_promise_probe.py` runs the fixed corpus; for every row, the overlay-derived `claimed_state` for the targeted capability equals the live-dispatch-graph-derived state; **zero rows claim `wired` for a non-wired capability**; the wired control row IS claimed wired. Mechanical judge only; first-run-stands; single false-`wired` = test failure.
- **AC-8 (CI wired):** `.github/workflows/specialist-parity.yml` runs both new pytest steps and its `paths:` trigger includes the manifest, dispatch-registry, and overlay artifact.
- **AC-9 (lockstep additive, non-regression):** `state/config/pipeline-manifest.yaml` gains exactly the two new `block_mode_trigger_paths` entries; nodes/edges/`pack_version`/`schema_version`/`data_plane_vocabulary_version` are byte-unchanged; `check_pipeline_manifest_lockstep.py` + the existing parity suite + lint-imports stay green.
- **AC-10 (v-next fence honored):** no trial-log/`runs/` consumption (v1.1), no live health-ping (26-10), no LLM judge, no live-pipeline node edit anywhere in the diff (grep-assert: the generator/tests do not import `runs/` paths or any LLM client).

## Non-regression / fences

- Additive only: new generator + artifact + tests + one CI step + two trigger-path entries + one docs pointer line. **No** edit to live pipeline nodes/edges, `production_runner.py`, Marcus runtime, `specialist-registry.yaml` content (read-only), or `capabilities/registry.yaml`. No pack/HUD/schema bump. No `--no-verify`, no force-push.
- The static `specialist-registry.yaml` org-chart STAYS (org-chart ≠ routing-truth); the overlay is additive ground-truth for routing claims, not a replacement of the registry.

## Dev notes

- **Canonicalization is load-bearing:** manifest uses hyphenated `irene-pass1` / `quinn-r` and the alias `elevenlabs`; dispatch-registry uses `irene_pass1` / `quinn_r` / `enrique`. Reuse `app.manifest.compiler.SPECIALIST_ALIASES` + the `replace("-", "_")` normalization (the compiler's `_canonical_specialist_id`) so manifest↔dispatch membership joins correctly. Mis-canonicalization would mis-classify `quinn-r`/`irene-pass1`/`enrique` as unrouted — a false `present-but-unrouted`. Add a regression test pinning these three.
- **`cd` is the only live `partial`** (manifest §4.75 + dispatch + real module + registry PARTIAL). The decision table puts `partial` BEFORE `wired` precisely so `cd` doesn't read as `wired`. Pin this ordering with a test.
- **`marcus` special-case** is the one hard-coded entry (orchestrator, in-manifest, not-in-dispatch). Without the special-case it would mis-read as a defect. Comment it with a spec citation.
- **shelf set** is derived from skills-on-disk minus dispatch-registry: enumerate `skills/bmad-agent-*/SKILL.md` + the registry `specialists:` map (which lists e.g. `canva`, `midjourney`, `vyond`, `articulate`, `coursearc`, `canvas`, `qualtrics`), subtract anything in `dispatch-registry::specialists`. Be conservative: a name on disk but not dispatchable AND not a manifest specialist_id = `shelf`.
- **Don't over-engineer the hash:** sha256 over `json.dumps(sorted derived facts, sort_keys=True)` is enough; the point is a stable staleness signal, not cryptographic ceremony.
- Keep the generator pure + importable so both the CLI, the parity test, and the probe call `derive_overlay` directly (single derivation path — no second re-implementation that could drift).
