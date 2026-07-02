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


# ----------------------------------------------------- F1 (live-diagnosed 2026-07-01)
# An instrumented live walk proved ``_runner_payload_for_specialist`` is invoked with
# the CANONICALIZED id ``"irene_pass1"`` (underscore), not the manifest spelling: the
# manifest compiler stamps ``handler.__production_specialist_id__`` with
# ``_canonical_specialist_id(node.specialist_id)`` (``app/manifest/compiler.py:163``,
# via ``SPECIALIST_ALIASES`` ``"irene-pass1" -> "irene_pass1"``, ``compiler.py:42-45``),
# and BOTH walks read that attribute as the ``specialist_id`` they thread to the
# dispatch site (``production_runner.py:2550`` start walk / ``:3276`` continuation
# walk -> ``_dispatch_specialist_at_node`` -> ``_runner_payload_for_specialist`` at
# ``:1978``). A hyphen-only branch therefore returns None on EVERY real dispatch —
# the floor never threads (the quinn_r branch learned the identical lesson on
# 2026-06-11).
def test_bound_floor_is_threaded_for_canonical_underscore_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED against the hyphen-only branch: the CANONICALIZED id must thread the floor."""
    ssot = _write_ssot(tmp_path, {"multi-beat": _floor_guide(5)})
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = _write_directive(tmp_path, [{"variant_id": "A", "styleguide": "multi-beat"}])

    payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1", directive_path=directive, bundle_dir=None
    )
    assert payload == {"min_cluster_floor": 5}


def test_walk_call_site_id_form_is_accepted_by_floor_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parity pin: whichever id form the walk ACTUALLY passes must thread the floor.

    The walk's id is ``_canonical_specialist_id(<manifest spelling>)`` (that is what
    the compiler stamps on ``__production_specialist_id__`` and what
    ``production_runner.py:2550``/``:3276`` pass down) — computed HERE from the same
    alias table, so a future SPECIALIST_ALIASES change that re-spells the canonical
    id re-fails this test loudly instead of silently un-threading the floor again.
    """
    from app.manifest.compiler import _canonical_specialist_id

    walk_id = _canonical_specialist_id("irene-pass1")
    assert walk_id is not None
    ssot = _write_ssot(tmp_path, {"multi-beat": _floor_guide(5)})
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = _write_directive(tmp_path, [{"variant_id": "A", "styleguide": "multi-beat"}])

    payload = _runner_payload_for_specialist(
        specialist_id=walk_id, directive_path=directive, bundle_dir=None
    )
    assert payload == {"min_cluster_floor": 5}


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
