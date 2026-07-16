"""Delegated, test-only HIL driver for Marcus-SPOC workbook verification.

This utility does not remove or bypass HIL.  It exercises the production G0
confirmation callback and the production ``resume_production_trial`` seam with
real, card-bound :class:`OperatorVerdict` values.  Its authority is a narrow,
versioned policy approved for Epics 36--40 workbook live tests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import time
import zipfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, TypeVar
from uuid import UUID, uuid4

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composers.section_02a.directive_model import Directive  # noqa: E402
from app.gates.resume_api import compute_decision_card_digest  # noqa: E402
from app.marcus.cli.trial import start_trial  # noqa: E402
from app.marcus.lesson_plan.prework_artifact import (  # noqa: E402
    WORKBOOK_RUNTIME_CONTEXT_FILENAME,
    WorkbookBriefRuntimeContext,
)
from app.marcus.orchestrator.production_runner import (  # noqa: E402
    resume_production_trial,
)
from app.models.decision_cards import AnyDecisionCardAdapter  # noqa: E402
from app.models.runtime.production_trial_envelope import (  # noqa: E402
    ProductionTrialEnvelope,
)
from app.models.state.component_selection import ComponentSelection  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402

DELEGATE_ID = "codex_hil_runner"
POLICY_SCHEMA = "marcus-spoc-live-test-delegation.v1"
JOURNAL_SCHEMA = "marcus-spoc-live-test-hil-journal.v1"
SUMMARY_SCHEMA = "marcus-spoc-live-test-hil-summary.v1"
PREFLIGHT_IDENTITY_SCHEMA = "governed-preflight-input-identity.v1"
OUTPUT_INVENTORY_SCHEMA = "governed-run-output-inventory.v1"
POSTFLIGHT_COMPARISON_SCHEMA = "governed-input-comparison.v1"
PREFLIGHT_IDENTITY_FILENAME = "preflight-input-identity.v1.json"
OUTPUT_INVENTORY_FILENAME = "output-inventory.v1.json"
POSTFLIGHT_COMPARISON_FILENAME = "postflight-input-comparison.v1.json"
_SELECTION_FIELDS = {
    "G2B": "slide_variant_selections",
    "G4A": "selected_voice_id",
}
_TERMINAL_STATES = frozenset({"completed", "failed"})
_STOP_STATES = frozenset(
    {"paused-at-error", "waiting_for_provider_batch", "failed", "registered", "in-flight"}
)
_SECRET_KEY_FRAGMENTS = ("api_key", "password", "secret", "authorization", "credential")
# A freshly written OOXML/Office file (the workbook ``.docx`` lands seconds before
# the output-inventory scan) can be held under a transient share-lock by Windows
# Defender / the Search indexer, surfacing as an ``OSError`` on ``os.open``/read.
# Bounded retry-with-backoff absorbs that transient lock so it cannot false-refuse
# an otherwise-good run; a genuinely unreadable file still fails loud once
# attempts are exhausted.
_TRANSIENT_READ_ATTEMPTS = 5
_TRANSIENT_READ_BACKOFF_SECONDS = 0.1
_WORKBOOK_EXPORT_PREFIX = "exports/workbooks/"

_T = TypeVar("_T")


class RunnerRefusal(RuntimeError):  # noqa: N818 - refusal is the domain term
    """Stable fail-closed refusal from the delegated runner."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class GateRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: Literal["approve", "select"]
    selection_field: Literal["slide_variant_selections", "selected_voice_id"] | None = None
    strategy: Literal["first_offered"] | None = None

    @model_validator(mode="after")
    def _validate_action(self) -> GateRule:
        if self.action == "approve" and (self.selection_field or self.strategy):
            raise ValueError("approve rules cannot carry selection configuration")
        if self.action == "select" and (
            self.selection_field is None or self.strategy != "first_offered"
        ):
            raise ValueError("select rules require a selection_field and first_offered strategy")
        return self


class DelegationScope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    purpose: Literal["epics-36-40-workbook-live-verification"]
    epics: tuple[int, ...]
    customer_facing_approval: Literal[False] = False

    @field_validator("epics")
    @classmethod
    def _exact_workbook_epics(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if value != (36, 37, 38, 39, 40):
            raise ValueError("delegation must be bound exactly to Epics 36-40")
        return value


class RunnerBudgets(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_gate_actions: int = Field(ge=1, le=32)
    max_wall_seconds: int = Field(ge=1, le=86_400)
    max_specialist_calls_per_segment: int = Field(ge=1, le=100)


class DelegationPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[POLICY_SCHEMA]
    delegate_id: Literal[DELEGATE_ID]
    approved_by: Literal["Juanl"]
    authority_spec: str = Field(min_length=1)
    scope: DelegationScope
    allowed_runs_roots: tuple[str, ...]
    allowed_input_roots: tuple[str, ...]
    allowed_evidence_root: str
    gate_rules: dict[str, GateRule]
    stop_states: tuple[str, ...]
    terminal_success_state: Literal["completed"]
    budgets: RunnerBudgets

    @model_validator(mode="after")
    def _closed_policy(self) -> DelegationPolicy:
        expected = {"G0E", "G0R", "G1", "G2B", "G2C", "G3", "G4", "G4A"}
        if set(self.gate_rules) != expected:
            raise ValueError("gate_rules must enumerate the exact production gate inventory")
        for gate, field in _SELECTION_FIELDS.items():
            rule = self.gate_rules[gate]
            if rule.action != "select" or rule.selection_field != field:
                raise ValueError(f"{gate} must use select with {field}")
        if any(self.gate_rules[g].action != "approve" for g in expected - set(_SELECTION_FIELDS)):
            raise ValueError("non-selection gates must be approve-only")
        if set(self.stop_states) != _STOP_STATES:
            raise ValueError("stop_states must enumerate every non-success stop class")
        if not self.allowed_runs_roots or not self.allowed_input_roots:
            raise ValueError("policy roots cannot be empty")
        return self


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _contained_by(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _retry_transient_read(operation: Callable[[], _T]) -> _T:
    """Run ``operation``, retrying only transient ``OSError`` with bounded backoff.

    A Windows AV/indexer share-lock on a just-written file raises ``OSError`` on
    open/read; a few short-backoff retries let it clear. A ``RunnerRefusal`` (or any
    non-``OSError``) raised by ``operation`` is a genuine integrity failure and
    propagates immediately without retry. Once the attempt budget is exhausted the
    last real ``OSError`` is re-raised so a truly unreadable file still fails loud.
    """
    last: OSError | None = None
    for attempt in range(_TRANSIENT_READ_ATTEMPTS):
        try:
            return operation()
        except OSError as exc:
            last = exc
            if attempt + 1 < _TRANSIENT_READ_ATTEMPTS:
                time.sleep(_TRANSIENT_READ_BACKOFF_SECONDS * (attempt + 1))
    assert last is not None  # loop only exits via return or a caught OSError
    raise last


def _stable_file_row(path: Path, *, coordinate: str) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)

    def _read_identity() -> tuple[os.stat_result, os.stat_result, os.stat_result, bytes, bytes]:
        path_before = path.lstat()
        if not stat.S_ISREG(path_before.st_mode):
            raise RunnerRefusal("identity-non-regular-file-refused")
        descriptor = os.open(path, flags)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or (
                path_before.st_dev,
                path_before.st_ino,
            ) != (before.st_dev, before.st_ino):
                raise RunnerRefusal("identity-file-mutated-before-read")
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                raw = stream.read()
                stream.seek(0)
                repeated = stream.read()
            after = os.fstat(descriptor)
            path_after = path.lstat()
        finally:
            os.close(descriptor)
        return before, after, path_after, raw, repeated

    try:
        before, after, path_after, raw, repeated = _retry_transient_read(_read_identity)
    except OSError as exc:
        raise RunnerRefusal("identity-file-unreadable") from exc
    stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields) or any(
        getattr(after, field) != getattr(path_after, field) for field in stable_fields
    ) or raw != repeated:
        raise RunnerRefusal("identity-file-mutated-during-read")
    return {
        "path": coordinate,
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def build_governed_input_identity(
    *,
    trial_id: UUID,
    roots: dict[str, Path],
    writable_exclusions: dict[str, Path],
    bound_files: dict[str, Path] | None = None,
) -> dict[str, Any]:
    """Build a retained, reconstructable per-file immutable-input manifest."""
    if not roots or any(not label or "/" in label for label in roots):
        raise RunnerRefusal("identity-root-label-invalid")
    normalized_roots: dict[str, Path] = {}
    for label, root in sorted(roots.items()):
        normalized = _absolute_without_resolving(root)
        _assert_safe_path(normalized, root=normalized, kind="dir")
        normalized_roots[label] = normalized
    exclusions: dict[str, Path] = {}
    exclusion_rows: list[dict[str, str]] = []
    for label, exclusion in sorted(writable_exclusions.items()):
        normalized = _absolute_without_resolving(exclusion)
        containing_roots = [
            root for root in normalized_roots.values() if _contained_by(normalized, root)
        ]
        if not containing_roots:
            raise RunnerRefusal("writable-exclusion-outside-identity-roots")
        _assert_safe_path(normalized, root=containing_roots[0], kind="missing-ok")
        exclusions[label] = normalized
        exclusion_rows.append(
            {
                "label": label,
                "path": str(normalized.resolve()),
                "reason": "declared-run-output-namespace",
            }
        )
    seen: set[Path] = set()
    files: list[dict[str, Any]] = []
    for label, root in normalized_roots.items():
        pending = [root]
        while pending:
            directory = pending.pop()
            try:
                entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
            except OSError as exc:
                raise RunnerRefusal("identity-tree-unreadable") from exc
            for entry in entries:
                absolute = _absolute_without_resolving(Path(entry.path))
                if any(_contained_by(absolute, exclusion) for exclusion in exclusions.values()):
                    continue
                if entry.is_symlink() or _is_reparse_point(absolute):
                    raise RunnerRefusal("identity-tree-link-refused")
                if entry.name == "__pycache__" or absolute.suffix == ".pyc":
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(absolute)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    raise RunnerRefusal("identity-non-regular-file-refused")
                if absolute in seen:
                    continue
                seen.add(absolute)
                relative = absolute.relative_to(root).as_posix()
                files.append(_stable_file_row(absolute, coordinate=f"{label}/{relative}"))
    bound_file_rows: list[dict[str, str]] = []
    for label, path in sorted((bound_files or {}).items()):
        if not label or "/" in label:
            raise RunnerRefusal("identity-bound-file-label-invalid")
        absolute = _absolute_without_resolving(path)
        _assert_safe_path(absolute, root=absolute.parent, kind="file")
        files.append(_stable_file_row(absolute, coordinate=f"bound/{label}"))
        bound_file_rows.append({"label": label, "path": str(absolute.resolve())})
    files.sort(key=lambda row: row["path"])
    body: dict[str, Any] = {
        "schema_version": PREFLIGHT_IDENTITY_SCHEMA,
        "trial_id": str(trial_id),
        "roots": [
            {"label": label, "path": str(root.resolve())}
            for label, root in normalized_roots.items()
        ],
        "writable_exclusions": exclusion_rows,
        "generated_exclusions": [
            {
                "patterns": ["**/__pycache__/**", "**/*.pyc"],
                "reason": "generated-python-bytecode",
            }
        ],
        "bound_files": bound_file_rows,
        "files": files,
        "file_count": len(files),
        "manifest_digest": _digest(files),
    }
    return {**body, "artifact_digest": _digest(body)}


def build_run_output_inventory(
    *,
    trial_id: UUID,
    run_dir: Path | None = None,
    run_dirs: dict[str, Path] | None = None,
) -> dict[str, Any]:
    """Inventory production outputs separately from immutable preflight inputs."""
    if (run_dir is None) == (run_dirs is None):
        raise RunnerRefusal("output-inventory-root-selection-invalid")
    selected = {"run": run_dir} if run_dir is not None else dict(run_dirs or {})
    files: list[dict[str, Any]] = []
    root_rows: list[dict[str, Any]] = []
    multi_root = len(selected) > 1
    for label, candidate in sorted(selected.items()):
        if not label or "/" in label or candidate is None:
            raise RunnerRefusal("output-inventory-root-invalid")
        absolute = _absolute_without_resolving(candidate)
        if not absolute.exists():
            root_rows.append({"label": label, "path": str(absolute), "present": False})
            continue
        root = _assert_safe_tree(absolute)
        root_rows.append({"label": label, "path": str(root.resolve()), "present": True})
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative == ".codex-hil-runner.lock":
                continue
            coordinate = f"{label}/{relative}" if multi_root else relative
            files.append(_stable_file_row(path, coordinate=coordinate))
    files.sort(key=lambda row: row["path"])
    body: dict[str, Any] = {
        "schema_version": OUTPUT_INVENTORY_SCHEMA,
        "trial_id": str(trial_id),
        "created_at": _utc_now(),
        "output_roots": root_rows,
        "files": files,
        "file_count": len(files),
        "inventory_digest": _digest(files),
    }
    return {**body, "artifact_digest": _digest(body)}


def _is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _absolute_without_resolving(path: Path) -> Path:
    return Path(os.path.abspath(os.path.normpath(os.fspath(path))))


def _assert_safe_path(
    path: Path,
    *,
    root: Path,
    kind: Literal["file", "dir", "missing-ok"],
) -> Path:
    """Refuse escapes, symlinks/junctions, and unexpected file kinds."""
    if ".." in path.parts or ".." in root.parts:
        raise RunnerRefusal("parent-traversal-refused")
    absolute_root = _absolute_without_resolving(root)
    absolute = _absolute_without_resolving(path)
    try:
        relative = absolute.relative_to(absolute_root)
    except ValueError as exc:
        raise RunnerRefusal("path-outside-allowed-root") from exc
    current = absolute_root
    if absolute_root.exists() and (absolute_root.is_symlink() or _is_reparse_point(absolute_root)):
        raise RunnerRefusal("symlink-or-reparse-root-refused")
    for part in relative.parts:
        current /= part
        if current.exists() and (current.is_symlink() or _is_reparse_point(current)):
            raise RunnerRefusal("symlink-or-reparse-path-refused")
    if kind == "file":
        try:
            mode = absolute.lstat().st_mode
        except FileNotFoundError as exc:
            raise RunnerRefusal("required-file-missing") from exc
        if not stat.S_ISREG(mode):
            raise RunnerRefusal("non-regular-file-refused")
    elif kind == "dir":
        try:
            mode = absolute.lstat().st_mode
        except FileNotFoundError as exc:
            raise RunnerRefusal("required-directory-missing") from exc
        if not stat.S_ISDIR(mode):
            raise RunnerRefusal("non-directory-refused")
    elif absolute.exists():
        mode = absolute.lstat().st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise RunnerRefusal("special-file-refused")
    return absolute


def _assert_safe_tree(root: Path) -> Path:
    """Recursively refuse links, reparse points, and special filesystem entries."""
    safe_root = _assert_safe_path(root, root=root, kind="dir")
    pending = [safe_root]
    while pending:
        directory = pending.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise RunnerRefusal("source-tree-unreadable") from exc
        for entry in entries:
            path = Path(entry.path)
            if entry.is_symlink() or _is_reparse_point(path):
                raise RunnerRefusal("source-tree-link-refused")
            try:
                mode = path.lstat().st_mode
            except OSError as exc:
                raise RunnerRefusal("source-tree-entry-unreadable") from exc
            if stat.S_ISDIR(mode):
                pending.append(path)
            elif not stat.S_ISREG(mode):
                raise RunnerRefusal("source-tree-special-entry-refused")
    return safe_root


def _policy_path(raw: str) -> Path:
    return PROJECT_ROOT / raw


def _match_allowed_root(path: Path, roots: tuple[str, ...], *, kind: str) -> Path:
    for raw in roots:
        root = _policy_path(raw)
        try:
            return _assert_safe_path(path, root=root, kind=kind)  # type: ignore[arg-type]
        except RunnerRefusal as exc:
            if exc.code != "path-outside-allowed-root":
                raise
    raise RunnerRefusal("path-outside-policy-roots")


def _read_json(path: Path, *, root: Path) -> dict[str, Any]:
    safe = _assert_safe_path(path, root=root, kind="file")
    try:
        value = json.loads(safe.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunnerRefusal("malformed-json") from exc
    if not isinstance(value, dict):
        raise RunnerRefusal("json-root-not-object")
    return value


def load_policy(path: Path) -> tuple[DelegationPolicy, str]:
    payload = _read_json(path, root=PROJECT_ROOT)
    try:
        policy = DelegationPolicy.model_validate(payload)
    except Exception as exc:  # pydantic errors must not leak untrusted content
        raise RunnerRefusal("invalid-delegation-policy") from exc
    expected_spec = PROJECT_ROOT / policy.authority_spec
    _assert_safe_path(expected_spec, root=PROJECT_ROOT, kind="file")
    if expected_spec.name != "spec-delegated-live-test-hil-runner.md":
        raise RunnerRefusal("wrong-delegation-authority")
    return policy, _digest(policy.model_dump(mode="json"))


def _reject_secret_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in _SECRET_KEY_FRAGMENTS):
                raise RunnerRefusal("secret-shaped-evidence-refused")
            _reject_secret_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_secret_keys(nested)


def _atomic_write_json(path: Path, payload: dict[str, Any], *, root: Path) -> None:
    _reject_secret_keys(payload)
    absolute = _assert_safe_path(path, root=root, kind="missing-ok")
    parent = absolute.parent
    parent.mkdir(parents=True, exist_ok=True)
    _assert_safe_path(parent, root=root, kind="dir")
    if absolute.exists():
        _assert_safe_path(absolute, root=root, kind="file")
    temp = parent / f".{absolute.name}.{uuid4().hex}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(temp, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, absolute)
        _fsync_directory(parent)
    finally:
        if temp.exists():
            temp.unlink()


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _write_once_json(path: Path, payload: dict[str, Any], *, root: Path) -> None:
    if path.exists():
        existing = _read_json(path, root=root)
        if existing != payload:
            raise RunnerRefusal("immutable-summary-already-exists")
        return
    _atomic_write_json(path, payload, root=root)


def _default_governed_input_roots(
    *,
    trial_id: UUID,
    input_path: Path,
    course_source_root: Path,
    policy_path: Path | None,
    authority_spec: str,
) -> tuple[dict[str, Path], dict[str, Path], dict[str, Path]]:
    roots: dict[str, Path] = {
        "input": input_path,
        "course-source": course_source_root,
    }
    if policy_path is not None:
        for label, relative in (
            ("app", "app"),
            ("config", "config"),
            ("runtime-config", "runtime/config"),
            ("state-config", "state/config"),
            ("skills", "skills"),
            ("bmad-memory", "_bmad/memory"),
        ):
            candidate = PROJECT_ROOT / relative
            if candidate.is_dir():
                roots[label] = candidate
    exclusions: dict[str, Path] = {}
    state_trial = PROJECT_ROOT / "state" / "config" / "runs" / str(trial_id)
    if "state-config" in roots:
        exclusions["state/config/runs/trial"] = state_trial
    bound_files = {
        "live-test-runner": Path(__file__),
        "delegation-authority": PROJECT_ROOT / authority_spec,
    }
    if policy_path is not None:
        bound_files["delegation-policy"] = policy_path
    return roots, exclusions, bound_files


def _write_governed_preflight_identity(
    *,
    trial_id: UUID,
    input_path: Path,
    course_source_root: Path,
    evidence_root: Path,
    policy_path: Path | None,
    authority_spec: str,
) -> tuple[Path, dict[str, Any]]:
    roots, exclusions, bound_files = _default_governed_input_roots(
        trial_id=trial_id,
        input_path=input_path,
        course_source_root=course_source_root,
        policy_path=policy_path,
        authority_spec=authority_spec,
    )
    payload = build_governed_input_identity(
        trial_id=trial_id,
        roots=roots,
        writable_exclusions=exclusions,
        bound_files=bound_files,
    )
    path = evidence_root / str(trial_id) / PREFLIGHT_IDENTITY_FILENAME
    _write_once_json(path, payload, root=evidence_root)
    return path, payload


def _write_run_output_inventory(
    *,
    trial_id: UUID,
    run_dir: Path,
    evidence_root: Path,
    state_config_run_dir: Path | None,
) -> Path:
    run_dirs = {"primary-run": run_dir}
    if state_config_run_dir is not None:
        run_dirs["state-config-run"] = state_config_run_dir
    payload = build_run_output_inventory(
        trial_id=trial_id,
        run_dirs=run_dirs,
    )
    path = evidence_root / str(trial_id) / OUTPUT_INVENTORY_FILENAME
    _atomic_write_json(path, payload, root=evidence_root)
    return path


def _write_postflight_input_comparison(
    *,
    trial_id: UUID,
    preflight: dict[str, Any],
    input_path: Path,
    course_source_root: Path,
    evidence_root: Path,
    policy_path: Path | None,
    authority_spec: str,
) -> tuple[Path, bool]:
    roots, exclusions, bound_files = _default_governed_input_roots(
        trial_id=trial_id,
        input_path=input_path,
        course_source_root=course_source_root,
        policy_path=policy_path,
        authority_spec=authority_spec,
    )
    postflight = build_governed_input_identity(
        trial_id=trial_id,
        roots=roots,
        writable_exclusions=exclusions,
        bound_files=bound_files,
    )
    return _persist_postflight_comparison(
        trial_id=trial_id,
        preflight=preflight,
        postflight=postflight,
        evidence_root=evidence_root,
    )


def _persist_postflight_comparison(
    *,
    trial_id: UUID,
    preflight: dict[str, Any],
    postflight: dict[str, Any],
    evidence_root: Path,
) -> tuple[Path, bool]:
    before_by_path = {row["path"]: row for row in preflight["files"]}
    after_by_path = {row["path"]: row for row in postflight["files"]}
    added = sorted(after_by_path.keys() - before_by_path.keys())
    removed = sorted(before_by_path.keys() - after_by_path.keys())
    changed = sorted(
        path
        for path in before_by_path.keys() & after_by_path.keys()
        if before_by_path[path] != after_by_path[path]
    )
    matches = not (added or removed or changed)
    body = {
        "schema_version": POSTFLIGHT_COMPARISON_SCHEMA,
        "trial_id": str(trial_id),
        "preflight_artifact_digest": preflight["artifact_digest"],
        "postflight_artifact_digest": postflight["artifact_digest"],
        "preflight_manifest_digest": preflight["manifest_digest"],
        "postflight_manifest_digest": postflight["manifest_digest"],
        "status": "match" if matches else "mismatch",
        "added": added,
        "removed": removed,
        "changed": changed,
    }
    payload = {**body, "artifact_digest": _digest(body)}
    path = evidence_root / str(trial_id) / POSTFLIGHT_COMPARISON_FILENAME
    _atomic_write_json(path, payload, root=evidence_root)
    return path, matches


def _rebuild_governed_identity_from_preflight(
    *, trial_id: UUID, preflight: dict[str, Any]
) -> dict[str, Any]:
    try:
        if (
            preflight.get("schema_version") != PREFLIGHT_IDENTITY_SCHEMA
            or preflight.get("trial_id") != str(trial_id)
        ):
            raise ValueError
        body = {key: value for key, value in preflight.items() if key != "artifact_digest"}
        if (
            preflight.get("manifest_digest") != _digest(preflight.get("files"))
            or preflight.get("artifact_digest") != _digest(body)
        ):
            raise ValueError
        roots = {str(row["label"]): Path(str(row["path"])) for row in preflight["roots"]}
        exclusions = {
            str(row["label"]): Path(str(row["path"]))
            for row in preflight["writable_exclusions"]
        }
        bound_files = {
            str(row["label"]): Path(str(row["path"]))
            for row in preflight["bound_files"]
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise RunnerRefusal("preflight-evidence-invalid") from exc
    rebuilt = build_governed_input_identity(
        trial_id=trial_id,
        roots=roots,
        writable_exclusions=exclusions,
        bound_files=bound_files,
    )
    return rebuilt


class EvidenceJournal:
    def __init__(
        self,
        *,
        trial_id: UUID,
        policy_digest: str,
        evidence_root: Path,
    ) -> None:
        self.trial_id = trial_id
        self.policy_digest = policy_digest
        self.root = evidence_root
        self.directory = evidence_root / str(trial_id)
        self.path = self.directory / "journal.json"
        self.summary_path = self.directory / "summary.json"
        if self.path.exists():
            self.payload = _read_json(self.path, root=evidence_root)
            if (
                self.payload.get("schema_version") != JOURNAL_SCHEMA
                or self.payload.get("trial_id") != str(trial_id)
                or self.payload.get("delegate_id") != DELEGATE_ID
                or self.payload.get("policy_digest") != policy_digest
                or not isinstance(self.payload.get("events"), list)
            ):
                raise RunnerRefusal("journal-binding-mismatch")
        else:
            self.payload = {
                "schema_version": JOURNAL_SCHEMA,
                "trial_id": str(trial_id),
                "delegate_id": DELEGATE_ID,
                "policy_digest": policy_digest,
                "created_at": _utc_now(),
                "events": [],
            }
            self._persist()

    @property
    def events(self) -> list[dict[str, Any]]:
        return self.payload["events"]

    def append(self, kind: str, **fields: Any) -> None:
        self.events.append(
            {
                "sequence": len(self.events) + 1,
                "at": _utc_now(),
                "kind": kind,
                **fields,
            }
        )
        self._persist()

    def _persist(self) -> None:
        _atomic_write_json(self.path, self.payload, root=self.root)

    def submitted_digests(self) -> set[str]:
        return {
            str(event["decision_card_digest"])
            for event in self.events
            if event.get("kind") == "submission-started" and event.get("decision_card_digest")
        }

    def pending_submission(self) -> dict[str, Any] | None:
        completed = {
            event.get("decision_card_digest")
            for event in self.events
            if event.get("kind") in {"transition-recorded", "submission-reconciled"}
        }
        for event in reversed(self.events):
            if (
                event.get("kind") == "submission-started"
                and event.get("decision_card_digest") not in completed
            ):
                return event
        return None

    def finalize(self, *, status: str, success: bool, reason: str, actions: int) -> dict[str, Any]:
        base = {
            "schema_version": SUMMARY_SCHEMA,
            "trial_id": str(self.trial_id),
            "delegate_id": DELEGATE_ID,
            "policy_digest": self.policy_digest,
            "status": status,
            "success": success,
            "reason": reason,
            "gate_actions": actions,
            "journal_path": self.path.as_posix(),
            "finished_at": _utc_now(),
        }
        summary_path = self.summary_path
        if summary_path.exists():
            existing = _read_json(summary_path, root=self.root)
            stable_keys = ("trial_id", "policy_digest", "status", "success", "reason")
            if all(existing.get(key) == base.get(key) for key in stable_keys):
                return existing
            index = 2
            while (self.directory / f"summary-{index:03d}.json").exists():
                index += 1
            summary_path = self.directory / f"summary-{index:03d}.json"
        summary = {**base, "summary_path": summary_path.as_posix()}
        _write_once_json(summary_path, summary, root=self.root)
        return summary


@contextmanager
def exclusive_trial_lock(
    run_dir: Path,
    *,
    trial_id: UUID,
    policy_digest: str,
    preflight_required: bool = False,
) -> Iterator[bool]:
    lock = run_dir / ".codex-hil-runner.lock"
    origin = run_dir / ".codex-hil-runner-origin.json"
    _assert_safe_path(run_dir, root=run_dir.parent, kind="dir")
    if lock.exists() or lock.is_symlink():
        before = lock.lstat()
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or _is_reparse_point(lock)
        ):
            raise RunnerRefusal("unsafe-trial-lock")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(lock, flags, 0o600)
    except OSError as exc:
        raise RunnerRefusal("unsafe-trial-lock") from exc
    stream = os.fdopen(descriptor, "r+b")
    acquired = False
    origin_validated = False
    try:
        opened = os.fstat(stream.fileno())
        path_state = lock.lstat()
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (path_state.st_dev, path_state.st_ino)
        ):
            raise RunnerRefusal("unsafe-trial-lock")
        if os.name == "nt":
            import msvcrt

            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except (OSError, PermissionError) as exc:
                raise RunnerRefusal("trial-lock-held") from exc
        else:
            import fcntl

            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RunnerRefusal("trial-lock-held") from exc
        acquired = True
        origin_body = {
            "schema_version": "codex-hil-runner-origin.v1",
            "trial_id": str(trial_id),
            "policy_digest": policy_digest,
            "preflight_required": preflight_required,
        }
        if origin.exists() or origin.is_symlink():
            retained_origin = _read_json(origin, root=run_dir)
            if (
                retained_origin.get("schema_version") != "codex-hil-runner-origin.v1"
                or retained_origin.get("trial_id") != str(trial_id)
                or retained_origin.get("policy_digest") != policy_digest
                or not isinstance(retained_origin.get("preflight_required"), bool)
                or (preflight_required and retained_origin["preflight_required"] is False)
            ):
                raise RunnerRefusal("trial-lock-origin-invalid")
            retained_preflight_required = retained_origin["preflight_required"]
            origin_body = retained_origin
        else:
            _write_once_json(origin, origin_body, root=run_dir)
            retained_preflight_required = preflight_required
        origin_validated = True
        body = {
            "trial_id": str(trial_id),
            "delegate_id": DELEGATE_ID,
            "policy_digest": policy_digest,
            "pid": os.getpid(),
            "acquired_at": _utc_now(),
            "preflight_required": retained_preflight_required,
        }
        serialized = (json.dumps(body, sort_keys=True) + "\n").encode("utf-8")
        stream.seek(0)
        stream.truncate()
        stream.write(serialized)
        stream.flush()
        os.fsync(stream.fileno())
        _fsync_directory(run_dir)
        yield retained_preflight_required
    finally:
        try:
            if acquired:
                try:
                    stream.seek(0)
                    current = json.loads(stream.read().decode("utf-8"))
                    path_state = lock.lstat()
                    opened = os.fstat(stream.fileno())
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    raise RunnerRefusal("trial-lock-mutated") from exc
                if (
                    not isinstance(current, dict)
                    or current.get("trial_id") != str(trial_id)
                    or current.get("policy_digest") != policy_digest
                    or (opened.st_dev, opened.st_ino) != (path_state.st_dev, path_state.st_ino)
                ):
                    raise RunnerRefusal("trial-lock-mutated")
                if origin_validated and _read_json(origin, root=run_dir) != origin_body:
                    raise RunnerRefusal("trial-lock-origin-mutated")
        finally:
            try:
                if acquired and os.name == "nt":
                    import msvcrt

                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                elif acquired:
                    import fcntl

                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            finally:
                stream.close()


def _load_envelope(trial_id: UUID, run_dir: Path) -> ProductionTrialEnvelope:
    payload = _read_json(run_dir / "run.json", root=run_dir)
    try:
        envelope = ProductionTrialEnvelope.model_validate_json(
            json.dumps(payload), context={"invariant_mode": "strict"}
        )
    except Exception as exc:
        raise RunnerRefusal("invalid-run-envelope") from exc
    if envelope.trial_id != trial_id:
        raise RunnerRefusal("trial-envelope-id-mismatch")
    return envelope


def _assert_workbook_checkpoint(trial_id: UUID, run_dir: Path) -> None:
    checkpoint = _read_json(run_dir / "checkpoint.json", root=run_dir)
    if checkpoint.get("trial_id") != str(trial_id):
        raise RunnerRefusal("checkpoint-trial-mismatch")
    run_state = checkpoint.get("run_state")
    selection = run_state.get("component_selection") if isinstance(run_state, dict) else None
    if not isinstance(selection, dict) or selection.get("workbook") is not True:
        raise RunnerRefusal("trial-not-workbook-scoped")


def _load_canonical_runtime_context(run_dir: Path) -> WorkbookBriefRuntimeContext:
    raw = _read_json(run_dir / WORKBOOK_RUNTIME_CONTEXT_FILENAME, root=run_dir)
    if raw.pop("schema_version", None) != "workbook-runtime-context.v1":
        raise RunnerRefusal("workbook-runtime-context-invalid")
    raw["run_dir"] = run_dir
    if raw.get("course_source_root") is not None:
        raw["course_source_root"] = Path(raw["course_source_root"])
    try:
        return WorkbookBriefRuntimeContext.model_validate(raw, strict=True)
    except (TypeError, ValueError) as exc:
        raise RunnerRefusal("workbook-runtime-context-invalid") from exc


def _assert_delegated_trial_scope(
    *,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    run_dir: Path,
    policy: DelegationPolicy,
) -> None:
    """Bind an attachment to a delegated production workbook test trial."""
    if envelope.preset != "production":
        raise RunnerRefusal("trial-preset-out-of-scope")
    if envelope.operator_id != DELEGATE_ID:
        raise RunnerRefusal("trial-operator-not-delegate")
    corpus = _match_allowed_root(Path(envelope.corpus_path), policy.allowed_input_roots, kind="dir")
    _assert_safe_tree(corpus)
    _assert_workbook_checkpoint(trial_id, run_dir)
    context = _load_canonical_runtime_context(run_dir)
    if context.course_source_root is None:
        raise RunnerRefusal("course-source-root-missing")
    course_root = _match_allowed_root(
        context.course_source_root, policy.allowed_input_roots, kind="dir"
    )
    _assert_safe_tree(course_root)


def _load_bound_card(trial_id: UUID, gate_id: str, run_dir: Path) -> tuple[Any, str, str]:
    path = run_dir / f"decision-card-{gate_id}.json"
    raw = _assert_safe_path(path, root=run_dir, kind="file").read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    try:
        payload = json.loads(raw.decode("utf-8"))
        card = AnyDecisionCardAdapter.validate_python(payload["card"])
        issued_at = datetime.fromisoformat(str(payload["issued_at"]).replace("Z", "+00:00"))
        nonce = str(payload["server_nonce"])
        persisted_digest = str(payload["digest"])
    except Exception as exc:
        raise RunnerRefusal("malformed-decision-card") from exc
    if card.trial_id != trial_id or card.gate_id != gate_id:
        raise RunnerRefusal("decision-card-identity-mismatch")
    if not nonce or len(persisted_digest) != 64:
        raise RunnerRefusal("decision-card-metadata-missing")
    expected = compute_decision_card_digest(
        card=card,
        trial_id=trial_id,
        issuance_timestamp=issued_at,
        server_nonce=nonce,
    )
    if expected != persisted_digest:
        raise RunnerRefusal("decision-card-digest-mismatch")
    checkpoint = _read_json(run_dir / "checkpoint.json", root=run_dir)
    if checkpoint.get("trial_id") != str(trial_id) or checkpoint.get("gate_id") != gate_id:
        raise RunnerRefusal("checkpoint-card-mismatch")
    checkpoint_path = Path(str(payload.get("checkpoint_path") or ""))
    if ".." in checkpoint_path.parts:
        raise RunnerRefusal("parent-traversal-refused")
    if _absolute_without_resolving(checkpoint_path) != _absolute_without_resolving(
        run_dir / "checkpoint.json"
    ):
        raise RunnerRefusal("decision-card-checkpoint-path-mismatch")
    return card, persisted_digest, file_digest


def _make_verdict(
    *,
    policy: DelegationPolicy,
    trial_id: UUID,
    gate_id: str,
    card: Any,
    card_digest: str,
) -> tuple[OperatorVerdict, Any | None]:
    rule = policy.gate_rules.get(gate_id)
    if rule is None:
        raise RunnerRefusal("unknown-gate")
    kwargs: dict[str, Any] = {
        "trial_id": trial_id,
        "gate_id": gate_id,
        "card_id": card.card_id,
        "operator_id": DELEGATE_ID,
        "decision_card_digest": card_digest,
    }
    selection_receipt: Any | None = None
    if rule.action == "approve":
        kwargs["verb"] = "approve"
    else:
        expected_field = _SELECTION_FIELDS.get(gate_id)
        if rule.selection_field != expected_field or expected_field is None:
            raise RunnerRefusal("selection-policy-gate-mismatch")
        if gate_id == "G2B":
            offered = getattr(card, "variant_candidates", None)
            if (
                not isinstance(offered, list)
                or not offered
                or any(not isinstance(item, str) or not item.strip() for item in offered)
                or len(set(offered)) != len(offered)
            ):
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            offered_set = set(offered)
            contexts = [
                row
                for row in getattr(card, "pick_context", [])
                if isinstance(row, dict) and row.get("kind") == "variant-options"
            ]
            if len(contexts) != 1 or not isinstance(contexts[0].get("slides"), list):
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            selections: dict[str, str] = {}
            for slide in contexts[0]["slides"]:
                if not isinstance(slide, dict):
                    raise RunnerRefusal("missing-or-ambiguous-selection-choices")
                slide_id = slide.get("slide_id")
                variants = slide.get("variants")
                if (
                    not isinstance(slide_id, str)
                    or not slide_id.strip()
                    or slide_id in selections
                    or not isinstance(variants, list)
                    or not variants
                ):
                    raise RunnerRefusal("missing-or-ambiguous-selection-choices")
                variant_ids = [
                    row.get("variant") if isinstance(row, dict) else None for row in variants
                ]
                if (
                    any(not isinstance(item, str) or not item.strip() for item in variant_ids)
                    or len(set(variant_ids)) != len(variant_ids)
                    or any(item not in offered_set for item in variant_ids)
                ):
                    raise RunnerRefusal("missing-or-ambiguous-selection-choices")
                selections[slide_id] = variant_ids[0]
            if not selections:
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            selection_receipt = selections
        else:
            candidates = getattr(card, "voice_candidates", None)
            if (
                not isinstance(candidates, list)
                or not candidates
                or any(not isinstance(item, str) or not item.strip() for item in candidates)
                or len(set(candidates)) != len(candidates)
            ):
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            selection_receipt = candidates[0]
        kwargs.update(verb="select", edit_payload={expected_field: selection_receipt})
    try:
        return OperatorVerdict(**kwargs), selection_receipt
    except Exception as exc:
        raise RunnerRefusal("delegated-verdict-invalid") from exc


def _reconcile_pending(
    journal: EvidenceJournal,
    envelope: ProductionTrialEnvelope,
    run_dir: Path,
) -> None:
    pending = journal.pending_submission()
    if pending is None:
        return
    if envelope.status == "paused-at-gate" and envelope.paused_gate == pending.get("gate_id"):
        _, current_digest, _ = _load_bound_card(
            envelope.trial_id, str(envelope.paused_gate), run_dir
        )
        if current_digest == pending.get("decision_card_digest"):
            raise RunnerRefusal("split-brain-consumed-card-still-current")
    journal.append(
        "submission-reconciled",
        decision_card_digest=pending["decision_card_digest"],
        observed_status=envelope.status,
        observed_gate=envelope.paused_gate,
    )


def _check_deadline(started_at: float, policy: DelegationPolicy) -> None:
    if time.monotonic() - started_at >= policy.budgets.max_wall_seconds:
        raise RunnerRefusal("wall-clock-budget-exhausted")


def _authoritative_resume_result(
    *,
    trial_id: UUID,
    run_dir: Path,
    returned: ProductionTrialEnvelope,
) -> ProductionTrialEnvelope:
    if not isinstance(returned, ProductionTrialEnvelope):
        raise RunnerRefusal("resume-return-envelope-invalid")
    persisted = _load_envelope(trial_id, run_dir)
    if returned.trial_id != trial_id:
        raise RunnerRefusal("resume-return-trial-mismatch")
    if returned.model_dump(mode="json") != persisted.model_dump(mode="json"):
        raise RunnerRefusal("resume-return-disk-mismatch")
    return persisted


def _assert_conformant_workbook_markdown(path: Path) -> None:
    """Refuse a present-but-nonconforming workbook MD (empty / no top-level heading)."""
    try:
        raw = _retry_transient_read(path.read_bytes)
    except OSError as exc:
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed") from exc
    first_nonblank = next((line for line in text.splitlines() if line.strip()), "")
    if not text.strip() or not first_nonblank.startswith("# "):
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")


def _assert_conformant_workbook_docx(path: Path) -> None:
    """Refuse a present-but-nonconforming workbook DOCX (not a valid OOXML zip)."""

    def _open_and_check() -> None:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
            names = set(archive.namelist())
        if "[Content_Types].xml" not in names or not any(n.startswith("word/") for n in names):
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")

    try:
        _retry_transient_read(_open_and_check)
    except zipfile.BadZipFile as exc:
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed") from exc
    except OSError as exc:
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed") from exc


_ASK_A_CITE_MARKER_RE = re.compile(r"\[(ask-a-cite-[0-9]{3})\]")
_ASK_A_REFERENCE_ENTRY_RE = re.compile(r"citation_id: `(ask-a-cite-[0-9]{3})`")
_PRESENTATION_SUPPORT_MD_SENTINEL = "This presentation-support workbook carries"
_DEEP_DIVE_HEADING = "## Deep Dive"
_DEEP_DIVE_LOSS_NOTE = "Deep Dive enrichment loss:"

# --- 39.1 glossary conformance clause (same-diff bar extension, plank 5) ---
_GLOSSARY_HEADING = "## Research Glossary"
_GLOSSARY_AUTHORITY_ABSENT_REASON = "bold-term authority absent"
_GLOSSARY_UNCOVERED_LINE = (
    "Key term from the Deep Dive. No research row in this run's pool covers "
    "it; no definition is invented."
)
# P2 (row d′ truthfulness): the state-accurate lean line for a term that a
# PRESENT pool row association-covers but degradation forced uncovered.
_GLOSSARY_UNCOVERED_DEGRADED_LINE = (
    "Enrichment was degraded this run; a research row associates with this "
    "term but was not composed."
)
_GLOSSARY_COVERAGE_RE = re.compile(
    r"Research coverage this run: ([0-9]+) of ([0-9]+) terms\."
)
_GLOSSARY_ENTRY_HEADING_RE = re.compile(r"^### (.+?)\s*$", re.MULTILINE)
_GLOSSARY_TIER_RE = re.compile(r"tier=([A-Za-z0-9_]+)")
# The glossary entry's citation idiom (``**Provenance:** `ask-a-cite-###` …``)
# is DISTINCT from the References-block idiom (``citation_id: `…```) so the
# glossary can never satisfy its own row-j resolvability claim.
_GLOSSARY_PROVENANCE_RE = re.compile(r"\*\*Provenance:\*\* `(ask-a-cite-[0-9]{3})`")
# P4: EVERY ask-a-cite token in a covered entry's body (any idiom, any line)
# must attribute to one of that entry's covering citation ids.
_ASK_A_CITE_TOKEN_RE = re.compile(r"ask-a-cite-[0-9]{3}")
_REFERENCES_HEADING = "## References"
_CITED_ENTRIES_BLOCK_HEADING = "#### Deep Dive cited entries"

# --- M-R3 LO shippability clause (closure rider; structured-channel-first) ---
_WORKBOOK_PRODUCER_SPECIALIST_ID = "workbook_producer"
_WORKBOOK_PRODUCER_NODE_ID = "07W"
# The producer's degraded-LO placeholder statement copy (composed into the
# ``## Learning Objectives`` section) and the visible loss callout it renders
# when ``lo_overlay_loss`` is populated — MD-floor witnesses ONLY; the
# persisted structured record is the primary assertion surface.
_LO_PLACEHOLDER_COPY = "objective statement unresolved"
_LO_OVERLAY_LOSS_CALLOUT = "Enrichment overlay loss:"

# --- 39.2 trends / Door-Ajar conformance clause (same-diff bar, plank 5) ---
_TRENDS_HEADING = "## Research Trends"
_TRENDS_CLAIMS_SUBHEADING = "#### Research trends"
_TRENDS_HOT_TOPICS_SUBHEADING = "#### Hot topics"
_TRENDS_REJECTED_SUBHEADING = "#### Rejected / unusable topics"
_TRENDS_ANTI_THEATER_LINE = (
    "*Bounded callout from wrangled evidence — not trend-forecasting theater.*"
)
# W-2 (defaults-drift pin): these recompute defaults are asserted EQUAL to the
# ``_act.py`` L1217 effective call defaults (``trends_inputs_from_run(run_dir)``
# with the signature defaults) by a named test — if either side drifts, the pin
# fails, so the bar's recompute authority can never silently diverge from the
# production call it stands in for.
_TRENDS_BAR_MAX_TRENDS = 5
_TRENDS_BAR_MAX_HOT_TOPICS = 3
_TRENDS_BAR_INJECTED_TOPICS: tuple[str, ...] = ()
# Rendered-line idioms of ``render_trends_markdown`` the clause parses (the
# bar re-derives claims/topics from the recompute, never from these lines).
_TRENDS_PROVENANCE_RE = re.compile(
    r"^  - \*\*Provenance:\*\* `([^`]+)` · `([^`]+)` · tier=[^\n]*?"
    r"confidence=([a-z]+)",
    re.MULTILINE,
)
_TRENDS_CLAIM_LINE_RE = re.compile(r"^- (.+)$", re.MULTILINE)
_TRENDS_TOPIC_LINE_RE = re.compile(
    r"^- \*\*(.+?)\*\* \(confidence=([a-z]+)\) — .*?"
    r"Supporting: (.*?); source_refs: (.*?)\.$",
    re.MULTILINE,
)
_TRENDS_REJECTED_LINE_RE = re.compile(r"^- \*\*(.+?)\*\* — ", re.MULTILINE)
_ASK_B_CITE_TOKEN_RE = re.compile(r"ask-b-cite-[0-9]{3,}")


def _md_section_body(text: str, heading: str) -> str | None:
    """The body of an H2 section (between ``## <heading>`` and the next H2)."""
    marker = f"\n{heading}\n"
    start = text.find(marker)
    if start == -1:
        return None
    body_start = start + len(marker)
    rest = text[body_start:]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


def _cited_entries_block(text: str) -> str:
    """P5 (row j): the ``#### Deep Dive cited entries`` block INSIDE the
    ``## References`` section — the ONLY surface a covered glossary citation
    may resolve against (never the glossary's own provenance lines, never a
    stray line elsewhere in the document)."""
    references = _md_section_body(text, _REFERENCES_HEADING)
    if references is None:
        return ""
    marker_match = re.search(
        rf"^{re.escape(_CITED_ENTRIES_BLOCK_HEADING)}.*$", references, re.MULTILINE
    )
    if marker_match is None:
        return ""
    block = references[marker_match.end() :]
    nxt = block.find("\n#### ")
    return block if nxt == -1 else block[:nxt]


def _assert_glossary_conformant_markdown(run_dir: Path, md_paths: list[Path]) -> None:
    """39.1 deliverable bar: glossary conformance, structured-artifact-first.

    Authority comes from the SAME 07W.3 contribution the deep-dive clause
    revalidates (status-dependent per AC-A3): enriched ⇒ ``result.bold_terms``;
    non-enriched with a skeleton ⇒ ``result.request.skeleton.bold_terms`` and
    EVERY entry must be uncovered-honest; no contribution / no result ⇒ the
    section must be explicitly-empty carrying the literal reason
    ``bold-term authority absent``. MD floor on presentation-support
    deliverables: exactly ONE glossary section + ONE coverage line (P9,
    counted, not first-match), headword-identity association EXACT (order +
    byte-exact — rejects mangled title-derived headwords, missing entries,
    orphan entries), reconciled coverage counts (a present authority with zero
    terms renders the honest "0 of 0" line — P1), uncovered entries carry
    EXACTLY the one state-accurate honest line and NOTHING else (P2/P3: the
    degraded-association line when a present pool row associates but
    degradation forced uncovered, the plain line otherwise; any extra body is
    a fabricated definition ⇒ REJECT), covered entries cite only pool rows
    that association-cover the term with the row's tier VERBATIM (negative
    pin v) and every ask-a-cite token in a covered body attributes to one of
    that entry's covering citation ids (P4), and every covered citation_id
    resolves into the cited-entries block INSIDE ``## References`` (matrix
    row j, P5). A presentation-support MD carrying the glossary section with
    NO ``run.json`` structured authority is REJECTED (P15 — mirror the R3
    stray-marker rule; never a silent skip). Test-harness-side only;
    production runtime is untouched.
    """
    text_by_path: dict[Path, str] = {}
    for path in md_paths:
        try:
            text = _retry_transient_read(path.read_bytes).decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            ) from exc
        # Platform-newline normalization (write_text translates \n -> \r\n on
        # Windows); section/heading anchors below are LF-based.
        text_by_path[path] = text.replace("\r\n", "\n")
    if not (run_dir / "run.json").is_file():
        # P15: a presentation-support deliverable carrying a Research Glossary
        # section with no structured authority behind it is a refusal —
        # mirror the R3 stray-marker rule, never a silent skip.
        for text in text_by_path.values():
            if (
                _PRESENTATION_SUPPORT_MD_SENTINEL in text
                and _GLOSSARY_HEADING in text
            ):
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
        return
    try:
        from app.marcus.lesson_plan.deep_dive_enrichment import (  # noqa: PLC0415
            load_workbook_review_contribution,
        )

        contribution = load_workbook_review_contribution(run_dir)
    except Exception as exc:
        raise RunnerRefusal(
            "workbook-deliverable-nonconforming-despite-completed"
        ) from exc
    result = contribution.deep_dive_enrichment if contribution is not None else None
    for text in text_by_path.values():
        if _PRESENTATION_SUPPORT_MD_SENTINEL not in text:
            continue  # legacy-profile deliverable: 39.1 clause does not apply
        # P9 singularity: exactly ONE glossary section heading (counted).
        if len(re.findall(rf"(?m)^{re.escape(_GLOSSARY_HEADING)}\s*$", text)) != 1:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        section = _md_section_body(text, _GLOSSARY_HEADING)
        if section is None:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        if result is None:
            # Matrix row d: explicitly-empty with the literal reason — and no
            # entries / citations may masquerade under an absent authority.
            if (
                _GLOSSARY_AUTHORITY_ABSENT_REASON not in section
                or _GLOSSARY_ENTRY_HEADING_RE.search(section)
                or "ask-a-cite-" in section
            ):
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
            continue
        enriched = result.status == "enriched"
        expected_terms = [
            marker.term
            for marker in (
                result.bold_terms if enriched else result.request.skeleton.bold_terms
            )
        ]
        rows_by_id = {row.citation_id: row for row in result.request.pool_rows}
        headwords = _GLOSSARY_ENTRY_HEADING_RE.findall(section)
        # Headword-identity association: EXACT (missing entry / orphan entry /
        # mangled title-derived headword / reorder all REJECT).
        if headwords != expected_terms:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        # P9 singularity: exactly ONE coverage line inside the section
        # (counted, not first-match). P1: zero terms reconcile as "0 of 0".
        coverage_matches = _GLOSSARY_COVERAGE_RE.findall(section)
        if len(coverage_matches) != 1:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        expected_covered = {
            term
            for term in expected_terms
            if enriched
            and any(term in row.supports_bold_terms for row in rows_by_id.values())
        }
        # P2: a degraded (non-enriched) authority forces every term uncovered;
        # a term a PRESENT pool row association-covers must carry the
        # state-accurate degraded line, a genuinely-uncovered term the plain
        # line.
        degraded_association_terms = (
            set()
            if enriched
            else {
                term
                for term in expected_terms
                if any(term in row.supports_bold_terms for row in rows_by_id.values())
            }
        )
        if (
            int(coverage_matches[0][0]) != len(expected_covered)
            or int(coverage_matches[0][1]) != len(expected_terms)
        ):
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        # Per-entry checks over the section split by ### headings.
        chunks = _GLOSSARY_ENTRY_HEADING_RE.split(section)
        # chunks = [lead, term1, body1, term2, body2, ...]
        entry_bodies = dict(zip(chunks[1::2], chunks[2::2], strict=True))
        covered_citation_ids: set[str] = set()
        for term, body in entry_bodies.items():
            cited = _GLOSSARY_PROVENANCE_RE.findall(body)
            if term not in expected_covered:
                # J-1 lean uncovered honesty, STRUCTURAL (P3): the entry body
                # is EXACTLY the one permitted state-accurate line — nothing
                # else may ride an uncovered term (no citation / tier /
                # capability note / appended fabricated definition).
                expected_line = (
                    _GLOSSARY_UNCOVERED_DEGRADED_LINE
                    if term in degraded_association_terms
                    else _GLOSSARY_UNCOVERED_LINE
                )
                body_lines = [line for line in body.splitlines() if line.strip()]
                if body_lines != [expected_line]:
                    raise RunnerRefusal(
                        "workbook-deliverable-nonconforming-despite-completed"
                    )
                continue
            if not cited:
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
            for line in body.splitlines():
                line_ids = _GLOSSARY_PROVENANCE_RE.findall(line)
                if not line_ids:
                    continue
                for citation_id in line_ids:
                    row = rows_by_id.get(citation_id)
                    # Citation must resolve to a pool row that association-
                    # covers THIS term.
                    if row is None or term not in row.supports_bold_terms:
                        raise RunnerRefusal(
                            "workbook-deliverable-nonconforming-despite-completed"
                        )
                    # Tier verbatim (negative pin v): the rendered tier token
                    # on the citation's provenance line equals the row's.
                    tier_match = _GLOSSARY_TIER_RE.search(line)
                    if (
                        tier_match is None
                        or tier_match.group(1) != row.evidence_hierarchy_tier
                    ):
                        raise RunnerRefusal(
                            "workbook-deliverable-nonconforming-despite-completed"
                        )
                    covered_citation_ids.add(citation_id)
            # P4 attribution sweep: EVERY ask-a-cite token anywhere in THIS
            # covered entry's body (any idiom, provenance line or prose) must
            # be one of THIS entry's covering citation ids validated above —
            # another entry's id does not attribute here.
            if not set(_ASK_A_CITE_TOKEN_RE.findall(body)) <= set(cited):
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
        # Matrix row j (P5): every covered citation_id resolves into the
        # cited-entries block INSIDE ``## References`` (AC-A9 seam) — the
        # glossary's own provenance lines must never satisfy their own
        # resolvability claim, and a reference line outside that block does
        # not count.
        reference_ids = set(_ASK_A_REFERENCE_ENTRY_RE.findall(_cited_entries_block(text)))
        if not covered_citation_ids <= reference_ids:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")


def _assert_lo_overlay_conformant(run_dir: Path, md_paths: list[Path]) -> None:
    """M-R3 LO shippability bar: degraded Learning Objectives never ship.

    STRUCTURED channel first (Amelia F2, closure record): the producer's
    ``lo_overlay_loss`` record on the persisted 07W ``workbook_producer``
    contribution in ``run.json`` is the assertion surface — a present record
    with ``unresolved_count > 0`` (or malformed) REFUSES the completed
    deliverable, naming the unresolved objectives; the placeholder prose is
    never the primary witness. MD floor (P15/R3 mirror) on
    presentation-support deliverables: the ``Enrichment overlay loss:``
    callout can only be minted by a populated record, so a callout with no
    record backing it refuses in EVERY branch; the placeholder copy
    (``objective statement unresolved``) while the persisted contribution
    carries a null/clean record is a prose/structured desync ⇒ REFUSE. Clean
    MD + absent/clean record = pass. A run with NO persisted 07W contribution
    (harness rig / legacy stub) keeps R3's tolerance for the by-design
    card-less degrade — the callout floor still applies. Test-harness-side
    only; production runtime is untouched.
    """
    placeholder_seen = False
    callout_seen = False
    for path in md_paths:
        try:
            text = _retry_transient_read(path.read_bytes).decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            ) from exc
        if _PRESENTATION_SUPPORT_MD_SENTINEL not in text:
            continue  # legacy-profile deliverable: M-R3 clause does not apply
        placeholder_seen = placeholder_seen or _LO_PLACEHOLDER_COPY in text
        callout_seen = callout_seen or _LO_OVERLAY_LOSS_CALLOUT in text
    if not (run_dir / "run.json").is_file():
        # No structured authority at all: a loss callout is a fabricated
        # claim (never a silent skip; P15 mirror).
        if callout_seen:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        return
    try:
        from app.marcus.lesson_plan.workbook_enrichment import (  # noqa: PLC0415
            load_run_envelope,
        )

        envelope = load_run_envelope(run_dir)
    except Exception as exc:
        raise RunnerRefusal(
            "workbook-deliverable-nonconforming-despite-completed"
        ) from exc
    contribution = (
        envelope.get_contribution(
            _WORKBOOK_PRODUCER_SPECIALIST_ID, node_id=_WORKBOOK_PRODUCER_NODE_ID
        )
        if envelope is not None
        else None
    )
    if contribution is None:
        # R3-style tolerance: no persisted 07W contribution (rig / legacy) —
        # but a loss callout no record can back still refuses.
        if callout_seen:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        return
    output = contribution.output if isinstance(contribution.output, dict) else {}
    workbook_refs = output.get("workbook")
    loss = (
        workbook_refs.get("lo_overlay_loss")
        if isinstance(workbook_refs, dict)
        else None
    )
    if loss is not None:
        # Structured channel: a persisted loss record must be well-formed and
        # zero-loss to ship; unresolved objectives refuse BY NAME.
        unresolved = loss.get("unresolved_count") if isinstance(loss, dict) else None
        if (
            not isinstance(unresolved, int)
            or isinstance(unresolved, bool)
            or unresolved > 0
        ):
            refusal = RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            )
            objectives = (
                loss.get("unresolved_objectives") if isinstance(loss, dict) else None
            )
            if isinstance(objectives, list) and objectives:
                refusal.add_note(
                    "unresolved learning objectives: "
                    + ", ".join(str(objective) for objective in objectives)
                )
            raise refusal
    if placeholder_seen or callout_seen:
        # Prose/structured desync: the deliverable claims an LO degrade the
        # persisted record does not back (record absent or clean).
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")


def _assert_exercise_composition_conformant(run_dir: Path, md_paths: list[Path]) -> None:
    """39.1b deliverable bar: exercise-composition clause, structured-first.

    The producer's persisted ``exercise_composition`` receipt +
    ``exercise_overlay_loss`` record on the 07W ``workbook_producer``
    contribution in ``run.json`` are the primary assertion surface; the MD is
    the conformance floor. Asserts (AC 8): (i) the per-unit provenance group
    labels ("Practice" / "Course Check — drawn from this course's own
    assessments") are present whenever the corresponding origin class has
    items; (ii) any collateral trim is accompanied by a structured
    ``exercise_overlay_loss`` record that matches the receipt tally (silent
    trim = REJECT); (iii) overlay-never-trimmed holds — every course-check id
    the receipt carries must render (an overlay item absent from the render =
    REJECT). MD floor in EVERY branch: an ``Exercise overlay loss:`` callout
    no structured record backs is a fabricated claim ⇒ REFUSE; a populated
    record whose callout is missing is a prose/structured desync ⇒ REFUSE.
    A run with no persisted receipt (pre-39.1b shape / harness rig) keeps the
    R3-style tolerance — the callout floor still applies. Test-harness-side
    only; production runtime is untouched.
    """
    from app.marcus.lesson_plan.workbook_producer import (  # noqa: PLC0415
        COURSE_CHECK_GROUP_LABEL,
        EXERCISE_OVERLAY_LOSS_CALLOUT,
        PRACTICE_GROUP_LABEL,
    )

    texts: list[str] = []
    for path in md_paths:
        try:
            texts.append(_retry_transient_read(path.read_bytes).decode("utf-8"))
        except (OSError, UnicodeError) as exc:
            raise RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            ) from exc
    callout_seen = any(EXERCISE_OVERLAY_LOSS_CALLOUT in text for text in texts)

    def _refuse() -> None:
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")

    if not (run_dir / "run.json").is_file():
        if callout_seen:
            _refuse()  # a callout can only be minted by a populated record
        return
    try:
        from app.marcus.lesson_plan.workbook_enrichment import (  # noqa: PLC0415
            load_run_envelope,
        )

        envelope = load_run_envelope(run_dir)
    except Exception as exc:
        raise RunnerRefusal(
            "workbook-deliverable-nonconforming-despite-completed"
        ) from exc
    contribution = (
        envelope.get_contribution(
            _WORKBOOK_PRODUCER_SPECIALIST_ID, node_id=_WORKBOOK_PRODUCER_NODE_ID
        )
        if envelope is not None
        else None
    )
    output = (
        contribution.output
        if contribution is not None and isinstance(contribution.output, dict)
        else {}
    )
    workbook_refs = output.get("workbook")
    refs = workbook_refs if isinstance(workbook_refs, dict) else {}
    receipt = refs.get("exercise_composition")
    loss = refs.get("exercise_overlay_loss")
    if receipt is None:
        # R3-style tolerance: pre-39.1b persisted shape (or rig) makes no
        # composition claim — but a loss record/callout with no receipt to
        # back it is a half-written claim, never a silent pass.
        if callout_seen or loss is not None:
            _refuse()
        return
    # Receipt well-formedness (a malformed receipt is a refusal, not a skip).
    sections = receipt.get("sections") if isinstance(receipt, dict) else None
    trimmed_count = (
        receipt.get("collateral_trimmed_count") if isinstance(receipt, dict) else None
    )
    if (
        not isinstance(sections, list)
        or not isinstance(trimmed_count, int)
        or isinstance(trimmed_count, bool)
        or trimmed_count < 0
    ):
        _refuse()
    # (ii) trim <-> loss-record consistency: silent trim = REJECT.
    loss_ids: list | None = None
    if trimmed_count > 0:
        loss_trimmed = loss.get("trimmed_count") if isinstance(loss, dict) else None
        loss_ids = (
            loss.get("trimmed_exercise_ids") if isinstance(loss, dict) else None
        )
        if (
            loss_trimmed != trimmed_count
            or not isinstance(loss_ids, list)
            or len(loss_ids) != trimmed_count
        ):
            _refuse()
    elif loss is not None:
        _refuse()  # a loss record with a zero-trim receipt is a desync
    # (ii-independent, T4 F2): the receipt's trim tally is producer-authored
    # alongside the loss record, so tally⇔loss alone cannot catch a cap bug
    # that trims WITHOUT recording. Irene's collateral blueprint on run.json
    # is the independent authority: kept Practice ids ∪ trimmed ids must
    # EQUAL the blueprint's authored collateral exercise ids. Tolerant when
    # the blueprint is absent (rig / declaration none) — never when it
    # contradicts the receipt.
    try:
        from app.marcus.lesson_plan.workbook_enrichment import (  # noqa: PLC0415
            collateral_from_run,
        )

        blueprint = collateral_from_run(run_dir)
    except Exception:
        blueprint = None
    if isinstance(blueprint, dict) and blueprint.get("declaration") == "present":
        workbook = blueprint.get("workbook")
        blueprint_sections = (
            workbook.get("sections") if isinstance(workbook, dict) else None
        )
        if isinstance(blueprint_sections, list) and blueprint_sections:
            authored_ids = {
                str(exercise.get("exercise_id"))
                for row in blueprint_sections
                if isinstance(row, dict)
                for exercise in (row.get("exercises") or [])
                if isinstance(exercise, dict) and exercise.get("exercise_id")
            }
            receipt_practice_ids = {
                str(exercise_id)
                for row in sections
                if isinstance(row, dict)
                for exercise_id in (
                    row.get("practice") if isinstance(row.get("practice"), list) else []
                )
            }
            trimmed_ids = {str(t) for t in loss_ids} if loss_ids else set()
            if receipt_practice_ids & trimmed_ids:
                _refuse()  # an id cannot be both kept and trimmed
            if receipt_practice_ids | trimmed_ids != authored_ids:
                _refuse()  # kept ∪ trimmed must account for EVERY authored id
    for text in texts:
        # MD floor both directions: callout ⇔ populated record.
        if (EXERCISE_OVERLAY_LOSS_CALLOUT in text) != (loss is not None):
            _refuse()
        # (ii-render): a trimmed id still rendering means the recorded trim
        # was not actually applied (record/prose desync).
        for trimmed_id in loss_ids or []:
            if f"#### Exercise `{trimmed_id}`" in text:
                _refuse()
        for row in sections:
            if not isinstance(row, dict):
                _refuse()
            section_id = row.get("section_id")
            practice = row.get("practice")
            course_check = row.get("course_check")
            if (
                not isinstance(section_id, str)
                or not isinstance(practice, list)
                or not isinstance(course_check, list)
            ):
                _refuse()
            # (i) origin-labeled group headings present when the class has
            # items — required in BOTH the Exercises block and its Answer Key
            # mirror (T4 F9: the render emits the identical heading in each,
            # so a single occurrence means one block lost its label).
            if practice and (
                text.count(f"### {PRACTICE_GROUP_LABEL} — section `{section_id}`") < 2
            ):
                _refuse()
            if course_check and (
                text.count(
                    f"### {COURSE_CHECK_GROUP_LABEL} — section `{section_id}`"
                )
                < 2
            ):
                _refuse()
            # (iii) overlay-never-trimmed: every course-check id renders; and
            # (T4 F10) every kept Practice id renders too — receipt/prose
            # desync refuses on BOTH origin classes.
            for exercise_id in (*practice, *course_check):
                if f"#### Exercise `{exercise_id}`" not in text:
                    _refuse()


def _assert_trends_door_ajar_conformant(run_dir: Path, md_paths: list[Path]) -> None:
    """39.2 deliverable bar: trends / Door-Ajar conformance, recompute-first.

    Substrate-forced difference from the glossary/exercise idiom, declared
    honestly: NO trends receipt is persisted on the 07W contribution
    (``_sidecar_refs``), and the projection is a pure deterministic function
    of ``run.json`` — so the structured authority is the deterministic
    RECOMPUTE: ``resolve_for_hot_topics(run_dir)`` →
    ``project_trends_from_packet(packet)`` with the ``_act.py`` production
    defaults (``max_trends=5``, ``max_hot_topics=3``, no injected topics;
    the W-2 pin asserts that equality), compared against the rendered
    ``## Research Trends`` section. Floor (presentation-support sentinel MDs
    only, mirroring the 39.1 scope — legacy-profile deliverables are out of
    clause scope, M-4): exactly ONE section per deliverable (counted, P9);
    recompute NOT usable ⇒ the section is the explicit-empty render (the
    recomputed ``empty_reason`` verbatim inside ``*(...)*``; NO claim list,
    NO usable hot-topic lines, NO ``ask-b-cite-`` tokens, NO ``Provenance:``
    lines, NO DOIs; the Rejected/unusable honesty block is permitted);
    recompute usable ⇒ rendered claims/topics reconcile EXACTLY with the
    recompute (claim texts, citation_id/source_ref/confidence order,
    topic/supporting/source_refs order — a missing rendered claim (M-1
    silent-loss direction), an extra/fabricated claim, or a reordered/
    rewritten confidence label all REJECT), every rendered citation_id /
    source_ref / supporting id resolves into the recomputed packet entries
    (AC 5 anti-theater formulation), the anti-theater sentinel line is
    present, and unusable topics appear ONLY under the Rejected block.
    No ``run.json`` ⇒ a presentation-support MD whose section carries any
    grounded-claim content (claim list / ``ask-b-cite-`` tokens /
    ``Provenance:`` lines) is REJECTED (P15 mirror: no structured authority
    may back no claims); an explicit-empty section is tolerated (R3-style
    tolerance — the section renders in every profile/run shape, so bare
    presence is never the refusal trigger, unlike the glossary heading).

    Residual named honestly (M-6): bar-time and render-time share
    ``project_trends_from_packet`` — a bug INSIDE that pure function is
    invisible to this recompute comparison; it is covered by the
    deterministic unit pins (39.2 ACs 3–5), not by this bar.
    Test-harness-side only; production runtime is untouched.
    """

    def _refuse() -> None:
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")

    text_by_path: dict[Path, str] = {}
    for path in md_paths:
        try:
            text = _retry_transient_read(path.read_bytes).decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            ) from exc
        # LF-normalize (write_text translates \n -> \r\n on Windows); the
        # section/heading anchors below are LF-based.
        text_by_path[path] = text.replace("\r\n", "\n")

    if not (run_dir / "run.json").is_file():
        # P15 mirror: grounded-claim content with no structured authority
        # behind it refuses; a bare / explicit-empty section is tolerated.
        for text in text_by_path.values():
            if _PRESENTATION_SUPPORT_MD_SENTINEL not in text:
                continue
            section = _md_section_body(text, _TRENDS_HEADING)
            if section is None:
                continue
            if (
                _TRENDS_CLAIMS_SUBHEADING in section
                or "**Provenance:**" in section
                or _ASK_B_CITE_TOKEN_RE.search(section)
            ):
                _refuse()
        return

    try:
        from app.marcus.lesson_plan.research_packet import (  # noqa: PLC0415
            resolve_for_hot_topics,
        )
        from app.marcus.lesson_plan.trends_projection import (  # noqa: PLC0415
            project_trends_from_packet,
        )

        packet = resolve_for_hot_topics(run_dir)
        brief = project_trends_from_packet(
            packet,
            max_trends=_TRENDS_BAR_MAX_TRENDS,
            max_hot_topics=_TRENDS_BAR_MAX_HOT_TOPICS,
            injected_topics=_TRENDS_BAR_INJECTED_TOPICS,
        )
    except Exception as exc:
        # A forged/malformed Ask-B contribution (ResearchPacketShapeError) or
        # corrupt envelope fails the recompute — reject, never trust prose.
        raise RunnerRefusal(
            "workbook-deliverable-nonconforming-despite-completed"
        ) from exc

    packet_citation_ids = {str(entry.get("citation_id")) for entry in packet.entries}
    packet_source_refs = {str(entry.get("source_ref")) for entry in packet.entries}
    expected_claims = [claim.claim_text for claim in brief.trends]
    expected_provenance = [
        (claim.citation_id, claim.source_ref, claim.confidence)
        for claim in brief.trends
    ]
    expected_topics = [
        (topic.topic, topic.confidence, topic.supporting_citation_ids, topic.source_refs)
        for topic in brief.hot_topics
        if topic.confidence != "unusable"
    ]
    expected_rejected = [
        topic.topic for topic in brief.hot_topics if topic.confidence == "unusable"
    ]

    for text in text_by_path.values():
        if _PRESENTATION_SUPPORT_MD_SENTINEL not in text:
            continue  # legacy-profile deliverable: 39.2 clause does not apply (M-4)
        # P9 singularity: exactly ONE Research Trends section (counted).
        if len(re.findall(rf"(?m)^{re.escape(_TRENDS_HEADING)}\s*$", text)) != 1:
            _refuse()
        section = _md_section_body(text, _TRENDS_HEADING)
        if section is None:
            _refuse()
            continue
        if not brief.usable:
            # Explicit-empty render: the recomputed reason verbatim, and no
            # grounded/fabricated content of any kind (Rejected block allowed).
            if brief.empty_reason is None or f"*({brief.empty_reason})*" not in section:
                _refuse()
            if (
                _TRENDS_CLAIMS_SUBHEADING in section
                or _TRENDS_TOPIC_LINE_RE.search(section)
                or "**Provenance:**" in section
                or _ASK_B_CITE_TOKEN_RE.search(section)
                or "https://doi.org/" in section
            ):
                _refuse()
            continue
        # Usable branch: split into the renderer's fixed subregion order.
        claims_at = section.find(_TRENDS_CLAIMS_SUBHEADING)
        topics_at = section.find(_TRENDS_HOT_TOPICS_SUBHEADING)
        rejected_at = section.find(_TRENDS_REJECTED_SUBHEADING)
        if claims_at == -1 or topics_at == -1 or topics_at < claims_at:
            _refuse()
        if rejected_at != -1 and rejected_at < topics_at:
            _refuse()
        topics_end = rejected_at if rejected_at != -1 else len(section)
        claims_region = section[claims_at:topics_at]
        topics_region = section[topics_at:topics_end]
        rejected_region = section[rejected_at:] if rejected_at != -1 else ""
        if _TRENDS_ANTI_THEATER_LINE not in topics_region:
            _refuse()
        # Trend claims reconcile exactly (order + text + provenance triple).
        rendered_claims = _TRENDS_CLAIM_LINE_RE.findall(claims_region)
        rendered_provenance = _TRENDS_PROVENANCE_RE.findall(claims_region)
        if rendered_claims != expected_claims:
            _refuse()
        if [tuple(row) for row in rendered_provenance] != expected_provenance:
            _refuse()
        # Usable hot topics reconcile exactly; unusable never renders here.
        rendered_topics = [
            (
                match[0],
                match[1],
                tuple(re.findall(r"`([^`]+)`", match[2])),
                tuple(re.findall(r"`([^`]+)`", match[3])),
            )
            for match in _TRENDS_TOPIC_LINE_RE.findall(topics_region)
        ]
        if rendered_topics != expected_topics:
            _refuse()
        if any(confidence == "unusable" for _, confidence, _, _ in rendered_topics):
            _refuse()
        # Rejected block reconciles (production defaults inject nothing, so a
        # populated Rejected block with an empty recompute is a desync).
        if _TRENDS_REJECTED_LINE_RE.findall(rejected_region) != expected_rejected:
            _refuse()
        # AC 5 packet-membership: every rendered claim/topic is backed by a
        # packet row — anything unbacked is fabricated ⇒ REJECT.
        for citation_id, source_ref, _confidence in rendered_provenance:
            if citation_id not in packet_citation_ids:
                _refuse()
            if source_ref not in packet_source_refs:
                _refuse()
        for _topic, _confidence, supporting_ids, source_refs in rendered_topics:
            if not set(supporting_ids) <= packet_citation_ids:
                _refuse()
            if not set(source_refs) <= packet_source_refs:
                _refuse()


def _assert_deep_dive_conformant_markdown(run_dir: Path, md_paths: list[Path]) -> None:
    """37.2b deliverable bar: deep-dive conformance, structured-artifact-first.

    The 07W.3 contribution + gate receipt from ``run.json`` are the primary
    assertion surface (Amelia-F2 idiom): the strict contract revalidation
    (constructed-model gate recompute) rejects phantom-citation and
    enriched-with-zero-citations mutants before any prose grep. The MD check is
    the minimal floor: an enriched claim requires the ``## Deep Dive`` heading,
    at least one inline ``ask-a-cite-`` marker, and every marker resolving to a
    rendered reference entry; a degraded claim requires the honest typed-loss
    note and ZERO ``ask-a-cite-`` markers (amendment M4).

    R3: the M4 stray-marker scan runs in EVERY branch — ``run.json`` absent,
    contribution absent (legacy stub / pre-37.2b), and degraded alike: an
    inline ``ask-a-cite-`` marker without an activated ENRICHED contribution is
    always a refusal (a marker can only be minted by cited enrichment).
    Test-harness-side only; production runtime is untouched.
    """
    text_by_path: dict[Path, str] = {}
    markers_by_path: dict[Path, set[str]] = {}
    for path in md_paths:
        try:
            text = _retry_transient_read(path.read_bytes).decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            ) from exc
        text_by_path[path] = text
        markers_by_path[path] = set(_ASK_A_CITE_MARKER_RE.findall(text))

    def _refuse_any_marker() -> None:
        if any(markers_by_path.values()):
            raise RunnerRefusal(
                "workbook-deliverable-nonconforming-despite-completed"
            )

    if not (run_dir / "run.json").is_file():
        _refuse_any_marker()  # R3 branch: run.json absent
        return
    try:
        from app.marcus.lesson_plan.deep_dive_enrichment import (  # noqa: PLC0415
            load_workbook_review_contribution,
        )

        contribution = load_workbook_review_contribution(run_dir)
    except Exception as exc:
        # A present-but-nonconforming activated contribution (phantom citation,
        # enriched-status-with-zero-citations, digest mismatch) fails strict
        # revalidation here — reject, never trust the prose.
        raise RunnerRefusal(
            "workbook-deliverable-nonconforming-despite-completed"
        ) from exc
    if contribution is None:
        # R3 branch: legacy stub / pre-37.2b run — the prior bar is otherwise
        # unchanged, but a stray marker still refuses.
        _refuse_any_marker()
        return
    result = contribution.deep_dive_enrichment
    enriched = result is not None and result.status == "enriched"
    if enriched and (
        result.gate.status != "pass" or not result.gate.used_citation_ids
    ):
        raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
    if not enriched:
        _refuse_any_marker()  # R3 branch: contribution degraded / not authored (M4)
    for path in md_paths:
        text = text_by_path[path]
        markers = markers_by_path[path]
        if enriched:
            if _DEEP_DIVE_HEADING not in text or not markers:
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
            if not markers <= set(result.gate.used_citation_ids):
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
            rendered_reference_ids = set(_ASK_A_REFERENCE_ENTRY_RE.findall(text))
            if not markers <= rendered_reference_ids:
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )
        else:
            # Degraded / not-run: the honest note is mandatory on the
            # presentation-support deliverable (stray markers already refused
            # above in every branch).
            if _PRESENTATION_SUPPORT_MD_SENTINEL in text and (
                _DEEP_DIVE_HEADING not in text or _DEEP_DIVE_LOSS_NOTE not in text
            ):
                raise RunnerRefusal(
                    "workbook-deliverable-nonconforming-despite-completed"
                )


def _assert_completed_workbook_deliverable(trial_id: UUID, run_dir: Path) -> None:
    """Kill the ``status == completed`` false-green: prove a real workbook was emitted.

    ``status == completed`` alone NEVER asserted a deliverable — a silent
    specialist-budget skip of the terminal 07W band could reach ``completed`` with
    a missing / empty workbook and still report success. Before finalising
    ``success=True`` on a completed run, assert an MD+DOCX pair is present in the
    freshly built output inventory under ``<run_dir>/exports/workbooks/`` (the
    producer's output root; trial-scoped by ``run_dir``) and that each file is
    non-empty and basically conformant (MD carries a top-level heading; DOCX is a
    valid OOXML zip). This is a TEST-HARNESS-side assertion only — it never changes
    production runtime behaviour. Presence + basic conformance is the priority that
    kills the false-green; full replay / reload-equality is a deferred follow-on.
    """
    inventory = build_run_output_inventory(trial_id=trial_id, run_dir=run_dir)
    md_by_stem: dict[str, str] = {}
    docx_by_stem: dict[str, str] = {}
    for row in inventory["files"]:
        coordinate = str(row["path"])
        if not coordinate.startswith(_WORKBOOK_EXPORT_PREFIX):
            continue
        if int(row["size"]) <= 0:
            raise RunnerRefusal("workbook-deliverable-nonconforming-despite-completed")
        if coordinate.endswith(".md"):
            md_by_stem[coordinate[: -len(".md")]] = coordinate
        elif coordinate.endswith(".docx"):
            docx_by_stem[coordinate[: -len(".docx")]] = coordinate
    paired = sorted(set(md_by_stem) & set(docx_by_stem))
    if not paired:
        raise RunnerRefusal("workbook-deliverable-missing-despite-completed")
    for stem in paired:
        _assert_conformant_workbook_markdown(run_dir / md_by_stem[stem])
        _assert_conformant_workbook_docx(run_dir / docx_by_stem[stem])
    # 37.2b: deep-dive conformance bar (structured artifacts first, then the
    # minimal MD floor) — same-diff extension per protocol plank 5.
    _assert_deep_dive_conformant_markdown(
        run_dir, [run_dir / md_by_stem[stem] for stem in paired]
    )
    # 39.1: glossary conformance clause (same-diff extension, plank 5) —
    # status-dependent bold-term authority, headword-identity association,
    # uncovered honesty, tier-verbatim, citation resolvability.
    _assert_glossary_conformant_markdown(
        run_dir, [run_dir / md_by_stem[stem] for stem in paired]
    )
    # M-R3 closure rider: LO shippability bar — a completed presentation-
    # support workbook whose Learning Objectives degraded (the producer's
    # persisted ``lo_overlay_loss`` record on the 07W contribution, structured
    # channel first) is REFUSED; prose desync is the MD floor, never the
    # primary witness.
    _assert_lo_overlay_conformant(
        run_dir, [run_dir / md_by_stem[stem] for stem in paired]
    )
    # 39.1b: exercise-composition clause (same-diff extension, plank 5) —
    # origin-labeled groups, trim ⇔ exercise_overlay_loss record consistency,
    # overlay-never-trimmed; structured receipt first, MD floor second.
    _assert_exercise_composition_conformant(
        run_dir, [run_dir / md_by_stem[stem] for stem in paired]
    )
    # 39.2: trends / Door-Ajar clause (same-diff extension, plank 5) —
    # deterministic-recompute authority off run.json (no persisted trends
    # receipt), presentation-support MD floor, conforming-empty accepted.
    _assert_trends_door_ajar_conformant(
        run_dir, [run_dir / md_by_stem[stem] for stem in paired]
    )
    # Spine tail (39-2 mirrored rider): 40-1 (cover producer) appends its
    # clause AFTER the 39.2 trends clause above — keep this the tail until then.


def _drive_paused_trial_impl(
    *,
    trial_id: UUID,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    resume_fn: Callable[..., ProductionTrialEnvelope] = resume_production_trial,
    started_at: float,
) -> dict[str, Any]:
    run_dir = runs_root / str(trial_id)
    journal = EvidenceJournal(
        trial_id=trial_id, policy_digest=policy_digest, evidence_root=evidence_root
    )
    actions = sum(event.get("kind") == "submission-started" for event in journal.events)
    envelope = _load_envelope(trial_id, run_dir)
    _assert_delegated_trial_scope(
        trial_id=trial_id,
        envelope=envelope,
        run_dir=run_dir,
        policy=policy,
    )
    _reconcile_pending(journal, envelope, run_dir)
    while True:
        _check_deadline(started_at, policy)
        if envelope.status == policy.terminal_success_state:
            envelope = _load_envelope(trial_id, run_dir)
            _assert_delegated_trial_scope(
                trial_id=trial_id,
                envelope=envelope,
                run_dir=run_dir,
                policy=policy,
            )
            _check_deadline(started_at, policy)
            if envelope.status != policy.terminal_success_state:
                raise RunnerRefusal("terminal-state-changed-before-success")
            # A ``completed`` status is NOT sufficient for success: assert the
            # workbook deliverable is actually real (present + basically conformant)
            # so a missing/empty/malformed workbook fails loud instead of reporting
            # a false-green. Test-harness-side only; production runtime is untouched.
            _assert_completed_workbook_deliverable(trial_id, run_dir)
            return journal.finalize(
                status=envelope.status, success=True, reason="completed", actions=actions
            )
        if envelope.status in policy.stop_states:
            return journal.finalize(
                status=envelope.status,
                success=False,
                reason=f"stopped-{envelope.status}",
                actions=actions,
            )
        if envelope.status != "paused-at-gate" or envelope.paused_gate is None:
            raise RunnerRefusal("unknown-run-state")
        if actions >= policy.budgets.max_gate_actions:
            raise RunnerRefusal("gate-action-budget-exhausted")
        gate_id = str(envelope.paused_gate)
        card, card_digest, card_file_digest = _load_bound_card(trial_id, gate_id, run_dir)
        if card_digest in journal.submitted_digests():
            raise RunnerRefusal("decision-card-replay-refused")
        verdict, selection_id = _make_verdict(
            policy=policy,
            trial_id=trial_id,
            gate_id=gate_id,
            card=card,
            card_digest=card_digest,
        )
        # Re-read both authority surfaces immediately before the one engine call.
        current = _load_envelope(trial_id, run_dir)
        _assert_delegated_trial_scope(
            trial_id=trial_id,
            envelope=current,
            run_dir=run_dir,
            policy=policy,
        )
        if current.status != "paused-at-gate" or current.paused_gate != gate_id:
            raise RunnerRefusal("stale-run-state-before-submit")
        _, rebound_digest, rebound_file_digest = _load_bound_card(trial_id, gate_id, run_dir)
        if rebound_digest != card_digest or rebound_file_digest != card_file_digest:
            raise RunnerRefusal("decision-card-mutated-before-submit")
        final_current = _load_envelope(trial_id, run_dir)
        _assert_delegated_trial_scope(
            trial_id=trial_id,
            envelope=final_current,
            run_dir=run_dir,
            policy=policy,
        )
        if final_current.status != "paused-at-gate" or final_current.paused_gate != gate_id:
            raise RunnerRefusal("stale-run-state-before-submit")
        _check_deadline(started_at, policy)
        journal.append(
            "submission-started",
            gate_id=gate_id,
            card_id=str(card.card_id),
            decision_card_digest=card_digest,
            verdict_id=str(verdict.verdict_id),
            verb=verdict.verb,
            selection_id=selection_id,
        )
        actions += 1
        returned = resume_fn(
            trial_id=trial_id,
            verdict=verdict,
            runs_root=runs_root,
            max_specialist_calls=policy.budgets.max_specialist_calls_per_segment,
        )
        _check_deadline(started_at, policy)
        envelope = _authoritative_resume_result(
            trial_id=trial_id,
            run_dir=run_dir,
            returned=returned,
        )
        _assert_delegated_trial_scope(
            trial_id=trial_id,
            envelope=envelope,
            run_dir=run_dir,
            policy=policy,
        )
        journal.append(
            "transition-recorded",
            decision_card_digest=card_digest,
            resulting_status=envelope.status,
            resulting_gate=envelope.paused_gate,
        )


def _drive_with_evidence_handling(
    *,
    trial_id: UUID,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    resume_fn: Callable[..., ProductionTrialEnvelope] = resume_production_trial,
    started_at: float,
) -> dict[str, Any]:
    """Drive one attached trial and persist a summary for every refusal."""
    try:
        return _drive_paused_trial_impl(
            trial_id=trial_id,
            runs_root=runs_root,
            policy=policy,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
            resume_fn=resume_fn,
            started_at=started_at,
        )
    except RunnerRefusal as exc:
        journal = EvidenceJournal(
            trial_id=trial_id,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
        )
        actions = sum(event.get("kind") == "submission-started" for event in journal.events)
        journal.append("runner-refused", reason=exc.code)
        journal.finalize(
            status="refused",
            success=False,
            reason=exc.code,
            actions=actions,
        )
        raise
    except Exception as exc:
        journal = EvidenceJournal(
            trial_id=trial_id,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
        )
        actions = sum(event.get("kind") == "submission-started" for event in journal.events)
        journal.append(
            "runner-refused",
            reason="engine-call-failed",
            error_type=type(exc).__name__,
        )
        journal.finalize(
            status="refused",
            success=False,
            reason="engine-call-failed",
            actions=actions,
        )
        raise RunnerRefusal("engine-call-failed") from exc


def _validate_public_roots(
    *,
    policy: DelegationPolicy,
    runs_root: Path,
    evidence_root: Path,
) -> tuple[Path, Path]:
    if ".." in evidence_root.parts:
        raise RunnerRefusal("parent-traversal-refused")
    if ".." in Path(policy.allowed_evidence_root).parts:
        raise RunnerRefusal("parent-traversal-refused")
    safe_runs_root = _match_allowed_root(runs_root, policy.allowed_runs_roots, kind="dir")
    expected_evidence = _absolute_without_resolving(_policy_path(policy.allowed_evidence_root))
    candidate_evidence = _absolute_without_resolving(evidence_root)
    if candidate_evidence != expected_evidence:
        raise RunnerRefusal("evidence-root-policy-mismatch")
    # Validate containment and every existing component before creating anything.
    safe_evidence = _assert_safe_path(candidate_evidence, root=PROJECT_ROOT, kind="missing-ok")
    safe_evidence.mkdir(parents=True, exist_ok=True)
    _assert_safe_path(safe_evidence, root=PROJECT_ROOT, kind="dir")
    return safe_runs_root, safe_evidence


def _validate_policy_digest(policy: DelegationPolicy, policy_digest: str) -> None:
    expected = _digest(policy.model_dump(mode="json"))
    if policy_digest != expected:
        raise RunnerRefusal("policy-digest-mismatch")


def drive_paused_trial(
    *,
    trial_id: UUID,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    resume_fn: Callable[..., ProductionTrialEnvelope] = resume_production_trial,
    started_at: float | None = None,
) -> dict[str, Any]:
    """Public attach entry: validate policy roots, lock, scope, then drive."""
    clock_start = time.monotonic() if started_at is None else started_at
    _validate_policy_digest(policy, policy_digest)
    safe_runs_root, safe_evidence = _validate_public_roots(
        policy=policy, runs_root=runs_root, evidence_root=evidence_root
    )
    _check_deadline(clock_start, policy)
    run_dir = _assert_safe_path(safe_runs_root / str(trial_id), root=safe_runs_root, kind="dir")
    with exclusive_trial_lock(
        run_dir,
        trial_id=trial_id,
        policy_digest=policy_digest,
    ) as preflight_required:
        result: dict[str, Any] | None = None
        primary_error: BaseException | None = None
        evidence_errors: list[BaseException] = []
        preflight_path = safe_evidence / str(trial_id) / PREFLIGHT_IDENTITY_FILENAME
        preflight: dict[str, Any] | None = None
        if preflight_path.exists():
            candidate = _read_json(preflight_path, root=safe_evidence)
            current = _rebuild_governed_identity_from_preflight(
                trial_id=trial_id,
                preflight=candidate,
            )
            if current["files"] != candidate["files"]:
                raise RunnerRefusal("governed-input-mutated-before-attach")
            preflight = candidate
        elif preflight_required:
            raise RunnerRefusal("attach-preflight-evidence-missing")
        try:
            result = _drive_with_evidence_handling(
                trial_id=trial_id,
                runs_root=safe_runs_root,
                policy=policy,
                policy_digest=policy_digest,
                evidence_root=safe_evidence,
                resume_fn=resume_fn,
                started_at=clock_start,
            )
        except BaseException as exc:
            primary_error = exc
        if preflight is not None:
            try:
                postflight = _rebuild_governed_identity_from_preflight(
                    trial_id=trial_id,
                    preflight=preflight,
                )
                _comparison_path, matches = _persist_postflight_comparison(
                    trial_id=trial_id,
                    preflight=preflight,
                    postflight=postflight,
                    evidence_root=safe_evidence,
                )
                if not matches:
                    evidence_errors.append(RunnerRefusal("governed-input-mutated-during-run"))
            except BaseException as exc:
                evidence_errors.append(exc)
        try:
            state_run_dir: Path | None = None
            if preflight is not None:
                for row in preflight.get("writable_exclusions", []):
                    if row.get("label") == "state/config/runs/trial":
                        state_run_dir = Path(str(row["path"]))
                        break
            _write_run_output_inventory(
                trial_id=trial_id,
                run_dir=run_dir,
                evidence_root=safe_evidence,
                state_config_run_dir=state_run_dir,
            )
        except BaseException as exc:
            evidence_errors.append(exc)
        if primary_error is not None:
            for evidence_error in evidence_errors:
                primary_error.add_note(f"postflight evidence error: {evidence_error}")
            raise primary_error
        if evidence_errors:
            raise RunnerRefusal("postflight-evidence-failed") from evidence_errors[0]
        if result is None:
            raise RunnerRefusal("attach-returned-no-summary")
        return result


def _directive_confirmation(
    *,
    trial_id: UUID,
    input_path: Path,
    run_dir: Path,
    journal: EvidenceJournal,
) -> Callable[..., Literal["confirmed"]]:
    def confirm(*, directive_path: Path, auto_confirm_directive: bool) -> Literal["confirmed"]:
        if auto_confirm_directive:
            raise RunnerRefusal("g0-auto-confirm-bypass-refused")
        safe = _assert_safe_path(directive_path, root=run_dir, kind="file")
        try:
            before = safe.lstat()
            raw = safe.read_bytes()
            after = safe.lstat()
            stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
            if any(getattr(before, name) != getattr(after, name) for name in stable_fields):
                raise RunnerRefusal("g0-directive-mutated-during-review")
            payload = yaml.safe_load(raw.decode("utf-8"))
            directive = Directive.model_validate(payload)
        except RunnerRefusal:
            raise
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            raise RunnerRefusal("g0-directive-malformed") from exc
        if directive.run_id != trial_id:
            raise RunnerRefusal("g0-directive-trial-mismatch")
        corpus = Path(directive.corpus_dir)
        if ".." in corpus.parts:
            raise RunnerRefusal("parent-traversal-refused")
        if _absolute_without_resolving(corpus) != _absolute_without_resolving(input_path):
            raise RunnerRefusal("g0-directive-corpus-mismatch")
        journal.append(
            "g0-directive-confirmed",
            directive_path=safe.relative_to(_absolute_without_resolving(run_dir)).as_posix(),
            directive_digest=hashlib.sha256(raw).hexdigest(),
        )
        return "confirmed"

    return confirm


def _start_and_drive_core(
    *,
    trial_id: UUID,
    input_path: Path,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    course_source_root: Path,
    encounter_mode: Literal["recorded", "live"],
    started_at: float,
) -> dict[str, Any]:
    run_dir = runs_root / str(trial_id)
    journal = EvidenceJournal(
        trial_id=trial_id, policy_digest=policy_digest, evidence_root=evidence_root
    )
    try:
        _check_deadline(started_at, policy)
        start_result = start_trial(
            preset="production",
            input_path=input_path,
            operator_id=DELEGATE_ID,
            trial_id=trial_id,
            runs_root=runs_root,
            auto_confirm_directive=False,
            confirm_fn=_directive_confirmation(
                trial_id=trial_id,
                input_path=input_path,
                run_dir=run_dir,
                journal=journal,
            ),
            max_specialist_calls=policy.budgets.max_specialist_calls_per_segment,
            component_selection=ComponentSelection(deck=True, motion=False, workbook=True),
            hud="off",
            course_source_root=course_source_root,
            encounter_mode=encounter_mode,
        )
        _check_deadline(started_at, policy)
    except Exception as exc:
        reason = exc.code if isinstance(exc, RunnerRefusal) else "start-failed"
        journal.append(
            "start-refused",
            reason=reason,
            error_type=type(exc).__name__,
        )
        journal.finalize(status="refused", success=False, reason=reason, actions=0)
        if isinstance(exc, RunnerRefusal):
            raise
        raise RunnerRefusal("start-failed") from exc
    journal.append("start-returned", status=str(start_result.get("status")))
    return _drive_with_evidence_handling(
        trial_id=trial_id,
        runs_root=runs_root,
        policy=policy,
        policy_digest=policy_digest,
        evidence_root=evidence_root,
        started_at=started_at,
    )


def start_and_drive_trial(
    *,
    trial_id: UUID,
    input_path: Path,
    course_source_root: Path,
    encounter_mode: Literal["recorded", "live"],
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    policy_path: Path | None = None,
    started_at: float | None = None,
) -> dict[str, Any]:
    """Public start entry: validate all roots, reserve trial, lock, then start."""
    clock_start = time.monotonic() if started_at is None else started_at
    _validate_policy_digest(policy, policy_digest)
    if encounter_mode not in {"recorded", "live"}:
        raise RunnerRefusal("encounter-mode-invalid")
    safe_runs_root, safe_evidence = _validate_public_roots(
        policy=policy, runs_root=runs_root, evidence_root=evidence_root
    )
    safe_input = _match_allowed_root(input_path, policy.allowed_input_roots, kind="dir")
    safe_course_root = _match_allowed_root(
        course_source_root, policy.allowed_input_roots, kind="dir"
    )
    _assert_safe_tree(safe_input)
    _assert_safe_tree(safe_course_root)
    _check_deadline(clock_start, policy)
    run_dir = safe_runs_root / str(trial_id)
    state_run_dir = (
        PROJECT_ROOT / "state" / "config" / "runs" / str(trial_id)
        if policy_path is not None
        else None
    )
    if run_dir.exists() or (state_run_dir is not None and state_run_dir.exists()):
        raise RunnerRefusal("trial-already-exists")
    try:
        run_dir.mkdir()
    except FileExistsError as exc:
        raise RunnerRefusal("trial-already-exists") from exc
    result: dict[str, Any] | None = None
    primary_error: BaseException | None = None
    evidence_errors: list[BaseException] = []
    inputs_match = False
    with exclusive_trial_lock(
        run_dir,
        trial_id=trial_id,
        policy_digest=policy_digest,
        preflight_required=True,
    ):
        _preflight_path, preflight = _write_governed_preflight_identity(
            trial_id=trial_id,
            input_path=safe_input,
            course_source_root=safe_course_root,
            evidence_root=safe_evidence,
            policy_path=policy_path,
            authority_spec=policy.authority_spec,
        )
        persisted_preflight = _read_json(_preflight_path, root=safe_evidence)
        if persisted_preflight != preflight:
            raise RunnerRefusal("preflight-evidence-identity-mismatch")
        try:
            result = _start_and_drive_core(
                trial_id=trial_id,
                input_path=safe_input,
                runs_root=safe_runs_root,
                policy=policy,
                policy_digest=policy_digest,
                evidence_root=safe_evidence,
                course_source_root=safe_course_root,
                encounter_mode=encounter_mode,
                started_at=clock_start,
            )
        except BaseException as exc:
            primary_error = exc

        if not run_dir.is_dir():
            evidence_errors.append(RunnerRefusal("output-root-missing"))
        else:
            try:
                _write_run_output_inventory(
                    trial_id=trial_id,
                    run_dir=run_dir,
                    evidence_root=safe_evidence,
                    state_config_run_dir=state_run_dir,
                )
            except BaseException as exc:
                evidence_errors.append(exc)
        try:
            _comparison_path, inputs_match = _write_postflight_input_comparison(
                trial_id=trial_id,
                preflight=preflight,
                input_path=safe_input,
                course_source_root=safe_course_root,
                evidence_root=safe_evidence,
                policy_path=policy_path,
                authority_spec=policy.authority_spec,
            )
        except BaseException as exc:
            evidence_errors.append(exc)

    if primary_error is not None:
        for evidence_error in evidence_errors:
            primary_error.add_note(f"postflight evidence error: {evidence_error}")
        raise primary_error
    if evidence_errors:
        raise RunnerRefusal("postflight-evidence-failed") from evidence_errors[0]
    if not inputs_match:
        raise RunnerRefusal("governed-input-mutated-during-run")
    if result is None:
        raise RunnerRefusal("start-returned-no-summary")
    return result


def run(
    *,
    mode: Literal["attach", "start"],
    trial_id: UUID,
    policy_path: Path,
    runs_root: Path,
    evidence_root: Path,
    input_path: Path | None = None,
    course_source_root: Path | None = None,
    encounter_mode: Literal["recorded", "live"] | None = None,
) -> dict[str, Any]:
    if mode not in {"attach", "start"}:
        raise RunnerRefusal("unknown-runner-mode")
    started_at = time.monotonic()
    policy, policy_digest = load_policy(policy_path)
    if mode == "start":
        if input_path is None or course_source_root is None or encounter_mode is None:
            raise RunnerRefusal("start-workbook-context-required")
        return start_and_drive_trial(
            trial_id=trial_id,
            input_path=input_path,
            course_source_root=course_source_root,
            encounter_mode=encounter_mode,
            runs_root=runs_root,
            policy=policy,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
            policy_path=policy_path,
            started_at=started_at,
        )
    return drive_paused_trial(
        trial_id=trial_id,
        runs_root=runs_root,
        policy=policy,
        policy_digest=policy_digest,
        evidence_root=evidence_root,
        started_at=started_at,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("attach", "start"))
    parser.add_argument("--trial-id", type=UUID, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--course-source-root", type=Path)
    parser.add_argument("--encounter-mode", choices=("recorded", "live"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = run(
            mode=args.mode,
            trial_id=args.trial_id,
            policy_path=args.policy,
            runs_root=args.runs_root,
            evidence_root=args.evidence_root,
            input_path=args.input,
            course_source_root=args.course_source_root,
            encounter_mode=args.encounter_mode,
        )
    except RunnerRefusal as exc:
        print(json.dumps({"status": "refused", "reason": exc.code}, sort_keys=True))
        return 2
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
