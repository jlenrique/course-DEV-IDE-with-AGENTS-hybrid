---
title: 'Fix stale llm_execution_config docstrings (batch model binding)'
type: 'fix'
created: '2026-07-10'
status: 'done'
route: 'one-shot'
---

# Fix stale llm_execution_config docstrings (batch model binding)

## Intent

**Problem:** The module docstring of `app/runtime/llm_execution_config.py` claimed batch "may diverge (default `gpt-4.1-mini`)", contradicting the ratified operator binding in `runtime/config/llm_execution.yaml` (2026-07-10: batch model MUST match realtime `gpt-5.5`; GPT-5-family fallback is declared policy; never `gpt-4.1-*` as product default). Surfaced by Murat during the guides claim-discipline review. Adversarial review additionally caught the `profile_for` docstring asserting "batch falls back to realtime" while the code raises `ValueError`.

**Approach:** Docstring-only one-shot: rewrite the module docstring to state the operator binding with explicit agency (`batch_model_fallback_family` is policy-only — this module does not auto-substitute), and correct `profile_for` to state the actual raise-on-missing behavior. Fresh dev agent implemented; context-free adversarial review; F1/F2/F4/F5 patched, F3 (no validator enforces the binding; fallback field consumed by zero production code) deferred to `deferred-work.md`, F6 informational.

## Suggested Review Order

1. [app/runtime/llm_execution_config.py](../../app/runtime/llm_execution_config.py) — the two corrected docstrings (module header; `profile_for`). Verify wording against the YAML header binding.
2. [runtime/config/llm_execution.yaml](../../runtime/config/llm_execution.yaml) — ground truth: operator binding comment + `batch_model_fallback_family: gpt-5`.
3. [deferred-work.md](deferred-work.md) — the F3 hardening defer (validator for the binding; dead `batch_model_fallback_family` consumption decision).
