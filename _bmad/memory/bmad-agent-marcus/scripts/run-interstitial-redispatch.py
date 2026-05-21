# /// script
# requires-python = ">=3.10"
# ///
"""Manual CLI for Story 21-5 interstitial re-dispatch.

This command is intentionally manual and credit-gated. It does not auto-run in
the default pipeline. Operator must pass both ``--execute`` and
``--confirm-credit-spend YES`` to allow Gamma dispatch calls.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cluster_coherence_validation import validate_interstitial_replacement
from interstitial_redispatch_protocol import (
    InterstitialRedispatchError,
    execute_interstitial_redispatch,
)

MANIFEST_FILENAME = "segment-manifest.yaml"
DISPATCH_RESULT_FILENAME = "gary-dispatch-result.json"
REDISPATCH_LOG_FILENAME = "interstitial-redispatch-log.jsonl"
REDISPATCH_METADATA_FILENAME = "interstitial-redispatch-metadata.json"


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise RuntimeError("pyyaml is required")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected YAML mapping at {path}")
    return raw


def _write_yaml_atomic(path: Path, payload: dict[str, Any]) -> None:
    if yaml is None:  # pragma: no cover
        raise RuntimeError("pyyaml is required")
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=path.parent) as tmp:
        yaml.safe_dump(payload, tmp, sort_keys=False)
        temp_path = Path(tmp.name)
    temp_path.replace(path)


def _load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return raw


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=path.parent) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp.write("\n")
        temp_path = Path(tmp.name)
    temp_path.replace(path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload))
        f.write("\n")


def _prompt_from_segment(segment: dict[str, Any]) -> str:
    for key in ("redispatch_prompt", "dispatch_prompt", "gamma_prompt", "interstitial_prompt", "prompt"):
        value = str(segment.get(key) or "").strip()
        if value:
            return value
    return ""


def _build_cluster_bundle(
    *,
    manifest: dict[str, Any],
    cluster_id: str,
    interstitial_id: str,
    interstitial_prompt_override: str | None,
    theme_id: str | None,
    style_parameters: dict[str, Any],
) -> dict[str, Any]:
    segments = manifest.get("segments")
    if not isinstance(segments, list):
        raise InterstitialRedispatchError("missing_required_field", "segment-manifest.yaml must include segments[]")

    head_segment: dict[str, Any] | None = None
    interstitials: list[dict[str, Any]] = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        if str(segment.get("cluster_id")) != cluster_id:
            continue
        role = str(segment.get("cluster_role") or "").strip().lower()
        if role == "head":
            head_segment = segment
            continue
        if role == "interstitial":
            prompt = _prompt_from_segment(segment)
            if str(segment.get("slide_id")) == interstitial_id and interstitial_prompt_override:
                prompt = interstitial_prompt_override.strip()
            interstitials.append(
                {
                    "slide_id": str(segment.get("slide_id") or ""),
                    "prompt": prompt,
                    "asset_path": str(segment.get("file_path") or segment.get("visual_file") or ""),
                    "re_dispatch_count": int(segment.get("re_dispatch_count", 0) or 0),
                }
            )

    if head_segment is None:
        raise InterstitialRedispatchError("missing_required_field", f"head segment missing for cluster: {cluster_id}")

    target = next((row for row in interstitials if row["slide_id"] == interstitial_id), None)
    if target is None:
        raise InterstitialRedispatchError(
            "missing_required_field",
            f"interstitial not found in cluster {cluster_id}: {interstitial_id}",
        )
    if not target["prompt"]:
        raise InterstitialRedispatchError(
            "missing_required_field",
            f"no interstitial prompt found for {interstitial_id}; pass --interstitial-prompt",
        )

    return {
        "cluster_id": cluster_id,
        "cluster_interstitial_count": int(head_segment.get("cluster_interstitial_count", len(interstitials)) or len(interstitials)),
        "head_slide": {
            "slide_id": str(head_segment.get("slide_id") or ""),
            "theme_id": theme_id or head_segment.get("theme_id"),
            "style_parameters": style_parameters or head_segment.get("style_parameters") or {},
            "text": str(head_segment.get("summary") or head_segment.get("head_claim") or ""),
        },
        "interstitials": interstitials,
    }


def _default_dispatch_adapter(payload: dict[str, Any], *, bundle_dir: Path, run_label: str) -> dict[str, Any]:
    gamma_module = importlib.import_module("gamma_operations")
    export_dir = bundle_dir / "redispatch-exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    style_parameters = payload.get("style_parameters") or {}
    style_line = ""
    if isinstance(style_parameters, dict) and style_parameters:
        style_line = " Style parameters: " + ", ".join(f"{k}={v}" for k, v in style_parameters.items())

    params: dict[str, Any] = {
        "input_text": str(payload.get("prompt") or "") + style_line,
        "text_mode": "generate",
        "num_cards": 1,
        "card_split": "auto",
        "export_as": "png",
        "export_dir": str(export_dir),
    }
    if payload.get("theme_id"):
        params["theme_id"] = payload["theme_id"]

    generation = gamma_module.generate_slide(params, run_id=run_label)
    export_url = str(generation.get("exportUrl") or "").strip()
    if not export_url:
        raise InterstitialRedispatchError(
            "invalid_output_format",
            "Gamma generation missing exportUrl; cannot materialize replacement PNG",
        )
    downloaded = gamma_module.download_export(
        export_url,
        output_dir=export_dir,
        filename=f"{run_label}.png",
        run_id=run_label,
    )
    resolved_paths = gamma_module._materialize_exported_slide_paths(  # type: ignore[attr-defined]
        downloaded,
        requested_format="png",
        expected_card_numbers=[1],
        module_lesson_part=run_label,
        export_dir=export_dir,
        label="interstitial-redispatch",
    )
    if not resolved_paths:
        raise InterstitialRedispatchError(
            "invalid_output_format",
            "No PNG path resolved for interstitial re-dispatch",
        )
    return {
        "session_id": generation.get("generationId") or generation.get("id") or run_label,
        "png_path": resolved_paths[0],
        "replacement_output": {
            "slide_id": payload.get("slide_id"),
            "text": payload.get("prompt", ""),
        },
    }


def _persist_updates(
    *,
    bundle_dir: Path,
    manifest: dict[str, Any],
    cluster_id: str,
    interstitial_id: str,
    redispatch_result: dict[str, Any],
) -> None:
    updated_bundle = redispatch_result["bundle"]
    updated_interstitials = {
        str(row.get("slide_id")): row
        for row in updated_bundle.get("interstitials", [])
        if isinstance(row, dict) and row.get("slide_id")
    }
    segments = manifest.get("segments") or []
    if not isinstance(segments, list):
        raise InterstitialRedispatchError("invalid_output_format", "segment-manifest.yaml segments[] must be list")

    dropped_ids: set[str] = set()
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        if str(segment.get("cluster_id")) != cluster_id:
            continue
        if str(segment.get("cluster_role") or "").strip().lower() != "interstitial":
            continue
        sid = str(segment.get("slide_id") or "")
        if sid and sid not in updated_interstitials:
            dropped_ids.add(sid)

    new_segments: list[dict[str, Any]] = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        sid = str(segment.get("slide_id") or "")
        if sid in dropped_ids and str(segment.get("cluster_id")) == cluster_id:
            continue
        if sid in updated_interstitials and str(segment.get("cluster_id")) == cluster_id:
            state = updated_interstitials[sid]
            segment["file_path"] = state.get("asset_path", segment.get("file_path"))
            segment["re_dispatch_count"] = int(state.get("re_dispatch_count", 0) or 0)
            if state.get("last_re_dispatch_session_id"):
                segment["last_re_dispatch_session_id"] = state["last_re_dispatch_session_id"]
            if state.get("fallback_decision"):
                segment["fallback_decision"] = state["fallback_decision"]
        if str(segment.get("cluster_id")) == cluster_id and str(segment.get("cluster_role") or "").strip().lower() == "head":
            segment["cluster_interstitial_count"] = int(updated_bundle.get("cluster_interstitial_count", 0) or 0)
        new_segments.append(segment)

    manifest["segments"] = new_segments
    _write_yaml_atomic(bundle_dir / MANIFEST_FILENAME, manifest)

    dispatch_path = bundle_dir / DISPATCH_RESULT_FILENAME
    if dispatch_path.is_file():
        dispatch_payload = _load_json(dispatch_path)
        rows = dispatch_payload.get("gary_slide_output")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                if str(row.get("slide_id") or "") == interstitial_id:
                    if interstitial_id in updated_interstitials:
                        state = updated_interstitials[interstitial_id]
                        row["file_path"] = state.get("asset_path", row.get("file_path"))
                        row["re_dispatch_count"] = int(state.get("re_dispatch_count", 0) or 0)
                        if state.get("last_re_dispatch_session_id"):
                            row["last_re_dispatch_session_id"] = state["last_re_dispatch_session_id"]
                    else:
                        row["dropped_from_cluster"] = True
        _write_json_atomic(dispatch_path, dispatch_payload)

    metadata_path = bundle_dir / REDISPATCH_METADATA_FILENAME
    metadata = _load_json(metadata_path) if metadata_path.is_file() else {}
    events = metadata.get("interstitial_events")
    if not isinstance(events, dict):
        events = {}
    events[interstitial_id] = {
        "status": redispatch_result.get("status"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "validation": redispatch_result.get("validation"),
    }
    metadata["interstitial_events"] = events
    _write_json_atomic(metadata_path, metadata)


def run_command(
    args: argparse.Namespace,
    *,
    dispatch_single_interstitial: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    validate_replacement: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
) -> tuple[int, dict[str, Any]]:
    bundle_dir = Path(args.bundle_dir).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else (bundle_dir / MANIFEST_FILENAME)
    coherence_report_path = Path(args.coherence_report).resolve()
    if not manifest_path.is_file():
        return 1, {"status": "fail", "code": "missing_required_field", "message": f"manifest not found: {manifest_path}"}
    if not coherence_report_path.is_file():
        return 1, {"status": "fail", "code": "missing_required_field", "message": f"coherence report not found: {coherence_report_path}"}

    if args.execute and args.confirm_credit_spend != "YES":
        return 1, {
            "status": "fail",
            "code": "credit_confirmation_required",
            "message": "Live dispatch requires --execute and --confirm-credit-spend YES",
        }

    manifest = _load_yaml(manifest_path)
    coherence_report = _load_json(coherence_report_path)
    style_parameters: dict[str, Any] = {}
    if args.style_parameters_json:
        style_parameters = json.loads(args.style_parameters_json)
        if not isinstance(style_parameters, dict):
            return 1, {"status": "fail", "code": "invalid_style_parameters", "message": "--style-parameters-json must decode to an object"}

    cluster_bundle = _build_cluster_bundle(
        manifest=manifest,
        cluster_id=args.cluster_id,
        interstitial_id=args.interstitial_id,
        interstitial_prompt_override=args.interstitial_prompt,
        theme_id=args.theme_id,
        style_parameters=style_parameters,
    )
    target = next(
        row for row in cluster_bundle["interstitials"] if row["slide_id"] == args.interstitial_id
    )
    attempt_before = int(target.get("re_dispatch_count", 0) or 0)
    if not args.execute:
        preview = {
            "status": "preview_only",
            "cluster_id": args.cluster_id,
            "interstitial_id": args.interstitial_id,
            "attempt_before": attempt_before,
            "attempt_after": attempt_before,
            "credits_consumed": False,
            "next_action": "run with --execute --confirm-credit-spend YES",
        }
        return 0, preview

    run_label = f"{args.cluster_id}-{args.interstitial_id}-rd{attempt_before + 1}"

    def _dispatch(payload: dict[str, Any]) -> dict[str, Any]:
        if dispatch_single_interstitial is not None:
            return dispatch_single_interstitial(payload)
        return _default_dispatch_adapter(payload, bundle_dir=bundle_dir, run_label=run_label)

    def _validate(head_output: dict[str, Any], replacement_output: dict[str, Any]) -> dict[str, Any]:
        if validate_replacement is not None:
            return validate_replacement(head_output, replacement_output)
        return validate_interstitial_replacement(
            head_output=head_output,
            replacement_output=replacement_output,
            constraints=coherence_report.get("replacement_constraints"),
            seed=args.seed,
        )

    try:
        redispatch_result = execute_interstitial_redispatch(
            cluster_bundle=cluster_bundle,
            interstitial_id=args.interstitial_id,
            coherence_report=coherence_report,
            dispatch_single_interstitial=_dispatch,
            validate_replacement=_validate,
            fallback=args.fallback,
        )
    except InterstitialRedispatchError as exc:
        return 1, {"status": "fail", "code": exc.code, "message": str(exc)}

    _persist_updates(
        bundle_dir=bundle_dir,
        manifest=manifest,
        cluster_id=args.cluster_id,
        interstitial_id=args.interstitial_id,
        redispatch_result=redispatch_result,
    )

    validation = redispatch_result.get("validation") or {}
    updated_bundle = redispatch_result.get("bundle") or {}
    after_rows = updated_bundle.get("interstitials") or []
    after_target = next((row for row in after_rows if row.get("slide_id") == args.interstitial_id), None)
    attempt_after = int((after_target or {}).get("re_dispatch_count", attempt_before) or attempt_before)
    output = {
        "status": redispatch_result.get("status"),
        "cluster_id": args.cluster_id,
        "interstitial_id": args.interstitial_id,
        "attempt_before": attempt_before,
        "attempt_after": attempt_after,
        "credits_consumed": True,
        "dispatch": {
            "session_id": (after_target or {}).get("last_re_dispatch_session_id"),
            "png_path": (after_target or {}).get("asset_path"),
        },
        "validation": {
            "decision": validation.get("decision"),
            "score": validation.get("score"),
            "violations": validation.get("violations"),
            "report_hash": validation.get("report_hash"),
        },
        "fallback_applied": (after_target or {}).get("fallback_decision"),
        "next_action": (
            "proceed"
            if redispatch_result.get("status") == "pass"
            else "retry_interstitial"
            if redispatch_result.get("status") == "retry_available"
            else "choose_fallback"
        ),
    }
    log_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **output,
    }
    _append_jsonl(bundle_dir / REDISPATCH_LOG_FILENAME, log_event)
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), output)
    return (0 if output["status"] in {"pass", "preview_only"} else 1), output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manual interstitial re-dispatch (Story 21-5). Credit-consuming path requires explicit confirmation.",
    )
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--cluster-id", type=str, required=True)
    parser.add_argument("--interstitial-id", type=str, required=True)
    parser.add_argument("--coherence-report", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument(
        "--fallback",
        type=str,
        choices=["accept-as-is", "replace-with-pace-reset", "drop-from-cluster"],
        default="accept-as-is",
    )
    parser.add_argument("--interstitial-prompt", type=str, default=None)
    parser.add_argument("--theme-id", type=str, default=None)
    parser.add_argument("--style-parameters-json", type=str, default=None)
    parser.add_argument("--seed", type=str, default=None)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-credit-spend", type=str, default=None)
    parser.add_argument("--out", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        code, payload = run_command(args)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "code": "unexpected_error",
                    "message": f"{type(exc).__name__}: {exc}",
                },
                indent=2,
            )
        )
        return 2
    print(json.dumps(payload, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

