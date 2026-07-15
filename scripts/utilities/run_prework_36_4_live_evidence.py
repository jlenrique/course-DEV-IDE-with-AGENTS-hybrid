#!/usr/bin/env python3
"""Bounded first-run-stands live evidence driver for Story 36.4.

Dry-run performs every filesystem/config/authority preflight but never constructs
provider adapters, creates an evidence pack, or consumes the one live attempt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

import yaml
from docx import Document
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from app.marcus.lesson_plan.prework_artifact import (  # noqa: E402
    WorkbookBriefRuntimeContext,
    read_workbook_brief,
    validate_course_source_root,
)
from app.marcus.lesson_plan.prework_from_run import load_part2_scene_source  # noqa: E402
from app.marcus.lesson_plan.promise_projection import resolve_promise_objectives  # noqa: E402
from app.marcus.orchestrator import workbook_wiring  # noqa: E402
from app.marcus.orchestrator.workbook_prework_writers import (  # noqa: E402
    CONFIG_PATH,
    LivePromiseTransformer,
    LiveSceneComposer,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope  # noqa: E402
from app.models.state.cache_state import CacheState  # noqa: E402
from app.models.state.component_selection import ComponentSelection  # noqa: E402
from app.models.state.model_resolution_entry import ModelResolutionEntry  # noqa: E402
from app.models.state.run_state import RunState  # noqa: E402
from app.runtime.cascade_config import PRICING_PATH, load_pricing  # noqa: E402
from app.specialists.workbook_producer._act import produce_workbook  # noqa: E402

EVIDENCE_ROOT = ROOT / "_bmad-output/implementation-artifacts/evidence"
REQUIRED_OPERATOR_SPOT_CHECKS = frozenset(
    {
        "provenance",
        "actual_payoff",
        "semantic_faithfulness",
        "scene_innocence",
        "pertinent_ability",
        "lo_fidelity",
        "half_rhyme",
        "mastery_overclaim",
        "no_spoiler",
    }
)
MAX_COMPLETION_TOKENS_PER_CALL = 4096
INPUT_TOKEN_CEILING_PER_CALL = 32768
CALL_COUNT = 2
CAUSAL_FIX_PATHS = (
    "app/marcus/lesson_plan/prework_from_run.py",
    "app/marcus/lesson_plan/prework_projection.py",
    "app/marcus/lesson_plan/scene_extraction.py",
    "app/marcus/orchestrator/workbook_prework_writers.py",
    "scripts/utilities/run_prework_36_4_live_evidence.py",
    "tests/integration/marcus/test_workbook_prework_writers_36_4.py",
    "tests/marcus/lesson_plan/test_prework_from_run_36_4.py",
    "tests/scripts/test_run_prework_36_4_live_evidence.py",
    "tests/unit/marcus/lesson_plan/test_prework_projection_36_2.py",
)


class FreshCloneManifest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    schema_version: Literal["prework-36-4-fresh-clone.v1"]
    source_label: str = Field(min_length=1)
    origin_label: str = Field(min_length=1)
    created_at: datetime
    run_json_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    ratified_los_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    segment_manifest_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    bundle_extracted_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    no_real_brief_contribution: Literal[True]
    no_workbook_brief_sidecar: Literal[True]


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def causal_fix_manifest(
    prior_verdict: Path, *, paths: tuple[str, ...] = CAUSAL_FIX_PATHS
) -> dict[str, Any]:
    files = [{"path": path, "sha256": _digest(ROOT / path)} for path in sorted(paths)]
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    prior_payload = json.loads(prior_verdict.read_text("utf-8"))
    prior_attempt = prior_payload.get("attempt_id")
    adjudication_path = (
        EVIDENCE_ROOT / f"prework-36-4-adjudication-{str(prior_attempt)[:8]}" / "adjudication.json"
    )
    second_defect = prior_attempt == "380ecd47-7491-42ab-a3d8-a68c1afbb078"
    third_defect = prior_attempt == "5ff7db47-62af-48d0-8b67-fa300c04aa4d"
    fourth_defect = prior_attempt == "b90fb3f6-8951-4dcc-abff-66036576d89f"
    manifest = {
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "cause": (
            "novel Scene terms were over-promoted from operator-review evidence to an "
            "automatic innocence failure"
            if fourth_defect
            else (
                "Q5 answer/resolution leaked into Scene authority and machine-green evidence "
                "was marked pass while operator checks remained pending"
                if third_defect
                else (
                    "faithfulness constraints absent from the Scene prompt and the driver "
                    "overaccepted a degraded golden witness"
                    if second_defect
                    else "SceneBrief provider output mixed authored status with losses and marker"
                )
            )
        ),
        "fix": (
            "exact structured-output invariants, token-derived cost accounting, and "
            "preventive recovery spend/evidence guards"
        ),
        "files": files,
        "manifest_digest": "sha256:" + hashlib.sha256(canonical).hexdigest(),
        "prior_failed_verdict": {
            "path": prior_verdict.relative_to(ROOT).as_posix(),
            "sha256": _digest(prior_verdict),
        },
    }
    if adjudication_path.is_file():
        manifest["prior_adjudication"] = {
            "path": adjudication_path.relative_to(ROOT).as_posix(),
            "sha256": _digest(adjudication_path),
        }
    return manifest


def preventive_spend_bound(max_spend_usd: float, model_id: str) -> dict[str, Any]:
    pricing = load_pricing()
    per_call = pricing.compute_cost(
        model_id,
        input_tokens=INPUT_TOKEN_CEILING_PER_CALL,
        output_tokens=MAX_COMPLETION_TOKENS_PER_CALL,
    )
    worst_case = CALL_COUNT * per_call
    if max_spend_usd < worst_case:
        raise ValueError(
            f"max spend ${max_spend_usd:.6f} is below preventive two-call bound ${worst_case:.6f}"
        )
    return {
        "model": model_id,
        "call_count": CALL_COUNT,
        "input_token_ceiling_per_call": INPUT_TOKEN_CEILING_PER_CALL,
        "max_completion_tokens_per_call": MAX_COMPLETION_TOKENS_PER_CALL,
        "worst_case_usd": worst_case,
        "pricing_source": PRICING_PATH.relative_to(ROOT).as_posix(),
        "pricing_source_sha256": "sha256:" + pricing.sha256_digest,
        "input_bound_method": (
            "UTF-8 payload bytes bound token count; 8192 additional tokens are reserved "
            "for system prompts, message framing, and structured-output schemas"
        ),
    }


def primary_part2_acceptance(payload: Any) -> bool:
    return bool(
        payload.pre_work.scene.status == "authored"
        and payload.pre_work.promise.status == "authored"
        and not payload.scene_receipt.gate.failures
        and not payload.promise_receipt.gate.failures
    )


def pending_operator_verdict(machine_pass: bool, primary_acceptance: bool) -> dict[str, Any]:
    return {
        "pass": None,
        "machine_transport_render_pass": machine_pass,
        "primary_part2_acceptance": primary_acceptance,
        "evidence_status": "pending_operator",
    }


def operator_adjudication_state(
    verdict_path: Path, adjudication: dict[str, Any]
) -> Literal["pass", "fail"] | None:
    try:
        verdict = json.loads(verdict_path.read_text("utf-8"))
        expected_path = verdict_path.relative_to(ROOT).as_posix()
        checks = adjudication["operator_spot_checks"]
    except (OSError, KeyError, json.JSONDecodeError, ValueError):
        return None
    identity_ok = (
        adjudication.get("story") == "36.4"
        and verdict.get("story") == "36.4"
        and adjudication.get("attempt_id") == verdict.get("attempt_id")
        and adjudication.get("original_verdict_path") == expected_path
        and adjudication.get("original_verdict_sha256") == _digest(verdict_path)
        and isinstance(checks, dict)
        and set(checks) == REQUIRED_OPERATOR_SPOT_CHECKS
    )
    if not identity_ok:
        return None
    values = tuple(checks.values())
    if (
        _machine_green_pending(verdict)
        and adjudication.get("semantic_acceptance") is True
        and adjudication.get("operator_verdict") == "PASS"
        and all(value == "PASS" for value in values)
    ):
        return "pass"
    if (
        adjudication.get("semantic_acceptance") is False
        and adjudication.get("operator_verdict") == "FAIL"
        and all(value in {"PASS", "FAIL"} for value in values)
        and "FAIL" in values
    ):
        return "fail"
    return None


def _machine_green_pending(verdict: dict[str, Any]) -> bool:
    assertions = verdict.get("assertions")
    writer_receipts = verdict.get("writer_receipts")
    scene_review = verdict.get("scene_review")
    return bool(
        verdict.get("pass") is None
        and verdict.get("evidence_status") == "pending_operator"
        and verdict.get("machine_transport_render_pass") is True
        and verdict.get("primary_part2_acceptance") is True
        and not verdict.get("error")
        and "error" not in verdict
        and verdict.get("calls") == 2
        and isinstance(writer_receipts, list)
        and len(writer_receipts) == 2
        and isinstance(verdict.get("artifact_digest"), str)
        and verdict["artifact_digest"].startswith("sha256:")
        and isinstance(verdict.get("markdown_path"), str)
        and bool(verdict["markdown_path"])
        and isinstance(verdict.get("docx_path"), str)
        and bool(verdict["docx_path"])
        and isinstance(assertions, dict)
        and bool(assertions)
        and all(value is True for value in assertions.values())
        and isinstance(scene_review, dict)
        and isinstance(scene_review.get("scene"), dict)
        and isinstance(scene_review.get("operator_warnings"), list)
        and isinstance(scene_review.get("introduced_terms"), list)
    )


def operator_adjudication_accepts(verdict_path: Path, adjudication: dict[str, Any]) -> bool:
    return operator_adjudication_state(verdict_path, adjudication) == "pass"


def _failed_attempts() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for adjudication_path in EVIDENCE_ROOT.glob("prework-36-4-adjudication-*/adjudication.json"):
        try:
            adjudication = json.loads(adjudication_path.read_text("utf-8"))
            original = ROOT / adjudication["original_verdict_path"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            continue
        if original.is_file() and operator_adjudication_state(original, adjudication) == "fail":
            found[adjudication["attempt_id"]] = original
    return found


def validate_recovery_label(recovery_of: str | None) -> Path | None:
    failed = _failed_attempts()
    if recovery_of:
        prior = failed.get(recovery_of)
        if prior is None:
            raise ValueError("--recovery-of must identify an existing failed Story 36.4 attempt")
        return prior
    if failed:
        raise ValueError(
            "a prior failed Story 36.4 live attempt exists; a second attempt must be "
            "explicitly labeled with --recovery-of <attempt-id>"
        )
    return None


def read_fresh_clone_manifest(run_dir: Path) -> tuple[FreshCloneManifest, str]:
    path = run_dir / "fresh-clone-manifest.json"
    if not path.is_file():
        raise ValueError("recovery requires fresh-clone-manifest.json")
    manifest = FreshCloneManifest.model_validate_json(path.read_text("utf-8"), strict=True)
    companions = {
        "run_json_digest": run_dir / "run.json",
        "ratified_los_digest": run_dir / "ratified-los.json",
        "segment_manifest_digest": run_dir / "exports/segment-manifest-storyboard-b.yaml",
        "bundle_extracted_digest": run_dir / "bundle/extracted.md",
    }
    for field, companion in companions.items():
        if getattr(manifest, field) != _digest(companion):
            raise ValueError(f"fresh clone manifest digest mismatch: {field}")
    if (run_dir / "workbook-brief.v1.json").exists():
        raise ValueError("fresh clone must not contain workbook-brief.v1.json sidecar")
    return manifest, _digest(path)


def validate_fresh_output_root(output_root: Path) -> None:
    if output_root.exists():
        raise ValueError("live recovery output root must be fresh and not already exist")


def preflight(args: argparse.Namespace, *, require_credentials: bool) -> dict[str, Any]:
    if not math.isfinite(args.max_spend_usd) or args.max_spend_usd <= 0:
        raise ValueError("--max-spend-usd must be finite and greater than zero")
    prior_verdict = validate_recovery_label(args.recovery_of)
    config_payload = yaml.safe_load(CONFIG_PATH.read_text("utf-8"))
    model_id = config_payload["default_model"]
    spend_bound = preventive_spend_bound(args.max_spend_usd, model_id)
    course_root = validate_course_source_root(Path(args.course_root))
    run_dir = Path(args.run_dir).resolve(strict=True)
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = (ROOT / output_root).resolve()
    output_root.relative_to(ROOT.resolve())
    validate_fresh_output_root(output_root)
    required = [
        run_dir / "run.json",
        run_dir / "ratified-los.json",
        run_dir / "exports/segment-manifest-storyboard-b.yaml",
        run_dir / "bundle/extracted.md",
        CONFIG_PATH,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"live witness preflight missing required files: {missing}")
    trial = ProductionTrialEnvelope.model_validate_json((run_dir / "run.json").read_text("utf-8"))
    if trial.production_envelope.get_contribution("workbook_brief", node_id="07W.1"):
        raise ValueError("first-run-stands attempt already has workbook_brief@07W.1")
    if (run_dir / "workbook-brief.v1.json").exists():
        raise ValueError("fresh clone must not contain workbook-brief.v1.json sidecar")
    clone_manifest = clone_manifest_digest = None
    if args.recovery_of:
        clone_manifest, clone_manifest_digest = read_fresh_clone_manifest(run_dir)
    source = load_part2_scene_source(course_root)
    authority = resolve_promise_objectives(run_dir)
    serialized_source_bytes = len(str(source).encode("utf-8"))
    serialized_authority_bytes = len(str(authority).encode("utf-8"))
    payload_byte_ceiling = INPUT_TOKEN_CEILING_PER_CALL - 8192
    if max(serialized_source_bytes, serialized_authority_bytes) > payload_byte_ceiling:
        raise ValueError("serialized writer input exceeds preventive input-token ceiling")
    if authority.status != "authored":
        raise ValueError(f"Promise authority is not authored: {authority.known_losses}")
    if require_credentials:
        absent = [
            name
            for name in ("OPENAI_API_KEY", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT")
            if not os.getenv(name)
        ]
        if absent:
            raise ValueError(f"live witness credentials absent: {absent}")
    return {
        "course_root": course_root,
        "run_dir": run_dir,
        "output_root": output_root,
        "trial": trial,
        "source": source,
        "authority": authority,
        "model_config_digest": _digest(CONFIG_PATH),
        "run_json_digest": _digest(run_dir / "run.json"),
        "ratified_los_digest": _digest(run_dir / "ratified-los.json"),
        "segment_manifest_digest": _digest(run_dir / "exports/segment-manifest-storyboard-b.yaml"),
        "bundle_extracted_digest": _digest(run_dir / "bundle/extracted.md"),
        "clone_manifest": clone_manifest.model_dump(mode="json") if clone_manifest else None,
        "clone_manifest_digest": clone_manifest_digest,
        "bound_fresh_output_root": output_root.relative_to(ROOT).as_posix(),
        "recovery_of": args.recovery_of,
        "fresh_pre_07w1_input_required": True,
        "causal_fix": causal_fix_manifest(prior_verdict) if prior_verdict else None,
        "spend_bound": spend_bound,
        "serialized_input_bytes": {
            "scene_source": serialized_source_bytes,
            "promise_authority": serialized_authority_bytes,
            "reserved_prompt_schema_overhead_tokens": 8192,
        },
    }


def _state(trial: ProductionTrialEnvelope, run_dir: Path, output_root: Path) -> RunState:
    entry = ModelResolutionEntry(
        level="per_specialist",
        requested="gpt-5",
        resolved="gpt-5",
        reason="story-36.4-live-witness",
        timestamp=datetime.now(UTC),
    )
    return RunState(
        run_id=trial.trial_id,
        graph_version="v42",
        status="running",
        model_resolution_trail=[entry],
        component_selection=ComponentSelection(deck=True, motion=True, workbook=True),
        production_envelope=trial.production_envelope,
        cache_state=CacheState(
            cache_prefix=json.dumps(
                {"run_dir": str(run_dir), "output_root": str(output_root)},
                sort_keys=True,
            ),
            entries_count=0,
        ),
    )


def run_live(args: argparse.Namespace, facts: dict[str, Any]) -> Path:
    attempt_id = str(uuid4())
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    pack = EVIDENCE_ROOT / f"prework-36-4-live-{stamp}-{attempt_id[:8]}"
    pack.mkdir(parents=True, exist_ok=False)
    (pack / "attempt-id.txt").write_text(attempt_id + "\n", "utf-8")
    verdict: dict[str, Any] = {
        "story": "36.4",
        "attempt_id": attempt_id,
        "first_run_stands": True,
        "pass": None,
        "recovery_of": facts["recovery_of"],
        "causal_fix": facts["causal_fix"],
        "preventive_spend_bound": facts["spend_bound"],
        "serialized_input_bytes": facts["serialized_input_bytes"],
        "inputs": {
            "course_root": str(facts["course_root"]),
            "run_json_digest": facts["run_json_digest"],
            "ratified_los_digest": facts["ratified_los_digest"],
            "model_config_digest": facts["model_config_digest"],
            "segment_manifest_digest": facts["segment_manifest_digest"],
            "bundle_extracted_digest": facts["bundle_extracted_digest"],
            "clone_manifest_digest": facts["clone_manifest_digest"],
            "clone_manifest": facts["clone_manifest"],
            "bound_fresh_output_root": facts["bound_fresh_output_root"],
        },
        "operator_spot_checks": {
            key: "PENDING"
            for key in (
                "provenance",
                "actual_payoff",
                "semantic_faithfulness",
                "scene_innocence",
                "pertinent_ability",
                "lo_fidelity",
                "half_rhyme",
                "mastery_overclaim",
                "no_spoiler",
            )
        },
    }
    try:
        max_tokens = facts["spend_bound"]["max_completion_tokens_per_call"]
        scene_writer = LiveSceneComposer(max_completion_tokens=max_tokens)
        promise_writer = LivePromiseTransformer(max_completion_tokens=max_tokens)
        context = WorkbookBriefRuntimeContext(
            run_dir=facts["run_dir"],
            course_source_root=facts["course_root"],
            encounter_mode=args.encounter_mode,
            context_origin="new_start",
            writer_execution_mode="live",
            scene_writer=scene_writer,
            promise_writer=promise_writer,
        )
        trial = facts["trial"]
        trial.production_envelope = workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
        calls = scene_writer.calls_made + promise_writer.calls_made
        artifact = read_workbook_brief(facts["run_dir"])
        receipts = [row.model_dump(mode="json") for row in artifact.payload.writer_receipts]
        known_costs = [row.cost_usd for row in artifact.payload.writer_receipts]
        if calls != 2:
            raise RuntimeError(f"bounded witness requires exactly two calls, got {calls}")
        if any(cost is None for cost in known_costs):
            raise RuntimeError("bounded spend is unprovable because provider cost is unavailable")
        total_cost = sum(float(cost) for cost in known_costs if cost is not None)
        if total_cost > args.max_spend_usd:
            raise RuntimeError(
                f"bounded spend ${total_cost:.6f} exceeds cap ${args.max_spend_usd:.6f}"
            )
        trial_path = facts["run_dir"] / "run.json"
        trial_path.write_text(trial.model_dump_json(indent=2) + "\n", "utf-8")
        sidecar = produce_workbook(
            _state(trial, facts["run_dir"], facts["output_root"]),
            {"run_dir": str(facts["run_dir"]), "output_root": str(facts["output_root"])},
        )
        if sidecar is None:
            raise RuntimeError("terminal 07W produced no workbook")
        md_path, docx_path = ROOT / sidecar.markdown_path, ROOT / sidecar.docx_path
        if not md_path.is_file() or not docx_path.is_file():
            raise RuntimeError("terminal workbook artifacts are absent")
        markdown = md_path.read_text("utf-8")
        paragraphs = [paragraph.text for paragraph in Document(docx_path).paragraphs]
        assertions = {
            "beat_order": all(
                markdown.index(f"## {heading}") >= 0
                for heading in ("Scene", "Friction Scale", "Promise")
            ),
            "fr17": all(
                forbidden not in markdown and forbidden not in paragraphs
                for forbidden in ("Transcript-narrative", "Transcript of Record", "Figures")
            ),
            "md_nonempty": md_path.stat().st_size > 0,
            "docx_nonempty": docx_path.stat().st_size > 0,
        }
        machine_transport_render_pass = all(assertions.values())
        scene_failures = artifact.payload.scene_receipt.gate.failures
        promise_failures = artifact.payload.promise_receipt.gate.failures
        primary_acceptance = primary_part2_acceptance(artifact.payload)
        verdict.update(pending_operator_verdict(machine_transport_render_pass, primary_acceptance))
        verdict.update(
            {
                "scene_gate_failures": list(scene_failures),
                "promise_gate_failures": list(promise_failures),
                "scene_review": {
                    "scene": artifact.payload.pre_work.scene.model_dump(mode="json"),
                    "operator_warnings": list(artifact.payload.scene_receipt.operator_warnings),
                    "introduced_terms": list(artifact.payload.scene_receipt.introduced_terms),
                },
                "calls": calls,
                "total_cost_usd": total_cost,
                "max_spend_usd": args.max_spend_usd,
                "writer_receipts": receipts,
                "artifact_digest": artifact.payload_digest,
                "contribution": workbook_wiring.workbook_brief_contribution_receipt(artifact),
                "markdown_path": sidecar.markdown_path,
                "docx_path": sidecar.docx_path,
                "assertions": assertions,
            }
        )
    except Exception as exc:  # first run stands: record, never retry
        verdict["error"] = f"{type(exc).__name__}: {exc}"
    (pack / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n", "utf-8")
    (pack / "PROOF.md").write_text(
        "# Story 36.4 bounded live proof\n\n"
        f"- attempt: `{attempt_id}`\n- pass: `{verdict['pass']}`\n"
        f"- first-run-stands: `true`\n- operator spot-checks: `PENDING`\n",
        "utf-8",
    )
    if "error" in verdict or not verdict.get("machine_transport_render_pass"):
        raise RuntimeError(f"live evidence failed; immutable pack: {pack}")
    return pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--encounter-mode", choices=["recorded", "live"], default="recorded")
    parser.add_argument("--max-spend-usd", type=float, required=True)
    parser.add_argument(
        "--recovery-of",
        help="Failed immutable attempt UUID this explicitly labeled recovery follows.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    facts = preflight(args, require_credentials=not args.dry_run)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "provider_calls": 0,
                    "evidence_pack_created": False,
                    "course_root": str(facts["course_root"]),
                    "run_dir": str(facts["run_dir"]),
                    "model_config_digest": facts["model_config_digest"],
                    "clone_manifest_digest": facts.get("clone_manifest_digest"),
                    "bound_fresh_output_root": facts.get("bound_fresh_output_root"),
                },
                indent=2,
            )
        )
        return 0
    pack = run_live(args, facts)
    print(pack)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
