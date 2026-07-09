"""S5-3b — the G0-enrichment DEFAULT FLIP truth-table contract (AC-1, F-1802).

``g0_enrichment_active()`` post-3b is DEFAULT-ON: it ENUMERATES the falsy
kill-switch set ``{"0","false","no","off"}`` (stripped/lowered) → False and
DEFAULTS EVERYTHING ELSE → True. Implemented as ``value not in KILL_SWITCH``
(NOT ``value not in TRUTHY`` — that would wrongly wake on the ``"0"`` kill-switch
and break every 3a ``setenv("0")`` pin). ``irene_refinement_active()`` (G0R)
delegates to the same predicate, so one env wakes both gates.

``g0_dispatch_live()`` STAYS default-OFF (party-ratified Reading A / D4): the
canonical default path wakes the HIL gates + the deterministic recorded
enrichment but never spends. The resolved enrichment mode is stamped
FAIL-LOUD from the result model_id.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.orchestrator import g0_enrichment_wiring as gw
from app.marcus.orchestrator import irene_refinement_wiring as iw

ENV = gw.G0_ENRICHMENT_ACTIVE_ENV
REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS = REPO_ROOT / "course-content" / "courses" / "studio-smoke-min"


# --------------------------------------------------------------------------- #
# AC-1 — the truth-table CONTRACT (default-ON; explicit-falsy kill-switch)
# --------------------------------------------------------------------------- #


def test_ac_1_unset_defaults_active(monkeypatch) -> None:
    """The CANONICAL (unset-env) run wakes G0E — the whole point of the 3b flip."""
    monkeypatch.delenv(ENV, raising=False)
    assert gw.g0_enrichment_active() is True


@pytest.mark.parametrize("value", ["", "   ", "\t", "\n"])
def test_ac_1_empty_and_whitespace_default_active(monkeypatch, value: str) -> None:
    """Empty / whitespace-only → True (NOT ``not in truthy_set`` which would keep OFF)."""
    monkeypatch.setenv(ENV, value)
    assert gw.g0_enrichment_active() is True


@pytest.mark.parametrize("value", ["maybe", "enabled", "2", "yep", "banana", "onoff"])
def test_ac_1_unrecognized_defaults_active(monkeypatch, value: str) -> None:
    """An UNRECOGNIZED value defaults to True (default-everything-else-ON)."""
    monkeypatch.setenv(ENV, value)
    assert gw.g0_enrichment_active() is True


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "false",
        "no",
        "off",
        "FALSE",
        "No",
        "OFF",
        "  0  ",
        "\tfalse\n",
        "Off ",
    ],
)
def test_ac_1_kill_switch_values_are_inactive(monkeypatch, value: str) -> None:
    """Each of {0,false,no,off} (+ case/whitespace variants) → False (kill-switch)."""
    monkeypatch.setenv(ENV, value)
    assert gw.g0_enrichment_active() is False


@pytest.mark.parametrize(
    "value",
    ["1", "true", "yes", "on", "TRUE", "Yes", "ON", "  1  ", "\ttrue\n", "On "],
)
def test_ac_1_explicit_truthy_values_are_active(monkeypatch, value: str) -> None:
    """Each of {1,true,yes,on} (+ case/whitespace variants) → True (explicit ON)."""
    monkeypatch.setenv(ENV, value)
    assert gw.g0_enrichment_active() is True


# --------------------------------------------------------------------------- #
# AC-1 — G0R delegation: one env wakes BOTH gates
# --------------------------------------------------------------------------- #


def test_ac_1_irene_refinement_delegates_default_on(monkeypatch) -> None:
    """UNSET default wakes G0R too (delegation), and the kill-switch silences both."""
    monkeypatch.delenv(ENV, raising=False)
    assert iw.irene_refinement_active() is True
    assert iw.irene_refinement_active() is gw.g0_enrichment_active()
    monkeypatch.setenv(ENV, "0")
    assert iw.irene_refinement_active() is False
    assert gw.g0_enrichment_active() is False


# --------------------------------------------------------------------------- #
# D4 — dispatch_live STAYS default-OFF (Reading A); mode-stamp is FAIL-LOUD
# --------------------------------------------------------------------------- #


def test_dispatch_live_stays_default_off(monkeypatch) -> None:
    """The live-LLM arm is NOT flipped by 3b — canonical default spends zero."""
    monkeypatch.delenv(gw.G0_DISPATCH_LIVE_ENV, raising=False)
    assert gw.g0_dispatch_live() is False
    # The enrichment gates are woken though (structure canonical, content armed).
    monkeypatch.delenv(ENV, raising=False)
    assert gw.g0_enrichment_active() is True


@pytest.mark.parametrize("value", ["1", "true", "yes", "on"])
def test_dispatch_live_arms_on_explicit_truthy(monkeypatch, value: str) -> None:
    monkeypatch.setenv(gw.G0_DISPATCH_LIVE_ENV, value)
    assert gw.g0_dispatch_live() is True


def test_resolve_enrichment_mode_deterministic() -> None:
    assert (
        gw.resolve_enrichment_mode(gw.G0_ENRICHMENT_MODEL_MARKER)
        == gw.G0_ENRICHMENT_MODE_DETERMINISTIC
    )


def test_resolve_enrichment_mode_live() -> None:
    assert gw.resolve_enrichment_mode(gw.G0_ENRICHMENT_LIVE_MODEL_ID) == gw.G0_ENRICHMENT_MODE_LIVE


def test_resolve_enrichment_mode_unrecognized_is_fail_loud() -> None:
    """An unrecognized model_id RAISES (never a silent mode) — the F-1801 legibility guard."""
    with pytest.raises(ValueError, match="unrecognized"):
        gw.resolve_enrichment_mode("some-unknown-model-xyz")


# --------------------------------------------------------------------------- #
# AC-6 — the receipt STAMPS the resolved mode (deterministic-recorded default)
# --------------------------------------------------------------------------- #


def test_ac_6_default_receipt_stamps_deterministic_recorded(tmp_path, monkeypatch) -> None:
    """A fake-key default run wakes G0E, spends ZERO, and emits a receipt naming the
    mode ``deterministic-recorded`` — asserted ON THE RECEIPT + the bundle contribution."""
    from app.models.runtime.production_envelope import ProductionEnvelope

    monkeypatch.delenv(gw.G0_DISPATCH_LIVE_ENV, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")  # fake key — no spend
    trial_id = UUID("62345678-1234-4234-8234-123456789abc")
    env = ProductionEnvelope(trial_id=trial_id)
    updated = gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=env,
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    # (1) the on-disk receipt
    receipt = json.loads(
        (tmp_path / str(trial_id) / "g0-enrichment.json").read_text(encoding="utf-8")
    )
    assert receipt["enrichment_mode"] == gw.G0_ENRICHMENT_MODE_DETERMINISTIC
    # (2) the bundle contribution receipt
    contribution = updated.get_contribution(
        gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
    )
    assert contribution.output["enrichment_mode"] == gw.G0_ENRICHMENT_MODE_DETERMINISTIC


# --------------------------------------------------------------------------- #
# D3 — Beats 2-3 narration + Dan's "live-available" affordance
# --------------------------------------------------------------------------- #


def _seed_receipt(run_dir: Path, mode: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "g0-enrichment.json").write_text(
        json.dumps({"enrichment_mode": mode, "typed_components": [], "provisional_los": []}),
        encoding="utf-8",
    )


def test_d3_g0e_beat2_and_affordance_on_deterministic(tmp_path) -> None:
    from app.marcus.cli import marcus_spoc as spoc

    _seed_receipt(tmp_path, gw.G0_ENRICHMENT_MODE_DETERMINISTIC)
    out = spoc.narrate_gate("G0E", {"card": {}}, tmp_path)
    assert "Beat 2 of 3" in out and "the material" in out
    assert "--g0-dispatch-live" in out  # Dan's affordance present


def test_d3_g0r_beat3_and_affordance_on_deterministic(tmp_path) -> None:
    from app.marcus.cli import marcus_spoc as spoc

    _seed_receipt(tmp_path, gw.G0_ENRICHMENT_MODE_DETERMINISTIC)
    out = spoc.narrate_gate("G0R", {"card": {"refined_los": [], "reconcile": {}}}, tmp_path)
    assert "Beat 3 of 3" in out and "the contract" in out
    assert "--g0-dispatch-live" in out
    assert "ratify" in out.lower()


def test_d3_no_affordance_when_live(tmp_path) -> None:
    """A LIVE run shows NO 'arm it' affordance (it is already live)."""
    from app.marcus.cli import marcus_spoc as spoc

    _seed_receipt(tmp_path, gw.G0_ENRICHMENT_MODE_LIVE)
    out = spoc.narrate_gate("G0E", {"card": {}}, tmp_path)
    assert "--g0-dispatch-live" not in out


# --------------------------------------------------------------------------- #
# D4 — the first-class --g0-dispatch-live CLI flag arms MARCUS_G0_DISPATCH_LIVE
# --------------------------------------------------------------------------- #


def test_d4_cli_flag_arms_env(tmp_path, monkeypatch) -> None:
    from app.marcus.cli import marcus_spoc as spoc

    monkeypatch.delenv(gw.G0_DISPATCH_LIVE_ENV, raising=False)
    trial_id = "62345678-1234-4234-8234-123456789abd"
    # main() legitimately mutates PROCESS os.environ (it is a CLI entrypoint arming
    # the run) — monkeypatch.delenv records nothing for an already-absent key, so
    # clean up explicitly in a finally to keep the process env hermetic for the rest
    # of the serial suite (no live-dispatch leak into downstream offline tests).
    try:
        rc = spoc.main(
            ["--trial-id", trial_id, "--runs-root", str(tmp_path), "--g0-dispatch-live"]
        )
        assert rc == 0
        assert os.environ.get(gw.G0_DISPATCH_LIVE_ENV) == "1"
    finally:
        os.environ.pop(gw.G0_DISPATCH_LIVE_ENV, None)


def test_d4_cli_default_does_not_arm(tmp_path, monkeypatch) -> None:
    from app.marcus.cli import marcus_spoc as spoc

    monkeypatch.delenv(gw.G0_DISPATCH_LIVE_ENV, raising=False)
    trial_id = "62345678-1234-4234-8234-123456789abe"
    try:
        rc = spoc.main(["--trial-id", trial_id, "--runs-root", str(tmp_path)])
        assert rc == 0
        assert os.environ.get(gw.G0_DISPATCH_LIVE_ENV) is None
    finally:
        os.environ.pop(gw.G0_DISPATCH_LIVE_ENV, None)
