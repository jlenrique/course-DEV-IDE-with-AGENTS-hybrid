"""Story Q1.4b — the deterministic final-report projector (AC2/AC3/AC4/AC5).

Hermetic + deterministic, like the sibling honesty/drift/golden pins. No live calls.

Coverage:
  * **Fixture full-string golden** — a hand-authored 2-dimension fixture (proving
    GL-13 CROSS-dimensional leak interleaving: paid-walk → learner-trust →
    governance across two dimensions) renders byte-identically to a pinned literal.
    RED under a seeded band flip / leak added / fence flip (AC4).
  * **Determinism** — same inputs → byte-identical repeat (AC4).
  * **Real-scorecard golden** — the REAL committed scorecard + a representative
    fence_state renders the exact Band row, the exact ordered 5 ranked-leak rows,
    both labelled sections, the fence rows, and the ``▬ baseline`` trend — never a
    ``/100`` headline (AC2/AC4a). A deep-copied real-block band flip reds it.
  * **Fail-soft (AC3)** — degraded scorecard, absent history, and absent /
    ``{"status":"unavailable"}`` fence_state each render an honest marker; the
    projector never raises.
  * **Trend never painted (AC2)** — a seeded rising/falling ledger flips the arrow.
  * **GL-13 coverage (AC5)** — ``leak_coverage_gaps`` flags a dimension with
    ``open_leaks > 0`` but no ``leaks`` list (RED), and is clean on the real repo.
"""

from __future__ import annotations

import copy
from pathlib import Path

import app.quality.report as report_mod
from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import _DID_KEY, read_scorecard_block

# --------------------------------------------------------------------------- #
# Hermetic fixtures (fully code-controlled — byte-exact golden).
# --------------------------------------------------------------------------- #
_FIXTURE_BLOCK: dict = {
    "dimensions": {
        "dim_alpha": {
            "label": "Alpha",
            "band": "B",
            "band_note": "note a",
            "open_leaks": 2,
            "criteria": {
                "c_one": {"level": "strong", "score": 3, "max": 4},
                "c_two": {"level": "weak", "score": 1, "max": 4},
            },
            "leaks": [
                {"rank": 1, "criterion": "CA", "slug": "alpha-gov", "lane": "governance"},
                {"rank": 2, "criterion": "CB", "slug": "alpha-paid", "lane": "paid-walk"},
            ],
        },
        "dim_beta": {
            "label": "Beta",
            "band": "C",
            "band_note": "note b",
            "open_leaks": 1,
            "criteria": {"c_x": {"level": "partial", "score": 2, "max": 4}},
            "leaks": [
                {
                    "rank": 1,
                    "criterion": "CX",
                    "slug": "beta-learner",
                    "lane": "learner-trust",
                }
            ],
        },
    }
}

_FIXTURE_FENCE: dict = {
    "fences_enabled": {"fidelity": True, "coverage": False, "udac": False},
    "silent_bypass_events": 0,
    "hil_allowlist_empty": True,
    "pack_hash_binding": "sha256:pack",
    "conversation_chain_digest": "sha256:chain",
    "cost_posture": "exact",
}

#: The byte-exact rendered projection for (_FIXTURE_BLOCK, empty-history, _FIXTURE_FENCE).
#: Deliberately hand-authored — update ONLY when the projector's format legitimately
#: changes (never auto-bless). Note the ranked-leaks table interleaves ACROSS the two
#: dimensions by lane priority (Alpha paid-walk → Beta learner-trust → Alpha governance),
#: which is the GL-13 cross-dimensional aggregation proof.
_FIXTURE_GOLDEN = """\
## Quality Scorecard — Final Report

### This run (facts)

_Mechanical fence facts this run actually emitted — not a project grade._

| Fact | Value |
| --- | --- |
| Fence enabled — fidelity | true |
| Fence enabled — coverage | false |
| Fence enabled — UDAC | false |
| Silent bypass events | 0 |
| HIL allowlist empty | true |
| Cost posture | exact |
| Pack hash binding | sha256:pack |
| Conversation chain digest | sha256:chain |

### Project (not this run)

_Project quality posture — Band, ranked leaks, trend. NOT a claim about this run._

**Band (per dimension)**

| Dimension | Band | Note |
| --- | --- | --- |
| Alpha | B | note a |
| Beta | C | note b |

**Per-criterion trace (0–4)**

| Dimension | Criterion | Level | 0–4 |
| --- | --- | --- | --- |
| Alpha | c_one | strong | 3/4 |
| Alpha | c_two | weak | 1/4 |
| Beta | c_x | partial | 2/4 |

**Ranked project leaks**

| Rank | Dimension | Criterion | Lane | Slug |
| --- | --- | --- | --- | --- |
| 2 | Alpha | CB | paid-walk | alpha-paid |
| 1 | Beta | CX | learner-trust | beta-learner |
| 1 | Alpha | CA | governance | alpha-gov |

**Trend**

| Dimension | Trend |
| --- | --- |
| Alpha | ▬ baseline |
| Beta | ▬ baseline |"""


def _empty_history(tmp_path: Path) -> Path:
    p = tmp_path / "history.jsonl"
    p.write_text("", encoding="utf-8")
    return p


def _render_fixture(tmp_path: Path, *, block=None, fence=None) -> str:
    return render_scorecard_final_report(
        block=_FIXTURE_BLOCK if block is None else block,
        history=_empty_history(tmp_path),
        fence_state=_FIXTURE_FENCE if fence is None else fence,
    )


# --------------------------------------------------------------------------- #
# AC4 — fixture full-string golden + determinism.
# --------------------------------------------------------------------------- #
def test_fixture_render_matches_golden(tmp_path: Path) -> None:
    """The 2-dimension fixture renders byte-identically to the pinned literal —
    including the CROSS-dimensional ranked-leak interleaving (GL-13)."""
    assert _render_fixture(tmp_path) == _FIXTURE_GOLDEN


def test_render_is_deterministic_byte_identical(tmp_path: Path) -> None:
    """Same inputs → byte-identical output (AC4: no dict-order / timestamp leakage)."""
    first = _render_fixture(tmp_path)
    second = _render_fixture(tmp_path)
    assert first == second == _FIXTURE_GOLDEN


def test_golden_reds_under_seeded_band_flip(tmp_path: Path) -> None:
    """RED under a seeded band change (AC4)."""
    mutated = copy.deepcopy(_FIXTURE_BLOCK)
    mutated["dimensions"]["dim_alpha"]["band"] = "A"
    assert _render_fixture(tmp_path, block=mutated) != _FIXTURE_GOLDEN


def test_golden_reds_under_seeded_leak_added(tmp_path: Path) -> None:
    """RED under a seeded added leak (AC4)."""
    mutated = copy.deepcopy(_FIXTURE_BLOCK)
    mutated["dimensions"]["dim_beta"]["leaks"].append(
        {"rank": 2, "criterion": "CY", "slug": "beta-extra", "lane": "paid-walk"}
    )
    assert _render_fixture(tmp_path, block=mutated) != _FIXTURE_GOLDEN


def test_golden_reds_under_seeded_fence_flip(tmp_path: Path) -> None:
    """RED under a seeded fence flip (AC4)."""
    mutated = copy.deepcopy(_FIXTURE_FENCE)
    mutated["fences_enabled"]["fidelity"] = False
    assert _render_fixture(tmp_path, fence=mutated) != _FIXTURE_GOLDEN


# --------------------------------------------------------------------------- #
# AC2 — trend is COMPUTED from the ledger, never painted.
# --------------------------------------------------------------------------- #
def test_trend_is_computed_not_painted(tmp_path: Path) -> None:
    """A seeded rising ledger renders ``▲ rising``; a falling ledger ``▼ falling`` —
    proving the arrow is derived from ``trend_from_history``, not painted."""
    rising = tmp_path / "rising.jsonl"
    rising.write_text(
        '{"as_of": "2026-07-01", "dimension": "dim_alpha", "score": 40}\n'
        '{"as_of": "2026-07-19", "dimension": "dim_alpha", "score": 65}\n',
        encoding="utf-8",
    )
    out_rising = render_scorecard_final_report(
        block=_FIXTURE_BLOCK, history=rising, fence_state=_FIXTURE_FENCE
    )
    assert "| Alpha | ▲ rising |" in out_rising

    falling = tmp_path / "falling.jsonl"
    falling.write_text(
        '{"as_of": "2026-07-01", "dimension": "dim_alpha", "score": 80}\n'
        '{"as_of": "2026-07-19", "dimension": "dim_alpha", "score": 65}\n',
        encoding="utf-8",
    )
    out_falling = render_scorecard_final_report(
        block=_FIXTURE_BLOCK, history=falling, fence_state=_FIXTURE_FENCE
    )
    assert "| Alpha | ▼ falling |" in out_falling


# --------------------------------------------------------------------------- #
# AC3 — fail-soft degraded / unavailable paths (deterministic markers).
# --------------------------------------------------------------------------- #
def test_degraded_scorecard_renders_honest_marker(tmp_path: Path) -> None:
    """A ``None`` / degraded block degrades the PROJECT section only; the This-run
    section still renders the fence facts. Never raises."""
    out = render_scorecard_final_report(
        block=None, history=_empty_history(tmp_path), fence_state=_FIXTURE_FENCE
    )
    assert "_quality scorecard unavailable_" in out
    assert "### This run (facts)" in out
    assert "| Fence enabled — fidelity | true |" in out  # fence section unaffected


def test_unavailable_fence_state_renders_honest_marker(tmp_path: Path) -> None:
    """An absent / ``{"status":"unavailable"}`` fence_state degrades the This-run
    section only; the Project section still renders. Never raises."""
    for fence in (None, {"status": "unavailable"}):
        out = render_scorecard_final_report(
            block=_FIXTURE_BLOCK, history=_empty_history(tmp_path), fence_state=fence
        )
        assert "_this run: fence_state unavailable_" in out
        assert "**Band (per dimension)**" in out  # project section unaffected


def test_fully_degraded_render_is_deterministic_and_safe() -> None:
    """Both inputs degraded → both honest markers, deterministic, never raises."""
    a = render_scorecard_final_report(block=None, history=None, fence_state=None)
    b = render_scorecard_final_report(block=None, history=None, fence_state=None)
    assert a == b
    assert "_quality scorecard unavailable_" in a
    assert "_this run: fence_state unavailable_" in a


def test_projector_never_raises_on_malformed_block(tmp_path: Path) -> None:
    """A structurally-malformed block (leaks not a list, criteria not a dict) degrades
    honestly rather than raising (AC3)."""
    junk = {"dimensions": {"d": {"label": "D", "leaks": "nope", "criteria": 7}}}
    out = render_scorecard_final_report(
        block=junk, history=_empty_history(tmp_path), fence_state=_FIXTURE_FENCE
    )
    assert isinstance(out, str) and out  # rendered, did not raise
    assert ranked_project_leaks(junk) == []  # malformed leaks skipped, no raise


# --------------------------------------------------------------------------- #
# AC4a — the REAL committed scorecard + representative fence_state (row-anchored,
# per the Q1.5 golden-robustness learning: stable structure over brittle spacing).
# --------------------------------------------------------------------------- #
_REAL_BAND_ROW = (
    "| Dynamic Intelligence vs Determinism | B- | "
    "strong design, non-uniform enforcement |"
)
#: The 5 ranked DID leaks in EXACT rendered order (paid-walk → learner-trust →
#: governance). A silent reorder / slug edit / lane change reds this.
_REAL_LEAK_ROWS = (
    "| 1 | Dynamic Intelligence vs Determinism | C3 | paid-walk | "
    "leg4-narration-fidelity-gate-precision-before-flag-on |",
    "| 2 | Dynamic Intelligence vs Determinism | C2 | paid-walk | "
    "gary-export-llm-brief-to-page-matcher |",
    "| 3 | Dynamic Intelligence vs Determinism | C5 | learner-trust | "
    "braid-workbook-semantic-claim-citation-audit |",
    "| 4 | Dynamic Intelligence vs Determinism | C5 | learner-trust | "
    "reading-path-fresh-naive-holdout-pre-trial |",
    "| 5 | Dynamic Intelligence vs Determinism | C5 | governance | "
    "workbook-capability-tier-honesty-lag |",
)


def test_real_scorecard_render_golden() -> None:
    """AC4a: the REAL scorecard + a representative fence_state renders the exact Band
    row, the exact ordered 5 ranked-leak rows, both labelled sections, the fence rows,
    and the ▬ baseline trend — and NEVER a false-precise ``/100`` headline."""
    block = read_scorecard_block()
    assert isinstance(block, dict), "committed scorecard machine block must parse"
    out = render_scorecard_final_report(
        block=block, history=None, fence_state=_FIXTURE_FENCE
    )
    # Two clearly-labelled sections (consensus rule #1).
    assert "### This run (facts)" in out
    assert "### Project (not this run)" in out
    # Band (per dimension) — not a /100 headline.
    assert _REAL_BAND_ROW in out
    assert "/100" not in out
    # The 5 ranked leaks in exact cross-dimensional order.
    idx = -1
    for row in _REAL_LEAK_ROWS:
        nxt = out.find(row)
        assert nxt != -1, f"missing ranked-leak row: {row}"
        assert nxt > idx, f"ranked-leak row out of order: {row}"
        idx = nxt
    # Representative fence facts (This-run section).
    assert "| Fence enabled — fidelity | true |" in out
    assert "| Cost posture | exact |" in out
    # Trend computed from the real (baseline) ledger.
    assert "| Dynamic Intelligence vs Determinism | ▬ baseline |" in out


def test_real_scorecard_render_reds_under_seeded_band_flip() -> None:
    """AC4a RED-under-seeded-change: a deep-copied real-block band flip no longer
    renders the pinned Band row."""
    block = copy.deepcopy(read_scorecard_block())
    block["dimensions"][_DID_KEY]["band"] = "A"
    out = render_scorecard_final_report(
        block=block, history=None, fence_state=_FIXTURE_FENCE
    )
    assert _REAL_BAND_ROW not in out


# --------------------------------------------------------------------------- #
# GL-13 — cross-dimensional ranked aggregation + AC5 coverage guard.
# --------------------------------------------------------------------------- #
def test_ranked_project_leaks_interleaves_across_dimensions() -> None:
    """GL-13: leaks from BOTH fixture dimensions aggregate into ONE list ranked by
    lane priority (NOT grouped by dimension)."""
    ranked = ranked_project_leaks(_FIXTURE_BLOCK)
    assert [e["slug"] for e in ranked] == ["alpha-paid", "beta-learner", "alpha-gov"]
    assert [e["lane"] for e in ranked] == ["paid-walk", "learner-trust", "governance"]
    # crosses dimensions: the top and bottom entries are from dim_alpha, the middle
    # from dim_beta — proving it is not a per-dimension concatenation.
    assert ranked[0]["dimension"] == "dim_alpha"
    assert ranked[1]["dimension"] == "dim_beta"


def test_real_did_leaks_reconcile_with_open_leaks() -> None:
    """The real DID ``leaks`` list has exactly 5 entries == its ``open_leaks``. The
    cross-dimensional ranked list now AGGREGATES DID (5) + cost_efficiency (1) +
    coverage_honesty (1) + fidelity_trust (1) = 8 (GL-13; Q2.1 added cost_efficiency's
    ``leaks`` list, Q2.2 added coverage_honesty's, Q2.3 added fidelity_trust's)."""
    block = read_scorecard_block()
    dim = block["dimensions"][_DID_KEY]
    assert len(dim["leaks"]) == dim["open_leaks"] == 5
    # Ranked list = sum of every dimension's open_leaks (DID 5 + cost 1 + coverage 1 + fid 1).
    total_open = sum(
        d.get("open_leaks", 0) for d in block["dimensions"].values() if isinstance(d, dict)
    )
    assert total_open == 8
    assert len(ranked_project_leaks(block)) == total_open == 8


def test_leak_coverage_gaps_clean_on_real_repo() -> None:
    """AC5: every real dimension declaring ``open_leaks > 0`` carries a ``leaks`` list."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


def test_leak_coverage_gap_reds_for_dimension_without_leaks() -> None:
    """AC5 RED: a dimension with ``open_leaks > 0`` but NO ``leaks`` list is a coverage
    gap AND silently missing from the ranked list — so a sibling cannot stay off it."""
    block = {
        "dimensions": {
            "sibling_no_leaks": {"label": "Sibling", "open_leaks": 3},  # no leaks list
        }
    }
    gaps = leak_coverage_gaps(block)
    assert len(gaps) == 1
    assert "sibling_no_leaks" in gaps[0]
    assert ranked_project_leaks(block) == []  # silently absent → the gap catches it


def test_leak_coverage_no_gap_when_open_leaks_zero() -> None:
    """A dimension with ``open_leaks == 0`` and no ``leaks`` list is NOT a gap."""
    block = {"dimensions": {"clean_dim": {"label": "Clean", "open_leaks": 0}}}
    assert leak_coverage_gaps(block) == []


# --------------------------------------------------------------------------- #
# FIX-2 — per-section fail-soft isolation + mixed-key sort guard.
# --------------------------------------------------------------------------- #
def test_mixed_key_block_does_not_crash_and_fence_survives(tmp_path: Path) -> None:
    """A machine block with HETEROGENEOUS mapping keys (a YAML int/bool key beside a
    str key) must NOT raise on ``sorted(...)`` — the Project section renders and the
    This-run fence section is intact (FIX-2b, total-order-safe sort)."""
    mixed = {
        "dimensions": {
            "z_str": {"label": "Zed", "band": "B", "open_leaks": 0, "criteria": {}},
            7: {"label": "IntKey", "band": "C", "open_leaks": 0, "criteria": {}},
            True: {"label": "BoolKey", "band": "D", "open_leaks": 0, "criteria": {}},
        }
    }
    out = render_scorecard_final_report(
        block=mixed, history=_empty_history(tmp_path), fence_state=_FIXTURE_FENCE
    )
    assert "| Fence enabled — fidelity | true |" in out  # fence section intact
    assert "| Zed | B |" in out and "| IntKey | C |" in out  # project rendered, no crash


def test_section_isolation_fence_survives_project_failure(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX-2a: if the PROJECT section raises, the This-run fence section is NOT dropped
    (the whole report used to collapse to the combined marker). Force the project
    renderer to raise → the fence table still renders + the project shows its marker."""

    def _boom(*_args, **_kwargs):
        raise RuntimeError("seeded project-render failure")

    monkeypatch.setattr(report_mod, "_render_project", _boom)
    out = render_scorecard_final_report(
        block=_FIXTURE_BLOCK, history=_empty_history(tmp_path), fence_state=_FIXTURE_FENCE
    )
    assert "| Fence enabled — fidelity | true |" in out  # fence SURVIVED the failure
    assert "_quality scorecard unavailable_" in out  # project degraded to its marker


# --------------------------------------------------------------------------- #
# FIX-3 — degraded fence marker aligned to the REAL _build_fence_state emit shape.
# --------------------------------------------------------------------------- #
def test_all_unavailable_fence_state_renders_single_marker(tmp_path: Path) -> None:
    """FIX-3: a fence_state whose every leaf value is ``unavailable``/``undetected``
    (mirroring the real ``production_runner._build_fence_state`` degraded emit, which
    has NO ``status`` key) renders the single honest marker — not 8 noisy rows."""
    degraded = {
        "fences_enabled": {
            "fidelity": "unavailable",
            "coverage": "unavailable",
            "udac": "unavailable",
        },
        "silent_bypass_events": "undetected",
        "hil_allowlist_empty": "unavailable",
        "pack_hash_binding": "unavailable",
        "conversation_chain_digest": "unavailable",
        "cost_posture": "unavailable",
    }
    out = render_scorecard_final_report(
        block=_FIXTURE_BLOCK, history=_empty_history(tmp_path), fence_state=degraded
    )
    assert "_this run: fence_state unavailable_" in out
    assert "Fence enabled — fidelity" not in out  # NOT 8 noisy rows


def test_empty_fence_state_renders_single_marker(tmp_path: Path) -> None:
    """FIX-3: an empty ``{}`` fence_state is the marker case."""
    out = render_scorecard_final_report(
        block=_FIXTURE_BLOCK, history=_empty_history(tmp_path), fence_state={}
    )
    assert "_this run: fence_state unavailable_" in out


def test_partially_degraded_fence_state_still_renders_rows(tmp_path: Path) -> None:
    """A fence_state with even ONE real fact (a live cost_posture) is NOT the marker
    case — it renders the table (the honest 'unavailable' fields shown alongside)."""
    partial = {
        "fences_enabled": {
            "fidelity": "unavailable",
            "coverage": "unavailable",
            "udac": "unavailable",
        },
        "silent_bypass_events": "undetected",
        "hil_allowlist_empty": "unavailable",
        "pack_hash_binding": "sha256:real",
        "conversation_chain_digest": "unavailable",
        "cost_posture": "unavailable",
    }
    out = render_scorecard_final_report(
        block=_FIXTURE_BLOCK, history=_empty_history(tmp_path), fence_state=partial
    )
    assert "| Pack hash binding | sha256:real |" in out
    assert "_this run: fence_state unavailable_" not in out


# --------------------------------------------------------------------------- #
# FIX-4 — _md_table cell escaping (pipe / newline).
# --------------------------------------------------------------------------- #
def test_cell_escaping_keeps_pipe_and_newline_in_one_cell(tmp_path: Path) -> None:
    """FIX-4: a raw ``|`` / newline in a band_note / slug is escaped / collapsed so the
    row stays ONE row inside its own cell — an unescaped pipe would split columns and
    silently defeat row-anchored goldens."""
    block = copy.deepcopy(_FIXTURE_BLOCK)
    block["dimensions"]["dim_alpha"]["band_note"] = "note | with\npipe"
    block["dimensions"]["dim_alpha"]["leaks"][1]["slug"] = "alpha|paid"
    out = render_scorecard_final_report(
        block=block, history=_empty_history(tmp_path), fence_state=_FIXTURE_FENCE
    )
    # band_note pipe escaped + newline collapsed to a space → single cell, single row.
    assert "| Alpha | B | note \\| with pipe |" in out
    # the leak slug pipe escaped inside its cell.
    assert "| alpha\\|paid |" in out
    # no bare " | " artifact from the injected slug pipe (it must be escaped).
    assert "alpha|paid" not in out
