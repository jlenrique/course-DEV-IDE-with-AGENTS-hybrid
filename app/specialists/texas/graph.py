"""Texas source-wrangler specialist graph (Story 2a.4)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.texas.retrieval_dispatch import dispatch_retrieval
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-texas"
TEXAS_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-texas" / "references"
TEXAS_REFERENCES: tuple[str, ...] = (
    "capability-authoring.md",
    "delegation-contract.md",
    "extract-and-validate.md",
    "extraction-report-schema.md",
    "fallback-resolution.md",
    "first-breath.md",
    "memory-guidance.md",
    "retrieval-contract.md",
    "source-interview.md",
    "transform-registry.md",
)
TEXAS_SANCTUM_LOCK_BASELINE: dict[str, str] = {
    "BOND.md": (
        "292daf562836bedb64f335b6f48ce4b1f8a76d7bf2999dfe591c2c7744602270"
    ),
    "CAPABILITIES.md": (
        "aa41899f3f5f3358f2d14c3f6d71e2dd4af7a98175b8f193c1233cc363305a30"
    ),
    "CLONE-FORK-NOTICE.md": (
        "3f217dda8cb9f251277c9cba647c6331c1da166abf43931979da7e75366423aa"
    ),
    "CREED.md": (
        "019e69a856912e9ca159dbabe4ec0849b69eccc75f69026f1a274a94ac9d5654"
    ),
    "INDEX.md": (
        "f9925f7b9da182f29fe5cee43aff57aadfd20f874099a37f683679c7e924fa57"
    ),
    "MEMORY.md": (
        "1845fb2666062835836b1ff71c9c6fcdb316485babe5064491a6d12c96459119"
    ),
    "PERSONA.md": (
        "c56223c4e873a2b8ed22e75cb128915948216ff6f471f50cd9e2ab0ab3f6a902"
    ),
    "references/capability-authoring.md": (
        "d03139cdecffc83b39cea0cae1475a5a137d6232b4c05914fa887199ea7585d7"
    ),
    "references/delegation-contract.md": (
        "0703ddce39eff29f9f690f0389eda2b0be9c9b295ac6dce059d93082ece099df"
    ),
    "references/extract-and-validate.md": (
        "935b53ad9d101d631d8e853e667ec9fe48f23bd7d0dc006c0f721778acc0ef29"
    ),
    "references/fallback-resolution.md": (
        "7f57912c214d35ec05bfada03bdfcf7a4c54b09077f6000c7170738fe0b4143d"
    ),
    "references/memory-guidance.md": (
        "1c01b65ed84440767ad9766ef36686f26c5d648333387a244f609f0da72f986e"
    ),
    "references/source-interview.md": (
        "e2cceee0dd474cdd4e5ca9c7d70c09701fa91ed30e83e2dcbf3a3c9b7fee2b02"
    ),
    "references/transform-registry.md": (
        "59f15c3b84e0763d1590510c997f731cef3706d51cf1cb4397734a1f355cb648"
    ),
    "scripts/cross_validator.py": (
        "b9b1379230bf604b06c5c67c7ade848a203c8a23a06ed35f43db730a80fce23e"
    ),
    "scripts/extraction_validator.py": (
        "391c61e564f8c00c89b9104013f83e0f266ef22c5751d14fce81f2aeacec1ade"
    ),
    "scripts/source_wrangler_operations.py": (
        "ac32edc8f3004b0e90d88c03cf613bd19afa7963ae689e417a262cb96715d981"
    ),
}

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


class SanctumLockViolation(RuntimeError):  # noqa: N818
    """Raised when the populated sanctum lock baseline drifts."""


class BundleParseError(RuntimeError):  # noqa: N818
    """Raised when Texas's six-artifact bundle cannot be parsed.

    Carries a `tag` attribute drawn from the canonical `bundle.parsed.*`
    namespace so callers (and tests) can assert two-sidedly: parser shape AND
    the resolution-trail tag that classifies the failure (Murat M5 rider).
    """

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


class BundleDispatchError(RuntimeError):  # noqa: N818
    """Raised when the wrangler subprocess dispatch surfaces a hard error.

    Distinguished from `BundleParseError` because the runner reports the
    failure (exit code 30 / unknown non-zero) before any bundle artifact has
    been parsed. Carries a `tag` attribute for two-sided assertions.
    """

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _new_dispatch_trail_entry(
    last_entry: ModelResolutionEntry, *, tag: str
) -> ModelResolutionEntry:
    """Clone the last plan-level resolution entry but stamp the dispatch tag.

    Texas is pure-tool-dispatch, so the trail entry shares the model identity
    of the plan-time resolution and only the `reason` carries the dispatch
    classification. Cloning keeps `cache_prefix_hash` stable for downstream
    cache-prefix attribution (NFR-I6).
    """
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.exists() or not sanctum_dir.is_dir():
        return ""
    files = sorted(
        (p for p in sanctum_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(sanctum_dir).as_posix(),
    )
    if not files:
        return ""
    lines: list[str] = []
    for file_path in files:
        rel = file_path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(
            file_path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return "\n".join(lines)


def _current_sanctum_manifest(sanctum_dir: Path = SANCTUM_DIR) -> dict[str, str]:
    digest = _read_sanctum_digest(sanctum_dir=sanctum_dir)
    if not digest:
        return {}
    manifest: dict[str, str] = {}
    for line in digest.splitlines():
        rel, sha = line.split("\t", 1)
        manifest[rel] = sha
    return manifest


def assert_sanctum_lock(
    expected_manifest: dict[str, str] = TEXAS_SANCTUM_LOCK_BASELINE,
    *,
    sanctum_dir: Path = SANCTUM_DIR,
) -> None:
    current = _current_sanctum_manifest(sanctum_dir=sanctum_dir)
    if current != expected_manifest:
        missing = sorted(set(expected_manifest) - set(current))
        extra = sorted(set(current) - set(expected_manifest))
        mismatched = sorted(
            rel
            for rel in set(expected_manifest).intersection(current)
            if current[rel] != expected_manifest[rel]
        )
        raise SanctumLockViolation(
            "texas sanctum lock baseline drift detected; "
            f"missing={missing}, extra={extra}, mismatched={mismatched}"
        )


def _read_texas_references(
    references_dir: Path = TEXAS_REFERENCES_DIR,
    names: tuple[str, ...] = TEXAS_REFERENCES,
) -> str:
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        header = f"### Reference: {name}\n"
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(header + body)
    return "\n\n".join(parts)


def _load_bundle_outputs(bundle_dir: Path) -> dict[str, Any]:
    result_path = bundle_dir / "result.yaml"
    report_path = bundle_dir / "extraction-report.yaml"
    if not result_path.is_file():
        raise BundleParseError(
            f"missing bundle artifact: {result_path.as_posix()}",
            tag="bundle.parsed.missing-key",
        )
    if not report_path.is_file():
        raise BundleParseError(
            f"missing bundle artifact: {report_path.as_posix()}",
            tag="bundle.parsed.missing-key",
        )
    try:
        result_payload = yaml.safe_load(result_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise BundleParseError(
            f"invalid result.yaml content: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    try:
        report_payload = yaml.safe_load(report_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise BundleParseError(
            f"invalid extraction-report.yaml content: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(result_payload, dict):
        raise BundleParseError(
            "result.yaml must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    if not isinstance(report_payload, dict):
        raise BundleParseError(
            "extraction-report.yaml must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    status = str(result_payload.get("status") or "").strip()
    if not status:
        raise BundleParseError(
            "result.yaml missing non-empty status",
            tag="bundle.parsed.empty",
        )
    overall_status = str(report_payload.get("overall_status") or "").strip()
    if not overall_status:
        raise BundleParseError(
            "extraction-report.yaml missing non-empty overall_status",
            tag="bundle.parsed.empty",
        )
    return {
        "result": result_payload,
        "report": report_payload,
        "status": status,
        "overall_status": overall_status,
        "tag": "bundle.parsed.ok",
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    # Texas is pure-tool-dispatch at act-time; this call exists to preserve the
    # standard resolution-trail contract across all specialist categories.
    handle = make_chat_model(
        specialist_id="texas",
        temperature=state.temperature,
        tier_request="fast",
    )
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    """Decode the envelope-carrier-hack JSON blob from cache_state.cache_prefix.

    Fail-loud on malformed JSON or non-dict shape so a production caller never
    silently drops into the dev-mode fixture-bundle short-circuit (Slab-3 will
    retire the carrier-hack via the dedicated envelope contract; until then,
    explicit shape rejection is the production guard.)
    """
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise BundleParseError(
            f"texas act envelope-carrier cache_prefix is not valid JSON: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise BundleParseError(
            "texas act envelope-carrier cache_prefix must decode to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return decoded


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("texas act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "texas act expected final plan resolution entry with cache_prefix_hash"
        )
    envelope_payload = _decode_envelope_payload(state)
    dispatch_receipt = dispatch_retrieval(
        directive_path=envelope_payload.get("directive_path"),
        bundle_dir=envelope_payload.get("bundle_dir"),
    )
    bundle_path = dispatch_receipt.get("bundle_dir")
    if not bundle_path:
        raise BundleDispatchError(
            "texas dispatch receipt missing bundle_dir",
            tag="bundle.parsed.missing-key",
        )
    bundle_dir = Path(str(bundle_path))
    exit_code = int(dispatch_receipt.get("exit_code") or 0)
    if exit_code == 30:
        raise BundleDispatchError(
            "texas wrangler reported hard error (exit 30); bundle not trusted",
            tag="bundle.parsed.exit-30",
        )
    if exit_code not in (0, 10):
        raise BundleDispatchError(
            f"texas wrangler returned unexpected exit code {exit_code}",
            tag="bundle.parsed.unknown-exit",
        )
    if exit_code == 10:
        # Graceful degrade: wrangler ran cleanly but found no results. Trail
        # records the outcome; downstream nodes can branch on bundle_reference
        # being absent.
        trail_entry = _new_dispatch_trail_entry(last_entry, tag="bundle.parsed.exit-10")
        output_blob = json.dumps(
            {
                "bundle_reference": None,
                "status": "no-results",
                "overall_status": "no-results",
                "artifacts": [],
                "report_schema_version": None,
                "dispatch_exit_code": exit_code,
                "model_id": last_entry.resolved,
            },
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            default=str,
        )
        return {
            "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
            "cache_state": {
                "cache_prefix": output_blob,
                "entries_count": (state.cache_state.entries_count + 1)
                if state.cache_state is not None
                else 1,
            },
        }
    try:
        parsed = _load_bundle_outputs(bundle_dir)
    except BundleParseError as exc:
        # Mutate the trail in-place so the test assertion (exception side) and
        # the trail-tag side (state side) are both observable. List append on a
        # Pydantic field with `validate_assignment=True` is allowed because we
        # mutate the existing list rather than rebinding the attribute.
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "bundle_reference": str(bundle_dir),
            "status": parsed["status"],
            "overall_status": parsed["overall_status"],
            "artifacts": parsed["result"].get("artifacts", []),
            "report_schema_version": parsed["report"].get("schema_version"),
            "dispatch_exit_code": exit_code,
            "model_id": last_entry.resolved,
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("texas", state)


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "texas-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_texas_graph() -> StateGraph:
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
            f"generated scaffold drift for texas; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "BundleDispatchError",
    "BundleParseError",
    "SanctumLockViolation",
    "TEXAS_REFERENCES",
    "TEXAS_SANCTUM_LOCK_BASELINE",
    "TRANSITIONS",
    "assert_sanctum_lock",
    "build_texas_graph",
]
