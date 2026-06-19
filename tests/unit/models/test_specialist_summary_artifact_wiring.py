"""S0.2 / T4-F1: specialist-summary 'Emitted artifacts' wired to the producer's
real output (bundle manifest / artifact_path), not the empty state.artifact_paths.

Trial-4: Texas wrote a real 5-artifact bundle but its summary said 'Emitted
artifacts: none', which drove G1's drafted-reject (`artifact_paths_empty`) over
genuinely-present content. The pre-gate-marcus proposal reads this summary, so
fixing the summary closes both halves of the false-negative.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from app.models.state import specialist_summary_artifacts as ssa


def _read_summary(runs_root: Path, trial_id) -> str:
    files = list(Path(runs_root).rglob("*.md"))
    assert files, "no specialist summary emitted"
    return files[0].read_text(encoding="utf-8")


def test_summary_lists_bundle_artifacts_when_state_paths_empty(tmp_path: Path) -> None:
    trial_id = uuid4()
    contrib = SimpleNamespace(
        specialist_id="texas",
        output={
            "artifacts": ["extracted.md", "manifest.json", "result.yaml"],
            "bundle_reference": "C:/repo/runs/x/bundle",
        },
    )
    state = SimpleNamespace(
        run_id=trial_id,
        cache_state=SimpleNamespace(cache_prefix='{"cache_prefix": "x"}'),
        production_envelope=SimpleNamespace(contributions=[contrib]),
        model_resolution_trail=[],
        artifact_paths=[],  # the Trial-4 false-empty
    )

    ssa.emit_summary_for_state("texas", state, runs_root=tmp_path)
    text = _read_summary(tmp_path, trial_id)

    assert "- `none`" not in text  # the Trial-4 false-negative is gone
    assert "extracted.md" in text
    assert "manifest.json" in text
    # bundle_reference is joined into the path
    assert "bundle/extracted.md" in text


def test_summary_uses_single_artifact_path(tmp_path: Path) -> None:
    trial_id = uuid4()
    contrib = SimpleNamespace(
        specialist_id="irene",
        output={"artifact_path": "C:/repo/runs/x/irene-pass1.md"},
    )
    state = SimpleNamespace(
        run_id=trial_id,
        cache_state=SimpleNamespace(cache_prefix="{}"),
        production_envelope=SimpleNamespace(contributions=[contrib]),
        model_resolution_trail=[],
        artifact_paths=[],
    )
    ssa.emit_summary_for_state("irene", state, runs_root=tmp_path)
    text = _read_summary(tmp_path, trial_id)
    assert "- `none`" not in text
    assert "irene-pass1.md" in text


def test_explicit_state_artifact_paths_still_win(tmp_path: Path) -> None:
    """When state.artifact_paths IS populated, it takes precedence (unchanged)."""
    trial_id = uuid4()
    state = SimpleNamespace(
        run_id=trial_id,
        cache_state=SimpleNamespace(cache_prefix="{}"),
        production_envelope=SimpleNamespace(contributions=[]),
        model_resolution_trail=[],
        artifact_paths=["C:/repo/explicit.md"],
    )
    ssa.emit_summary_for_state("gary", state, runs_root=tmp_path)
    text = _read_summary(tmp_path, trial_id)
    assert "explicit.md" in text


def test_no_artifacts_anywhere_still_reports_none(tmp_path: Path) -> None:
    trial_id = uuid4()
    state = SimpleNamespace(
        run_id=trial_id,
        cache_state=SimpleNamespace(cache_prefix="{}"),
        production_envelope=SimpleNamespace(contributions=[]),
        model_resolution_trail=[],
        artifact_paths=[],
    )
    ssa.emit_summary_for_state("kira", state, runs_root=tmp_path)
    text = _read_summary(tmp_path, trial_id)
    assert "- `none`" in text  # honest 'none' when nothing was emitted
