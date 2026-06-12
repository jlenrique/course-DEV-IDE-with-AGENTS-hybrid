"""Storyboard auto-publish seam pins (S5 criterion 7, operator-ratified 2026-06-12).

G2C approval = operator approval of Storyboard A in its ONLINE interactive
incarnation; publication is the pipeline's job. The seam invokes the proven
legacy generate-storyboard routine (generate + publish) at the gate pause;
failures are SpecialistDispatchError (error-pause + `trial recover`).
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.orchestrator import storyboard_publisher
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.specialists.dispatch_errors import SpecialistDispatchError

TRIAL_ID = UUID("62345678-1234-4234-8234-123456789abc")


def _envelope_with_gary() -> ProductionEnvelope:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="gary",
            output={"gary_slide_output": [{"slide_id": "s1", "file_path": "x.png"}]},
            model_used="gpt-5-nano",
            cost_usd=0.0,
            node_id="07",
        )
    )
    return envelope


def test_non_storyboard_gate_is_a_no_op(tmp_path: Path) -> None:
    result = storyboard_publisher.publish_storyboard_for_gate(
        gate_id="G1",
        trial_id=str(TRIAL_ID),
        production_envelope=ProductionEnvelope(trial_id=TRIAL_ID),
        runs_root=tmp_path,
    )
    assert result is None


def test_missing_token_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(storyboard_publisher.TOKEN_ENV_VAR, raising=False)
    with pytest.raises(storyboard_publisher.StoryboardPublishError) as excinfo:
        storyboard_publisher.publish_storyboard_for_gate(
            gate_id="G2C",
            trial_id=str(TRIAL_ID),
            production_envelope=_envelope_with_gary(),
            runs_root=tmp_path,
        )
    assert excinfo.value.tag == "storyboard.publish.token-missing"


def test_missing_gary_contribution_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(storyboard_publisher.TOKEN_ENV_VAR, "tok")
    with pytest.raises(storyboard_publisher.StoryboardPublishError) as excinfo:
        storyboard_publisher.publish_storyboard_for_gate(
            gate_id="G2C",
            trial_id=str(TRIAL_ID),
            production_envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            runs_root=tmp_path,
        )
    assert excinfo.value.tag == "storyboard.input.missing-gary"


def test_happy_path_invokes_generate_then_publish_and_records(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(storyboard_publisher.TOKEN_ENV_VAR, "tok")
    calls: list[tuple[str, Namespace]] = []
    exports_dir = tmp_path / "exports-root"
    exports_dir.mkdir()
    receipt = {
        "status": "published",
        "publish_url": f"https://example.test/assets/storyboards/{TRIAL_ID}/index.html",
    }

    class _FakeModule:
        DEFAULT_EXPORTS_DIR = exports_dir
        DEFAULT_PUBLISH_SUBDIR = "assets/storyboards"

        @staticmethod
        def cmd_generate(ns: Namespace) -> int:
            calls.append(("generate", ns))
            return 0

        @staticmethod
        def cmd_publish(ns: Namespace) -> int:
            calls.append(("publish", ns))
            (exports_dir / f"storyboard-{TRIAL_ID}-publish-receipt.json").write_text(
                json.dumps(receipt), encoding="utf-8"
            )
            return 0

    monkeypatch.setattr(
        storyboard_publisher, "_load_generator_module", lambda: _FakeModule
    )

    result = storyboard_publisher.publish_storyboard_for_gate(
        gate_id="G2C",
        trial_id=str(TRIAL_ID),
        production_envelope=_envelope_with_gary(),
        runs_root=tmp_path,
    )

    assert [name for name, _ in calls] == ["generate", "publish"]
    gen_ns = calls[0][1]
    assert gen_ns.strict is True
    assert gen_ns.run_id == str(TRIAL_ID)
    assert result is not None and result["publish_url"] == receipt["publish_url"]
    record = json.loads(Path(result["record_path"]).read_text(encoding="utf-8"))
    assert record["gate_id"] == "G2C"
    assert record["publish_url"] == receipt["publish_url"]
    # payload written from the envelope's gary output
    payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "exports" / "gary-dispatch-payload.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["gary_slide_output"][0]["slide_id"] == "s1"


def _envelope_with_gary_and_irene() -> ProductionEnvelope:
    envelope = _envelope_with_gary()
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene",
            output={
                "narration_script": [
                    {"id": "seg-1", "narration_text": "Opening narration."}
                ],
                "segment_manifest_deltas": [
                    {
                        "id": "seg-1",
                        "timing_role": "concept-build",
                        "visual_references": [{"perception_source": "s1"}],
                    }
                ],
            },
            model_used="gpt-5",
            cost_usd=0.0,
            node_id="08",
        )
    )
    return envelope


def test_storyboard_gate_roster_pins_a_and_b() -> None:
    # PIN-B1: the pre-filed Storyboard-B rider landed as a roster entry
    # (dp-v1.1, S5 criterion 7 — B reviews happen ONLINE at G3B).
    assert storyboard_publisher.STORYBOARD_GATES == {
        "G2C": "storyboard-A",
        "G3B": "storyboard-B",
    }


def test_g3b_missing_irene_contribution_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(storyboard_publisher.TOKEN_ENV_VAR, "tok")
    with pytest.raises(storyboard_publisher.StoryboardPublishError) as excinfo:
        storyboard_publisher.publish_storyboard_for_gate(
            gate_id="G3B",
            trial_id=str(TRIAL_ID),
            production_envelope=_envelope_with_gary(),
            runs_root=tmp_path,
        )
    assert excinfo.value.tag == "storyboard.input.missing-irene"


def test_g3b_threads_segment_manifest_and_distinct_slug(
    tmp_path: Path, monkeypatch
) -> None:
    """PIN-B2 (publisher leg): at G3B the generate call receives a REAL
    segment-manifest path (non-None — fields-passed-as-None is the hollow
    payload shape) and the pack publishes under its own run id so the B pack
    never overwrites the operator-approved A pack."""
    monkeypatch.setenv(storyboard_publisher.TOKEN_ENV_VAR, "tok")
    calls: list[tuple[str, Namespace]] = []
    exports_dir = tmp_path / "exports-root"
    exports_dir.mkdir()
    receipt = {
        "status": "published",
        "publish_url": f"https://example.test/assets/storyboards/{TRIAL_ID}-b/index.html",
    }

    class _FakeModule:
        DEFAULT_EXPORTS_DIR = exports_dir
        DEFAULT_PUBLISH_SUBDIR = "assets/storyboards"

        @staticmethod
        def cmd_generate(ns: Namespace) -> int:
            calls.append(("generate", ns))
            return 0

        @staticmethod
        def cmd_publish(ns: Namespace) -> int:
            calls.append(("publish", ns))
            (
                exports_dir / f"storyboard-{TRIAL_ID}-b-publish-receipt.json"
            ).write_text(json.dumps(receipt), encoding="utf-8")
            return 0

    monkeypatch.setattr(
        storyboard_publisher, "_load_generator_module", lambda: _FakeModule
    )

    result = storyboard_publisher.publish_storyboard_for_gate(
        gate_id="G3B",
        trial_id=str(TRIAL_ID),
        production_envelope=_envelope_with_gary_and_irene(),
        runs_root=tmp_path,
    )

    assert [name for name, _ in calls] == ["generate", "publish"]
    gen_ns = calls[0][1]
    assert gen_ns.run_id == f"{TRIAL_ID}-b"
    assert gen_ns.segment_manifest is not None
    manifest_text = Path(gen_ns.segment_manifest).read_text(encoding="utf-8")
    assert "slide_id: s1" in manifest_text
    assert "Opening narration." in manifest_text
    assert result is not None and result["label"] == "storyboard-B"
    record = json.loads(Path(result["record_path"]).read_text(encoding="utf-8"))
    assert record["gate_id"] == "G3B"


def test_g2c_still_passes_no_segment_manifest(tmp_path: Path, monkeypatch) -> None:
    """A-side behavior preserved byte-for-byte (Amelia: fork the pin, don't
    loosen it): G2C generates with segment_manifest=None and the bare trial
    run id."""
    monkeypatch.setenv(storyboard_publisher.TOKEN_ENV_VAR, "tok")
    captured: list[Namespace] = []
    exports_dir = tmp_path / "exports-root"
    exports_dir.mkdir()

    class _FakeModule:
        DEFAULT_EXPORTS_DIR = exports_dir
        DEFAULT_PUBLISH_SUBDIR = "assets/storyboards"

        @staticmethod
        def cmd_generate(ns: Namespace) -> int:
            captured.append(ns)
            return 0

        @staticmethod
        def cmd_publish(ns: Namespace) -> int:
            (exports_dir / f"storyboard-{TRIAL_ID}-publish-receipt.json").write_text(
                json.dumps({"publish_url": "https://example.test/a"}),
                encoding="utf-8",
            )
            return 0

    monkeypatch.setattr(
        storyboard_publisher, "_load_generator_module", lambda: _FakeModule
    )
    storyboard_publisher.publish_storyboard_for_gate(
        gate_id="G2C",
        trial_id=str(TRIAL_ID),
        production_envelope=_envelope_with_gary_and_irene(),
        runs_root=tmp_path,
    )
    assert captured[0].segment_manifest is None
    assert captured[0].run_id == str(TRIAL_ID)


def test_segment_manifest_join_failure_fails_loud(tmp_path: Path) -> None:
    # Deltas that join to zero slides → nothing to overlay → typed raise.
    with pytest.raises(storyboard_publisher.StoryboardPublishError) as excinfo:
        storyboard_publisher._write_segment_manifest_for_b(
            run_dir=tmp_path,
            irene_output={
                "narration_script": [{"id": "seg-1", "narration_text": "x"}],
                "segment_manifest_deltas": [{"id": "seg-1", "visual_references": []}],
            },
        )
    assert excinfo.value.tag == "storyboard.input.missing-irene"


def test_publish_failure_raises_recoverable_family(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(storyboard_publisher.TOKEN_ENV_VAR, "tok")

    class _FakeModule:
        DEFAULT_EXPORTS_DIR = tmp_path
        DEFAULT_PUBLISH_SUBDIR = "assets/storyboards"

        @staticmethod
        def cmd_generate(ns: Namespace) -> int:
            return 0

        @staticmethod
        def cmd_publish(ns: Namespace) -> int:
            raise RuntimeError("github push rejected")

    monkeypatch.setattr(
        storyboard_publisher, "_load_generator_module", lambda: _FakeModule
    )
    with pytest.raises(SpecialistDispatchError) as excinfo:
        storyboard_publisher.publish_storyboard_for_gate(
            gate_id="G2C",
            trial_id=str(TRIAL_ID),
            production_envelope=_envelope_with_gary(),
            runs_root=tmp_path,
        )
    assert excinfo.value.tag == "storyboard.publish.failed"
