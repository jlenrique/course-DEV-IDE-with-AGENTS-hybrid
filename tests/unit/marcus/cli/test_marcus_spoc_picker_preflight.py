"""RED-first proof of the marcus_spoc PRE-FLIGHT styleguide-picker seam (Seam 3).

The pre-flight beat runs BEFORE G1: surface the published url + a numbered-row HIL
instruction, then decode a pasted SELECTION CODE, echo-and-confirm in human terms,
and on confirm write the directive + append the sidecar event with A7 provenance.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.marcus.cli.marcus_spoc import (
    commit_picker_pick,
    decode_and_echo_pick,
    narrate_picker_preflight,
    run_picker_preflight,
)
from app.marcus.orchestrator.styleguide_picker import PickerError


def _ssot(tmp_path: Path) -> Path:
    ssot = tmp_path / "gamma-style-guides.yaml"
    ssot.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "style_guides": {
                    "alpha-style": {
                        "lifecycle": "permanent",
                        "presentation": {"display_name": "Alpha Look", "distinguishing": "d"},
                    },
                    "gamma-candidate": {
                        "lifecycle": "candidate",
                        "presentation": {"display_name": "Gamma Look", "distinguishing": "d"},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return ssot


def test_preflight_narration_is_client_facing() -> None:
    text = narrate_picker_preflight("https://x.github.io/p/index.html", "abc12345")
    assert "https://x.github.io/p/index.html" in text
    # numbered-row HIL instruction, paste-back close
    assert "selection code" in text.lower()
    assert "paste" in text.lower()
    # client-facing: no internal slug / directive vocabulary leaks
    assert "directive" not in text.lower()
    assert "styleguide_picker" not in text


def test_decode_and_echo_names_guides_and_version_count(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    picks, echo = decode_and_echo_pick(
        "SGP-abc12345-A:gamma-candidate B:alpha-style",
        expected_run_tag="abc12345",
        ssot_path=ssot,
    )
    assert picks == {"A": "gamma-candidate", "B": "alpha-style"}
    # human-readable echo: display names + lifecycle + version count, no raw directive
    assert "Gamma Look" in echo
    assert "Alpha Look" in echo
    assert "candidate" in echo.lower()
    assert "2 versions" in echo.lower()
    assert "confirm" in echo.lower()


def test_decode_and_echo_single_version(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    picks, echo = decode_and_echo_pick(
        "SGP-abc12345-A:alpha-style", expected_run_tag="abc12345", ssot_path=ssot
    )
    assert picks == {"A": "alpha-style"}
    assert "1 version" in echo.lower()


def test_decode_and_echo_propagates_stale_code(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)stale|foreign|run"):
        decode_and_echo_pick(
            "SGP-otherrun-A:alpha-style", expected_run_tag="abc12345", ssot_path=ssot
        )


def test_commit_writes_directive_sidecar_and_a7_provenance(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"
    events = tmp_path / "picks.jsonl"
    record = commit_picker_pick(
        {"A": "alpha-style", "B": "gamma-candidate"},
        directive_path=directive,
        expected_run_tag="abc12345",
        publish_url="https://x.github.io/p/index.html",
        picked_by="client:tejal",
        code="SGP-abc12345-A:alpha-style B:gamma-candidate",
        confirmed=True,
        ssot_path=ssot,
        events_path=events,
    )
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    settings = {row["variant_id"]: row["styleguide"] for row in loaded["gamma_settings"]}
    assert settings == {"A": "alpha-style", "B": "gamma-candidate"}

    prov = loaded["styleguide_picker_provenance"]
    # A7: who / from-url / roster hash / version count / the code itself
    assert prov["picked_by"] == "client:tejal"
    assert prov["publish_url"] == "https://x.github.io/p/index.html"
    assert prov["selection_code"] == "SGP-abc12345-A:alpha-style B:gamma-candidate"
    assert prov["version_count"] == 2
    assert prov.get("roster_sha256")
    assert record["picks"] == {"A": "alpha-style", "B": "gamma-candidate"}

    # one sidecar event line per pick
    lines = [ln for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2


def test_commit_unattributable_pick_fails_loud(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)attribut|picked_by|who"):
        commit_picker_pick(
            {"A": "alpha-style"},
            directive_path=tmp_path / "d.yaml",
            expected_run_tag="abc12345",
            publish_url="https://x.github.io/p/index.html",
            picked_by="",
            code="SGP-abc12345-A:alpha-style",
            confirmed=True,
            ssot_path=ssot,
            events_path=tmp_path / "e.jsonl",
        )


# ---------------------------------------------------------------- MUST-5 confirm gate
def test_commit_without_confirm_is_rejected(tmp_path: Path) -> None:
    """A caller cannot decode-then-commit directly, bypassing the echo-and-confirm."""
    ssot = _ssot(tmp_path)
    directive = tmp_path / "d.yaml"
    with pytest.raises(PickerError, match="(?i)confirm|refus"):
        commit_picker_pick(
            {"A": "alpha-style"},
            directive_path=directive,
            expected_run_tag="abc12345",
            publish_url="https://x.github.io/p/index.html",
            picked_by="client:tejal",
            code="SGP-abc12345-A:alpha-style",
            # confirmed omitted -> defaults False -> rejected
            ssot_path=ssot,
            events_path=tmp_path / "e.jsonl",
        )
    assert not directive.exists(), "an unconfirmed commit must not write the directive"


def test_commit_rederives_picks_from_code_and_rejects_disagreement(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)disagree|decode"):
        commit_picker_pick(
            {"A": "gamma-candidate"},  # disagrees with the code below
            directive_path=tmp_path / "d.yaml",
            expected_run_tag="abc12345",
            publish_url="https://x.github.io/p/index.html",
            picked_by="client:tejal",
            code="SGP-abc12345-A:alpha-style",
            confirmed=True,
            ssot_path=ssot,
            events_path=tmp_path / "e.jsonl",
        )


def test_run_picker_preflight_happy_path_binds_ab(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"
    events = tmp_path / "picks.jsonl"

    def _fake_publish(**kwargs):
        return {
            "publish_url": "https://x.github.io/p/index.html",
            "run_tag": kwargs["run_tag"],
            "style_count": 2,
        }

    replies = iter(
        ["SGP-abc12345-A:alpha-style B:gamma-candidate", "confirm"]
    )
    record = run_picker_preflight(
        run_tag="abc12345",
        directive_path=directive,
        out_dir=tmp_path / "out",
        picked_by="client:tejal",
        input_fn=lambda _prompt: next(replies),
        print_fn=lambda _msg: None,
        publish_fn=_fake_publish,
        ssot_path=ssot,
        events_path=events,
    )
    assert record["picks"] == {"A": "alpha-style", "B": "gamma-candidate"}
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    settings = {row["variant_id"]: row["styleguide"] for row in loaded["gamma_settings"]}
    assert settings == {"A": "alpha-style", "B": "gamma-candidate"}
    prov = loaded["styleguide_picker_provenance"]
    assert prov["selection_code"] == "SGP-abc12345-A:alpha-style B:gamma-candidate"
    assert prov["picked_by"] == "client:tejal"


def test_run_picker_preflight_stale_code_rejected_before_commit(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"

    def _fake_publish(**kwargs):
        return {"publish_url": "https://x/p.html", "run_tag": kwargs["run_tag"], "style_count": 2}

    replies = iter(["SGP-otherrun-A:alpha-style"])
    with pytest.raises(PickerError):
        run_picker_preflight(
            run_tag="abc12345",
            directive_path=directive,
            out_dir=tmp_path / "out",
            picked_by="client:tejal",
            input_fn=lambda _prompt: next(replies),
            print_fn=lambda _msg: None,
            publish_fn=_fake_publish,
            ssot_path=ssot,
            events_path=tmp_path / "picks.jsonl",
            max_attempts=1,
        )
    assert not directive.exists(), "a stale code must be rejected before any commit"


# ---------------------------------------------------------------- MUST-3 idempotency
def test_reconfirm_same_code_is_a_true_no_op(tmp_path: Path) -> None:
    """Re-committing the SAME (run_tag, code) appends exactly ONE sidecar event set
    and leaves exactly one provenance block, despite a fresh picked_at each call."""
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"
    events = tmp_path / "picks.jsonl"
    args = dict(
        directive_path=directive,
        expected_run_tag="abc12345",
        publish_url="https://x.github.io/p/index.html",
        picked_by="client:tejal",
        code="SGP-abc12345-A:alpha-style B:gamma-candidate",
        confirmed=True,
        ssot_path=ssot,
        events_path=events,
    )
    commit_picker_pick(**args)
    commit_picker_pick(**args)  # identical re-paste
    lines = [ln for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2, "identical re-confirm must not duplicate sidecar events"
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    # provenance is a single mapping, never a list of two blocks
    assert isinstance(loaded["styleguide_picker_provenance"], dict)


def test_different_code_same_run_appends_last_write_wins(tmp_path: Path) -> None:
    ssot = _ssot(tmp_path)
    directive = tmp_path / "directive.yaml"
    events = tmp_path / "picks.jsonl"
    base = dict(
        directive_path=directive,
        expected_run_tag="abc12345",
        publish_url="https://x.github.io/p/index.html",
        picked_by="client:tejal",
        confirmed=True,
        ssot_path=ssot,
        events_path=events,
    )
    commit_picker_pick(code="SGP-abc12345-A:alpha-style", **base)
    commit_picker_pick(code="SGP-abc12345-A:gamma-candidate", **base)
    lines = [ln for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2, "a deliberate different pick must append a new event"
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    settings = {row["variant_id"]: row["styleguide"] for row in loaded["gamma_settings"]}
    assert settings["A"] == "gamma-candidate", "last write wins on the directive"


# ---------------------------------------------------------------- SHOULD-7 caveat
def test_preflight_narration_carries_go_live_caveat() -> None:
    text = narrate_picker_preflight("https://x.github.io/p/index.html", "abc12345")
    lowered = text.lower()
    assert "minute" in lowered
    assert "refresh" in lowered or "wait" in lowered
