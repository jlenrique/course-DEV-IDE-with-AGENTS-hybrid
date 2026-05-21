# Text encoding and mojibake (UTF-8)

## Policy

- All tracked **text** in this repository is **UTF-8** (no BOM) unless a tool explicitly requires otherwise.
- Prefer **ASCII punctuation** in machine-generated or high-churn artifacts when readability allows (`->`, `--`, `<=`, `>=`, `"`).

## What went wrong (historical)

Some long YAML/Markdown lines were saved after UTF-8 bytes were misread as **Windows-1252** (or similar), then re-encoded as UTF-8. That **double corruption** replaces a single intended punctuation character with a short run of *wrong* characters (often starting with U+00E2). The canonical before/after list is `KNOWN_MOJIBAKE_SEQUENCES` in `scripts/utilities/normalize_mojibake.py` (do not paste live mojibake into new docs).

## Guardrails in this repo

- **`.editorconfig`** — `charset = utf-8`, LF endings, so editors that respect EditorConfig open and save as UTF-8.
- **`.gitattributes`** — `text=auto eol=lf` so line endings stay consistent on all platforms.
- **`scripts/utilities/normalize_mojibake.py`** — replaces known mojibake **sequences** with the intended Unicode (run on affected files, or a path list).
- **Contract test** `tests/contracts/test_no_mojibake_sequences_in_artifacts.py` — fails CI if known bad sequences reappear under `_bmad-output/implementation-artifacts/`.
- **Pre-flight heartbeat** `skills/pre-flight-check/scripts/preflight_runner.py` — the heartbeat line parser still accepts the legacy mojibake em dash in **process output** (not as a repo authoring goal) using explicit Unicode escapes.

## Local developer checklist (Windows)

- Save files as **UTF-8** in the editor; avoid the editor's "system default" or legacy code pages.
- In PowerShell, prefer `[Console]::OutputEncoding` and `$OutputEncoding` set to UTF-8 when piping text into files, or use Python/Node to write text.
- `git` — `core.autocrlf` left at normal defaults with `.gitattributes` LF rules is usually fine; avoid re-encoding hooks that rewrite file bodies as non-UTF-8.

## When you see mojibake in a new file

1. Run: `python scripts/utilities/normalize_mojibake.py --apply path/to/file.md`
2. Re-open the file; if any sequence remains, add a **new** `(bad, good)` entry to `KNOWN_MOJIBAKE_SEQUENCES` in `normalize_mojibake.py` (with a one-line comment) and re-run.
