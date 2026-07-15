"""Story 39.1 — probe honesty hardening pins (remediation P8).

P8a: the renderer-config identity covers every module the probe's claim rides
on (projection + producer + _act intake + the harness-side bar). P8b:
``provider_calls`` is MEASURED off the poison writer's invocation counter.
P8c: a missing frozen-evidence dir still yields an immutable attempt dir +
``verdict.json`` with ``pass=false`` (first-run-stands — never a bare
traceback). P8d: EXPECTED input digests are pinned constants and drift FAILS
(compared, not just recorded).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from scripts.utilities import run_glossary_render_39_1_probe as probe


def test_p8a_renderer_config_identity_covers_act_and_bar_modules() -> None:
    module_names = {path.name for path in probe.RENDERER_MODULES}
    assert "glossary_projection.py" in module_names
    assert "workbook_producer.py" in module_names
    assert "_act.py" in module_names
    assert "marcus_spoc_live_test_runner.py" in module_names
    for path in probe.RENDERER_MODULES:
        assert path.is_file(), f"renderer-identity module missing: {path}"


def test_p8b_poison_writer_counts_invocations_and_fails_loud() -> None:
    writer = probe._FrozenIdentityWriter(
        model_config_digest="sha256:" + "0" * 64, default_model=None
    )
    assert writer.calls == 0
    with pytest.raises(probe._PoisonDispatchError):
        writer(object())
    assert writer.calls == 1


def test_p8c_missing_frozen_inputs_writes_failed_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.setattr(probe, "FROZEN_RUN", tmp_path / "absent-frozen-run")
    monkeypatch.setattr(probe, "SOURCE_RUN", tmp_path / "absent-source-run")
    monkeypatch.setattr(probe, "EVIDENCE_ROOT", tmp_path / "evidence")
    monkeypatch.setattr(sys, "argv", ["run_glossary_render_39_1_probe.py"])
    assert probe.main() == 1
    capsys.readouterr()  # the verdict path + JSON are printed, not raised
    attempts = list((tmp_path / "evidence").glob("glossary-render-39-1-*"))
    assert len(attempts) == 1
    verdict = json.loads((attempts[0] / "verdict.json").read_text("utf-8"))
    assert verdict["pass"] is False
    assert verdict["error_type"] == "FileNotFoundError"
    assert verdict["missing_inputs"]
    # P8b: no replay leg ran, so provider_calls stays an honest ``None``
    # (never a hardcoded zero claim).
    assert verdict["provider_calls"] is None


def test_p8c_dry_run_missing_inputs_fails_without_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.setattr(probe, "FROZEN_RUN", tmp_path / "absent-frozen-run")
    monkeypatch.setattr(probe, "SOURCE_RUN", tmp_path / "absent-source-run")
    monkeypatch.setattr(
        sys, "argv", ["run_glossary_render_39_1_probe.py", "--dry-run"]
    )
    assert probe.main() == 1
    preflight = json.loads(capsys.readouterr().out)
    assert preflight["pass"] is False
    assert preflight["missing_inputs"]
    assert not list(tmp_path.glob("**/verdict.json"))  # dry-run writes nothing


def test_p8d_pinned_digests_match_frozen_inputs_on_disk() -> None:
    """Self-check: the pinned EXPECTED constants match the frozen inputs —
    a drift here means the frozen evidence was touched (fail loud)."""
    if probe._missing_inputs():
        pytest.skip("frozen probe inputs not present in this checkout")
    assert probe._digest_drift(probe._input_digests()) == {}


def test_p8d_digest_drift_fails_dry_run(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    if probe._missing_inputs():
        pytest.skip("frozen probe inputs not present in this checkout")
    pinned = dict(probe.EXPECTED_INPUT_DIGESTS)
    pinned["run.json"] = "sha256:" + "f" * 64
    monkeypatch.setattr(probe, "EXPECTED_INPUT_DIGESTS", pinned)
    monkeypatch.setattr(
        sys, "argv", ["run_glossary_render_39_1_probe.py", "--dry-run"]
    )
    assert probe.main() == 1
    preflight = json.loads(capsys.readouterr().out)
    assert preflight["pass"] is False
    assert "run.json" in preflight["input_digest_drift"]
