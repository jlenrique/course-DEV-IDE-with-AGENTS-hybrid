"""Standalone notifier process entry + launch helper (Story 35.6, AD-9).

Run directly::

    python -m app.notify --trial-id <uuid> --run-dir <run_dir> [--config <path>]

The process polls the projection every ~2s until the run reaches a terminal
status (``completed``/``failed``) plus a grace window, then exits. It is
deliberately its **own** OS process so the stall watchdog does not die with the
runtime session it guards.

Windows survives-session mechanics (the reason this is a separate process):
:func:`launch_notifier` starts the child with
``DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`` creation flags so it is not tied
to the parent console — closing the launching shell (or the parent Python
exiting) does not kill the notifier. On POSIX the equivalent is
``start_new_session=True`` (a new session/process group detached from the
controlling terminal). stdout/stderr are redirected to a per-trial logfile under
the notifier's own state dir so a detached child is still debuggable.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from app.notify.service import (
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_STATE_ROOT,
    PRODUCER_PID_ENV,
    NotifierService,
)

LOGGER = logging.getLogger("app.notify")

#: Grace period after a terminal status before the notifier exits (AD-9).
DEFAULT_GRACE_SECONDS = 60.0


def run_forever(
    service: NotifierService,
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    grace_seconds: float = DEFAULT_GRACE_SECONDS,
    sleep_fn: Callable[[float], None] = time.sleep,
    monotonic_fn: Callable[[], float] = time.monotonic,
    now_fn: Callable[[], datetime] | None = None,
    max_iterations: int | None = None,
) -> int:
    """Poll ``service`` until terminal-status + grace elapses. Returns poll count.

    ``sleep_fn`` / ``monotonic_fn`` / ``max_iterations`` are injected so the
    loop is unit-testable without wall-clock waits. The loop never raises:
    :meth:`NotifierService.poll_once` swallows its own faults.
    """
    terminal_since: float | None = None
    iterations = 0
    while True:
        moment = now_fn() if now_fn is not None else None
        service.poll_once(moment)
        iterations += 1

        if service.is_terminal():
            if terminal_since is None:
                terminal_since = monotonic_fn()
            elif monotonic_fn() - terminal_since >= grace_seconds:
                LOGGER.info("terminal status + grace elapsed — notifier exiting")
                break
        else:
            terminal_since = None

        if max_iterations is not None and iterations >= max_iterations:
            break
        sleep_fn(poll_interval)
    return iterations


def _detached_popen_kwargs(logfile: Path) -> dict:
    """Creation flags/handles that let the child outlive its launching session.

    Windows: ``DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`` — no inherited
    console, own process group. POSIX: ``start_new_session=True``. stdout/stderr
    go to ``logfile`` in append mode so a detached child stays debuggable.

    Story 42.2 AC-7 (no stray console windows): ``DETACHED_PROCESS`` already
    runs the child with NO console at all, so the notifier never pops an empty
    terminal window — it is the "equivalent no-window" mechanism the AC calls
    out. (``CREATE_NO_WINDOW`` is redundant here and is ignored by Windows when
    combined with ``DETACHED_PROCESS``, so it is deliberately not OR-ed in; the
    HUD-server child, which is NOT detached, is the spawn that gains
    ``CREATE_NO_WINDOW`` — see ``preflight._no_window_creationflags``.)
    """
    logfile.parent.mkdir(parents=True, exist_ok=True)
    handle = open(logfile, "ab")  # noqa: SIM115 — child owns this handle for its life
    kwargs: dict = {
        "stdout": handle,
        "stderr": handle,
        "stdin": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        detached_process = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        create_new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        kwargs["creationflags"] = detached_process | create_new_group
    else:
        kwargs["start_new_session"] = True
    return kwargs


def launch_notifier(
    trial_id: str,
    run_dir: str | Path,
    *,
    config: str | Path | None = None,
    state_dir: str | Path | None = None,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    python_executable: str | None = None,
    producer_pid: int | None = None,
) -> subprocess.Popen:
    """Launch the notifier as a detached, session-surviving child process.

    Returns the :class:`subprocess.Popen` handle. The child runs
    ``python -m app.notify`` with the given args and is detached (AD-9) so it
    survives the launching shell/session. The start path calls this; the child
    exits itself on terminal-status + grace.

    ``producer_pid`` (review S1) is handed to the child via the
    ``HUD_PRODUCER_PID`` environment variable so its producer-dead watchdog
    reading has a PID to probe without the launcher exporting anything itself.
    """
    state_root = Path(state_dir) if state_dir is not None else DEFAULT_STATE_ROOT
    logfile = state_root / f"{trial_id}.log"
    executable = python_executable or sys.executable
    argv = [
        executable,
        "-m",
        "app.notify",
        "--trial-id",
        str(trial_id),
        "--run-dir",
        str(run_dir),
        "--poll-interval",
        str(poll_interval),
    ]
    if config is not None:
        argv += ["--config", str(config)]
    if state_dir is not None:
        argv += ["--state-dir", str(state_dir)]
    kwargs = _detached_popen_kwargs(logfile)
    if producer_pid is not None:
        kwargs["env"] = {**os.environ, PRODUCER_PID_ENV: str(producer_pid)}
    LOGGER.info("launching detached notifier for trial %s (log: %s)", trial_id, logfile)
    return subprocess.Popen(argv, **kwargs)  # noqa: S603 — argv is fully controlled


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.notify", description=__doc__)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--config", default=None)
    parser.add_argument("--state-dir", default=None)
    parser.add_argument(
        "--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS
    )
    parser.add_argument(
        "--grace-seconds", type=float, default=DEFAULT_GRACE_SECONDS
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = _build_arg_parser().parse_args(argv)
    service = NotifierService(
        trial_id=args.trial_id,
        run_dir=args.run_dir,
        config_path=args.config,
        state_dir=args.state_dir,
    )
    LOGGER.info(
        "notifier online for trial %s (run_dir=%s, push_targets=%d, config=%s)",
        args.trial_id,
        args.run_dir,
        len(service.push_targets),
        service.config_parse_status,
    )
    run_forever(
        service,
        poll_interval=args.poll_interval,
        grace_seconds=args.grace_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
