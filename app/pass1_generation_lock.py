"""Shared same-host lock for Pass-1 generation publication and consumption."""

from __future__ import annotations

import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from pathlib import Path

if os.name == "nt":
    import msvcrt
else:  # pragma: no cover - exercised by non-Windows CI
    import fcntl


class Pass1GenerationLockError(RuntimeError):
    """The per-run Pass-1 generation lock is unavailable or unsafe."""


@contextmanager
def pass1_generation_lock(run_dir: Path) -> Iterator[None]:
    """Serialize cooperating Pass-1 publishers and authority consumers."""
    run_dir = Path(run_dir)
    lock_path = run_dir.parent / f".{run_dir.name}.irene-pass1.generation.lock"
    descriptor: int | None = None
    locked = False
    try:
        if lock_path.is_symlink():
            raise OSError("Pass-1 generation lock may not be a symlink")
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        opened = os.fstat(descriptor)
        named = lock_path.stat(follow_symlinks=False)
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(named.st_mode)
            or opened.st_nlink != 1
            or named.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
        ):
            raise OSError("Pass-1 generation lock coordinate is unsafe")
        if opened.st_size == 0:
            os.write(descriptor, b"\0")
            os.fsync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.name == "nt":
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        else:  # pragma: no cover - exercised by non-Windows CI
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
    except OSError as exc:
        if descriptor is not None:
            with suppress(OSError):
                os.close(descriptor)
        raise Pass1GenerationLockError(
            "Pass-1 generation lock is unavailable"
        ) from exc
    assert descriptor is not None
    try:
        yield
    finally:
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
            if locked and os.name == "nt":
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            elif locked:  # pragma: no cover - exercised by non-Windows CI
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


__all__ = ["Pass1GenerationLockError", "pass1_generation_lock"]
