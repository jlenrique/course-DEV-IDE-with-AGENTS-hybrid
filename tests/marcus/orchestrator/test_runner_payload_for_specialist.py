"""Leg-2 (concierge-production-substrate): kira runner-payload isolation.

Pins the DECOUPLED contract of ``_runner_payload_for_specialist`` for the
``kira`` (07E) specialist:

- The run-scoped ``bundle_path`` (per-run isolation invariant) is threaded
  UNCONDITIONALLY whenever ``runs_root`` and ``trial_id`` are present — so kira
  can NEVER silently fall back to the process-global
  ``DEFAULT_BUNDLE_PATH = REPO_ROOT/runs/kira-motion`` (which cross-contaminates
  concurrent real SPOC runs' motion/ receipts + downloaded .mp4s).
- The ``motion_plan_path`` seed/replay override is threaded ONLY when the
  ``KIRA_MOTION_PLAN_PATH`` env is set (vestigial now that 07D.5 landed, but
  preserved — regression pin).
- A non-run caller (``runs_root`` / ``trial_id`` None) still gets ``None`` and
  NEVER a global re-default (fail-loud precondition).
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist
from app.specialists.kira._act import DEFAULT_BUNDLE_PATH

TRIAL_ID = UUID("abcdef00-1234-4234-8234-abcdef012345")
TRIAL_ID_B = UUID("abcdef00-1234-4234-8234-abcdef019999")


def test_kira_bundle_path_run_scoped_when_env_unset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env UNSET + runs_root/trial_id present → run-scoped bundle_path, NOT global."""
    monkeypatch.delenv("KIRA_MOTION_PLAN_PATH", raising=False)
    runs_root = tmp_path

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID,
    )

    assert payload is not None
    expected = (runs_root / str(TRIAL_ID)).as_posix()
    assert payload["bundle_path"] == expected
    # Must NOT be the process-global collision dir on any walk.
    assert payload["bundle_path"] != DEFAULT_BUNDLE_PATH.as_posix()
    assert "runs/kira-motion" not in payload["bundle_path"]
    # No seed override when the env is unset.
    assert "motion_plan_path" not in payload


def test_kira_env_set_threads_both_motion_plan_and_run_scoped_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env SET → BOTH motion_plan_path AND run-scoped bundle_path (seed/replay pin)."""
    seed_plan = tmp_path / "seed" / "motion_plan.yaml"
    monkeypatch.setenv("KIRA_MOTION_PLAN_PATH", str(seed_plan))
    runs_root = tmp_path

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID,
    )

    assert payload is not None
    assert payload["motion_plan_path"] == str(seed_plan)
    assert payload["bundle_path"] == (runs_root / str(TRIAL_ID)).as_posix()
    assert payload["bundle_path"] != DEFAULT_BUNDLE_PATH.as_posix()


def test_kira_non_run_caller_returns_none_no_global_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """runs_root None (non-run caller) → None; NEVER a silent global re-default."""
    monkeypatch.delenv("KIRA_MOTION_PLAN_PATH", raising=False)

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=None,
        trial_id=None,
    )

    assert payload is None


def test_kira_env_set_but_no_runs_root_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even with the seed env set, a non-run caller gets None (precondition holds)."""
    monkeypatch.setenv("KIRA_MOTION_PLAN_PATH", str(tmp_path / "motion_plan.yaml"))

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=None,
        trial_id=None,
    )

    assert payload is None


def test_kira_distinct_trial_ids_yield_distinct_bundle_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SHOULD-FIX (per-run isolation pin): two DISTINCT trial_ids under the SAME
    runs_root MUST yield two DISTINCT bundle_paths, each containing its OWN
    trial_id.

    This is the invariant the whole Leg-2 change exists to protect: kira's
    motion/ receipts + downloaded .mp4s are rooted per-run so concurrent real
    SPOC runs never cross-contaminate. A future refactor that derived
    bundle_path from ``runs_root`` alone (dropping the ``/ str(trial_id)``
    segment) would collide both runs into one dir — and MUST fail here.
    """
    monkeypatch.delenv("KIRA_MOTION_PLAN_PATH", raising=False)
    runs_root = tmp_path

    payload_a = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID,
    )
    payload_b = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID_B,
    )

    assert payload_a is not None
    assert payload_b is not None
    # Distinct runs → distinct bundle roots (no collision under one runs_root).
    assert payload_a["bundle_path"] != payload_b["bundle_path"]
    # Each root carries its OWN trial_id (proves per-run derivation, not
    # runs_root-alone).
    assert str(TRIAL_ID) in payload_a["bundle_path"]
    assert str(TRIAL_ID_B) in payload_b["bundle_path"]
    assert str(TRIAL_ID_B) not in payload_a["bundle_path"]
    assert str(TRIAL_ID) not in payload_b["bundle_path"]


def test_kira_runs_root_present_trial_id_none_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SHOULD-FIX (asymmetric precondition pin — arm A): runs_root PRESENT but
    trial_id None → None.

    The precondition is ``runs_root is None or trial_id is None`` (OR, not AND).
    The both-None case is already covered; this pins the untested asymmetric arm
    so a future ``and`` typo (which would emit a broken ``runs_root/None`` bundle
    path) is caught.
    """
    monkeypatch.delenv("KIRA_MOTION_PLAN_PATH", raising=False)

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=tmp_path,
        trial_id=None,
    )

    assert payload is None


def test_kira_runs_root_none_trial_id_present_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SHOULD-FIX (asymmetric precondition pin — arm B): runs_root None but
    trial_id PRESENT → None (symmetric partner of arm A)."""
    monkeypatch.delenv("KIRA_MOTION_PLAN_PATH", raising=False)

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=None,
        bundle_dir=None,
        runs_root=None,
        trial_id=TRIAL_ID,
    )

    assert payload is None
