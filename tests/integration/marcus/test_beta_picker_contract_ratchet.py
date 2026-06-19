"""S0.4 integration-boundary ratchet (BETA charter D6; Murat/Mary P5).

Codifies the BETA picker contract CHAIN end-to-end so a future drift fails CI
here, not at a live trial:

    producer output key  ->  card candidate field  ->  `select` allowlist key

The Trial-4 cascade happened because no test asserted these boundaries together
(the woken-gate guard only checked template/shim existence). This pins:
- every picker gate in `_SELECTABLE_KEYS_BY_GATE` builds a card from a producer
  envelope and POPULATES its candidate field (producer -> card), and
- the same gate's `select` allowlist binds the selection key (card -> re-route),
so the surfacing and binding halves can never silently drift apart.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.marcus.orchestrator import production_runner as pr
from app.models.state.cache_state import CacheState
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState

# (gate, node, producer specialist, producer output, card candidate attr,
#  select key, expected candidate id surfaced)
_PICKER_CHAIN = [
    (
        "G4A",
        "11-gate",
        "enrique",
        {"voice_preview": {"voices": [{"voice_id": "vX", "voice_name": "X"}]}},
        "voice_candidates",
        "selected_voice_id",
        "vX",
    ),
    (
        "G2B",
        "07B-gate",
        "gary",
        {"gary_slide_output": [{"slide_id": "slide-01", "dispatch_variant": "A"}]},
        "variant_candidates",
        "selected_variant_id",
        "A",
    ),
]


def test_selectable_gates_are_exactly_the_picker_gates() -> None:
    assert set(pr._SELECTABLE_KEYS_BY_GATE) == {gate for gate, *_ in _PICKER_CHAIN}


@pytest.mark.parametrize(
    ("gate", "node", "specialist", "output", "cand_attr", "select_key", "expected"),
    _PICKER_CHAIN,
    ids=[c[0] for c in _PICKER_CHAIN],
)
def test_picker_contract_chain_holds(
    gate, node, specialist, output, cand_attr, select_key, expected, tmp_path: Path
) -> None:
    # 1) producer -> card: the card builder projects the producer output onto the
    #    candidate field.
    envelope = SimpleNamespace(
        contributions=[SimpleNamespace(specialist_id=specialist, output=output)]
    )
    card = pr._build_decision_card(
        gate_id=gate,
        trial_id=uuid4(),
        node_id=node,
        operator_id="operator_test",
        pending_nodes=[],
        artifact_paths=[],
        production_envelope=envelope,
        runs_root=tmp_path,
    )
    assert expected in getattr(card, cand_attr), (
        f"{gate}: producer output did not surface onto card.{cand_attr}"
    )

    # 2) card -> re-route: the gate's select allowlist binds the selection key.
    assert select_key in pr._SELECTABLE_KEYS_BY_GATE[gate], (
        f"{gate}: select allowlist missing {select_key}"
    )
    run_state = RunState(
        run_id=uuid4(),
        graph_version="v42",
        cache_state=CacheState(
            cache_prefix=json.dumps({"seed": 1}), entries_count=1, last_invalidated_at=None
        ),
    )
    verdict = OperatorVerdict(
        trial_id=uuid4(),
        verb="select",
        gate_id=gate,
        card_id=uuid4(),
        operator_id="operator_test",
        decision_card_digest="a" * 64,
        edit_payload={select_key: expected},
    )
    out = pr._apply_verdict_to_run_state(run_state, verdict)
    merged = json.loads(out.cache_state.cache_prefix)
    assert merged["seed"] == 1, f"{gate}: select clobbered an existing key"
    # the selection key bound somewhere reachable (top-level or nested voice_selection)
    bound = merged.get(select_key) or merged.get("voice_selection", {}).get(select_key)
    assert bound == expected, f"{gate}: select did not bind {select_key}={expected}"
