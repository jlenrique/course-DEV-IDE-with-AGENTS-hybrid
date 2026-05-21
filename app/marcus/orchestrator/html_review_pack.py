"""Skeleton HTML review-pack emitter for per-slide review gates."""

from __future__ import annotations

import hashlib
import json
import shutil
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any


class BrowserOpenError(RuntimeError):
    """Raised when the operator browser cannot be opened."""


class GateAdvanceBlockedError(RuntimeError):
    """Raised when a gate tries to advance without a browser-open log."""


@dataclass(frozen=True)
class ReviewPackRow:
    """One row in a per-slide review pack."""

    slide_index: int
    slide_label: str
    preview: str
    output: dict[str, Any]

    @property
    def output_digest(self) -> str:
        payload = json.dumps(self.output, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_review_pack(
    *,
    trial_id: str,
    gate_id: str,
    rows: list[ReviewPackRow],
    runs_root: Path = Path("runs"),
) -> Path:
    """Write a deterministic skeleton-only HTML review pack."""
    gate_dir = runs_root / trial_id / "gates"
    gate_dir.mkdir(parents=True, exist_ok=True)
    pack_path = gate_dir / f"{gate_id}-review-pack.html"
    if pack_path.exists():
        _archive_existing_pack(pack_path=pack_path, gate_id=gate_id)
    pack_path.write_text(
        _render_review_pack(trial_id=trial_id, gate_id=gate_id, rows=rows),
        encoding="utf-8",
        newline="\n",
    )
    return pack_path


def open_review_pack(
    *,
    pack_path: Path,
    trial_id: str,
    gate_id: str,
    opener: Callable[[str], bool] = webbrowser.open,
) -> str:
    """Open the pack in the default browser and append the open-event log."""
    file_url = pack_path.resolve().as_uri()
    if not opener(file_url):
        raise BrowserOpenError(f"webbrowser.open failed for {file_url}")
    log_path = open_log_path(pack_path=pack_path, gate_id=gate_id)
    timestamp = datetime.now(UTC).isoformat()
    log_path.write_text(
        f"{timestamp} trial_id={trial_id} gate_id={gate_id} pack_path={pack_path.as_posix()}\n",
        encoding="utf-8",
        newline="\n",
    )
    return file_url


def assert_gate_advance_allowed(*, pack_path: Path, gate_id: str) -> None:
    """Fail closed unless the browser-open event log exists and has content."""
    log_path = open_log_path(pack_path=pack_path, gate_id=gate_id)
    if not log_path.exists() or not log_path.read_text(encoding="utf-8").strip():
        raise GateAdvanceBlockedError(f"missing browser-open log for {gate_id}")


def open_log_path(*, pack_path: Path, gate_id: str) -> Path:
    return pack_path.parent / f"{gate_id}-pack-open.log"


def _archive_existing_pack(*, pack_path: Path, gate_id: str) -> None:
    history_dir = pack_path.parent / "_history"
    history_dir.mkdir(parents=True, exist_ok=True)
    version = 1
    while (history_dir / f"{gate_id}-v{version}.html").exists():
        version += 1
    shutil.copyfile(pack_path, history_dir / f"{gate_id}-v{version}.html")


def _render_review_pack(*, trial_id: str, gate_id: str, rows: list[ReviewPackRow]) -> str:
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        f"<title>{escape(gate_id)} review pack</title>",
        "<style>",
        "body { font-family: sans-serif; margin: 16px; }",
        "table { border-collapse: collapse; width: 100%; }",
        "th, td { border: 1px solid #ccc; padding: 4px; vertical-align: top; }",
        "textarea { width: 100%; min-height: 4rem; }",
        ".blocker { color: red; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{escape(gate_id)} Review Pack</h1>",
        f"<form id=\"review-pack\" data-gate-id=\"{escape(gate_id)}\">",
        "<table>",
        "<thead><tr><th>Slide</th><th>Preview</th><th>Decision</th>"
        "<th>Delta directive</th></tr></thead>",
        "<tbody>",
    ]
    for row in rows:
        parts.extend(_render_row(trial_id=trial_id, gate_id=gate_id, row=row))
    parts.extend(
        [
            "</tbody>",
            "</table>",
            "</form>",
            "<script>",
            "const form = document.getElementById('review-pack');",
            "for (const field of form.querySelectorAll('textarea,input[type=radio]')) {",
            "  const key = `${form.dataset.gateId}:${field.id || field.name}`;",
            "  const saved = sessionStorage.getItem(key);",
            "  if (saved !== null) {",
            "    if (field.type === 'radio') field.checked = saved === field.value;",
            "    else field.value = saved;",
            "  }",
            "  field.addEventListener('change', () => {",
            "    const value = field.type === 'radio' && !field.checked ? '' : field.value;",
            "    sessionStorage.setItem(key, value);",
            "  });",
            "}",
            "</script>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _render_row(*, trial_id: str, gate_id: str, row: ReviewPackRow) -> list[str]:
    prefix = f"{gate_id}-slide-{row.slide_index}"
    return [
        f"<tr data-gate-id=\"{escape(gate_id)}\" data-slide-index=\"{row.slide_index}\">",
        f"<td><label for=\"{prefix}-delta\">"
        f"{escape(row.slide_label)} ({row.slide_index})</label></td>",
        f"<td>{escape(row.preview)}</td>",
        "<td>",
        _radio(prefix, "approve"),
        _radio(prefix, "revise"),
        _radio(prefix, "skip"),
        f"<input type=\"hidden\" name=\"{prefix}-trial_id\" value=\"{escape(trial_id)}\">",
        f"<input type=\"hidden\" name=\"{prefix}-gate_id\" value=\"{escape(gate_id)}\">",
        f"<input type=\"hidden\" name=\"{prefix}-slide_index\" value=\"{row.slide_index}\">",
        f"<input type=\"hidden\" name=\"{prefix}-output_digest\" value=\"{row.output_digest}\">",
        "</td>",
        f"<td><textarea id=\"{prefix}-delta\" name=\"{prefix}-delta_directive\"></textarea></td>",
        "</tr>",
    ]


def _radio(prefix: str, value: str) -> str:
    field_id = f"{prefix}-{value}"
    return (
        f"<label for=\"{field_id}\"><input id=\"{field_id}\" type=\"radio\" "
        f"name=\"{prefix}-decision\" value=\"{value}\"> {value}</label>"
    )


__all__ = [
    "BrowserOpenError",
    "GateAdvanceBlockedError",
    "ReviewPackRow",
    "assert_gate_advance_allowed",
    "open_log_path",
    "open_review_pack",
    "write_review_pack",
]
