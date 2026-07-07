"""Leg-2 (concierge-production-substrate): START walk emits NO motion.

Guardrail pin for the two-walk architecture: the START walk
(``run_production_trial``) halts at G1 (node 04) and NEVER reaches the motion
nodes 07D.5 (``motion_planner``) / 07E (``kira``). Those belong exclusively to
the CONTINUATION walk (resume/recover after G1).

The assertion is anchored on the SHARED dispatch site
``_dispatch_specialist_at_node`` (the single seam every specialist invocation
flows through) — NOT on per-walk gate-branch hooks — so it holds regardless of
which walk is executing. It also asserts no run-scoped ``motion/`` dir is
created by the start walk.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution

TRIAL_ID = UUID("12345678-1234-4234-8234-fedcba987654")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


@pytest.fixture(autouse=True)
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a — kill-switch / escape-hatch coverage (D-kill-switch).

    This suite's subject IS the G0-dormant path: with the G0-enrichment brick
    ASLEEP, the START walk first-pauses at G1 and dispatches no motion nodes. Pin
    ``MARCUS_G0_ENRICHMENT_ACTIVE`` explicitly OFF so this remains the kill-switch
    regression witness after 3b flips the default OFF->ON (the canonical G0E-first
    walk gets its own witness in 3b). The no-motion teeth are unchanged; only the
    env intent is now explicit. Explicit ``"0"`` survives the code-default flip.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


class _FakeAdapter:
    """Minimal dispatch adapter — records nothing itself; the spy below does."""

    def __init__(self) -> None:
        self.last_interrupts = [{"gate_id": "fake-specialist-gate"}]

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
    ) -> ProductionEnvelope:
        del base_state, dependency_map
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
                node_id=node_id,
            )
        )
        return updated


def test_start_walk_halts_at_g1_and_dispatches_no_motion_nodes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", lambda: _FakeAdapter()
    )

    # Spy the SINGLE shared dispatch seam: record every (node_id, specialist_id)
    # the start walk actually dispatches, then delegate to the real function.
    dispatched: list[tuple[str, str]] = []
    real_dispatch = production_runner._dispatch_specialist_at_node

    def _spy(*args, **kwargs):
        dispatched.append((kwargs["node"].id, kwargs["specialist_id"]))
        return real_dispatch(*args, **kwargs)

    monkeypatch.setattr(production_runner, "_dispatch_specialist_at_node", _spy)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    # 1. START walk halts at G1 — it does not run past the first gate.
    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G1"

    # 2. Anchored on the shared dispatch site: neither motion node was dispatched.
    dispatched_node_ids = {node_id for node_id, _ in dispatched}
    dispatched_specialists = {spec for _, spec in dispatched}
    assert "07D.5" not in dispatched_node_ids
    assert "07E" not in dispatched_node_ids
    assert "motion_planner" not in dispatched_specialists
    assert "kira" not in dispatched_specialists

    # 3. No run-scoped motion/ dir is created by the start walk.
    assert not (tmp_path / str(TRIAL_ID) / "motion").exists()
