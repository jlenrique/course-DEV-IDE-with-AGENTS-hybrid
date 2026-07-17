"""Story 43-2 — generic gate-content table + renderer registry.

Replay-only against ``tests/fixtures/hil_projector/`` (zero live spend). Proves:

* AC-1 the renderer registry is enumerable / introspectable and the generic
  fallback is returned for any unregistered content type;
* AC-2 the generic renderer bounds nested values (no raw nested dump);
* AC-3 every paused gate tables its OWN content — RED-anchored on the G1 decision
  card fixture rendering via the generic path;
* AC-4 the ``recover`` and ``resume-batch`` front doors call the projector on a
  paused payload;
* AC-5 stdout stays machine JSON while the human table goes to stderr on the SAME
  invocation (rider R4);
* AC-6 a consistent one-line raw-access pointer rides on stderr at every gate.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

import app.marcus.cli.trial as trial
from app.marcus.cli import hil_tabular_projector as proj
from app.marcus.cli.hil_tabular_projector import (
    build_gate_surface,
    emit_gate_surface,
    get_renderer,
    register_renderer,
    registered_content_types,
    render_generic_gate_content,
    render_hil_tables,
)

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "hil_projector"
G1_CARD_FIXTURE = FIXTURES / "decision-card-g1-bc747b51.json"
TRIAL_ID = "bc747b51-7009-4742-9f65-8de6abc29ca4"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _g1_card() -> dict:
    return _load(G1_CARD_FIXTURE)["card"]


# ---------------------------------------------------------------------------
# AC-1 — renderer registry is enumerable / introspectable + generic fallback.
# ---------------------------------------------------------------------------


def test_registry_is_enumerable_and_falls_back_to_generic() -> None:
    types = registered_content_types()
    assert isinstance(types, frozenset)  # 43-10 consumes this enumerable set

    # unknown content type -> generic fallback renderer
    assert get_renderer("totally-unknown-gate") is render_generic_gate_content
    assert get_renderer(None) is render_generic_gate_content


def test_register_renderer_is_the_extension_point() -> None:
    def _sentinel(content, **kwargs):  # noqa: ANN001, ANN003, ARG001 — test stub
        return "SENTINEL-TABLE"

    assert "test-only-43-2" not in registered_content_types()
    register_renderer("test-only-43-2", _sentinel)
    try:
        assert "test-only-43-2" in registered_content_types()
        assert get_renderer("test-only-43-2") is _sentinel
    finally:
        proj._RENDERER_REGISTRY.pop("test-only-43-2", None)
    assert "test-only-43-2" not in registered_content_types()


def test_register_renderer_rejects_empty_key() -> None:
    with pytest.raises(ValueError):
        register_renderer("", lambda content, **kw: "")  # noqa: ARG005


# ---------------------------------------------------------------------------
# AC-2 — generic renderer bounds nested/complex values (never raw-dumps).
# ---------------------------------------------------------------------------


def test_generic_renderer_bounds_deeply_nested_value() -> None:
    marker = "SECRET_MARKER_" + "X" * 500
    content = {
        "operator_prompt": "Confirm the plan",
        "deep_field": {"a": {"b": {"c": {"leaf": marker}}}},
        "list_field": [{"k": 1}, {"k": 2}, {"k": 3}],
        "scalar": "hello",
    }
    out = render_generic_gate_content(content, title="Gate content")

    # the raw deep value is never dumped
    assert marker not in out
    assert "leaf" not in out
    # nested dict summarized as a field digest; list summarized by count
    assert "1 field(s): a" in out
    assert "3 item(s)" in out
    # scalars pass through
    assert "| scalar | hello |" in out
    # width-aware: no cell blows the line width out (rider R5)
    for line in out.splitlines():
        assert len(line) <= 120


def test_generic_renderer_tables_the_g1_card() -> None:
    card = _g1_card()
    out = render_generic_gate_content(card, title="Gate G1 content")
    assert "**Gate G1 content**" in out
    assert "| Field | Value |" in out
    # real card fields present as rows
    assert "| verb | approve |" in out
    assert "| gate_focus | trial_open |" in out
    # nested drafted_proposal / evidence are summarized (field digest = key
    # NAMES), but their deep VALUES are never raw-dumped
    assert "irene_lo_thin_gap:3" not in out  # a confidence_signals value, deep inside
    assert "Ingestion is broadly solid" not in out  # the long rationale value


# ---------------------------------------------------------------------------
# AC-3 — RED-anchored: the paused G1 gate tables its OWN content via the
# generic path (fails before the _emit_gate_surface_if_paused wiring).
# ---------------------------------------------------------------------------


def _paused_g1_run(tmp_path: Path) -> tuple[Path, dict]:
    run_dir = tmp_path / TRIAL_ID
    run_dir.mkdir(parents=True)
    (run_dir / "decision-card-G1.json").write_text(
        G1_CARD_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    payload = {
        "status": "paused-at-gate",
        "trial_id": TRIAL_ID,
        "paused_gate": "G1",
        "run_registry_path": str(run_dir / "run.json"),
    }
    return run_dir, payload


def test_emit_gate_surface_if_paused_tables_g1_card(tmp_path: Path) -> None:
    _run_dir, payload = _paused_g1_run(tmp_path)
    buf = io.StringIO()
    # redirect the projector's stderr stream to a buffer we can read
    import sys

    orig = sys.stderr
    sys.stderr = buf
    try:
        trial._emit_gate_surface_if_paused(payload, runs_root=tmp_path)
    finally:
        sys.stderr = orig
    err = buf.getvalue()

    # AC-3: the paused G1 gate tables its own content (RED before wiring)
    assert "**Gate G1 content**" in err
    assert "trial_open" in err  # gate_focus, only present via the gate-content table
    assert "Production graph reached Gate 1" in err  # trial_summary
    # AC-6: consistent raw-access pointer on the human surface
    assert "raw: full machine JSON on stdout" in err


# ---------------------------------------------------------------------------
# AC-4 + AC-5 + AC-6 — front-door coverage: recover / resume-batch call the
# projector; stdout JSON + stderr table split on the SAME invocation.
# ---------------------------------------------------------------------------


def _recover_args(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        trial_id=UUID(TRIAL_ID),
        runs_root=str(tmp_path),
        max_specialist_calls=None,
        reenter_at_node=None,
        course_source_root=None,
        encounter_mode=None,
    )


def test_recover_front_door_emits_table_and_splits_streams(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _run_dir, payload = _paused_g1_run(tmp_path)
    monkeypatch.setattr(trial, "recover_trial", lambda **kwargs: payload)

    rc = trial.recover_trial_cli(_recover_args(tmp_path))
    captured = capsys.readouterr()

    assert rc == 0
    # AC-5: stdout is untouched machine JSON
    stdout_payload = json.loads(captured.out)
    assert stdout_payload["status"] == "paused-at-gate"
    assert stdout_payload["paused_gate"] == "G1"
    assert "**Gate G1 content**" not in captured.out  # no table leaked to stdout
    # AC-4: the recover front door now tables its gate content on stderr
    assert "**Gate G1 content**" in captured.err
    assert "trial_open" in captured.err
    # AC-6: raw-access pointer present
    assert "raw: full machine JSON on stdout" in captured.err


def test_resume_batch_front_door_emits_table_and_splits_streams(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _run_dir, payload = _paused_g1_run(tmp_path)
    monkeypatch.setattr(trial, "resume_batch_trial", lambda **kwargs: payload)

    args = SimpleNamespace(
        trial_id=UUID(TRIAL_ID), runs_root=str(tmp_path), max_specialist_calls=None
    )
    rc = trial.resume_batch_trial_cli(args)
    captured = capsys.readouterr()

    assert rc == 0
    # AC-5: stdout JSON intact
    assert json.loads(captured.out)["status"] == "paused-at-gate"
    assert "**Gate G1 content**" not in captured.out
    # AC-4: resume-batch front door tables the gate content on stderr
    assert "**Gate G1 content**" in captured.err
    assert "raw: full machine JSON on stdout" in captured.err


def test_front_door_skips_emit_when_not_paused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A non-paused payload must NOT emit a gate table (early-return preserved)."""
    payload = {"status": "completed", "trial_id": TRIAL_ID, "paused_gate": None}
    monkeypatch.setattr(trial, "recover_trial", lambda **kwargs: payload)

    rc = trial.recover_trial_cli(_recover_args(tmp_path))
    captured = capsys.readouterr()

    assert rc == 0
    assert json.loads(captured.out)["status"] == "completed"
    assert "Gate content" not in captured.err
    assert "raw: full machine JSON on stdout" not in captured.err


# ---------------------------------------------------------------------------
# AC-7 — additive-within-v1: gate_content is a new optional surface part.
# ---------------------------------------------------------------------------


def test_gate_content_is_optional_additive_part() -> None:
    # a surface WITHOUT gate_content renders exactly as before (no new section)
    identity = {"trial": "t-1", "status": "paused-at-gate", "gate": "G1", "ask": ""}
    surface_without = build_gate_surface(gate_identity=identity)
    assert "gate_content" not in surface_without
    assert "Gate content" not in render_hil_tables(surface_without)

    # supplying it adds a generic table — no schema field renamed/removed
    surface_with = build_gate_surface(
        gate_identity=identity,
        gate_content={"content": _g1_card(), "content_type": "G1", "title": "Gate G1 content"},
    )
    out = render_hil_tables(surface_with)
    assert "**Gate G1 content**" in out
    assert "| Trial | t-1 |" in out  # identity section still present


def test_emit_gate_surface_raw_pointer_and_streams() -> None:
    """AC-5/AC-6 at the printer seam: table + raw pointer both land on one stream."""
    identity = {"trial": "t-1", "status": "paused-at-gate", "gate": "G1", "ask": ""}
    surface = build_gate_surface(
        gate_identity=identity,
        gate_content={"content": _g1_card(), "content_type": "G1", "title": "Gate G1 content"},
    )
    buf = io.StringIO()
    emit_gate_surface(
        surface,
        stream=buf,
        raw_artifact="C:/runs/bc747b51/operator-surface.json",
        shell_context="your shell prompt (PowerShell on Windows)",
    )
    out = buf.getvalue()
    assert "**Gate G1 content**" in out
    expected_raw = (
        "raw: full machine JSON on stdout · on-disk: "
        "C:/runs/bc747b51/operator-surface.json"
    )
    assert expected_raw in out
    assert "PAUSED" in out and "G1" in out
