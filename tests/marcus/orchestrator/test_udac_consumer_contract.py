"""UDAC v1 RED-first floor — consumer registry, USE anti-tautology, both-walks parity.

Covers the §F amendments that live above the neutral model:
  - MT-1 USE anti-tautology, parametrized over the consumer REGISTRY: mutate an
    upstream sentinel → assert mutated-PRESENT and constant/pre-mutation-ABSENT.
  - MT-2 "does not consume X" byte-identical tripwire for the DECLARED-non-consuming
    consumers (compositor/motion + the genuine enrique available_only) at the shared
    dispatch payload seam, with a USED-consumer positive control proving the seam is
    not vacuous.
  - MT-4 earned-`used` coverage parity: every declared `used` has an anti-tautology
    test; every `available_only` has a byte-identical test.
  - M-5 both-walks parity + M-3 rehydrate-reconcile via the gate writer.
  - M-4 fail-loud dispatch guard + flag-OFF byte-identical no-op.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.marcus.lesson_plan.run_asset_index import (
    CONSUMER_REGISTRY,
    AssetResolutionError,
    AssetUsage,
    DigestAlgo,
    load_rai,
    recompute_digest_from_disk,
)
from app.marcus.lesson_plan.workbook_enrichment import (
    project_enrichment_to_workbook_inputs,
)
from app.marcus.orchestrator import udac_wiring
from app.marcus.orchestrator.enrichment_consumption import (
    project_deck_enrichment_hint,
    project_role_derived_voice_by_slide,
)
from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "p5_workbook_corpus" / "live_enriched_result_card.json"
)
JAMA_URL = "https://doi.org/10.1001/jama.2019.13978"
JAMA_CITATION_ID = "src-001-c007"


@pytest.fixture(autouse=True)
def _udac_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(udac_wiring.MARCUS_UDAC_ACTIVE_ENV, "1")


def _fixture_card() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _citation(card: dict[str, Any], component_id: str) -> dict[str, Any]:
    for cit in card["citation_resolutions"]:
        if cit["component_id"] == component_id:
            return cit
    raise KeyError(component_id)


def _seed_card(role: str) -> dict[str, Any]:
    """A minimal seed-producing card for the Irene role-derived voice projection."""
    return {
        "typed_components": [
            {"component_id": "n1", "source_type": "narration", "locator": "Slide 1"}
        ],
        "pedagogy_annotations": [
            {"component_id": "n1", "teachable": True, "pedagogical_role": role}
        ],
        "provisional_los": [],
        "citation_resolutions": [],
    }


def _write_g0(run_dir: Path, card: dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "g0-enrichment.json").write_text(json.dumps(card), encoding="utf-8")


# ===========================================================================
# MT-1 — USE anti-tautology, per registry `used` consumer
# ===========================================================================


def test_use_workbook_consumes_g0_enrichment() -> None:
    """workbook (USED): a mutated citation URL projects into further-reading; the
    pre-mutation constant URL is ABSENT (mutated-present AND constant-absent)."""
    sentinel = "https://doi.org/10.5555/udac-workbook-use-probe"
    card = _fixture_card()
    _citation(card, JAMA_CITATION_ID)["resolved_ref"]["access_url"] = sentinel

    projection = project_enrichment_to_workbook_inputs(card)
    locators = {e.locator for e in projection.further_reading}
    assert sentinel in locators  # mutated value present
    assert JAMA_URL not in locators  # pre-mutation value absent


def test_use_gary_consumes_g0_enrichment() -> None:
    """gary (USED): a mutated LO statement appears verbatim in the deck hint; the
    pre-mutation statement is ABSENT."""
    card = _fixture_card()
    original = card["provisional_los"][0]["statement"]
    sentinel = "UDAC-GARY-USE-SENTINEL distinguishing administrative redesign"
    card["provisional_los"][0]["statement"] = sentinel

    hint = project_deck_enrichment_hint(card)
    assert hint is not None
    assert sentinel in hint  # mutated value present
    assert original not in hint  # pre-mutation value absent


def test_use_irene_consumes_g0_enrichment() -> None:
    """irene (USED): mutating the narration component's pedagogical_role flips the
    derived slide pace; the pre-mutation pace is ABSENT for that slide."""
    slower = project_role_derived_voice_by_slide(_seed_card("worked_example"))
    assert slower["1"]["pace"] == "slower"  # role-derived value

    neutral = project_role_derived_voice_by_slide(_seed_card("definition"))
    assert neutral["1"]["pace"] == "neutral"  # mutated value present
    assert neutral["1"]["pace"] != slower["1"]["pace"]  # pre-mutation value absent


# ===========================================================================
# MT-2 — "does not consume X" byte-identical tripwire (available_only)
# ===========================================================================

_AVAILABLE_ONLY = [
    cid
    for cid, decl in CONSUMER_REGISTRY.items()
    if all(c.usage is AssetUsage.AVAILABLE_ONLY for c in decl.consumes)
]


@pytest.mark.parametrize("specialist_id", _AVAILABLE_ONLY)
def test_tripwire_non_consumer_payload_byte_identical(
    specialist_id: str, tmp_path: Path
) -> None:
    """A DECLARED-non-consuming consumer's dispatch payload is BYTE-IDENTICAL when
    g0-enrichment.json is mutated — goes RED the day someone wires consumption
    without updating the declaration (MT-2). Non-vacuity: the g0 bytes really change."""
    runs_root = tmp_path
    trial_id = "tripwire-trial"
    run_dir = runs_root / trial_id

    _write_g0(run_dir, {"typed_components": [], "marker": "before"})
    before = _runner_payload_for_specialist(
        specialist_id=specialist_id,
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=trial_id,
    )
    g0_before = (run_dir / "g0-enrichment.json").read_bytes()

    _write_g0(run_dir, {"typed_components": [{"id": "x"}], "marker": "AFTER-MUTATION"})
    after = _runner_payload_for_specialist(
        specialist_id=specialist_id,
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=trial_id,
    )
    g0_after = (run_dir / "g0-enrichment.json").read_bytes()

    assert g0_before != g0_after  # the upstream asset genuinely changed
    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)


def test_tripwire_positive_control_used_consumer_payload_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Positive control: a USED consumer (irene) DOES change its dispatch payload
    under g0 mutation at the same seam — proving the tripwire above is not vacuous."""
    monkeypatch.setenv("MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE", "1")
    runs_root = tmp_path
    trial_id = "posctl-trial"
    run_dir = runs_root / trial_id

    _write_g0(run_dir, _seed_card("worked_example"))
    before = _runner_payload_for_specialist(
        specialist_id="irene",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=trial_id,
    )
    _write_g0(run_dir, _seed_card("definition"))
    after = _runner_payload_for_specialist(
        specialist_id="irene",
        directive_path=None,
        bundle_dir=None,
        runs_root=runs_root,
        trial_id=trial_id,
    )
    assert before is not None and after is not None
    assert json.dumps(before, sort_keys=True) != json.dumps(after, sort_keys=True)


# ===========================================================================
# MT-4 — earned-`used` coverage parity
# ===========================================================================

# Maps each registry consumer to the test proving its declaration. A `used`
# consumer MUST have an anti-tautology test; an `available_only` consumer MUST have
# a byte-identical tripwire. This dict is the parity ledger.
USE_ANTI_TAUTOLOGY_TESTS = {
    "workbook": "test_use_workbook_consumes_g0_enrichment",
    "gary": "test_use_gary_consumes_g0_enrichment",
    "irene": "test_use_irene_consumes_g0_enrichment",
}
BYTE_IDENTICAL_TESTS = {
    "enrique": "test_tripwire_non_consumer_payload_byte_identical",
    "compositor": "test_tripwire_non_consumer_payload_byte_identical",
    "kira": "test_tripwire_non_consumer_payload_byte_identical",
}


def test_mt4_earned_used_coverage_parity() -> None:
    """FAIL if any declared `used` lacks an anti-tautology test, or any
    `available_only` lacks a byte-identical test."""
    module_globals = globals()
    for consumer_id, decl in CONSUMER_REGISTRY.items():
        uses_any = any(c.usage is AssetUsage.USED for c in decl.consumes)
        if uses_any:
            test_name = USE_ANTI_TAUTOLOGY_TESTS.get(consumer_id)
            assert test_name is not None, (
                f"consumer {consumer_id!r} declares a `used` asset but has no "
                "anti-tautology test in the parity ledger"
            )
            assert callable(module_globals.get(test_name))
        else:
            test_name = BYTE_IDENTICAL_TESTS.get(consumer_id)
            assert test_name is not None, (
                f"consumer {consumer_id!r} is available_only but has no "
                "byte-identical tripwire in the parity ledger"
            )
            assert callable(module_globals.get(test_name))
            assert consumer_id in _AVAILABLE_ONLY  # actually parametrized above


# ===========================================================================
# M-5 both-walks parity + M-3 rehydrate-reconcile (gate writer)
# ===========================================================================


def test_both_walks_parity_ratified_at_stable_across_resume(tmp_path: Path) -> None:
    """ratified_at is identical whether a gate clears on the start walk or is
    re-crossed on the continuation/recover walk (M-5); the RAI rehydrates from disk
    and reconciles monotonically (M-3)."""
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [{"id": "c1"}], "corpus_fingerprint": "fp1"})

    # Start-walk crossing of G0E.
    idx1 = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    assert idx1 is not None
    first_at = idx1.get("g0-enrichment").ratified_at
    assert idx1.get("g0-enrichment").derived_from == "fp1"  # TX-4 trust chain

    # Continuation/recover walk re-crosses the SAME gate (rehydrate from disk).
    idx2 = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    assert idx2.get("g0-enrichment").ratified_at == first_at  # not regressed/duplicated

    # The on-disk RAI is identical across the resume.
    reloaded = load_rai(run_dir)
    assert reloaded.get("g0-enrichment").ratified_at == first_at


def test_gate_writer_records_second_gate_on_continuation(tmp_path: Path) -> None:
    """A later gate (G0R) ratifies its own asset on the continuation walk, alongside
    the G0E asset stamped earlier — both carry independent ratified_at. (G0R is the
    asleep/offline-branch case F3 now records on every branch.)"""
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [], "corpus_fingerprint": "fp"})
    udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)

    (run_dir / "ratified-los.json").write_text(
        json.dumps({"objectives": ["lo-1", "lo-2"]}), encoding="utf-8"
    )
    idx = udac_wiring.record_gate_ratification(gate_code="G0R", run_dir=run_dir)
    assert set(idx.entries) == {"g0-enrichment", "ratified-los"}
    assert idx.get("ratified-los").produced_by_node == "G0R"


def test_gate_writer_skips_unproduced_asset(tmp_path: Path) -> None:
    """A gate whose asset never landed on disk records NOTHING (never fabricates) —
    the harmless no-op that makes F3's call-on-every-branch safe."""
    idx = udac_wiring.record_gate_ratification(gate_code="G0R", run_dir=tmp_path)
    assert idx is None or "ratified-los" not in (idx.entries if idx else {})


# ===========================================================================
# F1 — own-gate additive re-pin (re-cross a GROWN asset: bump, no stale, no crash)
# ===========================================================================


def test_f1_own_gate_recross_grown_asset_repins_no_crash(tmp_path: Path) -> None:
    """Cross G0E (rev0) → grow g0-enrichment.json on disk → re-cross G0E (recover):
    revision BUMPS, NO stale-halt, NO crash; a consumer then resolves it cleanly."""
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [{"id": "c1"}], "corpus_fingerprint": "fp"})
    idx0 = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    assert idx0.get("g0-enrichment").revision == 0
    at0 = idx0.get("g0-enrichment").ratified_at

    # Legitimately grow the asset at its OWN gate (P2/P3 layer / one-process re-freeze).
    _write_g0(run_dir, {
        "typed_components": [{"id": "c1"}],
        "corpus_fingerprint": "fp",
        "citation_resolutions": [{"component_id": "c1", "resolution_status": "resolved"}],
    })
    # Re-cross G0E on the recover walk — must NOT raise (own-gate = additive, not stale).
    idx1 = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    assert idx1.get("g0-enrichment").revision == 1  # bumped
    assert idx1.get("g0-enrichment").ratified_at != at0  # re-pinned

    # A consumer resolving the grown, current asset succeeds (no false-stale).
    resolved = udac_wiring.resolve_consumed_assets(specialist_id="workbook", run_dir=run_dir)
    assert resolved["g0-enrichment"].revision == 1
    assert resolved["g0-enrichment"].legacy_mode.value == "none"


def test_f1_idempotent_recross_unchanged_no_rewrite_no_bump(tmp_path: Path) -> None:
    """An unchanged re-cross is an idempotent no-op: same revision, ratified_at
    preserved, no torn temp file (Blind-F2)."""
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [{"id": "c1"}]})
    idx0 = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    at0 = idx0.get("g0-enrichment").ratified_at
    idx1 = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    assert idx1.get("g0-enrichment").revision == 0
    assert idx1.get("g0-enrichment").ratified_at == at0
    assert not list(run_dir.glob("run-asset-index.json.*.tmp"))


def test_f1_gate_writer_never_crashes_on_corrupt_asset(tmp_path: Path) -> None:
    """A torn/corrupt asset at a gate is SKIPPED by the recorder (never an uncaught
    crash of the walk) — fail-loud is the consumer's job, not the recorder's (F1)."""
    run_dir = tmp_path
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "g0-enrichment.json").write_bytes(b"{ torn")  # corrupt at the gate
    idx = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)  # no raise
    assert idx is None or "g0-enrichment" not in (idx.entries if idx else {})


def test_f1_gate_writer_survives_corrupt_rai(tmp_path: Path) -> None:
    """A corrupt on-disk RAI does not crash the recorder; it is left intact for the
    consumer guard to fail-loud on (not clobbered)."""
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [{"id": "c1"}]})
    (run_dir / "run-asset-index.json").write_text("{ broken", encoding="utf-8")
    idx = udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    assert idx is None  # skipped, no overwrite, no crash
    assert (run_dir / "run-asset-index.json").read_text(encoding="utf-8") == "{ broken"


# ===========================================================================
# M-4 fail-loud dispatch guard + flag-OFF byte-identical
# ===========================================================================


def test_dispatch_guard_raises_on_stale_ratified_asset(tmp_path: Path) -> None:
    """A consumer dispatched against a STALE ratified asset raises
    AssetResolutionError (routed through the runner's recoverable pause)."""
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [{"id": "c1"}]})
    udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)

    # Corrupt the asset after ratification.
    (run_dir / "g0-enrichment.json").write_text(json.dumps({"typed_components": []}), "utf-8")
    with pytest.raises(AssetResolutionError):
        udac_wiring.resolve_consumed_assets(specialist_id="workbook", run_dir=run_dir)


def test_dispatch_guard_resolves_when_fresh(tmp_path: Path) -> None:
    run_dir = tmp_path
    _write_g0(run_dir, {"typed_components": [{"id": "c1"}]})
    udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=run_dir)
    resolved = udac_wiring.resolve_consumed_assets(specialist_id="workbook", run_dir=run_dir)
    assert resolved is not None
    assert resolved["g0-enrichment"].digest == recompute_digest_from_disk(
        run_dir / "g0-enrichment.json", DigestAlgo.CANONICAL_SHA256
    )


def test_dispatch_guard_noop_for_non_registered_specialist(tmp_path: Path) -> None:
    _write_g0(tmp_path, {"typed_components": []})
    udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=tmp_path)
    assert udac_wiring.resolve_consumed_assets(specialist_id="texas", run_dir=tmp_path) is None


def test_flag_off_is_byte_identical_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """UDAC OFF → the gate writer produces no RAI and the reader is a no-op
    (existing pipeline byte-identical)."""
    monkeypatch.delenv(udac_wiring.MARCUS_UDAC_ACTIVE_ENV, raising=False)
    _write_g0(tmp_path, {"typed_components": [{"id": "c1"}]})
    assert udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=tmp_path) is None
    assert not (tmp_path / "run-asset-index.json").exists()
    assert udac_wiring.resolve_consumed_assets(specialist_id="workbook", run_dir=tmp_path) is None
