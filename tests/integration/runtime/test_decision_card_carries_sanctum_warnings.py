from __future__ import annotations

from uuid import UUID

from app.runtime.override_api import decision_card_meta_for_trial
from app.runtime.sanctum_watcher import SanctumWatcher, clear_sanctum_warning_registry
from tests.unit.runtime._helpers import register_sample_run_state

TRIAL_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


def test_decision_card_carries_sanctum_warnings(tmp_path) -> None:
    clear_sanctum_warning_registry()
    register_sample_run_state()
    sanctum_root = tmp_path / "_bmad" / "memory" / "wanda-sidecar"
    sanctum_root.mkdir(parents=True)
    target = sanctum_root / "CAPABILITIES.md"
    target.write_text("baseline\n", encoding="utf-8")

    watcher = SanctumWatcher(sanctum_root=sanctum_root.parent)
    watcher.begin_invocation(TRIAL_ID)
    target.write_text("baseline\nmutated\n", encoding="utf-8")
    watcher.handle_path(target)

    meta = decision_card_meta_for_trial(TRIAL_ID)

    assert meta.cache_state == "mixed"
    assert len(meta.sanctum_warnings) == 1
    assert meta.sanctum_warnings[0].file_path.endswith("wanda-sidecar/CAPABILITIES.md")


def test_pre_invocation_mutation_does_not_surface_warning(tmp_path) -> None:
    clear_sanctum_warning_registry()
    register_sample_run_state()
    sanctum_root = tmp_path / "_bmad" / "memory" / "wanda-sidecar"
    sanctum_root.mkdir(parents=True)
    target = sanctum_root / "CAPABILITIES.md"
    target.write_text("baseline\n", encoding="utf-8")

    watcher = SanctumWatcher(sanctum_root=sanctum_root.parent)
    target.write_text("mutated-before\n", encoding="utf-8")
    watcher.handle_path(target)
    watcher.begin_invocation(TRIAL_ID)

    meta = decision_card_meta_for_trial(TRIAL_ID)

    assert meta.cache_state == "healthy"
    assert meta.sanctum_warnings == []
