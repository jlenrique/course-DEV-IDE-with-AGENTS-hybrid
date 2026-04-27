from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
            )
        )
        return updated


def test_live_mode_mocked_openai_sets_evidence_true(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    assert envelope.production_clone_launch_evidence is True
    assert envelope.production_clone_launch_evidence_reason == "live-specialist-call-recorded"


def test_offline_mode_keeps_evidence_false(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        allow_offline_cost_report=True,
        pause_at_gates=False,
    )

    assert envelope.production_clone_launch_evidence is False


def test_live_mode_with_zero_specialist_calls_keeps_evidence_false(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=0,
        pause_at_gates=False,
    )

    assert envelope.production_clone_launch_evidence is False
    assert envelope.production_clone_launch_evidence_reason == "no-live-specialist-call-recorded"


def test_openai_without_langsmith_keeps_evidence_false(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    assert envelope.production_clone_launch_evidence is False
