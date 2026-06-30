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

from app.marcus.lesson_plan.coverage_gate import (
    CoverageAssuranceError,
    assert_coverage_gate,
)
from app.marcus.lesson_plan.coverage_receipt import (
    COVERAGE_RECEIPT_BASENAME,
    CoverageReceipt,
    load_coverage_receipt,
)

logger = logging.getLogger(__name__)

COVERAGE_GATE_ACTIVE_ENV: Final[str] = "MARCUS_COVERAGE_GATE_ACTIVE"
COVERAGE_GATE_PROVISIONAL_ENV: Final[str] = "MARCUS_COVERAGE_GATE_PROVISIONAL_OK"
"""Dev escape hatch (Amelia): when set, a missing-receipt-past-G3 downgrades from
fail-loud to the silent no-op so intermediate integration is shippable. The SHIPPED
default is fail-loud (Marcus keystone) — provisional is opt-in only."""

COVERAGE_PASS_ACTIVE_ENV: Final[str] = "MARCUS_COVERAGE_PASS_ACTIVE"
"""Gates the AUTHORED coverage pass attach onto ``G0EnrichmentResult`` (Step 1).
Default OFF -> the pass returns no annotations -> the card firewall prunes the empty
layer -> existing flows stay byte-identical."""

# The marker the G3 seam drops to record "a coverage receipt is EXPECTED here" — the
# conservative proxy for "past G3" (the runner crossed the storyboard-publish gate).
# Self-contained: it is written by the same seam that derives the receipt, so a marker
# WITHOUT a receipt means the G3 derivation ran but failed to land a receipt -> the
# fail-loud gate fires. No marker means the legitimate pre-G3 provisional window.
COVERAGE_RECEIPT_EXPECTED_MARKER: Final[str] = "coverage-receipt-expected.marker"

COVERAGE_RECEIPT_MISSING_TAG: Final[str] = "marcus.coverage.receipt-missing-at-audio"

# The specialist(s) that incur real audio/synthesis spend; the gate fires BEFORE
# these dispatch (AC8 "before audio spend"). enrique is the ElevenLabs synthesis.
AUDIO_SPEND_SPECIALISTS: Final[frozenset[str]] = frozenset({"enrique"})


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def coverage_gate_active() -> bool:
    """True iff the coverage fail-loud gate is woken (env toggle; default OFF).

    Default OFF keeps every existing trial flow byte-identical: the seam call is a
    no-op and nothing (not even a disk read) happens.
    """
    return _env_true(COVERAGE_GATE_ACTIVE_ENV)


def coverage_gate_provisional_ok() -> bool:
    """True iff the dev provisional escape hatch is set (missing-receipt -> no-op)."""
    return _env_true(COVERAGE_GATE_PROVISIONAL_ENV)


def coverage_pass_active() -> bool:
    """True iff the authored coverage pass should attach onto ``G0EnrichmentResult``."""
    return _env_true(COVERAGE_PASS_ACTIVE_ENV)


def coverage_receipt_path(run_dir: Path) -> Path:
    return run_dir / COVERAGE_RECEIPT_BASENAME


def coverage_receipt_expected_marker_path(run_dir: Path) -> Path:
    return run_dir / COVERAGE_RECEIPT_EXPECTED_MARKER


def mark_coverage_receipt_expected(run_dir: Path) -> Path:
    """Drop the "past G3 / receipt expected" marker (idempotent; cheap, always-write).

    Written FIRST at the G3 seam (before the derive attempt) so a marker-without-receipt
    means the derive ran but did not land a receipt -> the gate fires loud.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    path = coverage_receipt_expected_marker_path(run_dir)
    path.write_text("coverage-receipt-expected\n", encoding="utf-8")
    return path


def coverage_receipt_expected(run_dir: Path) -> bool:
    """True iff the G3 seam has marked a receipt as expected (the "past G3" proxy)."""
    return coverage_receipt_expected_marker_path(run_dir).is_file()


def write_coverage_receipt(run_dir: Path, receipt: CoverageReceipt) -> Path:
    """Atomically persist the CANONICAL receipt to ``<run_dir>/coverage-receipt.json``.

    Disk-primary (mirror the RAI): temp file + ``os.replace`` so a crash mid-write
    never leaves a torn ledger. The on-disk JSON is the VOLATILE-FREE canonical
    projection (``canonical_hash_payload`` — no ``generated_at``) so the RAI
    CANONICAL_SHA256 pin survives the resume/recover G3 crossing (Round-4 ruling): the
    same surfaces -> the same on-disk bytes -> the same SHA.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    path = coverage_receipt_path(run_dir)
    payload = json.dumps(receipt.canonical_hash_payload(), indent=2, sort_keys=True)
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
        # Marcus keystone — FAIL-LOUD on missing-receipt-at-audio. If the run has
        # crossed G3 (the marker proxy) the receipt is OWED here; an audio-spend
        # dispatch with no receipt is the bypass the review found at its root → RAISE
        # (routed through the runner's recoverable pause BEFORE any ElevenLabs spend).
        # The dev provisional flag preserves the prior silent no-op for intermediate
        # integration; with NO marker we are still in the legitimate pre-G3 provisional
        # window → no-op.
        if coverage_receipt_expected(run_dir) and not coverage_gate_provisional_ok():
            raise CoverageAssuranceError(
                "audio-spend specialist dispatched without a coverage receipt; G3 was "
                "crossed (receipt expected) but no coverage-receipt.json is on disk — "
                "the coverage receipt is MISSING before audio spend. Resolve the G3 "
                "derivation (or set MARCUS_COVERAGE_GATE_PROVISIONAL_OK for intermediate "
                "integration) before incurring ElevenLabs/Descript spend.",
                tag=COVERAGE_RECEIPT_MISSING_TAG,
                blocking_rows=(),
            )
        logger.info(
            "coverage gate: no receipt on disk for %s yet (provisional window / dev flag) "
            "→ no enforcement",
            specialist_id,
        )
        return
    assert_coverage_gate(receipt)  # raises CoverageAssuranceError on a must-cover hole


__all__ = [
    "AUDIO_SPEND_SPECIALISTS",
    "COVERAGE_GATE_ACTIVE_ENV",
    "COVERAGE_GATE_PROVISIONAL_ENV",
    "COVERAGE_PASS_ACTIVE_ENV",
    "COVERAGE_RECEIPT_EXPECTED_MARKER",
    "COVERAGE_RECEIPT_MISSING_TAG",
    "coverage_gate_active",
    "coverage_gate_provisional_ok",
    "coverage_pass_active",
    "coverage_receipt_expected",
    "coverage_receipt_expected_marker_path",
    "coverage_receipt_path",
    "enforce_coverage_gate_before_audio",
    "load_coverage_receipt_from_disk",
    "mark_coverage_receipt_expected",
    "write_coverage_receipt",
]
