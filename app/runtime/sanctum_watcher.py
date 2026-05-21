"""Watch sanctum markdown files and surface in-flight mutation warnings."""

from __future__ import annotations

import hashlib
import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.ledger.emitter import EmissionResult, emit_ledger_event
from app.ledger.events import SanctumMutationEvent, build_sanctum_mutation_ledger_event
from app.runtime.sanctum_warning import SanctumWarning

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ModuleNotFoundError:
    WATCHDOG_AVAILABLE = False

    class FileSystemEvent:  # pragma: no cover - exercised only without watchdog installed.
        def __init__(self, src_path: str) -> None:
            self.src_path = src_path

    class FileSystemEventHandler:  # pragma: no cover - exercised only without watchdog installed.
        pass

    class Observer:  # pragma: no cover - exercised only without watchdog installed.
        def schedule(
            self,
            handler: FileSystemEventHandler,
            path: str,
            recursive: bool = True,
        ) -> None:
            del handler, path, recursive

        def start(self) -> None:
            return None

        def stop(self) -> None:
            return None

        def join(self, timeout: float | None = None) -> None:
            del timeout
            return None

DEFAULT_SANCTUM_ROOT = Path(__file__).resolve().parents[2] / "_bmad" / "memory"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
LOGGER = logging.getLogger(__name__)
_PENDING_WARNINGS: dict[UUID, list[SanctumWarning]] = {}
_SANCTUM_MUTATIONS_TOTAL = 0


def _sha256_for(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _iter_markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        (path for path in root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def get_sanctum_warnings(trial_id: UUID) -> list[SanctumWarning]:
    return list(_PENDING_WARNINGS.get(trial_id, []))


def clear_sanctum_warning_registry() -> None:
    global _SANCTUM_MUTATIONS_TOTAL
    _PENDING_WARNINGS.clear()
    _SANCTUM_MUTATIONS_TOTAL = 0


def get_sanctum_mutation_total() -> int:
    return _SANCTUM_MUTATIONS_TOTAL


class _SanctumEventHandler(FileSystemEventHandler):
    def __init__(self, watcher: SanctumWatcher) -> None:
        self._watcher = watcher

    def on_modified(self, event: FileSystemEvent) -> None:
        self._watcher.handle_path(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        self._watcher.handle_path(event.src_path)


class SanctumWatcher:
    """Observe sanctum markdown files and register in-flight mutation warnings."""

    def __init__(
        self,
        *,
        sanctum_root: Path = DEFAULT_SANCTUM_ROOT,
        emit_event: Callable[[SanctumMutationEvent], EmissionResult] = emit_ledger_event,
        observer_factory: type[Observer] = Observer,
        now_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self.sanctum_root = sanctum_root
        self._emit_event = emit_event
        self._observer_factory = observer_factory
        self._now_factory = now_factory or (lambda: datetime.now(UTC))
        self._observer: Observer | None = None
        self._active_trial_id: UUID | None = None
        self._hashes = self._snapshot_hashes()
        self._poll_thread: threading.Thread | None = None
        self._stop_polling = threading.Event()

    def _snapshot_hashes(self) -> dict[str, str]:
        return {
            path.relative_to(self.sanctum_root).as_posix(): _sha256_for(path)
            for path in _iter_markdown_files(self.sanctum_root)
        }

    def start(self) -> None:
        if self._observer is not None or self._poll_thread is not None:
            return
        if WATCHDOG_AVAILABLE:
            observer = self._observer_factory()
            observer.schedule(_SanctumEventHandler(self), str(self.sanctum_root), recursive=True)
            observer.start()
            self._observer = observer
            return

        self._stop_polling.clear()

        def _poll() -> None:
            while not self._stop_polling.wait(0.1):
                for path in _iter_markdown_files(self.sanctum_root):
                    self.handle_path(path)

        thread = threading.Thread(target=_poll, name="sanctum-watcher-poll", daemon=True)
        thread.start()
        self._poll_thread = thread

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
        if self._poll_thread is not None:
            self._stop_polling.set()
            self._poll_thread.join(timeout=5)
            self._poll_thread = None

    def begin_invocation(self, trial_id: UUID) -> None:
        self._active_trial_id = trial_id
        self._hashes = self._snapshot_hashes()

    def finish_invocation(self) -> None:
        self._active_trial_id = None
        self._hashes = self._snapshot_hashes()

    def handle_path(self, path: str | Path) -> SanctumMutationEvent | None:
        resolved = Path(path)
        if resolved.suffix.lower() != ".md" or not resolved.is_file():
            return None
        try:
            relative_path = resolved.relative_to(self.sanctum_root).as_posix()
        except ValueError:
            return None

        hash_after = _sha256_for(resolved)
        hash_before = self._hashes.get(relative_path, EMPTY_SHA256)
        if hash_before == hash_after:
            return None
        self._hashes[relative_path] = hash_after

        if self._active_trial_id is None:
            return None

        mutated_at = self._now_factory()
        event = build_sanctum_mutation_ledger_event(
            trial_id=self._active_trial_id,
            file_path=relative_path,
            hash_before=hash_before,
            hash_after=hash_after,
            mutated_at=mutated_at,
            suggested_invalidating_commit=None,
        )
        self._emit_event(event)

        warning = SanctumWarning(
            file_path=relative_path,
            hash_before=hash_before,
            hash_after=hash_after,
            mutated_at=mutated_at,
            suggested_invalidating_commit=None,
        )
        _PENDING_WARNINGS.setdefault(self._active_trial_id, []).append(warning)
        global _SANCTUM_MUTATIONS_TOTAL
        _SANCTUM_MUTATIONS_TOTAL += 1
        LOGGER.warning(
            "sanctum mutation detected trial_id=%s file_path=%s",
            self._active_trial_id,
            relative_path,
        )
        return event


__all__ = [
    "DEFAULT_SANCTUM_ROOT",
    "SanctumWatcher",
    "WATCHDOG_AVAILABLE",
    "clear_sanctum_warning_registry",
    "get_sanctum_mutation_total",
    "get_sanctum_warnings",
]
