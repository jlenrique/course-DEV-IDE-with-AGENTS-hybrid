"""Config opt-in gating (AD-19): a disabled class never fires; real file loads."""

from __future__ import annotations

from pathlib import Path

from app.models.runtime.operator_surface import HudConfig, load_hud_config
from app.notify.service import NotifierService
from tests.notify._helpers import make_projection

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "state" / "config" / "hud-config.yaml"


def test_shipped_config_parses_clean():
    cfg, status = load_hud_config(CONFIG_PATH)
    assert status == "ok"
    assert cfg.hud_port == 8791
    assert cfg.stall_budget_seconds == 600
    assert cfg.staleness_budget_seconds == 5
    assert cfg.notifications["paused_at_gate"].push is True
    assert cfg.notifications["batch_pause_resumed"].push is False
    assert cfg.notifications["health_threshold"].push is False


def test_disabled_class_does_not_fire(run_dir, state_dir, writer, fake_apprise, clock, tmp_path):
    """An operator who disables paused_at_gate gets no notification for it."""
    cfg = tmp_path / "hud-config.yaml"
    cfg.write_text(
        "notifications:\n  paused_at_gate:\n    enabled: false\n",
        encoding="utf-8",
    )
    svc = NotifierService(
        trial_id="22222222-2222-4222-8222-222222222222",
        run_dir=run_dir,
        state_dir=state_dir,
        config_path=cfg,
        push_urls=["ntfy://topic"],
        apprise_factory=lambda: fake_apprise,
        now_fn=clock.now,
    )
    # Partial override merged over defaults: only paused_at_gate disabled.
    assert svc.config.notifications["paused_at_gate"].enabled is False
    assert svc.config.notifications["paused_at_error"].enabled is True
    writer.write(make_projection(status="paused-at-gate", paused_gate="G1", seq=1, progress_seq=1))
    assert svc.poll_once() == []
    assert fake_apprise.notifications == []


def test_unreadable_config_falls_back_to_defaults(run_dir, state_dir, fake_apprise, tmp_path):
    """A missing/invalid config never crashes the notifier — defaults active."""
    missing = tmp_path / "does-not-exist.yaml"
    svc = NotifierService(
        trial_id="33333333-3333-4333-8333-333333333333",
        run_dir=run_dir,
        state_dir=state_dir,
        config_path=missing,
        push_urls=[],
        apprise_factory=lambda: fake_apprise,
    )
    assert "defaults active" in svc.config_parse_status
    assert isinstance(svc.config, HudConfig)
