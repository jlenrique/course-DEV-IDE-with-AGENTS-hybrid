# gamma-doc-audit run report

- driver: `scripts/utilities/audit_gamma_docs.py`
- started_at: 2026-07-02T05:54:36Z
- dry_run: False
- preflight: {'url': 'https://developers.gamma.app/llms.txt', 'ok': True, 'error': None}
- exit_tier: **0**
- terminal_state_counts: {'confirmed': 12, 'drift-detected': 3}

| item_id | state | kinds | http | reason |
|---|---|---|---|---|
| enum-parity-image-model | confirmed | - | 200 | enum-membership parity |
| enum-parity-text-mode | confirmed | - | 200 | enum-membership parity |
| enum-parity-text-amount | confirmed | - | 200 | enum-membership parity |
| enum-parity-text-language | confirmed | - | 200 | enum-membership parity |
| enum-parity-image-source | confirmed | - | 200 | enum-membership parity |
| enum-parity-image-style-preset | confirmed | - | 200 | free-text surface confirmed with positive witness |
| enum-parity-card-dimensions | confirmed | - | 200 | enum-membership parity |
| doc-fact-burst-throttle-429 | confirmed | - | 200 | documented literal present |
| doc-fact-ratelimit-burst-header | confirmed | - | 200 | documented literal present |
| doc-fact-polling-interval-5s | confirmed | - | 200 | documented literal present |
| doc-fact-list-themes-limit-50 | confirmed | - | 200 | numeric value matches |
| finding-imageoptions-discrete-tags-field | drift-detected | doc-drift | 200 | documented literal absent |
| finding-imageoptions-stylepreset-style-composition | drift-detected | doc-drift | 200 | documented literal absent |
| doc-fact-changelog-canary | confirmed | - | 200 | documented literal present |
| probe-absent-anchor-teeth | drift-detected | doc-restructure | 200 | declared anchor '#### zz-leg-e-probe-anchor-known-absent' absent from the fetched page (doc-restructure: run-report only |

- ledger: `C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid\state\config\gamma-learned-observations.jsonl`
- lines before/after: 6 -> 6 (written=0, noop=1)
- sha256 before: sha256:e8f8331fd2e3758e79f6436bd0d071587ae37d76e9bf597ddc924c1dc7b2290c
- sha256 after:  sha256:e8f8331fd2e3758e79f6436bd0d071587ae37d76e9bf597ddc924c1dc7b2290c
- rejected (wording-triple gate): []
