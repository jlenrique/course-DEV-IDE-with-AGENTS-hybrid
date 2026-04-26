from __future__ import annotations

import argparse
import json
from importlib import util
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "run-interstitial-redispatch.py"


def _load_module():
    spec = util.spec_from_file_location("run_interstitial_redispatch", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
run_command = mod.run_command


def _build_bundle(tmp_path: Path, *, count: int = 0) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = {
        "segments": [
            {
                "slide_id": "s-head",
                "cluster_id": "c1",
                "cluster_role": "head",
                "cluster_interstitial_count": 2,
                "theme_id": "theme-1",
            },
            {
                "slide_id": "s-int-1",
                "cluster_id": "c1",
                "cluster_role": "interstitial",
                "dispatch_prompt": "Bridge concept one.",
                "file_path": "old-int-1.png",
                "re_dispatch_count": 0,
            },
            {
                "slide_id": "s-int-2",
                "cluster_id": "c1",
                "cluster_role": "interstitial",
                "dispatch_prompt": "Bridge concept two.",
                "file_path": "old-int-2.png",
                "re_dispatch_count": count,
            },
        ]
    }
    (bundle / "segment-manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (bundle / "gary-dispatch-result.json").write_text(
        json.dumps(
            {
                "gary_slide_output": [
                    {"slide_id": "s-int-1", "file_path": "old-int-1.png"},
                    {"slide_id": "s-int-2", "file_path": "old-int-2.png"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (bundle / "coherence-report.json").write_text(
        json.dumps(
            {
                "head_perception": {
                    "palette_hex": ["#111111"],
                    "font_families": ["Inter"],
                    "background_treatment": "flat",
                }
            }
        ),
        encoding="utf-8",
    )
    return bundle


def _args(bundle: Path, *, execute: bool = False, fallback: str = "accept-as-is", confirm: str | None = None) -> argparse.Namespace:
    return argparse.Namespace(
        bundle_dir=bundle,
        cluster_id="c1",
        interstitial_id="s-int-2",
        coherence_report=bundle / "coherence-report.json",
        manifest=None,
        fallback=fallback,
        interstitial_prompt=None,
        theme_id=None,
        style_parameters_json=None,
        seed=None,
        execute=execute,
        confirm_credit_spend=confirm,
        out=None,
    )


def test_preview_mode_is_non_credit_and_no_mutation(tmp_path: Path):
    bundle = _build_bundle(tmp_path)
    code, payload = run_command(_args(bundle, execute=False))
    assert code == 0
    assert payload["status"] == "preview_only"
    updated_manifest = yaml.safe_load((bundle / "segment-manifest.yaml").read_text(encoding="utf-8"))
    target = next(s for s in updated_manifest["segments"] if s["slide_id"] == "s-int-2")
    assert target["file_path"] == "old-int-2.png"
    assert int(target["re_dispatch_count"]) == 0


def test_execute_requires_credit_confirmation(tmp_path: Path):
    bundle = _build_bundle(tmp_path)
    code, payload = run_command(_args(bundle, execute=True, confirm=None))
    assert code == 1
    assert payload["code"] == "credit_confirmation_required"


def test_execute_updates_only_target_interstitial(tmp_path: Path):
    bundle = _build_bundle(tmp_path)

    def _dispatch(_payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": "sess-77",
            "png_path": "new-int-2.png",
            "replacement_output": {"slide_id": "s-int-2", "text": "coherent replacement"},
        }

    def _validate(_head: dict[str, Any], _replacement: dict[str, Any]) -> dict[str, Any]:
        return {"decision": "pass", "score": 1.0, "violations": [], "report_hash": "hash-1"}

    code, payload = run_command(
        _args(bundle, execute=True, confirm="YES"),
        dispatch_single_interstitial=_dispatch,
        validate_replacement=_validate,
    )
    assert code == 0
    assert payload["status"] == "pass"
    updated_manifest = yaml.safe_load((bundle / "segment-manifest.yaml").read_text(encoding="utf-8"))
    interstitial_rows = {row["slide_id"]: row for row in updated_manifest["segments"] if row.get("cluster_role") == "interstitial"}
    assert interstitial_rows["s-int-1"]["file_path"] == "old-int-1.png"
    assert interstitial_rows["s-int-2"]["file_path"] == "new-int-2.png"
    assert int(interstitial_rows["s-int-2"]["re_dispatch_count"]) == 1


def test_circuit_breaker_drop_fallback_removes_target(tmp_path: Path):
    bundle = _build_bundle(tmp_path, count=2)

    code, payload = run_command(
        _args(bundle, execute=True, confirm="YES", fallback="drop-from-cluster"),
        dispatch_single_interstitial=lambda _: {},
        validate_replacement=lambda _a, _b: {},
    )
    assert code == 1
    assert payload["status"] == "circuit_breaker"
    updated_manifest = yaml.safe_load((bundle / "segment-manifest.yaml").read_text(encoding="utf-8"))
    ids = [row["slide_id"] for row in updated_manifest["segments"] if row.get("cluster_role") == "interstitial"]
    assert "s-int-2" not in ids

