"""Pin: generate_deck polls on Gamma's camelCase ``generationId`` ack.

Trial-3 cycle-2 root cause (2026-06-12): the POST /generations ack carries
``generationId``; generate_deck read only ``id``/``generation_id``, never
polled, returned the bare ack (no exportUrl), and orphaned a real
server-side generation. Companion act-layer pins live at
tests/specialists/gary/test_gary_generation_id_fail_loud.py.
"""

from __future__ import annotations

from scripts.api_clients.gamma_client import GammaClient


def test_generate_deck_polls_on_camelcase_generation_id(monkeypatch) -> None:
    client = GammaClient.__new__(GammaClient)  # no network setup
    completed = {
        "generationId": "g-cam-1",
        "status": "completed",
        "exportUrl": "https://assets.api.gamma.app/export/image/fake.zip",
    }
    monkeypatch.setattr(
        GammaClient, "generate", lambda self, *a, **k: {"generationId": "g-cam-1"}
    )
    waited: list[str] = []

    def _wait(self, generation_id, *a, **k):
        waited.append(generation_id)
        return dict(completed)

    monkeypatch.setattr(GammaClient, "wait_for_generation", _wait)

    result = client.generate_deck("two slides please")

    assert waited == ["g-cam-1"], "camelCase ack must trigger the poll"
    assert result["exportUrl"] == completed["exportUrl"]
    assert result["generation_id"] == "g-cam-1"  # setdefault normalization
