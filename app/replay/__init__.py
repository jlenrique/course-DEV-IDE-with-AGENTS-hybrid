"""Replay regression helpers for migration acceptance."""

from importlib import import_module

from app.replay.discovery import (
    TrialRef,
    get_closed_trial,
    list_closed_trials,
    list_legacy_run_artifacts,
)
from app.replay.regression import (
    ManifestSnapshotDriftError,
    NoClosedTrialsDiscoveredError,
    PackHashDriftError,
    ReplayBatchResult,
    ReplayBudgetExceeded,
    ReplayError,
    ReplayTrialResult,
    SanctumFingerprintDriftError,
    replay_all_closed_trials,
    replay_trial,
)

_PARITY_EXPORT_NAMES = {
    "ArtifactParityResult",
    "DEFAULT_BASELINE_ENVELOPE_PATH",
    "DEFAULT_CLONE_RUN_ROOT",
    "DEFAULT_PRIMARY_BUNDLE_ROOT",
    "ParityComparisonReport",
    "compare_actual_substrate_parity",
    "render_parity_evidence_markdown",
    "write_parity_evidence_markdown",
}


def __getattr__(name: str):
    if name in _PARITY_EXPORT_NAMES:
        module = import_module("app.replay.parity_comparison")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ArtifactParityResult",
    "DEFAULT_BASELINE_ENVELOPE_PATH",
    "DEFAULT_CLONE_RUN_ROOT",
    "DEFAULT_PRIMARY_BUNDLE_ROOT",
    "ManifestSnapshotDriftError",
    "NoClosedTrialsDiscoveredError",
    "ParityComparisonReport",
    "PackHashDriftError",
    "ReplayBatchResult",
    "ReplayBudgetExceeded",
    "ReplayError",
    "ReplayTrialResult",
    "SanctumFingerprintDriftError",
    "TrialRef",
    "compare_actual_substrate_parity",
    "get_closed_trial",
    "list_closed_trials",
    "list_legacy_run_artifacts",
    "render_parity_evidence_markdown",
    "replay_all_closed_trials",
    "replay_trial",
    "write_parity_evidence_markdown",
]
