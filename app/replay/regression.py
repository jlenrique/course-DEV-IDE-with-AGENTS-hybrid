"""Trial-replay regression harness for Slab 5a acceptance."""

from __future__ import annotations

import argparse
import json
import sys
import time
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from app.replay.discovery import TrialRef, get_closed_trial, list_closed_trials
from app.runtime.compiled_graph_digest import compute_compiled_graph_digest
from app.marcus.orchestrator.m3_trial import run_local_m3_trial

ReplayMode = Literal["fail-loud", "warn-on-clone"]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FROZEN_MANIFEST_PATH = _REPO_ROOT / "runtime" / "graphs" / "v42" / "manifest-snapshot.yaml"
_FROZEN_DISPATCH_REGISTRY_PATH = (
    _REPO_ROOT / "runtime" / "graphs" / "v42" / "dispatch-registry-snapshot.yaml"
)
_FROZEN_DIGEST_PATH = _REPO_ROOT / "runtime" / "graphs" / "v42" / "compiled-graph-digest.txt"
_DEFAULT_BUDGET_SECONDS = 15 * 60


class ReplayError(RuntimeError):
    """Base replay error."""

    def __init__(
        self,
        trial_id: str,
        message: str,
        *,
        expected: str | None = None,
        actual: str | None = None,
    ) -> None:
        super().__init__(message)
        self.trial_id = trial_id
        self.expected = expected
        self.actual = actual


class PackHashDriftError(ReplayError):
    """Raised when the replay pack hash drifts."""


class SanctumFingerprintDriftError(ReplayError):
    """Raised when the live sanctum digest drifts in fail-loud mode."""


class ManifestSnapshotDriftError(ReplayError):
    """Raised when the live manifest/dispatch digest drifts from frozen v42."""


class ReplayBudgetExceededError(ReplayError):
    """Raised when a replay exceeds the wall-clock budget."""


class NoClosedTrialsDiscoveredError(ReplayError):
    """Raised when replay discovery returns zero closed trials."""


ReplayBudgetExceeded = ReplayBudgetExceededError


@dataclass(frozen=True, slots=True)
class ReplayTrialResult:
    trial_id: str
    mode: ReplayMode
    source_kind: str
    pack_hash: str
    expected_pack_hash: str
    manifest_digest: str
    expected_manifest_digest: str
    elapsed_seconds: float
    normalized_for_clone: bool
    provenance_log: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReplayBatchResult:
    trial_ids: tuple[str, ...]
    passed_count: int
    total_count: int
    total_elapsed_seconds: float
    results: tuple[ReplayTrialResult, ...]


def _canonical_json_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return __import__("hashlib").sha256(encoded).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not deserialize to a mapping")
    return payload


def _load_baseline_payload(ref: TrialRef) -> dict[str, Any]:
    return _load_json(ref.envelope_path)


def _compute_live_manifest_digest() -> str:
    return compute_compiled_graph_digest(
        _FROZEN_MANIFEST_PATH,
        pack_version="v4.2",
        dispatch_registry_snapshot=_FROZEN_DISPATCH_REGISTRY_PATH,
    )


def _load_expected_manifest_digest() -> str:
    return _FROZEN_DIGEST_PATH.read_text(encoding="utf-8").strip()


def _normalize_clone_sanctum(payload: dict[str, Any], expected_sha: str) -> dict[str, Any]:
    normalized = deepcopy(payload)
    run_state = normalized.get("run_state")
    if not isinstance(run_state, dict):
        return normalized
    sanctum = run_state.get("sanctum_fingerprint")
    if isinstance(sanctum, dict):
        sanctum["content_sha256"] = expected_sha
    marcus_fingerprint = run_state.get("marcus_fingerprint")
    if (
        isinstance(marcus_fingerprint, list)
        and marcus_fingerprint
        and isinstance(marcus_fingerprint[0], str)
    ):
        marcus_fingerprint[0] = expected_sha
    return normalized


def _project_replay_payload(payload: dict[str, Any]) -> dict[str, Any]:
    run_state = payload["run_state"]
    gate_events = payload.get("gate_events", [])
    ledger_events = payload.get("ledger_events", [])
    projected: dict[str, Any] = {
        "schema_version": payload["schema_version"],
        "trial_id": payload["trial_id"],
        "preset": payload["preset"],
        "corpus_path": payload["corpus_path"],
        "steps_completed": payload["steps_completed"],
        "gate_events": [],
        "downstream_payloads": payload["downstream_payloads"],
        "ledger_events": [],
        "override_warning": None,
        "override_event": None,
        "run_state": {
            "status": run_state["status"],
            "graph_version": run_state["graph_version"],
            "temperature": run_state["temperature"],
            "model_resolution_trail": run_state["model_resolution_trail"],
            "model_overrides": run_state["model_overrides"],
            "sanctum_fingerprint": {
                "content_sha256": run_state["sanctum_fingerprint"]["content_sha256"],
            },
            "marcus_fingerprint": [run_state["marcus_fingerprint"][0]],
            "story_states": run_state["story_states"],
            "cache_state": {
                "cache_prefix": run_state["cache_state"]["cache_prefix"],
                "entries_count": run_state["cache_state"]["entries_count"],
            },
        },
    }

    for gate in gate_events:
        meta = gate["decision_card_meta"]
        projected["gate_events"].append(
            {
                "gate_id": gate["gate_id"],
                "node_id": gate["node_id"],
                "verdict_verb": gate["verdict_verb"],
                "decision_card_meta": {
                    "cache_state": meta["cache_state"],
                    "affected_nodes": meta["affected_nodes"],
                    "override_trail": [
                        {
                            "node_id": item["node_id"],
                            "previous_value": item["previous_value"],
                            "new_value": item["new_value"],
                            "operator_id": item["operator_id"],
                            "confirm_token": item["confirm_token"],
                        }
                        for item in meta.get("override_trail", [])
                    ],
                    "reject_rate": meta.get("reject_rate", 0.0),
                },
                "resume_payload": {
                    key: value
                    for key, value in gate["resume_payload"].items()
                    if key not in {"card_id", "verdict_id", "timestamp"}
                },
            }
        )

    for event in ledger_events:
        if event.get("kind") == "override" and event.get("operator_id") == "system":
            continue
        projected["ledger_events"].append(
            {
                key: value
                for key, value in event.items()
                if key not in {"event_id", "created_at", "gate_id", "phase"}
            }
        )

    override_warning = payload.get("override_warning")
    if isinstance(override_warning, dict):
        projected["override_warning"] = {
            "trial_id": override_warning["trial_id"],
            "node_id": override_warning["node_id"],
            "requested_model": override_warning["requested_model"],
            "current_model": override_warning["current_model"],
            "estimated_cost_delta_usd": override_warning["estimated_cost_delta_usd"],
            "affected_nodes": override_warning["affected_nodes"],
            "cache_state_delta": override_warning["cache_state_delta"],
            "confirm_token": override_warning["confirm_token"],
        }

    override_event = payload.get("override_event")
    if isinstance(override_event, dict):
        projected["override_event"] = {
            "node_id": override_event["node_id"],
            "previous_value": override_event["previous_value"],
            "new_value": override_event["new_value"],
            "operator_id": override_event["operator_id"],
            "confirm_token": override_event["confirm_token"],
        }

    return projected


def _capture_trial_payload(ref: TrialRef) -> dict[str, Any]:
    if ref.source_kind != "marcus_baseline":
        raise ValueError(f"unsupported replay source_kind: {ref.source_kind}")
    return run_local_m3_trial().model_dump(mode="json")


def _resolve_trial_ref(trial: TrialRef | str) -> TrialRef:
    return trial if isinstance(trial, TrialRef) else get_closed_trial(trial)


def replay_trial(
    trial: TrialRef | str,
    *,
    mode: ReplayMode = "fail-loud",
    budget_seconds: float = _DEFAULT_BUDGET_SECONDS,
) -> ReplayTrialResult:
    """Replay one closed trial and compare its canonical pack hash."""
    ref = _resolve_trial_ref(trial)
    started = time.perf_counter()

    expected_manifest_digest = _load_expected_manifest_digest()
    manifest_digest = _compute_live_manifest_digest()
    if manifest_digest != expected_manifest_digest:
        raise ManifestSnapshotDriftError(
            ref.trial_id,
            (
                f"manifest snapshot drift for trial_id={ref.trial_id}: "
                f"expected {expected_manifest_digest}, got {manifest_digest}"
            ),
            expected=expected_manifest_digest,
            actual=manifest_digest,
        )

    baseline_payload = _load_baseline_payload(ref)
    baseline_projected = _project_replay_payload(baseline_payload)
    expected_pack_hash = _canonical_json_hash(baseline_projected)

    current_payload = _capture_trial_payload(ref)
    current_sanctum_sha = current_payload["run_state"]["sanctum_fingerprint"]["content_sha256"]
    provenance_log: list[str] = []
    normalized_for_clone = False
    if current_sanctum_sha != ref.expected_sanctum_sha256:
        if mode == "fail-loud":
            raise SanctumFingerprintDriftError(
                ref.trial_id,
                (
                    f"sanctum fingerprint drift for trial_id={ref.trial_id}: "
                    f"expected {ref.expected_sanctum_sha256}, got {current_sanctum_sha}"
                ),
                expected=ref.expected_sanctum_sha256,
                actual=current_sanctum_sha,
            )
        current_payload = _normalize_clone_sanctum(current_payload, ref.expected_sanctum_sha256)
        normalized_for_clone = True
        provenance_log.append(
            "warn-on-clone applied D1 snapshot fallback: "
            f"captured sanctum {ref.expected_sanctum_sha256} replaced live digest "
            f"{current_sanctum_sha} "
            "for replay comparison only."
        )

    current_projected = _project_replay_payload(current_payload)
    pack_hash = _canonical_json_hash(current_projected)
    if pack_hash != expected_pack_hash:
        raise PackHashDriftError(
            ref.trial_id,
            (
                f"pack hash drift for trial_id={ref.trial_id}: "
                f"expected {expected_pack_hash}, got {pack_hash}"
            ),
            expected=expected_pack_hash,
            actual=pack_hash,
        )

    elapsed_seconds = time.perf_counter() - started
    if elapsed_seconds > budget_seconds:
        raise ReplayBudgetExceededError(
            ref.trial_id,
            (
                f"replay budget exceeded for trial_id={ref.trial_id}: "
                f"{elapsed_seconds:.3f}s > {budget_seconds:.3f}s"
            ),
            expected=f"{budget_seconds:.3f}",
            actual=f"{elapsed_seconds:.3f}",
        )

    return ReplayTrialResult(
        trial_id=ref.trial_id,
        mode=mode,
        source_kind=ref.source_kind,
        pack_hash=pack_hash,
        expected_pack_hash=expected_pack_hash,
        manifest_digest=manifest_digest,
        expected_manifest_digest=expected_manifest_digest,
        elapsed_seconds=elapsed_seconds,
        normalized_for_clone=normalized_for_clone,
        provenance_log=tuple(provenance_log),
    )


def replay_all_closed_trials(
    *,
    mode: ReplayMode = "fail-loud",
    budget_seconds: float = _DEFAULT_BUDGET_SECONDS,
) -> ReplayBatchResult:
    """Replay every discovered closed trial."""
    started = time.perf_counter()
    trials = list_closed_trials()
    if not trials:
        raise NoClosedTrialsDiscoveredError(
            "all",
            (
                "replay discovery returned zero closed trials; fail-loud mode "
                "refuses to report success without replay evidence"
            ),
        )
    results = tuple(
        replay_trial(trial, mode=mode, budget_seconds=budget_seconds)
        for trial in trials
    )
    total_elapsed_seconds = time.perf_counter() - started
    return ReplayBatchResult(
        trial_ids=tuple(trial.trial_id for trial in trials),
        passed_count=len(results),
        total_count=len(trials),
        total_elapsed_seconds=total_elapsed_seconds,
        results=results,
    )


def _to_jsonable(result: ReplayTrialResult | ReplayBatchResult) -> dict[str, Any]:
    return asdict(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.replay.regression")
    parser.add_argument("--trial-id", help="Replay one discovered closed trial id.")
    parser.add_argument(
        "--mode",
        choices=("fail-loud", "warn-on-clone"),
        default="fail-loud",
        help="Replay drift policy.",
    )
    parser.add_argument(
        "--budget-seconds",
        type=float,
        default=float(_DEFAULT_BUDGET_SECONDS),
        help="Per-trial wall-clock budget.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.trial_id:
            payload = _to_jsonable(
                replay_trial(
                    args.trial_id,
                    mode=args.mode,
                    budget_seconds=args.budget_seconds,
                )
            )
        else:
            payload = _to_jsonable(
                replay_all_closed_trials(
                    mode=args.mode,
                    budget_seconds=args.budget_seconds,
                )
            )
    except ReplayError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ManifestSnapshotDriftError",
    "NoClosedTrialsDiscoveredError",
    "PackHashDriftError",
    "ReplayBatchResult",
    "ReplayBudgetExceeded",
    "ReplayBudgetExceededError",
    "ReplayError",
    "ReplayTrialResult",
    "SanctumFingerprintDriftError",
    "build_parser",
    "main",
    "replay_all_closed_trials",
    "replay_trial",
]
