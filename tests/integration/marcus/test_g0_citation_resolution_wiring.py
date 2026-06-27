"""DD3 attach + DD7 cache — citation resolution rides the g0-enrichment brick.

The resolver is wired INSIDE ``build_enrichment_result`` (after groundedness
flagging, before result construction) and threads ``citation_resolutions`` onto
the frozen ``G0EnrichmentResult``. DD7: resolution serializes into the SAME
existing fingerprint cache, so a corpus-keyed replay reads the FROZEN resolutions
with NO second dispatch. The live scite dispatch is replaced here by an injected
counting fake (DI, not a mock of the SUT).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID

from app.marcus.orchestrator import g0_enrichment_wiring as gw
from app.models.runtime.production_envelope import ProductionEnvelope

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS = REPO_ROOT / "tests" / "fixtures" / "pass0_citation_corpus"
# REAL captured scite dispatch response (live in-process Texas dispatch of the
# JAMA DOI 10.1001/jama.2019.13978, captured 2026-06-26) — NOT a synthetic/
# hand-built row. The seam under test (resolver -> DD3 attach -> DD7 cache) is
# thereby exercised with the actual scite ProviderResult shape.
SCITE_REAL_RESPONSE = CORPUS / "scite_jama_real_response.json"

# Texas retrieval contracts (the dispatch return shape) — pythonpath includes
# the texas scripts dir (pyproject [tool.pytest.ini_options].pythonpath).
sys.path.insert(0, str(REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts"))
from retrieval.contracts import ProviderResult, TexasRow  # noqa: E402


def _load_captured_scite_result() -> ProviderResult:
    """Reconstruct a ``ProviderResult`` from the REAL captured scite response."""
    data = json.loads(SCITE_REAL_RESPONSE.read_text(encoding="utf-8"))
    rows = [
        TexasRow(
            source_id=r["source_id"],
            provider=r["provider"],
            title=r["title"],
            provider_metadata=r["provider_metadata"],
        )
        for r in data["rows"]
    ]
    return ProviderResult(
        provider=data["provider"],
        rows=rows,
        acceptance_met=data["acceptance_met"],
        iterations_used=data["iterations_used"],
    )


def _counting_hit_dispatch(counter: dict[str, int]):
    # Returns the REAL captured scite response (not a hand-built row); the
    # counter still records each dispatch for the DD7 cache assertions.
    captured = _load_captured_scite_result()

    def _dispatch(_intent):
        counter["n"] += 1
        return captured

    return _dispatch


def test_dd3_build_enrichment_result_threads_resolutions() -> None:
    counter = {"n": 0}
    result = gw.build_enrichment_result(
        corpus_dir=CORPUS,
        dispatch_live=False,
        resolve_dispatch=_counting_hit_dispatch(counter),
    )
    resolved = [r for r in result.citation_resolutions if r.resolution_status == "resolved"]
    assert resolved, "the DOI-bearing reference component must resolve"
    assert resolved[0].doi == "10.1001/jama.2019.13978"
    assert resolved[0].resolved_ref["title"] == "Waste in the US Health Care System"
    assert counter["n"] >= 1


def test_dd3_no_resolution_without_dispatch_offline() -> None:
    # Offline (no live + no injected dispatch) -> resolution skipped, network-free.
    result = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    assert result.citation_resolutions == ()


def test_dd7_cache_replay_does_not_redispatch(tmp_path: Path) -> None:
    counter = {"n": 0}
    trial_id = UUID("a2345678-1234-4234-8234-123456789abc")
    dispatch = _counting_hit_dispatch(counter)

    first = gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=ProductionEnvelope(trial_id=trial_id),
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
        resolve_dispatch=dispatch,
    )
    contrib = first.get_contribution(
        gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
    )
    payload = contrib.output[gw.ENRICHMENT_RESULT_KEY]
    assert any(r["resolution_status"] == "resolved" for r in payload["citation_resolutions"])
    calls_after_first = counter["n"]
    assert calls_after_first >= 1

    # Second walk: FRESH envelope (no contribution -> not resume-skipped) but the
    # same trial_id + runs_root, so the fingerprint cache file is hit -> the
    # frozen resolutions replay with NO second dispatch (DD7).
    second = gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=ProductionEnvelope(trial_id=trial_id),
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
        resolve_dispatch=dispatch,
    )
    assert counter["n"] == calls_after_first, "cache hit must NOT re-dispatch (DD7)"
    contrib2 = second.get_contribution(
        gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
    )
    payload2 = contrib2.output[gw.ENRICHMENT_RESULT_KEY]
    assert payload2["citation_resolutions"] == payload["citation_resolutions"]
