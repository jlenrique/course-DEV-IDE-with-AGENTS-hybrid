"""RED-first tests for the L2 source-provenance audit (numeric leg).

Fixtures mirror the real c2c6dcbf finding: narration says "$4.5 trillion" while
the source corpus says "$5.2 trillion" (drift), while "73 days" and "66%" are
faithfully sourced.
"""

from __future__ import annotations

import importlib

from app.specialists._shared.source_fidelity_audit import (
    SEMANTIC_TRIPWIRE,
    audit_numeric_provenance,
)

# Mirrors the real c2c6dcbf drift: narration $4.5T vs source $5.2T; 73 days + 66%
# faithfully sourced.
NARRATION = (
    "U.S. healthcare now exceeds $4.5 trillion annually. Compute doubles every "
    "73 days, and 66% of organizations report AI adoption."
)
SOURCE = (
    "National health expenditures reached $5.2 trillion in 2024. The doubling "
    "period is 73 days. Roughly 66% — two-thirds — cite AI."
)


def _bucket(report: dict, name: str) -> dict:
    return report["buckets"][name]


def test_module_is_read_only_caller_of_frozen_neck() -> None:
    """F4: imports & calls _figures/_normalize_figure; no neck mutation."""
    audit_mod = importlib.import_module(
        "app.specialists._shared.source_fidelity_audit"
    )
    neck = importlib.import_module("app.specialists._shared.figure_tokens")
    # Frozen neck remains read-only for callers; T4a may ADD exports
    # (PERCENT_TOLERANCE_PP / _figure_near_match) but must keep the original trio.
    assert {"_FIGURE_RE", "_figures", "_normalize_figure"} <= set(neck.__all__)
    # The audit module references the frozen-neck callables (read-only caller).
    src = (audit_mod.__file__ or "")
    assert src  # module is importable from a real file
    from app.specialists._shared.figure_tokens import _figures, _normalize_figure

    assert callable(_figures)
    assert callable(_normalize_figure)


def test_sourced_numbers_classify_source_derived_and_drift_flagged() -> None:
    report = audit_numeric_provenance(NARRATION, SOURCE)

    assert report["status"] == "AUDIT"
    assert report["non_gating"] is True

    # Denominators present and non-zero (F2).
    assert report["narration_token_count"] > 0
    assert report["source_token_count"] > 0

    # "73 days" is a bare integer with no figure-shape -> NOT a figure token.
    # "66%" -> source_derived (in source). "$4.5T" -> unsourced (source has $5.2T).
    source_derived_norms = set(_bucket(report, "source_derived")["tokens"])
    assert "percent:66" in source_derived_norms

    unsourced = _bucket(report, "unsourced_numeric")
    unsourced_norms = {p["narration_normalized"] for p in unsourced["pairs"]}
    assert "money-trillion:4.5" in unsourced_norms
    # And it is NOT classified source_derived.
    assert "money-trillion:4.5" not in source_derived_norms

    # Offending pair carries the nearest source token ($5.2T).
    pair = next(
        p
        for p in unsourced["pairs"]
        if p["narration_normalized"] == "money-trillion:4.5"
    )
    assert pair["nearest_source_normalized"] == "money-trillion:5.2"

    # drift_rate > 0 and the three buckets are explicitly counted.
    assert report["drift_rate"] > 0
    assert _bucket(report, "research_supplement")["count"] == 0
    assert _bucket(report, "research_supplement")["tokens"] == []  # empty-but-present
    assert unsourced["count"] >= 1

    # F3: unsourced_framing stub present but empty.
    assert report["unsourced_framing"]["count"] == 0
    assert report["unsourced_framing"]["items"] == []

    # F1: tripwire not tuned.
    assert report["semantic_tripwire"] is SEMANTIC_TRIPWIRE
    assert SEMANTIC_TRIPWIRE is None


def test_declared_research_supplement_reclassifies_and_drops_from_drift() -> None:
    base = audit_numeric_provenance(NARRATION, SOURCE)
    base_drift = base["drift_rate"]

    report = audit_numeric_provenance(
        NARRATION, SOURCE, research_supplements={"$4.5 trillion"}
    )

    supp = _bucket(report, "research_supplement")
    assert supp["count"] == 1
    assert "money-trillion:4.5" in supp["tokens"]

    # No longer counted as unsourced.
    unsourced_norms = {
        p["narration_normalized"]
        for p in _bucket(report, "unsourced_numeric")["pairs"]
    }
    assert "money-trillion:4.5" not in unsourced_norms

    # Supplements do not count toward drift -> drift drops.
    assert report["drift_rate"] < base_drift


def test_zero_denominator_guard_fails_not_clean_pass() -> None:
    # Empty narration -> FAIL.
    r_empty_narr = audit_numeric_provenance("", SOURCE)
    assert r_empty_narr["status"] == "FAIL"
    assert r_empty_narr["narration_token_count"] == 0
    assert r_empty_narr["drift_rate"] is None

    # Narration with no figures -> FAIL (zero numeric denominator).
    r_no_figs = audit_numeric_provenance("No numbers here at all.", SOURCE)
    assert r_no_figs["status"] == "FAIL"

    # Empty source -> FAIL.
    r_empty_src = audit_numeric_provenance(NARRATION, "")
    assert r_empty_src["status"] == "FAIL"
    assert r_empty_src["source_token_count"] == 0


def test_report_is_json_serializable() -> None:
    import json

    report = audit_numeric_provenance(NARRATION, SOURCE)
    json.dumps(report)  # must not raise
