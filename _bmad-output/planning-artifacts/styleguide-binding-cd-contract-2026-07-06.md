# Styleguide-binding → CD-consumption contract (W2 one-pager)

**Status:** S0 deliverable of the Canonical Production Conversation arc (Winston amendment W2, party record 2026-07-06). Both S1 (CD contract) and S2 (picker wiring) implement AGAINST this page; drift from it is a spec defect, not an implementation choice.

> **⚠️ AMENDED 2026-07-06 (same session) per the §7 RE-SCOPE ADDENDUM in the party record + shadow-monitor SOP-001.** The original "single runtime resolution point / Gary never reads the yaml" end-state below is now STAGED: SOP-001 proved CD is already live + load-bearing (F-101), the picker→gamma_settings→Gary seam already works and carries the protected source-detail→Gamma invariant, and Gary's LATE binding (§07, post-picks) is why that invariant is safe (F-104). **S1-era contract: CD emits the resolution as a sibling `styleguide_resolution` DATA block (deterministic neck, unconditionally present, `status` enum incl. `no_picks_at_authoring`), through a SHARED pure resolver re-homed to `app/styleguide/resolver.py` (gary/styleguide_library.py becomes a thin re-export); Gary keeps authority and shadow-parity-audits CD's block (three-outcome: ok / expected-ordering-gap INFO / divergence WARN).** The authority flip (Gary consumes the envelope; its yaml read collapses) is the deferred **S-flip** story gated on 3-consecutive-clean + 1-cross-deck live parity (full criteria in party record §7). Amended D2: single resolution *logic* + single authoritative *record*; the orchestrator's Leg-C `min_cluster_floor` yaml read is a chartered permanent exception. CD skip-records are DEAD (CD always runs, load-bearing at §06); presence semantics survive as `schema_version` discrimination for legacy bundles. CD's input seam = orchestrator-side `directive_projection` at the §4.75 dispatch site (CD never opens the directive file). §2/§3 below read through this amendment.

## The seam in one sentence (end-state, post-S-flip)

The **picker** commits an operator-confirmed styleguide *reference* into the run's directive at trial-start; **CD** (node 4.75) is the single point that *resolves* that reference into frozen creative settings, written once into the ProductionEnvelope; **Gary** (node 07) composes mechanically from the envelope artifact and never reads the styleguide SSOT at runtime.

## 1. What the picker commits (S2's write; producer = `run_picker_preflight`)

- **Where:** into the run **directive** at trial-start, BEFORE run-dir creation; persisted into the run bundle at creation time. The continuation walk reads the persisted pick from disk; resume/recover NEVER re-prompt and NEVER fall back to a default.
- **Shape (reference, not resolution):**
  - `styleguide_binding.picks[]` — one or two entries (slot A [+ slot B]), each `{guide_name, guide_version_or_digest}` naming a record in `state/config/gamma-style-guides.yaml`
  - `styleguide_binding.versions` — `1 | 2` (the slot-bar mechanic; 2 ⇒ A/B run)
  - `styleguide_binding.provenance` — `{run_tag, selection_code, publish_url, picked_by, picked_at, reuse_of (nullable: prior run_id when the fast-path was taken)}`
- **Invariants:** label-keyed zero-transposition (A→A, B→B) per the frozen `SGP-` grammar; a stale/foreign selection code is rejected at decode, pre-commit; the pick is a NAME + VERSION only — the picker never copies styleguide fields into the directive.

## 2. What CD consumes and authors (S1/S3's read+write; node 4.75)

- **Reads:** the directive's `styleguide_binding` (reference) + the creative directive (source-derived instructions/keywords/image briefs — Marcus-transported, never Marcus-authored) + `production_mode` + G0-enrichment outputs when present.
- **Writes exactly one envelope contribution — `ResolvedCreativeDirective`** (schema-versioned, `output_digest`-carrying, append-only per the carrier invariant):
  1. **Bound styleguide resolution** — each pick resolved against the SSOT *at that moment*, full field-set snapshotted per variant (prompt-config + page settings + template-or-theme), stamped `{guide_id, guide_version, resolved_at}`. Studio companion selected by the `production_mode` tag; the studio branch rejects Classic-only keys.
  2. **Experience profile** — CD-owned resolution; explicit, never silently inferred; underdetermined inputs ⇒ named fallback on the record.
  3. **Layering manifest** — ordered, per field-family: base = styleguide snapshot; overlay = source-derived values; **overlay wins**. Structural collisions (source demands what the picked guide's production_mode cannot express) are surfaced as a named `conflicts[]` entry — resolved for source, discrepancy on the record ("source wins loudly," Dan D3).
- **Skip semantics (W5/D-skip, presence-not-absence):** the node's ONLY two exits both write — the artifact, or an explicit skip-record `{skipped: true, reason ∈ closed enum, predicate_inputs}`. Legitimate skip reasons: `resume-artifact-already-present` (idempotent re-entry; never re-resolve mid-run) and `no-visual-deliverable`. **`no-pick` is not a skip reason** (post-S4 it is a trial-start hard failure, upstream of CD). Envelope write failure = halt, never a warning.

## 3. What Gary consumes (existing seam, tightened by AC)

- Gary's `styleguide:<name>` base-layer seam composes from the **envelope's ResolvedCreativeDirective**, per its layering manifest — mechanical composition, zero creative discretion.
- **AC (Dan D2, single-resolution-point):** no node other than CD reads `state/config/gamma-style-guides.yaml` at run time. Gary/studio-branch reads of the SSOT are refactored to envelope reads or fail the review.
- Downstream keys off **presence**: finding neither a ResolvedCreativeDirective nor a skip-record in the envelope = loud failure (the route-around state is structurally unrepresentable).

## 4. Protected invariants riding this seam

- **source-detail→Gamma conveyance:** source-derived instructions/keywords/prompts compose ON TOP of the styleguide base and WIN; the layering manifest makes this auditable per field-family. Named regression check on S1, S2, S8.
- **Carrier robustness:** the contribution is schema-validated, versioned, additive-safe, append-only, digest-stamped; survives resume/recover with the SAME resolution intact (no mid-run re-resolution drift).

## 5. Sequencing note

During the S2→S3 window the WARN-seed default remains reachable (status quo); S4 flips it to FAIL-LOUD once cd-envelope-authoring (S3) has landed. The picker never resolves; CD never picks; Marcus transports and narrates; the runner enforces.
