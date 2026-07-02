# gamma-doc-audit run report

- driver: `scripts/utilities/audit_gamma_docs.py`
- started_at: 2026-07-02T04:32:02Z
- dry_run: False
- preflight: {'url': 'https://developers.gamma.app/llms.txt', 'ok': True, 'error': None}
- exit_tier: **10**
- terminal_state_counts: {'drift-detected': 4, 'confirmed': 11}

| item_id | state | kinds | http | reason |
|---|---|---|---|---|
| enum-parity-image-model | drift-detected | doc-drift,coverage-gap | 200 | enum-membership divergence |
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
- lines before/after: 6 -> 6 (written=0, noop=3)
- sha256 before: sha256:b0e4f3e91dd04fe11f4e71a8fb08c14d968692a63441cd516cddced847a5275b
- sha256 after:  sha256:b0e4f3e91dd04fe11f4e71a8fb08c14d968692a63441cd516cddced847a5275b
- rejected (wording-triple gate): []
