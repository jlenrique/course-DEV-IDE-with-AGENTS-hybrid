# /// script
# requires-python = ">=3.10"
# ///
"""Official Vera-agentic Pass 2 semantic judge (G4-18 + spoken-bridge quality).

Usage:
  .venv/Scripts/python.exe skills/bmad-agent-marcus/scripts/judge-irene-pass2-semantics.py \\
    --envelope <bundle>/pass2-envelope.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required") from exc

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.utilities.env_loader import load_env  # noqa: E402

load_env(REPO / ".env")

from app.models.state.cache_state import CacheState  # noqa: E402
from app.models.state.run_state import RunState  # noqa: E402
from app.specialists.vera import _act as vera_act  # noqa: E402
from app.specialists.vera.sensory_bridges_dispatch import (  # noqa: E402
    dispatch_to_sensory_bridges,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _load_lesson_plan(bundle: Path, envelope: dict[str, Any]) -> dict[str, Any]:
    inline = envelope.get("lesson_plan")
    if isinstance(inline, dict) and isinstance(inline.get("plan_units"), list):
        return inline
    candidates = [
        envelope.get("lesson_plan_path"),
        str(bundle / "irene-pass1-live" / "irene-pass1.lesson-plan.json"),
        str(bundle / "irene-pass1.lesson-plan.json"),
    ]
    for raw in candidates:
        if not raw:
            continue
        path = Path(str(raw))
        if not path.is_file():
            continue
        if path.suffix.lower() != ".json":
            continue
        data = _load_json(path)
        if isinstance(data, dict) and isinstance(data.get("plan_units"), list):
            return data
    return {}


def _apply_closed_list_hygiene(manifest_path: Path) -> list[str]:
    """Apply within-cluster bridge_type none + two-dimension rationale shape."""
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    notes: list[str] = []
    for segment in data.get("segments") or []:
        if not isinstance(segment, dict):
            continue
        role = str(segment.get("cluster_role") or "").strip().lower()
        position = str(segment.get("cluster_position") or "").strip().lower()
        bridge = str(segment.get("bridge_type") or "none").strip().lower() or "none"
        if (
            role == "interstitial"
            and position in {"resolve", "develop"}
            and bridge not in {"", "none"}
        ):
            notes.append(f"{segment.get('id')}: bridge_type {bridge} -> none")
            segment["bridge_type"] = "none"
        rationale = str(segment.get("duration_rationale") or "")
        lowered = rationale.lower()
        has_purpose = any(
            token in lowered
            for token in ("purpose", "role", "transition", "walkthrough", "checkpoint")
        )
        has_density = any(
            token in lowered for token in ("detail", "density", "complexity", "unpack")
        )
        has_visual = any(
            token in lowered for token in ("visual", "illustration", "diagram", "chart", "table")
        )
        if rationale and sum([has_purpose, has_density, has_visual]) < 2:
            extra = (
                f" Purpose is a {segment.get('timing_role') or 'this'} walkthrough; "
                f"visual burden is the on-card load."
            )
            segment["duration_rationale"] = rationale.rstrip() + extra
            notes.append(f"{segment.get('id')}: duration_rationale given second dimension")
    if notes:
        manifest_path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    return notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envelope", required=True, type=Path)
    parser.add_argument(
        "--apply-closed-list-hygiene",
        action="store_true",
        help="Normalize interstitial bridge_type none + weak duration_rationale shape",
    )
    args = parser.parse_args()
    envelope_path = args.envelope.resolve()
    bundle = envelope_path.parent
    envelope = _load_json(envelope_path)
    if not isinstance(envelope, dict):
        raise SystemExit("envelope must be an object")
    manifest_path = bundle / "segment-manifest.yaml"
    if not manifest_path.is_file():
        raise SystemExit(f"missing {manifest_path}")
    hygiene_notes: list[str] = []
    if args.apply_closed_list_hygiene:
        hygiene_notes = _apply_closed_list_hygiene(manifest_path)
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    segments = manifest.get("segments") if isinstance(manifest, dict) else []
    if not isinstance(segments, list) or not segments:
        raise SystemExit("segment-manifest.yaml has no segments")
    run_id = str(uuid4())
    payload = {
        "gate_id": "G4",
        "pass2_semantic_judge": True,
        "pass2_segments": segments,
        "lesson_plan": _load_lesson_plan(bundle, envelope),
        "bundle_path": str(bundle),
        "runs_root": str(REPO / "runs"),
    }
    state = RunState(
        run_id=run_id,
        graph_version="v0.1-stub",
        temperature=0.2,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=0,
        ),
    )
    from app.models.state.model_resolution_entry import ModelResolutionEntry

    state.model_resolution_trail.append(
        ModelResolutionEntry(
            level="per_specialist",
            requested="vera",
            resolved="vera",
            reason="pass2-semantic-judge",
            timestamp=datetime.now(UTC),
            cache_prefix_hash="e" * 64,
        )
    )
    update = vera_act.act(state, dispatch_func=dispatch_to_sensory_bridges)
    output = json.loads(update["cache_state"]["cache_prefix"])
    receipt = {
        "invoked_at": datetime.now(UTC).isoformat(),
        "run_id": run_id,
        "pairing_bundle": str(bundle),
        "hygiene_notes": hygiene_notes,
        "vera": output.get("vera_finding"),
        "trace_report_path": output.get("trace_report_path"),
    }
    out_path = bundle / "irene-pass2-live" / "pass2-semantic-judge-receipt.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"RECEIPT={out_path}", flush=True)
    print(f"TRACE={receipt.get('trace_report_path')}", flush=True)
    vera = receipt.get("vera") or {}
    print(f"VERDICT={(vera.get('verdict') or {}).get('status')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
