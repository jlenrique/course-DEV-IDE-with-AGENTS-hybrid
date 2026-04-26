from __future__ import annotations

from pathlib import Path


def test_wanda_validation_c3_row_absent_after_retirement() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    row = "app.specialists.wanda_validation.graph -> app.gates.resume_api"
    assert row not in pyproject
    assert "2c.1 retire-to-fixtures" in pyproject
