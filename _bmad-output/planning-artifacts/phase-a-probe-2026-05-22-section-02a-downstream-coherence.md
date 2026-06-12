# Phase A probe — §02A→downstream integration-drift inventory

**Date:** 2026-05-22
**Anchor:** `ccb141a` (session-START HEAD on `trial/3-2026-05-21`)
**Operator directive:** *"start next session with a BMAD sprint to correct and address as many related issues as can be identified now and corrected proactively"* (2026-05-21T22:30 session-close)
**Pre-probe gate:** /harmonize full-repo CLEAN (`reports/dev-coherence/2026-05-22-0236/harmonization-summary.md`)

## Probe methodology

For each of the 9 surfaces named in `next-session-start-here.md`:
1. Read the module that consumes (or produces for) directive-shape data
2. Capture the field names, enum sets, and validation invariants
3. Compare to the §02A `Directive` baseline (`app/composers/section_02a/directive_model.py`)

## §02A baseline schema (the reference)

**Directive (top-level):** `run_id: UUID4` · `corpus_dir: str` · `sources: list[DirectiveSource]` · `composed_at: datetime` (tz-aware) · `schema_version: int`

**DirectiveSource (per row):** `src_id: str` · `locator: str` · `provider: str` (default `local_file`) · `role: DirectiveRole` enum {`primary | supporting | ignored`} · `description: str | None` · `expected_min_words: int | None` · `excluded_reason: ExcludedReason | None`

Cross-field invariants enforced at the §02A composer:
- `role=ignored` → MUST have `excluded_reason`, MUST NOT have `expected_min_words`
- `role=primary|supporting` → MUST NOT have `excluded_reason`
- Text extensions (`.docx`, `.md`) + role=primary|supporting → MUST have `expected_min_words`
- Binary extensions (`.png`/`.jpg`/`.pdf`/`.pptx`) + role=supporting → MUST NOT have `expected_min_words` (Trial-2 anti-pattern guard)

## Integration drift inventory

### 🔴 BLOCKING (causes Trial-3 attempt-3 to crash)

#### Surface 1 — Texas wrangler input validation

**File:** [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) lines 280-394

**Wrangler expects (per-row, locator-shape):**
- `ref_id: str` (non-empty, unique across sources) ← §02A emits `src_id` ❌
- `role: str` in {`primary | validation | supplementary | visual-primary | visual-supplementary`} ← §02A emits `supporting | ignored` ❌
- `provider: str` in {`local_file | pdf | docx | md | url | notion | notion_mcp | playwright_html | box | image`} ← §02A emits `local_file` ✓
- `locator: str` ← §02A emits `locator` ✓

**Cross-source invariant:** at least one source must have `role` in {`primary | visual-primary`}.

**Drift items:**

| # | §02A emits | Wrangler expects | Severity | Notes |
|---|---|---|---|---|
| D1 | `src_id` | `ref_id` | **HARD-CRASH** | First field validated; this is what crashed Trial-3 attempt-2 |
| D2 | `role: supporting` | `role: supplementary` | **HARD-CRASH (next gate)** | Would fail even after D1 fix |
| D3 | `role: ignored` | (no equivalent) | **HARD-CRASH (conditional)** | Tejal corpus dodged this; future corpora with `.gitkeep`/`.DS_Store` would crash |

### 🟡 SOFT-DEGRADE (data loss, no crash)

#### Surface 2 — Texas wrangler `result.yaml::materials[]` (consumed by Marcus / Irene)

**File:** [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) lines 1660-1738

**Wrangler writes:**
```yaml
materials:
  - ref_id: <wrangler input ref_id>
    role: <wrangler input role>  # primary | validation | supplementary | visual-*
    quality_tier: <enum>
    extractor_used: <str>
    content_path: "extracted.md" if role == "primary" else None
    word_count: int
    line_count: int
    heading_count: int
    quality_report: {completeness_ratio, structural_fidelity, known_losses, evidence}
```

**Drift item:**

| # | Surface | Detail | Severity |
|---|---|---|---|
| D4 | `materials[].role` | Hardcoded string compare `o.role == "primary"` in wrangler (line 1681) sets `content_path` only for `primary`. If §02A's `supporting` slipped through validation (it can't currently — D2 blocks first), no harm. But any future role-vocab fork would silently set `content_path=None`. | LOW (advisory; D2 is the actual blocker) |

#### Surface 3 — Texas wrangler `metadata.json` (consumed by `pre_packet.py`)

**Wrangler writes** (line 1240-1266):
```json
{
  "run_id": "...",
  "generated_at": "...",
  "provenance": [{"ref_id": "...", "kind": "...", "ref": "...", "role": "...", "description": "...", "extractor_used": "...", "fetched_at": "..."}],
  "primary_consumption_path": "extracted.md"
}
```

**`pre_packet._build_sme_refs` expects** ([`app/marcus/intake/pre_packet.py`](../../app/marcus/intake/pre_packet.py) line 175-207):
```python
metadata["sme_refs"]: [{"source_id": "...", "path": "...", "content_digest": "..."}]  # preferred
# OR fallback:
metadata["primary_source"]: str  # used to construct a synthetic SourceRef with source_id=<str>
```

**Drift items:**

| # | Surface | Detail | Severity |
|---|---|---|---|
| D5 | `metadata` keys | Wrangler writes `provenance` (per-source rich array) + `primary_consumption_path`; pre_packet reads `sme_refs` (different shape) OR `primary_source` (single str). **Neither key exists in the wrangler output.** | **MEDIUM** — soft-degrade: pre_packet falls back to `source_id="unknown"` + sha256 of extracted.md bytes. SME provenance is lost in the Marcus log. |
| D6 | Field-name fork: `ref_id` (wrangler) vs `source_id` (pre_packet) | Even if the wrangler produced `sme_refs`, the field naming would need translation. Plus pre_packet uses `content_digest` (not in wrangler provenance). | **LOW** — solvable at the same touch as D5. |

### ⚪ NOT-DRIFT (audited and clean)

| Surface | Module | Why not-drift |
|---|---|---|
| Irene Pass-2 graph | [`app/specialists/irene/graph.py`](../../app/specialists/irene/graph.py) | Reads `envelope_payload` from `state.cache_state.cache_prefix` (in-state envelope carrier). Shape-agnostic — does NOT directly read wrangler bundle. Drift surfaces at the envelope-construction step (Marcus side), not at Irene. |
| §04 G1 decision card | [`docs/conversational-gates/g1.j2`](../../docs/conversational-gates/g1.j2) + [`app/marcus/orchestrator/pre_gate_marcus.py`](../../app/marcus/orchestrator/pre_gate_marcus.py) | Jinja2 template with slot variables (`upstream_contributions`, `pending_nodes`, `artifact_paths`). Shape-agnostic — receives whatever `slot_values` the caller threads in. |
| §04A per-plan-unit verdict | [`app/models/operator_verdict_section_04a.py`](../../app/models/operator_verdict_section_04a.py) | `plan_unit_id: str` (opaque) + `verb` + `decision_card_digest`. Not source-vocab-bound. |
| §04.55 run-constants lock | [`app/models/operator_verdict_section_04_55.py`](../../app/models/operator_verdict_section_04_55.py) | `run_constants_id: str` (opaque) + verb. Not source-vocab-bound. |
| §07C storyboard gate | [`app/gates/section_07c/`](../../app/gates/section_07c/) | grep for `ref_id\|src_id\|source_id\|materials\|supporting\|supplementary` → 0 matches. Operator-verdict shape only. |
| §11 voice-selection gate | [`app/gates/section_11/`](../../app/gates/section_11/) | 0 matches. Not source-vocab-bound. |
| §15 final-bundle writer | [`app/marcus/orchestrator/writers/section_15_bundle.py`](../../app/marcus/orchestrator/writers/section_15_bundle.py) | Path-based digests (assembly_bundle_path, descript_assembly_guide_md_digest, trial_3_transcript_anchor). Not source-vocab-bound. |

### 🧹 CLEANUP-class (not blocking but worth folding into Epic 34)

| # | Surface | Detail | Severity |
|---|---|---|---|
| C1 | Legacy [`app/marcus/orchestrator/directive_composer.py`](../../app/marcus/orchestrator/directive_composer.py) (Story 7a.1 era) | Still exists in codebase. Uses `ref_id` + `role: supporting` (same `supporting`-vs-`supplementary` drift as §02A). Was the broken-fallback corpus-scan composer wired pre-Trial-3-wiring SCP. Now dead runtime code post §02A wiring (no production import path). Referenced by 7 test files (`tests/composition/test_texas_to_cd_chain.py`, `tests/unit/marcus/orchestrator/test_directive_composer_*.py`, `tests/parity/test_trial_475_*.py`, `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py`). | **LOW** — runtime-dead but test-active. Candidate for delete + test rewire after Epic 34 substrate changes settle. |

## Drift summary (count)

| Class | Count | Outcome |
|---|---|---|
| 🔴 Hard-crash blocking | 3 (D1, D2, D3) | Must resolve before Trial-3 attempt-3 |
| 🟡 Soft-degrade | 3 (D4, D5, D6) | Should resolve in same touch — both worth-doing-once and worth-doing-coherently |
| ⚪ Not-drift | 7 surfaces | No action |
| 🧹 Cleanup-class | 1 (C1) | Fold into Epic 34 cleanup wave OR file as separate post-Trial-3 follow-on |

**Total drift items requiring touch:** 6 (D1-D6); **plus** 1 cleanup candidate (C1).

## Phase B decision options (for party-mode)

Three directions named in `next-session-start-here.md`, now refined with the full drift inventory above:

### Option harmonize-downstream-to-§02A

- §02A's `src_id` + `{primary, supporting, ignored}` is the canonical vocabulary going forward
- Update Texas wrangler: rename `ref_id` → `src_id`, add `supporting`/`ignored` to allowed-role set (or rename `supplementary` → `supporting`), add `excluded_reason` handling for `ignored`, write `sme_refs` (in addition to or instead of `provenance`) for pre_packet compat
- Update `result.yaml::materials[].role` consumers (none currently load-bearing on the role enum besides wrangler-internal)
- Update `pre_packet.py` to read `sme_refs` from wrangler-written metadata (or rename the field)
- Update legacy `directive_composer.py` to match §02A vocab OR delete it (C1)
- **Blast radius:** ~2 specialist files + ~5 test files + ~1 metadata-shape change
- **Honors:** "newer schema is the deliberate redesign" — §02A's `supporting`/`ignored` taxonomy reflects the LLM-judged-source-classification model

### Option revert-§02A-to-existing-canonical

- Texas's `ref_id` + `{primary, validation, supplementary, visual-primary, visual-supplementary}` stays canonical
- Update §02A composer: rename `src_id` → `ref_id`, rename `supporting` → `supplementary`, drop `ignored` (or remap to `excluded_reason`-only sentinel + filter-out at compose time)
- Update §02A 12-test suite + 4 M-A1 adapter wiring-contract tests to use new vocab
- **Blast radius:** ~1 composer file + ~16 test files (all §02A test surface)
- **Honors:** "minimize-blast-radius" — existing canonical doesn't move

### Option adapter-translation-layer

- `app/composers/section_02a/cli_adapter.py` translates §02A output → wrangler-expected shape at the boundary
- §02A composer stays untouched (preserves the deliberate LLM-judged design)
- Texas wrangler stays untouched (preserves existing canonical)
- Adapter handles 3 field/enum mappings + filters out `role: ignored` rows (or maps to wrangler's enum somehow)
- **Blast radius:** ~1 adapter file + ~5 adapter-test files; 0 changes to either side
- **Honors:** "pragmatic non-breaking patch" but adds an architecture seam (two source-of-truth schemas)
- **D5/D6 still need separate fix** — adapter wouldn't touch metadata.json shape

## Recommendation for party-mode framing

The three options span a trade-space:
- **harmonize-downstream-to-§02A** is the cleanest long-term but largest immediate blast-radius
- **revert-§02A-to-existing-canonical** preserves wrangler stability but loses the §02A-side richness (`ignored` taxonomy + content-aware `expected_min_words` defaults)
- **adapter-translation-layer** is the smallest patch but introduces lasting schema duality

D5/D6 (metadata.json shape) are independent of the role/field-name choice and **need a separate decision** regardless: should the wrangler emit `sme_refs` matching pre_packet's contract, OR should pre_packet read `provenance` matching wrangler's contract?

## Pre-existing context worth carrying into party-mode

- §02A is the NEWER deliverable (Story 7c.3a, 2026-05-05) — but the LLM-judged classification was the explicit design goal, not the field-name choices
- The `src_id` vs `ref_id` rename in §02A appears to have been an unforced authorship choice; no SCP cited a reason for diverging from wrangler's vocab
- The `supporting` vs `supplementary` divergence is identical in the LEGACY directive composer (`app/marcus/orchestrator/directive_composer.py` line 120/132) — i.e., **both directive composers have ALWAYS been incompatible with the wrangler's role enum**. The legacy composer was never actually integration-tested against the wrangler either (Trial-2 attempts halted before specialist dispatch; Trial-3 attempt-2 is the first integration evidence)
- The `ignored` taxonomy is new to §02A and is a deliberate richness gain — `git-marker-file` / `macos-metadata` / `windows-metadata` / `llm-classified-out-of-scope` give the operator first-class visibility into LLM filtering decisions
- The `excluded_reason` enum (4 values) is new to §02A and has no wrangler equivalent

## Files referenced in this probe (for audit trail)

- [`app/composers/section_02a/directive_model.py`](../../app/composers/section_02a/directive_model.py) — §02A baseline
- [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) — surfaces 1, 2, 3
- [`app/specialists/irene/graph.py`](../../app/specialists/irene/graph.py) — Irene envelope shape
- [`app/marcus/intake/pre_packet.py`](../../app/marcus/intake/pre_packet.py) — metadata.json consumer
- [`app/marcus/lesson_plan/log.py`](../../app/marcus/lesson_plan/log.py) — `SourceRef` model
- [`app/marcus/orchestrator/pre_gate_marcus.py`](../../app/marcus/orchestrator/pre_gate_marcus.py) — G1 LLM node
- [`docs/conversational-gates/g1.j2`](../../docs/conversational-gates/g1.j2) — G1 template
- [`app/models/operator_verdict_section_04a.py`](../../app/models/operator_verdict_section_04a.py) — §04A verdict
- [`app/models/operator_verdict_section_04_55.py`](../../app/models/operator_verdict_section_04_55.py) — §04.55 verdict
- [`app/gates/section_07c/`](../../app/gates/section_07c/) · [`section_11/`](../../app/gates/section_11/) · [`section_15/`](../../app/gates/section_15/) — gate poll surfaces (all not-drift)
- [`app/marcus/orchestrator/writers/section_15_bundle.py`](../../app/marcus/orchestrator/writers/section_15_bundle.py) — §15 bundle writer
- [`app/marcus/orchestrator/directive_composer.py`](../../app/marcus/orchestrator/directive_composer.py) — legacy composer (C1 cleanup candidate)
