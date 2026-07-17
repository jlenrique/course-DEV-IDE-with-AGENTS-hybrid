"""Story 42.1 (finding C) — the tabular HIL projector, replayed against the REAL
frozen ``bc747b51`` trial artifacts (P-5: acceptance is the real 64-component
enrichment, not a toy) plus a committed trimmed fixture so the proof also runs on
machines without the live run dir (40-1 / 41-2 skip-if-absent precedent).

Every table shape here is pinned to the worked exemplars in
``evidence/operator-hil-display-requirements-2026-07-16.md`` §1.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from app.marcus.cli.hil_tabular_projector import (
    PAGE_SIZE,
    build_gate_surface,
    emit_gate_surface,
    render_enrichment_metrics,
    render_gate_identity,
    render_hil_tables,
    render_learning_objectives,
    render_ungrounded_advisories,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_TRIAL = "bc747b51-7009-4742-9f65-8de6abc29ca4"
LIVE_ENRICHMENT = (
    REPO_ROOT / "state" / "config" / "runs" / LIVE_TRIAL / "g0-enrichment.json"
)
LIVE_OPERATOR_SURFACE = (
    REPO_ROOT / "state" / "config" / "runs" / LIVE_TRIAL / "operator-surface.json"
)
TRIMMED_FIXTURE = Path(__file__).parent / "fixtures" / "g0-enrichment.trimmed.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _body_rows(table: str, header_token: str) -> list[str]:
    """Markdown table body rows (drop the header + the ``---`` separator)."""
    return [
        ln
        for ln in table.splitlines()
        if ln.startswith("| ") and header_token not in ln and "---" not in ln
    ]


# ---------------------------------------------------------------------------
# AC-2 / P-5: replay against the REAL frozen artifact — pin the row counts.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not LIVE_ENRICHMENT.exists(),
    reason="live bc747b51 run dir absent on this machine (committed fixture covers the shape)",
)
def test_real_bc747b51_row_counts_pinned() -> None:
    """The projector is proven on the real 64-component data: 64 typed / 12
    ungrounded advisories / 14 provisional LOs (AC-2)."""
    enrichment = _load(LIVE_ENRICHMENT)

    assert len(enrichment["typed_components"]) == 64
    ungrounded = [c for c in enrichment["typed_components"] if c.get("flagged_ungrounded")]
    assert len(ungrounded) == 12
    assert enrichment["reconcile"]["n_ungrounded"] == 12
    assert len(enrichment["provisional_los"]) == 14

    # metrics table carries the real counts verbatim
    metrics = render_enrichment_metrics(enrichment)
    assert "| Typed components | 64 |" in metrics
    assert "| Flagged ungrounded (advisory) | 12 |" in metrics
    assert "| Provisional LOs | 14 |" in metrics

    # advisory table = one row per flag (12 body rows) — no truncation-to-illegibility
    adv = render_ungrounded_advisories(enrichment, page_size=0)
    assert len(_body_rows(adv, "component_id")) == 12
    # each real ungrounded component is a narration speaker-note
    assert "Narration (Speaker Notes)" in adv
    assert "advisory (speaker notes) — adjudicate at G0E" in adv

    # provisional LO table = one row per LO (14 rows)
    los = render_learning_objectives(enrichment["provisional_los"], page_size=0)
    assert len(_body_rows(los, "Statement")) == 14
    assert "Define intrapreneurship" in los


@pytest.mark.skipif(
    not LIVE_OPERATOR_SURFACE.exists(),
    reason="live bc747b51 operator-surface absent on this machine",
)
def test_real_operator_surface_gate_identity_renders() -> None:
    surface = _load(LIVE_OPERATOR_SURFACE)
    identity = {
        "trial": surface["identity"]["trial_id"],
        "status": surface["envelope"]["status"],
        "gate": surface["envelope"].get("paused_gate") or "",
        "ask": "Confirm source TYPE manifest + candidate provisional LOs",
    }
    rendered = render_gate_identity(identity)
    assert f"| Trial | {LIVE_TRIAL} |" in rendered
    assert "| Item | Value |" in rendered


# ---------------------------------------------------------------------------
# Committed trimmed fixture — always available (P-5 portability).
# ---------------------------------------------------------------------------


def test_trimmed_fixture_exists_and_is_derived() -> None:
    assert TRIMMED_FIXTURE.exists()
    fx = _load(TRIMMED_FIXTURE)
    assert "trimmed from" in fx["_provenance"]
    # 7 components, 3 ungrounded, 3 LOs (see fixture provenance)
    assert len(fx["typed_components"]) == 7
    assert sum(1 for c in fx["typed_components"] if c["flagged_ungrounded"]) == 3
    assert len(fx["provisional_los"]) == 3


def test_metrics_table_shape_on_fixture() -> None:
    fx = _load(TRIMMED_FIXTURE)
    metrics = render_enrichment_metrics(fx)
    assert "| Metric | Count |" in metrics
    assert "| Typed components | 7 |" in metrics
    assert "| Flagged ungrounded (advisory) | 3 |" in metrics
    assert "| Provisional LOs | 3 |" in metrics


def test_advisories_one_row_per_flag_on_fixture() -> None:
    fx = _load(TRIMMED_FIXTURE)
    adv = render_ungrounded_advisories(fx)
    # header columns per exemplar §1
    assert "| # | component_id | parent | Kind |" in adv
    assert "advisory (speaker notes) — adjudicate at G0E" in adv
    # exactly 3 numbered body rows, one per ungrounded flag
    assert "| 1 | src-003-c005 | src-003 | Narration (Speaker Notes) |" in adv
    body_rows = [
        ln
        for ln in adv.splitlines()
        if ln.startswith("| ") and "component_id" not in ln and "---" not in ln
    ]
    assert len(body_rows) == 3
    # grounded components are NOT in the advisory table
    assert "src-001-c001" not in adv


def test_provisional_los_one_row_per_lo_on_fixture() -> None:
    fx = _load(TRIMMED_FIXTURE)
    los = render_learning_objectives(fx["provisional_los"], title="Provisional LOs")
    assert "**Provisional LOs**" in los
    assert "| # | Statement |" in los
    assert len(_body_rows(los, "Statement")) == 3
    assert los.count("| 1 |") == 1


def test_render_hil_tables_composes_all_sections() -> None:
    fx = _load(TRIMMED_FIXTURE)
    identity = {"trial": "t-1", "status": "paused-at-gate", "gate": "G0E", "ask": "Confirm"}
    surface = build_gate_surface(gate_identity=identity, enrichment=fx)
    out = render_hil_tables(surface)
    # gate identity + metrics + advisories + provisional LOs all present
    assert "| Trial | t-1 |" in out
    assert "| Typed components | 7 |" in out
    assert "advisory (speaker notes) — adjudicate at G0E" in out
    assert "**Provisional LOs**" in out


# ---------------------------------------------------------------------------
# Pagination at > ~15 rows (Marcus HIL Display Standards).
# ---------------------------------------------------------------------------


def test_advisories_paginate_over_15_rows() -> None:
    # 20 synthetic ungrounded components -> first 15 shown, 5 held back.
    enrichment = {
        "typed_components": [
            {
                "component_id": f"src-{i:03d}-c001",
                "parent_source_id": f"src-{i:03d}",
                "source_type": "narration",
                "flagged_ungrounded": True,
                "kind": None,
            }
            for i in range(20)
        ]
    }
    adv = render_ungrounded_advisories(enrichment)
    assert len(_body_rows(adv, "component_id")) == PAGE_SIZE == 15
    assert "5 more row(s) not shown" in adv
    assert "show next" in adv


def test_los_paginate_over_15_rows() -> None:
    los = [{"statement": f"Objective {i}"} for i in range(18)]
    rendered = render_learning_objectives(los)
    assert len(_body_rows(rendered, "Statement")) == 15
    assert "3 more row(s) not shown" in rendered


def test_no_pagination_footer_when_under_threshold() -> None:
    los = [{"statement": f"Objective {i}"} for i in range(5)]
    rendered = render_learning_objectives(los)
    assert "more row(s) not shown" not in rendered


# ---------------------------------------------------------------------------
# CLI printer (emit_gate_surface) — the handoff cue (AC-6).
# ---------------------------------------------------------------------------


def test_emit_gate_surface_writes_tables_and_handoff_cue() -> None:
    fx = _load(TRIMMED_FIXTURE)
    identity = {"trial": "t-1", "status": "paused-at-gate", "gate": "G0E", "ask": "Confirm"}
    surface = build_gate_surface(gate_identity=identity, enrichment=fx)
    buf = io.StringIO()
    emit_gate_surface(
        surface,
        stream=buf,
        next_action="trial resume ... --verb approve|edit|reject",
        shell_context="your shell prompt (PowerShell on Windows)",
    )
    out = buf.getvalue()
    # tables present
    assert "| Typed components | 7 |" in out
    # AC-6 handoff cue: names the shell context + the resume affordance,
    # warns off typing 'c'/'approve' at the shell.
    assert "PowerShell" in out
    assert "PAUSED" in out and "G0E" in out
    assert "Do NOT type 'c' / 'approve'" in out
    assert "trial resume" in out
