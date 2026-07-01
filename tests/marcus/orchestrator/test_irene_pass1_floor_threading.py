"""Leg-C AC#3 — orchestrator threads scripted.min_cluster_floor to irene-pass1.

RED-first: ``_runner_payload_for_specialist`` returns None for ``irene-pass1``
today. These pin:

- a directive binding a styleguide whose ``scripted.min_cluster_floor = N`` ->
  ``{"min_cluster_floor": N}``;
- absent styleguide / absent scripted -> no key (None), no crash, no None-leak;
- the orchestrator reads the SSOT yaml DIRECTLY (mirroring
  ``_gamma_settings_from_directive``) and NEVER imports ``app/specialists/gary``;
- multi-variant binding -> the strictest (max) declared floor.

Hermetic: temp SSOT + temp directive, no network.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.production_runner import (
    _SCRIPTED_MIN_CLUSTER_FLOOR_CLASS,
    _runner_payload_for_specialist,
    _scripted_min_cluster_floor_for_record,
)


def _write_ssot(tmp_path: Path, guides: dict) -> Path:
    ssot = tmp_path / "gamma-style-guides.yaml"
    ssot.write_text(yaml.safe_dump({"style_guides": guides}), encoding="utf-8")
    return ssot


def _write_directive(tmp_path: Path, gamma_settings: list[dict]) -> Path:
    directive = tmp_path / "directive.yaml"
    directive.write_text(yaml.safe_dump({"gamma_settings": gamma_settings}), encoding="utf-8")
    return directive


def _floor_guide(value: int) -> dict:
    return {
        "production_mode": "api",
        "scripted": [
            {
                "class": "min_cluster_floor",
                "value": value,
                "rationale": "multi-beat walk",
                "provenance": {"authoring_styleguide": "x", "envelope_write_stamp": "z"},
            }
        ],
    }


def test_bound_floor_is_threaded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ssot = _write_ssot(tmp_path, {"multi-beat": _floor_guide(5)})
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = _write_directive(tmp_path, [{"variant_id": "A", "styleguide": "multi-beat"}])

    payload = _runner_payload_for_specialist(
        specialist_id="irene-pass1", directive_path=directive, bundle_dir=None
    )
    assert payload == {"min_cluster_floor": 5}


def test_absent_styleguide_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ssot = _write_ssot(tmp_path, {"multi-beat": _floor_guide(5)})
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = _write_directive(tmp_path, [{"variant_id": "A"}])  # no styleguide bound

    payload = _runner_payload_for_specialist(
        specialist_id="irene-pass1", directive_path=directive, bundle_dir=None
    )
    assert payload is None


def test_styleguide_without_scripted_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ssot = _write_ssot(tmp_path, {"plain": {"production_mode": "api"}})
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = _write_directive(tmp_path, [{"variant_id": "A", "styleguide": "plain"}])

    payload = _runner_payload_for_specialist(
        specialist_id="irene-pass1", directive_path=directive, bundle_dir=None
    )
    assert payload is None


def test_no_directive_returns_none() -> None:
    assert (
        _runner_payload_for_specialist(
            specialist_id="irene-pass1", directive_path=None, bundle_dir=None
        )
        is None
    )


def test_multi_variant_uses_strictest_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ssot = _write_ssot(
        tmp_path, {"low": _floor_guide(2), "high": _floor_guide(6)}
    )
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = _write_directive(
        tmp_path,
        [
            {"variant_id": "A", "styleguide": "low"},
            {"variant_id": "B", "styleguide": "high"},
        ],
    )

    payload = _runner_payload_for_specialist(
        specialist_id="irene-pass1", directive_path=directive, bundle_dir=None
    )
    assert payload == {"min_cluster_floor": 6}


# --------------------------------------------------------------------- P7 (review)
def test_present_but_malformed_floor_warns_not_silent(caplog: pytest.LogCaptureFixture) -> None:
    """P7: a PRESENT-but-invalid floor (non-int/0/negative) must surface a loud
    signal (WARN), not silently return ``None`` as if absent."""
    record = {
        "scripted": [
            {
                "class": "min_cluster_floor",
                "value": 0,  # malformed: not a positive int
                "rationale": "x",
                "provenance": {"authoring_styleguide": "x", "envelope_write_stamp": "z"},
            }
        ]
    }
    with caplog.at_level(logging.WARNING, logger=production_runner.LOGGER.name):
        result = _scripted_min_cluster_floor_for_record(record)
    assert result is None
    assert any("min_cluster_floor" in r.message for r in caplog.records), caplog.records


def test_absent_floor_is_clean_none_no_warn(caplog: pytest.LogCaptureFixture) -> None:
    """P7 control: an ABSENT scripted/floor stays a clean ``None`` with NO warning."""
    with caplog.at_level(logging.WARNING, logger=production_runner.LOGGER.name):
        result = _scripted_min_cluster_floor_for_record({"production_mode": "api"})
    assert result is None
    assert not any("min_cluster_floor" in r.message for r in caplog.records), caplog.records


# --------------------------------------------------------------------- P8 (review)
def test_orchestrator_scripted_class_literal_parity() -> None:
    """P8: the orchestrator's LOCAL literal must stay in the sealed registry AND its
    value-validation must match the gary accessor / validator rule (guards drift
    across the deliberate import-boundary duplication)."""
    from app.specialists.gary.styleguide_library import (
        SCRIPTED_ENUM_CLASSES,
        resolve_scripted,
    )

    # (a) class-name parity
    assert _SCRIPTED_MIN_CLUSTER_FLOOR_CLASS in SCRIPTED_ENUM_CLASSES

    # (b) value-rule parity: for each candidate value the orchestrator reader and the
    # gary accessor must AGREE on accept (int returned) vs reject (None / raise).
    def _guide(value: object) -> dict:
        return {
            "scripted": [
                {
                    "class": "min_cluster_floor",
                    "value": value,
                    "rationale": "x",
                    "provenance": {"authoring_styleguide": "x", "envelope_write_stamp": "z"},
                }
            ]
        }

    from app.specialists.gary.styleguide_library import StyleguideError

    for value in (5, 1, 0, -1, True, "3", 2.5):
        orch = _scripted_min_cluster_floor_for_record(_guide(value))
        try:
            acc = resolve_scripted(_guide(value), "min_cluster_floor")
            acc_accepted = acc is not None
        except StyleguideError:
            acc_accepted = False
        orch_accepted = orch is not None
        assert orch_accepted == acc_accepted, (
            f"parity drift on value={value!r}: orchestrator accepted={orch_accepted} "
            f"vs accessor accepted={acc_accepted}"
        )
