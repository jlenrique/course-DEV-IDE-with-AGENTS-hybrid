"""Canonical-arc S2 — styleguide picker canonical at trial-start (WARN-preserving).

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s2-picker-canonical-trial-start.md`
(D1 ceremony wiring @ the F-501 insertion point, D2 scripted `--selection-code`,
D3 Beat-1 narration + publish-flake degrade, F-502..F-506 monitor amendments).

RED-first plan items 1-5 live here, plus the AC-8 zero-publish witness, the
F-504 run_tag pin, the F-505 riders, and the F-506(a)/(b) witnesses.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest
import yaml

import app.marcus.cli.trial as trial_module
from app.marcus.cli.marcus_spoc import run_picker_preflight
from app.marcus.cli.trial import (
    DirectiveConfirmationRequiredError,
    build_trial_parser,
    recover_trial,
    resume_trial,
    start_trial,
)
from app.marcus.orchestrator.picker_html_emitter import (
    _RUN_TAG_RE,
    build_selection_code,
)
from app.marcus.orchestrator.styleguide_picker import (
    PickerError,
    append_pick_event,
)

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
# Real-SSOT pickable guide for paths that validate against the production SSOT
# (the scripted --selection-code path decodes without an ssot_path override).
REAL_GUIDE = "hil-2026-apc-crossroads-classic"


# ------------------------------------------------------------------ shared fixtures
def _ssot(tmp_path: Path) -> Path:
    ssot = tmp_path / "gamma-style-guides.yaml"
    ssot.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "style_guides": {
                    "alpha-style": {
                        "lifecycle": "permanent",
                        "presentation": {
                            "display_name": "Alpha Look",
                            "distinguishing": "clean line art",
                        },
                    },
                    "gamma-candidate": {
                        "lifecycle": "candidate",
                        "presentation": {
                            "display_name": "Gamma Look",
                            "distinguishing": "bold collage",
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return ssot


@pytest.fixture
def stub_corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("body", encoding="utf-8")
    return corpus


def _stub_compose(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the §02A composer at the trial seam (it is LLM-driven; this file
    pins the S2 ceremony contract, not composition)."""

    def _compose(
        *,
        corpus_dir: Path,
        run_dir: Path,
        run_id: Any,
        llm: Any = None,
        gamma_settings: Any = None,
    ) -> tuple[Path, str]:
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "directive.yaml"
        payload: dict[str, Any] = {
            "run_id": str(run_id),
            "corpus_dir": corpus_dir.as_posix(),
            "sources": [],
        }
        if gamma_settings is not None:
            payload["gamma_settings"] = gamma_settings
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    monkeypatch.setattr(trial_module, "compose_and_write", _compose)


def _start_args(stub_corpus: Path, runs_root: Path, **overrides: Any) -> dict:
    base = {
        "preset": "production",
        "input_path": stub_corpus,
        "operator_id": "operator_test",
        "trial_id": TRIAL_ID,
        "allow_offline_cost_report": True,
        "runs_root": runs_root,
    }
    base.update(overrides)
    return base


def _fake_publish(**kwargs: Any) -> dict[str, Any]:
    return {
        "publish_url": "https://x.github.io/p/index.html",
        "run_tag": kwargs["run_tag"],
        "style_count": 2,
    }


def _explode_input(_prompt: str) -> str:
    raise AssertionError("input() must never be called on this path")


def _fake_walk_envelope() -> SimpleNamespace:
    return SimpleNamespace(
        status="paused-at-gate",
        paused_gate="G1",
        paused_error_tag=None,
        cost_report_path=None,
        production_clone_launch_evidence=False,
    )


# ---------------------------------------------------------- RED-1: ceremony canonical
def test_interactive_start_requires_confirmed_pick(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D1: the interactive start runs the ceremony post-compose / pre-confirm-gate
    and the confirmed pick lands in the composed directive (F-404)."""
    _stub_compose(monkeypatch)
    runs_root = tmp_path / "runs"
    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    seen_kwargs: dict[str, Any] = {}
    code = build_selection_code(TRIAL_ID.hex, {"A": "alpha-style"})
    replies = iter([code, "confirm"])

    def _preflight(**kwargs: Any) -> dict[str, Any] | None:
        seen_kwargs.update(kwargs)
        return run_picker_preflight(
            input_fn=lambda _p: next(replies),
            print_fn=lambda _m: None,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            **kwargs,
        )

    result = start_trial(
        **_start_args(
            stub_corpus,
            runs_root,
            auto_confirm_directive=False,
            confirm_fn=lambda **_k: "saved-only",
            picker_preflight_fn=_preflight,
            picker_events_path=events,
        )
    )

    assert result["status"] == "saved-only"
    directive = runs_root / str(TRIAL_ID) / "directive.yaml"
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    settings = {row["variant_id"]: row["styleguide"] for row in loaded["gamma_settings"]}
    assert settings == {"A": "alpha-style"}
    prov = loaded["styleguide_picker_provenance"]
    assert prov["selection_code"] == code
    # F-504: the run_tag handed to the ceremony is trial_id.hex (hyphen-free).
    assert seen_kwargs["run_tag"] == TRIAL_ID.hex
    assert _RUN_TAG_RE.match(seen_kwargs["run_tag"])
    # F-502: the course identity threads from start_trial's input_path,
    # canonicalized per P4 (resolved + normcase + posix).
    assert seen_kwargs["course"] == _expected_course_key(stub_corpus)
    # out_dir = the run_dir (the publish receipt lands in the bundle).
    assert Path(seen_kwargs["out_dir"]) == runs_root / str(TRIAL_ID)
    # The re-digested directive attests the PICKED bytes, not the composed ones.
    assert result["directive_digest"] == hashlib.sha256(directive.read_bytes()).hexdigest()


# ------------------------------------------- RED-2: fail-closed abort, no run record
def test_no_pick_after_max_attempts_aborts_before_run_record(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-1: no confirmed pick => PickerError; NO run record, zero dispatch."""
    _stub_compose(monkeypatch)
    runs_root = tmp_path / "runs"
    ssot = _ssot(tmp_path)

    def _no_walk(**_kwargs: Any) -> Any:
        raise AssertionError("run_production_trial must not run after a PickerError")

    monkeypatch.setattr(trial_module, "run_production_trial", _no_walk)

    def _preflight(**kwargs: Any) -> dict[str, Any] | None:
        return run_picker_preflight(
            input_fn=lambda _p: "not-a-selection-code",
            print_fn=lambda _m: None,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            max_attempts=1,
            **kwargs,
        )

    with pytest.raises(PickerError, match="(?i)no confirmed"):
        start_trial(
            **_start_args(
                stub_corpus,
                runs_root,
                auto_confirm_directive=False,
                picker_preflight_fn=_preflight,
                picker_events_path=tmp_path / "picks.jsonl",
            )
        )

    run_dir = runs_root / str(TRIAL_ID)
    assert not (run_dir / "run.json").exists(), "aborted start must leave no run record"
    assert not (run_dir / "trial-start.json").exists()
    directive_text = (run_dir / "directive.yaml").read_text(encoding="utf-8")
    assert "styleguide_picker_provenance" not in directive_text


# --------------------------------------------- RED-3: resume/recover never prompt
def test_resume_and_recover_never_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D1: resume/recover read the persisted directive; ZERO input calls, zero
    ceremony invocations (the deep walk-level witness rides the AC-4 pin)."""
    monkeypatch.setattr("builtins.input", _explode_input)
    preflight_calls: list[Any] = []
    monkeypatch.setattr(
        trial_module,
        "run_picker_preflight",
        lambda **kwargs: preflight_calls.append(kwargs),
    )
    monkeypatch.setattr(trial_module, "_load_env_if_available", lambda: None)
    monkeypatch.setattr(
        trial_module, "resume_production_trial", lambda **_k: _fake_walk_envelope()
    )
    monkeypatch.setattr(
        trial_module, "recover_production_trial", lambda **_k: _fake_walk_envelope()
    )
    (tmp_path / str(TRIAL_ID)).mkdir(parents=True)

    from app.models.state.operator_verdict import OperatorVerdict

    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=uuid4(),
        operator_id="operator_test",
        decision_card_digest="0" * 64,
    )
    verdict_file = tmp_path / "verdict.json"
    verdict_file.write_text(verdict.model_dump_json(), encoding="utf-8")

    resumed = resume_trial(
        trial_id=TRIAL_ID, verdict_file=verdict_file, runs_root=tmp_path
    )
    recovered = recover_trial(trial_id=TRIAL_ID, runs_root=tmp_path)

    assert resumed["status"] == "paused-at-gate"
    assert recovered["status"] == "paused-at-gate"
    assert preflight_calls == [], "resume/recover must NEVER invoke the ceremony"


# ------------------------------------------- RED-4: scripted --selection-code path
def test_selection_code_arg_commits_noninteractively(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D2/F-505: a scripted start commits the pick through the SAME
    decode->validate->commit path — no prompt, no publish, no ceremony."""
    _stub_compose(monkeypatch)
    monkeypatch.setattr("builtins.input", _explode_input)
    monkeypatch.setattr(
        trial_module,
        "run_picker_preflight",
        lambda **_k: pytest.fail("scripted start must not run the ceremony"),
    )
    monkeypatch.setattr(
        trial_module, "run_production_trial", lambda **_k: _fake_walk_envelope()
    )
    runs_root = tmp_path / "runs"
    events = tmp_path / "picks.jsonl"
    code = build_selection_code(TRIAL_ID.hex, {"A": REAL_GUIDE})

    result = start_trial(
        **_start_args(
            stub_corpus,
            runs_root,
            auto_confirm_directive=True,
            selection_code=code,
            picker_events_path=events,
        )
    )

    directive = runs_root / str(TRIAL_ID) / "directive.yaml"
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    settings = {row["variant_id"]: row["styleguide"] for row in loaded["gamma_settings"]}
    assert settings == {"A": REAL_GUIDE}
    assert loaded["styleguide_picker_provenance"]["selection_code"] == code
    # P14: the scripted no-page arm carries a degraded:* family sentinel.
    assert loaded["styleguide_picker_provenance"]["publish_url"].startswith("degraded:")
    # F-502: the sidecar event carries the course/corpus identity field,
    # canonicalized per P4 (resolved + normcase + posix).
    lines = [
        json.loads(ln)
        for ln in events.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert len(lines) == 1
    assert lines[0]["course"] == _expected_course_key(stub_corpus)
    assert lines[0]["guide_name"] == REAL_GUIDE
    # Re-digest pin: the payload attests the picked directive bytes.
    assert result["directive_digest"] == hashlib.sha256(directive.read_bytes()).hexdigest()


def test_selection_code_stale_code_fails_start_loudly(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_compose(monkeypatch)
    monkeypatch.setattr(
        trial_module,
        "run_production_trial",
        lambda **_k: pytest.fail("a stale selection code must abort before the walk"),
    )
    runs_root = tmp_path / "runs"
    stale = build_selection_code(uuid4().hex, {"A": REAL_GUIDE})

    with pytest.raises(PickerError, match="(?i)stale|foreign"):
        start_trial(
            **_start_args(
                stub_corpus,
                runs_root,
                auto_confirm_directive=True,
                selection_code=stale,
                picker_events_path=tmp_path / "picks.jsonl",
            )
        )
    assert not (runs_root / str(TRIAL_ID) / "run.json").exists()


def test_selection_code_requires_trial_id(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F-505 rider: --selection-code needs a pre-mintable run_tag => --trial-id."""
    compose_calls: list[Any] = []
    monkeypatch.setattr(
        trial_module,
        "compose_and_write",
        lambda **kwargs: compose_calls.append(kwargs),
    )
    with pytest.raises(PickerError, match="(?i)trial.id|trial-id"):
        start_trial(
            **_start_args(
                stub_corpus,
                tmp_path / "runs",
                trial_id=None,
                auto_confirm_directive=True,
                selection_code=f"SGP-{TRIAL_ID.hex}-A:{REAL_GUIDE}",
            )
        )
    assert compose_calls == [], "fail loud BEFORE spending the composition LLM call"


def test_selection_code_respects_gamma_settings_j3(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F-505 rider: --selection-code x --gamma-settings-file follows the
    write_pick_to_directive J-3 semantics — the pick wins the `styleguide` key
    per-variant; the entry's OTHER keys survive."""
    _stub_compose(monkeypatch)
    monkeypatch.setattr(
        trial_module, "run_production_trial", lambda **_k: _fake_walk_envelope()
    )
    runs_root = tmp_path / "runs"
    settings_file = tmp_path / "gamma-settings.yaml"
    settings_file.write_text(
        yaml.safe_dump(
            [
                {
                    "variant_id": "A",
                    "styleguide": "hil-2026-apc-crossroads-blueprint",
                    "tone": "warm",
                }
            ]
        ),
        encoding="utf-8",
    )
    code = build_selection_code(TRIAL_ID.hex, {"A": REAL_GUIDE})

    start_trial(
        **_start_args(
            stub_corpus,
            runs_root,
            auto_confirm_directive=True,
            selection_code=code,
            gamma_settings_file=settings_file,
            picker_events_path=tmp_path / "picks.jsonl",
        )
    )

    directive = runs_root / str(TRIAL_ID) / "directive.yaml"
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    (entry,) = loaded["gamma_settings"]
    assert entry["variant_id"] == "A"
    assert entry["styleguide"] == REAL_GUIDE, "the pick wins the styleguide key"
    assert entry["tone"] == "warm", "other per-variant keys survive (J-3)"


# ------------------------------------------------ AC-8: F-503 zero-publish witness
def test_nontty_no_auto_confirm_raises_with_zero_publish(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-8 named witness: non-tty + no --auto-confirm-directive still raises
    DirectiveConfirmationRequiredError with ZERO publish_fn invocations."""
    _stub_compose(monkeypatch)
    monkeypatch.setattr("sys.stdin", io.StringIO(""))  # honest non-tty
    ceremony_calls: list[Any] = []
    monkeypatch.setattr(
        trial_module,
        "run_picker_preflight",
        lambda **kwargs: ceremony_calls.append(kwargs),
    )
    with pytest.raises(DirectiveConfirmationRequiredError):
        start_trial(
            **_start_args(
                stub_corpus,
                tmp_path / "runs",
                auto_confirm_directive=False,
            )
        )
    # Zero ceremony invocations => transitively zero publish_fn invocations
    # (the publish only happens inside run_picker_preflight).
    assert ceremony_calls == []


# ------------------------------------- RED-5 + AC-5: publish-flake degrade honesty
def test_publish_failure_degrades_to_inline_list_pick(tmp_path: Path) -> None:
    """AC-5 + F-506(a): publish flake => three numbered options; the inline
    text list equals the SSOT roster; the pick commits the SAME shape."""
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"
    events = tmp_path / "picks.jsonl"
    printed: list[str] = []

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("syncing_files flake: pages build never went live")

    # choice 2 (inline list) -> style A = 1 (alpha-style), B blank -> confirm.
    replies = iter(["2", "1", "", "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=directive,
        out_dir=tmp_path / "out",
        picked_by="client:tejal",
        input_fn=lambda _p: next(replies),
        print_fn=printed.append,
        publish_fn=_boom_publish,
        ssot_path=ssot,
        events_path=events,
    )
    assert record is not None
    assert record["picks"] == {"A": "alpha-style"}

    narration = "\n".join(printed)
    # P15: the numbered-options witness is scoped to the DEGRADE MENU text
    # (not the whole narration, where Beat-1's own 1/2/3 would mask it). With
    # no usable prior pick, option 3 is not offered (P8) — two ways forward,
    # still with a recommendation.
    menu = next(m for m in printed if "ways forward" in m)
    assert "1." in menu and "2." in menu
    assert "3." not in menu
    assert "recommend" in menu.lower()
    # F-506(a): the inline list's guides EQUAL the SSOT roster.
    assert "alpha-style" in narration and "gamma-candidate" in narration
    assert "Alpha Look" in narration and "Gamma Look" in narration
    # Honest about the missing thumbnails in text mode.
    assert "thumbnail" in narration.lower()

    # SAME directive shape as a pasted-code commit (control run).
    control_directive = tmp_path / "control-directive.yaml"
    control_replies = iter([build_selection_code("abc12345", {"A": "alpha-style"}), "confirm"])
    run_picker_preflight(
        run_tag="abc12345",
        directive_path=control_directive,
        out_dir=tmp_path / "out2",
        picked_by="client:tejal",
        input_fn=lambda _p: next(control_replies),
        print_fn=lambda _m: None,
        publish_fn=_fake_publish,
        ssot_path=ssot,
        events_path=tmp_path / "control-picks.jsonl",
    )
    degraded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    control = yaml.safe_load(control_directive.read_text(encoding="utf-8"))
    assert degraded["gamma_settings"] == control["gamma_settings"]
    assert set(degraded["styleguide_picker_provenance"]) == set(
        control["styleguide_picker_provenance"]
    )
    assert (
        degraded["styleguide_picker_provenance"]["selection_code"]
        == control["styleguide_picker_provenance"]["selection_code"]
    )


def test_publish_degrade_reuse_last_pick_arm(tmp_path: Path) -> None:
    """AC-5 rider (F-506(a)): the reuse-last-pick arm commits the prior pick,
    with provenance — enabled by F-502's course field."""
    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    append_pick_event(
        {"A": "alpha-style"},
        directive_path=tmp_path / "old-run-directive.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course="course-content/courses/c1m1",
    )
    directive = tmp_path / "directive.yaml"
    printed: list[str] = []

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    replies = iter(["3", "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=directive,
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=printed.append,
        publish_fn=_boom_publish,
        ssot_path=ssot,
        events_path=events,
        course="course-content/courses/c1m1",
    )
    assert record is not None
    assert record["picks"] == {"A": "alpha-style"}
    narration = "\n".join(printed)
    assert "2026-07-01" in narration, "reuse arm must show last-pick provenance"
    # AC-5: WITH a usable prior pick the degrade menu presents all THREE
    # numbered options (P8 gates option 3 on availability; here it IS available).
    menu = next(m for m in printed if "ways forward" in m)
    assert "1." in menu and "2." in menu and "3." in menu
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    assert loaded["styleguide_picker_provenance"]["selection_code"] == (
        build_selection_code("abc12345", {"A": "alpha-style"})
    )


def test_reuse_arm_unavailable_without_prior_course_pick(tmp_path: Path) -> None:
    """Honest degrade: no prior pick for this course => option 3 is unavailable
    and choosing it re-prompts instead of silently binding anything."""
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    replies = iter(["3", "2", "1", "", "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=directive,
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=lambda _m: None,
        publish_fn=_boom_publish,
        ssot_path=ssot,
        events_path=tmp_path / "picks.jsonl",
        course="course-content/courses/never-seen",
    )
    assert record is not None
    assert record["picks"] == {"A": "alpha-style"}


# ------------------------------------------ D3: Beat-1 narration + recommendation
def test_kickoff_framing_names_three_signoffs_and_known_end() -> None:
    from app.marcus.cli.marcus_spoc import narrate_kickoff_beat1

    text = narrate_kickoff_beat1(course="course-content/courses/c1m1")
    lowered = text.lower()
    # X1: look -> material -> contract, plus the known end — never a surprise gate.
    assert "look" in lowered
    assert "material" in lowered
    assert "contract" in lowered
    assert "finished" in lowered
    assert "1." in text and "2." in text and "3." in text


def test_versions_default_first_run_ab_rerun_single() -> None:
    from app.marcus.cli.marcus_spoc import narrate_kickoff_beat1

    first = narrate_kickoff_beat1(course="c", recommendation=None).lower()
    rerun = narrate_kickoff_beat1(
        course="c",
        recommendation={"picks": {"A": "alpha-style"}, "picked_at": "2026-07-01"},
    ).lower()
    assert "two versions" in first and "a/b" in first
    assert "single version" in rerun
    assert "override" in first and "override" in rerun


def test_accept_recommended_commit_shape_identical(tmp_path: Path) -> None:
    """F-506(b): accepting the recommendation without a pasted code mints the
    code via build_selection_code and commits SHAPE-IDENTICALLY to a paste."""
    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    course = "course-content/courses/c1m1"
    append_pick_event(
        {"A": "gamma-candidate"},
        directive_path=tmp_path / "old-run-directive.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course=course,
    )
    printed: list[str] = []
    directive = tmp_path / "directive.yaml"
    replies = iter(["recommended", "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=directive,
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=printed.append,
        publish_fn=_fake_publish,
        ssot_path=ssot,
        events_path=events,
        course=course,
    )
    assert record is not None
    assert record["picks"] == {"A": "gamma-candidate"}
    narration = "\n".join(printed)
    assert "2026-07-01" in narration, "recommendation carries last-used provenance"

    # Control: the SAME code pasted by hand into a fresh directive.
    control_directive = tmp_path / "control-directive.yaml"
    code = build_selection_code("abc12345", {"A": "gamma-candidate"})
    control_replies = iter([code, "confirm"])
    run_picker_preflight(
        run_tag="abc12345",
        directive_path=control_directive,
        out_dir=tmp_path / "out2",
        picked_by="operator_test",
        input_fn=lambda _p: next(control_replies),
        print_fn=lambda _m: None,
        publish_fn=_fake_publish,
        ssot_path=ssot,
        events_path=tmp_path / "control-picks.jsonl",
    )
    accepted = yaml.safe_load(directive.read_text(encoding="utf-8"))
    control = yaml.safe_load(control_directive.read_text(encoding="utf-8"))
    assert accepted["gamma_settings"] == control["gamma_settings"]
    assert accepted["styleguide_picker_provenance"]["selection_code"] == code
    # P15: shape-identical means EQUAL key sets, not a superset.
    assert set(accepted["styleguide_picker_provenance"]) == set(
        control["styleguide_picker_provenance"]
    )


def test_recommendation_still_requires_explicit_confirm(tmp_path: Path) -> None:
    """AC-7: no auto-accept — a recommendation followed by a non-affirmative
    reply commits NOTHING."""
    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    course = "course-content/courses/c1m1"
    append_pick_event(
        {"A": "alpha-style"},
        directive_path=tmp_path / "old.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course=course,
    )
    directive = tmp_path / "directive.yaml"
    replies = iter(["recommended", "nope"])
    with pytest.raises(PickerError, match="(?i)no confirmed"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=directive,
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=lambda _p: next(replies),
            print_fn=lambda _m: None,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            events_path=events,
            course=course,
            max_attempts=1,
        )
    assert not directive.exists()


def test_last_pick_derives_only_from_course_field(tmp_path: Path) -> None:
    """F-502: legacy events (no course field) are honestly 'no prior pick';
    directive_path is NEVER dereferenced as a course proxy."""
    from app.marcus.cli.marcus_spoc import _last_pick_for_course

    ssot = _ssot(tmp_path)  # P1: the lookup validates pickability vs the SSOT
    events = tmp_path / "picks.jsonl"
    # Legacy event: same directive_path a naive proxy would match, NO course.
    append_pick_event(
        {"A": "alpha-style"},
        directive_path=tmp_path / "runs" / "x" / "directive.yaml",
        picked_at="2026-06-01T00:00:00+00:00",
        events_path=events,
    )
    assert _last_pick_for_course("course-x", events_path=events, ssot_path=ssot) is None
    # Course-stamped events: the LATEST one wins.
    append_pick_event(
        {"A": "alpha-style"},
        directive_path=tmp_path / "runs" / "y" / "directive.yaml",
        picked_at="2026-06-02T00:00:00+00:00",
        events_path=events,
        course="course-x",
    )
    append_pick_event(
        {"A": "gamma-candidate", "B": "alpha-style"},
        directive_path=tmp_path / "runs" / "z" / "directive.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course="course-x",
    )
    last = _last_pick_for_course("course-x", events_path=events, ssot_path=ssot)
    assert last is not None
    assert last["picks"] == {"A": "gamma-candidate", "B": "alpha-style"}
    assert last["picked_at"] == "2026-07-01T00:00:00+00:00"


# ----------------------------------------------------------------- F-504 grammar pin
def test_hyphenated_uuid_run_tag_fails_loud_and_hex_passes() -> None:
    """F-504: `str(trial_id)` (hyphenated) FAILS LOUD at both producers;
    `trial_id.hex` is the run_tag rule."""
    with pytest.raises(PickerError, match="(?i)malformed|hyphen"):
        build_selection_code(str(TRIAL_ID), {"A": "alpha-style"})
    assert _RUN_TAG_RE.match(TRIAL_ID.hex)
    assert build_selection_code(TRIAL_ID.hex, {"A": "alpha-style"}).startswith(
        f"SGP-{TRIAL_ID.hex}-"
    )


# ============================================================================
# T11 remediation witnesses (spec §Review Findings P1..P18, RED-first)
# ============================================================================


def _ssot_with_extras(tmp_path: Path) -> Path:
    """Stub SSOT with a deprecated and a probe guide beside the two pickable ones."""
    ssot = tmp_path / "gamma-style-guides-extras.yaml"
    ssot.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "style_guides": {
                    "alpha-style": {
                        "lifecycle": "permanent",
                        "presentation": {
                            "display_name": "Alpha Look",
                            "distinguishing": "clean line art",
                        },
                    },
                    "gamma-candidate": {
                        "lifecycle": "candidate",
                        "presentation": {
                            "display_name": "Gamma Look",
                            "distinguishing": "bold collage",
                        },
                    },
                    "old-style": {
                        "lifecycle": "deprecated",
                        "presentation": {
                            "display_name": "Old Look",
                            "distinguishing": "retired",
                        },
                    },
                    "probe-style": {
                        "lifecycle": "candidate",
                        "presentation": {
                            "display_name": "Probe Look",
                            "distinguishing": "scaffolding",
                            "visibility": "probe",
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return ssot


def _expected_course_key(path: Path) -> str:
    """P4 canonical course key: resolved + os.path.normcase + posix form."""
    return Path(os.path.normcase(str(path.resolve()))).as_posix()


# --------------------------------------------------------------------- P1 witnesses
def test_last_pick_unpickable_guide_degrades_to_none(tmp_path: Path) -> None:
    """P1: a deprecated/deleted last pick is honestly 'no prior usable pick'."""
    from app.marcus.cli.marcus_spoc import _last_pick_for_course

    ssot = _ssot_with_extras(tmp_path)
    events = tmp_path / "picks.jsonl"
    append_pick_event(
        {"A": "old-style"},  # deprecated in the SSOT
        directive_path=tmp_path / "old.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course="course-dead",
    )
    append_pick_event(
        {"A": "ghost-style"},  # deleted from the SSOT entirely
        directive_path=tmp_path / "old2.yaml",
        picked_at="2026-07-02T00:00:00+00:00",
        events_path=events,
        course="course-ghost",
    )
    warnings: list[str] = []
    assert (
        _last_pick_for_course(
            "course-dead", events_path=events, ssot_path=ssot, warn_fn=warnings.append
        )
        is None
    )
    assert (
        _last_pick_for_course(
            "course-ghost", events_path=events, ssot_path=ssot, warn_fn=warnings.append
        )
        is None
    )
    assert warnings, "the degrade must be narrated, never silent"


def test_ceremony_never_recommends_unpickable_last_pick(tmp_path: Path) -> None:
    """P1: an unpickable last pick must not surface as a recommendation
    (no recommended dead-end that burns attempts)."""
    ssot = _ssot_with_extras(tmp_path)
    events = tmp_path / "picks.jsonl"
    course = "course-content/courses/dead"
    append_pick_event(
        {"A": "old-style"},
        directive_path=tmp_path / "old.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course=course,
    )
    printed: list[str] = []
    prompts: list[str] = []
    code = build_selection_code("abc12345", {"A": "alpha-style"})
    replies = iter([code, "confirm"])

    def _input(prompt: str) -> str:
        prompts.append(prompt)
        return next(replies)

    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=tmp_path / "directive.yaml",
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=_input,
        print_fn=printed.append,
        publish_fn=_fake_publish,
        ssot_path=ssot,
        events_path=events,
        course=course,
    )
    assert record is not None and record["picks"] == {"A": "alpha-style"}
    narration = "\n".join(printed)
    assert "My recommendation: reuse" not in narration
    assert not any("recommended" in p for p in prompts), (
        "the paste prompt must not offer accepting an unpickable recommendation"
    )


# --------------------------------------------------------------------- P2 witness
def test_trial_id_reuse_with_existing_run_record_fails_loud_pre_compose(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P2: run.json already present for --trial-id => fail loud BEFORE compose,
    naming resume/recover as the correct verbs."""
    from app.marcus.cli.trial import TrialAlreadyExistsError

    runs_root = tmp_path / "runs"
    run_dir = runs_root / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text("{}", encoding="utf-8")
    compose_calls: list[Any] = []
    monkeypatch.setattr(
        trial_module,
        "compose_and_write",
        lambda **kwargs: compose_calls.append(kwargs),
    )
    with pytest.raises(TrialAlreadyExistsError, match="(?i)resume.*recover|recover.*resume"):
        start_trial(**_start_args(stub_corpus, runs_root, auto_confirm_directive=True))
    assert compose_calls == [], "the exists-guard must fire BEFORE composition"


# --------------------------------------------------------------------- P3 witness
def test_selection_code_validated_pre_compose(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P3: --selection-code decode+pickability run PRE-compose — a stale code
    must never spend the composition LLM call."""
    compose_calls: list[Any] = []

    def _compose(**kwargs: Any) -> tuple[Path, str]:
        compose_calls.append(kwargs)
        run_dir = kwargs["run_dir"]
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "directive.yaml"
        path.write_text("sources: []\n", encoding="utf-8")
        return path, "0" * 64

    monkeypatch.setattr(trial_module, "compose_and_write", _compose)
    stale = build_selection_code(uuid4().hex, {"A": REAL_GUIDE})
    with pytest.raises(PickerError, match="(?i)stale|foreign"):
        start_trial(
            **_start_args(
                stub_corpus,
                tmp_path / "runs",
                auto_confirm_directive=True,
                selection_code=stale,
            )
        )
    assert compose_calls == [], "decode must fail loud BEFORE composition"


# --------------------------------------------------------------------- P4 witnesses
def test_course_key_is_canonical_across_spellings(
    stub_corpus: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P4: relative/absolute/drive-case spellings of the SAME corpus produce ONE
    course key (resolved + normcase + posix)."""
    _stub_compose(monkeypatch)
    seen: list[str] = []

    def _preflight(**kwargs: Any) -> None:
        seen.append(kwargs["course"])
        return None

    def _run(spelling: Path, trial_id: UUID, runs_root: Path) -> None:
        start_trial(
            **_start_args(
                stub_corpus,
                runs_root,
                trial_id=trial_id,
                input_path=spelling,
                auto_confirm_directive=False,
                confirm_fn=lambda **_k: "saved-only",
                picker_preflight_fn=_preflight,
            )
        )

    _run(stub_corpus, uuid4(), tmp_path / "runs-a")
    monkeypatch.chdir(tmp_path)
    _run(Path("corpus"), uuid4(), tmp_path / "runs-b")

    assert len(seen) == 2
    assert seen[0] == seen[1], "one corpus must key one pick-history bucket"
    assert seen[0] == _expected_course_key(stub_corpus)


# --------------------------------------------------------------------- P5 witnesses
def test_corrupt_sidecar_does_not_block_ceremony(tmp_path: Path) -> None:
    """P5: a corrupt pick-history line WARNs + degrades to 'no prior pick' —
    the LOOKUP is optional and must never block the ceremony. (Commit-time
    append to a corrupt store stays FAIL-LOUD per the A-1 store contract —
    only the optional lookup degrades.)"""
    from app.marcus.cli.marcus_spoc import _last_pick_for_course

    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    events.write_text("this-is-not-json{{{\n", encoding="utf-8")
    warnings: list[str] = []
    assert (
        _last_pick_for_course(
            "course-x", events_path=events, ssot_path=ssot, warn_fn=warnings.append
        )
        is None
    )
    assert warnings and "warning" in warnings[0].lower()

    # Ceremony-level: the degraded lookup lets the ceremony proceed all the way
    # to the paste prompt (no PickerError raised AT the lookup).
    printed: list[str] = []
    prompts: list[str] = []

    def _input(prompt: str) -> str:
        prompts.append(prompt)
        raise EOFError  # stop here — commit into the corrupt store is A-1 loud

    with pytest.raises(PickerError, match="(?i)abort"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=tmp_path / "directive.yaml",
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=_input,
            print_fn=printed.append,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            events_path=events,
            course="course-content/courses/c1m1",
        )
    assert prompts, "the ceremony must reach the paste prompt despite the corrupt sidecar"
    assert any("warning" in msg.lower() for msg in printed)


# --------------------------------------------------------------------- P6 witnesses
def test_eof_at_paste_prompt_becomes_clean_picker_error(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)

    def _eof(_prompt: str) -> str:
        raise EOFError

    with pytest.raises(PickerError, match="(?i)abort"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=tmp_path / "directive.yaml",
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=_eof,
            print_fn=lambda _m: None,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            events_path=tmp_path / "picks.jsonl",
        )


def test_keyboard_interrupt_at_confirm_prompt_becomes_clean_picker_error(
    tmp_path: Path,
) -> None:
    ssot = _ssot(tmp_path)
    code = build_selection_code("abc12345", {"A": "alpha-style"})
    replies = iter([code])

    def _input(prompt: str) -> str:
        try:
            return next(replies)
        except StopIteration:
            raise KeyboardInterrupt from None

    with pytest.raises(PickerError, match="(?i)abort"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=tmp_path / "directive.yaml",
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=_input,
            print_fn=lambda _m: None,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            events_path=tmp_path / "picks.jsonl",
        )
    assert not (tmp_path / "directive.yaml").exists()


# --------------------------------------------------------------------- P7 witnesses
def test_inline_pick_without_slot_a_is_bounded_by_shared_budget(tmp_path: Path) -> None:
    """P7: repeated inline passes without slot A consume the SHARED budget and
    the ceremony aborts with PickerError — never an unbounded loop."""
    ssot = _ssot(tmp_path)

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    replies = iter(["2", "", "", "", ""])
    with pytest.raises(PickerError, match="(?i)within 2 attempts|no confirmed"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=tmp_path / "directive.yaml",
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=lambda _p: next(replies),
            print_fn=lambda _m: None,
            publish_fn=_boom_publish,
            ssot_path=ssot,
            events_path=tmp_path / "picks.jsonl",
            max_attempts=2,
        )


def test_inline_pick_number_typos_are_bounded(tmp_path: Path) -> None:
    """P7: number typos re-prompt free (P8) but are capped — never unbounded."""
    ssot = _ssot(tmp_path)

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    replies = iter(["2"] + ["99"] * 50)
    with pytest.raises(PickerError, match="(?i)too many invalid"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=tmp_path / "directive.yaml",
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=lambda _p: next(replies),
            print_fn=lambda _m: None,
            publish_fn=_boom_publish,
            ssot_path=ssot,
            events_path=tmp_path / "picks.jsonl",
        )


# --------------------------------------------------------------------- P8 witnesses
def test_successful_publish_retry_does_not_refresh_budget(tmp_path: Path) -> None:
    """P8: ONE budget across the ceremony — a failed retry consumes, a
    successful retry carries the REMAINING budget into the paste loop."""
    ssot = _ssot(tmp_path)
    publish_calls: list[int] = []

    def _flaky_publish(**kwargs: Any) -> dict[str, Any]:
        publish_calls.append(1)
        if len(publish_calls) < 3:  # initial + first retry fail; second retry OK
            raise RuntimeError("syncing_files flake")
        return _fake_publish(**kwargs)

    good = build_selection_code("abc12345", {"A": "alpha-style"})
    replies = iter(["1", "1", "bad-code", good, "confirm"])
    with pytest.raises(PickerError, match="(?i)no confirmed"):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=tmp_path / "directive.yaml",
            out_dir=tmp_path / "out",
            picked_by="operator_test",
            input_fn=lambda _p: next(replies),
            print_fn=lambda _m: None,
            publish_fn=_flaky_publish,
            ssot_path=ssot,
            events_path=tmp_path / "picks.jsonl",
            max_attempts=2,
        )
    assert not (tmp_path / "directive.yaml").exists(), (
        "a refreshed budget would have let the good code through — the budget "
        "must be SHARED, not re-granted after a successful retry"
    )


def test_menu_typos_do_not_consume_attempts(tmp_path: Path) -> None:
    """P8: menu typos re-prompt without consuming — a single-attempt budget
    still completes a valid pick after two typos."""
    ssot = _ssot(tmp_path)

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    replies = iter(["9", "banana", "2", "1", "", "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=tmp_path / "directive.yaml",
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=lambda _m: None,
        publish_fn=_boom_publish,
        ssot_path=ssot,
        events_path=tmp_path / "picks.jsonl",
        max_attempts=1,
    )
    assert record is not None and record["picks"] == {"A": "alpha-style"}


def test_degrade_menu_omits_option_3_when_no_usable_prior_pick(tmp_path: Path) -> None:
    """P8: option 3 is NOT offered when unavailable — the menu presents exactly
    two ways forward and still recommends one."""
    ssot = _ssot(tmp_path)
    printed: list[str] = []

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    replies = iter(["2", "1", "", "confirm"])
    run_picker_preflight(
        run_tag="abc12345",
        directive_path=tmp_path / "directive.yaml",
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=printed.append,
        publish_fn=_boom_publish,
        ssot_path=ssot,
        events_path=tmp_path / "picks.jsonl",
        course="course-content/courses/never-seen",
    )
    menu = next(m for m in printed if "ways forward" in m)
    assert "1." in menu and "2." in menu
    assert "3." not in menu, "option 3 must not be offered without a usable prior pick"
    assert "recommend" in menu.lower()


def test_minted_code_reject_message_never_says_paste(tmp_path: Path) -> None:
    """P8: decode-reject messaging is context-correct — a MINTED code (inline
    probe pick) that fails decode must not tell the operator to 'paste it again'."""
    ssot = _ssot_with_extras(tmp_path)
    printed: list[str] = []

    def _boom_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("publish down")

    # include_probes=True -> roster: alpha-style(1), gamma-candidate(2), probe-style(3)
    replies = iter(["2", "3", "", "2", "1", "", "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=tmp_path / "directive.yaml",
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=printed.append,
        publish_fn=_boom_publish,
        ssot_path=ssot,
        events_path=tmp_path / "picks.jsonl",
        include_probes=True,
    )
    assert record is not None and record["picks"] == {"A": "alpha-style"}
    rejects = [m for m in printed if "didn't work" in m or "can't be locked in" in m]
    assert rejects, "the probe pick must be rejected at decode"
    assert not any("paste" in m.lower() for m in rejects), (
        "no 'paste it again' where there was no paste (minted-code context)"
    )


# --------------------------------------------------------------------- P9 witnesses
def test_beat1_never_promises_a_versions_default() -> None:
    """P9/F-606: Beat-1 states the recommendation verbatim — no false
    'I'll default to N versions' promise (no default engine exists)."""
    from app.marcus.cli.marcus_spoc import narrate_kickoff_beat1

    first = narrate_kickoff_beat1(course="c", recommendation=None).lower()
    rerun = narrate_kickoff_beat1(
        course="c",
        recommendation={"picks": {"A": "alpha-style"}, "picked_at": "2026-07-01"},
    ).lower()
    assert "default" not in first and "default" not in rerun
    assert "recommend" in first and "recommend" in rerun


def test_beat1_rerun_recommendation_carries_its_own_version_count() -> None:
    """P9: a two-version last pick is recommended AS two versions."""
    from app.marcus.cli.marcus_spoc import narrate_kickoff_beat1

    rerun_two = narrate_kickoff_beat1(
        course="c",
        recommendation={
            "picks": {"A": "alpha-style", "B": "gamma-candidate"},
            "picked_at": "2026-07-01",
        },
    ).lower()
    assert "two versions" in rerun_two and "a/b" in rerun_two


# --------------------------------------------------------------------- P10 witness
def test_redigest_after_confirm_loop_and_warn_on_pick_dropped_by_edit(
    stub_corpus: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """P10/F-604: the digest attests the POST-edit bytes; an edit that dropped
    the just-committed pick WARNs loudly."""
    _stub_compose(monkeypatch)
    monkeypatch.setattr(
        trial_module, "run_production_trial", lambda **_k: _fake_walk_envelope()
    )
    runs_root = tmp_path / "runs"
    code = build_selection_code(TRIAL_ID.hex, {"A": REAL_GUIDE})

    def _edit_confirm(*, directive_path: Path, auto_confirm_directive: bool) -> str:
        del auto_confirm_directive
        loaded = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
        loaded.pop("gamma_settings", None)  # the edit drops the committed pick
        directive_path.write_text(yaml.safe_dump(loaded, sort_keys=False), encoding="utf-8")
        return "confirmed"

    result = start_trial(
        **_start_args(
            stub_corpus,
            runs_root,
            auto_confirm_directive=False,
            confirm_fn=_edit_confirm,
            selection_code=code,
            picker_events_path=tmp_path / "picks.jsonl",
        )
    )
    directive = runs_root / str(TRIAL_ID) / "directive.yaml"
    assert result["directive_digest"] == hashlib.sha256(directive.read_bytes()).hexdigest(), (
        "the digest must attest the bytes the run actually uses (post-edit)"
    )
    err = capsys.readouterr().err
    assert "WARNING" in err and REAL_GUIDE in err, (
        "an edit that dropped the committed pick must WARN loudly"
    )


# --------------------------------------------------------------------- P11 witness
def test_selection_code_with_single_file_input_fails_loud(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P11: a single-file --input composes no directive — silently dropping an
    explicit --selection-code pick violates fail-loud."""
    monkeypatch.setattr(
        trial_module,
        "run_production_trial",
        lambda **_k: pytest.fail("the start must abort before the walk"),
    )
    single_file = tmp_path / "single.md"
    single_file.write_text("body", encoding="utf-8")
    code = build_selection_code(TRIAL_ID.hex, {"A": REAL_GUIDE})
    with pytest.raises(PickerError, match="(?i)directory|single-file"):
        start_trial(
            **_start_args(
                single_file,
                tmp_path / "runs",
                input_path=single_file,
                auto_confirm_directive=True,
                selection_code=code,
            )
        )


# --------------------------------------------------------------------- P12 witnesses
def test_last_pick_uses_parsed_timestamps_not_lexicographic(tmp_path: Path) -> None:
    """P12/F-603: the latest event is chosen by PARSED timestamp — an offset
    timestamp that is lexicographically smaller but chronologically later wins."""
    from app.marcus.cli.marcus_spoc import _last_pick_for_course

    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    append_pick_event(
        {"A": "alpha-style"},
        directive_path=tmp_path / "runs" / "a" / "directive.yaml",
        picked_at="2026-07-01T00:00:00+00:00",
        events_path=events,
        course="course-x",
    )
    # Lexicographically SMALLER ("2026-06-30..." < "2026-07-01...") yet
    # chronologically LATER (04:00 UTC on 07-01).
    append_pick_event(
        {"A": "gamma-candidate"},
        directive_path=tmp_path / "runs" / "b" / "directive.yaml",
        picked_at="2026-06-30T23:00:00-05:00",
        events_path=events,
        course="course-x",
    )
    last = _last_pick_for_course("course-x", events_path=events, ssot_path=ssot)
    assert last is not None
    assert last["picks"] == {"A": "gamma-candidate"}
    assert last["picked_at"] == "2026-06-30T23:00:00-05:00"


def test_last_pick_never_merges_across_events(tmp_path: Path) -> None:
    """P12: same-timestamp events from DIFFERENT commits are not merged — only
    the latest event's own commit group forms the pick."""
    from app.marcus.cli.marcus_spoc import _last_pick_for_course

    ssot = _ssot(tmp_path)
    events = tmp_path / "picks.jsonl"
    stamp = "2026-07-01T00:00:00+00:00"
    append_pick_event(
        {"A": "gamma-candidate", "B": "alpha-style"},
        directive_path=tmp_path / "runs" / "b" / "directive.yaml",
        picked_at=stamp,
        events_path=events,
        course="course-x",
    )
    # A DIFFERENT commit (other run) sharing the same timestamp string.
    append_pick_event(
        {"A": "alpha-style"},
        directive_path=tmp_path / "runs" / "c" / "directive.yaml",
        picked_at=stamp,
        events_path=events,
        course="course-x",
    )
    last = _last_pick_for_course("course-x", events_path=events, ssot_path=ssot)
    assert last is not None
    assert last["picks"] == {"A": "alpha-style"}, (
        "the tie breaks to the LAST event's commit group — never a cross-commit merge"
    )
    assert "B" not in last["picks"]


# --------------------------------------------------------------------- P13 witness
def test_publish_failure_narration_scrubs_urls_and_tokens(tmp_path: Path) -> None:
    """P13: raw URLs/token-shaped substrings in the publish exception never
    reach the operator narration."""
    ssot = _ssot(tmp_path)
    printed: list[str] = []

    def _leaky_publish(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError(
            "push failed for https://x-access-token:ghp_secret1234567890@github.com/o/r "
            "(token ghp_secret1234567890)"
        )

    replies = iter(["2", "1", "", "confirm"])
    run_picker_preflight(
        run_tag="abc12345",
        directive_path=tmp_path / "directive.yaml",
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=printed.append,
        publish_fn=_leaky_publish,
        ssot_path=ssot,
        events_path=tmp_path / "picks.jsonl",
    )
    narration = "\n".join(printed)
    assert "ghp_secret1234567890" not in narration
    assert "https://" not in narration
    assert "RuntimeError" in narration, "keep the class name for diagnosis"


# --------------------------------------------------------------------- P16 witness
def test_non_affirmative_confirm_reply_is_decoded_as_fresh_code(tmp_path: Path) -> None:
    """P16: the confirm prompt says 'or paste a new code' — honor it: a valid
    code pasted AT the confirm prompt replaces the pending pick."""
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"
    code_a = build_selection_code("abc12345", {"A": "alpha-style"})
    code_b = build_selection_code("abc12345", {"A": "gamma-candidate"})
    replies = iter([code_a, code_b, "confirm"])
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=directive,
        out_dir=tmp_path / "out",
        picked_by="operator_test",
        input_fn=lambda _p: next(replies),
        print_fn=lambda _m: None,
        publish_fn=_fake_publish,
        ssot_path=ssot,
        events_path=tmp_path / "picks.jsonl",
    )
    assert record is not None
    assert record["picks"] == {"A": "gamma-candidate"}, (
        "the code pasted at the confirm prompt must be the one committed"
    )
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    assert loaded["styleguide_picker_provenance"]["selection_code"] == code_b


# --------------------------------------------------------------------- P17 witness
def test_default_preflight_requires_stdin_and_stdout_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P17/F-601: a tty stdin with a piped stdout is NOT interactive — the
    default preflight must stay pickless."""

    class _Tty:
        def isatty(self) -> bool:
            return True

    class _Pipe:
        def isatty(self) -> bool:
            return False

    monkeypatch.setattr(
        trial_module,
        "run_picker_preflight",
        lambda **_k: pytest.fail("the ceremony must not run without a full tty"),
    )
    monkeypatch.setattr(sys, "stdin", _Tty())
    monkeypatch.setattr(sys, "stdout", _Pipe())
    assert trial_module._default_picker_preflight() is None
    monkeypatch.setattr(sys, "stdin", _Pipe())
    monkeypatch.setattr(sys, "stdout", _Tty())
    assert trial_module._default_picker_preflight() is None


# --------------------------------------------------------------------- P18 witness
def test_read_pick_events_is_public_with_back_compat_alias() -> None:
    from app.marcus.orchestrator import styleguide_picker

    assert callable(styleguide_picker.read_pick_events)
    assert styleguide_picker._read_pick_events is styleguide_picker.read_pick_events
    assert "read_pick_events" in styleguide_picker.__all__


# ----------------------------------------------------------------- CLI arg surface
def test_trial_parser_carries_selection_code_arg() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    args = parser.parse_args(
        [
            "start",
            "--input",
            "x",
            "--trial-id",
            str(TRIAL_ID),
            "--selection-code",
            f"SGP-{TRIAL_ID.hex}-A:{REAL_GUIDE}",
        ]
    )
    assert args.selection_code == f"SGP-{TRIAL_ID.hex}-A:{REAL_GUIDE}"
