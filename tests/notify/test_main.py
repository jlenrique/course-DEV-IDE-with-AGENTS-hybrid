"""Standalone entry: run loop exit-on-terminal + detached launch flags (35.6)."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC

from app.notify.__main__ import (
    _build_arg_parser,
    _detached_popen_kwargs,
    launch_notifier,
    run_forever,
)
from app.notify.service import PRODUCER_PID_ENV, NotifierService
from tests.notify._helpers import FakeApprise, make_projection


class _FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def monotonic(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.t += s


def _service(run_dir, state_dir):
    return NotifierService(
        trial_id="44444444-4444-4444-8444-444444444444",
        run_dir=run_dir,
        state_dir=state_dir,
        push_urls=[],
        apprise_factory=FakeApprise,
    )


def test_run_forever_exits_after_terminal_plus_grace(run_dir, state_dir, writer):
    """Loop keeps polling while in-flight, then exits grace after terminal."""
    svc = _service(run_dir, state_dir)
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    clk = _FakeClock()

    # Flip to completed on the 3rd poll so the grace window starts there.
    polls = {"n": 0}
    orig = svc.poll_once

    def counting_poll(now=None):
        polls["n"] += 1
        if polls["n"] == 3:
            from datetime import datetime

            writer.write(
                make_projection(
                    status="completed",
                    seq=9,
                    progress_seq=9,
                    completed_at=datetime(2026, 7, 11, 12, 5, tzinfo=UTC),
                )
            )
        return orig(now)

    svc.poll_once = counting_poll  # type: ignore[assignment]
    iterations = run_forever(
        svc,
        poll_interval=2.0,
        grace_seconds=60.0,
        sleep_fn=clk.sleep,
        monotonic_fn=clk.monotonic,
    )
    assert svc.is_terminal()
    # Exact grace accounting (review N4): terminal lands on poll 3, then the
    # loop polls once per interval until grace elapses (60s / 2s = 30 more).
    assert iterations == 3 + int(60.0 / 2.0)


def test_run_forever_respects_max_iterations(run_dir, state_dir, writer):
    svc = _service(run_dir, state_dir)
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    clk = _FakeClock()
    iterations = run_forever(
        svc, sleep_fn=clk.sleep, monotonic_fn=clk.monotonic, max_iterations=5
    )
    assert iterations == 5


def test_detached_popen_kwargs_platform_flags(tmp_path):
    logfile = tmp_path / "state" / "notify" / "trial.log"
    kwargs = _detached_popen_kwargs(logfile)
    try:
        assert logfile.parent.exists()
        assert kwargs["stdin"] is subprocess.DEVNULL
        if sys.platform == "win32":
            detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            assert kwargs["creationflags"] == (detached | new_group)
            assert "start_new_session" not in kwargs
        else:
            assert kwargs["start_new_session"] is True
            assert "creationflags" not in kwargs
    finally:
        kwargs["stdout"].close()


def test_arg_parser_requires_trial_and_run_dir():
    parser = _build_arg_parser()
    ns = parser.parse_args(["--trial-id", "t1", "--run-dir", "/tmp/run", "--config", "c.yaml"])
    assert ns.trial_id == "t1"
    assert ns.run_dir == "/tmp/run"
    assert ns.config == "c.yaml"
    assert ns.poll_interval == 2.0


def test_launch_notifier_builds_detached_child(run_dir, tmp_path, monkeypatch):
    """launch_notifier issues a detached Popen with the right argv (no real spawn)."""
    captured = {}

    class _FakePopen:
        def __init__(self, argv, **kwargs):
            captured["argv"] = argv
            captured["kwargs"] = kwargs
            # Close the logfile handle the helper opened so we don't leak it.
            if "stdout" in kwargs and hasattr(kwargs["stdout"], "close"):
                kwargs["stdout"].close()

    monkeypatch.setattr(subprocess, "Popen", _FakePopen)
    state_dir = tmp_path / "notify-state"
    launch_notifier(
        "trial-xyz",
        run_dir,
        config="cfg.yaml",
        state_dir=state_dir,
        python_executable="python",
    )
    argv = captured["argv"]
    assert argv[:3] == ["python", "-m", "app.notify"]
    assert "--trial-id" in argv and "trial-xyz" in argv
    assert "--run-dir" in argv
    assert "--config" in argv and "cfg.yaml" in argv
    assert (state_dir / "trial-xyz.log").exists()  # logfile pre-created
    if sys.platform == "win32":
        assert "creationflags" in captured["kwargs"]
    else:
        assert captured["kwargs"].get("start_new_session") is True
    # No producer_pid -> the child simply inherits the parent env untouched.
    assert "env" not in captured["kwargs"]


def test_launch_notifier_injects_producer_pid_env(run_dir, tmp_path, monkeypatch):
    """producer_pid rides to the child as HUD_PRODUCER_PID on top of os.environ (S1)."""
    captured = {}

    class _FakePopen:
        def __init__(self, argv, **kwargs):
            captured["argv"] = argv
            captured["kwargs"] = kwargs
            if "stdout" in kwargs and hasattr(kwargs["stdout"], "close"):
                kwargs["stdout"].close()

    monkeypatch.setattr(subprocess, "Popen", _FakePopen)
    monkeypatch.setenv("HUD_TEST_CANARY", "inherited")
    launch_notifier(
        "trial-pid",
        run_dir,
        state_dir=tmp_path / "notify-state",
        python_executable="python",
        producer_pid=31337,
    )
    env = captured["kwargs"]["env"]
    assert env[PRODUCER_PID_ENV] == "31337"
    assert env["HUD_TEST_CANARY"] == "inherited"  # os.environ carried over
