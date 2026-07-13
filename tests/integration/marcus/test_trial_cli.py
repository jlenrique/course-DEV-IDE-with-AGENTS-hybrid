from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.marcus.cli.__main__ import main
from app.marcus.cli.trial import start_trial
from app.marcus.course_source.input_bundle import build_lesson_planning_input_bundle
from app.models.state.component_selection import ComponentSelection

TRIAL_ID = "12345678-1234-4234-8234-123456789abc"
REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "s7p2-story-b-syllabus-metadata-20260708T110225"
)
HAI_ROOT = (
    REPO_ROOT / "course-content" / "courses" / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)
HAI_PROPOSAL = EVIDENCE / "hai-510" / "module-metadata.yaml"


@pytest.fixture(autouse=True)
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a.2 — file-corpus dormant-path migration (D-kill-switch pin).

    These CLI walks pass a README FILE as ``corpus_path`` and first-pause at G1 on the
    dormant path. The 3b default flip wakes G0-enrichment's corpus-DIRECTORY
    enumeration, which crashes pre-gate with ``DirectiveCompositionError`` on a file
    corpus. Pinning ``MARCUS_G0_ENRICHMENT_ACTIVE`` OFF explicitly preserves the
    enrichment-orthogonal downstream subject under the flip (explicit ``"0"`` survives
    the code-default flip). TEST-ONLY: no production/default change.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


def test_start_trial_registers_run_and_cost_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)

    result = start_trial(
        preset="production",
        input_path=Path("tests/fixtures/trial_corpus/README.md"),
        operator_id="operator_test",
        allow_offline_cost_report=True,
        runs_root=tmp_path,
    )

    run_dir = tmp_path / result["trial_id"]
    assert result["status"] == "registered-offline"
    assert result["langsmith_trace_status"] == "skipped-no-langsmith-env"
    assert result["production_clone_launch_evidence"] is False
    assert (run_dir / "run.json").exists()
    assert (run_dir / "cost-report.json").exists()
    assert (run_dir / "cost-report.md").exists()

    envelope = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert envelope["trial_id"] == result["trial_id"]
    assert envelope["preset"] == "production"
    assert Path(envelope["corpus_path"]).as_posix() == "tests/fixtures/trial_corpus/README.md"
    assert envelope["schema_version"] == "production-trial-envelope.v1"
    assert envelope["production_clone_launch_evidence"] is False
    assert envelope["cost_report_path"] == str(run_dir / "cost-report.json")


def test_start_trial_ratified_collateral_intent_threads_selection(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    captured: dict[str, object] = {}

    def _spy(**kwargs):
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _spy)
    intent_path = tmp_path / "ratified-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: ratified\n"
        "bundle_id: narrated-deck-with-workbook\n"
        "collateral:\n"
        "  declaration: present\n"
        "  workbook:\n"
        "    sections:\n"
        "      - section_id: sec-1\n"
        "        learning_objective_id: obj-1\n"
        "        title: Read in depth\n"
        "        depth_delta:\n"
        "          deferred_from_slide: slide-1\n"
        "          deferred_depth: supporting method\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="stop-after-capture"):
        start_trial(
            preset="production",
            input_path=Path("tests/fixtures/trial_corpus/README.md"),
            operator_id="operator_test",
            allow_offline_cost_report=True,
            runs_root=tmp_path,
            lesson_plan_collateral_intent_path=intent_path,
            course_source_root=Path("course-content/courses/tejal-apc-c1-m1-p2-trends"),
            encounter_mode="recorded",
        )

    selection = captured["component_selection"]
    assert selection is not None
    assert selection.as_map() == {"deck": True, "motion": True, "workbook": True}


def test_start_trial_ratified_collateral_intent_runs_local_runtime(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "ratified-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: ratified\n"
        "bundle_id: narrated-deck-with-workbook\n"
        "collateral:\n"
        "  declaration: present\n"
        "  workbook:\n"
        "    sections:\n"
        "      - section_id: sec-1\n"
        "        learning_objective_id: obj-1\n"
        "        title: Read in depth\n"
        "        depth_delta:\n"
        "          deferred_from_slide: slide-1\n"
        "          deferred_depth: supporting method\n",
        encoding="utf-8",
    )

    result = start_trial(
        preset="production",
        input_path=Path("tests/fixtures/trial_corpus/README.md"),
        operator_id="operator_test",
        allow_offline_cost_report=True,
        runs_root=tmp_path,
        lesson_plan_collateral_intent_path=intent_path,
        course_source_root=Path("course-content/courses/tejal-apc-c1-m1-p2-trends"),
        encounter_mode="recorded",
    )

    run_dir = tmp_path / result["trial_id"]
    start_receipt = json.loads((run_dir / "trial-start.json").read_text(encoding="utf-8"))
    assert start_receipt["lesson_plan_collateral_bundle_id"] == ("narrated-deck-with-workbook")
    assert start_receipt["lesson_plan_collateral_intent_path"] == intent_path.as_posix()
    summary = yaml.safe_load((run_dir / "run_summary.yaml").read_text(encoding="utf-8"))
    assert summary["component_selection"] == {
        "deck": True,
        "motion": True,
        "workbook": True,
    }
    assert (run_dir / "run.json").exists()


def test_start_trial_ratified_input_bundle_intent_runs_local_runtime(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "ratified-input-bundle-intent.yaml"
    input_bundle = build_lesson_planning_input_bundle(
        course_root=HAI_ROOT,
        proposal_path=HAI_PROPOSAL,
        module_id="module-01-foundations-of-ai-in-healthcare",
        operator_focus="Plan around missing lecture video and slide source.",
    )
    intent_path.write_text(
        yaml.safe_dump(
            {
                "ratification_status": "ratified",
                "source_ref": HAI_PROPOSAL.relative_to(REPO_ROOT).as_posix(),
                "input_bundle": input_bundle.model_dump(mode="json"),
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = start_trial(
        preset="production",
        input_path=Path("tests/fixtures/trial_corpus/README.md"),
        operator_id="operator_test",
        allow_offline_cost_report=True,
        runs_root=tmp_path,
        lesson_plan_collateral_intent_path=intent_path,
    )

    run_dir = tmp_path / result["trial_id"]
    start_receipt = json.loads((run_dir / "trial-start.json").read_text(encoding="utf-8"))
    assert start_receipt["lesson_plan_collateral_bundle_id"] == ("narrated-deck-with-motion")
    summary = yaml.safe_load((run_dir / "run_summary.yaml").read_text(encoding="utf-8"))
    assert summary["component_selection"] == {
        "deck": True,
        "motion": True,
        "workbook": False,
    }
    assert (run_dir / "run.json").exists()


def test_start_trial_unratified_collateral_intent_preserves_manual_selection(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    captured: dict[str, object] = {}

    def _spy(**kwargs):
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _spy)
    intent_path = tmp_path / "draft-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: draft\nbundle_id: narrated-deck-with-workbook\n",
        encoding="utf-8",
    )
    manual = ComponentSelection(deck=True, motion=False, workbook=False)

    with pytest.raises(RuntimeError, match="stop-after-capture"):
        start_trial(
            preset="production",
            input_path=Path("tests/fixtures/trial_corpus/README.md"),
            operator_id="operator_test",
            allow_offline_cost_report=True,
            runs_root=tmp_path,
            component_selection=manual,
            lesson_plan_collateral_intent_path=intent_path,
        )

    assert captured["component_selection"] == manual


def test_start_trial_ratified_intent_conflicts_with_manual_selection_before_run(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "ratified-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: ratified\n"
        "bundle_id: narrated-deck-with-workbook\n"
        "collateral:\n"
        "  declaration: present\n"
        "  workbook:\n"
        "    sections:\n"
        "      - section_id: sec-1\n"
        "        learning_objective_id: obj-1\n"
        "        title: Read in depth\n"
        "        depth_delta:\n"
        "          deferred_from_slide: slide-1\n"
        "          deferred_depth: supporting method\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="conflicts with the explicit"):
        start_trial(
            preset="production",
            input_path=Path("tests/fixtures/trial_corpus/README.md"),
            operator_id="operator_test",
            allow_offline_cost_report=True,
            runs_root=tmp_path,
            component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
            lesson_plan_collateral_intent_path=intent_path,
        )

    assert sorted(path.name for path in tmp_path.iterdir()) == ["ratified-collateral-intent.yaml"]


def test_trial_start_cli_unratified_intent_preserves_bundle_pick(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "draft-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: draft\nbundle_id: narrated-deck-with-workbook\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
            "--bundle",
            "narrated-deck",
            "--lesson-plan-collateral-intent",
            str(intent_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    summary = yaml.safe_load(
        (tmp_path / payload["trial_id"] / "run_summary.yaml").read_text(encoding="utf-8")
    )
    assert summary["component_selection"] == {
        "deck": True,
        "motion": False,
        "workbook": False,
    }


def test_trial_start_cli_ratified_intent_conflicts_with_bundle_before_run(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "ratified-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: ratified\n"
        "bundle_id: narrated-deck-with-workbook\n"
        "collateral:\n"
        "  declaration: present\n"
        "  workbook:\n"
        "    sections:\n"
        "      - section_id: sec-1\n"
        "        learning_objective_id: obj-1\n"
        "        title: Read in depth\n"
        "        depth_delta:\n"
        "          deferred_from_slide: slide-1\n"
        "          deferred_depth: supporting method\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
            "--bundle",
            "narrated-deck",
            "--lesson-plan-collateral-intent",
            str(intent_path),
            "--course-source-root",
            "course-content/courses/tejal-apc-c1-m1-p2-trends",
            "--encounter-mode",
            "recorded",
        ]
    )

    assert exit_code == 1
    assert "conflicts with --bundle" in capsys.readouterr().err
    assert not (tmp_path / TRIAL_ID / "run.json").exists()


def test_trial_start_cli_matching_ratified_intent_takes_precedence_over_readiness(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "ratified-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: ratified\n"
        "bundle_id: narrated-deck-with-workbook\n"
        "collateral:\n"
        "  declaration: present\n"
        "  workbook:\n"
        "    sections:\n"
        "      - section_id: sec-1\n"
        "        learning_objective_id: obj-1\n"
        "        title: Read in depth\n"
        "        depth_delta:\n"
        "          deferred_from_slide: slide-1\n"
        "          deferred_depth: supporting method\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
            "--bundle",
            "narrated-deck-with-workbook",
            "--lesson-plan-collateral-intent",
            str(intent_path),
            "--course-source-root",
            "course-content/courses/tejal-apc-c1-m1-p2-trends",
            "--encounter-mode",
            "recorded",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["lesson_plan_collateral_bundle_id"] == ("narrated-deck-with-workbook")


def test_trial_start_cli_rejects_invalid_ratified_collateral_intent(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_path = tmp_path / "invalid-collateral-intent.yaml"
    intent_path.write_text(
        "ratification_status: ratified\ncomponents: [deck, quiz]\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
            "--lesson-plan-collateral-intent",
            str(intent_path),
        ]
    )

    assert exit_code == 1
    assert "closed ratified intent validation failed" in capsys.readouterr().err
    assert not (tmp_path / TRIAL_ID / "run.json").exists()


def test_trial_start_cli_rejects_plan_json_missing_collateral(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """A well-formed lesson-plan JSON that is missing the `collateral` block
    fails loud at the CLI (exit 1, no run.json) — absent collateral is not a
    silent default."""
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    plan_json_path = tmp_path / "malformed.lesson-plan.json"
    plan_json_path.write_text(
        json.dumps({"lesson_summary": "x", "plan_units": []}),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
            "--lesson-plan-json",
            str(plan_json_path),
        ]
    )

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "ERROR: " in stderr
    assert "lesson_plan.collateral is required" in stderr
    assert not (tmp_path / TRIAL_ID / "run.json").exists()


def test_trial_start_cli_accepts_production_input(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["trial_id"] == TRIAL_ID
    assert payload["production_clone_launch_evidence"] is False
    # Story 7a.1 P5 (Codex review): trial-start payload paths emit POSIX form
    # via Path.as_posix() for Windows-stable cross-platform digests.
    assert payload["run_registry_path"] == (tmp_path / TRIAL_ID / "run.json").as_posix()


def test_start_trial_requires_langsmith_for_production_evidence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)

    with pytest.raises(RuntimeError, match="LANGSMITH_API_KEY and LANGSMITH_PROJECT"):
        start_trial(
            preset="production",
            input_path=Path("tests/fixtures/trial_corpus/README.md"),
            operator_id="operator_test",
            runs_root=tmp_path,
        )

    assert not any(tmp_path.iterdir())
