"""Run-scoped perception cache.

Cache key: (artifact_path, modality)
Cache scope: production run
"""

from __future__ import annotations

import importlib.util
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:
    from scripts.utilities.file_helpers import project_root
except ModuleNotFoundError:
    def _load_file_helpers() -> Any:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "scripts" / "utilities" / "file_helpers.py"
            if candidate.exists():
                spec = importlib.util.spec_from_file_location("file_helpers_local", candidate)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        raise

    project_root = _load_file_helpers().project_root


class PerceptionCache:
    """Run-scoped JSON cache for sensory bridge outputs."""

    def __init__(self, run_id: str, runtime_dir: str | Path | None = None) -> None:
        if not str(run_id).strip():
            raise ValueError("run_id is required for perception cache")
        self.run_id = str(run_id).strip()
        base = Path(runtime_dir) if runtime_dir else project_root() / "state" / "runtime"
        self.cache_path = base / "perception-cache" / f"{self.run_id}.json"

    @staticmethod
    def _make_key(artifact_path: str | Path, modality: str) -> str:
        return f"{Path(artifact_path).resolve().as_posix()}::{str(modality).strip().lower()}"

    def _read(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            return {"run_id": self.run_id, "entries": {}}
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"run_id": self.run_id, "entries": {}}

    def _write(self, data: dict[str, Any]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(self.cache_path)

    @contextmanager
    def _lock(self, timeout_seconds: float = 3.0):
        """Acquire a lightweight lock for read-modify-write cache operations."""
        lock_path = self.cache_path.with_suffix(self.cache_path.suffix + ".lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.monotonic()
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                try:
                    yield
                finally:
                    os.close(fd)
                    lock_path.unlink(missing_ok=True)
                return
            except (FileExistsError, PermissionError):
                if time.monotonic() - start >= timeout_seconds:
                    raise TimeoutError(f"Timed out waiting for cache lock: {lock_path}")
                time.sleep(0.02)

    def get(self, artifact_path: str | Path, modality: str) -> dict[str, Any] | None:
        data = self._read()
        key = self._make_key(artifact_path, modality)
        entry = data.get("entries", {}).get(key)
        if not entry:
            return None
        return entry.get("result")

    def put(self, artifact_path: str | Path, modality: str, result: dict[str, Any]) -> None:
        with self._lock():
            data = self._read()
            key = self._make_key(artifact_path, modality)
            entries = data.setdefault("entries", {})
            entries[key] = {
                "artifact_path": str(Path(artifact_path).resolve()),
                "modality": str(modality).strip().lower(),
                "result": result,
            }
            self._write(data)

    def clear(self) -> None:
        if self.cache_path.exists():
            self.cache_path.unlink(missing_ok=True)
