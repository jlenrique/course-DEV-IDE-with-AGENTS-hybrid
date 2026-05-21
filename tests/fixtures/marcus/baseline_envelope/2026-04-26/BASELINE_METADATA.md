# Marcus Envelope Baseline Metadata

- trial-id: `33333333-3333-4333-8333-333333333333`
- corpus-path: `tests/fixtures/trial_corpus/README.md`
- commit-sha: `6ecfed3c795d51a33a556bba063502df93d96b31`
- capture-timestamp: `2026-04-26T17:00:00Z`
- operator-name: `Codex dev agent`
- purpose: frozen baseline for Slab-4+ Marcus-output regression-detection per W-R7-3.1
- capture-command: `python - <<'PY' ... from marcus.orchestrator.m3_trial import run_local_m3_trial ... PY`
- capture-environment-hash: `3662e177e11b6bf9d2f0815d3ae6bd35cbe4cfa51af6460d8e3526e7669c1382`
- marcus-persona-load-sha: `b754f8eaa553776073b0fe7ba4a81b2e51e55545bd50ce8ac8969e250624c06e`
- sanctum-state-sha: `7adaeaf8b24c081278ecad82ca4c9dd4744dc98cb4ea49f37c0b8aeeeed6468e`
- reference-set-sha: `3327a5874ef10d20e5d629f2c22faa0d1cd27394c6326fc0d076e2f7b4f09676`
- envelope-content-sha256: `9f36ed824e75960a5a943225ac0966495484462f3d25c9e04da687c2dbb0dbfb`
- rebaseline-protocol: rebaseline only after party-mode review confirms the change is intentional, update the schema version if the envelope shape changes, regenerate the content hash and environment hash in the same PR, and record the rationale in `slab-3-m3-acceptance-verdict.md`.
