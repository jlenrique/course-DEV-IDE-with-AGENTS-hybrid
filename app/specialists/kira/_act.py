"""Kira Class-C Kling API act implementation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.kira.kling_dispatch import dispatch_to_kling
from scripts.api_clients.kling_client import KlingClient

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-kira"
CONFIG_PATH = REPO_ROOT / "app" / "specialists" / "kira" / "config.yaml"
DEFAULT_BUNDLE_PATH = REPO_ROOT / "runs" / "kira-motion"


class KiraActError(RuntimeError):
    """Raised when Kira cannot produce a valid motion-generation envelope."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise KiraActError("kira envelope cache_prefix is not JSON", tag="kling.malformed") from exc
    if not isinstance(decoded, dict):
        raise KiraActError(
            "kira envelope cache_prefix must decode to an object",
            tag="kling.wrong-type",
        )
    return decoded


def _load_budget(config_path: Path = CONFIG_PATH) -> dict[str, float]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    return {
        "daily_budget_usd": float(data.get("daily_budget_usd", 0.0)),
        "per_invocation_cap_usd": float(data.get("per_invocation_cap_usd", 0.0)),
    }


def _load_motion_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("motion_plan"), dict):
        return dict(payload["motion_plan"])
    plan_path = payload.get("motion_plan_path")
    if plan_path:
        data = yaml.safe_load(Path(str(plan_path)).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    return {"slides": payload.get("slides") or []}


def _slides_from_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    raw = plan.get("slides") or plan.get("motion_segments") or []
    if isinstance(raw, dict):
        raw = raw.get("items") or []
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise KiraActError("motion_plan slides must be a list of objects", tag="kling.plan.invalid")
    return raw


def _slide_id(slide: dict[str, Any], index: int) -> str:
    return str(slide.get("slide_id") or slide.get("id") or f"slide-{index:02d}")


def _prompt_for(slide: dict[str, Any]) -> str:
    prompt = slide.get("kling_prompt") or slide.get("motion_prompt") or slide.get("prompt")
    if prompt:
        return str(prompt)
    return "Create concise instructional motion from the approved still image."


def _estimate_cost(slide: dict[str, Any]) -> float:
    raw = slide.get("estimated_cost_usd", slide.get("cost_usd", 0.0))
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _video_url(provider_response: dict[str, Any]) -> str:
    data = provider_response.get("data")
    if isinstance(data, dict):
        task_result = data.get("task_result")
        if isinstance(task_result, dict):
            videos = task_result.get("videos")
            if isinstance(videos, list) and videos and isinstance(videos[0], dict):
                return str(videos[0].get("url") or "")
    return str(
        provider_response.get("video_url")
        or provider_response.get("motion_asset_path")
        or ""
    )


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dumps(data) + "\n", encoding="utf-8", newline="\n")


def _inspection_note(bundle_path: Path, slide_id: str, name: str, body: str) -> Path:
    target = bundle_path / "recovery" / "inspection" / slide_id / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8", newline="\n")
    return target


def _call_generate_motion(
    client: KlingClient, slide: dict[str, Any], *, prompt: str
) -> dict[str, Any]:
    generate_motion = getattr(client, "generate_motion", None)
    kwargs = {
        "prompt": prompt,
        "model_name": str(slide.get("model_name") or "kling-v2-6"),
        "duration": str(slide.get("duration") or "5"),
        "aspect_ratio": str(slide.get("aspect_ratio") or "16:9"),
        "mode": str(slide.get("mode") or "std"),
        "negative_prompt": slide.get("negative_prompt"),
        "sound": bool(slide.get("sound", False)),
    }
    image_url = slide.get("image_url") or slide.get("visual_file")
    if callable(generate_motion):
        return generate_motion(image_url=image_url, **kwargs)
    if image_url:
        return client.image_to_video(str(image_url), **kwargs)
    return client.text_to_video(**kwargs)


def generate_motion_from_plan(
    payload: dict[str, Any], *, client: KlingClient | None = None
) -> dict[str, Any]:
    client = client or KlingClient()
    bundle_path = Path(str(payload.get("bundle_path") or DEFAULT_BUNDLE_PATH))
    motion_dir = bundle_path / "motion"
    budget = _load_budget()
    plan = _load_motion_plan(payload)
    slides = _slides_from_plan(plan)
    cumulative_cost = 0.0
    receipts: list[dict[str, Any]] = []
    for index, slide in enumerate(slides, start=1):
        sid = _slide_id(slide, index)
        estimated_cost = _estimate_cost(slide)
        if (
            budget["per_invocation_cap_usd"] and estimated_cost > budget["per_invocation_cap_usd"]
        ) or (
            budget["daily_budget_usd"]
            and cumulative_cost + estimated_cost > budget["daily_budget_usd"]
        ):
            receipt = {
                "slide_id": sid,
                "status": "budget-exceeded",
                "reason": "Kling motion budget exceeded before provider invocation.",
                "cost_tracking": {
                    "estimated_cost_usd": estimated_cost,
                    "cumulative_cost_usd": cumulative_cost,
                },
            }
            _write_json(motion_dir / f"{sid}.json", receipt)
            _inspection_note(
                bundle_path,
                sid,
                "budget-exhausted.md",
                "# Budget Exhausted\n\n"
                "Kira aborted before attempting subsequent slides.\n",
            )
            receipts.append(receipt)
            break
        prompt = _prompt_for(slide)
        progress = {"slide_id": sid, "status": "submitted", "prompt": prompt}
        _write_json(motion_dir / f"{sid}.progress.json", progress)
        legacy_receipt = dispatch_to_kling(
            kling_prompt=prompt,
            model_name=str(slide.get("model_name") or "kling-v2-6"),
            mode=str(slide.get("mode") or "std"),
            duration=float(slide.get("duration") or 5),
            negative_prompt=slide.get("negative_prompt"),
        )
        try:
            provider_response = _call_generate_motion(client, slide, prompt=prompt)
            final_response = provider_response
            status = "success"
        except Exception as exc:  # pragma: no cover - covered through fake failures.
            final_response = {"error": str(exc)}
            status = "failure"
        actual_cost = float(slide.get("actual_cost_usd", estimated_cost))
        cumulative_cost += actual_cost
        motion_asset_path = ""
        if status == "success":
            motion_asset_path = _video_url(final_response) or legacy_receipt[
                "motion_asset_path"
            ]
        receipt = {
            "slide_id": sid,
            "status": status,
            "motion_asset_path": motion_asset_path,
            "cost_tracking": {
                "estimated_cost_usd": estimated_cost,
                "actual_cost_usd": actual_cost,
                "cumulative_cost_usd": cumulative_cost,
            },
            "provider_response": final_response,
        }
        _write_json(motion_dir / f"{sid}.json", receipt)
        if status != "success":
            _inspection_note(
                bundle_path,
                sid,
                "failure.md",
                f"# Kling Failure\n\n{_json_dumps(final_response)}\n",
            )
        receipts.append(receipt)
    return {
        "specialist_id": "kira",
        "gate_id": "G2F",
        "motion_receipts": receipts,
        "bundle_path": str(bundle_path),
    }


def build_compositor_invocation(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [
        row["motion_asset_path"]
        for row in receipts
        if row.get("status") == "success" and row.get("motion_asset_path")
    ]
    return {"specialist_id": "compositor", "gate_id": "G3", "motion_asset_paths": paths}


def act(state: RunState, *, client: KlingClient | None = None) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("kira act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    try:
        verdict = generate_motion_from_plan(payload, client=client)
    except KiraActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    verdict["compositor_invocation"] = build_compositor_invocation(verdict["motion_receipts"])
    verdict["model_id"] = last_entry.resolved
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="kling.dispatch.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(verdict),
            entries_count=entries_count + 1,
        ).model_dump(mode="json"),
    }


__all__ = [
    "CONFIG_PATH",
    "KiraActError",
    "SANCTUM_DIR",
    "act",
    "build_compositor_invocation",
    "decode_envelope_payload",
    "generate_motion_from_plan",
]
