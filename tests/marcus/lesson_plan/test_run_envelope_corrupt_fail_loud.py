"""Mine-next N6 — corrupt run.json fails loud; absent returns None."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.lesson_plan.workbook_enrichment import (
    RunEnvelopeCorruptError,
    load_run_envelope,
)


def test_absent_run_json_returns_none(tmp_path: Path) -> None:
    assert load_run_envelope(tmp_path) is None


def test_corrupt_json_raises_run_envelope_corrupt_error(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(RunEnvelopeCorruptError, match="corrupt"):
        load_run_envelope(tmp_path)


def test_invalid_schema_raises_run_envelope_corrupt_error(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text(
        '{"status": "completed", "not_a_trial_envelope": true}\n',
        encoding="utf-8",
    )
    with pytest.raises(RunEnvelopeCorruptError, match="corrupt"):
        load_run_envelope(tmp_path)


def test_empty_file_raises_run_envelope_corrupt_error(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text("", encoding="utf-8")
    with pytest.raises(RunEnvelopeCorruptError):
        load_run_envelope(tmp_path)
