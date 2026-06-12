"""CLI shim for production-clone trial launches."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

from app.composers.section_02a.cli_adapter import compose_and_write
from app.marcus.orchestrator.production_runner import (
    recover_production_trial,
    resume_production_trial,
    run_production_trial,
)
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT


class DirectiveConfirmationRequiredError(RuntimeError):
    """Non-interactive trial-start without --auto-confirm-directive — refuse silent auto-accept."""


class EditorUnavailableError(RuntimeError):
    """Operator chose [e]dit but no usable editor resolved on PATH (per P-R6)."""


class DirectiveDeclinedError(RuntimeError):
    """Operator chose [x]ancel at the G0 confirm-or-edit prompt."""


def _load_env_if_available() -> None:
    try:
        from scripts.utilities.env_loader import load_env

        load_env()
    except (FileNotFoundError, ImportError):
        pass


def _ensure_utf8_io() -> None:
    """Force UTF-8 stdio regardless of OS default codepage (SCP 2026-05-21 §4.3).

    Closes Trial-2 finding #1 cp1252 crash vector for any invocation path
    (PowerShell, CMD, IDE terminal). Idempotent; safe to call repeatedly.
    """
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            with suppress(ValueError, OSError):
                reconfigure(encoding="utf-8", errors="replace")


def _has_langsmith_env() -> bool:
    return bool(os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"))


def _resolve_editor() -> str:
    """Windows-portable editor resolution (P-R6, hardened per Codex P6 review).

    Order:
      1. $EDITOR env (whitespace-stripped); empty/whitespace value falls through.
      2. Platform fallback: notepad on Windows, vi on POSIX. Verified present on
         PATH via ``shutil.which``; absent fallback raises EditorUnavailableError.
      3. Raise EditorUnavailableError if neither resolves.
    """
    editor = (os.environ.get("EDITOR") or "").strip()
    if editor:
        return editor
    fallback = "notepad" if sys.platform.startswith("win") else "vi"
    if shutil.which(fallback) is None:
        raise EditorUnavailableError(
            f"editor fallback {fallback!r} not found on PATH; set $EDITOR (e.g. "
            f"'set EDITOR=notepad' on Windows or 'export EDITOR=vi' on Linux) "
            f"and retry trial start"
        )
    return fallback


def _edit_directive_in_editor(directive_path: Path) -> None:
    editor = _resolve_editor()
    try:
        exit_code = subprocess.call([editor, str(directive_path)])
    except OSError as exc:
        raise EditorUnavailableError(
            f"editor {editor!r} could not be launched ({exc.__class__.__name__}: "
            f"{exc}); set $EDITOR to a launchable binary and retry"
        ) from exc
    if exit_code != 0:
        raise EditorUnavailableError(
            f"editor {editor!r} exited with non-zero code {exit_code}; "
            f"directive edit aborted"
        )


def _g0_prompt_text(directive_path: Path) -> str:
    return (
        "G0 — Directive Composition\n"
        f"Composed directive written to: {directive_path}\n"
        "Review the directive (printed above). Choose:\n"
        "  [c] confirm and proceed\n"
        "  [e] edit in $EDITOR, then reload and re-prompt\n"
        "  [s] save and show path; exit without running the trial\n"
        "  [x] cancel trial (no specialist dispatch)\n"
        "At-gate context: docs/conversational-gates/g0-directive-composition.md\n"
        "Choice [c/e/s/x]: "
    )


def _utf8_safe_print(msg: str) -> None:
    """Write operator-visible text as UTF-8 bytes even on cp1252 consoles."""
    text = str(msg)
    stdout_buffer = getattr(sys.stdout, "buffer", None)
    if stdout_buffer is not None:
        stdout_buffer.write(text.encode("utf-8", errors="replace") + b"\n")
        sys.stdout.flush()
        return
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def _confirm_or_edit_directive(
    *,
    directive_path: Path,
    auto_confirm_directive: bool,
    input_fn: Callable[[str], str] | None = None,
    edit_fn: Callable[[Path], None] | None = None,
    isatty_fn: Callable[[], bool] | None = None,
    print_fn: Callable[[str], None] | None = None,
) -> Literal["confirmed", "saved-only"]:
    """Drive the G0 confirm-or-edit loop; return verdict or raise on cancel/non-interactive.

    Pure-IO seam: callers can inject ``input_fn``, ``edit_fn``, ``isatty_fn``,
    ``print_fn`` for deterministic testing (AC-7.1-C harness).
    """
    input_fn = input_fn or input
    edit_fn = edit_fn or _edit_directive_in_editor
    isatty_fn = isatty_fn or (lambda: sys.stdin.isatty())
    print_fn = print_fn or _utf8_safe_print
    if not isatty_fn():
        if auto_confirm_directive:
            return "confirmed"
        raise DirectiveConfirmationRequiredError(
            "non-interactive stdin and --auto-confirm-directive not set; "
            "directive composition cannot be silently auto-confirmed"
        )
    while True:
        print_fn(directive_path.read_text(encoding="utf-8"))
        choice = (input_fn(_g0_prompt_text(directive_path)) or "").strip().lower()
        if choice == "c":
            return "confirmed"
        if choice == "e":
            edit_fn(directive_path)
            continue
        if choice == "s":
            return "saved-only"
        if choice == "x":
            raise DirectiveDeclinedError(
                "directive composition declined; trial halted at G0 with no "
                "specialist dispatch"
            )
        print_fn("invalid choice; please enter c, e, s, or x")


def _write_cancellation_record(
    *,
    run_dir: Path,
    trial_id: UUID,
    operator_id: str,
    reason: str,
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "trial_id": str(trial_id),
        "operator_id": operator_id,
        "reason": reason,
        "timestamp_utc": datetime.now(tz=UTC).isoformat(),
    }
    target = run_dir / "trial-cancelled-at-g0.json"
    target.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def start_trial(
    *,
    preset: Literal["production", "explore"],
    input_path: Path,
    operator_id: str,
    trial_id: UUID | None = None,
    allow_offline_cost_report: bool = False,
    runs_root: Path = RUNS_ROOT,
    auto_confirm_directive: bool = False,
    confirm_fn: Callable[..., Literal["confirmed", "saved-only"]] | None = None,
) -> dict[str, Any]:
    _ensure_utf8_io()
    _load_env_if_available()
    if not input_path.exists():
        raise FileNotFoundError(f"trial input path does not exist: {input_path}")
    if not allow_offline_cost_report and (
        not os.getenv("OPENAI_API_KEY") or not _has_langsmith_env()
    ):
        raise RuntimeError(
            "OPENAI_API_KEY plus LANGSMITH_API_KEY and LANGSMITH_PROJECT are required "
            "before production trial start. Use --allow-offline-cost-report only "
            "for local harness checks; offline reports do not close production "
            "clone-launch equivalence."
        )
    effective_trial_id = trial_id or uuid4()
    run_dir = runs_root / str(effective_trial_id)

    # G0 directive composition (Story 7a.1, AC-7.1-A/B/C/J).
    # Composer activates for directory inputs (course-content corpora). File
    # inputs are accepted ONLY when the trial is offline (allow_offline_cost_report
    # OR pre-existing test fixtures that never reach Texas); production trials
    # MUST point --input at a corpus directory or G0 composition would be skipped
    # and Texas would receive directive_path=None — exactly the trial-475
    # silent-bypass we are closing. Fail-loud per Codex P4 review.
    if not input_path.is_dir() and not allow_offline_cost_report:
        raise DirectiveConfirmationRequiredError(
            f"--input must point to a corpus directory for production trials; "
            f"single-file --input {input_path} would leave Texas without a "
            f"composed directive_path (trial-475 silent-bypass class). Use "
            f"--allow-offline-cost-report only for local harness checks."
        )

    directive_path: Path | None = None
    directive_digest: str | None = None
    if input_path.is_dir():
        directive_path, directive_digest = compose_and_write(
            corpus_dir=input_path,
            run_dir=run_dir,
            run_id=effective_trial_id,
        )

        confirm = confirm_fn or _confirm_or_edit_directive
        try:
            verdict = confirm(
                directive_path=directive_path,
                auto_confirm_directive=auto_confirm_directive,
            )
        except DirectiveDeclinedError:
            cancel_path = _write_cancellation_record(
                run_dir=run_dir,
                trial_id=effective_trial_id,
                operator_id=operator_id,
                reason="directive_composition_declined",
            )
            print(
                "directive composition declined; trial halted at G0 with no "
                "specialist dispatch"
            )
            return {
                "status": "cancelled-at-g0",
                "trial_id": str(effective_trial_id),
                "operator_id": operator_id,
                "directive_path": directive_path.as_posix(),
                "directive_digest": directive_digest,
                "cancellation_record": cancel_path.as_posix(),
                "transport_kind": "cli",
            }
        if verdict == "saved-only":
            return {
                "status": "saved-only",
                "trial_id": str(effective_trial_id),
                "operator_id": operator_id,
                "directive_path": directive_path.as_posix(),
                "directive_digest": directive_digest,
                "transport_kind": "cli",
            }

    envelope = run_production_trial(
        corpus_path=input_path,
        preset=preset,
        operator_id=operator_id,
        trial_id=effective_trial_id,
        runs_root=runs_root,
        allow_offline_cost_report=allow_offline_cost_report,
        pause_at_gates=not allow_offline_cost_report,
        directive_path=directive_path,
    )

    run_json = run_dir / "run.json"
    cost_json = envelope.cost_report_path
    trace_status = (
        "measured-from-langsmith"
        if envelope.production_clone_launch_evidence
        else "skipped-no-langsmith-env"
    )

    result = {
        "status": (
            envelope.status
            if envelope.production_clone_launch_evidence
            else "registered-offline"
        ),
        "trial_id": str(effective_trial_id),
        "preset": preset,
        "input": input_path.as_posix(),
        "operator_id": operator_id,
        "run_registry_path": run_json.as_posix(),
        "cost_report_json": cost_json.as_posix() if cost_json is not None else None,
        "cost_report_markdown": (
            cost_json.with_suffix(".md").as_posix() if cost_json is not None else None
        ),
        "langsmith_trace_status": trace_status,
        "production_clone_launch_evidence": envelope.production_clone_launch_evidence,
        "directive_path": directive_path.as_posix() if directive_path else None,
        "directive_digest": directive_digest,
        "transport_kind": "cli",
    }
    (run_dir / "trial-start.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def start_trial_cli(args: argparse.Namespace) -> int:
    try:
        payload = start_trial(
            preset=args.preset,
            input_path=Path(args.input),
            operator_id=args.operator_id,
            trial_id=args.trial_id,
            allow_offline_cost_report=args.allow_offline_cost_report,
            runs_root=Path(args.runs_root) if args.runs_root else RUNS_ROOT,
            auto_confirm_directive=getattr(args, "auto_confirm_directive", False),
        )
    except DirectiveConfirmationRequiredError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except EditorUnavailableError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, sort_keys=True))
    if payload.get("status") == "cancelled-at-g0":
        return 2
    return 0


def resume_trial(
    *,
    trial_id: UUID,
    verdict_file: Path,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
) -> dict[str, Any]:
    _load_env_if_available()
    verdict = OperatorVerdict.model_validate_json(
        verdict_file.read_text(encoding="utf-8")
    )
    if verdict.trial_id != trial_id:
        raise ValueError(
            f"verdict trial_id={verdict.trial_id} does not match --trial-id={trial_id}"
        )
    envelope = resume_production_trial(
        trial_id=trial_id,
        verdict=verdict,
        runs_root=runs_root,
        max_specialist_calls=max_specialist_calls,
    )
    result = {
        "status": envelope.status,
        "trial_id": str(trial_id),
        "paused_gate": envelope.paused_gate,
        "run_registry_path": str(runs_root / str(trial_id) / "run.json"),
        "cost_report_json": str(envelope.cost_report_path)
        if envelope.cost_report_path is not None
        else None,
        "production_clone_launch_evidence": envelope.production_clone_launch_evidence,
        "transport_kind": "cli",
    }
    (runs_root / str(trial_id) / "trial-resume.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def resume_trial_cli(args: argparse.Namespace) -> int:
    payload = resume_trial(
        trial_id=args.trial_id,
        verdict_file=Path(args.verdict_file),
        runs_root=Path(args.runs_root) if args.runs_root else RUNS_ROOT,
        max_specialist_calls=args.max_specialist_calls,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


def recover_trial(
    *,
    trial_id: UUID,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
) -> dict[str, Any]:
    """Continue an error-paused trial from its failed node (S4 part 2).

    No verdict file: dispatch-error pauses carry no operator decision — the
    operator fixes the transient cause and re-enters the walk. Gate pauses
    still require `trial resume` + a verdict.
    """
    _load_env_if_available()
    envelope = recover_production_trial(
        trial_id=trial_id,
        runs_root=runs_root,
        max_specialist_calls=max_specialist_calls,
    )
    result = {
        "status": envelope.status,
        "trial_id": str(trial_id),
        "paused_gate": envelope.paused_gate,
        "paused_error_tag": envelope.paused_error_tag,
        "run_registry_path": str(runs_root / str(trial_id) / "run.json"),
        "cost_report_json": str(envelope.cost_report_path)
        if envelope.cost_report_path is not None
        else None,
        "production_clone_launch_evidence": envelope.production_clone_launch_evidence,
        "transport_kind": "cli",
    }
    (runs_root / str(trial_id) / "trial-recover.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def recover_trial_cli(args: argparse.Namespace) -> int:
    payload = recover_trial(
        trial_id=args.trial_id,
        runs_root=Path(args.runs_root) if args.runs_root else RUNS_ROOT,
        max_specialist_calls=args.max_specialist_calls,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


def build_trial_parser(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="trial_command")
    start = subparsers.add_parser("start")
    start.add_argument("--preset", choices=["production", "explore"], default="production")
    start.add_argument("--input", required=True)
    start.add_argument("--operator-id", default="operator_cli")
    start.add_argument("--trial-id", required=False, type=UUID)
    start.add_argument("--runs-root", required=False, help=argparse.SUPPRESS)
    start.add_argument(
        "--allow-offline-cost-report",
        action="store_true",
        help=(
            "Write a zero-cost deterministic local report when LangSmith env is absent. "
            "Does not count as production clone-launch evidence."
        ),
    )
    start.add_argument(
        "--auto-confirm-directive",
        action="store_true",
        help=(
            "Skip the G0 confirm-or-edit prompt and accept the composed "
            "directive verbatim. Required for non-interactive trial starts."
        ),
    )
    resume = subparsers.add_parser("resume")
    resume.add_argument("--trial-id", required=True, type=UUID)
    resume.add_argument("--verdict-file", required=True)
    resume.add_argument("--runs-root", required=False, help=argparse.SUPPRESS)
    resume.add_argument(
        "--max-specialist-calls",
        required=False,
        type=int,
        help=(
            "Maximum downstream specialist calls to make during this resume "
            "continuation. Defaults to the paused runner cap."
        ),
    )
    recover = subparsers.add_parser(
        "recover",
        help=(
            "Continue an error-paused trial from its failed node (no verdict "
            "file; dispatch-error pauses carry no operator decision)."
        ),
    )
    recover.add_argument("--trial-id", required=True, type=UUID)
    recover.add_argument("--runs-root", required=False, help=argparse.SUPPRESS)
    recover.add_argument(
        "--max-specialist-calls",
        required=False,
        type=int,
        help=(
            "Maximum downstream specialist calls to make during this recovery "
            "continuation. Defaults to the paused runner cap."
        ),
    )


__all__ = [
    "DirectiveConfirmationRequiredError",
    "DirectiveDeclinedError",
    "EditorUnavailableError",
    "build_trial_parser",
    "recover_trial",
    "recover_trial_cli",
    "resume_trial",
    "resume_trial_cli",
    "start_trial",
    "start_trial_cli",
]
