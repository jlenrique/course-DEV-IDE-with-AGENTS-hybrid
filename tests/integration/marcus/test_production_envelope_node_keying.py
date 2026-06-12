"""S2 envelope v2 ratchets — per-node contribution keying (SCP 2026-06-11).

Pins, per Amelia + Murat's regression shape:
1. Legacy v1 envelopes (real bytes from frozen trial 50b7d353) round-trip
   losslessly with ``node_id is None`` on every row — and the RESUME path
   rejects them loudly (never half-reads).
2. Multi-node specialists accumulate one contribution per manifest node —
   the per-specialist Path-Z rule silently skipped irene_pass1's §05/§05B
   jobs in Trial-3 attempt-4 (fifth A23/P5 instance).
3. Same-node retry overwrites with attempt provenance — never duplicates.
4. The dispatch adapter's duplicate guard is node-aware in the same change
   as the walker skip-rule (the live-crash trap Amelia named).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.marcus.orchestrator.dispatch_adapter import (
    ProductionDispatchAdapter,
    ProductionDispatchAdapterError,
)
from app.marcus.orchestrator.production_runner import LegacyEnvelopeSchemaError
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
LEGACY_ENVELOPE_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "integration" / "marcus" / "legacy_envelope_50b7d353.json"
)
LEGACY_RUN_DIR = (
    REPO_ROOT / "state" / "config" / "runs" / "50b7d353-d10d-45d7-a0cc-7a4caa2dd572"
)


def _contribution(
    specialist_id: str, node_id: str | None = None, *, marker: str = "x"
) -> SpecialistContribution:
    return SpecialistContribution.from_output(
        specialist_id=specialist_id,
        output={"specialist_id": specialist_id, "marker": marker},
        model_used="gpt-5-nano",
        node_id=node_id,
    )


def test_legacy_v1_envelope_round_trips_with_null_node_ids() -> None:
    text = LEGACY_ENVELOPE_FIXTURE.read_text(encoding="utf-8-sig")
    raw = json.loads(text)
    # JSON-mode validation (strict model: python-dict mode rejects string
    # UUIDs/datetimes — same mode the resume path uses).
    envelope = ProductionEnvelope.model_validate_json(text)
    assert envelope.schema_version == "production-envelope.v1"
    assert len(envelope.contributions) == 6
    assert all(c.node_id is None for c in envelope.contributions)
    assert all(c.attempt == 1 for c in envelope.contributions)
    # Digests survive the round-trip untouched (frozen-evidence discipline).
    redumped = envelope.model_dump(mode="json")
    assert [c["output_digest"] for c in redumped["contributions"]] == [
        c["output_digest"] for c in raw["contributions"]
    ]


def test_new_envelopes_default_to_v2() -> None:
    envelope = ProductionEnvelope(trial_id=uuid4())
    assert envelope.schema_version == "production-envelope.v2"


def test_multi_node_specialist_accumulates_distinct_contributions() -> None:
    envelope = ProductionEnvelope(trial_id=uuid4())
    for node_id in ("04A", "05", "05B"):
        envelope.add_contribution(_contribution("irene_pass1", node_id))
    assert len(envelope.contributions) == 3
    assert [c.node_id for c in envelope.contributions] == ["04A", "05", "05B"]
    assert envelope.get_contribution("irene_pass1", node_id="05B") is not None


def test_same_node_retry_overwrites_with_attempt_provenance() -> None:
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(_contribution("gary", "07", marker="first"))
    envelope.add_contribution(_contribution("gary", "07", marker="second"))
    assert len(envelope.contributions) == 1
    survivor = envelope.contributions[0]
    assert survivor.attempt == 2
    assert survivor.output["marker"] == "second"


def test_get_contribution_node_semantics() -> None:
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(_contribution("quinn_r", "07B", marker="variant"))
    envelope.add_contribution(_contribution("quinn_r", "13", marker="g5"))
    # node-pinned lookups
    assert envelope.get_contribution("quinn_r", node_id="13").output["marker"] == "g5"
    assert envelope.get_contribution("quinn_r", node_id="08B") is None
    # node_id=None keeps legacy any-node semantics ("contributed at all?")
    assert envelope.get_contribution("quinn_r") is not None
    # dependency consumers get the most recent output
    assert envelope.latest_for_specialist("quinn_r").output["marker"] == "g5"


def test_adapter_duplicate_guard_is_node_aware() -> None:
    adapter = ProductionDispatchAdapter(graph_builders={})
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(_contribution("irene_pass1", "04A"))
    # Same (specialist, node): the guard refuses BEFORE graph compilation.
    with pytest.raises(ValueError, match="already has contribution"):
        adapter.invoke_specialist(
            specialist_id="irene_pass1",
            envelope=envelope,
            dependency_map={},
            cost_usd=0.0,
            node_id="04A",
        )
    # Different node: the guard passes — proof is reaching the registry
    # lookup (empty here), NOT the duplicate ValueError.
    with pytest.raises(ProductionDispatchAdapterError, match="absent from dispatch registry"):
        adapter.invoke_specialist(
            specialist_id="irene_pass1",
            envelope=envelope,
            dependency_map={},
            cost_usd=0.0,
            node_id="05",
        )


def test_resume_rejects_legacy_v1_envelope_loudly(tmp_path: Path) -> None:
    """Characterization against the REAL frozen attempt-4 run dir: the new
    reader rejects v1 explicitly with a named error — never half-reads."""
    from app.marcus.orchestrator import production_runner
    from app.models.state.operator_verdict import OperatorVerdict

    trial_id = UUID("50b7d353-d10d-45d7-a0cc-7a4caa2dd572")
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    for name in ("run.json", "checkpoint.json"):
        shutil.copy2(LEGACY_RUN_DIR / name, run_dir / name)
    verdict = OperatorVerdict(
        trial_id=trial_id,
        gate_id="G2C",
        card_id=UUID("b2bf01a6-9ce0-424f-8a3e-b83b012941fd"),
        operator_id="juanl",
        verb="approve",
        decision_card_digest="760fec174acac3fb92bc7d6d8b9d00877025319715ad12715fb1d4960404afb2",
    )
    with pytest.raises(LegacyEnvelopeSchemaError, match="not resumable"):
        production_runner.resume_production_trial(
            trial_id=trial_id,
            verdict=verdict,
            runs_root=tmp_path,
        )
