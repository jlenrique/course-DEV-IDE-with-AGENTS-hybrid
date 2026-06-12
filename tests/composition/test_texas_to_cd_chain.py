from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from tests.composition.composed_specialist_chain_harness import (
    ComposedSpecialistChainHarness,
    fake_make_chat_model,
)

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def _write_current_directive(
    *,
    corpus: Path,
    run_dir: Path,
    trial_id: UUID,
) -> tuple[Path, str]:
    payload = {
        "run_id": str(trial_id),
        "sources": [
            {
                "ref_id": "src-001",
                "provider": "local_file",
                "locator": (corpus / "intro.md").resolve().as_posix(),
                "role": "primary",
                "description": "Current Section 02A-compatible test directive",
                "expected_min_words": 1,
            },
            {
                "ref_id": "src-002",
                "provider": "local_file",
                "locator": (corpus / "chapter-1.md").resolve().as_posix(),
                "role": "supporting",
                "description": "Current Section 02A-compatible support source",
                "expected_min_words": 1,
            },
        ],
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    directive_path = run_dir / "directive.yaml"
    directive_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return directive_path, hashlib.sha256(directive_path.read_bytes()).hexdigest()


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


def test_texas_to_cd_chain_with_current_directive_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A current-shape directive path threads through
    the same Texas → CD envelope-append + dependency-threading invariants as
    the fixture-stub path. Pinned in the existing dispatch-path-driven envelope
    assertion site per Codex P2 review.
    """
    trial_id = UUID("87654321-4321-4321-8321-cba987654321")

    monkeypatch.setattr("app.specialists.texas.graph.make_chat_model", fake_make_chat_model)
    monkeypatch.setattr("app.specialists.cd.graph.make_chat_model", fake_make_chat_model)
    monkeypatch.setattr("app.specialists.cd.graph.assert_sanctum_lock", lambda: None)

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("body", encoding="utf-8")
    (corpus / "chapter-1.md").write_text("body", encoding="utf-8")
    run_dir = tmp_path / str(trial_id)
    directive_path, directive_digest = _write_current_directive(
        corpus=corpus,
        run_dir=run_dir,
        trial_id=trial_id,
    )
    # Point bundle_dir at the existing 6-artifact fixture bundle so Texas's
    # `_load_bundle_outputs` finds parseable artifacts (M-R5: monkeypatching
    # only `dispatch_retrieval` leaves Texas's bundle-read in place).
    fixture_bundle = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "specialists"
        / "texas"
        / "fixture_bundle"
    )
    bundle_dir = fixture_bundle

    captured: dict[str, object] = {}

    def _fake_dispatch(
        *,
        directive_path: object = None,
        bundle_dir: object = None,
    ) -> dict[str, object]:
        captured["directive_path"] = directive_path
        captured["bundle_dir"] = bundle_dir
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

    harness = ComposedSpecialistChainHarness(trial_id)
    # Inject runner_supplied_payload exactly as 7a.1's runner does.
    original_invoke = harness.adapter.invoke_specialist

    def _invoke_with_payload(*args: object, **kwargs: object) -> object:
        if kwargs.get("specialist_id") == "texas":
            kwargs["runner_supplied_payload"] = {
                "directive_path": directive_path.as_posix(),
                "bundle_dir": bundle_dir.as_posix(),
            }
        return original_invoke(*args, **kwargs)

    monkeypatch.setattr(harness.adapter, "invoke_specialist", _invoke_with_payload)
    envelope = harness.run_texas_to_cd()

    # Same invariants as fixture-stub path:
    assert [item.specialist_id for item in envelope.contributions] == ["texas", "cd"]
    texas = envelope.get_contribution("texas")
    cd = envelope.get_contribution("cd")
    assert texas is not None
    assert cd is not None
    assert texas.output["status"] == "complete"
    assert cd.output["cd_directive"]["schema_version"] == "1.0"
    # Plus composer-driven assertions:
    assert captured["directive_path"] == directive_path.as_posix()
    assert captured["bundle_dir"] == bundle_dir.as_posix()
    assert directive_digest  # materialization produced a real digest
