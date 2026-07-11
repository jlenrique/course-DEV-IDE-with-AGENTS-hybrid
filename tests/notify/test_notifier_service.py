"""Notifier service goldens + watchdog + restart + fault injection (Story 35.6).

All hermetic: a FakeApprise spy replaces the real transport; no network is
touched (the one real push is the separate ``live`` witness). These pin AD-9
(restart semantics, own state dir, channel split), AD-10 (stall + producer-dead
watchdog), AD-18 (derivation is contract-owned) and AD-19 (single config owner).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.notify.service import (
    ALLOWED_PUSH_SCHEMES,
    NotifierService,
    validate_push_urls,
)
from tests.notify._helpers import make_projection

NTFY_URL = "ntfy://hud-test-topic"


def _service(run_dir, state_dir, fake_apprise, *, clock=None, push_urls=None, **kw):
    sink: list = []
    svc = NotifierService(
        trial_id="11111111-1111-4111-8111-111111111111",
        run_dir=run_dir,
        state_dir=state_dir,
        push_urls=push_urls if push_urls is not None else [NTFY_URL],
        apprise_factory=lambda: fake_apprise,
        now_fn=(clock.now if clock else None),
        on_event=sink.append,
        **kw,
    )
    svc.test_events = sink  # type: ignore[attr-defined]
    return svc


# --------------------------------------------------------------------------
# Event-firing goldens (AD-18 derivation is contract-owned)
# --------------------------------------------------------------------------


def test_five_event_classes_fire_config_gated(run_dir, state_dir, writer, fake_apprise, clock):
    """A projection sequence fires exactly the right classes; push is config-gated.

    Push classes (paused_at_gate/paused_at_error/run_stalled) reach the spy;
    on-HUD-only classes (batch_pause_resumed/health_threshold) fire but do NOT
    push — the channel split in action.
    """
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)

    # 1) in-flight baseline — no transition.
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    assert [e.event_class for e in svc.poll_once()] == []

    # 2) pause at gate G1 -> paused_at_gate (push).
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=2, progress_seq=2))
    assert [e.event_class for e in svc.poll_once()] == ["paused_at_gate"]

    # 3) resume to in-flight -> nothing.
    writer.write(make_projection(status="in-flight", seq=3, progress_seq=3))
    assert [e.event_class for e in svc.poll_once()] == []

    # 4) enter provider-batch wait -> nothing.
    writer.write(
        make_projection(
            status="waiting_for_provider_batch", waiting_batch_id="b1", seq=4, progress_seq=4
        )
    )
    assert [e.event_class for e in svc.poll_once()] == []

    # 5) batch resumes -> batch_pause_resumed (NO push).
    writer.write(make_projection(status="in-flight", seq=5, progress_seq=5))
    assert [e.event_class for e in svc.poll_once()] == ["batch_pause_resumed"]

    # 6) pause at error -> paused_at_error (push).
    writer.write(
        make_projection(status="paused-at-error", paused_error_tag="oom", seq=6, progress_seq=6)
    )
    assert [e.event_class for e in svc.poll_once()] == ["paused_at_error"]

    # 7) recover then health tile crosses -> health_threshold (NO push).
    writer.write(make_projection(status="in-flight", seq=7, progress_seq=7, health_state="nominal"))
    svc.poll_once()
    writer.write(
        make_projection(status="in-flight", seq=8, progress_seq=8, health_state="breached")
    )
    assert [e.event_class for e in svc.poll_once()] == ["health_threshold"]

    # Channel split: only the three push classes reached the transport.
    pushed_titles = [t for (t, _b) in fake_apprise.notifications]
    assert any("Gate G1" in t for t in pushed_titles)
    assert any("error oom" in t for t in pushed_titles)
    assert len(fake_apprise.notifications) == 2  # batch/health did NOT push


def test_new_gate_identity_refires_within_session(run_dir, state_dir, writer, fake_apprise, clock):
    """G1 -> G2 between polls is a fresh alert (derive same-status new-identity)."""
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=1, progress_seq=1))
    assert [e.event_class for e in svc.poll_once()] == ["paused_at_gate"]
    writer.write(make_projection(status="paused-at-gate", paused_gate="G2", seq=2, progress_seq=1))
    assert [e.event_class for e in svc.poll_once()] == ["paused_at_gate"]
    assert len(fake_apprise.notifications) == 2


# --------------------------------------------------------------------------
# Watchdog (AD-10): frozen progress_seq + producer-dead; batch exempt
# --------------------------------------------------------------------------


def test_stall_fires_once_when_progress_frozen_past_budget(  # noqa: E501
    run_dir, state_dir, writer, fake_apprise, clock
):
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    assert svc.poll_once() == []  # fresh, within budget

    # Advance past the 600s stall budget with NO new projection write.
    clock.advance(601)
    fired = [e.event_class for e in svc.poll_once()]
    assert fired == ["run_stalled"]
    assert svc.state.acked  # acked persisted

    # Still stalled next poll -> does not re-fire (acked at this progress_seq).
    clock.advance(60)
    assert svc.poll_once() == []
    assert len([e for e in fake_apprise.notifications]) == 1


def test_stall_refires_after_progress_then_restall(run_dir, state_dir, writer, fake_apprise, clock):
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    svc.poll_once()
    clock.advance(601)
    assert [e.event_class for e in svc.poll_once()] == ["run_stalled"]
    # Progress advances (new progress_seq), then stalls again -> new alarm.
    writer.write(
        make_projection(
            status="in-flight", seq=2, progress_seq=2, last_progress_at=clock.now()
        )
    )
    svc.poll_once()
    clock.advance(601)
    assert [e.event_class for e in svc.poll_once()] == ["run_stalled"]
    assert len(fake_apprise.notifications) == 2


def test_batch_status_exempt_from_stall(run_dir, state_dir, writer, fake_apprise, clock):
    """waiting_for_provider_batch never stalls no matter how long it sits."""
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write(
        make_projection(
            status="waiting_for_provider_batch", waiting_batch_id="b1", seq=1, progress_seq=1
        )
    )
    svc.poll_once()
    clock.advance(10_000)
    assert svc.poll_once() == []
    assert fake_apprise.notifications == []


def test_producer_dead_fires_run_stalled(run_dir, state_dir, writer, fake_apprise, clock):
    """in-flight + frozen mtime + producer PID not alive -> run_stalled (producer dead)."""
    svc = _service(
        run_dir,
        state_dir,
        fake_apprise,
        clock=clock,
        producer_pid=424242,
        pid_alive_fn=lambda pid: False,
    )
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    svc.poll_once()  # first poll: mtime changed -> not treated as frozen
    fired = [e.event_class for e in svc.poll_once()]  # second poll: frozen + dead
    assert fired == ["run_stalled"]
    assert any("producer dead" in b for (_t, b) in fake_apprise.notifications)


def test_producer_alive_does_not_false_alarm(run_dir, state_dir, writer, fake_apprise, clock):
    svc = _service(
        run_dir, state_dir, fake_apprise, clock=clock, producer_pid=1, pid_alive_fn=lambda pid: True
    )
    writer.write(make_projection(status="in-flight", seq=1, progress_seq=1))
    svc.poll_once()
    assert svc.poll_once() == []  # frozen but producer alive, within stall budget


# --------------------------------------------------------------------------
# Restart semantics (AD-9): own state dir; acked dedup; transition-only batch
# --------------------------------------------------------------------------


def test_restart_mid_pause_unacked_fires_once(run_dir, state_dir, writer, fake_apprise, clock):
    """No prior ack -> the active pause fires exactly once on restart."""
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=5, progress_seq=5))
    # Seed a state file WITHOUT the pause ack (unacknowledged active pause).
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "11111111-1111-4111-8111-111111111111.json").write_text(
        json.dumps({"last_processed_progress_seq": 4, "last_status": "in-flight", "acked": {}}),
        encoding="utf-8",
    )
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    assert [e.event_class for e in svc.poll_once()] == ["paused_at_gate"]
    # Second poll (same pause) -> no refire.
    assert svc.poll_once() == []
    assert len(fake_apprise.notifications) == 1


def test_restart_mid_pause_acked_does_not_refire(run_dir, state_dir, writer, fake_apprise, clock):
    """Already-acked active pause -> silent on restart (no double phone buzz)."""
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=5, progress_seq=5))
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "11111111-1111-4111-8111-111111111111.json").write_text(
        json.dumps(
            {
                "last_processed_progress_seq": 5,
                "last_status": "paused-at-gate",
                "acked": {"paused_at_gate:G1": "2026-07-11T11:59:00+00:00"},
            }
        ),
        encoding="utf-8",
    )
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    assert svc.poll_once() == []
    assert fake_apprise.notifications == []


def test_batch_pause_resumed_transition_only_across_restart(  # noqa: E501
    run_dir, state_dir, writer, fake_apprise, clock
):
    """A restart observing in-flight must NOT synthesize batch_pause_resumed."""
    writer.write(make_projection(status="in-flight", seq=6, progress_seq=6))
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "11111111-1111-4111-8111-111111111111.json").write_text(
        json.dumps(
            {
                "last_processed_progress_seq": 5,
                "last_status": "waiting_for_provider_batch",
                "acked": {},
            }
        ),
        encoding="utf-8",
    )
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    # prev is None on a fresh process -> derive cannot fire batch_pause_resumed.
    assert svc.poll_once() == []


def test_state_file_lives_in_own_dir_never_run_dir(run_dir, state_dir, writer, fake_apprise, clock):
    """Single-writer rule: the notifier writes ONLY to its own state dir."""
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=1, progress_seq=1))
    svc.poll_once()
    assert (state_dir / "11111111-1111-4111-8111-111111111111.json").exists()
    # The run dir holds ONLY the projection the notifier read — nothing written.
    run_contents = {p.name for p in Path(run_dir).iterdir()}
    assert run_contents == {"operator-surface.json"}


# --------------------------------------------------------------------------
# Fault injection (AD-9): notifier failure never propagates
# --------------------------------------------------------------------------


def test_transport_raising_does_not_propagate(run_dir, state_dir, writer, fake_apprise, clock):
    fake_apprise.raise_on_notify = True
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=1, progress_seq=1))
    # poll_once must NOT raise even though the transport blows up.
    events = svc.poll_once()
    assert [e.event_class for e in events] == ["paused_at_gate"]
    assert events[0].pushed is False  # push failed but was swallowed


def test_garbage_projection_is_skipped_not_raised(run_dir, state_dir, writer, fake_apprise, clock):
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    writer.write_raw("{ this is not json ]")
    assert svc.poll_once() == []  # unrecognized -> skipped, no raise


def test_missing_projection_is_noop(run_dir, state_dir, fake_apprise, clock):
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock)
    assert svc.poll_once() == []  # file absent -> no events, no raise


# --------------------------------------------------------------------------
# Scheme allowlist (AD-9): email/webhook stay OUT of v1
# --------------------------------------------------------------------------


def test_scheme_allowlist_rejects_mailto(run_dir, state_dir, writer, fake_apprise, clock):
    svc = _service(
        run_dir,
        state_dir,
        fake_apprise,
        clock=clock,
        push_urls=["mailto://user:pass@example.com", NTFY_URL],
    )
    assert NTFY_URL in svc.push_targets
    assert any(u.startswith("mailto://") for u in svc.rejected_urls)
    assert all(not u.startswith("mailto://") for u in svc.push_targets)


def test_validate_push_urls_unit():
    accepted, rejected = validate_push_urls(
        [
            "ntfy://topic",
            "ntfys://topic",
            "pover://user@token",
            "mailto://a@b.c",
            "json://host/path",
            "slack://token",
            "",
            "   ",
        ]
    )
    assert accepted == ["ntfy://topic", "ntfys://topic", "pover://user@token"]
    assert set(rejected) == {"mailto://a@b.c", "json://host/path", "slack://token"}


def test_allowed_schemes_are_the_v1_set():
    assert frozenset({"ntfy", "ntfys", "pover"}) == ALLOWED_PUSH_SCHEMES


def test_no_push_targets_means_no_push(run_dir, state_dir, writer, fake_apprise, clock):
    """With zero configured URLs, push classes still fire on-HUD but never push."""
    svc = _service(run_dir, state_dir, fake_apprise, clock=clock, push_urls=[])
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=1, progress_seq=1))
    events = svc.poll_once()
    assert [e.event_class for e in events] == ["paused_at_gate"]
    assert events[0].pushed is False
    assert fake_apprise.notifications == []
