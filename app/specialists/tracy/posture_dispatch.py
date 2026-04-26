"""Tracy posture-dispatch wrapper (bounded no-op trail-tag emitter for 2b.5)."""

from __future__ import annotations

from pathlib import Path

import yaml

from skills.bmad_agent_tracy.scripts import posture_dispatcher as _posture_dispatcher_module

REPO_ROOT = Path(__file__).resolve().parents[3]
VOCAB_PATH = REPO_ROOT / "skills" / "bmad_agent_tracy" / "references" / "vocabulary.yaml"


def _load_valid_intent_classes(path: Path = VOCAB_PATH) -> frozenset[str]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    intent = payload.get("intent_class") or {}
    day_1_values = intent.get("day_1_values") or {}
    if not isinstance(day_1_values, dict):
        return frozenset()
    return frozenset(str(key) for key in day_1_values)


_VALID_INTENT_CLASSES: frozenset[str] = _load_valid_intent_classes()
POSTURE_DISPATCHER_SEAM = _posture_dispatcher_module


def record_posture_selection(intent_class: str) -> str:
    """Return a normalized posture-selection trail tag for the selected intent class."""
    normalized = str(intent_class).strip()
    if normalized not in _VALID_INTENT_CLASSES:
        raise ValueError(f"unknown tracy intent_class: {normalized!r}")
    return f"posture.selected:{normalized}"


__all__ = ["POSTURE_DISPATCHER_SEAM", "_VALID_INTENT_CLASSES", "record_posture_selection"]
