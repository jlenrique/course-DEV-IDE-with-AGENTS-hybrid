"""Story Q1.1 — hermetic component tests for the fail-soft scorecard reader.

Covers AC2 (generalized ``dimension_ref`` + retained ``did_score_ref`` wrapper),
AC6 (fail-soft matrix, v2 schema round-trip, unknown-key behaviour, unchanged
``did_score_ref`` return keys). All hermetic: the fail-soft matrix writes fixture
docs into ``tmp_path`` and passes them via the reader's ``path=`` parameter — no
live calls, no coupling to the committed repo doc in the fail-soft cases.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.quality.scorecard import (
    _DID_KEY,
    _EXPECTED_CANONICAL_DIMENSION_KEYS,
    did_score_ref,
    dimension_ref,
    read_scorecard_block,
)

# A minimal, well-formed v2 machine block (mirrors the committed doc's shape but
# is self-contained so the round-trip / dimension_ref tests stay hermetic).
_V2_DOC = """# fixture

<!-- QUALITY-SCORECARD-MACHINE-BLOCK v2 -->

```yaml
schema: quality-scorecard/v2
as_of: 2026-07-19
dimensions:
  dynamic_intelligence_vs_determinism:
    label: Dynamic Intelligence vs Determinism
    rubric_version: 1
    as_of: 2026-07-19
    as_verified: 2026-07-19
    score: 65
    max: 100
    band: "B-"
    band_note: "strong design, non-uniform enforcement"
    criteria:
      neck_placement:
        level: strong
        signal: null
        evidence_ref: "§1.6 C1 · Neck placement"
        score: 4
        max: 4
      honesty_and_calibration:
        level: partial
        signal: null
        evidence_ref: "§1.6 C5 · Leaks 2,4,5"
        score: 2
        max: 4
    open_leaks: 5
    trend: baseline
```
"""


def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "scorecard.md"
    p.write_text(text, encoding="utf-8")
    return p


# --- AC6: fail-soft matrix (parametrized; never raises, always unavailable) ---


def test_missing_file_is_unavailable(tmp_path: Path) -> None:
    absent = tmp_path / "does-not-exist.md"
    assert read_scorecard_block(absent) is None
    assert dimension_ref(_DID_KEY, absent) == {
        "status": "unavailable",
        "source": "docs/quality/project-quality-scorecard.md",
    }
    assert did_score_ref(absent)["status"] == "unavailable"


@pytest.mark.parametrize(
    "body",
    [
        pytest.param("# no marker here at all\n\njust prose\n", id="marker-absent"),
        pytest.param(
            # Fenced body parses to a bare list — a non-mapping top-level result.
            "<!-- QUALITY-SCORECARD-MACHINE-BLOCK v2 -->\n\n```yaml\n"
            "- this\n- is\n- not\n- a\n- mapping\n```\n",
            id="non-mapping",
        ),
        pytest.param(
            "<!-- QUALITY-SCORECARD-MACHINE-BLOCK v2 -->\n\n```yaml\n"
            "schema: v2\n  bad: : indent: :\n```\n",
            id="bad-yaml",
        ),
    ],
)
def test_fail_soft_never_raises(tmp_path: Path, body: str) -> None:
    path = _write(tmp_path, body)
    # read_scorecard_block returns None on any of these; dimension_ref -> unavailable.
    block = read_scorecard_block(path)
    assert block is None
    ref = dimension_ref(_DID_KEY, path)
    assert ref == {
        "status": "unavailable",
        "source": "docs/quality/project-quality-scorecard.md",
    }


# --- AC6: v2 schema round-trip ---


def test_v2_block_parses_with_versioning_and_criterion_shape(tmp_path: Path) -> None:
    path = _write(tmp_path, _V2_DOC)
    block = read_scorecard_block(path)
    assert isinstance(block, dict)
    assert block["schema"] == "quality-scorecard/v2"
    dim = block["dimensions"][_DID_KEY]
    # dimension-level versioning fields present
    assert dim["rubric_version"] == 1
    assert "as_of" in dim
    assert "as_verified" in dim
    # each criterion carries the v2 shape {level, signal, evidence_ref} (+ score/max)
    for crit in dim["criteria"].values():
        assert set(crit) >= {"level", "signal", "evidence_ref", "score", "max"}
        assert crit["signal"] is None  # Q1.2 fills signals; null at Q1.1


# --- AC2: dimension_ref for real key vs unknown key ---


def test_dimension_ref_returns_summary_for_real_key(tmp_path: Path) -> None:
    path = _write(tmp_path, _V2_DOC)
    ref = dimension_ref(_DID_KEY, path)
    assert ref["dimension"] == "Dynamic Intelligence vs Determinism"
    assert ref["score"] == 65
    assert ref["max"] == 100
    assert ref["band"] == "B-"
    assert ref["as_of"] == "2026-07-19"  # date coerced to str (JSON-clean)
    assert ref["source"] == "docs/quality/project-quality-scorecard.md"


def test_dimension_ref_unknown_key_is_unavailable(tmp_path: Path) -> None:
    path = _write(tmp_path, _V2_DOC)
    ref = dimension_ref("some_future_dimension_not_present", path)
    assert ref == {
        "status": "unavailable",
        "source": "docs/quality/project-quality-scorecard.md",
    }


# --- AC2: did_score_ref return-key contract unchanged (backward-compat) ---


def test_did_score_ref_return_keys_unchanged(tmp_path: Path) -> None:
    path = _write(tmp_path, _V2_DOC)
    ref = did_score_ref(path)
    # The two live consumers depend on exactly these keys.
    required = {"dimension", "score", "max", "band", "as_of", "source"}
    assert required <= set(ref)
    # as_verified MAY additionally be surfaced (AC2) but is not required by the contract.
    assert ref["score"] == 65
    assert ref["band"] == "B-"


def test_did_score_ref_delegates_to_dimension_ref(tmp_path: Path) -> None:
    path = _write(tmp_path, _V2_DOC)
    assert did_score_ref(path) == dimension_ref(_DID_KEY, path)


# --- AC2: canonical dimension-key rail for Q1.3's GL-6 meta-ratchet ---


def test_canonical_dimension_keys_constant() -> None:
    assert _DID_KEY in _EXPECTED_CANONICAL_DIMENSION_KEYS
    # Q2.1 added cost_efficiency (Dimension 2); Q2.2 added coverage_honesty (Dimension 3);
    # Q2.3 added fidelity_trust (Dimension 4); Q3.1 added capability_honesty (Dimension 5);
    # Q3.2 added tracker_coherence (Dimension 6); Q3.3 added lane_discipline (Dimension 7); Q3.4
    # adds calibration (Dimension 8 — the 8th and FINAL, closing the scorecard) — each in lockstep
    # with registering its honesty-pin (GL-6). The canonical universe now names all 8 dimensions.
    assert _EXPECTED_CANONICAL_DIMENSION_KEYS == (
        "dynamic_intelligence_vs_determinism",
        "cost_efficiency",
        "coverage_honesty",
        "fidelity_trust",
        "capability_honesty",
        "tracker_coherence",
        "lane_discipline",
        "calibration",
    )
