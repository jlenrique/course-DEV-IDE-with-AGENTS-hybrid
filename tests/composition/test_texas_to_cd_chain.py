from __future__ import annotations

from uuid import UUID

import pytest

from tests.composition.composed_specialist_chain_harness import (
    ComposedSpecialistChainHarness,
    fake_make_chat_model,
)

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


@pytest.mark.parametrize("trial_id", [TRIAL_ID])
def test_texas_to_cd_chain_accumulates_envelope_and_threads_dependency(
    trial_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.specialists.texas.graph.make_chat_model", fake_make_chat_model)
    monkeypatch.setattr("app.specialists.cd.graph.make_chat_model", fake_make_chat_model)
    monkeypatch.setattr("app.specialists.cd.graph.assert_sanctum_lock", lambda: None)

    harness = ComposedSpecialistChainHarness(trial_id)
    envelope = harness.run_texas_to_cd()

    assert [item.specialist_id for item in envelope.contributions] == ["texas", "cd"]
    texas = envelope.get_contribution("texas")
    cd = envelope.get_contribution("cd")
    assert texas is not None
    assert cd is not None
    assert texas.output["status"] == "complete"
    assert cd.output["cd_directive"]["schema_version"] == "1.0"
    assert harness.cd_input_payload == {"source_bundle": texas.output}
    assert harness.adapter.last_interrupts
