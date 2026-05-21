# Irene Pass 2 Authoring Template

**Canonical authoring-time contract for Pass 2 segment-manifest emission.**

Story §7.1 discipline. Pair with [`pass-2-procedure.md`](./pass-2-procedure.md) for the authoring flow; this template is the **structural contract** that Pass 2 output must conform to before Storyboard B renders. Validation is deterministic (JSON Schema + fail-closed lint), not LLM-mediated.

Authoritative schema: [`state/config/schemas/segment-manifest.schema.json`](../../../state/config/schemas/segment-manifest.schema.json).
Enforcement: [`scripts/validators/pass_2_emission_lint.py`](../../../scripts/validators/pass_2_emission_lint.py) (invoked at end of Pack v4.2 §07; failing lint blocks §08 Storyboard B render).
Upstream-reference reader: [`skills/bmad-agent-content-creator/scripts/motion_gate_receipt_reader.py`](../scripts/motion_gate_receipt_reader.py).

---

## Why this template exists

Trial `C1-M1-PRES-20260419B` §6 fix-on-the-fly log surfaced three **structural** emission bugs that cost material time at §14 Compositor:

| § | Bug | Durable fix |
|---|---|---|
| §6.3 | Irene emitted BOTH `motion_asset` and `motion_asset_path` on motion cards | Emit ONLY `motion_asset_path`; never emit the legacy `motion_asset` key |
| §6.4 | `visual_file` was missing on 13/14 segments; §14 back-filled from gates | Populate `visual_file` at Pass 2 emission, NOT at §14 back-fill |
| §6.5 | `motion_duration_seconds` was null despite Motion Gate receipt carrying the value | Carry `motion_duration_seconds` forward from the Motion Gate receipt at Pass 2 emission |

The schema + lint catch all three in seconds, deterministically, before any downstream spend. Irene's creative-layer output (narration prose, behavioral intent, segment ordering, cluster-boundary seams) is **NOT** constrained by this template — creative judgments continue to be LLM-driven and reviewed by Quinn-R / Vera.

---

## Structural contract (schema-enforced)

### Envelope (top-level required fields)

```yaml
schema_version: "1.1"            # MUST be exactly "1.1"
run_id: <string>                 # MUST be non-empty
generated_at_utc: <ISO-8601>     # MUST be non-empty (UTC, Zulu preferred)
generated_by: "Irene Pass 2"     # MUST be non-empty
segments: [...]                  # MUST be a non-empty list of segment objects
```

Other envelope fields (`cluster_density`, `narration_directive`, `slide_echo_policy`, etc.) are permitted and unconstrained — the template is additive-permissive at envelope level.

### Segment (per-item required fields)

```yaml
- id: <string>                          # MUST be non-empty
  slide_id: <string>                    # MUST be non-empty
  card_number: <int ≥ 1>                # MUST be ≥ 1
  visual_mode: video | static | animation | null
  motion_asset_path: <string> | null    # see per-mode rules below
  motion_duration_seconds: <number> | null  # see per-mode rules below
```

Authoring-layer fields (`narration_text`, `behavioral_intent`, `master_behavioral_intent`, `visual_references`, `narration_burden`, `cluster_id`, `cluster_role`, etc.) are permitted and unconstrained.

### Per-mode rules

| `visual_mode` | `visual_file` | `motion_asset_path` | `motion_duration_seconds` |
|---|---|---|---|
| `"video"` | **REQUIRED (non-empty string)** | **REQUIRED (non-empty string)** | **REQUIRED (positive number, ≥ 0.001s tolerance against receipt)** |
| `"static"` | **REQUIRED (non-empty string)** | null | null |
| `"animation"` | **REQUIRED (non-empty string)** | null | null |
| `null` | (optional) | null | null |

### Upstream-reference cross-validation (lint only)

The lint cross-references the Motion Gate receipt for every segment with `visual_mode: "video"`:

- If the manifest has `motion_duration_seconds: null`, the receipt's `duration_seconds` MUST be carried forward.
- If the manifest has a concrete `motion_duration_seconds`, it MUST agree with the receipt (tolerance 0.001s).
- If the manifest claims `visual_mode: "video"` but the receipt has no matching `slide_id` in `non_static_slides`, the manifest is asserting unapproved motion — lint rejects.

---

## Legacy key ban list (do NOT emit)

| Key | Reason | Replacement |
|---|---|---|
| `motion_asset` | §6.3 legacy duplicate (pre-Storyboard-B era); downstream ambiguity | `motion_asset_path` only |

The ban is declarative in the schema (`not: {required: [motion_asset]}`). Any future legacy-vocabulary additions land in this section + the schema in lockstep.

---

## Reading-path repertoire (Sprint 2)

The Sprint-1 convention `narration_directive: z-pattern-literal-scan` is now one of seven structured patterns in the **reading-path repertoire**. The envelope (or a per-segment override) carries a `reading_path` sub-object with `{pattern, confidence, evidence, fallback}`. Registry: [reading-path-patterns.yaml](../../../state/config/reading-path-patterns.yaml). Schema: `reading_path` sub-object in [segment-manifest.schema.json](../../../state/config/schemas/segment-manifest.schema.json). Narration-grammar worked examples: [pass-2-grammar-riders-examples.md](./pass-2-grammar-riders-examples.md).

### Enum (closed)

| Pattern | Narration cadence | Lint |
|---|---|---|
| `z_pattern` | four-beat-sweep (headline / body / visual / CTA) | warning |
| `f_pattern` | drill-down at evidence markers | warning |
| `center_out` | establish-orbit-return-to-hero | warning |
| `top_down` | spine-item boundary cadence | warning |
| `multi_column` | column-boundary bridges | warning |
| `grid_quadrant` | compare/contrast connectives | warning |
| `sequence_numbered` | ordinal markers (first/second/next/step N) | **fail-closed** |

`sequence_numbered` is the only pattern with fail-closed lint in v1 (Murat Sprint-2 ruling) — ordinal-marker absence on that classification is a contract violation.

### Envelope vs. per-segment

The envelope's `reading_path` is the default for every segment. A segment may override by emitting its own `reading_path` sub-object. Backward-compatibility: when neither is present, the lint normalizes free-text `narration_directive: z-pattern-literal-scan` → `reading_path.pattern: "z_pattern"` with `fallback: false` at validation time (preserving byte-identical Sprint-1 fixtures).

---

## Worked example: static segment

```yaml
- id: apc-c1m1-tejal-20260419b-motion-card-02
  slide_id: apc-c1m1-tejal-20260419b-motion-card-02
  card_number: 2
  cluster_id: c-u01
  cluster_role: body
  cluster_position: develop
  narrative_arc: develop
  selected_template_id: concept-anchor
  visual_mode: static
  motion_type: null
  motion_asset_path: null
  motion_duration_seconds: null
  visual_file: gamma-export/apc-c1m1-tejal-20260419b-motion_slide_02.png
  motion_status: not_applicable
  fidelity: creative
  slide_echo: paraphrase
  narration_text: >
    Burnout is not a personal failure. It is a systems signal — and that
    signal is an invitation to design.
  behavioral_intent: >
    Reframe burnout as systems signal; set up the designer-lens perspective.
```

**Why this is correct:**
- `visual_mode: static` → `visual_file` is populated (§6.4 fix).
- No motion fields populated (motion_asset_path null, motion_duration_seconds null).
- `motion_asset` legacy key is absent (§6.3 ban).
- No Motion Gate receipt cross-reference needed (static segment).

---

## Worked example: motion segment

```yaml
- id: apc-c1m1-tejal-20260419b-motion-card-01
  slide_id: apc-c1m1-tejal-20260419b-motion-card-01
  card_number: 1
  cluster_id: c-u01
  cluster_role: head
  cluster_position: establish
  narrative_arc: establish
  selected_template_id: emotional-arc
  visual_mode: video
  motion_type: video
  motion_asset_path: motion/slide-01-motion.mp4
  motion_duration_seconds: 5.041                # carried from Motion Gate receipt
  visual_file: gamma-export/apc-c1m1-tejal-20260419b-motion_slide_01.png
  motion_status: approved
  fidelity: creative
  slide_echo: paraphrase
  narration_text: >
    Watch the physician on screen. That pause — the weight behind the eyes,
    the handheld device, the corridor pressing in around them — is not a
    personal failure. It is a systems signal.
  behavioral_intent: >
    Establish the clinician-as-designer identity reframe.
```

**Why this is correct:**
- `visual_mode: video` → `visual_file` populated, `motion_asset_path` populated, `motion_duration_seconds` populated with receipt value 5.041s (§6.5 fix).
- `motion_asset` legacy key is absent (§6.3 ban).
- Upstream-reference cross-validation: Motion Gate receipt's `non_static_slides[0].duration_seconds == 5.041` matches the manifest — lint passes.

---

## Retrieval-intake-consuming segments

When a segment narrates findings from Tracy-dispatched retrieval (sibling Sprint #1 story `irene-retrieval-intake`), the segment carries an additive `retrieval_provenance` field. The canonical worked example for that shape lives in the intake contract, not here:

> See [retrieval-intake-contract.md](./retrieval-intake-contract.md) for the intake-attached segment shape and worked example.

This template's segment-manifest schema permits `retrieval_provenance` as an additive field (`additionalProperties: true`). The intake story's contract doc is single source of truth for its shape.

---

## How lint invocation works

From Pack v4.2 §07 end, after Irene emits `segment-manifest.yaml`:

```bash
python scripts/validators/pass_2_emission_lint.py \
  --manifest course-content/staging/.../segment-manifest.yaml \
  --motion-gate-receipt course-content/staging/.../motion-gate-receipt.json
```

Exit codes:
- `0` — clean; §08 Storyboard B renders.
- `1` — violations found; lint blocks §08 with per-segment findings on stdout.
- `2` — infrastructure error (missing file, malformed input); treat as §08-blocker pending operator triage.

---

## Version history

| Schema version | Story | Change |
|---|---|---|
| `1.1` | §7.1 (2026-04-22) | Initial authoritative schema — structural enforcement of §6.3 / §6.4 / §6.5 durable fixes; convention promoted to contract. |

Future schema edits update the version per [`_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md`](../../../_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md) semver-for-schemas discipline. This template updates in lockstep with the schema (doc-parity enforced by `tests/irene/test_pass_2_authoring_template_doc_parity.py`).
