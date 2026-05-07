"""Story 32-2a AC-C.1: every implemented inventory entry carries a sample_factory.

Iterates DEFAULT_COVERAGE_INVENTORY; for each row whose owner story resolves to
"done" or "review" in sprint-status.yaml AND whose module file exists, asserts
`entry.sample_factory is not None and callable(entry.sample_factory)`. Deferred
rows are skipped. This regression guards against the class of failure 32-2a
remediates: inventory drift where a new story lands a module without wiring a
corresponding factory, silently breaking `emit_coverage_manifest()`.
"""

from __future__ import annotations

from app.marcus.lesson_plan.coverage_manifest import (
    DEFAULT_COVERAGE_INVENTORY,
    PROJECT_ROOT,
    _load_story_statuses,
)

_IMPLEMENTED_STATUSES = frozenset({"done", "review"})


def test_every_implemented_entry_has_callable_sample_factory() -> None:
    statuses = _load_story_statuses(PROJECT_ROOT)
    offenders: list[str] = []
    for entry in DEFAULT_COVERAGE_INVENTORY:
        if entry.deferred:
            continue
        owner_status = statuses.get(entry.owner_story_key)
        module_exists = (PROJECT_ROOT / entry.module_path).exists()
        if (
            owner_status in _IMPLEMENTED_STATUSES
            and module_exists
            and (entry.sample_factory is None or not callable(entry.sample_factory))
        ):
            offenders.append(
                f"step {entry.step_id} ({entry.surface_name!r}) "
                f"owner={entry.owner_story_key} status={owner_status}"
            )
    assert not offenders, (
        "Every implemented coverage inventory entry must wire a callable "
        f"sample_factory (32-2a AC-C.1). Offenders: {offenders}"
    )
