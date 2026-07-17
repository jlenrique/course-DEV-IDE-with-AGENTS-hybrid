"""Story 43-11 — SPOC narration <-> tabular projector anti-drift parity guard.

The Marcus-SPOC driver (``app/marcus/cli/marcus_spoc.py``) hand-formats the same
G0E/G0R kickoff material as **prose**, independently of the tabular projector
(``app/marcus/cli/hil_tabular_projector.py``). Two independent renderings of the
SAME gate data can silently diverge (rider R5 / the audit's drift-debt finding).
This test installs the anti-drift guard: it feeds the SAME frozen 43-0 replay
inputs to BOTH surfaces and asserts they agree on the LOAD-BEARING facts they
BOTH render.

Surfaces pinned:

* **G0E — source-enrichment confirm** (Kickoff Beat 2, "the material"):
  the typed-component total, the provisional-LO total, and the provisional-LO
  identity set (each ``objective_id`` + ``statement``) are IDENTICAL across the
  SPOC prose and the projector's ``render_enrichment_metrics`` /
  ``render_learning_objectives``.
* **G0R — LO ratify** (Kickoff Beat 3, "the contract"):
  the refined-LO total and the refined-LO identity set are IDENTICAL across the
  SPOC prose and the projector's ``render_learning_objectives``.

If either surface is ever changed to read a different field / a different LO list
/ a different count, the shared-source facts asserted below stop matching one of
the two renderings and this test fails.

Deterministic / replay-only — reads the frozen ``tests/fixtures/hil_projector/``
fixtures, no live calls, zero spend.

KNOWN, deliberately-NOT-asserted divergence (filed to
``_bmad-output/planning-artifacts/deferred-inventory.md`` §Static-validation as an
Epic-43 SPOC-drift finding): the SPOC prose surfaces the ``flagged_unconsumed``
axis (bc747b51: 13 components, "flagged classification-only") while the projector's
``render_enrichment_metrics`` / ``render_ungrounded_advisories`` surface the
distinct ``flagged_ungrounded`` axis (12 components, "advisory"). The SPOC never
enumerates the ungrounded-advisory set the projector exists to show. That flag-axis
gap is a genuine pre-existing divergence; this guard pins the facts the two surfaces
DO agree on and leaves the gap to the filed follow-on rather than forcing a risky
prose refactor.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.cli.hil_tabular_projector import (
    render_enrichment_metrics,
    render_learning_objectives,
)
from app.marcus.cli.marcus_spoc import narrate_gate

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "hil_projector"

# How many LOs the SPOC prose enumerates inline (``los[:8]`` / ``refined[:8]``);
# the parity comparison of per-LO identity is over this shared window.
_SPOC_LO_CAP = 8
# Statement prefix length compared across surfaces. Shorter than the SPOC prose
# ``statement[:80]`` truncation, so it is a common prefix of both renderings.
_STMT_FRAG = 50


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _projector_lo_rows(table: str) -> list[str]:
    """The data rows (excluding header + separator) of a ``render_learning_objectives``
    markdown table — used to count the LOs the projector enumerated."""
    rows: list[str] = []
    for line in table.splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| # ") or line.startswith("| ---"):
            continue
        rows.append(line)
    return rows


@pytest.fixture()
def run_dir(tmp_path: Path) -> Path:
    """A run directory carrying the frozen enrichment receipt, so the SPOC's
    ``narrate_gate`` reads the SAME g0-enrichment the projector is fed."""
    enrichment = _load("g0-enrichment-bc747b51.json")
    (tmp_path / "g0-enrichment.json").write_text(
        json.dumps(enrichment), encoding="utf-8"
    )
    return tmp_path


def test_g0e_enrichment_counts_agree(run_dir: Path) -> None:
    """G0E: typed-component total and provisional-LO total are identical across the
    SPOC prose and the projector's enrichment-metrics table."""
    enrichment = _load("g0-enrichment-bc747b51.json")
    g0e_card = _load("decision-card-g0e-bc747b51.json")

    expected_typed = len(enrichment["typed_components"])
    expected_provisional = len(enrichment["provisional_los"])

    spoc = narrate_gate("G0E", g0e_card, run_dir)
    metrics = render_enrichment_metrics(enrichment)

    # Typed-component total: SPOC prose header <-> projector metric row.
    assert f"Typed COMPONENTS ({expected_typed} across" in spoc
    assert f"| Typed components | {expected_typed} |" in metrics

    # Provisional-LO total: SPOC prose header <-> projector metric row.
    assert f"Candidate provisional LOs ({expected_provisional})" in spoc
    assert f"| Provisional LOs | {expected_provisional} |" in metrics


def test_g0e_provisional_lo_identity_agrees(run_dir: Path) -> None:
    """G0E: the SPOC prose and the projector enumerate the SAME provisional LOs
    (objective_id + statement), so a change to either surface's LO source diverges."""
    enrichment = _load("g0-enrichment-bc747b51.json")
    g0e_card = _load("decision-card-g0e-bc747b51.json")
    provisional = enrichment["provisional_los"]

    spoc = narrate_gate("G0E", g0e_card, run_dir)
    lo_table = render_learning_objectives(provisional, page_size=0)

    # The projector enumerates EVERY provisional LO ...
    assert len(_projector_lo_rows(lo_table)) == len(provisional)
    for lo in provisional:
        assert lo["statement"][:_STMT_FRAG] in lo_table

    # ... and the LOs the SPOC prose enumerates inline are the SAME objects (same
    # objective_id + same statement text) the projector renders.
    for lo in provisional[:_SPOC_LO_CAP]:
        frag = lo["statement"][:_STMT_FRAG]
        assert lo["objective_id"] in spoc
        assert frag in spoc
        assert frag in lo_table


def test_g0r_refined_lo_count_and_identity_agree(run_dir: Path) -> None:
    """G0R: the refined-LO total and identity set are identical across the SPOC
    prose and the projector's learning-objectives table."""
    g0r_card = _load("decision-card-g0r-bc747b51.json")
    refined = g0r_card["card"]["refined_los"]
    expected_refined = len(refined)

    spoc = narrate_gate("G0R", g0r_card, run_dir)
    refined_table = render_learning_objectives(
        refined, title="Refined LOs", page_size=0
    )

    # Refined-LO total: SPOC prose header <-> projector table row count.
    assert f"Refined learning objectives ({expected_refined})" in spoc
    assert len(_projector_lo_rows(refined_table)) == expected_refined

    # The projector enumerates EVERY refined LO ...
    for lo in refined:
        assert lo["statement"][:_STMT_FRAG] in refined_table

    # ... and the refined LOs the SPOC prose enumerates inline are the SAME objects.
    for lo in refined[:_SPOC_LO_CAP]:
        frag = lo["statement"][:_STMT_FRAG]
        assert lo["objective_id"] in spoc
        assert frag in spoc
        assert frag in refined_table


def test_g0e_g0r_share_the_same_lo_backbone(run_dir: Path) -> None:
    """Cross-surface, cross-gate: the G0R refined LOs are the same objective_ids the
    G0E provisional surface confirmed (the contract is refined FROM the confirmed
    material), so both projector and SPOC render a single coherent LO backbone."""
    enrichment = _load("g0-enrichment-bc747b51.json")
    g0r_card = _load("decision-card-g0r-bc747b51.json")

    provisional_ids = [lo["objective_id"] for lo in enrichment["provisional_los"]]
    refined_ids = [lo["objective_id"] for lo in g0r_card["card"]["refined_los"]]

    # Identity backbone is preserved G0E -> G0R (no silent add/drop in the fixture),
    # which is what lets the two surfaces stay in lockstep across the kickoff beats.
    assert refined_ids == provisional_ids
