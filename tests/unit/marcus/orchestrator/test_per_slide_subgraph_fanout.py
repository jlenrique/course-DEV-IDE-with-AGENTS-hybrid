from __future__ import annotations

from app.marcus.orchestrator.per_slide_subgraph import (
    fan_out_per_slide,
    join_per_slide_results,
    per_slide_review_subgraph,
)


def test_one_slide_creates_one_subgraph_send() -> None:
    sends = fan_out_per_slide(gate_id="G2B", slides=[{"title": "Slide 1"}])

    assert len(sends) == 1
    assert sends[0].node == "per_slide_review_subgraph"
    assert sends[0].arg["slide_index"] == 0


def test_n_slides_create_n_subgraph_sends() -> None:
    sends = fan_out_per_slide(gate_id="G3B", slides=[{}, {}, {}])

    assert [send.arg["slide_index"] for send in sends] == [0, 1, 2]


def test_each_slide_has_isolated_checkpoint_boundary() -> None:
    sends = fan_out_per_slide(gate_id="G2F-merged", slides=[{}, {}])

    assert {send.arg["checkpoint_ns"] for send in sends} == {
        "G2F-merged/slide-0",
        "G2F-merged/slide-1",
    }


def test_parent_join_orders_out_of_order_slide_results() -> None:
    joined = join_per_slide_results(
        [
            {"slide_index": 2, "operator_decision": {"decision": "approve"}},
            {"slide_index": 0, "operator_decision": {"decision": "revise"}},
            {"slide_index": 1, "operator_decision": {"decision": "skip"}},
        ],
        expected_count=3,
    )

    assert [item["slide_index"] for item in joined] == [0, 1, 2]


def test_subgraph_interrupts_once_for_one_slide() -> None:
    seen: list[dict[str, object]] = []

    def fake_interrupt(payload: dict[str, object]) -> dict[str, str]:
        seen.append(payload)
        return {"decision": "approve"}

    result = per_slide_review_subgraph(
        {
            "gate_id": "G2B",
            "slide_index": 0,
            "slide": {"title": "Slide 1"},
            "checkpoint_ns": "G2B/slide-0",
        },
        interrupt_fn=fake_interrupt,
    )

    assert len(seen) == 1
    assert result["operator_decision"] == {"decision": "approve"}
