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
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import ValidationError

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.perception import PerceptionArtifact as RichPerceptionArtifact
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.run_state import RunState
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS
from app.specialists._shared.figure_tokens import _FIGURE_RE, _figures, _normalize_figure
from app.specialists._shared.voice_direction_map import voice_direction_active
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.authoring.voice_direction_annotation import (
    annotate_segments_with_voice_direction,
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
    user_message = (
        "## Source corpus (the ONLY content basis for narration)\n\n"
        f"{extracted_source}\n\n"
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
        "possibly stale context; never use it as visual authority. If a slide "
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
    role_derived_seeds = _role_derived_seeds_for_deltas(
        deltas, envelope_payload.get("role_derived_voice_by_slide")
    )
    annotated = annotate_segments_with_voice_direction(
        deltas,
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


def _role_derived_seeds_for_deltas(
    deltas: list[dict[str, Any]],
    role_derived_voice_by_slide: Any,
) -> dict[str, dict[str, Any]] | None:
    """Re-key the orchestrator's per-slide seed table onto THIS pass's segment ids.

    The orchestrator threads ``{"by_slide": {ordinal: voice}, "source_slide_ordinals":
    [...]}``: ``by_slide`` is the seed table keyed by SOURCE-deck slide ordinal (the
    segment manifest does not exist at dispatch time, so it cannot key by segment id);
    ``source_slide_ordinals`` is the source deck's slide-ordinal universe.

    EDGE-1 DIVERGENCE GUARD (the production-correctness fix): the source-card slide
    numbering and the FINAL-deck slide numbering are TWO DIFFERENT ordinal spaces —
    Pass-1 clustering / sub-slide split / ignore-drop / reorder renumbers the final
    deck (a 6-source-slide deck becomes ``slide-01..slide-11``). Applying a source
    ordinal to a final ``slide-NN`` of a different value would MIS-PACE a real learner
    segment, silently. So we only apply seeds when the source and final slide-ordinal
    SETS COINCIDE 1:1 (cardinality + membership); on ANY divergence we FAIL OPEN —
    emit NO seeds (neutral built-in), never a wrong-role seed. Voice is delivery-only,
    so a fail-open neutral is harmless; a mis-seed is not. The durable content-grounded
    join is filed as ``p5-s2-role-seed-robust-source-to-final-slide-linkage``.

    Each surviving delta's seed is keyed by its (stripped) ``id`` — pre-filtered to
    the ids present in THIS manifest (IR-A2; never lean on the leaf's fail-loud
    unmatched-id raise). Returns ``None`` when nothing is seeded (no table, guard
    tripped, or no delta matched) so the pass is byte-identical to the non-enriched
    directed-voice run.
    """
    if not isinstance(role_derived_voice_by_slide, dict):
        return None
    by_slide = role_derived_voice_by_slide.get("by_slide")
    source_ordinals = role_derived_voice_by_slide.get("source_slide_ordinals")
    if not isinstance(by_slide, dict) or not by_slide:
        return None
    if not isinstance(source_ordinals, list):
        return None

    # Final-deck distinct slide ordinals + the per-delta ordinal map.
    final_ordinals: set[int] = set()
    delta_ordinal: dict[str, int] = {}
    for delta in deltas:
        if not isinstance(delta, dict):
            continue
        sid = delta.get("id")
        if not (isinstance(sid, str) and sid.strip()):
            continue
        ordinal = _slide_id_ordinal(delta.get("slide_id"))
        if ordinal is None:
            continue
        final_ordinals.add(ordinal)
        delta_ordinal[sid.strip()] = ordinal

    # EDGE-1 guard: source↔final ordinal spaces must coincide exactly, else fail open.
    try:
        source_set = {int(o) for o in source_ordinals}
    except (TypeError, ValueError):
        return None
    if not source_set or source_set != final_ordinals:
        return None

    seeds: dict[str, dict[str, Any]] = {}
    for sid, ordinal in delta_ordinal.items():
        seed = by_slide.get(str(ordinal))
        if isinstance(seed, dict) and seed:
            seeds[sid] = dict(seed)
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
    _assert_narration_joins_roster(parsed, slide_roster)
    _assert_reading_path_conformance(parsed, slide_roster)
    _assert_figure_citations_within_perceived(parsed, slide_roster)
    # P5 directed-voice Step 2 (IR-1): the SEPARATE, pure, deterministic voice-
    # direction annotation pass runs ONLY here — AFTER the manifest is frozen and
    # AFTER the figure-citation gate has passed — and ONLY attaches delivery
    # metadata. It never re-generates the script and never touches a grounded
    # field. Flag OFF (default) ⇒ byte-identical (no voice_direction emitted).
    parsed = _attach_voice_direction(parsed, envelope_payload)
    output_blob = json.dumps(
        {
            "narration_script": parsed["narration_script"],
            "segment_manifest_deltas": parsed["segment_manifest_deltas"],
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
    "PASS_2_PROMPT_REFERENCES",
    "PASS_2_SYSTEM_MESSAGE",
    "Pass2GroundingError",
    "Pass2ReadingPathError",
    "TRANSITIONS",
    "UNVERIFIED_VISUAL_AUTHORITY",
    "_act",
    "_assert_reading_path_conformance",
    "_assemble_pass_2_prompt",
    "_decode_envelope_payload",
    "_act_pass_1",
    "_act_pass_2",
    "_assert_figure_citations_within_perceived",
    "_parse_pass_2_response",
    "_parse_pass_1_response",
    "_slide_roster",
    "_plan",
    "_read_pass_2_references",
    "_read_sanctum_digest",
    "build_irene_graph",
]
