"""Replay the enrolled ``ask-b-hot-topics-call.v1`` (07W.4) witnesses.

FIRST Scite-canonical band research-call family (38-2 / A-6): the witness is
a CALL JOURNAL (idempotency key + provider/config fingerprint + raw rows),
not a writer-output capture — a deliberate small shape delta from the three
existing per-family modules. Completed witnesses replay the full
journal→output chain with zero provider calls via the owned wiring seam;
frozen failed attempts replay the ambiguity classification.

Zero-witness rule state machine (D3): the family enrolls IN the 38-2 story
diff with its first witness OWED by probe ``probe-38-2-ask-b-hot-topics-001``
(``disposition: pending``). The pending state is machine-asserted below —
never silent — and the replay loop consumes only ``disposition: enrolled``
rows, so STRICT pre-flight stays green while the witness is owed.
"""

from __future__ import annotations

import json
from typing import Any

from tests.live_witness_replay.registry import family, skip_or_fail, witness_path

FAMILY = "ask-b-hot-topics-call.v1"
OWING_PROBE = "probe-38-2-ask-b-hot-topics-001"


def _rows() -> list[dict[str, Any]]:
    return [row for row in family(FAMILY)["witnesses"] if row["disposition"] == "enrolled"]


def _pending_rows() -> list[dict[str, Any]]:
    return [row for row in family(FAMILY)["witnesses"] if row["disposition"] == "pending"]


def test_family_enrolled_at_exact_node() -> None:
    assert family(FAMILY)["node_id"] == "07W.4"


def test_witness_state_is_explicit_never_silent() -> None:
    """Either a COMPLETED enrolled witness exists (post-probe), or the pending
    row names the owing probe (pre-probe). A family with neither would claim
    replay coverage it does not have."""
    enrolled = _rows()
    if enrolled:
        assert any(row["state"] == "completed" for row in enrolled), (
            f"{FAMILY} has enrolled witnesses but no COMPLETED one — the call "
            "family may not claim replay-green off ambiguity shapes alone"
        )
        return
    pending = _pending_rows()
    assert pending, (
        f"{FAMILY} has neither an enrolled witness nor an explicit pending row "
        f"owed by {OWING_PROBE}"
    )
    assert any(
        row.get("capture", {}).get("owed_by_probe") == OWING_PROBE for row in pending
    )


def test_enrolled_witnesses_replay_with_zero_provider_calls() -> None:
    """Loop (not parametrize) so the owed-witness state yields a PASS on the
    explicit pending pin above instead of an empty-parameter-set skip that
    STRICT could not distinguish from coverage."""
    for row in _rows():
        path = witness_path(row)
        if not path.is_file():
            skip_or_fail(f"witness journal missing on disk: {row['id']}")
        journal = json.loads(path.read_text(encoding="utf-8"))
        assert journal["schema_version"] == FAMILY
        assert journal["state"] == row["state"]
        capture = row.get("capture") or {}
        if "idempotency_key" in capture:
            assert journal["idempotency_key"] == capture["idempotency_key"]
        if row["state"] == "call_in_progress":
            # Frozen failed attempt: the ambiguity shape stands — a completed
            # payload must never have appeared on this coordinate.
            assert "output" not in journal
            assert "raw_rows" not in journal
            continue
        # Completed witness: replay the full journal→output chain with zero
        # provider calls through the owned wiring machinery.
        from app.marcus.lesson_plan.ask_b_hot_topics import (
            AskBRetrievalScopeV1,
        )
        from app.marcus.orchestrator import ask_b_research_wiring as wiring

        scope = AskBRetrievalScopeV1.model_validate_json(
            json.dumps(journal["scope"], separators=(",", ":")), strict=True
        )
        if "provider_config_fingerprint" in capture:
            assert scope.provider_config_fingerprint == capture[
                "provider_config_fingerprint"
            ]
        output, records = wiring._build_completed(
            scope,
            raw_rows=journal["raw_rows"],
            provider_iterations=tuple(journal["provider_iterations"]),
            refinement_logs=tuple(journal["refinement_logs"]),
            provider_outcomes=tuple(journal["provider_outcomes"]),
            provider_receipts=tuple(journal["provider_receipts"]),
        )
        assert journal["normalization_records"] == records
        assert journal["output"] == output.model_dump(mode="json")
        assert journal["output_digest"] == output.output_digest
