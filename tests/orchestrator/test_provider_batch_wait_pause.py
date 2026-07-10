"""B3: waiting_for_provider_batch — non-blocking submit + resume-batch."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.marcus.orchestrator.production_runner import (
    _pause_at_provider_batch,
    resume_batch_production_trial,
)
from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.state.run_state import RunState
from app.runtime.llm_batch.errors import WaitingForProviderBatchError
from app.runtime.llm_batch.receipts import BatchReceipt, write_receipt
from app.specialists.vision.batch_route import run_vision_batch_perception


def _png(tmp_path: Path, name: str = "s.png") -> Path:
    path = tmp_path / name
    path.write_bytes(b"\x89PNG\r\n\x1a\n")
    return path


def test_batch_submit_pauses_without_poll_loop(tmp_path: Path) -> None:
    run_id = str(uuid4())
    sleeps: list[float] = []

    class FakeAdapter:
        def submit_and_receipt(self, rows: Any, **kwargs: Any) -> BatchReceipt:
            receipt = BatchReceipt(
                run_id=kwargs["run_id"],
                batch_id="batch_pending",
                input_file_id="file_in",
                output_file_id=None,
                status="validating",
                submitted_at="2026-07-10T00:00:00Z",
                row_count=len(rows),
                model=kwargs.get("model"),
            )
            write_receipt(kwargs["runs_root"], receipt)
            return receipt

        def retrieve_batch(self, *_a: Any, **_k: Any) -> Any:
            raise AssertionError("raise_pending must not poll")

    with pytest.raises(WaitingForProviderBatchError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", _png(tmp_path))],
            run_id=run_id,
            runs_root=tmp_path,
            adapter=FakeAdapter(),  # type: ignore[arg-type]
            sleep_fn=lambda s: sleeps.append(s),
            wait_policy="raise_pending",
        )
    assert exc_info.value.tag == "vision.batch.waiting-for-provider"
    assert exc_info.value.batch_id == "batch_pending"
    assert sleeps == []
    assert (tmp_path / run_id / "llm_batch" / "receipt.json").is_file()


def test_existing_pending_receipt_raises_wait_without_resubmit(tmp_path: Path) -> None:
    run_id = str(uuid4())
    write_receipt(
        tmp_path,
        BatchReceipt(
            run_id=run_id,
            batch_id="batch_existing",
            input_file_id="file_in",
            output_file_id=None,
            status="in_progress",
            submitted_at="2026-07-10T00:00:00Z",
            row_count=1,
            model="gpt-5.5",
        ),
    )
    spies = {"submit": 0}

    class BoomAdapter:
        def submit_and_receipt(self, *_a: Any, **_k: Any) -> Any:
            spies["submit"] += 1
            raise AssertionError("must not re-submit")

    with pytest.raises(WaitingForProviderBatchError):
        run_vision_batch_perception(
            [("slide-01", _png(tmp_path))],
            run_id=run_id,
            runs_root=tmp_path,
            adapter=BoomAdapter(),  # type: ignore[arg-type]
            wait_policy="raise_pending",
        )
    assert spies["submit"] == 0


def test_pause_at_provider_batch_writes_distinct_status(tmp_path: Path) -> None:
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    receipt = BatchReceipt(
        run_id=str(trial_id),
        batch_id="batch_x",
        input_file_id="in",
        output_file_id=None,
        status="in_progress",
        submitted_at="2026-07-10T00:00:00Z",
        row_count=1,
        model="gpt-5.5",
    )
    write_receipt(tmp_path, receipt)
    waiting = WaitingForProviderBatchError(
        "waiting",
        batch_id="batch_x",
        receipt_path=tmp_path / str(trial_id) / "llm_batch" / "receipt.json",
        receipt=receipt,
    )
    pe = ProductionEnvelope(trial_id=trial_id)
    envelope = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path="x",
        operator_id="op",
        started_at=__import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
        status="in-flight",
        production_clone_launch_evidence=False,
        production_envelope=pe,
    )
    run_state = RunState(run_id=trial_id, graph_version="v42", status="running")
    paused = _pause_at_provider_batch(
        waiting=waiting,
        node_id="07G",
        node_index=3,
        specialist_id="vision",
        trial_id=trial_id,
        envelope=envelope,
        production_envelope=pe,
        run_state=run_state,
        child_runs=[],
        trace_metadata={},
        last_gate_crossed=None,
        graph_step_completed=True,
        specialist_calls=1,
        manifest_path=Path("state/config/pipeline-manifest.yaml"),
        runs_root=tmp_path,
        allow_offline_cost_report=True,
        max_specialist_calls=1,
        directive_path=None,
        bundle_dir=None,
    )
    assert paused.status == "waiting_for_provider_batch"
    assert paused.paused_gate is None
    assert paused.paused_error_tag is None
    assert paused.waiting_batch_id == "batch_x"
    pause_file = tmp_path / str(trial_id) / "provider-batch-pause.json"
    assert pause_file.is_file()
    body = json.loads(pause_file.read_text(encoding="utf-8"))
    assert body["batch_id"] == "batch_x"
    assert "resume-batch" in body["resume_command"]


def test_resume_batch_still_waiting_no_resubmit(tmp_path: Path) -> None:
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    write_receipt(
        tmp_path,
        BatchReceipt(
            run_id=str(trial_id),
            batch_id="batch_wait",
            input_file_id="in",
            output_file_id=None,
            status="in_progress",
            submitted_at="2026-07-10T00:00:00Z",
            row_count=1,
            model="gpt-5.5",
        ),
    )
    pe = ProductionEnvelope(trial_id=trial_id)
    envelope = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path="x",
        operator_id="op",
        started_at=__import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
        status="waiting_for_provider_batch",
        waiting_batch_id="batch_wait",
        production_clone_launch_evidence=False,
        production_envelope=pe,
    )
    (run_dir / "run.json").write_text(
        envelope.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    run_state = RunState(run_id=trial_id, graph_version="v42", status="running")
    (run_dir / "provider-batch-pause.json").write_text(
        json.dumps(
            {
                "trial_id": str(trial_id),
                "node_index": 0,
                "node_id": "07G",
                "specialist_id": "vision",
                "tag": "vision.batch.waiting-for-provider",
                "message": "waiting",
                "batch_id": "batch_wait",
                "receipt_path": (
                    tmp_path / str(trial_id) / "llm_batch" / "receipt.json"
                ).as_posix(),
                "last_gate_crossed": None,
                "run_state": run_state.model_dump(mode="json"),
                "runner": {
                    "corpus_path": "x",
                    "preset": "production",
                    "operator_id": "op",
                    "manifest_path": "state/config/pipeline-manifest.yaml",
                    "allow_offline_cost_report": True,
                    "max_specialist_calls": 1,
                    "directive_path": None,
                    "bundle_dir": None,
                },
                "resume_command": f"trial resume-batch --trial-id {trial_id}",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    spies = {"create_file": 0, "create_batch": 0, "submit": 0}

    class FakeAdapter:
        def retrieve_batch(self, batch_id: str) -> Any:
            assert batch_id == "batch_wait"
            return SimpleNamespace(
                id="batch_wait",
                status="in_progress",
                input_file_id="in",
                output_file_id=None,
                error_file_id=None,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                request_counts={},
                model="gpt-5.5",
                completed_at=None,
            )

        def submit_and_receipt(self, *_a: Any, **_k: Any) -> Any:
            spies["submit"] += 1
            raise AssertionError("no submit on resume-batch")

        def create_file(self, *_a: Any, **_k: Any) -> Any:
            spies["create_file"] += 1
            raise AssertionError("no create_file")

        def create_batch(self, *_a: Any, **_k: Any) -> Any:
            spies["create_batch"] += 1
            raise AssertionError("no create_batch")

    out = resume_batch_production_trial(
        trial_id=trial_id,
        runs_root=tmp_path,
        adapter=FakeAdapter(),  # type: ignore[arg-type]
    )
    assert out.status == "waiting_for_provider_batch"
    assert spies == {"create_file": 0, "create_batch": 0, "submit": 0}
    assert (run_dir / "trial-resume-batch.json").is_file()


def test_resume_batch_terminal_failed_fail_loud(tmp_path: Path) -> None:
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    write_receipt(
        tmp_path,
        BatchReceipt(
            run_id=str(trial_id),
            batch_id="batch_fail",
            input_file_id="in",
            output_file_id=None,
            status="failed",
            submitted_at="2026-07-10T00:00:00Z",
            row_count=1,
            model="gpt-5.5",
        ),
    )
    pe = ProductionEnvelope(trial_id=trial_id)
    envelope = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path="x",
        operator_id="op",
        started_at=__import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
        status="waiting_for_provider_batch",
        waiting_batch_id="batch_fail",
        production_clone_launch_evidence=False,
        production_envelope=pe,
    )
    (run_dir / "run.json").write_text(
        envelope.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    run_state = RunState(run_id=trial_id, graph_version="v42", status="running")
    (run_dir / "provider-batch-pause.json").write_text(
        json.dumps(
            {
                "trial_id": str(trial_id),
                "node_index": 0,
                "node_id": "07G",
                "specialist_id": "vision",
                "tag": "vision.batch.waiting-for-provider",
                "message": "waiting",
                "batch_id": "batch_fail",
                "receipt_path": (
                    tmp_path / str(trial_id) / "llm_batch" / "receipt.json"
                ).as_posix(),
                "last_gate_crossed": None,
                "run_state": run_state.model_dump(mode="json"),
                "runner": {
                    "corpus_path": "x",
                    "preset": "production",
                    "operator_id": "op",
                    "manifest_path": "state/config/pipeline-manifest.yaml",
                    "allow_offline_cost_report": True,
                    "max_specialist_calls": 1,
                },
            }
        ),
        encoding="utf-8",
    )

    class FakeAdapter:
        def retrieve_batch(self, batch_id: str) -> Any:
            return SimpleNamespace(
                id=batch_id,
                status="failed",
                input_file_id="in",
                output_file_id=None,
                error_file_id="err",
                endpoint="/v1/chat/completions",
                completion_window="24h",
                request_counts={},
                model="gpt-5.5",
                completed_at=None,
            )

    with pytest.raises(RuntimeError, match="vision.batch.not-completed|ended status"):
        resume_batch_production_trial(
            trial_id=trial_id,
            runs_root=tmp_path,
            adapter=FakeAdapter(),  # type: ignore[arg-type]
        )


def test_two_walk_chokepoint_helper_exists() -> None:
    import inspect

    from app.marcus.orchestrator import production_runner as pr

    src = inspect.getsource(pr)
    assert src.count("_dispatch_specialist_catching_batch_wait(") >= 2
    assert "WaitingForProviderBatchError" in src


def test_trial_resume_batch_cli_parser() -> None:
    import argparse

    from app.marcus.cli.trial import build_trial_parser

    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    args = parser.parse_args(
        ["resume-batch", "--trial-id", "12345678-1234-4234-8234-123456789abc"]
    )
    assert args.trial_command == "resume-batch"


def test_resume_batch_completed_continues_once_t5(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Completed resume continues walk once; second call skips re-submit (T5)."""

    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    write_receipt(
        tmp_path,
        BatchReceipt(
            run_id=str(trial_id),
            batch_id="batch_done",
            input_file_id="in",
            output_file_id="out",
            status="completed",
            submitted_at="2026-07-10T00:00:00Z",
            row_count=1,
            model="gpt-5.5",
        ),
    )
    pe = ProductionEnvelope(trial_id=trial_id)
    envelope = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path="x",
        operator_id="op",
        started_at=__import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
        status="waiting_for_provider_batch",
        waiting_batch_id="batch_done",
        production_clone_launch_evidence=False,
        production_envelope=pe,
    )
    (run_dir / "run.json").write_text(
        envelope.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    run_state = RunState(run_id=trial_id, graph_version="v42", status="running")
    (run_dir / "provider-batch-pause.json").write_text(
        json.dumps(
            {
                "trial_id": str(trial_id),
                "node_index": 0,
                "node_id": "07G",
                "specialist_id": "vision",
                "tag": "vision.batch.waiting-for-provider",
                "message": "waiting",
                "batch_id": "batch_done",
                "receipt_path": (
                    tmp_path / str(trial_id) / "llm_batch" / "receipt.json"
                ).as_posix(),
                "last_gate_crossed": None,
                "run_state": run_state.model_dump(mode="json"),
                "runner": {
                    "corpus_path": "x",
                    "preset": "production",
                    "operator_id": "op",
                    "manifest_path": "state/config/pipeline-manifest.yaml",
                    "allow_offline_cost_report": True,
                    "max_specialist_calls": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    continue_calls = {"n": 0}
    spies = {"submit": 0}

    class FakeAdapter:
        def retrieve_batch(self, batch_id: str) -> Any:
            return SimpleNamespace(
                id=batch_id,
                status="completed",
                input_file_id="in",
                output_file_id="out",
                error_file_id=None,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                request_counts={},
                model="gpt-5.5",
                completed_at="2026-07-10T00:01:00Z",
            )

        def submit_and_receipt(self, *_a: Any, **_k: Any) -> Any:
            spies["submit"] += 1
            raise AssertionError("no submit")

    def fake_continue(**kwargs: Any) -> ProductionTrialEnvelope:
        continue_calls["n"] += 1
        return kwargs["envelope"].model_copy(
            update={"status": "completed", "completed_at": kwargs["envelope"].started_at}
        )

    monkeypatch.setattr(
        "app.marcus.orchestrator.production_runner._continue_production_walk",
        fake_continue,
    )
    out1 = resume_batch_production_trial(
        trial_id=trial_id,
        runs_root=tmp_path,
        adapter=FakeAdapter(),  # type: ignore[arg-type]
    )
    assert continue_calls["n"] == 1
    assert out1.status == "completed"
    assert spies["submit"] == 0

    # After success, status is no longer waiting — second resume-batch must fail loud
    # (not re-submit). Operator does not double-continue the same wait.
    with pytest.raises(RuntimeError, match="not waiting for a provider batch"):
        resume_batch_production_trial(
            trial_id=trial_id,
            runs_root=tmp_path,
            adapter=FakeAdapter(),  # type: ignore[arg-type]
        )
    assert continue_calls["n"] == 1
    assert spies["submit"] == 0
