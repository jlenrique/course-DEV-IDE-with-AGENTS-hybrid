"""Story Q1.5 — DID §1.6 section golden (catch unreviewed prose/number drift).

AC5 asks for a golden of the rendered DID §1.6 section (or the machine-block DID
projection) so an *unreviewed* prose drift is caught. This is a real **doc↔golden**
check — the expectations below are hand-authored and must be updated *deliberately*
when the DID assessment legitimately changes (never auto-blessed):

  * **Part A — machine-block DID projection golden.** A canonical projection of the
    DID dimension ({score, band, open_leaks, trend, per-criterion level/score/
    derivation}) is pinned to an exact literal. A silent number/level/derivation edit
    to the machine block fails here. (The honesty pins already reconcile these against
    CODE; this golden additionally freezes the *authored values themselves*.)

  * **Part B — §1.6 prose honesty anchors.** The load-bearing honest phrasings Mary's
    corrections require MUST be present verbatim in the §1.6 prose: the reading-path
    metric citation ``(subject, substrate@date)`` with the built-classifier 0.071, the
    explicit "no fresh-naive number measured", the "0.93 = catalog-approach, NOT the
    built classifier" disambiguation, the Band+trend headline, the motion
    "VERIFY (not a leak)" carve-out, and each of the 5 ranked-leak slugs. A prose
    drift that deletes any of these anchors (e.g. re-implying a fresh-naive number)
    goes RED.

Pure-structural + hermetic (reads the committed doc + committed reader), like the
sibling honesty/drift pins. No live calls.
"""

from __future__ import annotations

from app.quality.scorecard import _DID_KEY, read_scorecard_block, scorecard_path

# --------------------------------------------------------------------------- #
# Part A — the machine-block DID projection golden (deliberately hand-authored).
# --------------------------------------------------------------------------- #
_DID_PROJECTION_GOLDEN: dict = {
    "score": 65,
    "band": "B-",
    "open_leaks": 5,
    "trend": "baseline",
    "criteria": {
        "neck_placement": {"level": "strong", "score": 4, "derivation": "judgment"},
        "bone_determinism": {
            "level": "strong",
            "score": 3,
            "derivation": "judgment-with-evidence",
        },
        "fence_enforcement_default_on": {
            "level": "weak",
            "score": 1,
            "derivation": "signal-derived",
        },
        "lock_and_contract_discipline": {
            "level": "strong",
            "score": 3,
            "derivation": "judgment-with-evidence",
        },
        "honesty_and_calibration": {
            "level": "partial",
            "score": 2,
            "derivation": "judgment",
        },
    },
}

#: The 5 ranked DID-leak slugs — every one MUST appear in the §1.6 prose (and each is
#: tagged ``did_leak:`` in deferred-inventory.md; the honesty pin reconciles the count).
_DID_LEAK_SLUGS: tuple[str, ...] = (
    "leg4-narration-fidelity-gate-precision-before-flag-on",
    "gary-export-llm-brief-to-page-matcher",
    "braid-workbook-semantic-claim-citation-audit",
    "reading-path-fresh-naive-holdout-pre-trial",
    "workbook-capability-tier-honesty-lag",
)

#: Honest-phrasing anchors Mary's corrections require in §1.6 prose. Load-bearing
#: TOKENS only (FIX-6a) — NOT long exact-spaced phrases — so a meaning-preserving
#: reformat on the next honest edit does not red this, while honesty drift (deleting a
#: token, e.g. re-implying a fresh-naive number) is still caught.
_PROSE_HONESTY_ANCHORS: tuple[str, ...] = (
    # reading-path metric citation carries (subject, substrate@date) + the 0.071 number
    "0.071",
    "subject=built-classifier",
    "substrate=fresh",
    # the 0.93 is disambiguated as catalog-approach, NOT the built classifier
    "catalog-approach",
    # the fresh-naive holdout is OWED/UNMEASURED and none may be implied
    "fresh-naive",
    "OWED",
    "UNMEASURED",
    # motion capability-tier is a verification TODO, NOT a counted leak
    "VERIFY (not a leak)",
    # Band-primary headline + baseline trend (not a false-precise /100 headline)
    "Band: B",
    "baseline",
    # C3 fence posture
    "OFF by default",
)


def _did_projection(block: dict) -> dict:
    dim = block["dimensions"][_DID_KEY]
    return {
        "score": dim.get("score"),
        "band": dim.get("band"),
        "open_leaks": dim.get("open_leaks"),
        "trend": dim.get("trend"),
        "criteria": {
            k: {
                "level": (c or {}).get("level"),
                "score": (c or {}).get("score"),
                "derivation": (c or {}).get("derivation"),
            }
            for k, c in (dim.get("criteria") or {}).items()
        },
    }


def _section_16_text(doc_text: str) -> str:
    """Extract the §1.6 section prose (from ``### 1.6`` to the next top-level
    ``### `` header that is not ``### 1.6``)."""
    lines = doc_text.splitlines()
    out: list[str] = []
    in_16 = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### 1.6"):
            in_16 = True
            out.append(line)
            continue
        if in_16 and stripped.startswith("### ") and not stripped.startswith("### 1.6"):
            break
        if in_16:
            out.append(line)
    return "\n".join(out)


def test_did_machine_block_projection_matches_golden() -> None:
    """Part A: the machine-block DID projection equals the hand-authored golden — a
    silent number/level/derivation drift fails RED (update the golden deliberately)."""
    block = read_scorecard_block()
    assert isinstance(block, dict), "committed scorecard machine block must be parseable"
    assert _did_projection(block) == _DID_PROJECTION_GOLDEN


def test_did_section_prose_carries_honesty_anchors() -> None:
    """Part B: every load-bearing honest phrasing Mary's corrections require is present
    verbatim in §1.6 — deleting any (e.g. re-implying a fresh-naive number) goes RED."""
    section = _section_16_text(scorecard_path().read_text(encoding="utf-8"))
    assert section, "§1.6 heading not found (renumbered?) — cannot check honesty anchors"
    missing = [a for a in _PROSE_HONESTY_ANCHORS if a not in section]
    assert missing == [], f"§1.6 prose lost required honesty anchor(s): {missing}"


def test_did_section_prose_names_all_five_ranked_leaks() -> None:
    """Part B: all 5 ranked DID-leak slugs appear in §1.6 (the ranked-leak headline),
    so the doc's leak roster cannot silently diverge from the 5 tagged leaks."""
    section = _section_16_text(scorecard_path().read_text(encoding="utf-8"))
    assert section, "§1.6 heading not found (renumbered?) — cannot check leak slugs"
    missing = [s for s in _DID_LEAK_SLUGS if s not in section]
    assert missing == [], f"§1.6 prose missing ranked-leak slug(s): {missing}"
