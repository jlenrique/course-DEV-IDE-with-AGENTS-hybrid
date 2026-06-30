"""Runner-integration glue (Step 3 render + Step 4 G3 derive/write SCAFFOLD).

The OFFLINE core of the G3 coverage seam. ``_derive_and_write_coverage_receipt`` is the
ONE shared helper the production runner calls at BOTH walk sites (start + continuation),
guarded ``gate_id == "G3"``. It:

  1. drops the "past G3 / receipt expected" marker FIRST (so a later derive failure
     still trips the fail-loud gate, never a silent bypass);
  2. loads the AUTHORED coverage annotations from ``g0-enrichment.json``;
  3. marshals the run's deck + narration surfaces into anchors (``_marshal_coverage_surfaces``
     — the DEFENSIVE stub the orchestrator finalizes against live shapes);
  4. DERIVES the receipt (idempotent), WRITES the canonical RAI artifact, and RENDERS
     the standalone ``coverage-report.html`` (Step 3, FORK B → B1).

ORCHESTRATOR HANDOFF: the live MARSHALLING BODY (the exact run-state shapes for
``gary_slide_content`` / ``joined_narration`` / ``plan_units`` / ``slide_briefs``) is
finalized by the orchestrator against pre-captured live shapes — see the
``# ORCHESTRATOR: finalize marshalling against live shapes`` marker. Until then the stub
reads the obvious keys best-effort and records every unresolved join as a receipt
DIAGNOSTIC (never a crash); the gate tolerates an absent receipt until this is
live-proven (or fail-loud once the marker is dropped, per the keystone).
"""

from __future__ import annotations

import json
import logging
from html import escape
from pathlib import Path
from typing import Any

from app.gates.section_07c.storyboard_html_emitter import render_coverage_section
from app.marcus.lesson_plan.coverage_annotation import (
    CoverageAnnotation,
    load_coverage_annotation,
)
from app.marcus.lesson_plan.coverage_receipt import (
    AnchorResolution,
    CoverageReceipt,
    derive_coverage_receipt,
)
from app.marcus.orchestrator.coverage_anchors import (
    build_coverage_anchors,
    resolve_slide_key_map,
)
from app.marcus.orchestrator.coverage_gate_wiring import (
    coverage_gate_active,
    mark_coverage_receipt_expected,
    write_coverage_receipt,
)
from app.marcus.orchestrator.enrichment_consumption import (
    project_ambiguous_narration_ordinals,
)

logger = logging.getLogger(__name__)

COVERAGE_GATE_ID: str = "G3"
COVERAGE_REPORT_BASENAME: str = "coverage-report.html"
G0_ENRICHMENT_BASENAME: str = "g0-enrichment.json"


# ---------------------------------------------------------------------------
# Authored-annotation load (from the frozen g0-enrichment.json)
# ---------------------------------------------------------------------------


def _load_coverage_annotations(run_dir: Path) -> tuple[CoverageAnnotation, ...]:
    """Rehydrate the authored coverage annotations from ``g0-enrichment.json``.

    Defensive: an absent / unreadable / coverage-free enrichment file yields ``()`` (a
    vacuous receipt, PASS-vacuous), never a crash.
    """
    path = run_dir / G0_ENRICHMENT_BASENAME
    if not path.is_file():
        return ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.warning("coverage: g0-enrichment.json unreadable at %s → no annotations", run_dir)
        return ()
    raw = payload.get("coverage_annotations") if isinstance(payload, dict) else None
    if not isinstance(raw, list) or not raw:
        return ()
    out: list[CoverageAnnotation] = []
    for item in raw:
        try:
            out.append(load_coverage_annotation(item))
        except (ValueError, TypeError):
            logger.warning("coverage: dropping malformed coverage annotation in g0-enrichment.json")
    return tuple(out)


# ---------------------------------------------------------------------------
# Marshalling stub (DEFENSIVE — the orchestrator finalizes the live body)
# ---------------------------------------------------------------------------


def _as_list(value: Any) -> list[dict[str, Any]]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def _first_key(run_state: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in run_state and run_state.get(key) is not None:
            return run_state.get(key)
    return None


def _marshal_coverage_surfaces(
    run_state: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], dict[str, str], set[str], list[str]
]:
    """Read the deck + narration surfaces from run-state DEFENSIVELY (the stub).

    Returns ``(gary_slide_content, joined_narration, slide_key_map, ambiguous_ordinals,
    diagnostics)``. EVERY unresolved join appends a diagnostic string (surfaced on the
    receipt face); NOTHING here raises.

    # ORCHESTRATOR: finalize marshalling against live shapes. The run-state KEYS this
    # stub reads best-effort (so the orchestrator knows what to confirm/inject at the
    # G3 seam pre-capture):
    #   * deck rows       <- run_state["gary_slide_content" | "gary_slide_output" | "slide_content"]
    #                        (each row: slide_index|slide_id + title + body)
    #   * narration rows  <- run_state["joined_narration" | "narration_deltas" |
    #                        "voice_direction_deltas"] (row: slide_key|slide_id + narration_text)
    #   * deck->coverage  <- run_state["slide_key_map"] if pre-built, ELSE
    #     slide_key_map      resolve_slide_key_map(plan_units, slide_briefs) bridged to the
    #                        coverage "Slide N" namespace (the bridge is the live detail)
    #   * plan_units      <- run_state["plan_units"] | run_state["lesson_plan"]["plan_units"]
    #   * slide_briefs    <- run_state["slide_briefs"]
    #   * card payload    <- run_state["g0_card" | "card_payload"] (for ambiguous ordinals)
    """
    diagnostics: list[str] = []
    rs = run_state if isinstance(run_state, dict) else {}
    if not rs:
        diagnostics.append("coverage-marshal: no run_state supplied → empty surfaces")

    gary = _as_list(_first_key(rs, "gary_slide_content", "gary_slide_output", "slide_content"))
    if not gary:
        diagnostics.append("coverage-marshal: no deck rows resolved (gary_slide_content absent)")

    narration = _as_list(
        _first_key(rs, "joined_narration", "narration_deltas", "voice_direction_deltas")
    )
    if not narration:
        diagnostics.append("coverage-marshal: no narration rows resolved (joined_narration absent)")

    # deck slide_index -> coverage slide_key: prefer a pre-built map; else attempt the
    # lineage resolution (final_slide_id -> source ordinal). The bridge from the source
    # ordinal to the coverage "Slide N" namespace is the live detail the orchestrator
    # finalizes; the stub passes through whatever map is available.
    slide_key_map = rs.get("slide_key_map")
    if not isinstance(slide_key_map, dict) or not slide_key_map:
        lesson_plan = rs.get("lesson_plan") if isinstance(rs.get("lesson_plan"), dict) else {}
        plan_units = rs.get("plan_units") or lesson_plan.get("plan_units")
        slide_briefs = rs.get("slide_briefs")
        resolved = resolve_slide_key_map(plan_units, slide_briefs)
        if not resolved:
            diagnostics.append(
                "coverage-marshal: slide_key_map unresolved (no pre-built map and "
                "resolve_slide_key_map(plan_units, slide_briefs) was empty)"
            )
        slide_key_map = resolved

    card_payload = _first_key(rs, "g0_card", "card_payload")
    ambiguous = project_ambiguous_narration_ordinals(
        card_payload if isinstance(card_payload, dict) else None
    )

    return gary, narration, dict(slide_key_map or {}), set(ambiguous), diagnostics


# ---------------------------------------------------------------------------
# Step 3 — standalone coverage-report.html (FORK B → B1)
# ---------------------------------------------------------------------------


def _write_coverage_report_html(run_dir: Path, receipt: CoverageReceipt) -> Path:
    """Write the standalone operator-facing ``coverage-report.html`` next to the receipt.

    Wraps the built ``render_coverage_section`` (machine-truth = the receipt JSON;
    HTML = the human view) in a minimal deterministic document with a back-link to
    ``run_summary.yaml``. Deterministic LF output.
    """
    section = render_coverage_section(receipt.model_dump(mode="json"))
    diags = receipt.diagnostics or ()
    diag_block = ""
    if diags:
        items = "\n".join(f"    <li>{escape(str(d))}</li>" for d in diags)
        diag_block = (
            '  <section class="coverage-diagnostics">\n'
            "    <h2>Marshalling diagnostics</h2>\n"
            f"    <ul>\n{items}\n    </ul>\n  </section>\n"
        )
    doc = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n  <meta charset="utf-8">\n'
        "  <title>Coverage report</title>\n</head>\n<body>\n"
        "  <h1>Source-note coverage report</h1>\n"
        '  <p><a href="run_summary.yaml">run_summary.yaml</a></p>\n'
        f"{diag_block}"
        f"  {section}\n"
        "</body>\n</html>\n"
    )
    path = run_dir / COVERAGE_REPORT_BASENAME
    path.write_text(doc, encoding="utf-8", newline="\n")
    _link_into_run_summary(run_dir)
    return path


def _link_into_run_summary(run_dir: Path) -> None:
    """Best-effort: record the coverage-report link in run_summary.yaml (never crash)."""
    summary = run_dir / "run_summary.yaml"
    if not summary.is_file():
        return
    try:
        import yaml

        data = yaml.safe_load(summary.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return
        if data.get("coverage_report") == COVERAGE_REPORT_BASENAME:
            return  # idempotent
        data["coverage_report"] = COVERAGE_REPORT_BASENAME
        summary.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
    except Exception:  # noqa: BLE001 - defensive: a run_summary link must never break the run
        logger.warning("coverage: could not link coverage-report into run_summary.yaml")


# ---------------------------------------------------------------------------
# Step 4 — the ONE shared both-walks helper (guarded gate_id == "G3")
# ---------------------------------------------------------------------------


def _derive_and_write_coverage_receipt(
    run_dir: Path,
    gate_id: str,
    run_state: dict[str, Any] | None,
) -> Path | None:
    """Derive + write + render the coverage receipt at the G3 storyboard-publish seam.

    Called at BOTH walk sites, guarded ``gate_id == "G3"``. No-op when coverage is OFF
    (byte-identical). DEFENSIVE end-to-end: a marshalling/derive failure records a
    diagnostic and still lands a (possibly vacuous) receipt — it NEVER crashes the
    runner. The "receipt expected" marker is dropped FIRST so even a total derive
    failure trips the fail-loud gate before audio spend.
    """
    if gate_id != COVERAGE_GATE_ID:
        return None
    if not coverage_gate_active():
        return None  # gate asleep → no receipt, byte-identical
    # Mark "past G3 / receipt expected" FIRST — a later failure must still fail loud.
    mark_coverage_receipt_expected(run_dir)
    try:
        annotations = _load_coverage_annotations(run_dir)
        gary, narration, slide_key_map, ambiguous, diagnostics = _marshal_coverage_surfaces(
            run_state
        )
        anchors: dict[str, AnchorResolution] = build_coverage_anchors(
            gary, narration, slide_key_map, ambiguous
        )
        receipt = derive_coverage_receipt(
            annotations, anchors, diagnostics=tuple(diagnostics)
        )
        path = write_coverage_receipt(run_dir, receipt)
        _write_coverage_report_html(run_dir, receipt)
        logger.info(
            "coverage: G3 receipt derived (%d rows, %d diagnostics) at %s",
            len(receipt.rows), len(receipt.diagnostics), path,
        )
        return path
    except Exception:  # noqa: BLE001 - defensive: G3 derivation must never crash the runner
        logger.exception(
            "coverage: G3 receipt derivation failed; marker stands so the fail-loud gate "
            "still fires before audio spend (no silent bypass)"
        )
        return None


__all__ = [
    "COVERAGE_GATE_ID",
    "COVERAGE_REPORT_BASENAME",
    "_derive_and_write_coverage_receipt",
    "_marshal_coverage_surfaces",
]
