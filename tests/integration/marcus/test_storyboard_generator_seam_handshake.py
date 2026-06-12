"""Real-seam handshake pins for the legacy generate-storyboard routine.

Murat MUST-FIX + Winston rider R1 (party review 2026-06-12): the publisher's
unit tests use fakes and the legacy routine's own suite lives in skills/ —
without this handshake, signature or payload drift between them surfaces
only as a mid-trial error-pause. Two legs:

1. Field handshake: every Namespace field the publisher passes is actually
   read by the corresponding cmd_* function (source-introspected).
2. Real dry-run: cmd_generate (the non-network half) runs the REAL routine
   against a schema-valid sample gary payload and emits the pack.
"""

from __future__ import annotations

import inspect
import json
import re
from argparse import Namespace
from pathlib import Path

from app.marcus.orchestrator import storyboard_publisher

MODULE = storyboard_publisher._load_generator_module()

GENERATE_FIELDS = {
    "payload",
    "out_dir",
    "asset_base",
    "print_summary",
    "strict",
    "segment_manifest",
    "related_assets",
    "run_id",
    "cluster_coherence_report",
    "pass2_envelope",
}
PUBLISH_FIELDS = {
    "manifest",
    "export_root",
    "export_name",
    "site_repo_url",
    "publish_subdir",
    "site_branch",
    "token_env_var",
}


def _args_read_by(func) -> set[str]:
    return set(re.findall(r"args\.([a-z_]+)", inspect.getsource(func)))


def test_publisher_fields_match_generator_cli_surface() -> None:
    assert _args_read_by(MODULE.cmd_generate) <= GENERATE_FIELDS, (
        "cmd_generate reads fields the publisher does not pass"
    )
    assert _args_read_by(MODULE.cmd_publish) <= PUBLISH_FIELDS, (
        "cmd_publish reads fields the publisher does not pass"
    )
    for name in ("DEFAULT_EXPORTS_DIR", "DEFAULT_PUBLISH_SUBDIR"):
        assert hasattr(MODULE, name), name


def test_real_generate_dry_run_with_segment_manifest_overlays_narration(
    tmp_path: Path,
) -> None:
    """PIN-B2 (real-seam leg, dp-v1.1): the B-variant handshake — a segment
    manifest built by the publisher's own transform feeds the REAL
    cmd_generate and the narration lands on the slide."""
    png = tmp_path / "slide-01.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    payload_path = tmp_path / "gary-dispatch-payload.json"
    payload_path.write_text(
        json.dumps(
            {
                "generation_id": "gen-handshake-b",
                "status": "complete",
                "gary_slide_output": [
                    {
                        "slide_id": "slide-01",
                        "card_number": 1,
                        "dispatch_variant": "A",
                        "file_path": str(png),
                        "generation_id": "gen-handshake-b",
                        "visual_description": "Handshake sample",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output={
            "narration_script": [
                {"id": "seg-1", "narration_text": "B-side narration text."}
            ],
            "segment_manifest_deltas": [
                {
                    "id": "seg-1",
                    "timing_role": "concept-build",
                    "visual_references": [{"perception_source": "slide-01"}],
                }
            ],
        },
    )
    out_dir = tmp_path / "pack-b"

    rc = MODULE.cmd_generate(
        Namespace(
            payload=payload_path,
            out_dir=out_dir,
            asset_base=None,
            print_summary=False,
            strict=True,
            segment_manifest=manifest_path,
            related_assets=None,
            run_id="handshake-test-b",
            cluster_coherence_report=None,
            pass2_envelope=None,
        )
    )

    assert rc == 0
    manifest = json.loads(
        (out_dir / "storyboard" / "storyboard.json").read_text(encoding="utf-8")
    )
    slide = manifest["slides"][0]
    assert slide["asset_status"] == "present"
    assert "B-side narration text." in json.dumps(slide)


def test_real_generate_dry_run_emits_pack(tmp_path: Path) -> None:
    png = tmp_path / "slide-01.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    payload_path = tmp_path / "gary-dispatch-payload.json"
    payload_path.write_text(
        json.dumps(
            {
                "generation_id": "gen-handshake",
                "status": "complete",
                "gary_slide_output": [
                    {
                        "slide_id": "slide-01",
                        "card_number": 1,
                        "dispatch_variant": "A",
                        "file_path": str(png),
                        "generation_id": "gen-handshake",
                        "visual_description": "Handshake sample",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "pack"

    rc = MODULE.cmd_generate(
        Namespace(
            payload=payload_path,
            out_dir=out_dir,
            asset_base=None,
            print_summary=False,
            strict=True,
            segment_manifest=None,
            related_assets=None,
            run_id="handshake-test",
            cluster_coherence_report=None,
            pass2_envelope=None,
        )
    )

    assert rc == 0
    assert (out_dir / "storyboard" / "storyboard.json").is_file()
    assert (out_dir / "storyboard" / "index.html").is_file()
    manifest = json.loads(
        (out_dir / "storyboard" / "storyboard.json").read_text(encoding="utf-8")
    )
    assert manifest["slides"][0]["asset_status"] == "present"
