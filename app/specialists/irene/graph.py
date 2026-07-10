"""Irene Pass 2 specialist — 9-node scaffold-conformant graph (Story 2a.2).

Per AC-B (with MF4 bounded-scope rider), the `act` node assembles a Pass 2
narration prompt, invokes the LLM via `app.models.adapter.make_chat_model`,
and parses the response. The LLM does the procedural narration authoring per
[`pass-2-procedure.md`](../../../skills/bmad-agent-content-creator/references/pass-2-procedure.md);
Python is bounded to prompt-assembly + dispatch + parse — NO procedural
narration logic in Python.

Cache-prefix stability (NFR-I6 + MF6): `_assemble_pass_2_prompt` produces
byte-identical output for byte-identical inputs across in-process iterations.
Determinism contract (per T4 party-mode round 2026-04-24, Murat MF3 binding):
- Sanctum file ordering: `sorted(..., key=lambda p: p.as_posix())` for
  cross-platform stability (Windows backslash vs POSIX slash sort divergence).
- `Path.read_text(encoding="utf-8")` normalizes CRLF→LF on read regardless of
  on-disk newline (Python `newline=None` default).
- Envelope payload: `json.dumps(payload, sort_keys=True, ensure_ascii=True,
  separators=(",", ":"))` — explicit signature pinned for byte-stability.
- NO datetime, UUIDs, or randomized components in prompt body.

The empty-sanctum case (Story 2a.2) yields a deterministic empty-string sanctum
section. Story 2a.3 inherits the populated-and-locked sanctum pattern.

Gate-decision binding (AC-E + MF6 + Winston W2): `_gate_decision` retains the
`interrupt()` pattern + `resume_from_verdict` import binding for Contract C3
without invoking at runtime. Pass-2 runtime routes around `gate_decision` on
clean `verify`; only synthetic verify-fail envelopes traverse it (raises
`NotImplementedError` per Slab-1 stub semantics).

ENVELOPE-CARRIER-HACK (Slab 2 bounded-scope decision, T4 party-mode 2026-04-24):
RunState has no first-class envelope field at Slab 1 substrate. To deliver the
Pass-2 envelope payload to `_act` from a synthetic test fixture, the payload is
encoded as sorted-keys canonical JSON in `state.cache_state.cache_prefix`. This
overloads the field's documented role ("Stable prefix derived from sanctum +
model + manifest version") deliberately — Slab 3 retires this hack by adding
`RunState.specialist_envelope` (or equivalent) per the deferred-inventory
follow-on entry. See `_bmad-output/planning-artifacts/deferred-inventory.md`
§Named-But-Not-Filed Follow-Ons.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, get_args

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import ValidationError

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.marcus.lesson_plan.pedagogy_annotation import build_pedagogy_annotations
from app.models.adapter import make_chat_model
from app.models.perception import PerceptionArtifact as RichPerceptionArtifact
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.run_state import RunState
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS
from app.specialists._shared.figure_tokens import (
    _FIGURE_RE,
    _figure_near_match,
    _figures,
    _normalize_figure,
)
from app.specialists._shared.voice_direction_map import voice_direction_active
from app.specialists._shared.voice_provider_text import extract_tags
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.authoring.pass_2_template import RhetoricalRole
from app.specialists.irene.authoring.voice_direction_annotation import (
    VoiceDirectionError,
    annotate_segments_with_voice_direction,
)
from app.specialists.irene.authoring.warm_callback import (
    gate_warm_callback,
    select_grounded_callback_anchors,
)
from app.specialists.irene.authoring.warm_callback_authoring import (
    render_warm_callback,
    warm_callback_authoring_active,
)
from app.specialists.irene.payload_contract import CONSUMED_PAYLOAD_KEYS
from app.specialists.source_bundle import read_extracted_source
from scripts.utilities.reading_path_classifier import (
    cadence_tokens_for_pattern,
    ordered_element_keys_for_reading_path,
)

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
SANCTUM_DIR: Path = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"
IRENE_REFERENCES_DIR: Path = (
    REPO_ROOT / "skills" / "bmad-agent-content-creator" / "references"
)

# L5 reference subset bundled into every Pass-2 prompt. Order matters for
# byte-stability — sorted alphabetically + frozen.
PASS_2_PROMPT_REFERENCES: tuple[str, ...] = (
    "cluster-narrative-arc-schema.md",
    "pass-2-authoring-template.md",
    "pass-2-grammar-riders-examples.md",
    "pass-2-procedure.md",
    "retrieval-intake-contract.md",
    "spoken-bridging-language.md",
)

PASS_2_SYSTEM_MESSAGE: str = (
    "You are Irene, a senior instructor for health-sciences and "
    "medical-education content. Right now you are SPEAKING ALOUD to a live "
    "room, with the slide visible on the screen behind you. You are not "
    "writing a script or a caption — you are a presenter saying out loud the "
    "ideas the slides exist to teach. The narration you produce is your spoken "
    "voice in that room.\n\n"
    "VOICE RULES (binding):\n"
    "1. Speak the IDEA; let the visual support it — NEVER narrate the "
    "diagram's geometry. The slide is evidence behind you, not your subject. "
    "Banned constructions: \"the diagram/chart/timeline/figure shows / traces "
    "/ lays out / depicts\", \"on the left/right/top/bottom\", \"this slide "
    "presents/shows\", \"as you can see\". If a sentence's grammatical subject "
    "is a visual element (the fishbone, the chart, the journey), rewrite so "
    "the subject is an IDEA or the AUDIENCE.\n"
    "2. Grounding is for ACCURACY, not content. Use what you perceive ONLY to "
    "keep facts/numbers/labels exact. Do NOT report the slide back. Ask: "
    "\"Having fully absorbed this slide, what would I SAY to make a room "
    "understand the point?\" — then say that.\n"
    "3. Address a present audience and give every fact a STAKE. Use second "
    "person where natural (\"notice\", \"think about\", \"you've felt this\"). "
    "Every number/term arrives with WHY it matters to the listener, not just "
    "that it's on the slide.\n"
    "4. Deliver the slide's ARGUMENT, not an inventory of its parts. Name "
    "components only as the spine of the story they add up to.\n"
    "SELF-TEST: \"If the line would still make sense as a caption printed "
    "under the image, it has failed — a caption describes the picture; a "
    "presenter says the thing the picture exists to prove.\"\n\n"
    "Follow the Pass 2 procedure exactly. The narration must stay accurate to "
    "and grounded in the perceived slide evidence and source corpus; never "
    "confabulate facts, numbers, labels, or visual elements that are not "
    "present in what you are given. When clusters are present, honor cluster "
    "boundaries and bridge cadence. Output deterministic, well-structured "
    "spoken prose; weave visual references in only as the spine of the spoken "
    "argument, never as a description of the slide's layout."
)

VISUAL_AUTHORITY_HEADER = (
    "## Visual authority - perceived slide evidence (SOLE visual authority)"
)
EXPECTED_VISUAL_PLAN_HEADER = (
    "## Expected visual plan - brief/Gary signals "
    "(subordinate; may be stale; defer to perceived)"
)
UNVERIFIED_VISUAL_AUTHORITY = "UNVERIFIED — no perceived authority"

# Leg-4 narration-fidelity down-payment (SOURCE-direction figure gate + reground).
# Env toggle, default OFF -> byte-identical prompt + inert gate (mirrors the
# MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE / g0_enrichment_wiring flag idiom). Flag
# ON wakes (a) the source-figure reground block in the Pass-2 prompt and (b) the
# additive SOURCE-direction fail-loud gate in _act_pass_2. This is a real product
# defect fix (Irene faithfully narrating Gamma-confabulated numerals over source
# truth on EVERY run); it is not shaped to make any proofing run pass.
FIGURE_FIDELITY_ACTIVE_ENV = "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"

SOURCE_FIGURE_AUTHORITY_HEADER = (
    "## Source figure authority - authoritative SOURCE numerals "
    "(provenance only; speech still requires on-screen presence)"
)

PERCEIVED_SPEAKABLE_FIGURES_HEADER = (
    "## Perceived speakable figures "
    "(digit-form; SOLE on-screen authority for spoken numerals)"
)

# Prompt-only marker when a source digit-form figure is absent from the deck union.
# Gates still receive the unredacted source_text; this only shapes generation input.
UNRENDERED_SOURCE_FIGURE_TOKEN = (
    "[SOURCE FIGURE NOT ON DECK — paraphrase without digit-form]"
)


def narration_figure_fidelity_active() -> bool:
    """Return True iff the Leg-4 narration figure-fidelity gate is woken (default OFF).

    The underlying DEFECT is every-run (Irene faithfully narrates
    Gamma-confabulated numerals over source truth on EVERY production run); the
    FIX, however, ships opt-in — this gate is flag-gated and NOT yet default-on, so
    it stays inert / byte-identical until ``MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE``
    is set.
    """
    return os.environ.get(FIGURE_FIDELITY_ACTIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class Pass2GroundingError(SpecialistDispatchError):
    """Pass-2 grounding input absent or output unjoined to the real slide roster.

    dp-v1.1 (Trial-3 cycle-4 defect 1): an ungrounded Pass-2 prompt produces
    confabulated narration with ``provenance: real`` — a false green. Raising
    this (SpecialistDispatchError family) error-pauses the trial recoverably
    instead of shipping invented content downstream.
    """


class Pass2ReadingPathError(SpecialistDispatchError):
    """Pass-2 narration order does not conform to perceived reading path."""


def _slide_roster(envelope_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract slide ids plus perceived authority and demoted expected plans.

    Fail-loud: Pass 2 narrates SLIDES; without Gary's node-07 contribution
    there is nothing real to join. Visual authority, however, comes only from
    the rich vision PerceptionArtifact projection.
    """
    rows = envelope_payload.get("gary_slide_output")
    if not isinstance(rows, list) or not rows:
        raise Pass2GroundingError(
            "Pass 2 requires gary_slide_output (real slide roster) in its "
            "payload; node 08 projections must deliver it",
            tag="irene.pass2.grounding-missing",
        )
    roster: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if not slide_id:
            raise Pass2GroundingError(
                f"gary_slide_output row {index} carries no slide_id",
                tag="irene.pass2.grounding-missing",
            )
        roster.append({"slide_id": slide_id, "visual_description": _expected_visual(row)})
    if not roster:
        raise Pass2GroundingError(
            "gary_slide_output contained no usable slide rows",
            tag="irene.pass2.grounding-missing",
        )
    # P2-3 decoy note: the minimal authoring-envelope
    # app.specialists.irene.authoring.pass_2_template.PerceptionArtifact is
    # not a runtime grounding source. Pass 2 consumes the rich upstream model.
    perception_by_slide = _perception_artifacts_by_slide(envelope_payload)
    brief_by_slide = _slide_briefs_by_slide(envelope_payload)
    for entry in roster:
        slide_id = entry["slide_id"]
        artifact = perception_by_slide.get(slide_id)
        entry["visual_authority"] = _visual_authority_for_slide(
            slide_id, artifact
        )
        perceived_figures = _perceived_figures(artifact)
        entry["perceived_figures"] = sorted(perceived_figures)
        expected_visual_plan = _expected_visual_plan_for_slide(
            entry["visual_description"], brief_by_slide.get(slide_id)
        )
        entry["expected_visual_plan"] = _redact_text_for_unperceived_figures(
            expected_visual_plan, slide_id, perceived_figures
        )
        if (
            artifact is not None
            and artifact.coverage == "perceived"
            and artifact.confidence == "HIGH"
        ):
            entry["reading_path"] = artifact.reading_path
            entry["reading_path_order"] = (
                ordered_element_keys_for_reading_path(artifact)
                if artifact.reading_path
                else []
            )
    return roster


def _expected_visual(row: dict[str, Any]) -> str:
    candidates = [
        row.get("visual_description"),
        row.get("prompt"),
        row.get("title"),
        row.get("slide_purpose"),
    ]
    return " | ".join(str(item).strip() for item in candidates if str(item or "").strip())


def _perception_artifacts_by_slide(
    envelope_payload: dict[str, Any],
) -> dict[str, RichPerceptionArtifact]:
    raw = envelope_payload.get("perception_artifacts")
    if raw is None:
        return {}
    if isinstance(raw, dict):
        if "perception_artifacts" in raw:
            raw = raw["perception_artifacts"]
        elif "slide_id" in raw:
            raw = [raw]
        else:
            raw = list(raw.values())
    if not isinstance(raw, list):
        raise Pass2GroundingError(
            "perception_artifacts must be a list or slide-id map when supplied",
            tag="irene.pass2.perception-invalid",
        )
    try:
        artifacts = [RichPerceptionArtifact.model_validate(item) for item in raw]
    except ValidationError as exc:
        raise Pass2GroundingError(
            f"perception_artifacts failed rich model validation: {exc}",
            tag="irene.pass2.perception-invalid",
        ) from exc
    mapping: dict[str, RichPerceptionArtifact] = {}
    for artifact in artifacts:
        if artifact.slide_id in mapping:
            raise Pass2GroundingError(
                f"duplicate perception artifact for slide {artifact.slide_id}",
                tag="irene.pass2.perception-invalid",
            )
        mapping[artifact.slide_id] = artifact
    return mapping


def _slide_briefs_by_slide(envelope_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = envelope_payload.get("slide_briefs")
    if not isinstance(raw, list):
        return {}
    briefs: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        slide_id = str(item.get("slide_id") or "").strip()
        if slide_id and slide_id not in briefs:
            briefs[slide_id] = item
    return briefs


def _visual_authority_for_slide(
    slide_id: str, artifact: RichPerceptionArtifact | None
) -> str:
    if artifact is None:
        return f"- {slide_id}: {UNVERIFIED_VISUAL_AUTHORITY}"
    if artifact.coverage != "perceived" or artifact.confidence != "HIGH":
        return (
            f"- {slide_id}: {UNVERIFIED_VISUAL_AUTHORITY} "
            f"(coverage={artifact.coverage}; confidence={artifact.confidence})"
        )
    lines = [
        f"- {slide_id}: source=vision.perception_artifacts; "
        f"coverage={artifact.coverage}; confidence={artifact.confidence}"
    ]
    if artifact.slide_title:
        lines.append(f"  - perceived_slide_title: {artifact.slide_title}")
    if artifact.extracted_text:
        lines.append(f"  - perceived_extracted_text: {artifact.extracted_text}")
    if artifact.layout_description:
        lines.append(f"  - perceived_layout: {artifact.layout_description}")
    if artifact.reading_path:
        lines.append(f"  - reading_path: {artifact.reading_path}")
    for block in _stable_json_items(artifact.text_blocks):
        lines.append(f"  - perceived_text_block: {block}")
    for element in _stable_json_items(artifact.visual_elements):
        lines.append(f"  - perceived_visual_element: {element}")
    if artifact.source_png_path:
        lines.append(f"  - perceived_source_png_path: {artifact.source_png_path}")
    return "\n".join(lines)


def _expected_visual_plan_for_slide(
    gary_visual_description: str, slide_brief: dict[str, Any] | None
) -> str:
    parts = []
    if gary_visual_description:
        parts.append(f"gary_visual_description={gary_visual_description}")
    if slide_brief:
        parts.append(f"slide_brief={_json_fragment(slide_brief)}")
    if not parts:
        parts.append("<none supplied>")
    return "; ".join(parts)


def _stable_json_items(items: list[Any]) -> list[str]:
    return sorted(_json_fragment(item) for item in items)


def _json_fragment(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def _perceived_figures(artifact: RichPerceptionArtifact | None) -> set[str]:
    if (
        artifact is None
        or artifact.coverage != "perceived"
        or artifact.confidence != "HIGH"
    ):
        return set()
    values: list[str] = [
        artifact.extracted_text,
        artifact.layout_description,
        artifact.slide_title,
    ]
    values.extend(_json_fragment(item) for item in artifact.text_blocks)
    values.extend(_json_fragment(item) for item in artifact.visual_elements)
    return _figures(" ".join(value for value in values if value))


def _reading_path_guidance(slide_roster: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for entry in slide_roster:
        pattern = entry.get("reading_path")
        order = entry.get("reading_path_order") or []
        if not pattern:
            continue
        tokens = ", ".join(cadence_tokens_for_pattern(str(pattern)))
        order_text = " -> ".join(str(item) for item in order) if order else "<unavailable>"
        lines.append(
            f"- {entry['slide_id']}: reading_path={pattern}; "
            f"scan_order={order_text}; cadence_tokens={tokens}"
        )
    return "\n".join(lines) if lines else "- <none supplied>"


def _payload_section_for_prompt(
    envelope_payload: dict[str, Any], slide_roster: list[dict[str, Any]]
) -> str:
    unverified = {
        entry["slide_id"]
        for entry in slide_roster
        if UNVERIFIED_VISUAL_AUTHORITY in str(entry.get("visual_authority") or "")
    }
    perceived_figures_by_slide = {
        entry["slide_id"]: set(entry.get("perceived_figures") or [])
        for entry in slide_roster
    }
    payload = _redact_payload_visual_leaks(
        envelope_payload,
        unverified_slide_ids=unverified,
        perceived_figures_by_slide=perceived_figures_by_slide,
    )
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )


def _redact_payload_visual_leaks(
    envelope_payload: dict[str, Any],
    *,
    unverified_slide_ids: set[str],
    perceived_figures_by_slide: dict[str, set[str]],
) -> dict[str, Any]:
    redacted = _redact_unverified_payload(envelope_payload, unverified_slide_ids)
    for key in ("gary_slide_output", "slide_briefs"):
        rows = redacted.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            slide_id = str(row.get("slide_id") or "").strip()
            if not slide_id or slide_id in unverified_slide_ids:
                continue
            allowed = perceived_figures_by_slide.get(slide_id, set())
            _redact_row_for_unperceived_figures(row, slide_id, allowed)
    return redacted


def _redact_unverified_payload(
    envelope_payload: dict[str, Any], unverified_slide_ids: set[str]
) -> dict[str, Any]:
    redacted = deepcopy(envelope_payload)
    for key in ("gary_slide_output", "slide_briefs"):
        rows = redacted.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            slide_id = str(row.get("slide_id") or "").strip()
            if slide_id in unverified_slide_ids:
                _redact_slide_row(row, slide_id)
    return redacted


def _redact_slide_row(row: dict[str, Any], slide_id: str) -> None:
    keep = {
        "slide_id",
        "id",
        "card_number",
        "file_path",
        "png_path",
        "artifact_path",
        "source_ref",
    }
    token = f"[REDACTED: no perceived authority for {slide_id}]"
    for key, value in list(row.items()):
        if key in keep:
            continue
        if isinstance(value, str):
            row[key] = token
        elif isinstance(value, dict):
            row[key] = {inner_key: token for inner_key in value}
        elif isinstance(value, list):
            row[key] = [token for _ in value]


def _redact_row_for_unperceived_figures(
    row: dict[str, Any], slide_id: str, allowed_figures: set[str]
) -> None:
    for key, value in list(row.items()):
        if key == "slide_id":
            continue
        row[key] = _redact_value_for_unperceived_figures(value, slide_id, allowed_figures)


def _redact_value_for_unperceived_figures(
    value: Any, slide_id: str, allowed_figures: set[str]
) -> Any:
    if isinstance(value, str):
        return _redact_text_for_unperceived_figures(value, slide_id, allowed_figures)
    if isinstance(value, dict):
        return {
            inner_key: _redact_value_for_unperceived_figures(
                inner_value, slide_id, allowed_figures
            )
            for inner_key, inner_value in value.items()
        }
    if isinstance(value, list):
        return [
            _redact_value_for_unperceived_figures(item, slide_id, allowed_figures)
            for item in value
        ]
    return value


def _redact_text_for_unperceived_figures(
    value: str, slide_id: str, allowed_figures: set[str]
) -> str:
    token = f"[REDACTED: figure absent from perceived authority for {slide_id}]"
    return _FIGURE_RE.sub(
        lambda match: (
            match.group(0)
            if _normalize_figure(match.group(0)) in allowed_figures
            else token
        ),
        value,
    )


def backfill_delta_ids(parsed: dict[str, Any]) -> dict[str, Any]:
    """Story 1.2a: ensure every segment_manifest_delta carries an ``id`` the
    party-governed join can key on, at the Pass-2 output boundary.

    The shared join (`app/specialists/narration_join.py`, the single home of join
    POLICY) matches narration_script <-> deltas by ``id`` ONLY. On a clustered deck
    (live trial 52890be7) Pass-2 emitted the delta id under ``segment_id`` (which the
    sibling ``_segment_slide_id_from_deltas`` already accepts) but NOT ``id`` — so the
    id-keyed join dropped every one of the 13 segments and enrique's pre-spend guard
    refused. Two repairs, both at the source so join policy + G5 stay untouched:

    1. **segment_id -> id alias** (the real, confirmed 52890be7 bug): when a delta has
       a usable ``segment_id`` but no ``id``, copy it. Always safe — same value,
       canonical key; no positional assumption. Per-delta (partial arrays are fine).
    2. **positional backfill** (defensive fallback, unobserved-but-possible): if after
       step 1 the deltas STILL all lack an id AND len(deltas)==len(narr), assign ids
       from the parallel narration_script by index. Gated to the all-None + equal-length
       case ONLY — a *partially* id'd array signals out-of-order emission where positional
       pairing would mis-attribute (Winston green-light A1).

    PURE (no input mutation), idempotent. LOAD-BEARING INVARIANT for step 2: Pass-2 emits
    narration_script and deltas positionally aligned from one authoring pass; do not relax
    the all-None / equal-length gates.
    """
    narr = parsed.get("narration_script")
    deltas = parsed.get("segment_manifest_deltas")
    if not isinstance(narr, list) or not isinstance(deltas, list) or not deltas:
        return parsed

    def _usable(value: object) -> str:
        return str(value).strip() if value is not None else ""

    changed = False
    work: list[Any] = []
    # Step 1: per-delta segment_id -> id alias (always safe).
    for delta in deltas:
        if not isinstance(delta, dict):
            work.append({})
            changed = True
            continue
        copy = dict(delta)
        if not _usable(copy.get("id")) and _usable(copy.get("segment_id")):
            copy["id"] = copy["segment_id"]
            changed = True
        work.append(copy)

    # Step 2: defensive positional backfill ONLY if still all id-less + len matches.
    def _has_id(d: object) -> bool:
        return isinstance(d, dict) and d.get("id") is not None

    if len(work) == len(narr) and not any(_has_id(d) for d in work):
        positional: list[Any] = []
        for nseg, delta in zip(narr, work, strict=False):
            copy = dict(delta) if isinstance(delta, dict) else {}
            nid = _usable(nseg.get("id")) if isinstance(nseg, dict) else ""
            if nid:
                copy["id"] = nid
                changed = True
            positional.append(copy)
        work = positional

    if not changed:
        return parsed
    return {**parsed, "segment_manifest_deltas": work}


def _first_perception_source(delta: object) -> str:
    """The first non-empty visual_reference perception_source on a delta, or ''."""
    if not isinstance(delta, dict):
        return ""
    for ref in delta.get("visual_references") or []:
        if isinstance(ref, dict):
            source = str(ref.get("perception_source") or "").strip()
            if source:
                return source
    return ""


def backfill_delta_perception_sources(
    parsed: dict[str, Any], roster: list[dict[str, Any]]
) -> dict[str, Any]:
    """Backfill a delta's MISSING ``perception_source`` from the slide roster.

    Live trial 72ed8fd5 (non-clustered) error-paused at the enrique audio leg:
    Pass-2 emitted 13 narration segments + 13 deltas with matching ids, but one
    cluster-head delta (``seg-10``) carried an EMPTY ``visual_references`` list.
    The shared join drops a delta with no perception_source, so its narration
    segment is "dropped" and enrique's pre-spend guard refuses
    (``elevenlabs.join.dropped-segments``). This is a DISTINCT failure mode from
    :func:`backfill_delta_ids` (which repairs a missing ``id``, not a missing
    ``perception_source``).

    Repair at the Pass-2 output boundary (join policy + G5 stay untouched),
    mirroring backfill_delta_ids' discipline:

    - **Roster-grounded, not invented.** The backfilled slide id comes from the
      authoritative ``roster`` (the same one ``_assert_narration_joins_roster``
      validates against) by positional index — never a guess.
    - **Alignment-gated.** Only backfill when ``len(deltas) == len(roster)`` AND
      every delta that ALREADY has a perception_source matches its
      positionally-aligned roster slide_id (confirming the deltas are emitted in
      roster order). A single misalignment ⇒ skip entirely (positional inference
      would mis-attribute — same caution as backfill_delta_ids step-2).

    PURE (no input mutation), idempotent.
    """
    deltas = parsed.get("segment_manifest_deltas")
    if not isinstance(deltas, list) or not deltas:
        return parsed
    if not isinstance(roster, list) or len(roster) != len(deltas):
        return parsed
    roster_ids = [str(entry.get("slide_id") or "").strip() for entry in roster]
    if not all(roster_ids):
        return parsed

    present = [(i, _first_perception_source(d)) for i, d in enumerate(deltas)]
    aligned = all(src == roster_ids[i] for i, src in present if src)
    has_gap = any(not src for _, src in present)
    if not aligned or not has_gap:
        return parsed

    work: list[Any] = []
    changed = False
    for i, delta in enumerate(deltas):
        if not isinstance(delta, dict) or _first_perception_source(delta):
            work.append(delta)
            continue
        copy = dict(delta)
        copy["visual_references"] = [
            *(copy.get("visual_references") or []),
            {"perception_source": roster_ids[i]},
        ]
        work.append(copy)
        changed = True
    if not changed:
        return parsed
    return {**parsed, "segment_manifest_deltas": work}


def _assert_narration_joins_roster(
    parsed: dict[str, Any], roster: list[dict[str, Any]]
) -> None:
    """Winston post-check: narration must reference REAL slide ids only.

    Converts residual confabulation (exemplar bleed despite grounding) from
    silent to fail-loud. Every non-empty ``perception_source`` in the
    segment_manifest_deltas' visual_references must name a roster slide id,
    and at least one real slide must be referenced.
    """
    slide_ids = {entry["slide_id"] for entry in roster}
    referenced: set[str] = set()
    for delta in parsed.get("segment_manifest_deltas") or []:
        if not isinstance(delta, dict):
            continue
        for ref in delta.get("visual_references") or []:
            if isinstance(ref, dict):
                source = str(ref.get("perception_source") or "").strip()
                if source:
                    referenced.add(source)
    if not parsed.get("narration_script"):
        return
    orphans = sorted(referenced - slide_ids)
    if orphans or not referenced:
        raise Pass2GroundingError(
            "Pass-2 narration does not join the real slide roster "
            f"(orphan perception_source values: {orphans}; "
            f"roster: {sorted(slide_ids)})",
            tag="irene.pass2.slide-join-failed",
        )


def _assert_join_id_integrity(parsed: dict[str, Any]) -> None:
    """Id-integrity gate at the Pass-2 output boundary (defect fix,
    irene-pass2-slidejoin-id-integrity-gate.md).

    The gap this closes: `_assert_narration_joins_roster` validates
    perception_source→roster grounding but NEVER the id-join. The shared join
    (`narration_join.join_narration_segments`) keys narration text by segment
    ``id`` and rows by delta ``id``; an id-less or non-bijective emission (the
    frozen `40f3a90a` shape) collapses every segment into a single join bucket
    (last-write-wins) → distinct slide_id + IDENTICAL narration on every row, a
    silent degenerate storyboard the roster gate passes clean.

    Raise the already-retryable ``irene.pass2.slide-join-failed`` tag (in
    `_RETRYABLE_DISPATCH_TAGS`) so the runner's auto-retry re-rolls Pass-2
    (id-bearing) and self-heals. Enforcement stays HERE at the boundary — the
    frozen import-identity-pinned shared join (`narration_join.py`) is untouched.

    Two fail conditions, checked in order, each with a DISTINCT detail:
      (a) *id-less after backfill* — any narration_script segment OR delta still
          lacks a usable ``id`` (empty/None) after the boundary backfills; the
          id-keyed join would collapse/drop it.
      (b) *id-join non-bijective* — narration segment ids are not 1:1:
          ``len({usable ids}) < len(narration_script)`` (positional id
          cardinality — NEVER keyed on ``narration_text``; identical prose under
          DISTINCT ids is legitimate and MUST pass). This is the ``text_by_id``
          overwrite collapse vector.

    Pure, no mutation. Mirrors `_assert_narration_joins_roster`: silent when
    there is no narration_script (nothing to join).
    """
    narr = parsed.get("narration_script")
    if not isinstance(narr, list) or not narr:
        return

    def _usable(value: object) -> str:
        return str(value).strip() if value is not None else ""

    # (a) id-absence — every narration segment AND every delta must key.
    for seg in narr:
        if not isinstance(seg, dict) or not _usable(seg.get("id")):
            raise Pass2GroundingError(
                "Pass-2 narration_script segment lacks a usable join id "
                "(id-less after backfill) — the id-keyed shared join would "
                "collapse every segment into one bucket, flooding the "
                "storyboard with a single narration",
                tag="irene.pass2.slide-join-failed",
            )
    deltas = parsed.get("segment_manifest_deltas")
    for delta in deltas if isinstance(deltas, list) else []:
        if not isinstance(delta, dict) or not _usable(delta.get("id")):
            raise Pass2GroundingError(
                "Pass-2 segment_manifest_delta lacks a usable join id "
                "(id-less after backfill) — the id-keyed shared join would "
                "drop its narration segment",
                tag="irene.pass2.slide-join-failed",
            )

    # (b) non-bijective id-join — positional id cardinality; NEVER text-keyed.
    usable_ids = {_usable(seg.get("id")) for seg in narr}
    if len(usable_ids) < len(narr):
        raise Pass2GroundingError(
            "Pass-2 narration_script ids are not bijective "
            "(id-join non-bijective) — distinct segments share a join key, so "
            "the shared join's text_by_id overwrite collapses them into one "
            "narration",
            tag="irene.pass2.slide-join-failed",
        )

    # (c) delta ids must ALSO be bijective — the shared join builds one ROW per
    #     delta and keys each row's narration_text by the DELTA id. Duplicate
    #     non-empty delta ids (distinct perception_sources) flood every distinct
    #     slide with a single narration — the 40f3a90a collapse reached via
    #     duplicated delta ids, not empty ids. phantom_segment_ids misses it
    #     (the flooded text is non-empty). Positional id cardinality; NEVER text-
    #     keyed. (delta-ids ⊆ narration-ids is a DISTINCT concern deferred to
    #     join-narration-segments-silent-collapse-hardening — not checked here.)
    delta_list = deltas if isinstance(deltas, list) else []
    delta_ids = [_usable(d.get("id")) for d in delta_list if isinstance(d, dict)]
    if len(set(delta_ids)) < len(delta_ids):
        raise Pass2GroundingError(
            "Pass-2 segment_manifest_delta ids are not bijective "
            "(delta id-join non-bijective) — distinct deltas share a join key, "
            "so the shared join floods every slide with one narration",
            tag="irene.pass2.slide-join-failed",
        )


def _assert_figure_citations_within_perceived(
    parsed: dict[str, Any], roster: list[dict[str, Any]]
) -> None:
    perceived_by_slide = {
        entry["slide_id"]: set(entry.get("perceived_figures") or []) for entry in roster
    }
    for segment in parsed.get("narration_script") or []:
        if not isinstance(segment, dict):
            continue
        slide_id = str(segment.get("slide_id") or segment.get("perception_source") or "")
        if not slide_id:
            slide_id = _segment_slide_id_from_deltas(segment, parsed)
        if not slide_id:
            continue
        text = str(segment.get("text") or segment.get("narration_text") or "").strip()
        if not text:
            continue
        figures = _figures(text)
        offending = sorted(figures - perceived_by_slide.get(slide_id, set()))
        if offending:
            raise Pass2GroundingError(
                f"scope=narration; slide {slide_id} narration figures not present in perceived "
                f"authority: {offending}",
                tag="irene.pass2.figure-contradiction",
            )


def _assert_narration_figures_sourced(
    parsed: dict[str, Any],
    roster: list[dict[str, Any]],
    *,
    source_text: str,
) -> None:
    """Leg-4 SOURCE-direction narration figure gate (flag-gated; ADDITIVE).

    ``_assert_figure_citations_within_perceived`` enforces the DECK-direction
    invariant (narration ⊆ deck). This gate enforces the orthogonal
    SOURCE-direction invariant and stays additive — both must hold when the flag
    is ON; the deck-direction gate is untouched.

    Root cause it closes: Pass-2 grounds on the DECK as sole visual authority, so
    when Gamma confabulates a chart numeral Irene faithfully narrates the invented
    value over source truth. The one in-graph figure gate only checks
    narration ⊆ deck, so a deck-invented figure PASSES today.

    Two fail-loud conditions (flag ON):
      * ``irene.pass2.figure-unsourced`` — a narrated digit-form figure is absent
        from the SOURCE corpus (unsourced / confabulated introduction).
      * ``irene.pass2.figure-source-deck-conflict`` — 🔒 BINDING VO-PROTECTION:
        the deck rendered a value that CONTRADICTS a same-kind source numeral
        (source 67%, deck 60%, narration 60%). Fail loud as an upstream
        deck-confabulation defect and route the repair to Gamma. The gate MUST
        NOT rewrite/reorder narration (that would itself risk the protected
        VO↔on-screen invariant) — it only BLOCKS; VO is never desynced from
        on-screen.

    Declared scope: digit-form ``$N`` / ``N%`` / ``Nx`` only (the frozen
    ``_FIGURE_RE`` neck, same extractor the WARN-only source_fidelity_audit uses).
    Word-form + bare-integer figures are explicitly OUT — do NOT widen
    ``_FIGURE_RE`` (frozen-neck governance).
    """
    if not narration_figure_fidelity_active():
        return
    source_figures = _figures(source_text)
    source_kinds = {_figure_kind(fig) for fig in source_figures}
    perceived_by_slide = {
        entry["slide_id"]: set(entry.get("perceived_figures") or []) for entry in roster
    }
    for segment in parsed.get("narration_script") or []:
        if not isinstance(segment, dict):
            continue
        slide_id = str(segment.get("slide_id") or segment.get("perception_source") or "")
        if not slide_id:
            slide_id = _segment_slide_id_from_deltas(segment, parsed)
        text = str(segment.get("text") or segment.get("narration_text") or "").strip()
        if not text:
            continue
        # Edge-2: the SOURCE-provenance check (figure in source_figures) is GLOBAL
        # and needs NO slide_id — it must run for EVERY narrated segment, keyed or
        # not, so a confabulated digit-form figure in an unkeyed segment can never
        # escape the source gate. Only the deck-CONFLICT sub-check needs the
        # per-slide key; when the segment is unkeyed/unresolvable we DEGRADE that
        # classification (perceived unavailable -> empty set) and the figure falls
        # through to the plain figure-unsourced raise.
        perceived = perceived_by_slide.get(slide_id, set()) if slide_id else set()
        slide_label = slide_id or "<unkeyed>"
        for figure in sorted(_figures(text)):
            # T4a precision: exact OR percent-tolerance near-match counts as sourced
            # (source 18.4% → narration 18% must not false-halt).
            if _figure_near_match(figure, source_figures):
                continue  # sourced — clean
            # Source-vs-deck CONFLICT: the deck rendered this figure AND the source
            # carries a same-KIND numeral it contradicts (e.g. source 67%, deck
            # 60%). Fail loud as an upstream Gamma deck-confabulation defect; never
            # silently narrate either value (VO↔on-screen protection). Requires a
            # resolvable slide_id (perceived authority); unkeyed segments degrade to
            # figure-unsourced below.
            if figure in perceived and _figure_kind(figure) in source_kinds:
                raise Pass2GroundingError(
                    f"scope=narration; slide {slide_label} narration figure {figure} "
                    "conflicts with the SOURCE (deck-rendered value contradicts a "
                    "same-kind source numeral) — route the repair to Gamma; do NOT "
                    "desync VO from on-screen",
                    tag="irene.pass2.figure-source-deck-conflict",
                )
            # Unsourced/confabulated introduction: a narrated figure with no source
            # provenance at all (whether or not the deck also invented it).
            raise Pass2GroundingError(
                f"scope=narration; slide {slide_label} narration figure {figure} is "
                "not present in the SOURCE corpus (unsourced/confabulated "
                "introduction)",
                tag="irene.pass2.figure-unsourced",
            )


def _assert_source_figures_positively_carried(
    parsed: dict[str, Any],
    roster: list[dict[str, Any]],
    *,
    source_text: str,
) -> None:
    """Mine-next T4b: source∩deck figures must appear in narration (flag-gated).

    Closes the positive-carry half of ``leg4-narration-figure-fidelity-enforcement``
    without violating VO↔on-screen: only figures that are BOTH in the SOURCE and
    on the perceived deck are required. Conflicting deck confabulations remain
    the job of :func:`_assert_narration_figures_sourced` (block, never rewrite).

    Vacuous when the flag is OFF, when source has no digit-form figures, or when
    no source∩deck consistent set exists.
    """
    if not narration_figure_fidelity_active():
        return
    source_figures = _figures(source_text)
    if not source_figures:
        return
    required: set[str] = set()
    for entry in roster:
        for fig in entry.get("perceived_figures") or []:
            fig_s = str(fig)
            if _figure_near_match(fig_s, source_figures):
                required.add(fig_s)
    if not required:
        return
    narrated: set[str] = set()
    for segment in parsed.get("narration_script") or []:
        if not isinstance(segment, dict):
            continue
        text = str(segment.get("text") or segment.get("narration_text") or "").strip()
        if text:
            narrated |= _figures(text)
    missing = sorted(
        fig for fig in required if not _figure_near_match(fig, narrated)
    )
    if missing:
        raise Pass2GroundingError(
            f"scope=narration; source∩deck figure(s) {missing} absent from "
            "narration (positive-carry miss) — regenerate Pass-2 so source "
            "figures that appear on-screen are spoken",
            tag="irene.pass2.figure-positive-carry-miss",
        )


def _segment_slide_id_from_deltas(segment: dict[str, Any], parsed: dict[str, Any]) -> str:
    segment_id = str(segment.get("id") or segment.get("segment_id") or "").strip()
    if not segment_id:
        return ""
    for delta in parsed.get("segment_manifest_deltas") or []:
        if not isinstance(delta, dict):
            continue
        delta_id = str(delta.get("id") or delta.get("segment_id") or "").strip()
        if delta_id != segment_id:
            continue
        for ref in delta.get("visual_references") or []:
            if not isinstance(ref, dict):
                continue
            slide_id = str(ref.get("perception_source") or "").strip()
            if slide_id:
                return slide_id
    return ""


def _assert_reading_path_conformance(
    parsed: dict[str, Any], roster: list[dict[str, Any]]
) -> None:
    """Record, but do not hard-block on, classified scan-order drift."""
    by_slide = {entry["slide_id"]: entry for entry in roster}
    last_seen_by_slide: dict[str, int] = {}
    warnings: list[dict[str, Any]] = []
    for delta in parsed.get("segment_manifest_deltas") or []:
        if not isinstance(delta, dict):
            continue
        for ref in delta.get("visual_references") or []:
            if not isinstance(ref, dict):
                continue
            slide_id = str(ref.get("perception_source") or "").strip()
            if not slide_id or slide_id not in by_slide:
                continue
            entry = by_slide[slide_id]
            pattern = entry.get("reading_path")
            order = entry.get("reading_path_order") or []
            if not pattern or not order:
                warnings.append(
                    {
                        "tag": "irene.pass2.reading-path-missing",
                        "slide_id": slide_id,
                        "message": f"slide {slide_id} is referenced but missing reading_path",
                    }
                )
                continue
            element_key = _visual_reference_key(ref)
            if not element_key:
                continue
            index_by_key = {_norm_key(key): index for index, key in enumerate(order)}
            normalized = _norm_key(element_key)
            if normalized not in index_by_key:
                continue
            current = index_by_key[normalized]
            previous = last_seen_by_slide.get(slide_id, -1)
            if current < previous:
                warnings.append(
                    {
                        "tag": "irene.pass2.reading-path-order-failed",
                        "slide_id": slide_id,
                        "reading_path": pattern,
                        "element_key": element_key,
                        "previous_scan_index": previous,
                        "message": (
                            "Pass-2 narration visual reference order violates "
                            f"{pattern} for {slide_id}: {element_key!r} appears after "
                            f"scan index {previous}"
                        ),
                    }
                )
                continue
            last_seen_by_slide[slide_id] = current
    if warnings:
        parsed["reading_path_conformance_warnings"] = warnings


def assert_callback_reading_path(
    parsed: dict[str, Any], roster: list[dict[str, Any]]
) -> None:
    """07G read-path teeth for a FIRED warm_callback line (close-bar #4).

    Runs the SAME monotonic scan-order logic as
    :func:`_assert_reading_path_conformance` (which is RECORD-ONLY for normal
    narration) on the callback-bearing host segment, then RAISES
    :class:`Pass2ReadingPathError` ONLY on a real scan-order BREACH
    (``irene.pass2.reading-path-order-failed``) — i.e. the host segment's
    on-screen references appear out of the perceived display order. This proves
    the callback-bearing segment still conforms to the read path; it does NOT
    raise on ``reading-path-missing`` (a low-confidence / un-perceived slide that
    carries no reading_path is NOT a VO↔on-screen breach — the caller drops the
    callback silently rather than aborting the whole run). The record-only
    behaviour of ``_assert_reading_path_conformance`` for ordinary narration is
    unchanged, as is its pre-existing record-only treatment of missing patterns.
    """
    _assert_reading_path_conformance(parsed=parsed, roster=roster)
    warnings = parsed.get("reading_path_conformance_warnings") or []
    order_failed = [
        w for w in warnings
        if str(w.get("tag")) == "irene.pass2.reading-path-order-failed"
    ]
    if order_failed:
        raise Pass2ReadingPathError(
            "Fired warm_callback violates the perceived reading path "
            f"(07G read-path teeth): {order_failed}",
            tag="irene.pass2.reading-path-order-failed",
        )


_RHETORICAL_ROLE_VALUES: frozenset[str] = frozenset(get_args(RhetoricalRole))


def assert_pass2_surfaces_validatable(parsed: dict[str, Any]) -> None:
    """AC1 (finding-d): the emitted Pass-2 package is DIRECTLY validatable.

    A focused, additive assertion that the reading-path / cue / timing-role
    surfaces — ``SegmentManifestSegment.{timing_role, bridge_type,
    visual_references}``, ``VisualReference.{narration_cue, perception_source}``,
    and ``VoiceDirection.rhetorical_role`` — conform WHEN PRESENT, so handoff-
    validation + the 07G gate bind a firm in-band target instead of the out-of-
    band concierge normalization step (``concierge-production-2026-06-30/
    pass2-validation-package/normalization-receipt.json``). It is TOLERANT of the
    minimal delta shape (absent fields are not required here — full package-
    contract formalization is Leg-4), so it never breaks the existing manifest
    shape; it only fails LOUD on a malformed surface that IS emitted.
    """
    for delta in parsed.get("segment_manifest_deltas") or []:
        if not isinstance(delta, dict):
            continue
        for field in ("timing_role", "bridge_type"):
            value = delta.get(field)
            if value is not None and not (isinstance(value, str) and value.strip()):
                raise Pass2GroundingError(
                    f"Pass-2 package surface {field!r} is present but not a "
                    f"non-empty string: {value!r}",
                    tag="irene.pass2.surface-invalid",
                )
        refs = delta.get("visual_references")
        if refs is not None:
            for ref in refs if isinstance(refs, list) else []:
                if not isinstance(ref, dict):
                    continue
                for ref_field in ("narration_cue", "perception_source"):
                    value = ref.get(ref_field)
                    if value is not None and not (
                        isinstance(value, str) and value.strip()
                    ):
                        raise Pass2GroundingError(
                            f"Pass-2 visual_reference surface {ref_field!r} is "
                            f"present but not a non-empty string: {value!r}",
                            tag="irene.pass2.surface-invalid",
                        )
        direction = delta.get("voice_direction")
        if isinstance(direction, dict):
            role = direction.get("rhetorical_role")
            if role is not None and role not in _RHETORICAL_ROLE_VALUES:
                raise Pass2GroundingError(
                    f"Pass-2 voice_direction.rhetorical_role {role!r} is not a "
                    f"member of the RhetoricalRole taxonomy {sorted(_RHETORICAL_ROLE_VALUES)}",
                    tag="irene.pass2.surface-invalid",
                )


def _warm_callback_delta_for_segment(
    segment: dict[str, Any], parsed: dict[str, Any]
) -> dict[str, Any] | None:
    """Resolve the segment_manifest delta that carries a narration segment.

    Matches by ``id`` first (the figure-gate join key), then by a UNIQUE
    ``slide_id``. Returns ``None`` when no unambiguous delta exists (caller then
    skips the segment — fail-safe SILENT).
    """
    seg_id = str(segment.get("id") or segment.get("segment_id") or "").strip()
    deltas = [d for d in (parsed.get("segment_manifest_deltas") or []) if isinstance(d, dict)]
    if seg_id:
        for delta in deltas:
            if str(delta.get("id") or delta.get("segment_id") or "").strip() == seg_id:
                return delta
    seg_slide = str(segment.get("slide_id") or "").strip()
    if seg_slide:
        matches = [d for d in deltas if str(d.get("slide_id") or "").strip() == seg_slide]
        if len(matches) == 1:
            return matches[0]
    return None


def _gate_canonical_field(segment: dict[str, Any]) -> str | None:
    """The narration field the FIGURE GATE actually reads (``text`` THEN
    ``narration_text``, mirroring ``_assert_figure_citations_within_perceived``).

    Returns the name of the first gate-read field that carries non-empty prose, or
    ``None`` when neither is present (the gate skips an empty segment). Sharing this
    resolver between injection and the gate closes M2a: a callback can NEVER be
    written to a field the gate does not read while still reaching TTS via the
    narration join.
    """
    for field in ("text", "narration_text"):
        value = segment.get(field)
        if isinstance(value, str) and value.strip():
            return field
    return None


def _inject_warm_callback_into_canonical(segment: dict[str, Any], callback_text: str) -> None:
    """Prepend the kept callback to the EXACT field the figure gate reads.

    Writes the SAME field as :func:`_gate_canonical_field` (``text`` first, then
    ``narration_text``) so the authored callback ALSO flows
    ``_assert_figure_citations_within_perceived``. The callback leads (a
    re-orienting bridge) the existing narration. When neither gate-read field is
    present yet, seed ``narration_text`` (gate-visible as the ``text``-or-
    ``narration_text`` fallback, and the canonical downstream field).
    """
    field = _gate_canonical_field(segment)
    if field is not None:
        segment[field] = f"{callback_text} {str(segment[field]).strip()}".strip()
        return
    segment["narration_text"] = callback_text


def _set_warm_callback_role(delta: dict[str, Any]) -> None:
    """Stamp ``voice_direction.rhetorical_role = 'warm_callback'`` on the delta."""
    direction = delta.get("voice_direction")
    if not isinstance(direction, dict):
        direction = {}
    direction["rhetorical_role"] = "warm_callback"
    delta["voice_direction"] = direction


def _warm_callback_role_keys(parsed: dict[str, Any]) -> list[tuple[str, str]]:
    """Snapshot (id, slide_id) of every delta currently bearing the warm_callback
    role, so the role can be RE-STAMPED after ``_attach_voice_direction`` rebuilds
    ``voice_direction`` from scratch (M3 — both-flags precedence)."""
    keys: list[tuple[str, str]] = []
    for delta in parsed.get("segment_manifest_deltas") or []:
        if not isinstance(delta, dict):
            continue
        direction = delta.get("voice_direction")
        if isinstance(direction, dict) and direction.get("rhetorical_role") == "warm_callback":
            keys.append(
                (
                    str(delta.get("id") or delta.get("segment_id") or "").strip(),
                    str(delta.get("slide_id") or "").strip(),
                )
            )
    return keys


def _restamp_warm_callback_roles(
    parsed: dict[str, Any], keys: list[tuple[str, str]]
) -> None:
    """Re-apply ``rhetorical_role='warm_callback'`` to the deltas in ``keys`` after
    the voice-direction annotation pass rebuilt their ``voice_direction`` (which
    drops the role). Matches by ``id`` first, then a UNIQUE ``slide_id`` (M3)."""
    if not keys:
        return
    deltas = [d for d in (parsed.get("segment_manifest_deltas") or []) if isinstance(d, dict)]
    for did, dslide in keys:
        target: dict[str, Any] | None = None
        if did:
            for delta in deltas:
                if str(delta.get("id") or delta.get("segment_id") or "").strip() == did:
                    target = delta
                    break
        if target is None and dslide:
            matches = [d for d in deltas if str(d.get("slide_id") or "").strip() == dslide]
            if len(matches) == 1:
                target = matches[0]
        if target is not None:
            _set_warm_callback_role(target)


def _attach_warm_callbacks(
    parsed: dict[str, Any],
    envelope_payload: dict[str, Any],
    roster: list[dict[str, Any]],
    *,
    model_invoke: Any,
) -> dict[str, Any]:
    """Author + R7-gate warm_callback narration in Pass-2 (Slice-2 attach-point).

    Runs between ``backfill_delta_perception_sources`` and the join/reading-path/
    figure asserts, so a KEPT callback's canonical prose flows ALL three gates.
    Gated by ``warm_callback_authoring_active()`` (default OFF ⇒ ``parsed``
    returned UNCHANGED ⇒ byte-identical baseline). Per eligible segment:

      (a) ``select_grounded_callback_anchors`` → empty ⇒ NO callback (silent);
      (b) ``render_warm_callback`` via the injected ``model_invoke`` (real gpt-5
          by default; a deterministic fake in unit tests);
      (c) ``gate_warm_callback`` against the FULL strictly-prior teachable corpus
          (AC7). ``kept=False`` ⇒ DROP the callback (silent) + a loud audit
          record; STRIP is forbidden;
      (d) on KEEP: inject into CANONICAL narration, stamp
          ``rhetorical_role='warm_callback'`` on the delta, and run
          ``assert_callback_reading_path`` (07G teeth) on the fired line.

    Eligibility: a narration segment carrying a ``component_id`` resolvable in the
    ``warm_callback_grounding.components`` corpus; everything else is skipped
    (fail-safe SILENT). The audit list lands under ``parsed['warm_callback_audit']``.
    """
    if not warm_callback_authoring_active():
        return parsed
    grounding = envelope_payload.get("warm_callback_grounding")
    if not isinstance(grounding, dict):
        return parsed
    components = grounding.get("components")
    if not isinstance(components, list) or not components:
        return parsed
    audit_records: list[dict[str, Any]] = []
    # M1 exception containment: the P3 pre-flight raises (e.g. a component missing
    # doc_ordinal) on malformed grounding. An ADDITIVE feature must NEVER crash a
    # green Pass-2 — skip ALL callbacks (silent) + a loud audit record, then return.
    try:
        annotations = build_pedagogy_annotations(components, [])
    except Exception as exc:  # noqa: BLE001 — contain infra error, never crash Pass-2
        parsed["warm_callback_audit"] = [
            {
                "decision": "skipped",
                "scope": "pedagogy_annotations",
                "reason": f"pedagogy-annotation-error: {exc}",
            }
        ]
        return parsed
    source_text_by_id = {
        str(c.get("component_id")): str(c.get("source_text") or "")
        for c in components
        if isinstance(c, dict) and c.get("component_id")
    }
    # M2b: the SAME perceived-figure authority the figure gate consumes, keyed by
    # slide_id, so a callback figure absent from the CURRENT slide is blocked by
    # OMISSION here instead of aborting the whole run at the global figure gate.
    perceived_by_slide = {
        entry["slide_id"]: set(entry.get("perceived_figures") or []) for entry in roster
    }
    for segment in parsed.get("narration_script") or []:
        if not isinstance(segment, dict):
            continue
        target_cid = str(segment.get("component_id") or "").strip()
        if not target_cid or target_cid not in source_text_by_id:
            continue
        anchors = select_grounded_callback_anchors(target_cid, components, annotations)
        # S2: drop blank-source_text anchors (a vacuous denominator would let any
        # wording through R7 and produce a content-free callback).
        anchors = tuple(a for a in anchors if source_text_by_id.get(a, "").strip())
        if not anchors:
            # AC4 fail-safe SILENT: no grounded strictly-prior teachable anchor.
            continue
        # AC7: render off the primary anchor; gate against the FULL strictly-prior
        # teachable corpus (the source-containment denominator).
        anchor_text = source_text_by_id.get(anchors[0], "")
        corpus = "\n".join(source_text_by_id.get(a, "") for a in anchors).strip()
        # M1: contain a renderer (gpt-5) fault — skip THIS callback + audit, never
        # crash. The downstream gates (R7, figure, read-path) still propagate.
        try:
            callback_text = render_warm_callback(
                anchor_text=anchor_text,
                segment_context=str(
                    segment.get("text") or segment.get("narration_text") or ""
                ),
                model_invoke=model_invoke,
            )
        except Exception as exc:  # noqa: BLE001 — contain renderer error, skip + audit
            audit_records.append(
                {
                    "decision": "skipped",
                    "target_component_id": target_cid,
                    "anchor_component_ids": list(anchors),
                    "reason": f"renderer-error: {exc}",
                }
            )
            continue
        if not callback_text:
            # AC4: renderer produced nothing usable ⇒ no callback (silent).
            continue
        # S3: a v3 audio tag in canonical narration breaks the PROTECTED tag-free
        # invariant — DROP (block-by-omission) before it can be injected.
        leaked_tags = extract_tags(callback_text)
        if leaked_tags:
            audit_records.append(
                {
                    "decision": "dropped",
                    "target_component_id": target_cid,
                    "anchor_component_ids": list(anchors),
                    "callback_text": callback_text,
                    "reason": f"v3-tag-leak: {leaked_tags}",
                }
            )
            continue
        gate = gate_warm_callback(callback_text, source_text=corpus)
        if not gate.kept:
            # AC5 block-by-omission: DROP the whole callback (never strip) + a
            # loud audit record. The dropped text never enters canonical, so it
            # can never reach the Enrique compiler.
            audit_records.append(
                {
                    "decision": "dropped",
                    "target_component_id": target_cid,
                    "anchor_component_ids": list(anchors),
                    "callback_text": callback_text,
                    "reason": gate.reason,
                    "audit": gate.audit,
                }
            )
            continue
        # M4: a KEPT callback with no joinable delta can be neither role-stamped
        # nor 07G-teethed ⇒ never ship it; DROP (silent) + audit.
        delta = _warm_callback_delta_for_segment(segment, parsed)
        if delta is None:
            audit_records.append(
                {
                    "decision": "dropped",
                    "target_component_id": target_cid,
                    "anchor_component_ids": list(anchors),
                    "callback_text": callback_text,
                    "reason": "no-joinable-delta",
                }
            )
            continue
        # AC3 / close-bar #4: 07G read-path teeth on the FIRED callback's HOST
        # segment (visual_reference order is independent of the not-yet-injected
        # narration text, so run it BEFORE injecting). A real scan-order BREACH
        # raises (abort); a low-confidence slide with NO reading_path is not a
        # breach (S1) ⇒ DROP the callback silently + audit.
        fired = {"narration_script": [segment], "segment_manifest_deltas": [delta]}
        assert_callback_reading_path(parsed=fired, roster=roster)
        read_path_warnings = fired.get("reading_path_conformance_warnings") or []
        if any(
            str(w.get("tag")) == "irene.pass2.reading-path-missing"
            for w in read_path_warnings
        ):
            audit_records.append(
                {
                    "decision": "dropped",
                    "target_component_id": target_cid,
                    "anchor_component_ids": list(anchors),
                    "callback_text": callback_text,
                    "reason": "reading-path-missing",
                }
            )
            continue
        # M2b: block-by-omission for a callback figure present in the prior anchor
        # but ABSENT from the current slide's perceived authority (would otherwise
        # ABORT the whole run at the global figure gate). Reuses the FROZEN
        # figure_tokens neck READ-ONLY.
        current_slide = _segment_current_slide_id(segment, parsed)
        offending = sorted(
            _figures(callback_text) - perceived_by_slide.get(current_slide, set())
        )
        if offending:
            audit_records.append(
                {
                    "decision": "dropped",
                    "target_component_id": target_cid,
                    "anchor_component_ids": list(anchors),
                    "callback_text": callback_text,
                    "reason": f"figure-absent-from-current-slide: {offending}",
                }
            )
            continue
        # KEEP: inject into the EXACT gate-read canonical field (M2a) + stamp role.
        _inject_warm_callback_into_canonical(segment, callback_text)
        _set_warm_callback_role(delta)
        audit_records.append(
            {
                "decision": "kept",
                "target_component_id": target_cid,
                "anchor_component_ids": list(anchors),
                "callback_text": callback_text,
                "audit": gate.audit,
            }
        )
    if audit_records:
        parsed["warm_callback_audit"] = audit_records
    return parsed


def _segment_current_slide_id(segment: dict[str, Any], parsed: dict[str, Any]) -> str:
    """The segment's slide id by the SAME rule the figure gate uses (M2b)."""
    slide_id = str(segment.get("slide_id") or segment.get("perception_source") or "").strip()
    if not slide_id:
        slide_id = _segment_slide_id_from_deltas(segment, parsed)
    return slide_id


def _visual_reference_key(ref: dict[str, Any]) -> str:
    for field in (
        "element_id",
        "visual_element_id",
        "visual_element",
        "element",
        "label",
        "text",
        "description",
    ):
        value = str(ref.get(field) or "").strip()
        if value:
            return value
    return ""


def _norm_key(value: Any) -> str:
    return " ".join(str(value).strip().lower().split())


TRANSITIONS: tuple[tuple[str, str], ...] = (
    ("receive", "plan"),
    ("plan", "act"),
    ("act", "verify"),
    ("verify", "reflect"),
    ("reflect", "emit_spans"),
    ("emit_spans", "gate_decision"),
    ("gate_decision", "finalize"),
    ("finalize", "handoff"),
)


def _read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    """Return the canonical-sorted listing of sanctum files (deterministic).

    Empty-sanctum case (Story 2a.2): returns the empty string. The fingerprint
    sha256 of an empty sorted-listing is deterministic across invocations.
    Populated-sanctum case (Story 2a.3+): returns sorted relative paths +
    sha256 of each file's bytes joined by newlines.
    """
    if not sanctum_dir.exists() or not sanctum_dir.is_dir():
        return ""
    # Sort by POSIX-form to keep cross-platform stable (Murat MF3 binding):
    # `sorted()` default on Path objects uses the platform-native separator,
    # which can drift between Windows (`\`) and POSIX (`/`) for paths whose
    # adjacent characters straddle the separator's ASCII codepoint.
    files = sorted(
        (p for p in sanctum_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(sanctum_dir).as_posix(),
    )
    if not files:
        return ""
    lines: list[str] = []
    for path in files:
        rel = path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return "\n".join(lines)


def _read_pass_2_references(
    references_dir: Path = IRENE_REFERENCES_DIR,
    names: tuple[str, ...] = PASS_2_PROMPT_REFERENCES,
) -> str:
    """Read the bundled L5 references in fixed order; concatenate as a single section.

    Byte-stability: file order is the static `names` tuple; each file is read as
    UTF-8; missing files emit a deterministic placeholder so the prompt shape
    is invariant across environments.
    """
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        header = f"### Reference: {name}\n"
        if path.is_file():
            body = path.read_text(encoding="utf-8")
        else:
            body = f"<reference-missing: {name}>"
        parts.append(header + body)
    return "\n\n".join(parts)


def _source_figure_surfaces(source_text: str) -> list[str]:
    """Raw digit-form figure surfaces present in the SOURCE corpus (sorted, deduped).

    Read-only caller of the frozen-neck ``_FIGURE_RE`` (figure_tokens neck is
    untouched — no signature change, no widening). Declared scope is digit-form
    ``$N`` / ``N%`` / ``Nx`` ONLY; word-form + bare-integer numerals are OUT by
    frozen-neck governance and MUST NOT motivate a ``_FIGURE_RE`` change.
    """
    surfaces = {match.group(0).strip() for match in _FIGURE_RE.finditer(source_text)}
    return sorted(surfaces)


def _union_perceived_figures(slide_roster: list[dict[str, Any]]) -> set[str]:
    """Union of per-slide perceived digit-form figures (normalized tokens)."""
    union: set[str] = set()
    for entry in slide_roster:
        for fig in entry.get("perceived_figures") or []:
            union.add(str(fig))
    return union


def _redact_unrendered_source_figures(
    source_text: str, *, deck_figures: set[str]
) -> str:
    """Prompt-only: strip source digit-form figures that appear on no perceived slide.

    Prevents Irene from copying source numerals (e.g. 10%/90%) onto a conceptual
    slide that never rendered them. Does NOT mutate gate inputs — callers must
    keep the raw ``source_text`` for ``_assert_narration_figures_sourced``.
    """
    if not source_text:
        return source_text

    def _replace(match: re.Match[str]) -> str:
        surface = match.group(0)
        if _figure_near_match(_normalize_figure(surface), deck_figures):
            return surface
        return UNRENDERED_SOURCE_FIGURE_TOKEN

    return _FIGURE_RE.sub(_replace, source_text)


def _perceived_speakable_figures_block(slide_roster: list[dict[str, Any]]) -> str:
    """Always-on per-slide allowlist of digit-form figures Irene may speak."""
    lines: list[str] = [
        f"{PERCEIVED_SPEAKABLE_FIGURES_HEADER}\n",
        "Digit-form spoken figures ($N / N% / Nx) MUST be ⊆ this slide's set. "
        "If the set is empty, paraphrase any source teaching point WITHOUT "
        "digit-form numerals — do not invent on-screen authority.\n",
    ]
    for entry in slide_roster:
        slide_id = str(entry.get("slide_id") or "").strip() or "<unknown>"
        figs = sorted(str(f) for f in (entry.get("perceived_figures") or []))
        if figs:
            lines.append(f"- {slide_id}: {', '.join(figs)}")
        else:
            lines.append(
                f"- {slide_id}: <none — paraphrase; do not speak digit-form figures>"
            )
    return "\n".join(lines) + "\n\n"


def _source_figure_authority_block(
    source_text: str, *, slide_roster: list[dict[str, Any]] | None = None
) -> str:
    """Leg-4 reground block: authoritative SOURCE numerals (flag ON only, else "").

    When the flag is OFF this returns "" so the Pass-2 prompt is byte-identical
    aside from the always-on perceived-speakable block (separate seam).

    Speech rules align with VO↔on-screen protection: source provenance never
    licenses speaking a numeral absent from the perceived slide. Conflict
    between source and deck is fail-loud for Gamma — not \"narrate source over
    the slide.\"
    """
    if not narration_figure_fidelity_active():
        return ""
    surfaces = _source_figure_surfaces(source_text)
    figures_line = ", ".join(surfaces) if surfaces else "<none present in source>"
    deck_figures = _union_perceived_figures(slide_roster or [])
    speakable_in_source = sorted(
        s
        for s in surfaces
        if _figure_near_match(_normalize_figure(s), deck_figures)
    )
    speakable_line = (
        ", ".join(speakable_in_source)
        if speakable_in_source
        else "<none — source∩deck empty; paraphrase source numerals>"
    )
    return (
        f"{SOURCE_FIGURE_AUTHORITY_HEADER}\n\n"
        "These are the ONLY numerals with SOURCE provenance (digit-form "
        "$N / N% / Nx). Provenance is necessary but NOT sufficient to speak:\n"
        "1. Speak a digit-form figure only if it is in that slide's perceived "
        "speakable set (on-screen binds speech).\n"
        "2. Speak a digit-form figure only if it also appears in this source "
        "set (no confabulation).\n"
        "3. When a source figure IS on the perceived deck for the slide you "
        "are narrating, you MUST speak it (positive carry).\n"
        "4. When a source figure is NOT on the perceived deck for that slide, "
        "paraphrase WITHOUT the digit-form numeral. Do not speak it. If the "
        "teaching point requires the numeral on-screen, that is an upstream "
        "Gamma/deck defect — not a license to invent VO figures.\n"
        "5. When the deck shows a same-kind numeral that contradicts source, "
        "do not resolve by narrating either value as a workaround; the run "
        "fails loud for Gamma repair (VO must never desync from on-screen).\n\n"
        f"Source-provenance surfaces: {figures_line}\n"
        f"Source∩deck (speakable when on the narrated slide): {speakable_line}\n\n"
    )


def _figure_kind(normalized_figure: str) -> str:
    """Kind prefix of a normalized figure token (money-trillion/percent/multiple/...)."""
    return (
        normalized_figure.split(":", 1)[0]
        if ":" in normalized_figure
        else normalized_figure
    )


def _assemble_pass_2_prompt(
    envelope_payload: dict[str, Any],
    *,
    extracted_source: str,
    slide_roster: list[dict[str, Any]],
) -> tuple[str, str]:
    """Build (system_message, user_message) for Irene's Pass-2 invocation.

    Deterministic concatenation; no datetime, UUIDs, or randomized components
    in the prompt body. dp-v1.1 grounding order (party consensus 2026-06-12):
    the CORPUS leads, then the REAL slide roster she narrates, then the
    sanctum digest and L5 references — explicitly demoted to format-only —
    then the envelope payload as sorted-keys canonical JSON (NFR-I6
    byte-stability; pinned dumps signature per Murat MF3 T4 binding).

    NFR-I6 carve-out (party 2026-07-10): Flag-OFF byte-stability means the
    Flag-ON-only source-figure authority block is absent — NOT that the prompt
    is eternally identical to pre-speakable-block baselines. The always-on
    ``PERCEIVED_SPEAKABLE_FIGURES_HEADER`` block is baseline VO↔on-screen
    contract and is present regardless of the fidelity flag.
    """
    sanctum_section = _read_sanctum_digest()
    references_section = _read_pass_2_references()
    payload_section = _payload_section_for_prompt(envelope_payload, slide_roster)
    authority_lines = "\n".join(entry["visual_authority"] for entry in slide_roster)
    expected_lines = "\n".join(
        f"- {entry['slide_id']}: {entry['expected_visual_plan']}"
        for entry in slide_roster
    )
    reading_path_guidance = _reading_path_guidance(slide_roster)
    deck_figures = _union_perceived_figures(slide_roster)
    # Prompt-only redaction: source numerals absent from the entire perceived
    # deck cannot be copied into VO. Gates still use raw extracted_source.
    prompt_source = _redact_unrendered_source_figures(
        extracted_source, deck_figures=deck_figures
    )
    speakable_figures_block = _perceived_speakable_figures_block(slide_roster)
    # Leg-4 reground (flag ON only). Provenance list + speech rules that keep
    # VO⊆on-screen; when the flag is OFF this is "" (speakable block remains).
    source_figure_block = _source_figure_authority_block(
        extracted_source, slide_roster=slide_roster
    )
    user_message = (
        "## Source corpus (the ONLY content basis for narration)\n\n"
        f"{prompt_source}\n\n"
        f"{source_figure_block}"
        f"{speakable_figures_block}"
        f"{VISUAL_AUTHORITY_HEADER}\n\n"
        f"{authority_lines}\n\n"
        f"{EXPECTED_VISUAL_PLAN_HEADER}\n\n"
        "These expected-plan signals are subordinate planning context only. "
        "They may be stale. When they conflict with perceived slide evidence, "
        "use the perceived visual authority above and ignore the expected plan.\n\n"
        f"{expected_lines}\n\n"
        "## Reading path cadence guidance\n\n"
        "Follow each slide's classified scan order when sequencing visual "
        "references. Use cadence tokens naturally; do not invent unseen "
        "elements to satisfy a pattern.\n\n"
        f"{reading_path_guidance}\n\n"
        "## Sanctum digest (sorted file listing + sha256)\n\n"
        f"{sanctum_section}\n\n"
        "## L5 references (fixed order — STRUCTURE AND FORMAT ONLY; any "
        "subject matter inside these references is exemplar, NOT course "
        "content)\n\n"
        f"{references_section}\n\n"
        "## Envelope payload (sorted-keys JSON)\n\n"
        f"```json\n{payload_section}\n```\n\n"
        "## Task\n\n"
        "Author Pass 2 narration + segment manifest deltas per the procedure "
        "above, grounded EXCLUSIVELY in the source corpus and the perceived "
        "visual authority block. Treat the expected visual plan as demoted, "
        "possibly stale context; never use it as visual authority. Digit-form "
        "spoken figures ($N / N% / Nx) MUST be ⊆ that slide's perceived "
        "speakable set; if the set is empty, paraphrase without digit-form "
        "numerals. If a slide "
        f"is marked `{UNVERIFIED_VISUAL_AUTHORITY}`, say that exact token or "
        "avoid visual claims for that slide. Every visual_reference's "
        "`perception_source` MUST be one of "
        "the roster slide ids verbatim. Return your output as a JSON object "
        "with two top-level keys: `narration_script` (an array of segment "
        "objects) and `segment_manifest_deltas` (an array of manifest patch "
        "objects). Be explicit about visual references and cluster-boundary "
        "bridges."
    )
    return PASS_2_SYSTEM_MESSAGE, user_message


def _parse_pass_2_response(response_content: str) -> dict[str, Any]:
    """Parse the LLM response. Tolerates JSON-with-prose-preamble + bare-JSON.

    Returns a dict with keys `narration_script` (list) + `segment_manifest_deltas`
    (list) + `raw_response` (str). On parse failure, returns the raw content
    under `narration_response` so the verify node can flag the shape mismatch
    rather than the act node raising — bounded scope per AC-B.
    """
    stripped = response_content.strip()
    # Try fenced JSON block first; then bare JSON; then fall back to raw.
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return {
                "narration_script": parsed.get("narration_script", []),
                "segment_manifest_deltas": parsed.get("segment_manifest_deltas", []),
                "raw_response": response_content,
            }
    except json.JSONDecodeError:
        pass
    return {
        "narration_script": [],
        "segment_manifest_deltas": [],
        "raw_response": response_content,
    }


def _parse_pass_1_response(response_content: str) -> dict[str, Any]:
    """Parse Pass-1 response into lesson-design shape."""
    stripped = response_content.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        return parsed
    return {
        "learning_objectives": [],
        "structural_outline": [],
        "cluster_intent": "",
        "raw_response": response_content,
    }


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    """Decode envelope payload from cache carrier; malformed carrier degrades to empty."""
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _act_pass_1(
    state: RunState,
    *,
    handle: Any,
    envelope_payload: dict[str, Any],
    model_id: str,
) -> dict[str, Any]:
    """Pass-1 lesson design branch."""
    system_msg = (
        "You are Irene pass-1. Produce lesson design JSON with keys "
        "`learning_objectives`, `structural_outline`, and `cluster_intent`."
    )
    payload_section = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    response = handle.chat.invoke(
        [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"```json\n{payload_section}\n```"},
        ]
    )
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    lesson_design = _parse_pass_1_response(raw_text)

    output_blob = json.dumps(
        {
            "irene_lesson_design": lesson_design,
            "irene_pass_2_envelope": None,
            "model_id": model_id,
            "usage": getattr(response, "usage_metadata", None),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


def _attach_voice_direction(
    parsed: dict[str, Any], envelope_payload: dict[str, Any]
) -> dict[str, Any]:
    """Attach per-segment `voice_direction` to the frozen manifest (P5 Step 2).

    IR-1 seam: runs post-freeze + post-figure-gate. Delegates to the PURE
    annotation leaf (``annotate_segments_with_voice_direction``) which only ADDS
    delivery metadata and never mutates a grounded field. Gated by
    ``voice_direction_active()`` (``MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE``,
    default OFF): when the flag is OFF the parsed dict is returned UNCHANGED, so
    non-directed runs are byte-identical to the pre-Step-2 baseline.

    Direction inputs are read from the envelope payload (all optional): CD/Pass-2
    ``voice_direction_defaults``, per-segment ``voice_direction_overrides``, and
    the Step-6 G0-enrichment ``role_derived_voice_by_slide`` map (a per-SLIDE seed
    table the orchestrator projected from the frozen enrichment card). The
    component matching + role→voice mapping + ambiguity resolution all happened
    ORCHESTRATOR-SIDE (Winston A3); here we only ALIGN that per-slide table to THIS
    pass's frozen segment ids by the PINNED join (segment ``slide_id`` ordinal ↔
    component ``Slide N`` locator ordinal — Winston A4). The orchestrator cannot key
    by segment id because the segment manifest does not exist until AFTER Pass-2, so
    this thin, deterministic delta-id re-key (no ``app.marcus`` import — Contract M3)
    is the unavoidable specialist-side step. Precedence: explicit override > CD
    defaults > role-derived seed > built-in.

    Two-walk determinism (Winston W-A4): the flag is read live here, but the
    production runner's S2 per-node idempotency contract skips re-dispatch on the
    resume/continuation walk (this node does not re-execute; the captured
    ProductionEnvelope contribution — the baked annotated deltas — is reused).
    There is therefore no cross-walk divergence as long as
    ``MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE`` does not flip mid-run (standing
    constraint; a capture-the-flag-once-into-state hardening is filed as a
    cross-walk follow-on). Fail-loud (UDAC): an out-of-contract or unmatched
    override raises ``VoiceDirectionError`` (a ``SpecialistDispatchError`` ⇒
    recoverable error-pause), never a silent drop.
    """
    if not voice_direction_active():
        return parsed
    deltas = parsed.get("segment_manifest_deltas") or []
    if not deltas:
        return parsed
    # Story enhanced-vo.1 (Slice 0): the role->slide linkage is a DETERMINISTIC
    # IDENTITY JOIN on a stable ``slide_key`` (the source-deck slide ordinal each
    # final segment descends from), replacing the fail-open source/final ordinal-
    # SET comparison. Only a directed+ENRICHED run (a non-empty role-seed table)
    # threads the lineage and stamps slide_key; a card-absent run skips it and is
    # byte-identical to the non-enriched directed-voice run (A5).
    role_table = envelope_payload.get("role_derived_voice_by_slide")
    by_slide = role_table.get("by_slide") if isinstance(role_table, dict) else None
    role_derived_seeds: dict[str, dict[str, Any]] | None = None
    work_deltas = deltas
    if isinstance(by_slide, dict) and by_slide:
        # Authoritative final-slide universe: the grounding-asserted roster
        # (gary_slide_output); fall back to the deltas' own slide_ids (which are
        # grounded to that roster by _assert_narration_joins_roster upstream).
        roster_slide_ids = _roster_slide_ids(envelope_payload, deltas)
        # Resolve final->source slide_key from the explicit carrier
        # (slide_briefs.source_ref), with a deterministic lesson_plan+roster
        # fallback for finals slide_briefs cannot cover (M1: absent/variant-drift
        # slide_briefs is reconstructable; it is NOT a hard-stop).
        slide_key_by_final = _resolve_slide_key_map(
            envelope_payload.get("lesson_plan"),
            envelope_payload.get("slide_briefs"),
            roster_slide_ids,
        )
        # GROUNDING ASSERT (M1): every delta's final slide_id MUST resolve to a
        # source slide_key. A TRUE lineage break fails LOUD with ONE diagnostic
        # naming ALL uncovered slide_ids — never a per-delta first-failure abort,
        # never a fuzzy/ordinal fallback, never degrade-to-neutral (party-binding:
        # a wrong/mis-seed is worse than no run).
        uncovered = sorted(
            {
                str(d.get("slide_id") or "").strip()
                for d in deltas
                if isinstance(d, dict) and str(d.get("slide_id") or "").strip()
            }
            - set(slide_key_by_final)
        )
        if uncovered:
            _lp = envelope_payload.get("lesson_plan")
            has_plan_units = bool(isinstance(_lp, dict) and _lp.get("plan_units"))
            has_briefs = bool(envelope_payload.get("slide_briefs"))
            raise VoiceDirectionError(
                "directed-voice role->slide identity join could not resolve a "
                f"source slide_key for final segment(s) {uncovered}; the source->"
                "final lineage is broken "
                f"(slide_briefs present={has_briefs}, lesson_plan plan_units "
                f"present={has_plan_units}, roster size={len(roster_slide_ids)}). "
                "Fail loud — NO fuzzy/ordinal fallback, NO degrade-to-neutral.",
                tag="irene.voice_direction.slide-key-unresolved",
            )
        # Stamp slide_key on every delta so it rides the segment_manifest_deltas
        # blob to every join consumer (enrique decode + the seed join), then join
        # by slide_key identity.
        work_deltas = _stamp_slide_keys(deltas, slide_key_by_final)
        role_derived_seeds = _role_derived_seeds_for_deltas(work_deltas, by_slide)
    annotated = annotate_segments_with_voice_direction(
        work_deltas,
        defaults=envelope_payload.get("voice_direction_defaults"),
        per_segment_overrides=envelope_payload.get("voice_direction_overrides"),
        role_derived_seeds=role_derived_seeds,
    )
    return {**parsed, "segment_manifest_deltas": annotated}


# Segment ``slide_id`` ordinal parser — the PINNED join's segment side (Winston A4).
# ANCHORED on the TRAILING digit run (EDGE-4): a numeric-PREFIXED slide_id such as
# ``"c1m1-slide-03"`` / ``"module-1-slide-03"`` must read ordinal 3, not the prefix
# "1". This mirrors the orchestrator's anchored ``Slide N`` locator parse so both
# sides of the join agree. Duplicated here (a one-line regex) rather than imported
# from the orchestrator projector to honor Contract M3 (``app.specialists`` ↛
# ``app.marcus.orchestrator``), mirroring the workbook_enrichment loader-replication.
_SLIDE_ID_ORDINAL_RE = re.compile(r"(\d+)\s*$")


def _slide_id_ordinal(slide_id: Any) -> int | None:
    """The 1-based ordinal from a segment ``slide_id`` (trailing digit run)."""
    match = _SLIDE_ID_ORDINAL_RE.search(str(slide_id or ""))
    return int(match.group(1)) if match else None


def _roster_slide_ids(
    envelope_payload: dict[str, Any], deltas: list[dict[str, Any]]
) -> list[str]:
    """The ordered FINAL-deck slide ids — the authoritative universe for the join.

    Prefers the grounding-asserted ``gary_slide_output`` roster (post-variant-filter:
    one row per slide_id); falls back to the deltas' own slide_ids (which are grounded
    to that roster by ``_assert_narration_joins_roster``). Order + first-seen dedup.
    """
    rows = envelope_payload.get("gary_slide_output")
    source: list[Any] = rows if isinstance(rows, list) and rows else deltas
    ordered: list[str] = []
    seen: set[str] = set()
    for row in source:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id and slide_id not in seen:
            seen.add(slide_id)
            ordered.append(slide_id)
    return ordered


def _unit_in_scope(unit: dict[str, Any]) -> bool:
    """Include a plan_unit unless it is explicitly ratified out-of-scope.

    Replicates ``app.marcus.orchestrator.package_builders._unit_included`` (the
    same predicate ``build_gary_briefs`` uses to expand in-scope units into the
    final ``slide-NN`` deck), duplicated here to honor Contract M3
    (``app.specialists`` ↛ ``app.marcus``), mirroring the ``_slide_id_ordinal``
    loader-replication. ``scope_decision`` is a bare string or a ``{"scope": ...}``
    mapping; absence keeps the unit IN (conservative).
    """
    decision: Any = unit.get("scope_decision")
    if isinstance(decision, dict):
        decision = decision.get("scope")
    return decision != "out-of-scope"


def _source_slide_id_for_unit(unit: dict[str, Any]) -> str:
    """The SOURCE-deck slide id a plan_unit descends from (FAIL-LOUD; S1).

    A head IS its own source slide (``unit_id``); an interstitial borrows its
    head's ``parent_slide_id``. An interstitial with NO resolvable parent is a
    ``normalize_clusters`` invariant violation: we must NOT fall through to the
    interstitial's own id (``"slide-2-i1"`` whose trailing ordinal is ``1`` not
    ``2``) — that is exactly the silent mis-seed this story exists to kill. Raise
    instead (a wrong seed is worse than no run; party-binding).
    """
    unit_id = str(unit.get("unit_id") or "").strip()
    if unit.get("cluster_role") == "interstitial":
        parent = str(unit.get("parent_slide_id") or "").strip()
        if not parent:
            raise VoiceDirectionError(
                f"interstitial plan_unit unit_id={unit_id!r} carries no resolvable "
                "parent_slide_id; its source slide_key cannot be derived without "
                "mis-keying on its own ordinal (the normalize_clusters invariant is "
                "violated). Fail loud — never silently mis-seed.",
                tag="irene.voice_direction.interstitial-no-parent",
            )
        return parent
    return unit_id


def _source_slide_key_by_final(
    lesson_plan: Any, slide_briefs: Any
) -> dict[str, str]:
    """PRIMARY ``{final_slide_id: slide_key}`` from the explicit lineage carrier.

    Story enhanced-vo.1 (Slice 0). ``slide_key`` is the SOURCE-deck slide ordinal
    (a stable source-slide identity) each FINAL segment descends from — NOT the
    final segment ordinal (which Pass-1 clustering renumbers and which made the
    legacy join fail open). The carrier rides Irene's Pass-2 envelope:

    * ``slide_briefs`` (node 08 projection of ``package_builder.slides`` =
      ``build_gary_briefs`` output) maps each FINAL ``slide_id`` -> its source
      ``source_ref`` (the Pass-1 ``unit_id``);
    * ``lesson_plan.plan_units`` (irene_pass1, deterministically normalized by
      ``normalize_clusters``) resolves a unit to its SOURCE slide via
      :func:`_source_slide_id_for_unit`.

    N sub-slides of one clustered source slide share one slide_key and all inherit
    the source slide's role seed. PURE / offline. Reads DATA only (Contract M3).
    Dedup is FIRST-WINS on both plan_units and briefs (matches
    ``_slide_briefs_by_slide``). FAIL-LOUD on a parentless interstitial (S1); a
    brief whose ``source_ref`` is not in the plan (re-refinement drift) is OMITTED
    — the CALLER's grounding assert turns an uncovered final slide into a loud,
    aggregated lineage-break error.
    """
    plan_units = lesson_plan.get("plan_units") if isinstance(lesson_plan, dict) else None
    if not isinstance(plan_units, list):
        plan_units = []
    unit_by_id: dict[str, dict[str, Any]] = {}
    for unit in plan_units:
        if not isinstance(unit, dict):
            continue
        unit_id = str(unit.get("unit_id") or "").strip()
        if unit_id and unit_id not in unit_by_id:  # first-wins
            unit_by_id[unit_id] = unit

    briefs = slide_briefs if isinstance(slide_briefs, list) else []
    slide_key_by_final: dict[str, str] = {}
    for brief in briefs:
        if not isinstance(brief, dict):
            continue
        final_slide_id = str(brief.get("slide_id") or "").strip()
        source_ref = str(brief.get("source_ref") or "").strip()
        if not final_slide_id or not source_ref:
            continue
        if final_slide_id in slide_key_by_final:  # first-wins
            continue
        unit = unit_by_id.get(source_ref)
        if unit is None:
            continue  # re-refinement drift -> caller's grounding assert fails loud
        ordinal = _slide_id_ordinal(_source_slide_id_for_unit(unit))
        if ordinal is None:
            continue
        slide_key_by_final[final_slide_id] = str(ordinal)
    return slide_key_by_final


def _fallback_slide_key_by_final(
    lesson_plan: Any, roster_slide_ids: list[str]
) -> dict[str, str]:
    """FALLBACK ``{final_slide_id: slide_key}`` reconstructed from lesson_plan + roster.

    When ``slide_briefs`` is absent/incomplete (an OPTIONAL, non-grounding-asserted
    envelope key), reconstruct the SAME deterministic expansion ``build_gary_briefs``
    performed: the in-scope ``plan_units`` (in order) map 1:1 onto the final deck
    ``slide-01..slide-NN``. For each final ``slide-NN`` the source identity is the
    N-th in-scope plan_unit's source slide (:func:`_source_slide_id_for_unit`).

    LOAD-BEARING INVARIANT (Winston, CLOSE condition) — the positional
    reconstruction is sound ONLY under three assumptions that MUST hold together;
    this gate is a contract, not an implementation detail. A future editor who
    weakens any of them MUST update this gate or the reconstruction silently
    mis-seeds:
      1. LENGTH-EQUALITY: ``len(in_scope_units) == len(roster)`` (one final slide
         per in-scope unit — exactly the ``build_gary_briefs`` expansion).
      2. CONTIGUITY: the final ``slide-NN`` ordinals are 1..len(in_scope), so
         ``slide-NN`` indexes ``in_scope[N-1]``.
      3. ROSTER ⊆ BRIEFS / ORDER-COUPLING: the roster's slide order is locked to
         the in-scope unit order. Confirmed by investigation (enhanced-vo.1):
         (a) ``gary_slide_output`` carries NO source lineage — only ``slide_id`` —
         so position is the only available link; (b) variant filtering
         (production_runner ``_apply_*_variant_selection``) is slide_id-PRESERVING
         (every original slide_id retained, one row each), so it cannot drop or
         reorder the roster relative to the brief expansion.
    On a shape mismatch (length/contiguity) this returns ``{}`` so the caller's
    grounding assert fails loud rather than risk an off-by-one mis-seed. A same-
    length, same-contiguity RE-ORDERING (assumption 3 broken) is BLIND to this gate
    alone — it is caught by the cross-consistency guard in
    :func:`_resolve_slide_key_map` (the explicit ``source_ref`` carrier vs this
    positional map MUST agree). ``gary_slide_output`` IS grounding-asserted upstream,
    so this carrier is at least as trustworthy as ``slide_briefs``. PURE / offline /
    DATA-only (M3).
    """
    plan_units = lesson_plan.get("plan_units") if isinstance(lesson_plan, dict) else None
    if not isinstance(plan_units, list):
        return {}
    in_scope = [u for u in plan_units if isinstance(u, dict) and _unit_in_scope(u)]
    roster = [str(s or "").strip() for s in roster_slide_ids if str(s or "").strip()]
    if not in_scope or not roster or len(in_scope) != len(roster):
        return {}
    mapping: dict[str, str] = {}
    for final_slide_id in roster:
        index = _slide_id_ordinal(final_slide_id)
        if index is None or not (1 <= index <= len(in_scope)):
            return {}  # non-contiguous / unexpected numbering -> let the assert fail loud
        ordinal = _slide_id_ordinal(_source_slide_id_for_unit(in_scope[index - 1]))
        if ordinal is None:
            return {}
        mapping[final_slide_id] = str(ordinal)
    return mapping


def _resolve_slide_key_map(
    lesson_plan: Any, slide_briefs: Any, roster_slide_ids: list[str]
) -> dict[str, str]:
    """The DETERMINISTIC ``{final_slide_id: slide_key}`` map: primary + cross-checked fallback.

    Primary = the explicit ``slide_briefs.source_ref`` carrier (identity lookup,
    re-refinement-drift-detecting). Fallback = the positional lesson_plan+roster
    reconstruction (:func:`_fallback_slide_key_by_final`).

    CROSS-CONSISTENCY GUARD (Murat, CLOSE condition — order-invariant): the two
    derivations are INDEPENDENT (one keys on ``source_ref`` identity, the other on
    position). On a consistent envelope they are identical by construction
    (``build_gary_briefs`` sets ``source_ref = in_scope_units[N-1].unit_id`` for
    final ``slide-N``). Where BOTH resolve the same final they MUST AGREE; a
    disagreement means the positional order-coupling the fallback relies on is
    broken (a future roster-construction change, or a corrupt carrier) — FAIL LOUD
    (a wrong/mis-seed is worse than no run; party-binding). This surfaces the
    coupling break on every NORMAL briefs-present run, BEFORE it can silently
    mis-seed a later briefs-absent run. The positional fallback's blindness to a
    same-length/same-contiguity re-ordering is therefore covered here, not left to
    the length+contiguity gate alone.

    Merge: the explicit carrier WINS; the fallback fills only finals the primary
    could not cover (e.g. ``slide_briefs`` absent). Both fail loud on a parentless
    interstitial. Neither degrades to neutral — a final neither can cover is
    surfaced by the caller's aggregated grounding assert.
    """
    primary = _source_slide_key_by_final(lesson_plan, slide_briefs)
    fallback = _fallback_slide_key_by_final(lesson_plan, roster_slide_ids)
    conflicts = sorted(
        final_id
        for final_id in primary
        if final_id in fallback and primary[final_id] != fallback[final_id]
    )
    if conflicts:
        detail = ", ".join(
            f"{f}: source_ref->{primary[f]} vs positional->{fallback[f]}"
            for f in conflicts
        )
        raise VoiceDirectionError(
            "directed-voice slide_key lineage is INCONSISTENT: the explicit "
            "slide_briefs.source_ref carrier and the positional lesson_plan+roster "
            f"reconstruction DISAGREE on final segment(s) [{detail}]. The roster<->"
            "in-scope-unit order coupling is broken (a roster-construction change or "
            "a corrupt lineage carrier). Fail loud — never silently mis-seed.",
            tag="irene.voice_direction.slide-key-order-mismatch",
        )
    merged = dict(fallback)
    merged.update(primary)  # explicit carrier wins; fallback fills gaps
    return merged


def _stamp_slide_keys(
    deltas: list[dict[str, Any]], slide_key_by_final: dict[str, str]
) -> list[dict[str, Any]]:
    """Return NEW deltas each carrying its ``slide_key`` (PURE; never mutates input).

    AC-A3 no-fuzzy-fallback: a delta whose final ``slide_id`` does not resolve to a
    source ``slide_key`` is a lineage break — raise ``VoiceDirectionError`` (build-
    breaking), never silently fall back to ordinal matching. Called ONLY when a
    role-seed table is present (a directed+enriched run).
    """
    stamped: list[dict[str, Any]] = []
    for delta in deltas:
        if not isinstance(delta, dict):
            stamped.append(delta)
            continue
        final_slide_id = str(delta.get("slide_id") or "").strip()
        slide_key = slide_key_by_final.get(final_slide_id)
        if slide_key is None:
            raise VoiceDirectionError(
                "directed-voice role->slide identity join could not resolve a "
                f"slide_key for final segment slide_id={final_slide_id!r} "
                f"(delta id={delta.get('id')!r}); the source->final lineage "
                "(slide_briefs.source_ref + lesson_plan.plan_units) is broken. "
                "Fail loud — NO fuzzy/ordinal fallback.",
                tag="irene.voice_direction.slide-key-unresolved",
            )
        new_delta = dict(delta)
        new_delta["slide_key"] = slide_key
        stamped.append(new_delta)
    return stamped


def _role_derived_seeds_for_deltas(
    deltas: list[dict[str, Any]],
    by_slide: Any,
) -> dict[str, dict[str, Any]] | None:
    """Re-key the orchestrator's per-slide seed table onto THIS pass's segment ids.

    Story enhanced-vo.1 (Slice 0) — DETERMINISTIC IDENTITY JOIN. ``by_slide`` is the
    orchestrator's seed table keyed by SOURCE-deck slide ordinal (the slide_key). Each
    delta already carries its ``slide_key`` (stamped by :func:`_stamp_slide_keys` from
    the source lineage). The join is a direct identity lookup ``by_slide[slide_key]`` —
    there is NO source/final ordinal-SET comparison and NO fail-open path: a clustered
    final deck (where the final ordinals diverge from the source ordinals) now FIRES the
    correct seed on the correct final segment. A source slide with no seed leaves its
    segments on the conservative built-in (IR-A2 no-seed fail-safe).

    Each seed is keyed by the delta's (stripped) ``id`` — pre-filtered to the ids
    present in THIS manifest. Returns ``None`` when nothing is seeded so the pass is
    byte-identical to the non-enriched directed-voice run.
    """
    if not isinstance(by_slide, dict) or not by_slide:
        return None
    seeds: dict[str, dict[str, Any]] = {}
    for delta in deltas:
        if not isinstance(delta, dict):
            continue
        sid = delta.get("id")
        if not (isinstance(sid, str) and sid.strip()):
            continue
        slide_key = delta.get("slide_key")
        if slide_key is None:
            continue
        seed = by_slide.get(str(slide_key))
        if isinstance(seed, dict) and seed:
            seeds[sid.strip()] = dict(seed)
    return seeds or None


def _act_pass_2(
    state: RunState,
    *,
    handle: Any,
    envelope_payload: dict[str, Any],
    model_id: str,
) -> dict[str, Any]:
    """Pass-2 narration branch (dp-v1.1 grounded; party consensus 2026-06-12).

    Fail-loud grounding reads BEFORE prompt assembly: corpus via the shared
    ``read_extracted_source`` reader (raises ``SourceBundleError``), real
    slide roster via ``_slide_roster`` (raises ``Pass2GroundingError``), and
    the latest refined lesson plan. Post-parse, the narration must join the
    real roster (Winston deterministic post-check).
    """
    extracted_source = read_extracted_source(envelope_payload)
    slide_roster = _slide_roster(envelope_payload)
    if not envelope_payload.get("lesson_plan"):
        raise Pass2GroundingError(
            "Pass 2 requires the latest refined lesson_plan in its payload; "
            "node 08 projections must deliver it",
            tag="irene.pass2.grounding-missing",
        )
    system_msg, user_msg = _assemble_pass_2_prompt(
        envelope_payload,
        extracted_source=extracted_source,
        slide_roster=slide_roster,
    )
    response = handle.chat.invoke(
        [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
    )
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    parsed = _parse_pass_2_response(raw_text)
    # Story 1.2a: backfill id-less deltas BEFORE the join-dependent asserts and
    # before the deltas are serialized for enrique/publisher/G5 (clustered-deck
    # LLM-variance repair; see backfill_delta_ids).
    parsed = backfill_delta_ids(parsed)
    # Live trial 72ed8fd5 (non-clustered): a cluster-head delta lost its
    # perception_source (empty visual_references) → the join drops its narration
    # → enrique refuses pre-spend. Roster-grounded, alignment-gated backfill.
    parsed = backfill_delta_perception_sources(parsed, slide_roster)
    # Story concierge-leg1b (Slice 2): author + Vera-R7-gate warm_callback
    # narration HERE — after perception backfill, BEFORE the join/reading-path/
    # figure asserts — so a KEPT callback's canonical prose ALSO flows all three
    # gates. The renderer is the real gpt-5 chat-invoke by default (injectable
    # seam; a deterministic fake in unit tests). Flag OFF (default) ⇒ unchanged.
    parsed = _attach_warm_callbacks(
        parsed,
        envelope_payload,
        slide_roster,
        model_invoke=handle.chat.invoke,
    )
    _assert_narration_joins_roster(parsed, slide_roster)
    # id-integrity gate (irene-pass2-slidejoin-id-integrity-gate.md): the roster
    # gate above checks perception_source grounding but NEVER the id-join. An
    # id-less / non-bijective emission (the frozen 40f3a90a shape) passes it yet
    # collapses in the shared join into a degenerate one-narration storyboard.
    # Fail loud on the retryable tag so auto-retry re-rolls an id-bearing Pass-2.
    _assert_join_id_integrity(parsed)
    _assert_reading_path_conformance(parsed, slide_roster)
    _assert_figure_citations_within_perceived(parsed, slide_roster)
    # Leg-4 SOURCE-direction figure-fidelity gate (flag-gated; ADDITIVE to the
    # deck-direction gate above — both hold when the flag is ON). Self-guards on
    # MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE, so flag OFF (default) ⇒ inert / no
    # state change ⇒ byte-identical. Runs AFTER the deck-direction gate so that
    # gate's behavior is unchanged.
    _assert_narration_figures_sourced(
        parsed, slide_roster, source_text=extracted_source
    )
    # Mine-next T4b positive-carry (flag-gated; ADDITIVE): source∩deck figures
    # must appear in narration. Self-guards on the same fidelity flag.
    _assert_source_figures_positively_carried(
        parsed, slide_roster, source_text=extracted_source
    )
    # AC1 (finding-d): the emitted Pass-2 package is directly validatable in-band
    # (retires the out-of-band concierge normalization step).
    assert_pass2_surfaces_validatable(parsed)
    # P5 directed-voice Step 2 (IR-1): the SEPARATE, pure, deterministic voice-
    # direction annotation pass runs ONLY here — AFTER the manifest is frozen and
    # AFTER the figure-citation gate has passed — and ONLY attaches delivery
    # metadata. It never re-generates the script and never touches a grounded
    # field. Flag OFF (default) ⇒ byte-identical (no voice_direction emitted).
    # M3 (both-flags precedence): snapshot the warm_callback roles, then re-stamp
    # them AFTER _attach_voice_direction — which rebuilds voice_direction from
    # scratch and would otherwise drop rhetorical_role='warm_callback'.
    warm_callback_role_keys = _warm_callback_role_keys(parsed)
    parsed = _attach_voice_direction(parsed, envelope_payload)
    _restamp_warm_callback_roles(parsed, warm_callback_role_keys)
    output_payload: dict[str, Any] = {
        "narration_script": parsed["narration_script"],
        "segment_manifest_deltas": parsed["segment_manifest_deltas"],
        "model_id": model_id,
        "usage": getattr(response, "usage_metadata", None),
    }
    # Story concierge-leg1b (Slice 2 / T11 carrier-robustness): the warm_callback
    # decision audit — BOTH kept and block-by-omission DROPPED records — must
    # survive into the persisted carrier (the bundle/envelope side-car carries
    # current state of EVERYTHING; AC5 requires a LOUD, durable audit). Added ONLY
    # when non-empty, so a flag-OFF / no-callback run stays byte-identical.
    warm_callback_audit = parsed.get("warm_callback_audit")
    if warm_callback_audit:
        output_payload["warm_callback_audit"] = warm_callback_audit
    output_blob = json.dumps(
        output_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


def _receive(state: RunState) -> dict[str, Any]:
    """Accept envelope + advance to plan; cache-prefix idempotent."""
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    """Resolve model cascade for Irene + append the resolution entry to the trail (AC-C)."""
    handle = make_chat_model(
        specialist_id="irene",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, handle.entry],
    }


def _act(state: RunState) -> dict[str, Any]:
    """Pass-2 narration LLM invocation (bounded ~150 LOC across helpers — AC-B + MF4).

    Reads the latest resolution entry from `_plan`, reconstructs the chat
    handle, assembles the deterministic prompt, invokes once, parses, and
    returns a partial RunState update plus the parsed result under the
    transient `cache_state` slot (entries_count carries the prompt-token
    floor evidence at MF2).
    """
    if not state.model_resolution_trail:
        # Defensive: plan must run before act. Bounded fail-loud per Murat.
        raise RuntimeError("act node invoked before plan; resolution trail empty")
    last_entry = state.model_resolution_trail[-1]
    # Discriminator check (Winston T4 binding): the last trail entry must carry
    # a cache_prefix_hash — i.e., it must be a *final* cascade resolution, not
    # an intermediate or upstream-injected entry. Slab-3 middleware that
    # appends between plan and act would land here without a prefix hash;
    # fail loud rather than reuse a stale or wrong-shape entry.
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "act node read trail entry without cache_prefix_hash; expected "
            "the final cascade resolution from `_plan` as the immediate "
            "predecessor (level=" + last_entry.level + ")"
        )
    # G6 BH-MF1 fix: cache_prefix_hash is non-None (raised above otherwise).
    # The `or ""` defensive fallback was dead code that contradicted the explicit
    # `is None` raise above; pass the hash directly.
    handle = make_chat_model(
        specialist_id="irene",
        temperature=state.temperature,
        tier_request="reasoning",
        system_prompt_hash=last_entry.cache_prefix_hash,
    )
    envelope_payload = _decode_envelope_payload(state)
    pass_phase = envelope_payload.get("pass_phase")
    if pass_phase == "pass-1":
        return _act_pass_1(
            state,
            handle=handle,
            envelope_payload=envelope_payload,
            model_id=last_entry.resolved,
        )
    return _act_pass_2(
        state,
        handle=handle,
        envelope_payload=envelope_payload,
        model_id=last_entry.resolved,
    )


def _verify(state: RunState) -> dict[str, Any]:
    """Cross-field invariants on Irene act output (G4 narration-script stub at Slab 2)."""
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    """Self-assessment placeholder — Vera-style drift detection at Slab 3."""
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    """LangSmith span emission per NFR-O4 (handle metadata already attached at adapter)."""
    return specialist_summary_writer.emit_summary_for_state("irene", state)


def _gate_decision(state: RunState) -> dict[str, Any]:
    """Gate-decision interrupt() binding (AC-E + Winston W2).

    Pass-2 runtime routes around this node on clean verify (edges direct
    `verify` → `finalize` via the canonical TRANSITIONS table). Synthetic
    verify-fail envelopes traverse here and raise the Slab-1 stub
    NotImplementedError when reached — confirms wiring without committing
    to Slab 3.3 semantics. `_resume_from_verdict` import retained for C3 binding.
    """
    _ = _resume_from_verdict
    interrupt({"gate_id": "irene-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    """Build SpecialistReturn-equivalent payload (idempotent partial)."""
    del state
    return {}


def _handoff(state: RunState) -> Command:
    """Terminal handoff command back to orchestrator."""
    del state
    return Command(goto=END, update={})


def build_irene_graph() -> StateGraph:
    """Build Irene's 9-node scaffold-conformant LangGraph subgraph."""
    graph = StateGraph(state_schema=RunState)
    graph.add_node("receive", _receive)
    graph.add_node("plan", _plan)
    graph.add_node("act", _act)
    graph.add_node("verify", _verify)
    graph.add_node("reflect", _reflect)
    graph.add_node("emit_spans", _emit_spans)
    graph.add_node("gate_decision", _gate_decision)
    graph.add_node("finalize", _finalize)
    graph.add_node("handoff", _handoff)
    graph.add_edge(START, "receive")
    for src, dst in TRANSITIONS:
        graph.add_edge(src, dst)
    graph.add_edge("handoff", END)

    present = frozenset(graph.nodes.keys())
    if present != SCAFFOLD_NODE_IDS:
        missing = sorted(SCAFFOLD_NODE_IDS - present)
        extra = sorted(present - SCAFFOLD_NODE_IDS)
        raise RuntimeError(
            f"generated scaffold drift for irene; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "CONSUMED_PAYLOAD_KEYS",
    "FIGURE_FIDELITY_ACTIVE_ENV",
    "PASS_2_PROMPT_REFERENCES",
    "PASS_2_SYSTEM_MESSAGE",
    "PERCEIVED_SPEAKABLE_FIGURES_HEADER",
    "Pass2GroundingError",
    "Pass2ReadingPathError",
    "SOURCE_FIGURE_AUTHORITY_HEADER",
    "TRANSITIONS",
    "UNRENDERED_SOURCE_FIGURE_TOKEN",
    "UNVERIFIED_VISUAL_AUTHORITY",
    "_act",
    "_assert_reading_path_conformance",
    "_assemble_pass_2_prompt",
    "_decode_envelope_payload",
    "_act_pass_1",
    "_act_pass_2",
    "_assert_figure_citations_within_perceived",
    "_assert_narration_figures_sourced",
    "_assert_source_figures_positively_carried",
    "_perceived_speakable_figures_block",
    "_redact_unrendered_source_figures",
    "_source_figure_authority_block",
    "_union_perceived_figures",
    "narration_figure_fidelity_active",
    "_parse_pass_2_response",
    "_parse_pass_1_response",
    "_slide_roster",
    "_plan",
    "_read_pass_2_references",
    "_read_sanctum_digest",
    "build_irene_graph",
]
