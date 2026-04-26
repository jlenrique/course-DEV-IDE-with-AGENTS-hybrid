from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.specialists.tracy.posture_dispatch import (
    _VALID_INTENT_CLASSES,
    POSTURE_DISPATCHER_SEAM,
    record_posture_selection,
)


def test_tracy_vocabulary_loaded_at_import_time() -> None:
    path = Path("skills") / "bmad_agent_tracy" / "references" / "vocabulary.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    expected = frozenset((payload.get("intent_class") or {}).get("day_1_values", {}).keys())
    assert expected == _VALID_INTENT_CLASSES


def test_record_posture_selection_emits_tag() -> None:
    assert record_posture_selection("supporting_evidence") == "posture.selected:supporting_evidence"


def test_record_posture_selection_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        record_posture_selection("unknown")


def test_tracy_wrapper_imports_upstream_posture_dispatcher_module() -> None:
    assert POSTURE_DISPATCHER_SEAM is not None
    assert hasattr(POSTURE_DISPATCHER_SEAM, "PostureDispatcher")
