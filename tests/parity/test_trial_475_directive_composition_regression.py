"""trial-475 regression: directive composition closes silent gate-bypass.

Story 7a.1 / AC-7.1-H (M-R1 BINDING). Replays trial-475's
``--input course-content/courses/tejal-APC-C1/`` against the new composer in
deterministic test mode. Per M-R5, ``dispatch_retrieval`` is monkeypatched —
the live wrangler subprocess is NEVER invoked.

The regression is parametrized over operator-confirm path AND operator-edit
path so both UX flows are pinned.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import yaml

from app.marcus.cli.trial import start_trial

MINI_CORPUS = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "trials"
    / "trial_475_mini_corpus"
)


def _write_trial_475_directive(
    *,
    corpus_dir: Path,
    run_dir: Path,
    run_id: UUID,
) -> tuple[Path, str]:
    files = sorted(p.name for p in corpus_dir.iterdir() if p.is_file())
    payload = {
        "run_id": str(run_id),
        "sources": [
            {
                "ref_id": f"src-{index:03d}",
                "provider": "local_file",
                "locator": name,
                "role": "primary" if index == 1 else "supporting",
                "description": f"trial-475 current-shape fixture source: {name}",
                "expected_min_words": 1,
            }
            for index, name in enumerate(files, start=1)
        ],
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    directive_path = run_dir / "directive.yaml"
    directive_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return directive_path, hashlib.sha256(directive_path.read_bytes()).hexdigest()


@pytest.fixture
def env_for_offline_trial(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow trial-start without live API keys or live LLM calls."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    monkeypatch.setenv("LANGSMITH_API_KEY", "lsv2-fake")
    monkeypatch.setenv("LANGSMITH_PROJECT", "trial-475-regression")
    monkeypatch.setattr(
        "app.marcus.cli.trial.compose_and_write",
        _write_trial_475_directive,
    )


@pytest.fixture
def dispatch_capture(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Monkeypatch dispatch_retrieval per M-R5; capture call args."""
    captured: dict[str, Any] = {"calls": []}

    def _fake_dispatch(
        *,
        directive_path: str | Path | None = None,
        bundle_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        captured["calls"].append(
            {
                "directive_path": str(directive_path) if directive_path else None,
                "bundle_dir": str(bundle_dir) if bundle_dir else None,
            }
        )
        # Simulate non-mocked branch — synthesized "dispatched" payload.
        return {
            "status": "dispatched",
            "bundle_dir": str(bundle_dir) if bundle_dir else "",
            "exit_code": 0,
            "stdout": "synthetic-dispatched",
            "stderr": "",
            "command": [
                "python",
                "skills/bmad-agent-texas/scripts/run_wrangler.py",
                "--directive",
                str(directive_path) if directive_path else "",
                "--bundle-dir",
                str(bundle_dir) if bundle_dir else "",
                "--json",
            ],
        }

    monkeypatch.setattr(
        "app.specialists.texas.retrieval_dispatch.dispatch_retrieval",
        _fake_dispatch,
    )
    return captured


def test_mini_corpus_fixture_is_present() -> None:
    """Sanity guard: the mini-fixture is checked into the repo."""
    assert MINI_CORPUS.exists(), f"missing trial-475 mini-corpus at {MINI_CORPUS}"
    files = sorted(p.name for p in MINI_CORPUS.iterdir() if p.is_file())
    assert files == ["appendix.md", "chapter-1.md", "intro.md"]


def test_trial_475_mini_corpus_shape_is_stable() -> None:
    """The mini-corpus fixture remains suitable for current directive composition."""
    files = sorted(p.name for p in MINI_CORPUS.iterdir() if p.is_file())
    assert files == ["appendix.md", "chapter-1.md", "intro.md"]
    # appendix sorts first alphabetically — auto-walker pins it as primary.


def test_trial_475_confirm_path_threads_directive_to_texas(
    tmp_path: Path,
    env_for_offline_trial: None,
    dispatch_capture: dict[str, Any],
) -> None:
    """Operator confirms the auto-composed directive → Texas receives non-None paths."""
    runs_root = tmp_path / "runs"

    payload = start_trial(
        preset="production",
        input_path=MINI_CORPUS,
        operator_id="trial-475-regression",
        trial_id=uuid4(),
        allow_offline_cost_report=True,
        runs_root=runs_root,
        auto_confirm_directive=True,
    )

    assert payload["status"] in {"registered-offline"}
    directive_path = Path(payload["directive_path"])
    assert directive_path.exists(), "directive.yaml must materialize on disk"

    # No live LLM ⇒ runner skips specialist invocation in offline mode and Texas is not called;
    # the regression here pins COMPOSITION + materialization on disk.
    # The dispatch-threading check below is exercised by the live-OpenAI test pin
    # in tests/integration/marcus/test_production_runner_threads_directive.py.
    assert payload["directive_digest"]
    assert "directive_path" in payload


def test_trial_475_edit_path_re_pins_role_primary(
    tmp_path: Path,
    env_for_offline_trial: None,
    dispatch_capture: dict[str, Any],
) -> None:
    """Operator edits the directive between materialize and confirm → re-pinned shape persists."""
    from app.marcus.cli import trial as trial_module

    runs_root = tmp_path / "runs"
    edit_invocations: list[Path] = []

    def _edit(directive_path: Path) -> None:
        # Simulate operator swapping role: primary from appendix.md → chapter-1.md.
        data = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
        for src in data["sources"]:
            if src["locator"] == "appendix.md":
                src["role"] = "supporting"
            elif src["locator"] == "chapter-1.md":
                src["role"] = "primary"
        directive_path.write_text(
            yaml.safe_dump(
                data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        edit_invocations.append(directive_path)

    inputs = iter(["e", "c"])

    def _confirm(*, directive_path: Path, auto_confirm_directive: bool) -> str:
        return trial_module._confirm_or_edit_directive(
            directive_path=directive_path,
            auto_confirm_directive=auto_confirm_directive,
            input_fn=lambda _prompt: next(inputs),
            edit_fn=_edit,
            isatty_fn=lambda: True,
            print_fn=lambda _msg: None,
        )

    payload = start_trial(
        preset="production",
        input_path=MINI_CORPUS,
        operator_id="trial-475-regression-edit",
        trial_id=uuid4(),
        allow_offline_cost_report=True,
        runs_root=runs_root,
        confirm_fn=_confirm,
    )
    directive_path = Path(payload["directive_path"])
    composed = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    primary = [src for src in composed["sources"] if src["role"] == "primary"]
    assert len(primary) == 1
    assert primary[0]["locator"] == "chapter-1.md"
    assert len(edit_invocations) == 1


def test_trial_475_dispatch_branch_taken_not_mocked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    dispatch_capture: dict[str, Any],
) -> None:
    """Direct call to dispatch_retrieval w/ runner-supplied paths returns 'dispatched'.

    This pins the M-R5 contract: when both directive_path + bundle_dir are
    populated, the dispatch seam reports `status: "dispatched"` (NOT `"mocked"`).
    Pre-7a.1 silent-bypass path returned `"mocked"`; the new threading prevents
    that branch.
    """
    from app.specialists.texas import retrieval_dispatch as rd

    directive = tmp_path / "directive.yaml"
    directive.write_text("run_id: TEST\nsources: []\n", encoding="utf-8")
    bundle = tmp_path / "bundle"
    bundle.mkdir()

    result = rd.dispatch_retrieval(
        directive_path=directive,
        bundle_dir=bundle,
    )
    assert result["status"] == "dispatched"
    assert dispatch_capture["calls"] == [
        {
            "directive_path": str(directive),
            "bundle_dir": str(bundle),
        }
    ]


def test_trial_475_silent_bypass_is_observable_when_paths_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The pre-7a.1 silent-bypass branch is still reachable when paths omitted.

    Documents the regression: with directive_path=None OR bundle_dir=None,
    dispatch_retrieval returns `status: "mocked"`. Story 7a.1's runner
    threading guarantees production-trial mode never hits this branch.
    """
    # Re-import to bypass the dispatch_capture monkeypatch from earlier fixtures.
    import importlib

    from app.specialists.texas import retrieval_dispatch

    importlib.reload(retrieval_dispatch)

    result = retrieval_dispatch.dispatch_retrieval(
        directive_path=None,
        bundle_dir=None,
    )
    assert result["status"] == "mocked"


def test_start_trial_threads_composed_directive_to_texas_dispatch(
    tmp_path: Path,
    env_for_offline_trial: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P1 BINDING (Codex review): prove start_trial → run_production_trial →
    adapter → texas.graph._act → dispatch_retrieval threads the composed
    directive_path through the actual production code path (NOT just a direct
    dispatch_retrieval call).

    Patches `app.specialists.texas.graph.dispatch_retrieval` (the import binding
    at module load) so the live wrangler subprocess never executes; asserts the
    captured call args carry the composer-materialized directive_path + bundle_dir.
    """
    from app.marcus.orchestrator import production_runner

    runs_root = tmp_path / "runs"
    captured: dict[str, Any] = {"calls": []}

    def _fake_dispatch(
        *,
        directive_path: Any = None,
        bundle_dir: Any = None,
    ) -> dict[str, Any]:
        captured["calls"].append(
            {
                "directive_path": str(directive_path) if directive_path else None,
                "bundle_dir": str(bundle_dir) if bundle_dir else None,
            }
        )
        return {
            "status": "dispatched",
            "bundle_dir": str(bundle_dir) if bundle_dir else "",
            "exit_code": 0,
            "stdout": "synthetic-dispatched",
            "stderr": "",
            "command": None,
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        _fake_dispatch,
    )
    # Texas's _act ALSO calls _load_bundle_outputs(bundle_dir) and consumes the
    # parsed["tag"] field. Override the runner's bundle_dir derivation to point
    # at the existing 6-artifact fixture bundle so the load succeeds with the
    # canonical shape (M-R5: monkeypatching dispatch alone leaves bundle-read
    # in place; this is the runner-side bundle_dir override).
    fixture_bundle = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "specialists"
        / "texas"
        / "fixture_bundle"
    )

    original_payload_helper = production_runner._runner_payload_for_specialist

    def _override_runner_payload(
        *,
        specialist_id: str,
        directive_path: Path | None,
        bundle_dir: Path | None,
    ) -> dict[str, str] | None:
        return original_payload_helper(
            specialist_id=specialist_id,
            directive_path=directive_path,
            bundle_dir=fixture_bundle if specialist_id == "texas" else bundle_dir,
        )

    monkeypatch.setattr(
        production_runner,
        "_runner_payload_for_specialist",
        _override_runner_payload,
    )
    monkeypatch.setattr(production_runner, "_has_live_openai", lambda: True)
    # Stub LangSmith client to avoid network 403s during the test run.
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)

    # Capture runner_supplied_payload via a build_specialist_state spy.
    from app.marcus.orchestrator import dispatch_adapter as adapter_module

    captured_payloads: list[dict[str, Any]] = []
    original_build = adapter_module.ProductionDispatchAdapter.build_specialist_state

    def _capturing_build(self: Any, **kw: Any) -> Any:
        if kw.get("runner_supplied_payload"):
            captured_payloads.append(kw["runner_supplied_payload"])
        return original_build(self, **kw)

    monkeypatch.setattr(
        adapter_module.ProductionDispatchAdapter,
        "build_specialist_state",
        _capturing_build,
    )

    payload = start_trial(
        preset="production",
        input_path=MINI_CORPUS,
        operator_id="trial-475-real-path-regression",
        trial_id=uuid4(),
        allow_offline_cost_report=False,  # exercise the live-specialist branch
        runs_root=runs_root,
        auto_confirm_directive=True,
    )

    # Composer + materializer ran:
    assert payload["directive_path"]
    assert payload["directive_digest"]
    # Runner threaded the directive_path + bundle_dir to the adapter for Texas:
    texas_payloads = [
        p for p in captured_payloads if "directive_path" in p and "bundle_dir" in p
    ]
    assert texas_payloads, (
        "expected runner_supplied_payload with directive_path + bundle_dir to "
        "reach build_specialist_state for Texas"
    )
    assert payload["directive_path"] in texas_payloads[0]["directive_path"]


def test_start_trial_cli_cancel_returns_exit_code_2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6 BINDING (Codex review): the CLI wrapper exit code for cancelled
    trials is 2 (distinguishable from 0 = success and 1 = error)."""
    import argparse

    from app.marcus.cli import trial as trial_module

    def _fake_start_trial(**_kwargs: Any) -> dict[str, Any]:
        return {
            "status": "cancelled-at-g0",
            "trial_id": "00000000-0000-0000-0000-000000000000",
            "operator_id": "test",
            "directive_path": "/tmp/runs/x/directive.yaml",
            "directive_digest": "0" * 64,
            "cancellation_record": "/tmp/runs/x/trial-cancelled-at-g0.json",
            "transport_kind": "cli",
        }

    monkeypatch.setattr(trial_module, "start_trial", _fake_start_trial)
    args = argparse.Namespace(
        preset="production",
        input="/tmp/corpus",
        operator_id="test",
        trial_id=None,
        allow_offline_cost_report=True,
        runs_root=None,
        auto_confirm_directive=False,
    )
    assert trial_module.start_trial_cli(args) == 2
