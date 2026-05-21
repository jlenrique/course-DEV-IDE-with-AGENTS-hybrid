"""Conversation turn persistence with a tamper-evident SHA256 chain."""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = "1.0"
_SHA256_HEX_LEN = 64


class ConversationChainBrokenError(RuntimeError):
    """Raised when a persisted conversation chain cannot be verified."""


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    """Return canonical JSON bytes matching the production digest precedent."""
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_hex_bytes(value: str) -> bytes:
    if len(value) != _SHA256_HEX_LEN or not all(c in "0123456789abcdef" for c in value):
        raise ConversationChainBrokenError(f"invalid sha256 hex digest: {value!r}")
    return bytes.fromhex(value)


def compute_turn_digest(
    *,
    prior_envelope_digest: str,
    decision_card: Mapping[str, Any],
    timestamp_utc: str,
    operator_id: str,
) -> str:
    """Compute the turn digest from prior digest bytes and canonical card JSON."""
    digest = hashlib.sha256()
    digest.update(_sha256_hex_bytes(prior_envelope_digest))
    digest.update(canonical_json_bytes(decision_card))
    digest.update(timestamp_utc.encode("utf-8"))
    digest.update(operator_id.encode("utf-8"))
    return digest.hexdigest()


def directive_digest(trial_id: str, runs_root: Path) -> str:
    """Return the SHA256 digest of ``runs/<trial_id>/directive.yaml``."""
    path = runs_root / trial_id / "directive.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"directive.yaml missing for trial {trial_id}: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _conversation_root(trial_id: str, runs_root: Path) -> Path:
    return runs_root / trial_id / "conversation"


def _gate_dir(trial_id: str, gate_id: str, runs_root: Path) -> Path:
    return _conversation_root(trial_id, runs_root) / gate_id


def _turn_files(trial_id: str, runs_root: Path) -> list[Path]:
    root = _conversation_root(trial_id, runs_root)
    if not root.is_dir():
        return []
    return sorted(root.glob("*/*.json"))


def _sort_key(path: Path) -> tuple[str, str, int]:
    payload = load_turn(path)
    return (
        str(payload["timestamp_utc"]),
        str(payload["gate_id"]),
        int(payload["turn_index"]),
    )


def ordered_turn_files(trial_id: str, runs_root: Path) -> list[Path]:
    """Return all turn files in deterministic chain order."""
    return sorted(_turn_files(trial_id, runs_root), key=_sort_key)


def latest_turn_digest(trial_id: str, runs_root: Path) -> str | None:
    """Return the last persisted conversation digest for a trial, if present."""
    files = ordered_turn_files(trial_id, runs_root)
    if not files:
        return None
    payload = load_turn(files[-1])
    digest = payload.get("digest")
    if not isinstance(digest, str):
        raise ConversationChainBrokenError(f"turn missing digest: {files[-1]}")
    return digest


def _next_turn_index(trial_id: str, gate_id: str, runs_root: Path) -> int:
    gate_dir = _gate_dir(trial_id, gate_id, runs_root)
    if not gate_dir.is_dir():
        return 0
    return len(sorted(gate_dir.glob("*.json")))


def _coerce_decision_card(decision_card: Mapping[str, Any] | BaseModel) -> dict[str, Any]:
    if isinstance(decision_card, BaseModel):
        return decision_card.model_dump(mode="json")
    return dict(decision_card)


def load_turn(path: Path) -> dict[str, Any]:
    """Load a turn JSON file, defaulting missing schema version with a warning."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "_schema_version" not in payload:
        LOGGER.warning(
            "conversation turn %s missing _schema_version; defaulting to %s",
            path,
            SCHEMA_VERSION,
        )
        payload["_schema_version"] = SCHEMA_VERSION
    return payload


def write_turn(
    *,
    trial_id: str,
    gate_id: str,
    decision_card: Mapping[str, Any] | BaseModel,
    free_text_rationale: str,
    operator_id: str,
    runs_root: Path,
    timestamp_utc: datetime | None = None,
) -> Path:
    """Persist one structured operator turn under ``conversation/<gate_id>``."""
    timestamp = timestamp_utc or datetime.now(UTC)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    timestamp_text = timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z")
    card_payload = _coerce_decision_card(decision_card)
    previous_digest = latest_turn_digest(trial_id, runs_root)
    prior_digest = previous_digest or directive_digest(trial_id, runs_root)
    turn_index = _next_turn_index(trial_id, gate_id, runs_root)
    digest = compute_turn_digest(
        prior_envelope_digest=prior_digest,
        decision_card=card_payload,
        timestamp_utc=timestamp_text,
        operator_id=operator_id,
    )
    payload = {
        "_schema_version": SCHEMA_VERSION,
        "trial_id": trial_id,
        "gate_id": gate_id,
        "turn_index": turn_index,
        "timestamp_utc": timestamp_text,
        "operator_id": operator_id,
        "decision_card": card_payload,
        "free_text_rationale": free_text_rationale,
        "prior_envelope_digest": prior_digest,
        "digest": digest,
    }
    target_dir = _gate_dir(trial_id, gate_id, runs_root)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{turn_index:04d}.json"
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def verify_chain(trial_id: str, runs_root: Path) -> bool:
    """Verify all persisted conversation turns for a trial."""
    expected_prior = directive_digest(trial_id, runs_root)
    for path in ordered_turn_files(trial_id, runs_root):
        payload = load_turn(path)
        try:
            prior = payload["prior_envelope_digest"]
            decision_card = payload["decision_card"]
            timestamp_utc = payload["timestamp_utc"]
            operator_id = payload["operator_id"]
            stored_digest = payload["digest"]
        except KeyError as exc:
            raise ConversationChainBrokenError(
                f"turn {path} missing required field {exc.args[0]!r}"
            ) from exc
        if prior != expected_prior:
            raise ConversationChainBrokenError(
                f"turn {path} prior digest mismatch: expected {expected_prior}, got {prior}"
            )
        recomputed = compute_turn_digest(
            prior_envelope_digest=prior,
            decision_card=decision_card,
            timestamp_utc=str(timestamp_utc),
            operator_id=str(operator_id),
        )
        if stored_digest != recomputed:
            raise ConversationChainBrokenError(
                f"turn {path} digest mismatch: expected {recomputed}, got {stored_digest}"
            )
        expected_prior = str(stored_digest)
    return True


__all__ = [
    "ConversationChainBrokenError",
    "SCHEMA_VERSION",
    "canonical_json_bytes",
    "compute_turn_digest",
    "directive_digest",
    "latest_turn_digest",
    "load_turn",
    "ordered_turn_files",
    "verify_chain",
    "write_turn",
]
