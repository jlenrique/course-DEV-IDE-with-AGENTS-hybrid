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
COVERAGE_VACUOUS_TAG: str = "marcus.coverage.vacuous-receipt"


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

    ``must_cover ∧ ( (coverage_status == missing ∧ no_planned_surface)
    ∨ verbatim_absent ∨ narration_obligation_unmet )``.

    FIX 1: ``verbatim_absent`` is an INDEPENDENT blocking condition, NOT gated behind
    ``no_planned_surface``. Previously ``(missing ∨ verbatim_absent) ∧
    no_planned_surface`` made ``verbatim_absent`` a DEAD term — it is only ever set
    when a surface EXISTS (so ``no_planned_surface`` was always False there), meaning a
    must-cover verbatim-required span DROPPED off a rendered slide failed OPEN. It is
    deterministic + money-on-the-line, so it blocks on its own.

    FIX 2: ``narration_obligation_unmet`` (a ``detail_in_narration`` point covered
    ONLY on the slide) is likewise an independent block term — a slide carriage does
    not satisfy a narration obligation (AC3).

    Fuzzy verdicts (altered/risky/advisory semantics where the span IS present) are
    NOT blocking — WARN / ledger-only until the ≥3-run calibration window.
    """
    if not row.must_cover:
        return False
    no_planned_surface = not (row.planned_on_slide or row.planned_in_narration)
    missing_unsurfaced = row.coverage_status == "missing" and no_planned_surface
    return missing_unsurfaced or row.verbatim_absent or row.narration_obligation_unmet


def evaluate_coverage_gate(receipt: CoverageReceipt) -> tuple[CoverageReceiptRow, ...]:
    """Return the BLOCKING rows (empty == clear). Pure, deterministic, no LLM."""
    return tuple(row for row in receipt.rows if _is_blocking(row))


def coverage_warnings(receipt: CoverageReceipt) -> tuple[CoverageReceiptRow, ...]:
    """The fuzzy WARN/ledger-only rows (altered/risky/advisory; never blocking).

    Exclusion of the blocking rows keys on ``source_point_id`` (NOT a row-identity
    set): a :class:`CoverageReceiptRow` carries a ``r7_report`` dict, so it is not
    hashable and cannot go into a ``set`` — building one raised ``TypeError`` whenever
    a row carried an R7 report.
    """
    blocking_ids = {r.source_point_id for r in evaluate_coverage_gate(receipt)}
    return tuple(
        row
        for row in receipt.rows
        if row.source_point_id not in blocking_ids
        and (
            row.containment_verdict in {"altered", "risky"}
            or (row.must_cover and row.coverage_status == "missing")
        )
    )


def evaluate_vacuous_receipt(
    receipt: CoverageReceipt, *, note_bearing_content_exists: bool
) -> str | None:
    """The VACUOUS-RECEIPT GUARD predicate (MF1+MF2): a BLOCK reason or ``None``.

    A run with real authored notes but a broken/empty bridge would otherwise PASS to
    audio spend whenever no point happened to be ``must_cover`` (the regular gate is
    silent). This deterministic guard catches the two false-PASS vectors WITHOUT
    blocking the legitimately-empty case:

      * **vacuous-with-content** — ``receipt.rows`` non-empty AND
        ``joined_row_count() == 0`` (source points exist but NOTHING joined/covered);
      * **empty-when-content-exists** — note-bearing (``narration``-typed) source
        content existed for the run but the receipt has ZERO rows (the pass did not
        run / produced nothing / a cache-replay dropped it).

    PASS (returns ``None``) for: an empty receipt when NO note-bearing content
    existed (Round-4 empty-coverage-never-blocks contract); and an
    all-``deliberately_excluded`` receipt (SF2 — legitimate nothing-to-cover, folded
    into ``is_vacuous``). The discriminator is "did note-bearing source content
    exist?", NOT merely "is the receipt empty?".
    """
    if receipt.all_deliberately_excluded():
        return None  # SF2: fully operator-signed exclusions — legitimate nothing-to-cover
    if receipt.is_vacuous():
        return (
            f"coverage receipt is VACUOUS before audio spend: {len(receipt.rows)} authored "
            "source point(s) but ZERO joined anchors — every span missed this run's own "
            "deck+narration (a broken/empty bridge crediting NO real coverage). A vacuous "
            "receipt is NOT a clean pass (R5-A5)."
        )
    if note_bearing_content_exists and not receipt.rows:
        return (
            "coverage receipt is EMPTY before audio spend but the run carries note-bearing "
            "(narration-typed) source content — the coverage pass did not run / produced "
            "nothing / was dropped on cache-replay. An empty receipt against existing "
            "note-bearing content is NOT a clean pass (MF2)."
        )
    return None


def assert_receipt_not_vacuous(
    receipt: CoverageReceipt, *, note_bearing_content_exists: bool
) -> None:
    """Raise :class:`CoverageAssuranceError` on a vacuous / empty-with-content receipt.

    The fail-loud half of the VACUOUS-RECEIPT GUARD (MF1+MF2). Returns ``None`` for a
    legitimately-empty or all-excluded receipt (no false-BLOCK).
    """
    reason = evaluate_vacuous_receipt(
        receipt, note_bearing_content_exists=note_bearing_content_exists
    )
    if reason is not None:
        raise CoverageAssuranceError(reason, tag=COVERAGE_VACUOUS_TAG, blocking_rows=())


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
    "COVERAGE_VACUOUS_TAG",
    "CoverageAssuranceError",
    "assert_coverage_gate",
    "assert_receipt_not_vacuous",
    "coverage_warnings",
    "evaluate_coverage_gate",
    "evaluate_vacuous_receipt",
]
