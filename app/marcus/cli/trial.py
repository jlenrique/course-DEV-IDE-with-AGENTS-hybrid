"""CLI shim for production-clone trial launches."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

import yaml

from app.composers.section_02a.cli_adapter import compose_and_write
from app.composers.section_02a.composer import (
    DirectiveCompositionError,
    assert_lesson_corpus_leaf,
)
from app.marcus.cli.front_door import FrontDoorError, front_door_select
from app.marcus.cli.marcus_spoc import (
    DEGRADED_PUBLISH_URL_SCRIPTED,
    commit_picker_pick,
    run_picker_preflight,
)
from app.marcus.lesson_plan.bundle_catalog import get_bundle
from app.marcus.lesson_plan.collateral_selection import (
    CollateralSelectionError,
    load_lesson_plan_collateral_selection,
)
from app.marcus.orchestrator.picker_html_emitter import decode_picker_selection_code
from app.marcus.orchestrator.production_runner import (
    recover_production_trial,
    resume_production_trial,
    run_production_trial,
)
from app.marcus.orchestrator.styleguide_picker import PickerError
from app.models.state.component_selection import ComponentSelection
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT


class DirectiveConfirmationRequiredError(RuntimeError):
    """Non-interactive trial-start without --auto-confirm-directive — refuse silent auto-accept."""


class TrialAlreadyExistsError(RuntimeError):
    """`trial start` with a --trial-id that already has a run record (S2 P2).

    Starting again would clobber the existing walk's state; the correct verbs
    are `trial resume` (gate pause) / `trial recover` (error pause). Ceremony
    -abort orphans have no run.json, so the documented "re-run start" retry
    path survives this guard.
    """


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
    # Trial-3 cycle-3 launch fix (2026-06-12): the flag is EXPLICIT operator
    # consent and is honored unconditionally — the old tty-gated form
    # prompted anyway whenever isatty() lied (Windows NUL is a character
    # device, so `< /dev/null` still reads as a tty and two launches died
    # on EOFError at the G0 prompt).
    if auto_confirm_directive:
        return "confirmed"
    if not isatty_fn():
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


def _default_picker_preflight(**kwargs: Any) -> dict[str, Any] | None:
    """Isatty-aware default for the S2 canonical picker ceremony (F-503).

    Interactive means BOTH ``sys.stdin`` AND ``sys.stdout`` are ttys (P17 /
    F-601): a tty stdin with a piped/captured stdout is a scripted shell, not
    an operator conversation. Under a non-interactive stdio pair (pytest, CI,
    scripted shells) the ceremony cannot run: return None — a pickless start
    keeps today's WARN-seed staging byte-identically (AC-3), and the
    non-interactive G0 confirm gate still fail-louds downstream with ZERO
    publish invocations (AC-8). A real tty pair runs the full
    :func:`run_picker_preflight` ceremony (exercised live at AC-L).
    Injectable via ``picker_preflight_fn`` on :func:`start_trial`, mirroring
    the ``confirm_fn`` precedent.
    """

    def _is_tty(stream: Any) -> bool:
        return stream is not None and bool(
            getattr(stream, "isatty", lambda: False)()
        )

    if not (_is_tty(sys.stdin) and _is_tty(sys.stdout)):
        return None
    return run_picker_preflight(**kwargs)


def _course_key(input_path: Path) -> str:
    """Canonical course/corpus identity for pick events (S2 P4).

    ``resolve()`` + ``os.path.normcase`` + posix form: the same corpus reached
    via relative/absolute/drive-case spellings yields ONE key, and relative-
    name cross-corpus collisions are eliminated. Legacy raw-key events simply
    won't match (honest miss)."""
    return Path(os.path.normcase(str(input_path.resolve()))).as_posix()


def _warn_if_pick_dropped_by_edit(directive_path: Path, picks: dict[str, str]) -> None:
    """S2 P10: after the G0 confirm/edit loop, verify the just-committed pick
    still stands in the directive; WARN loudly (stderr) if an edit dropped or
    changed it. The edited directive still wins (operator authority) — this
    is honesty, never a silent revert."""
    try:
        loaded = yaml.safe_load(directive_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        loaded = {}
    rows: dict[str, str] = {}
    if isinstance(loaded, dict):
        for item in loaded.get("gamma_settings") or []:
            if isinstance(item, dict):
                variant = str(item.get("variant_id") or "").strip().upper()
                if variant:
                    rows[variant] = str(item.get("styleguide") or "").strip()
    dropped = {
        variant: guide
        for variant, guide in picks.items()
        if rows.get(str(variant).strip().upper()) != str(guide).strip()
    }
    if dropped:
        print(
            f"WARNING: the directive edit at the G0 gate dropped or changed the "
            f"just-committed styleguide pick {dropped}; the run will proceed "
            f"with the EDITED directive — re-run start with a fresh pick if "
            f"this was unintended.",
            file=sys.stderr,
        )


def _load_gamma_settings_file(path: Path | None) -> list[dict[str, Any]] | None:
    if path is None:
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return None
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("--gamma-settings-file must contain a YAML/JSON list of objects")
    return [dict(item) for item in data]


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
    max_specialist_calls: int | None = None,
    gamma_settings_file: Path | None = None,
    component_selection: ComponentSelection | None = None,
    lesson_plan_collateral_intent_path: Path | None = None,
    lesson_plan_collateral_receipt_path: Path | None = None,
    lesson_plan_collateral_bundle_id: str | None = None,
    picker_preflight_fn: Callable[..., dict[str, Any] | None] | None = None,
    selection_code: str | None = None,
    picker_events_path: Path | None = None,
) -> dict[str, Any]:
    _ensure_utf8_io()
    if not input_path.exists():
        raise FileNotFoundError(f"trial input path does not exist: {input_path}")
    if input_path.is_dir():
        try:
            assert_lesson_corpus_leaf(input_path)
        except DirectiveCompositionError as exc:
            raise DirectiveConfirmationRequiredError(str(exc)) from exc
    _load_env_if_available()
    # S2 P2: an explicit --trial-id that already has a run record is a
    # RESUME/RECOVER situation, not a start — starting again would clobber the
    # walk's state. Fail loud PRE-compose. (Ceremony-abort orphans have no
    # run.json, so the documented re-run-start retry path survives.)
    if trial_id is not None and (runs_root / str(trial_id) / "run.json").exists():
        raise TrialAlreadyExistsError(
            f"trial {trial_id} already has a run record at "
            f"{(runs_root / str(trial_id) / 'run.json').as_posix()}; starting "
            f"again would clobber that run's state. Use 'trial resume' (gate "
            f"pause) or 'trial recover' (error pause) to continue it, or mint "
            f"a fresh --trial-id for a new start."
        )
    if selection_code is not None:
        # S2 F-505 rider: --selection-code binds run_tag = trial_id.hex
        # (F-504), so the trial id must be pre-minted before a code can exist.
        # Fail loud BEFORE composition spends a live LLM call.
        if trial_id is None:
            raise PickerError(
                "--selection-code requires --trial-id: the selection code binds "
                "run_tag = trial_id.hex (F-504), so the trial id must be minted "
                "before the code can be issued"
            )
        # S2 P11: a single-file --input composes no directive for the pick to
        # land in — silently dropping an explicit pick violates fail-loud.
        if not input_path.is_dir():
            raise PickerError(
                f"--selection-code requires a corpus-directory --input: the "
                f"single-file input {input_path} composes no directive for the "
                f"pick to land in, and an explicit pick is never silently dropped"
            )
        # S2 P3: decode + pickability validated PRE-compose (the decode needs
        # only the code + the SSOT; the commit still runs post-compose against
        # the composed directive). A stale/foreign/unpickable code aborts here.
        decode_picker_selection_code(selection_code, expected_run_tag=trial_id.hex)
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
    gamma_settings = _load_gamma_settings_file(gamma_settings_file)
    lesson_plan_bundle_id = lesson_plan_collateral_bundle_id
    if lesson_plan_collateral_intent_path is not None:
        resolved_collateral_selection = load_lesson_plan_collateral_selection(
            lesson_plan_collateral_intent_path
        )
        if resolved_collateral_selection.source == "ratified":
            if (
                component_selection is not None
                and component_selection != resolved_collateral_selection.selection
            ):
                raise CollateralSelectionError(
                    "lesson-plan collateral intent selection conflicts with the "
                    "explicit component_selection argument"
                )
            component_selection = resolved_collateral_selection.selection
            lesson_plan_bundle_id = resolved_collateral_selection.bundle_id
    lesson_plan_receipt_path = (
        lesson_plan_collateral_receipt_path or lesson_plan_collateral_intent_path
    )

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
            gamma_settings=gamma_settings,
        )

        # S2 canonical picker ceremony — F-501 insertion point: post-compose /
        # pre-confirm-gate. The pick lands in THIS directive via
        # write_pick_to_directive (F-404: the projection BOTH walks resolve),
        # before the operator confirm gate, the run record, and any specialist
        # dispatch. A PickerError abort leaves no run record and nothing to
        # resume — the operator re-runs start (the hard halt is S4's).
        pick_record: dict[str, Any] | None = None
        if selection_code is not None:
            # D2 scripted path (F-505): the SAME decode -> validate -> commit
            # path as the interactive ceremony — no prompt, no publish; an
            # invalid/stale code fails the start loudly. The CLI arg IS the
            # operator's explicit, pre-confirmed pick.
            pick_record = commit_picker_pick(
                directive_path=directive_path,
                expected_run_tag=effective_trial_id.hex,
                publish_url=DEGRADED_PUBLISH_URL_SCRIPTED,  # P14 sentinel family
                picked_by=operator_id,
                code=selection_code,
                confirmed=True,
                events_path=picker_events_path,
                run_id=str(effective_trial_id),
                course=_course_key(input_path),  # P4 canonical course key
            )
        elif not auto_confirm_directive:
            # D1 interactive ceremony, F-503 discriminator: gated on
            # (not auto_confirm_directive) AND interactive — the injectable
            # seam mirrors confirm_fn; the default is isatty-gated so a
            # non-tty start stays pickless (WARN-seed staging preserved).
            preflight = picker_preflight_fn or _default_picker_preflight
            pick_record = preflight(
                run_tag=effective_trial_id.hex,  # F-504: hyphen-free run_tag
                directive_path=directive_path,
                out_dir=run_dir,  # the publish receipt lands in the bundle
                picked_by=operator_id,
                run_id=str(effective_trial_id),
                course=_course_key(input_path),  # F-502 identity, P4 canonical
                events_path=picker_events_path,
            )
        if pick_record is not None:
            # The pick patched the directive AFTER composition — re-digest so
            # every downstream record attests the bytes the run actually uses.
            directive_digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()

        confirm = confirm_fn or _confirm_or_edit_directive
        try:
            verdict = confirm(
                directive_path=directive_path,
                auto_confirm_directive=auto_confirm_directive,
            )
        except DirectiveDeclinedError:
            # P10/F-604: [e]dit rounds may have preceded the [x] — the
            # cancellation record attests the post-edit bytes.
            directive_digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
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
        # S2 P10 / F-604: re-digest AFTER the confirm/edit loop — an [e]dit at
        # the G0 gate changes the bytes the run actually uses, so every exit
        # path attests the post-edit directive; WARN loudly if the edit
        # dropped the just-committed pick (the edited directive still wins —
        # operator authority — but never silently).
        directive_digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
        if pick_record is not None:
            _warn_if_pick_dropped_by_edit(directive_path, pick_record["picks"])
        if verdict == "saved-only":
            return {
                "status": "saved-only",
                "trial_id": str(effective_trial_id),
                "operator_id": operator_id,
                "directive_path": directive_path.as_posix(),
                "directive_digest": directive_digest,
                "transport_kind": "cli",
            }

    # Open-throttle discipline (finding #8 at trial scale, 2026-06-12): under
    # S2 per-node keying a resume never revisits pre-checkpoint nodes, so a
    # cap-starved START permanently under-populates the pre-G1 segment and
    # the §06 builder fail-louds post-G1. Production starts pass the cap
    # explicitly; the runner default (1) stays for harness checks.
    runner_kwargs: dict[str, Any] = {}
    if max_specialist_calls is not None:
        runner_kwargs["max_specialist_calls"] = max_specialist_calls
    envelope = run_production_trial(
        corpus_path=input_path,
        preset=preset,
        operator_id=operator_id,
        trial_id=effective_trial_id,
        runs_root=runs_root,
        allow_offline_cost_report=allow_offline_cost_report,
        pause_at_gates=not allow_offline_cost_report,
        directive_path=directive_path,
        # S5 front door: thread the chosen bundle's ComponentSelection through to
        # the composer + both walks. None preserves today's behavior byte-
        # identically (the runner defaults to ComponentSelection.production_default).
        component_selection=component_selection,
        **runner_kwargs,
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
        "lesson_plan_collateral_intent_path": (
            lesson_plan_receipt_path.as_posix()
            if lesson_plan_receipt_path
            else None
        ),
        "lesson_plan_collateral_bundle_id": lesson_plan_bundle_id,
        "transport_kind": "cli",
    }
    (run_dir / "trial-start.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def _resolve_bundle_selection(args: argparse.Namespace) -> ComponentSelection | None:
    """Resolve an optional ``--bundle`` pick to a ComponentSelection via the front
    door (readiness-guarded). A bundle id on the command line IS the operator's
    explicit pick, so it is treated as confirmed; a flagged (non-fully-proven)
    bundle is refused unless ``--allow-unproven-bundle`` is set. No ``--bundle``
    means None (today's default graph)."""
    bundle = getattr(args, "bundle", None)
    if not bundle:
        return None
    selection = front_door_select(
        operator_pick=bundle,
        confirmed=True,
        seeds={"corpus_path": args.input},
        allow_unproven=getattr(args, "allow_unproven_bundle", False),
    )
    return selection.selection


@dataclass(frozen=True)
class _StartSelection:
    selection: ComponentSelection | None
    lesson_plan_collateral_intent_path: Path | None = None
    lesson_plan_collateral_bundle_id: str | None = None


def _resolve_start_component_selection(args: argparse.Namespace) -> _StartSelection:
    """Resolve runtime selection from ratified lesson-plan intent or front door.

    Ratified lesson-plan collateral intent has precedence once present. Without
    that file, the existing manual bundle/front-door path is unchanged.
    """
    intent_path = getattr(args, "lesson_plan_collateral_intent", None)
    if not intent_path:
        return _StartSelection(selection=_resolve_bundle_selection(args))
    intent_file = Path(intent_path)
    resolved = load_lesson_plan_collateral_selection(intent_file)
    if resolved.source != "ratified":
        return _StartSelection(
            selection=_resolve_bundle_selection(args),
            lesson_plan_collateral_intent_path=intent_file,
        )
    bundle = getattr(args, "bundle", None)
    if bundle:
        record = get_bundle(bundle)
        if record is None:
            raise CollateralSelectionError(
                f"{bundle!r} is not a bundle in the closed catalog"
            )
        if record.selection != resolved.selection:
            raise CollateralSelectionError(
                "lesson-plan collateral intent selection conflicts with --bundle"
            )
    return _StartSelection(
        selection=resolved.selection,
        lesson_plan_collateral_intent_path=intent_file,
        lesson_plan_collateral_bundle_id=resolved.bundle_id,
    )


def start_trial_cli(args: argparse.Namespace) -> int:
    try:
        start_selection = _resolve_start_component_selection(args)
        payload = start_trial(
            preset=args.preset,
            input_path=Path(args.input),
            operator_id=args.operator_id,
            trial_id=args.trial_id,
            allow_offline_cost_report=args.allow_offline_cost_report,
            runs_root=Path(args.runs_root) if args.runs_root else RUNS_ROOT,
            auto_confirm_directive=getattr(args, "auto_confirm_directive", False),
            max_specialist_calls=getattr(args, "max_specialist_calls", None),
            gamma_settings_file=(
                Path(args.gamma_settings_file)
                if getattr(args, "gamma_settings_file", None)
                else None
            ),
            component_selection=start_selection.selection,
            lesson_plan_collateral_receipt_path=(
                start_selection.lesson_plan_collateral_intent_path
            ),
            lesson_plan_collateral_bundle_id=(
                start_selection.lesson_plan_collateral_bundle_id
            ),
            selection_code=getattr(args, "selection_code", None),
        )
    except FrontDoorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except CollateralSelectionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except DirectiveConfirmationRequiredError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except TrialAlreadyExistsError as exc:
        # S2 P2: an existing run record means resume/recover, never re-start.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except EditorUnavailableError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except PickerError as exc:
        # S2: a failed/aborted styleguide pick leaves no run record and nothing
        # to resume — surface it and let the operator re-run start.
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
    start.add_argument(
        "--max-specialist-calls",
        required=False,
        type=int,
        help=(
            "Maximum live specialist calls during the start walk (G0 to the "
            "first gate). Production starts should open the throttle: under "
            "per-node keying, resumes never revisit pre-checkpoint nodes, so "
            "a starved start cannot be repaired downstream."
        ),
    )
    start.add_argument(
        "--gamma-settings-file",
        required=False,
        help=(
            "YAML/JSON list of per-variant Gamma settings to inject into the "
            "composed directive before digesting."
        ),
    )
    start.add_argument(
        "--selection-code",
        required=False,
        help=(
            "Pre-minted styleguide-picker SELECTION CODE (SGP-...) to commit "
            "non-interactively at start (S2 scripted path). Requires --trial-id "
            "(the code binds run_tag = trial_id.hex); validated through the "
            "same decode/commit path as the interactive ceremony and fails "
            "loud when stale or invalid."
        ),
    )
    start.add_argument(
        "--bundle",
        required=False,
        help=(
            "Front-door bundle id to compose (e.g. 'narrated-deck'). Omit for "
            "today's default graph (deck+motion). Flagged (not-fully-proven) "
            "bundles are refused unless --allow-unproven-bundle is set."
        ),
    )
    start.add_argument(
        "--lesson-plan-collateral-intent",
        required=False,
        help=(
            "Local YAML/JSON ratified lesson-plan collateral intent. When present, "
            "it resolves through the curated bundle catalog and feeds the existing "
            "ComponentSelection runtime seam."
        ),
    )
    start.add_argument(
        "--allow-unproven-bundle",
        action="store_true",
        help=(
            "Permit a flagged (partial / not-yet) front-door bundle to run "
            "knowing its honest readiness status. Off by default."
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
    "TrialAlreadyExistsError",
    "build_trial_parser",
    "recover_trial",
    "recover_trial_cli",
    "resume_trial",
    "resume_trial_cli",
    "start_trial",
    "start_trial_cli",
]
