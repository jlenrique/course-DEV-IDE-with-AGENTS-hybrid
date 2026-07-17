"""Story 41-1: resume/recover/resume-batch live-env preflight — fail loud at the front door.

Root cause (frozen trial ``bc747b51``): the operator resumed a paid production
run from a fresh shell with no ``OPENAI_API_KEY``. ``start_trial`` enforces a
live-env preflight; ``resume_trial`` / ``recover_trial`` / ``resume_batch_trial``
did not, so the keyless resume silently skipped live specialist dispatch and the
run stranded three nodes later with a misattributed ``builder.gary.upstream-missing``
error. These tests pin the parity fix: a keyless live continuation now raises a
``RuntimeError`` BEFORE ``_continue_production_walk`` is entered.

Hermetic: no live LLM, no network. The persisted pause records (checkpoint.json /
error-pause.json / provider-batch-pause.json) are constructed on ``tmp_path`` and
``resume_production_trial`` / ``recover_production_trial`` / ``resume_batch_production_trial``
are monkeypatched to a fake so a preflight PASS never spends a real call.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.marcus.cli import trial as trial_module
from app.marcus.orchestrator.production_runner import _has_live_openai
from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.state.component_selection import ComponentSelection
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState

TRIAL_ID = UUID("bc747b51-7009-4742-9f65-8de6abc29ca4")
FROZEN_RUN_DIR = (
    Path(__file__).resolve().parents[3]
    / "state"
    / "config"
    / "runs"
    / "bc747b51-7009-4742-9f65-8de6abc29ca4"
)


def _live_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set the full live env (OPENAI + LangSmith) so the preflight passes."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-live-key")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test-key")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")


def _keyless_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reproduce the fresh-shell resume: no OPENAI_API_KEY, no LangSmith env."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    # The pre-existing _load_env_if_available() must not re-source a key from a
    # repo .env — the fix is to FAIL LOUD, not to mask the misconfiguration.
    monkeypatch.setattr(trial_module, "_load_env_if_available", lambda: None)


def _make_run_state() -> RunState:
    return RunState(
        run_id=TRIAL_ID,
        graph_version="v42",
        status="running",
        component_selection=ComponentSelection(deck=True),
    )


def _fake_envelope(status: str, **overrides) -> ProductionTrialEnvelope:
    fields: dict = {
        "trial_id": TRIAL_ID,
        "preset": "production",
        "corpus_path": "legacy",
        "operator_id": "operator_test",
        "started_at": datetime.now(UTC),
        "status": status,
        "production_clone_launch_evidence": False,
        "production_envelope": ProductionEnvelope(trial_id=TRIAL_ID),
    }
    fields.update(overrides)
    return ProductionTrialEnvelope(**fields)


def _seed_pause(
    runs_root: Path,
    *,
    pause_filename: str,
    allow_offline_cost_report: bool,
    extra: dict | None = None,
) -> Path:
    """Persist a minimal paused-run record carrying the runner's offline flag."""
    run_dir = runs_root / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    record: dict = {
        "trial_id": str(TRIAL_ID),
        "run_state": _make_run_state().model_dump(mode="json"),
        "runner": {"allow_offline_cost_report": allow_offline_cost_report},
    }
    if extra:
        record.update(extra)
    (run_dir / pause_filename).write_text(json.dumps(record), encoding="utf-8")
    return run_dir


# ---------------------------------------------------------------------------
# AC-1: keyless resume/recover raises at the front door (before the walk)
# ---------------------------------------------------------------------------


def test_ac1_keyless_recover_raises_at_front_door(tmp_path: Path, monkeypatch) -> None:
    _keyless_env(monkeypatch)
    _seed_pause(tmp_path, pause_filename="error-pause.json", allow_offline_cost_report=False)

    # Guard: if the preflight is missing, the walk would run — make the walk
    # blow up distinctively so a passing test can only mean the FRONT-DOOR raise.
    def _walk_ran(**kwargs):
        raise AssertionError(
            "recover_production_trial must NOT be reached on a keyless live resume"
        )

    monkeypatch.setattr(trial_module, "recover_production_trial", _walk_ran)

    with pytest.raises(RuntimeError) as exc:
        trial_module.recover_trial(trial_id=TRIAL_ID, runs_root=tmp_path)

    msg = str(exc.value)
    assert "OPENAI_API_KEY" in msg
    assert "recover" in msg
    assert str(TRIAL_ID) in msg
    assert "--allow-offline-cost-report" in msg


def test_ac1_keyless_resume_raises_at_front_door(tmp_path: Path, monkeypatch) -> None:
    _keyless_env(monkeypatch)
    _seed_pause(tmp_path, pause_filename="checkpoint.json", allow_offline_cost_report=False)

    def _walk_ran(**kwargs):
        raise AssertionError("resume_production_trial must NOT be reached on a keyless live resume")

    monkeypatch.setattr(trial_module, "resume_production_trial", _walk_ran)

    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        gate_id="G1",
        verb="approve",
        card_id=uuid4(),
        decision_card_digest=hashlib.sha256(b"card").hexdigest(),
        operator_id="operator_test",
    )
    with pytest.raises(RuntimeError) as exc:
        trial_module.resume_trial(trial_id=TRIAL_ID, verdict=verdict, runs_root=tmp_path)

    msg = str(exc.value)
    assert "OPENAI_API_KEY" in msg
    assert "resume" in msg
    assert str(TRIAL_ID) in msg


# ---------------------------------------------------------------------------
# AC-2: offline continuations (allow_offline_cost_report=True) stay keyless
# ---------------------------------------------------------------------------


def test_ac2_offline_recover_passes_without_env(tmp_path: Path, monkeypatch) -> None:
    _keyless_env(monkeypatch)
    run_dir = _seed_pause(
        tmp_path, pause_filename="error-pause.json", allow_offline_cost_report=True
    )
    envelope = _fake_envelope("paused-at-error", paused_error_tag="offline-stub")

    def _recover(**kwargs):
        return envelope

    monkeypatch.setattr(trial_module, "recover_production_trial", _recover)

    # No raise: the offline harness resume stays keyless.
    result = trial_module.recover_trial(trial_id=TRIAL_ID, runs_root=tmp_path)
    assert result["trial_id"] == str(TRIAL_ID)
    assert (run_dir / "trial-recover.json").exists()


# ---------------------------------------------------------------------------
# AC-3: predicate agreement — preflight-pass ⇒ _has_live_openai() True
# ---------------------------------------------------------------------------


def test_ac3_preflight_pass_implies_live_openai_true(monkeypatch) -> None:
    # Live env set → preflight does not raise AND the walk's own guard is live.
    _live_env(monkeypatch)
    trial_module._require_live_env_unless_offline(
        allow_offline_cost_report=False, context="resume", trial_id=TRIAL_ID
    )
    assert _has_live_openai() is True


def test_ac3_preflight_fails_when_openai_absent(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test-key")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    with pytest.raises(RuntimeError):
        trial_module._require_live_env_unless_offline(
            allow_offline_cost_report=False, context="resume", trial_id=TRIAL_ID
        )
    assert _has_live_openai() is False


def test_ac3_preflight_fails_when_langsmith_absent(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-live-key")
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    with pytest.raises(RuntimeError):
        trial_module._require_live_env_unless_offline(
            allow_offline_cost_report=False, context="resume", trial_id=TRIAL_ID
        )


def test_ac3_offline_flag_short_circuits_env_requirement(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    # allow_offline_cost_report True → no raise even with a bare env.
    trial_module._require_live_env_unless_offline(
        allow_offline_cost_report=True, context="resume", trial_id=TRIAL_ID
    )


# ---------------------------------------------------------------------------
# AC-4: frozen bc747b51 reproduction — keyless recover raises, not a degraded walk
# ---------------------------------------------------------------------------


def test_ac4_frozen_bc747b51_shape_raises_not_degraded_walk(tmp_path: Path, monkeypatch) -> None:
    """Reconstruct the frozen resume entry shape (runner.allow_offline_cost_report=False).

    Prefer a small constructed record on tmp_path so the test is hermetic; if the
    real frozen run dir is present its runner shape is asserted to match (skip-if-absent).
    """
    _keyless_env(monkeypatch)

    if FROZEN_RUN_DIR.is_dir() and (FROZEN_RUN_DIR / "error-pause.json").is_file():
        frozen = json.loads((FROZEN_RUN_DIR / "error-pause.json").read_text(encoding="utf-8"))
        assert (frozen.get("runner") or {}).get("allow_offline_cost_report") is False, (
            "frozen bc747b51 must be a live (non-offline) paused run"
        )

    _seed_pause(tmp_path, pause_filename="error-pause.json", allow_offline_cost_report=False)

    def _walk_ran(**kwargs):
        # This is the misattributed downstream failure the operator actually saw.
        raise AssertionError(
            "reached the walk (builder.gary.upstream-missing style strand) — "
            "the front-door preflight must have fired instead"
        )

    monkeypatch.setattr(trial_module, "recover_production_trial", _walk_ran)

    with pytest.raises(RuntimeError) as exc:
        trial_module.recover_trial(trial_id=TRIAL_ID, runs_root=tmp_path)

    msg = str(exc.value)
    assert "OPENAI_API_KEY" in msg
    assert "silently skip live specialist dispatch" in msg


# ---------------------------------------------------------------------------
# AC-5: batch-resume gets the same preflight
# ---------------------------------------------------------------------------


def test_ac5_keyless_batch_resume_raises_at_front_door(tmp_path: Path, monkeypatch) -> None:
    _keyless_env(monkeypatch)
    _seed_pause(
        tmp_path,
        pause_filename="provider-batch-pause.json",
        allow_offline_cost_report=False,
        extra={"batch_id": "batch-abc", "node_index": 5},
    )

    def _walk_ran(**kwargs):
        raise AssertionError(
            "resume_batch_production_trial must NOT be reached on a keyless live batch resume"
        )

    monkeypatch.setattr(trial_module, "resume_batch_production_trial", _walk_ran)

    with pytest.raises(RuntimeError) as exc:
        trial_module.resume_batch_trial(trial_id=TRIAL_ID, runs_root=tmp_path)

    msg = str(exc.value)
    assert "OPENAI_API_KEY" in msg
    assert str(TRIAL_ID) in msg


def test_ac5_offline_batch_resume_passes_without_env(tmp_path: Path, monkeypatch) -> None:
    _keyless_env(monkeypatch)
    _seed_pause(
        tmp_path,
        pause_filename="provider-batch-pause.json",
        allow_offline_cost_report=True,
        extra={"batch_id": "batch-abc", "node_index": 5},
    )
    envelope = _fake_envelope("waiting_for_provider_batch", waiting_batch_id="batch-abc")

    def _resume_batch(**kwargs):
        return envelope

    monkeypatch.setattr(trial_module, "resume_batch_production_trial", _resume_batch)

    result = trial_module.resume_batch_trial(trial_id=TRIAL_ID, runs_root=tmp_path)
    assert result["trial_id"] == str(TRIAL_ID)
