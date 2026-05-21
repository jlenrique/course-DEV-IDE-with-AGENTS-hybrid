"""Tracy retrieval-intent enrichment implementation."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.tracy.posture_dispatch import record_posture_selection

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-tracy"
REFERENCES_DIR = REPO_ROOT / "skills" / "bmad_agent_tracy" / "references"
TEXAS_CONTRACT = REPO_ROOT / "skills" / "bmad-agent-texas" / "references" / (
    "retrieval-contract.md"
)
TEXAS_SCRIPTS_DIR = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts"
TRACY_REFERENCES = ("vocabulary.yaml", "postures.md")
TRACY_SYSTEM_MESSAGE = (
    "You are Tracy. Shape Irene Pass-2 research needs into Texas-compatible "
    "RetrievalIntent JSON. Return strict JSON with key retrieval_intents."
)


class RetrievalIntentParseError(RuntimeError):
    """Raised when Tracy retrieval intent output is malformed."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


ManifestParseError = RetrievalIntentParseError


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str
    )


def _retrieval_package() -> tuple[Any, Any, Any, Any]:
    if str(TEXAS_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(TEXAS_SCRIPTS_DIR))
    from retrieval import AcceptanceCriteria, ProviderHint, RetrievalIntent  # noqa: PLC0415
    from retrieval.provider_directory import list_providers  # noqa: PLC0415

    return AcceptanceCriteria, ProviderHint, RetrievalIntent, list_providers


def available_retrieval_provider_ids() -> list[str]:
    _, _, _, list_providers = _retrieval_package()
    providers = list_providers(shape="retrieval")
    return sorted(p.id for p in providers if p.status in {"ready", "stub"})


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise RetrievalIntentParseError(
            f"tracy envelope cache_prefix is not valid JSON: {exc}",
            tag="retrieval_intent.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise RetrievalIntentParseError(
            "tracy envelope cache_prefix must decode to a mapping",
            tag="retrieval_intent.parsed.wrong-type",
        )
    return decoded


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows = []
    for path in sorted(
        sanctum_dir.rglob("*"), key=lambda item: item.relative_to(sanctum_dir).as_posix()
    ):
        if path.is_file():
            rel = path.relative_to(sanctum_dir).as_posix()
            digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            rows.append(f"{rel}\t{digest}")
    return "\n".join(rows)


def read_references(references_dir: Path = REFERENCES_DIR) -> str:
    parts = []
    for name in TRACY_REFERENCES:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    texas_body = TEXAS_CONTRACT.read_text(encoding="utf-8")
    parts.append(f"### Texas retrieval contract\n{texas_body}")
    return "\n\n".join(parts)


def assemble_tracy_prompt(payload: dict[str, Any]) -> tuple[str, str]:
    providers = available_retrieval_provider_ids()
    user = (
        "## Sanctum digest\n\n"
        f"{read_sanctum_digest()}\n\n"
        "## References\n\n"
        f"{read_references()}\n\n"
        "## Ready retrieval providers\n\n"
        f"{', '.join(providers)}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{_json_dumps(payload)}\n```\n\n"
        "Return JSON: {\"retrieval_intents\":[{\"intent\":\"natural language\","
        "\"provider_hints\":[{\"provider\":\"scite\",\"params\":{\"mode\":\"search\"}}],"
        "\"acceptance_criteria\":{\"mechanical\":{},\"provider_scored\":{},"
        "\"semantic_deferred\":\"post-fetch judgment\"},\"cross_validate\":false}]}."
    )
    return TRACY_SYSTEM_MESSAGE, user


def _extract_json(raw_text: str) -> Any:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    return json.loads(stripped)


def _default_intent(payload: dict[str, Any]) -> dict[str, Any]:
    topic = payload.get("topic") or payload.get("lesson_summary") or "Irene Pass-2 claim"
    providers = available_retrieval_provider_ids()
    selected = providers[:2] if len(providers) >= 2 else providers[:1]
    if not selected:
        raise RetrievalIntentParseError(
            "no ready-or-stub retrieval providers available",
            tag="retrieval_intent.parsed.no-providers",
        )
    return {
        "intent": f"Find evidence that supports or challenges: {topic}",
        "provider_hints": [
            {"provider": provider, "params": {"mode": "search"}} for provider in selected
        ],
        "acceptance_criteria": {
            "mechanical": {"min_results": 3},
            "provider_scored": {"authority_tier_min": "peer-reviewed"},
            "semantic_deferred": "Tracy will screen retrieved rows against the Pass-2 claim.",
        },
        "cross_validate": len(selected) > 1,
    }


def parse_retrieval_intents(
    raw_content: Any,
    payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if isinstance(raw_content, dict):
        parsed = raw_content
    elif isinstance(raw_content, str):
        try:
            parsed = _extract_json(raw_content)
        except json.JSONDecodeError as exc:
            raise RetrievalIntentParseError(
                f"tracy retrieval-intent parse failed: {exc}",
                tag="retrieval_intent.parsed.malformed",
            ) from exc
    else:
        raise RetrievalIntentParseError(
            "tracy retrieval output must be mapping-or-json-string",
            tag="retrieval_intent.parsed.wrong-type",
        )
    if not isinstance(parsed, dict):
        raise RetrievalIntentParseError(
            "tracy retrieval output must be a mapping",
            tag="retrieval_intent.parsed.wrong-type",
        )
    intents = parsed.get("retrieval_intents")
    if not intents and payload is not None:
        intents = [_default_intent(payload)]
    if not isinstance(intents, list) or not intents:
        raise RetrievalIntentParseError(
            "tracy retrieval output has empty retrieval_intents",
            tag="retrieval_intent.parsed.empty",
        )
    _, _, retrieval_intent_cls, _ = _retrieval_package()
    allowed = set(available_retrieval_provider_ids())
    out = []
    for item in intents:
        if not isinstance(item, dict):
            raise RetrievalIntentParseError(
                "tracy retrieval intent rows must be mappings",
                tag="retrieval_intent.parsed.wrong-type",
            )
        model = retrieval_intent_cls.model_validate(item)
        provider_ids = {hint.provider for hint in model.provider_hints}
        if not provider_ids <= allowed:
            raise RetrievalIntentParseError(
                f"unknown provider_hints: {sorted(provider_ids - allowed)}",
                tag="retrieval_intent.parsed.provider-unknown",
            )
        out.append(model.model_dump(mode="json"))
    return out


def build_retrieval_intent(
    payload: dict[str, Any],
    llm_payload: dict[str, Any],
    *,
    cross_validate: bool,
) -> Any:
    acceptance_criteria_cls, provider_hint_cls, retrieval_intent_cls, _ = (
        _retrieval_package()
    )
    providers = available_retrieval_provider_ids()
    selected = providers[:2] if cross_validate and len(providers) > 1 else providers[:1]
    topic = payload.get("topic") or payload.get("lesson_summary") or "Irene Pass-2 claim"
    criteria = llm_payload.get("acceptance_criteria")
    criteria = criteria if isinstance(criteria, dict) else {}
    mechanical = criteria.get("mechanical") if isinstance(criteria.get("mechanical"), dict) else {}
    provider_scored = (
        criteria.get("provider_scored") if isinstance(criteria.get("provider_scored"), dict) else {}
    )
    semantic = criteria.get("semantic_deferred") or llm_payload.get("semantic_deferred")
    intent_text = llm_payload.get("intent") or (
        f"Find evidence that supports or challenges: {topic}"
    )
    return retrieval_intent_cls(
        intent=str(intent_text),
        provider_hints=[
            provider_hint_cls(provider=provider, params={"mode": "search"})
            for provider in selected
        ],
        acceptance_criteria=acceptance_criteria_cls(
            mechanical={"min_results": 3, **mechanical},
            provider_scored={"authority_tier_min": "peer-reviewed", **provider_scored},
            semantic_deferred=str(
                semantic
                or "Tracy will screen retrieved rows against the Pass-2 claim."
            ),
        ),
        cross_validate=cross_validate,
    )


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def act(state: RunState, *, handle: Any, model_id: str) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("tracy act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    system_msg, user_msg = assemble_tracy_prompt(payload)
    try:
        response = handle.chat.invoke(
            [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        )
        raw = response.content if hasattr(response, "content") else str(response)
        intents = parse_retrieval_intents(raw, payload=payload)
    except RetrievalIntentParseError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    posture_tag = record_posture_selection("supporting_evidence")
    output = {
        "specialist_id": "tracy",
        "model_id": model_id,
        "retrieval_intents": intents,
        "posture_tag": posture_tag,
        "usage": getattr(response, "usage_metadata", None),
    }
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="retrieval_intent.parsed.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(output),
            entries_count=entries_count + 1,
        ).model_dump(mode="json"),
    }


__all__ = [
    "ManifestParseError",
    "RetrievalIntentParseError",
    "TRACY_SYSTEM_MESSAGE",
    "act",
    "assemble_tracy_prompt",
    "available_retrieval_provider_ids",
    "build_retrieval_intent",
    "decode_envelope_payload",
    "parse_retrieval_intents",
    "read_references",
    "read_sanctum_digest",
]
