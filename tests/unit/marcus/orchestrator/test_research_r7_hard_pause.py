"""Hermetic tests for R7 research-detective hard-pause gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.orchestrator import research_detective_gate as gate
from app.marcus.orchestrator.research_wiring import RESEARCH_DETECTIVE_LIVE_ENV


@pytest.fixture(autouse=True)
def _clear_detective_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(RESEARCH_DETECTIVE_LIVE_ENV, raising=False)


def test_flag_off_is_noop(tmp_path: Path) -> None:
    # No landing / disposition required when detective is OFF.
    gate.enforce_before_pass2(
        specialist_id="irene",
        node_id="08",
        run_dir=tmp_path,
    )
    assert not gate.landing_path(tmp_path).exists()
    assert not gate.disposition_path(tmp_path).exists()


def test_non_pass2_dispatch_is_noop(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
    gate.enforce_before_pass2(
        specialist_id="irene-pass1",
        node_id="05B",
        run_dir=tmp_path,
    )
    gate.enforce_before_pass2(
        specialist_id="gary",
        node_id="08",
        run_dir=tmp_path,
    )
    assert not gate.disposition_path(tmp_path).exists()


def test_pass2_blocked_without_disposition(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "on")
    with pytest.raises(gate.ResearchDetectiveGateError, match="Pass-2 blocked") as exc:
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=tmp_path,
        )
    assert exc.value.tag == gate.GATE_PENDING_TAG
    assert gate.landing_path(tmp_path).is_file()
    landing = json.loads(gate.landing_path(tmp_path).read_text(encoding="utf-8"))
    assert landing["status"] == "awaiting_disposition"


@pytest.mark.parametrize("disposition", sorted(gate.VALID_DISPOSITIONS))
def test_valid_disposition_unlocks_pass2(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, disposition: str
) -> None:
    monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
    gate.write_landing_point(tmp_path, trial_id="t-hermetic")
    gate.write_disposition(
        tmp_path,
        disposition,
        operator_id="hermetic",
        rationale=f"state-machine unlock via {disposition}",
    )
    gate.enforce_before_pass2(
        specialist_id="irene",
        node_id="08",
        run_dir=tmp_path,
    )


def test_advisory_disposition_cannot_unlock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
    with pytest.raises(ValueError, match="advisory-only cannot unlock"):
        gate.write_disposition(tmp_path, "advisory")

    # Hand-plant an advisory receipt — still blocked.
    gate.disposition_path(tmp_path).write_text(
        json.dumps({"disposition": "advisory", "unlocks_pass2": True}),
        encoding="utf-8",
    )
    with pytest.raises(gate.ResearchDetectiveGateError, match="advisory") as exc:
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=tmp_path,
        )
    assert exc.value.tag == gate.GATE_ADVISORY_TAG


def test_state_machine_block_then_unlock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Hermetic AC sequence: landing → block → disposition → proceed."""
    monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "true")
    with pytest.raises(gate.ResearchDetectiveGateError):
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=tmp_path,
        )
    gate.write_disposition(tmp_path, "approve", rationale="operator reviewed rows")
    gate.enforce_before_pass2(
        specialist_id="irene",
        node_id="08",
        run_dir=tmp_path,
    )
