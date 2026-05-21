"""Regression tests for write-authorized-storyboard.py (Storyboard B 8B pipeline).

Guards against the regressions discovered during the 2026-04-08 session:
  1. authorized_slides stripped to minimal fields → lost Irene's narration nuances,
     stage directions, behavioral intent, emphasis, and anti-meta controls.
  2. 8B subprocess used authorized-storyboard.json as --payload instead of
     the original Gary dispatch result JSON (which has gary_slide_output).
  3. 8B subprocess used wrong CLI arg (--manifest instead of --payload).
  4. Missing Gary payload discovery logic caused FileNotFoundError.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_AUTHORIZE_SCRIPT = _SCRIPTS_DIR / "write-authorized-storyboard.py"


def _load_authorize_module():
    spec = importlib.util.spec_from_file_location("write_authorized_mod", _AUTHORIZE_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_RICH_SLIDE_FIELDS = {
    "slide_id": "m1-c1",
    "card_number": 1,
    "fidelity": "creative",
    "source_ref": "src-a",
    "file_path": "slides/s1.png",
    "dispatch_variant": "B",
    "asset_status": "present",
    "orientation": "landscape",
    "dimensions": {"width": 1920, "height": 1080},
    "aspect_ratio": "16:9",
    "narration_status": "present",
    "narration_text": "Notice how each element builds on the previous one.",
    "script_notes": "Emphasize progression — audience-directed, NOT meta.",
    "stage_directions": "Pause after 'builds on'. Let visual land.",
    "behavioral_intent": "guide_attention",
    "emphasis": "progressive_reveal",
    "visual_description": "Three callouts animate in sequence left to right.",
    "perception_cue": "visual_build",
    "motion_type": "video",
    "motion_status": "approved",
    "motion_asset_path": "motion/clip.mp4",
    "motion_source": "kling",
    "motion_duration_seconds": 5.041,
    "visual_mode": "video",
    "issue_flags": [],
    "segment_match_count": 1,
    "row_id": "slide-0001",
    "preview_kind": "image",
}

_MINIMAL_SLIDE_FIELDS = {"slide_id", "card_number", "file_path", "source_ref", "dispatch_variant"}


def _manifest_with_rich_slides(slide_overrides: list[dict] | None = None) -> dict[str, Any]:
    """Build a realistic storyboard manifest with full field coverage."""
    slides = slide_overrides or [
        {**_RICH_SLIDE_FIELDS},
        {
            **_RICH_SLIDE_FIELDS,
            "slide_id": "m1-c2",
            "card_number": 2,
            "narration_text": "Here the instructor walks you through the key takeaway.",
            "stage_directions": "Lean into key takeaway — direct address.",
            "behavioral_intent": "reinforce_concept",
        },
        {
            **_RICH_SLIDE_FIELDS,
            "slide_id": "m1-c3",
            "card_number": 3,
            "narration_text": "Let's look at how this applies in practice.",
            "stage_directions": "Transition to applied example.",
            "behavioral_intent": "bridge_to_example",
        },
    ]
    return {"slides": slides}


def _write_manifest(path: Path, manifest: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def _gary_dispatch_result(slide_count: int = 3) -> dict:
    """Minimal Gary dispatch result with gary_slide_output."""
    return {
        "gary_slide_output": [
            {
                "slide_id": f"m1-c{i}",
                "fidelity": "creative",
                "card_number": i,
                "source_ref": f"src-{chr(96 + i)}",
                "file_path": f"slides/s{i}.png",
            }
            for i in range(1, slide_count + 1)
        ]
    }


# ---------------------------------------------------------------------------
# REGRESSION 1: authorized_slides must contain FULL manifest items
# ---------------------------------------------------------------------------


class TestAuthorizedSlidesPreserveFullContext:
    """The meta-commentary regression was caused by stripping authorized_slides
    to only {slide_id, card_number, file_path, source_ref, dispatch_variant}.
    This lost narration nuances, stage directions, behavioral intent, emphasis,
    and anti-meta controls that Irene had carefully embedded."""

    def test_authorized_slides_are_not_stripped_to_minimal(self, tmp_path: Path) -> None:
        """CRITICAL: authorized_slides must pass through full manifest items."""
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        proc = subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "REGRESSION-FULL-SLIDES",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, proc.stderr
        data = json.loads(out.read_text(encoding="utf-8"))
        authorized = data["authorized_slides"]

        assert len(authorized) == 3
        for slide in authorized:
            # These fields were lost in the regression — now they MUST be present
            assert "narration_text" in slide, f"narration_text missing from {slide['slide_id']}"
            assert "stage_directions" in slide, f"stage_directions missing from {slide['slide_id']}"
            assert "behavioral_intent" in slide, f"behavioral_intent missing from {slide['slide_id']}"
            assert "emphasis" in slide, f"emphasis missing from {slide['slide_id']}"
            assert "script_notes" in slide, f"script_notes missing from {slide['slide_id']}"
            assert "perception_cue" in slide, f"perception_cue missing from {slide['slide_id']}"
            assert "visual_description" in slide, f"visual_description missing from {slide['slide_id']}"

    def test_slide_narration_text_survives_authorization(self, tmp_path: Path) -> None:
        """Exact narration text must round-trip through authorization."""
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "REGRESSION-NARRATION",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        by_id = {s["slide_id"]: s for s in data["authorized_slides"]}

        assert by_id["m1-c1"]["narration_text"] == "Notice how each element builds on the previous one."
        assert by_id["m1-c2"]["narration_text"] == "Here the instructor walks you through the key takeaway."
        assert by_id["m1-c3"]["narration_text"] == "Let's look at how this applies in practice."

    def test_motion_metadata_survives_authorization(self, tmp_path: Path) -> None:
        """Motion Gate-approved bindings must not be lost."""
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "REGRESSION-MOTION",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        slide = data["authorized_slides"][0]
        assert slide["motion_type"] == "video"
        assert slide["motion_status"] == "approved"
        assert slide["motion_asset_path"] == "motion/clip.mp4"
        assert slide["motion_source"] == "kling"
        assert slide["motion_duration_seconds"] == 5.041

    def test_authorized_slide_field_count_exceeds_minimal(self, tmp_path: Path) -> None:
        """Guard: each authorized slide must have significantly more fields
        than the old stripped set of 5."""
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "REGRESSION-FIELD-COUNT",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        for slide in data["authorized_slides"]:
            field_count = len(slide.keys())
            assert field_count > len(_MINIMAL_SLIDE_FIELDS), (
                f"Slide {slide.get('slide_id')} has only {field_count} fields — "
                f"looks like the old stripped-down regression. Expected >> {len(_MINIMAL_SLIDE_FIELDS)}"
            )


# ---------------------------------------------------------------------------
# REGRESSION 2: authorized_storyboard_version must be 2
# ---------------------------------------------------------------------------


class TestAuthorizedStoryboardVersion:
    """Version 2 signals full 8B context support. Downgrading to v1 means
    stripped slides and broken downstream hydration."""

    def test_version_is_2(self, tmp_path: Path) -> None:
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "V2-CHECK",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["authorized_storyboard_version"] == 2


# ---------------------------------------------------------------------------
# REGRESSION 3: script_context_path + motion_plan_path recorded
# ---------------------------------------------------------------------------


class TestContextPathsRecorded:

    def test_script_context_and_motion_plan_paths_in_output(self, tmp_path: Path) -> None:
        """Both context paths must be captured for downstream traceability."""
        manifest = _manifest_with_rich_slides()
        storyboard_dir = tmp_path / "storyboard"
        manifest_path = _write_manifest(storyboard_dir / "storyboard.json", manifest)

        # Create dummy context files
        script_ctx = tmp_path / "narration-script.md"
        script_ctx.write_text("# Narration Script\n", encoding="utf-8")
        motion_plan = tmp_path / "motion_plan.yaml"
        motion_plan.write_text("motion: []\n", encoding="utf-8")

        # Also need a discoverable Gary payload for the 8B subprocess to find
        gary_payload = tmp_path / "gary-dispatch-result.json"
        gary_payload.write_text(json.dumps(_gary_dispatch_result()), encoding="utf-8")
        # segment-manifest.yaml needed by the generate command
        seg_manifest = tmp_path / "segment-manifest.yaml"
        seg_manifest.write_text("segments: []\n", encoding="utf-8")

        out = tmp_path / "authorized-storyboard.json"

        mod = _load_authorize_module()
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
            sys_argv = [
                str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "CTX-PATHS",
                "--output", str(out),
                "--script-context", str(script_ctx),
                "--motion-plan", str(motion_plan),
            ]
            with patch.object(sys, "argv", sys_argv):
                rc = mod.main()

        assert rc == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["script_context_path"] is not None
        assert "narration-script.md" in data["script_context_path"]
        assert data["motion_plan_path"] is not None
        assert "motion_plan.yaml" in data["motion_plan_path"]

    def test_paths_null_when_no_context_flags(self, tmp_path: Path) -> None:
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "NO-CTX",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["script_context_path"] is None
        assert data["motion_plan_path"] is None


# ---------------------------------------------------------------------------
# REGRESSION 4+5: Gary payload discovery (source_payload → fallback)
# ---------------------------------------------------------------------------


class TestGaryPayloadDiscovery:
    """The 8B subprocess must use the original Gary dispatch result JSON
    (containing gary_slide_output), NOT the authorized-storyboard.json."""

    def _setup_bundle(self, tmp_path: Path) -> dict:
        """Build a realistic bundle with storyboard, manifest, and context files."""
        bundle = tmp_path / "bundle"
        storyboard_dir = bundle / "storyboard"
        storyboard_dir.mkdir(parents=True)

        gary_payload = bundle / "gary-dispatch-result.json"
        gary_payload.write_text(json.dumps(_gary_dispatch_result()), encoding="utf-8")

        # Manifest referencing the gary payload via source_payload
        manifest_data = _manifest_with_rich_slides()
        manifest_data["source_payload"] = str(gary_payload.resolve())
        _write_manifest(storyboard_dir / "storyboard.json", manifest_data)

        script_ctx = bundle / "narration-script.md"
        script_ctx.write_text("# Script\n", encoding="utf-8")
        motion_plan = bundle / "motion_plan.yaml"
        motion_plan.write_text("motion: []\n", encoding="utf-8")
        seg_manifest = bundle / "segment-manifest.yaml"
        seg_manifest.write_text("segments: []\n", encoding="utf-8")

        return {
            "bundle": bundle,
            "gary_payload": gary_payload,
            "manifest_path": storyboard_dir / "storyboard.json",
            "script_ctx": script_ctx,
            "motion_plan": motion_plan,
            "out": bundle / "authorized-storyboard.json",
        }

    def test_discovers_gary_payload_from_source_payload_field(self, tmp_path: Path) -> None:
        """Primary path: reads source_payload from existing storyboard.json."""
        ctx = self._setup_bundle(tmp_path)
        mod = _load_authorize_module()

        # Patch subprocess.run inside the module to capture the generate command
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
            # Simulate calling main() with args
            sys_argv = [
                str(_AUTHORIZE_SCRIPT),
                "--manifest", str(ctx["manifest_path"]),
                "--run-id", "GARY-DISCOVER",
                "--output", str(ctx["out"]),
                "--script-context", str(ctx["script_ctx"]),
                "--motion-plan", str(ctx["motion_plan"]),
            ]
            with patch.object(sys, "argv", sys_argv):
                rc = mod.main()

        assert rc == 0
        # The first subprocess.run call should be the generate command
        generate_call = mock_run.call_args_list[0]
        cmd_args = generate_call[0][0]
        # Must use --payload with the Gary dispatch result, NOT the authorized JSON
        payload_idx = cmd_args.index("--payload")
        payload_path = cmd_args[payload_idx + 1]
        assert "gary-dispatch-result.json" in payload_path or "dispatch" in payload_path
        assert "authorized-storyboard" not in payload_path, (
            "REGRESSION: 8B subprocess must NOT use authorized-storyboard.json as --payload"
        )

    def test_falls_back_to_gary_dispatch_result_json(self, tmp_path: Path) -> None:
        """Fallback: when storyboard.json has no source_payload, find gary-dispatch-result.json in bundle."""
        ctx = self._setup_bundle(tmp_path)

        # Remove source_payload from storyboard.json so primary discovery fails
        storyboard_data = json.loads(ctx["manifest_path"].read_text(encoding="utf-8"))
        del storyboard_data["source_payload"]
        ctx["manifest_path"].write_text(json.dumps(storyboard_data), encoding="utf-8")

        mod = _load_authorize_module()
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
            sys_argv = [
                str(_AUTHORIZE_SCRIPT),
                "--manifest", str(ctx["manifest_path"]),
                "--run-id", "GARY-FALLBACK",
                "--output", str(ctx["out"]),
                "--script-context", str(ctx["script_ctx"]),
                "--motion-plan", str(ctx["motion_plan"]),
            ]
            with patch.object(sys, "argv", sys_argv):
                rc = mod.main()

        assert rc == 0
        generate_call = mock_run.call_args_list[0]
        cmd_args = generate_call[0][0]
        payload_idx = cmd_args.index("--payload")
        assert "gary-dispatch-result.json" in cmd_args[payload_idx + 1]

    def test_errors_when_no_gary_payload_available(self, tmp_path: Path) -> None:
        """Must fail clearly when no Gary payload can be found."""
        ctx = self._setup_bundle(tmp_path)

        # Remove source_payload AND the fallback file
        storyboard_data = json.loads(ctx["manifest_path"].read_text(encoding="utf-8"))
        del storyboard_data["source_payload"]
        ctx["manifest_path"].write_text(json.dumps(storyboard_data), encoding="utf-8")
        ctx["gary_payload"].unlink()

        mod = _load_authorize_module()
        sys_argv = [
            str(_AUTHORIZE_SCRIPT),
            "--manifest", str(ctx["manifest_path"]),
            "--run-id", "NO-GARY",
            "--output", str(ctx["out"]),
            "--script-context", str(ctx["script_ctx"]),
            "--motion-plan", str(ctx["motion_plan"]),
        ]
        with patch.object(sys, "argv", sys_argv):
            rc = mod.main()

        assert rc == 2, "Must return error code 2 when no Gary payload is found"


# ---------------------------------------------------------------------------
# REGRESSION 6: 8B subprocess command structure
# ---------------------------------------------------------------------------


class TestEightBSubprocessCommands:
    """Verify the generate + publish subprocess chain uses correct arguments."""

    def _setup_and_run(self, tmp_path: Path) -> list:
        """Set up bundle and capture subprocess calls."""
        bundle = tmp_path / "bundle"
        storyboard_dir = bundle / "storyboard"
        storyboard_dir.mkdir(parents=True)

        gary_payload = bundle / "gary-dispatch-result.json"
        gary_payload.write_text(json.dumps(_gary_dispatch_result()), encoding="utf-8")

        manifest_data = _manifest_with_rich_slides()
        manifest_data["source_payload"] = str(gary_payload.resolve())
        _write_manifest(storyboard_dir / "storyboard.json", manifest_data)

        script_ctx = bundle / "narration-script.md"
        script_ctx.write_text("# Script\n", encoding="utf-8")
        motion_plan = bundle / "motion_plan.yaml"
        motion_plan.write_text("motion: []\n", encoding="utf-8")
        seg_manifest = bundle / "segment-manifest.yaml"
        seg_manifest.write_text("segments: []\n", encoding="utf-8")
        out = bundle / "authorized-storyboard.json"

        mod = _load_authorize_module()
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
            sys_argv = [
                str(_AUTHORIZE_SCRIPT),
                "--manifest", str(storyboard_dir / "storyboard.json"),
                "--run-id", "CMD-CHECK",
                "--output", str(out),
                "--script-context", str(script_ctx),
                "--motion-plan", str(motion_plan),
            ]
            with patch.object(sys, "argv", sys_argv):
                rc = mod.main()

        assert rc == 0
        return mock_run.call_args_list

    def test_generate_command_uses_payload_not_manifest(self, tmp_path: Path) -> None:
        """REGRESSION: must use --payload for generate, not --manifest."""
        calls = self._setup_and_run(tmp_path)
        generate_cmd = calls[0][0][0]
        assert "--payload" in generate_cmd, "generate command must use --payload"
        assert "generate" in generate_cmd, "first subprocess must be 'generate' subcommand"

    def test_generate_command_includes_segment_manifest(self, tmp_path: Path) -> None:
        """Must pass --segment-manifest for full Irene narration hydration."""
        calls = self._setup_and_run(tmp_path)
        generate_cmd = calls[0][0][0]
        assert "--segment-manifest" in generate_cmd

    def test_generate_command_includes_run_id(self, tmp_path: Path) -> None:
        calls = self._setup_and_run(tmp_path)
        generate_cmd = calls[0][0][0]
        assert "--run-id" in generate_cmd
        run_id_idx = generate_cmd.index("--run-id")
        assert generate_cmd[run_id_idx + 1] == "CMD-CHECK"

    def test_publish_command_is_second_subprocess(self, tmp_path: Path) -> None:
        """Must chain publish after generate."""
        calls = self._setup_and_run(tmp_path)
        assert len(calls) == 2, f"Expected exactly 2 subprocess calls (generate + publish), got {len(calls)}"
        publish_cmd = calls[1][0][0]
        assert "publish" in publish_cmd

    def test_publish_command_uses_storyboard_manifest(self, tmp_path: Path) -> None:
        """Publish must reference storyboard/storyboard.json, not authorized JSON."""
        calls = self._setup_and_run(tmp_path)
        publish_cmd = calls[1][0][0]
        assert "--manifest" in publish_cmd
        manifest_idx = publish_cmd.index("--manifest")
        assert "storyboard.json" in publish_cmd[manifest_idx + 1]
        assert "authorized" not in publish_cmd[manifest_idx + 1]


# ---------------------------------------------------------------------------
# REGRESSION 7: Overwrite protection + 8B override
# ---------------------------------------------------------------------------


class TestOverwriteProtection:

    def test_refuses_overwrite_without_8b_flags(self, tmp_path: Path) -> None:
        """Basic mode: must refuse to overwrite existing authorized output."""
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "authorized-storyboard.json"

        # First write
        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "OVERWRITE-1",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        assert out.exists()

        # Second write should be refused
        r2 = subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "OVERWRITE-2",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=False,
        )
        assert r2.returncode == 1
        assert "refusing to overwrite" in (r2.stderr or "").lower()

    def test_allows_overwrite_in_8b_mode(self, tmp_path: Path) -> None:
        """When both --script-context and --motion-plan are provided, overwrite is allowed
        (8B regeneration mode rewrites the authorized snapshot)."""
        bundle = tmp_path / "bundle"
        storyboard_dir = bundle / "storyboard"
        storyboard_dir.mkdir(parents=True)

        gary_payload = bundle / "gary-dispatch-result.json"
        gary_payload.write_text(json.dumps(_gary_dispatch_result()), encoding="utf-8")

        manifest_data = _manifest_with_rich_slides()
        manifest_data["source_payload"] = str(gary_payload.resolve())
        manifest_path = _write_manifest(storyboard_dir / "storyboard.json", manifest_data)

        script_ctx = bundle / "narration-script.md"
        script_ctx.write_text("# Script\n", encoding="utf-8")
        motion_plan = bundle / "motion_plan.yaml"
        motion_plan.write_text("motion: []\n", encoding="utf-8")
        seg_manifest = bundle / "segment-manifest.yaml"
        seg_manifest.write_text("segments: []\n", encoding="utf-8")
        out = bundle / "authorized-storyboard.json"

        # First write (basic mode)
        subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "8B-OVERWRITE-1",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=True,
        )
        assert out.exists()
        first_data = json.loads(out.read_text(encoding="utf-8"))

        # Second write in 8B mode should succeed (with subprocess mocked)
        mod = _load_authorize_module()
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
            sys_argv = [
                str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "8B-OVERWRITE-2",
                "--output", str(out),
                "--script-context", str(script_ctx),
                "--motion-plan", str(motion_plan),
            ]
            with patch.object(sys, "argv", sys_argv):
                rc = mod.main()

        assert rc == 0
        second_data = json.loads(out.read_text(encoding="utf-8"))
        assert second_data["run_id"] == "8B-OVERWRITE-2"
        assert second_data["run_id"] != first_data["run_id"]


# ---------------------------------------------------------------------------
# Unit tests for _ordered_authorized_slides (no subprocess)
# ---------------------------------------------------------------------------


class TestOrderedAuthorizedSlidesPreservesFields:
    """Direct unit tests on the function that selects authorized slides."""

    def test_non_dispatch_slides_pass_through_complete(self) -> None:
        """Plain slides (no double-dispatch) must pass through with ALL fields."""
        mod = _load_authorize_module()
        manifest = _manifest_with_rich_slides()
        # Remove dispatch_variant to simulate non-double-dispatch slides
        for slide in manifest["slides"]:
            slide.pop("dispatch_variant", None)

        result = mod._ordered_authorized_slides(manifest)
        assert len(result) == 3
        for slide in result:
            assert set(slide.keys()) == set(_RICH_SLIDE_FIELDS.keys()) - {"dispatch_variant"}
            assert "narration_text" in slide
            assert "stage_directions" in slide
            assert "behavioral_intent" in slide
            assert "emphasis" in slide

    def test_double_dispatch_winner_preserves_all_fields(self) -> None:
        """When double-dispatch selects a winner, the full slide dict must be kept."""
        mod = _load_authorize_module()
        slide_a = {**_RICH_SLIDE_FIELDS, "dispatch_variant": "A", "narration_text": "Variant A narration."}
        slide_b = {**_RICH_SLIDE_FIELDS, "dispatch_variant": "B", "narration_text": "Variant B narration."}
        manifest = {
            "slides": [slide_a, slide_b],
            "double_dispatch": {
                "variant_pairs": [
                    {
                        "card_number": 1,
                        "slide_id": "m1-c1",
                        "selected_variant": "B",
                        "variants": {"A": slide_a, "B": slide_b},
                    }
                ]
            },
        }

        result = mod._ordered_authorized_slides(manifest)
        assert len(result) == 1
        winner = result[0]
        assert winner["dispatch_variant"] == "B"
        assert winner["narration_text"] == "Variant B narration."
        assert "stage_directions" in winner
        assert "behavioral_intent" in winner
        assert "emphasis" in winner


# ---------------------------------------------------------------------------
# Validation: input error handling
# ---------------------------------------------------------------------------


class TestInputValidation:

    def test_missing_manifest_returns_error(self, tmp_path: Path) -> None:
        out = tmp_path / "out.json"
        proc = subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(tmp_path / "nonexistent.json"),
                "--run-id", "ERR-1",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 2
        assert "manifest not found" in proc.stderr.lower()

    def test_missing_script_context_returns_error(self, tmp_path: Path) -> None:
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "out.json"
        proc = subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "ERR-2",
                "--output", str(out),
                "--script-context", str(tmp_path / "missing.md"),
            ],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 2
        assert "script-context not found" in proc.stderr.lower()

    def test_missing_motion_plan_returns_error(self, tmp_path: Path) -> None:
        manifest = _manifest_with_rich_slides()
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", manifest)
        out = tmp_path / "out.json"
        proc = subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "ERR-3",
                "--output", str(out),
                "--motion-plan", str(tmp_path / "missing.yaml"),
            ],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 2
        assert "motion-plan not found" in proc.stderr.lower()

    def test_empty_slides_returns_error(self, tmp_path: Path) -> None:
        manifest_path = _write_manifest(tmp_path / "storyboard" / "storyboard.json", {"slides": []})
        out = tmp_path / "out.json"
        proc = subprocess.run(
            [
                sys.executable, str(_AUTHORIZE_SCRIPT),
                "--manifest", str(manifest_path),
                "--run-id", "ERR-4",
                "--output", str(out),
            ],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 2
        assert "no authorized slide_id" in proc.stderr.lower()
