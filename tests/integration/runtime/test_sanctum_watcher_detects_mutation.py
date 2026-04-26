from __future__ import annotations

import time
from uuid import UUID

from app.ledger.emitter import EmissionResult
from app.runtime.sanctum_watcher import SanctumWatcher, clear_sanctum_warning_registry

TRIAL_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


def test_sanctum_watcher_detects_mutation(tmp_path) -> None:
    clear_sanctum_warning_registry()
    sanctum_root = tmp_path / "_bmad" / "memory" / "wanda-sidecar"
    sanctum_root.mkdir(parents=True)
    target = sanctum_root / "CAPABILITIES.md"
    target.write_text("baseline\n", encoding="utf-8")
    captured = []

    def _emit(event):
        captured.append(event)
        return EmissionResult(
            status="inserted",
            event_id=event.event_id,
            idempotency_key=event.idempotency_key(),
        )

    watcher = SanctumWatcher(sanctum_root=sanctum_root.parent, emit_event=_emit)
    watcher.begin_invocation(TRIAL_ID)
    watcher.start()
    try:
        target.write_text("baseline\nmutated\n", encoding="utf-8")
        deadline = time.time() + 5
        while not captured and time.time() < deadline:
            time.sleep(0.1)
    finally:
        watcher.stop()

    assert captured
    assert captured[0].file_path.endswith("wanda-sidecar/CAPABILITIES.md")


def test_watcher_observes_only_md_files(tmp_path) -> None:
    clear_sanctum_warning_registry()
    sanctum_root = tmp_path / "_bmad" / "memory" / "wanda-sidecar"
    sanctum_root.mkdir(parents=True)
    target = sanctum_root / "notes.txt"
    target.write_text("baseline\n", encoding="utf-8")
    captured = []

    def _emit(event):
        captured.append(event)
        return EmissionResult(
            status="inserted",
            event_id=event.event_id,
            idempotency_key=event.idempotency_key(),
        )

    watcher = SanctumWatcher(sanctum_root=sanctum_root.parent, emit_event=_emit)
    watcher.begin_invocation(TRIAL_ID)
    watcher.handle_path(target)

    assert captured == []
