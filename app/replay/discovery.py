"""Closed-trial discovery for the replay regression harness.

The current migration substrate does not yet persist a LangGraph-native catalog
of closed trial threads. Slab 5a.1 therefore discovers the migration-native
replay surface from frozen Marcus baseline fixtures and keeps legacy
``state/config/runs`` artifacts available as reference-only inputs for later
parity work instead of pretending they are checkpoint-native replays.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BASELINE_ROOT = _REPO_ROOT / "tests" / "fixtures" / "marcus" / "baseline_envelope"
_LEGACY_RUN_ROOT = _REPO_ROOT / "state" / "config" / "runs"


@dataclass(frozen=True, slots=True)
class TrialRef:
    """Replayable closed-trial reference."""

    trial_id: str
    label: str
    source_kind: Literal["marcus_baseline"]
    baseline_dir: Path
    envelope_path: Path
    metadata_path: Path
    closed_at: datetime
    expected_sanctum_sha256: str
    note: str


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not deserialize to a mapping")
    return payload


def _as_trial_ref(baseline_dir: Path) -> TrialRef | None:
    envelope_path = baseline_dir / "envelope.json"
    metadata_path = baseline_dir / "BASELINE_METADATA.md"
    if not envelope_path.is_file() or not metadata_path.is_file():
        return None

    envelope = _load_json(envelope_path)
    run_state = envelope.get("run_state")
    if not isinstance(run_state, dict) or run_state.get("status") != "complete":
        return None

    completed_at_raw = run_state.get("completed_at")
    sanctum = run_state.get("sanctum_fingerprint")
    if not isinstance(completed_at_raw, str) or not isinstance(sanctum, dict):
        return None

    expected_sanctum_sha256 = sanctum.get("content_sha256")
    if not isinstance(expected_sanctum_sha256, str):
        return None

    return TrialRef(
        trial_id=str(envelope["trial_id"]),
        label=baseline_dir.name,
        source_kind="marcus_baseline",
        baseline_dir=baseline_dir,
        envelope_path=envelope_path,
        metadata_path=metadata_path,
        closed_at=datetime.fromisoformat(completed_at_raw.replace("Z", "+00:00")),
        expected_sanctum_sha256=expected_sanctum_sha256,
        note=(
            "Migration-native Marcus baseline captured at Slab 3 close. "
            "Legacy state/config/runs bundles remain parity/reference inputs "
            "and are intentionally excluded from replay discovery until they "
            "gain checkpoint-native baselines."
        ),
    )


def list_closed_trials() -> list[TrialRef]:
    """Return every replayable migration-native closed trial."""
    if not _BASELINE_ROOT.is_dir():
        return []

    discovered: list[TrialRef] = []
    for baseline_dir in sorted(path for path in _BASELINE_ROOT.iterdir() if path.is_dir()):
        ref = _as_trial_ref(baseline_dir)
        if ref is not None:
            discovered.append(ref)
    return sorted(discovered, key=lambda ref: (ref.closed_at, ref.trial_id))


def get_closed_trial(trial_id: str) -> TrialRef:
    """Return one replayable trial by id or raise."""
    for ref in list_closed_trials():
        if ref.trial_id == trial_id:
            return ref
    raise KeyError(f"replayable closed trial not found: {trial_id}")


def list_legacy_run_artifacts() -> list[Path]:
    """Return legacy run-artifact directories for parity/reference workflows."""
    if not _LEGACY_RUN_ROOT.is_dir():
        return []
    return sorted(path for path in _LEGACY_RUN_ROOT.iterdir() if path.is_dir())


__all__ = [
    "TrialRef",
    "get_closed_trial",
    "list_closed_trials",
    "list_legacy_run_artifacts",
]
