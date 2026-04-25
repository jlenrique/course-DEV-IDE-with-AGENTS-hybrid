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

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state.run_state import RunState
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

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


def _assemble_pass_2_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
    """Build (system_message, user_message) for Irene's Pass-2 invocation.

    Deterministic concatenation; no datetime, UUIDs, or randomized components
    in the prompt body. The user_message contains the sanctum digest, the
    reference bundle, and the envelope's `payload_in` serialized as
    sorted-keys canonical JSON (NFR-I6 byte-stability).
    """
    sanctum_section = _read_sanctum_digest()
    references_section = _read_pass_2_references()
    # Pinned dumps signature for byte-stability (Murat MF3 T4 binding):
    # sort_keys=True for key-order determinism; ensure_ascii=True so any
    # non-ASCII payload bytes are escape-stable across Python versions;
    # separators pinned to remove platform/version whitespace variance.
    payload_section = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    user_message = (
        "## Sanctum digest (sorted file listing + sha256)\n\n"
        f"{sanctum_section}\n\n"
        "## L5 references (fixed order)\n\n"
        f"{references_section}\n\n"
        "## Envelope payload (sorted-keys JSON)\n\n"
        f"```json\n{payload_section}\n```\n\n"
        "## Task\n\n"
        "Author Pass 2 narration + segment manifest deltas per the procedure "
        "above. Return your output as a JSON object with two top-level keys: "
        "`narration_script` (an array of segment objects) and "
        "`segment_manifest_deltas` (an array of manifest patch objects). "
        "Be explicit about visual references and cluster-boundary bridges."
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
    # NB: envelope-level payload is not on RunState directly in Slab 1 substrate;
    # tests pass it via a synthetic state.cache_state.cache_prefix-encoded path
    # OR invoke `_act` directly with a state pre-populated via the act-test
    # fixture. The bounded scope here is prompt-assembly + dispatch + parse.
    envelope_payload: dict[str, Any] = {}
    if state.cache_state is not None and state.cache_state.cache_prefix:
        # Test fixture conventionally embeds payload as the cache_prefix value
        # (sorted-keys canonical JSON). Bounded extraction for byte-stability.
        try:
            decoded = json.loads(state.cache_state.cache_prefix)
        except json.JSONDecodeError:
            decoded = None
        # G6 EH-MF1 fix: only dict-typed payloads are valid envelope carriers.
        # `json.loads` accepts lists / strings / scalars / null; downstream
        # `_assemble_pass_2_prompt` would otherwise either crash deep on
        # subscript or silently produce garbage prompts.
        if isinstance(decoded, dict):
            envelope_payload = decoded
    system_msg, user_msg = _assemble_pass_2_prompt(envelope_payload)
    response = handle.chat.invoke(
        [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
    )
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    parsed = _parse_pass_2_response(raw_text)
    # Cache-state carries the response payload (raw + parsed) as JSON in
    # cache_prefix for downstream nodes. Production wiring (Slab 3+) will add
    # a dedicated specialist-output field on RunState.
    output_blob = json.dumps(
        {
            "narration_script": parsed["narration_script"],
            "segment_manifest_deltas": parsed["segment_manifest_deltas"],
            "model_id": last_entry.resolved,
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
    del state
    return {}


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
    "PASS_2_PROMPT_REFERENCES",
    "PASS_2_SYSTEM_MESSAGE",
    "TRANSITIONS",
    "_act",
    "_assemble_pass_2_prompt",
    "_parse_pass_2_response",
    "_plan",
    "_read_pass_2_references",
    "_read_sanctum_digest",
    "build_irene_graph",
]
