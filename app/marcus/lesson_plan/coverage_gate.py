"""Coverage fail-loud gate (T6) — the teeth, before audio spend (AC8).

BLOCK iff ``must_cover ∧ (missing ∨ verbatim_absent) ∧ no_planned_surface`` — a
set-difference over the DERIVED :class:`~app.marcus.lesson_plan.coverage_receipt.
CoverageReceipt`, raised at the existing both-walks UDAC dispatch seam
(``resolve_consumed_assets`` → ``_pause_at_error``), BEFORE any ElevenLabs/Descript
spend. Everything fuzzy (``altered``/``risky``, negation/comparator semantics,
low-confidence anchored judgments) is WARN / ledger-only until a ≥3-run calibration
window (mirror ``SEMANTIC_TRIPWIRE=None``). Every point still appears on the receipt
with a status (full accountability); only deterministically-certain, money-on-the-
line failures halt.

This module is the NEUTRAL gate logic (lesson_plan side, M3-clean). The orchestrator
wiring (env flag + disk load + the both-walks call site) lives in
``app.marcus.orchestrator.coverage_gate_wiring``; it raises
:class:`CoverageAssuranceError` — a :class:`SpecialistDispatchError` subclass — so
the runner's existing ``except SpecialistDispatchError`` routes it through the
recoverable ``_pause_at_error`` channel (NO parallel error channel).
"""

from __future__ import annotations

from app.marcus.lesson_plan.coverage_receipt import CoverageReceipt, CoverageReceiptRow
from app.specialists.dispatch_errors import SpecialistDispatchError

COVERAGE_GATE_TAG: str = "marcus.coverage.must-cover-uncovered"


class CoverageAssuranceError(SpecialistDispatchError):  # noqa: N818
    """Fail-loud: a must-cover source point is uncovered with no planned surface.

    Re-bases the dispatch-error family (S0 fail-loud convention) so the production
    runner's existing ``except SpecialistDispatchError`` at the shared dispatch site
    routes a coverage failure through the recoverable ``_pause_at_error`` channel,
    BEFORE audio spend (AC8). Carries the offending rows for the operator report.
    """

    def __init__(self, message: str, *, tag: str, blocking_rows: tuple[CoverageReceiptRow, ...]):
        super().__init__(message, tag=tag)
        self.blocking_rows = blocking_rows


def _is_blocking(row: CoverageReceiptRow) -> bool:
    """The deterministic, money-on-the-line BLOCK predicate (AC8).

    ``must_cover ∧ (missing ∨ verbatim_absent) ∧ no_planned_surface``. Fuzzy
    verdicts (altered/risky/advisory) are NOT blocking — WARN / ledger-only.
    """
    if not row.must_cover:
        return False
    uncovered = row.coverage_status == "missing" or row.verbatim_absent
    no_planned_surface = not (row.planned_on_slide or row.planned_in_narration)
    return uncovered and no_planned_surface


def evaluate_coverage_gate(receipt: CoverageReceipt) -> tuple[CoverageReceiptRow, ...]:
    """Return the BLOCKING rows (empty == clear). Pure, deterministic, no LLM."""
    return tuple(row for row in receipt.rows if _is_blocking(row))


def coverage_warnings(receipt: CoverageReceipt) -> tuple[CoverageReceiptRow, ...]:
    """The fuzzy WARN/ledger-only rows (altered/risky/advisory; never blocking)."""
    blocking = set(evaluate_coverage_gate(receipt))
    return tuple(
        row
        for row in receipt.rows
        if row not in blocking
        and (
            row.containment_verdict in {"altered", "risky"}
            or (row.must_cover and row.coverage_status == "missing")
        )
    )


def assert_coverage_gate(receipt: CoverageReceipt) -> None:
    """Raise :class:`CoverageAssuranceError` iff any must-cover point is uncovered (AC8).

    The fail-loud teeth. Clear receipts return ``None``. Called at the both-walks
    dispatch seam before the audio-spending specialist dispatches.
    """
    blocking = evaluate_coverage_gate(receipt)
    if not blocking:
        return
    ids = ", ".join(r.source_point_id for r in blocking)
    raise CoverageAssuranceError(
        f"coverage gate BLOCK before audio spend: {len(blocking)} must-cover source point(s) "
        f"uncovered with no planned surface [{ids}] — resolve coverage or sign a deliberate "
        "exclusion before incurring ElevenLabs/Descript spend (AC8).",
        tag=COVERAGE_GATE_TAG,
        blocking_rows=blocking,
    )


__all__ = [
    "COVERAGE_GATE_TAG",
    "CoverageAssuranceError",
    "assert_coverage_gate",
    "coverage_warnings",
    "evaluate_coverage_gate",
]
