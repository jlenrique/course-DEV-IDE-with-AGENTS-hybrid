from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.marcus.orchestrator import conversation_persistence as cp

TRIAL_ID = "12345678-1234-4234-8234-123456789abc"


def test_turn_json_carries_schema_version(tmp_path: Path) -> None:
    (tmp_path / TRIAL_ID).mkdir()
    (tmp_path / TRIAL_ID / "directive.yaml").write_text("trial: test\n", encoding="utf-8")

    path = cp.write_turn(
        trial_id=TRIAL_ID,
        gate_id="G1",
        decision_card={
            "decision": "confirm",
            "directive": "accept-as-is",
            "rationale": "The evidence is complete enough.",
            "confidence": 0.9,
            "confidence_signals": ["complete"],
        },
        free_text_rationale="operator prose",
        operator_id="operator_test",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, tzinfo=UTC),
    )

    assert json.loads(path.read_text(encoding="utf-8"))["_schema_version"] == "1.0"


def test_loader_defaults_missing_schema_version_with_warning(tmp_path: Path, caplog) -> None:
    path = tmp_path / "0000.json"
    path.write_text('{"trial_id": "trial"}', encoding="utf-8")

    payload = cp.load_turn(path)

    assert payload["_schema_version"] == "1.0"
    assert "missing _schema_version" in caplog.text
