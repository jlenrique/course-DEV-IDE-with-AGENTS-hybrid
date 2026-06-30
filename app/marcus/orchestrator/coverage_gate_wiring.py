"""Coverage gate orchestrator wiring (T6) — env flag + disk I/O + both-walks seam.

The NEUTRAL gate logic lives in ``app.marcus.lesson_plan.coverage_gate`` (M3-clean).
This orchestrator module owns only the disk-primary receipt I/O + the env
feature-flag (default OFF → existing pipeline byte-identical) + the seam-callable
that the SHARED dispatch site invokes before the audio-spending specialist.

Both-walks parity (mirrors UDAC ``resolve_consumed_assets``): the shared dispatch
site ``_dispatch_specialist_at_node`` is taken by BOTH the start walker (reaches G1)
AND the continuation/recover walker (owns G2B+), so a single guarded call there
gates audio spend on every walk. ``CoverageAssuranceError`` is a
``SpecialistDispatchError`` subclass, so the runner's existing
``except SpecialistDispatchError`` routes it through ``_pause_at_error`` — NO
parallel error channel, BEFORE any ElevenLabs/Descript spend (AC8).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Final

from app.marcus.lesson_plan.coverage_gate import assert_coverage_gate
from app.marcus.lesson_plan.coverage_receipt import (
    COVERAGE_RECEIPT_BASENAME,
    CoverageReceipt,
    load_coverage_receipt,
)

logger = logging.getLogger(__name__)

COVERAGE_GATE_ACTIVE_ENV: Final[str] = "MARCUS_COVERAGE_GATE_ACTIVE"

# The specialist(s) that incur real audio/synthesis spend; the gate fires BEFORE
# these dispatch (AC8 "before audio spend"). enrique is the ElevenLabs synthesis.
AUDIO_SPEND_SPECIALISTS: Final[frozenset[str]] = frozenset({"enrique"})


def coverage_gate_active() -> bool:
    """True iff the coverage fail-loud gate is woken (env toggle; default OFF).

    Default OFF keeps every existing trial flow byte-identical: the seam call is a
    no-op and nothing (not even a disk read) happens.
    """
    return os.environ.get(COVERAGE_GATE_ACTIVE_ENV, "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def coverage_receipt_path(run_dir: Path) -> Path:
    return run_dir / COVERAGE_RECEIPT_BASENAME


def write_coverage_receipt(run_dir: Path, receipt: CoverageReceipt) -> Path:
    """Atomically persist the derived receipt to ``<run_dir>/coverage-receipt.json``.

    Disk-primary (mirror the RAI): temp file + ``os.replace`` so a crash mid-write
    never leaves a torn ledger.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    path = coverage_receipt_path(run_dir)
    payload = json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True)
    tmp = path.with_name(f"{COVERAGE_RECEIPT_BASENAME}.{os.getpid()}.tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)
    return path


def load_coverage_receipt_from_disk(run_dir: Path) -> CoverageReceipt | None:
    """Rehydrate the receipt from disk (disk is SSOT). ``None`` when absent."""
    path = coverage_receipt_path(run_dir)
    if not path.is_file():
        return None
    return load_coverage_receipt(json.loads(path.read_text(encoding="utf-8")))


def enforce_coverage_gate_before_audio(*, specialist_id: str, run_dir: Path) -> None:
    """Fail-loud coverage guard at the both-walks dispatch seam (AC8).

    No-op when the flag is OFF (byte-identical firewall), when the dispatching
    specialist is not audio-spending, or when no receipt has been derived yet (the
    provisional window — nothing to gate). Otherwise loads the frozen receipt and
    raises :class:`~app.marcus.lesson_plan.coverage_gate.CoverageAssuranceError` iff
    a must-cover source point is uncovered with no planned surface — routed through
    the runner's recoverable pause BEFORE audio spend.
    """
    if not coverage_gate_active():
        return
    if specialist_id not in AUDIO_SPEND_SPECIALISTS:
        return
    receipt = load_coverage_receipt_from_disk(run_dir)
    if receipt is None:
        logger.info(
            "coverage gate: no receipt on disk for %s yet (provisional window) → no enforcement",
            specialist_id,
        )
        return
    assert_coverage_gate(receipt)  # raises CoverageAssuranceError on a must-cover hole


__all__ = [
    "AUDIO_SPEND_SPECIALISTS",
    "COVERAGE_GATE_ACTIVE_ENV",
    "coverage_gate_active",
    "coverage_receipt_path",
    "enforce_coverage_gate_before_audio",
    "load_coverage_receipt_from_disk",
    "write_coverage_receipt",
]
