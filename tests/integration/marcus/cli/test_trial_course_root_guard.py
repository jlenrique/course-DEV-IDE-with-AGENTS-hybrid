from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

import app.marcus.cli.trial as trial_module
from app.marcus.cli.trial import DirectiveConfirmationRequiredError, start_trial

TRIAL_ID = UUID("33333333-3333-4333-8333-333333333333")


def test_trial_start_course_root_refuses_before_env_and_run_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course_root = tmp_path / "course-root"
    (course_root / "modules" / "module-01").mkdir(parents=True)
    (course_root / "course.yaml").write_text(
        "runtime_contract:\n  runnable_input_scope: lesson_corpus_leaf\n",
        encoding="utf-8",
    )
    runs_root = tmp_path / "runs"

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.setattr(
        trial_module,
        "_load_env_if_available",
        lambda: pytest.fail("env loading must not run before broad-root refusal"),
    )
    monkeypatch.setattr(
        trial_module,
        "compose_and_write",
        lambda **_kwargs: pytest.fail("compose_and_write must not run for course root"),
    )
    monkeypatch.setattr(
        trial_module,
        "run_production_trial",
        lambda **_kwargs: pytest.fail("production runner must not run for course root"),
    )

    with pytest.raises(DirectiveConfirmationRequiredError, match="non-runnable-scope"):
        start_trial(
            preset="production",
            input_path=course_root,
            operator_id="operator_test",
            trial_id=TRIAL_ID,
            allow_offline_cost_report=False,
            runs_root=runs_root,
            auto_confirm_directive=True,
        )

    run_dir = runs_root / str(TRIAL_ID)
    assert not (run_dir / "directive.yaml").exists()
    assert not (run_dir / "run.json").exists()
    assert not (run_dir / "trial-start.json").exists()
