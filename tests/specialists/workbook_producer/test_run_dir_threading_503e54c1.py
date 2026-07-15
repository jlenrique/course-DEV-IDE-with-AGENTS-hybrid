"""07W run-dir threading regression (live trial 503e54c1, paused at 07W).

Live trial ``503e54c1-fd3c-4e26-b4fc-77ad77bf5bab`` ran under a NON-default
``--runs-root`` (``runs``) and paused at the terminal 07W producer with
``workbook_producer.segment-manifest.missing``: the storyboard publisher wrote
the segment manifest to the REAL run dir (``runs/<trial>/exports/…``) but the
producer's ``_resolve_run_dir`` fell back to the SHIPPED default root
(``RUNS_ROOT`` == ``state/config/runs``) because the runner threaded no run_dir
into the 07W payload. It then read an empty shipped-root dir and failed loud on
a manifest that DID exist under the run the trial was actually executing in.

These floors pin the fix at the dispatch seam
(``_runner_payload_for_specialist``): the ACTUAL run dir (``runs_root /
trial_id`` — the SAME coordinate the workbook band, storyboard_publisher, and
deep-dive resolve) is threaded into the 07W payload's ``run_dir`` override so
every run-dir-relative read resolves under the real run, regardless of
``--runs-root``. The ``WORKBOOK_RUN_DIR`` replay/dev override still wins.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.workbook_producer import _act as wb_act

TRIAL_ID = UUID("503e54c1-fd3c-4e26-b4fc-77ad77bf5bab")

_MANIFEST_SEGMENTS = {
    "segments": [
        {"segment_id": "seg-01", "id": "seg-01", "slide_id": "slide-01"},
        {"segment_id": "seg-02", "id": "seg-02", "slide_id": "slide-02"},
    ]
}


def _seed_state(run_id: UUID) -> RunState:
    entry = ModelResolutionEntry(
        level="per_specialist",
        requested="gpt-5-nano",
        resolved="gpt-5-nano",
        reason="seed",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        run_id=run_id,
        model_resolution_trail=[entry],
    )


def _write_manifest(run_dir: Path) -> Path:
    manifest_path = run_dir / wb_act._DEFAULT_SEGMENT_MANIFEST_RELPATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(_MANIFEST_SEGMENTS), encoding="utf-8")
    return manifest_path


def test_payload_threads_real_run_dir_under_non_default_runs_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """runs_root/trial_id present + env unset → payload carries the REAL run_dir."""
    monkeypatch.delenv("WORKBOOK_RUN_DIR", raising=False)
    runs_root = tmp_path / "runs"  # a NON-default root (not state/config/runs)

    payload = _runner_payload_for_specialist(
        specialist_id="workbook_producer",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID,
    )

    assert payload is not None
    assert payload["run_dir"] == (runs_root / str(TRIAL_ID)).as_posix()


def test_producer_resolves_segment_manifest_under_non_default_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: with the threaded payload the producer resolves the manifest;
    WITHOUT it (old behavior) it falls back to the shipped root and fails loud
    with the exact ``segment-manifest.missing`` tag the live trial hit."""
    monkeypatch.delenv("WORKBOOK_RUN_DIR", raising=False)
    runs_root = tmp_path / "runs"  # the real --runs-root the trial executes under
    real_run_dir = runs_root / str(TRIAL_ID)
    _write_manifest(real_run_dir)

    # The SHIPPED default root the un-threaded resolver would fall back to — it
    # does NOT contain this run's manifest (the exact live-trial mismatch).
    shipped_root = tmp_path / "state-config-runs"
    (shipped_root / str(TRIAL_ID)).mkdir(parents=True)
    monkeypatch.setattr(wb_act, "RUNS_ROOT", shipped_root)

    state = _seed_state(TRIAL_ID)

    # RED (old behavior — no run_dir in payload): resolves shipped_root/run_id,
    # the manifest is absent there, _load_segments fails with the live tag.
    fallback_dir = wb_act._resolve_run_dir(state, {})
    assert fallback_dir == shipped_root / str(TRIAL_ID)
    with pytest.raises(wb_act.WorkbookProducerActError) as excinfo:
        wb_act._load_segments(fallback_dir, wb_act._DEFAULT_SEGMENT_MANIFEST_RELPATH)
    assert excinfo.value.tag == "workbook-producer.segment-manifest.missing"

    # GREEN (fix): the runner threads run_dir → resolves the REAL run dir →
    # the manifest is found and segments load.
    payload = _runner_payload_for_specialist(
        specialist_id="workbook_producer",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID,
    )
    assert payload is not None
    resolved = wb_act._resolve_run_dir(state, payload)
    assert resolved == real_run_dir
    segments = wb_act._load_segments(resolved, wb_act._DEFAULT_SEGMENT_MANIFEST_RELPATH)
    assert tuple(seg.segment_id for seg in segments) == ("seg-01", "seg-02")


def test_env_override_still_wins_through_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WORKBOOK_RUN_DIR replay/dev override wins even through the runner seam."""
    override_dir = tmp_path / "replay-run"
    monkeypatch.setenv("WORKBOOK_RUN_DIR", str(override_dir))
    runs_root = tmp_path / "runs"

    payload = _runner_payload_for_specialist(
        specialist_id="workbook_producer",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=TRIAL_ID,
    )

    assert payload is not None
    assert payload["run_dir"] == str(override_dir)
    assert payload["run_dir"] != (runs_root / str(TRIAL_ID)).as_posix()


def test_non_run_caller_returns_none_no_shipped_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A non-run caller (runs_root/trial_id None) → None; never a silent default."""
    monkeypatch.delenv("WORKBOOK_RUN_DIR", raising=False)

    assert (
        _runner_payload_for_specialist(
            specialist_id="workbook_producer",
            directive_path=None,
            bundle_dir=None,
            runs_root=None,
            trial_id=None,
        )
        is None
    )
    # Asymmetric precondition arms (OR, not AND).
    assert (
        _runner_payload_for_specialist(
            specialist_id="workbook_producer",
            directive_path=None,
            bundle_dir=None,
            runs_root=Path("/tmp/runs"),
            trial_id=None,
        )
        is None
    )
    assert (
        _runner_payload_for_specialist(
            specialist_id="workbook_producer",
            directive_path=None,
            bundle_dir=None,
            runs_root=None,
            trial_id=TRIAL_ID,
        )
        is None
    )
