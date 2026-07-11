"""R7 research-detective hard-pause gate — teeth before Irene Pass-2.

When ``MARCUS_RESEARCH_DETECTIVE_LIVE`` is ON, Irene Pass-2 (manifest node ``08``)
must not dispatch until an operator disposition receipt is on disk with one of
``approve`` / ``reject`` / ``defer``. Advisory-only and missing receipts cannot
unlock the gate.

Resume/recover completeness remains TRAIL (``tracy-gate-resume-recover``); this
module is Teeth-Thin only: write disposition → unblock Pass-2 spend.

Both-walks parity: enforced from the shared ``_dispatch_specialist_at_node``
site (same pattern as coverage / UDAC). ``ResearchDetectiveGateError`` subclasses
``SpecialistDispatchError`` so the runner routes through ``_pause_at_error``.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

from app.marcus.orchestrator.research_wiring import research_detective_live
from app.specialists.dispatch_errors import SpecialistDispatchError

logger = logging.getLogger(__name__)

Disposition = Literal["approve", "reject", "defer"]

VALID_DISPOSITIONS: Final[frozenset[str]] = frozenset({"approve", "reject", "defer"})

# Manifest node 08 = Irene Pass 2 + Segment Manifest (pipeline-manifest.yaml).
PASS2_NODE_IDS: Final[frozenset[str]] = frozenset({"08"})
PASS2_SPECIALIST_IDS: Final[frozenset[str]] = frozenset({"irene"})

DISPOSITION_BASENAME: Final[str] = "research-detective-disposition.json"
LANDING_BASENAME: Final[str] = "research-detective-landing.json"

GATE_PENDING_TAG: Final[str] = "marcus.research.detective-gate-pending"
GATE_ADVISORY_TAG: Final[str] = "marcus.research.detective-gate-advisory-rejected"

SCHEMA_VERSION: Final[str] = "research-detective-disposition.v1"


class ResearchDetectiveGateError(SpecialistDispatchError):
    """Pass-2 blocked: detective flag ON and no valid disposition receipt."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message, tag=tag)


def disposition_path(run_dir: Path) -> Path:
    """Return the on-disk path for the operator disposition receipt."""
    return run_dir / DISPOSITION_BASENAME


def landing_path(run_dir: Path) -> Path:
    """Return the on-disk path for the pre-Pass-2 landing marker."""
    return run_dir / LANDING_BASENAME


def is_pass2_dispatch(*, specialist_id: str, node_id: str) -> bool:
    """True when this dispatch is Irene Pass-2 (the gated spend)."""
    return node_id in PASS2_NODE_IDS and specialist_id in PASS2_SPECIALIST_IDS


def write_landing_point(
    run_dir: Path,
    *,
    trial_id: str | None = None,
    node_id: str = "08",
) -> Path:
    """Write the pre-Pass-2 landing marker (idempotent).

    Marks that the detective path reached the hard-pause landing point and is
    awaiting approve/reject/defer. Does not unlock Pass-2 by itself.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    path = landing_path(run_dir)
    payload = {
        "schema_version": "research-detective-landing.v1",
        "status": "awaiting_disposition",
        "node_id": node_id,
        "trial_id": trial_id,
        "written_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "note": (
            "Hard-pause landing (R7 Teeth-Thin). Pass-2 blocked until "
            f"{DISPOSITION_BASENAME} carries approve|reject|defer. "
            "Resume/recover completeness = TRAIL (tracy-gate-resume-recover)."
        ),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_disposition(
    run_dir: Path,
    disposition: str,
    *,
    operator_id: str = "operator",
    rationale: str = "",
    trial_id: str | None = None,
) -> Path:
    """Persist an operator disposition that unlocks Pass-2 when valid.

    Raises ``ValueError`` for advisory / unknown values — those must never
    unlock the gate (AC: advisory-only cannot close).
    """
    normalized = disposition.strip().lower()
    if normalized not in VALID_DISPOSITIONS:
        raise ValueError(
            f"invalid research-detective disposition {disposition!r}; "
            f"required one of {sorted(VALID_DISPOSITIONS)} "
            "(advisory-only cannot unlock Pass-2)"
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    path = disposition_path(run_dir)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "disposition": normalized,
        "operator_id": operator_id,
        "rationale": rationale,
        "trial_id": trial_id,
        "written_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "unlocks_pass2": True,
        "trail_non_claim": "tracy-gate-resume-recover",
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def load_disposition(run_dir: Path) -> dict[str, Any] | None:
    """Load disposition receipt if present and JSON-parseable; else None."""
    path = disposition_path(run_dir)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def disposition_unlocks_pass2(receipt: dict[str, Any] | None) -> bool:
    """True iff receipt carries a valid approve/reject/defer disposition."""
    if not receipt:
        return False
    value = str(receipt.get("disposition", "")).strip().lower()
    # Explicit advisory / pending / other — never unlock.
    return value in VALID_DISPOSITIONS


def enforce_before_pass2(
    *,
    specialist_id: str,
    node_id: str,
    run_dir: Path,
) -> None:
    """Block Irene Pass-2 when detective is ON and disposition is missing/invalid.

    Flag-OFF: no-op (byte-identical firewall — no disk read).
    Non-Pass-2 dispatches: no-op.
    """
    if not research_detective_live():
        return
    if not is_pass2_dispatch(specialist_id=specialist_id, node_id=node_id):
        return

    # Ensure landing marker exists so live evidence can show the landing-point.
    if not landing_path(run_dir).is_file():
        write_landing_point(run_dir, node_id=node_id)

    receipt = load_disposition(run_dir)
    if disposition_unlocks_pass2(receipt):
        logger.info(
            "research detective gate unlocked for Pass-2 (disposition=%s)",
            receipt.get("disposition") if receipt else None,
        )
        return

    if receipt is not None:
        bad = str(receipt.get("disposition", "")).strip().lower() or "<empty>"
        raise ResearchDetectiveGateError(
            f"Pass-2 blocked: disposition {bad!r} is not approve|reject|defer "
            f"(advisory-only cannot unlock). Write {DISPOSITION_BASENAME}.",
            tag=GATE_ADVISORY_TAG,
        )

    raise ResearchDetectiveGateError(
        f"Pass-2 blocked: MARCUS_RESEARCH_DETECTIVE_LIVE is ON and "
        f"{DISPOSITION_BASENAME} is missing. Write approve|reject|defer "
        f"before Irene Pass-2 spend. Resume/recover = TRAIL.",
        tag=GATE_PENDING_TAG,
    )
