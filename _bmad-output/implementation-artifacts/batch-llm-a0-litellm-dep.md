# Story: batch-llm-a0-litellm-dep — LiteLLM dependency honesty

**Status:** done  
**Epic:** `epic-batch-llm-execution-mode`  
**Kanban key:** `batch-llm-a0-litellm-dep`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate:** single-gate  
**Party:** GO-WITH-AMENDMENTS folded — `_bmad-output/planning-artifacts/batch-llm-party-greenlight-2026-07-10.md`  
**SSOT:** `_bmad-output/implementation-artifacts/batch-llm-execution-mode-stories-2026-07-10.md` §A0  
**Research:** `_bmad-output/planning-artifacts/research/technical-litellm-batch-hookup-research-2026-07-10.md`

## Story

As the Marcus-SPOC runtime maintainer,  
I want LiteLLM declared as a first-class project dependency with an import/version smoke test,  
so clones and CI do not rely on a tribal `.venv` install before Batch adapter work (B1) begins.

## Acceptance Criteria

1. **Given** a clean install from `pyproject.toml`, **when** dependencies resolve, **then** `litellm>=1.90.2,<2` is present.
2. **Given** the project venv, **when** hermetic tests run, **then** `import litellm` succeeds and `importlib.metadata.version("litellm")` starts with `1.90`.
3. **Given** `app/runtime/llm_batch/__init__.py`, **when** a developer reads the package docstring, **then** they see: (a) cite to the 2026-07-10 research path, (b) true Batch path = Files + `create_batch` (not `batch_completion`), (c) A0 claims dep honesty only — adapter is B1.
4. **CLOSE claim fence:** this story may claim **dependency honesty only** — not Batch adapter hookup, not perception route, not cost savings.

## Out of scope

- `adapter.py` / `jsonl.py` / `join.py` / `receipts.py` (B1)
- Vision batch route (B2)
- Any live OpenAI / Batch API calls

## Tasks

- [x] Author this story file; flip Kanban `backlog` → `in-progress`
- [x] Add `litellm>=1.90.2,<2` to `pyproject.toml` dependencies (near langchain-openai)
- [x] Ensure package installable (`pip install "litellm>=1.90.2,<2"`; editable `-e .` still blocked by pre-existing multi-package discovery — not A0 scope)
- [x] Add `app/runtime/llm_batch/__init__.py` with naming-trap + research docstring
- [x] Add `tests/runtime/llm_batch/test_litellm_dep_smoke.py` (GREEN: 4 passed)
- [x] Run focused pytest; ruff on touched paths
- [x] Flip story + Kanban to `done` on green

## Dev Notes

- Machine already had `litellm==1.90.2` in `.venv` — A0 makes that **project-declared**.
- Do **not** implement Batch client wrappers here.
- Prefer not to touch `app/models/adapter.py`.

## Dev Agent Record

### Completion Notes

- Declared `litellm>=1.90.2,<2` in `pyproject.toml`.
- Package stub `app/runtime/llm_batch/` documents research path + `batch_completion` naming trap; no adapter yet.
- Hermetic smoke: 4 passed (`import`, version `1.90.2`, docstring trap, pyproject pin).
- CLOSE claim: **dependency honesty only**.

### File List

- `pyproject.toml`
- `app/runtime/llm_batch/__init__.py`
- `tests/runtime/llm_batch/test_litellm_dep_smoke.py`
- `_bmad-output/implementation-artifacts/batch-llm-a0-litellm-dep.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/batch-llm-execution-mode-stories-2026-07-10.md`
