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
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.payload_contract import CONSUMED_PAYLOAD_KEYS
from app.specialists.source_bundle import read_extracted_source

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
    "You are Irene, a senior Instructional Architect for health-sciences and "
    "medical-education content. You author Pass 2 narration scripts and "
    "segment manifests grounded in pedagogically faithful instructional design. "
    "Follow the Pass 2 procedure exactly. Return narration that complements "
    "(not duplicates) the visual content of each slide. When clusters are "
    "present, honor cluster boundaries and bridge cadence. Output deterministic, "
    "well-structured prose with explicit visual references woven into the flow."
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


def _slide_roster(envelope_payload: dict[str, Any]) -> list[dict[str, str]]:
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
    roster: list[dict[str, str]] = []
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
        entry["visual_authority"] = _visual_authority_for_slide(
            slide_id, perception_by_slide.get(slide_id)
        )
        entry["expected_visual_plan"] = _expected_visual_plan_for_slide(
            entry["visual_description"], brief_by_slide.get(slide_id)
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


def _assert_narration_joins_roster(
    parsed: dict[str, Any], roster: list[dict[str, str]]
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
    slide_roster: list[dict[str, str]],
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
    payload_section = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    authority_lines = "\n".join(entry["visual_authority"] for entry in slide_roster)
    expected_lines = "\n".join(
        f"- {entry['slide_id']}: {entry['expected_visual_plan']}"
        for entry in slide_roster
    )
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
    _assert_narration_joins_roster(parsed, slide_roster)
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
    "TRANSITIONS",
    "UNVERIFIED_VISUAL_AUTHORITY",
    "_act",
    "_assemble_pass_2_prompt",
    "_decode_envelope_payload",
    "_act_pass_1",
    "_act_pass_2",
    "_parse_pass_2_response",
    "_parse_pass_1_response",
    "_slide_roster",
    "_plan",
    "_read_pass_2_references",
    "_read_sanctum_digest",
    "build_irene_graph",
]
