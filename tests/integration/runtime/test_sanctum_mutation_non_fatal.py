from __future__ import annotations

from uuid import UUID

from app.ledger.emitter import EmissionResult
from app.runtime.sanctum_watcher import (
    SanctumWatcher,
    clear_sanctum_warning_registry,
    get_sanctum_mutation_total,
)

TRIAL_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


def test_sanctum_mutation_non_fatal(tmp_path) -> None:
    clear_sanctum_warning_registry()
    sanctum_root = tmp_path / "_bmad" / "memory" / "wanda-sidecar"
    sanctum_root.mkdir(parents=True)
    target = sanctum_root / "CAPABILITIES.md"
    target.write_text("baseline\n", encoding="utf-8")
    captured = []

    def _emit(event):
        captured.append(event)
        return EmissionResult(
            status="failed",
            event_id=None,
            idempotency_key=event.idempotency_key(),
            reason="connection refused",
        )

    watcher = SanctumWatcher(sanctum_root=sanctum_root.parent, emit_event=_emit)
    watcher.begin_invocation(TRIAL_ID)
    target.write_text("baseline\nmutated\n", encoding="utf-8")

    watcher.handle_path(target)
    watcher.finish_invocation()

    assert len(captured) == 1
    assert get_sanctum_mutation_total() == 1
