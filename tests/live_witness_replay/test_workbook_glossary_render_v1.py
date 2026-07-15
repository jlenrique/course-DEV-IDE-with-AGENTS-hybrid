"""Replay the enrolled ``workbook-glossary-render.v1`` (07W) witness.

Deterministic replay-render family (no LLM surface): the frozen witness is
the probe's ``verdict.json`` (probe-39-1-glossary-render-001, attempt
fdbed233). Replay pins the verdict's honesty invariants (pass, deterministic
replay, zero provider calls, zero input-digest drift, all seven machine-judge
checks) and cross-pins the registry's capture digests against the frozen
verdict so silent tamper/drift in either file fails the suite.

This module also carries the registry↔module META-PIN: every family enrolled
in ``witnesses.yaml`` must have a consuming test module in this directory
(declared via the house ``FAMILY = "<family>"`` claim line), so a future
enrolled-but-unreplayed family fails STRICT pre-flight instead of silently
narrowing what "all families witnessed" proves.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from tests.live_witness_replay.registry import family, load_registry, skip_or_fail, witness_path

FAMILY = "workbook-glossary-render.v1"

# The machine judge's seven named checks (probe-39-1 verdict contract). A
# missing, renamed, or false check is a witness regression, not a variant.
MACHINE_JUDGE_CHECKS = frozenset(
    {
        "citation_resolvability_deduped_once",
        "covered_entry_verbatim_tier_and_citation",
        "deliverable_bar_clauses",
        "docx_association_python_docx",
        "headword_identity_association",
        "lean_uncovered_honesty_plus_coverage_line",
        "md_bold_set_equals_headword_set",
    }
)


def _rows() -> list[dict[str, Any]]:
    return [row for row in family(FAMILY)["witnesses"] if row["disposition"] == "enrolled"]


def test_family_has_a_completed_enrolled_witness() -> None:
    rows = _rows()
    assert rows, f"{FAMILY} enrolled in witnesses.yaml but has zero enrolled witnesses"
    assert any(row["state"] == "completed" for row in rows), (
        f"{FAMILY} has no COMPLETED enrolled witness — a deterministic render "
        "family may not claim replay-green off non-completed shapes"
    )


@pytest.mark.parametrize("row", _rows(), ids=lambda row: row["id"])
def test_witness_verdict_replays_with_zero_provider_calls(row: dict[str, Any]) -> None:
    path = witness_path(row)
    if not path.is_file():
        skip_or_fail(f"witness verdict missing on disk: {row['id']}")
    verdict = json.loads(path.read_text(encoding="utf-8"))
    assert verdict["schema_version"] == "glossary-render-39-1-probe-evidence.v1"
    assert row["state"] == "completed"

    # Honesty invariants of the frozen PASS.
    assert verdict["pass"] is True
    assert verdict["deterministic_replay"] is True
    assert verdict["provider_calls"] == 0
    assert verdict["input_digest_drift"] == {}

    # Machine judge: all seven named checks present and true; no silent
    # narrowing (renamed/dropped checks) and no silent widening counts as
    # the frozen shape.
    judge = verdict["machine_judge"]
    assert judge["pass"] is True
    checks = judge["judge"]
    assert set(checks) == MACHINE_JUDGE_CHECKS
    failed = sorted(name for name, ok in checks.items() if ok is not True)
    assert not failed, f"machine-judge checks not true in frozen witness: {failed}"
    assert verdict["bold_term_count"] == len(judge["headwords"])

    # Tamper/drift pin: the registry's capture digests must MATCH the frozen
    # verdict's values — editing either file alone fails the replay.
    capture = row["capture"]
    assert capture["renderer_config_identity"] == verdict["renderer_config_identity"]
    assert capture["bold_term_set_digest"] == verdict["bold_term_set_digest"]


def test_meta_pin_every_enrolled_family_has_a_consuming_module() -> None:
    """Registry↔module META-PIN: enrolled-but-unreplayed families fail the suite.

    Consumption is declared via the house convention every family module uses:
    a module-level ``FAMILY = "<family>"`` claim line. A family enrolled in
    witnesses.yaml with no module claiming it means STRICT 19/19 would prove
    less than "all families witnessed" — exactly the defect this pin closes.
    """
    directory = Path(__file__).parent
    claims: dict[str, list[str]] = {}
    for module in sorted(directory.glob("test_*.py")):
        for claimed in re.findall(
            r'^FAMILY\s*=\s*"([^"]+)"\s*$', module.read_text(encoding="utf-8"), re.MULTILINE
        ):
            claims.setdefault(claimed, []).append(module.name)

    enrolled_families = [row["family"] for row in load_registry()["families"]]
    unclaimed = [name for name in enrolled_families if name not in claims]
    assert not unclaimed, (
        f"families enrolled in witnesses.yaml with NO consuming test module in "
        f"{directory.name}/ (add a replay module with a 'FAMILY = \"<family>\"' "
        f"claim line): {unclaimed}"
    )
