# Codex dispatch: Slab 6.4 cycle 2 remediation (3 focused patches; re-trace FAIL recovery)

**Session:** 2026-04-28 (operator-authorized post-second-pass-review HALT on 6.4)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Cycle 1 remediation `c2df610` addressed 11 first-pass patches but second-pass review surfaced 3 re-trace FAIL findings on 6.4
- Second-pass review record: `_bmad-output/implementation-artifacts/6-3-6-4-6-5-second-pass-review-2026-04-28.md`
- 6.3 + 6.5 are CLEAN per second-pass and proceeding to operator close in parallel — this dispatch is 6.4 ONLY
- Codex-side cycle 1 verification still passing; cycle 2 must preserve + extend

**Mission:** focused cycle 2 remediation on the 3 NEW patches surfaced by second-pass full review of 6.4 commit `c2df610`. All three are re-trace FAILs of cycle 1 work — meaning cycle 1 partially addressed but didn't fully satisfy. Cycle 2 closes the gaps so third-pass verification clears.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec.

## Three patches (BINDING; per second-pass review record)

### Patch 1 — `6.4-SP2-BH-1` (re-trace FAIL on 6.4-EH-4)

**Finding:** JSON Schema accepts remote `.png` URLs that Pydantic rejects. The current `LOCAL_PNG_PATH_PATTERN = r"^.+[.][Pp][Nn][Gg]$"` permits `https://example.com/slide.png`. Pydantic field validators reject remote URLs at runtime (`app/specialists/irene/authoring/pass_2_template.py:61, :67`), but generated JSON Schema contains ONLY the suffix pattern. JSON Schema consumers see weaker validation than Pydantic.

**Required code changes:**
- Strengthen `LOCAL_PNG_PATH_PATTERN` at `app/specialists/irene/authoring/pass_2_template.py:10` so the regex itself rejects URL schemes:
  ```python
  # Reject any path that starts with a URL scheme (e.g., http://, https://, file://, ftp://, etc.)
  # The negative lookahead at start guards against scheme prefixes; positive part requires .png suffix.
  LOCAL_PNG_PATH_PATTERN = r"^(?![a-zA-Z][a-zA-Z0-9+.-]*://).+[.][Pp][Nn][Gg]$"
  ```
- Verify the pattern is applied to ALL three fields where JSON Schema currently leaks: `gary_slide_output.file_path`, `perception_artifacts.source_image_path`, `segment_manifest.visual_file`. Use `Field(..., pattern=LOCAL_PNG_PATH_PATTERN)` so the constraint propagates into JSON Schema generation.
- Verify Pydantic field validators at `:61, :67` remain in place as defense-in-depth (regex is structural; runtime validators may carry additional logic — preserve both).

**Required test additions:**
- Add explicit JSON Schema red-rejection test:
  ```python
  # tests/unit/specialists/irene/test_pass_2_template_strict.py
  def test_json_schema_rejects_remote_png_urls() -> None:
      """6.4-EH-4 / 6.4-SP2-BH-1: JSON Schema must reject remote .png URLs (was accepting)."""
      schema = generate_pass_2_template_schema()  # or the equivalent generator
      for remote_url in ("https://example.com/slide.png", "http://x/y.png", "file:///etc/slide.png", "ftp://srv/s.png"):
          for field_path in ("gary_slide_output.file_path", "perception_artifacts.source_image_path", "segment_manifest.visual_file"):
              with pytest.raises(jsonschema.ValidationError):
                  jsonschema.validate({"...": remote_url}, schema)  # adapt to actual fixture shape
  ```
- Re-run Pydantic-side rejection test to confirm both layers reject (defense-in-depth).

**Verification command:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/specialists/irene/test_pass_2_template_strict.py -k "json_schema_rejects_remote_png_urls" -q --tb=short
```

### Patch 2 — `6.4-SP2-EH-1` (re-trace FAIL on M-R3 / 6.4-AA-4)

**Finding:** Validator-oracle alignment NOT FULL. `validate-irene-pass2-handoff.py` contains 39 `errors.append(...)` enforcement points + 11 `warnings.append(...)` points = 50 enforcement points. Current alignment parametrization at `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py:310` covers only 6 procedural cases. Test neither imports authoritative rule list from validator NOR enumerates rules with cross-reference comments + skip rationale.

**Required code changes:**

Choose ONE of two approaches per discipline doc (operator-judgement-call; surface to operator if neither works cleanly):

**Approach A — dynamic rule extraction:**
- Refactor `validate-irene-pass2-handoff.py` to expose a `RULES: list[ValidatorRule]` constant where `ValidatorRule` is a small dataclass: `(rule_id: str, message_template: str, kind: Literal["error", "warning"], category: str)`. Each `errors.append(...)` and `warnings.append(...)` site references a `RULES[i]` entry by id.
- Test imports `RULES` and parametrizes over each entry; per rule, test asserts the new template enforces the same behavior (schema OR procedural; whichever is correct per rule).
- Best long-term shape but requires validator refactor (~1-1.5 hr).

**Approach B — explicit enumeration with cross-reference + skip rationale:**
- In `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py`, replace the current 6-case parametrize with explicit enumeration of ALL 39 error rules + 11 warning rules. Each entry: `(rule_id: str, validator_line: int, expected_coverage: Literal["schema", "procedural", "skipped"], rationale: str)`. For "skipped" entries, rationale must explain why coverage is not applicable (e.g., "warning-only; not enforced fail-loud; covered by docs not test").
- Test parametrizes over the explicit enumeration; per "schema" entry, asserts Pydantic rejects schema-violating input; per "procedural" entry, asserts procedural alignment test exists; per "skipped" entry, asserts the rationale is non-empty + comment block in test docs the skip.
- Faster path (~1 hr) but creates a maintenance dependency (test enumeration must stay in sync with validator).

**Surface as decision_needed if:** Approach A's validator refactor introduces unrelated behavior changes OR Approach B's explicit enumeration is unwieldy at 50 entries.

**Recommended default:** Approach B (explicit enumeration). Validator refactor (Approach A) can be a follow-on Slab-6-4-cycle-2-followon if maintenance burden materializes.

**Required test additions:**
- The expanded parametrization itself IS the test addition
- Add a meta-test: `test_validator_alignment_enumeration_covers_all_validator_rules` — counts `errors.append(...)` + `warnings.append(...)` sites in `validate-irene-pass2-handoff.py`; asserts equals length of alignment-test parametrize list. Prevents drift if validator gains new rules without alignment-test update.

**Verification command:**
```bash
.venv/Scripts/python.exe -m pytest tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py -q --tb=short
```

### Patch 3 — `6.4-SP2-AA-1` (re-trace FAIL on 6.4-AA-1 closed-enum portion)

**Finding:** Closed-enum 3-surface audit omits the `ProceduralRule` enum. Current parametrization at `tests/unit/specialists/irene/test_pass_2_template_strict.py:103` covers `schema_version`, `composition_mode`, `visual_detail_load`, `content_density`, `bridge_type`, `cluster_role`, `cluster_position` (7 enums) but missing `procedural_rules` unknown-value case. Partial/order test at `:178` doesn't pin Pydantic Literal rejection + JSON Schema enum rejection + explicit shape-pin for an unknown procedural rule.

**Required test additions:**
- Add `ProceduralRule` to the closed-enum 3-surface red-rejection parametrize at `tests/unit/specialists/irene/test_pass_2_template_strict.py:103`:
  ```python
  ("procedural_rules", ProceduralRule, "phantom_rule_unknown_value"),  # 6.4-SP2-AA-1
  ```
- Verify the parametrize per-enum loop covers:
  1. Pydantic `Literal` red-rejection: instantiating model with unknown value raises `ValidationError`
  2. JSON Schema `enum` red-rejection: `jsonschema.validate(...)` rejects unknown value
  3. Explicit shape-pin: assertion that the unknown value is NOT in the enum's accepted-values list
- If the existing parametrize doesn't cover all 3 surfaces uniformly, refactor to ensure all 8 enums (7 existing + ProceduralRule) get the same 3-surface treatment.

**Verification command:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/specialists/irene/test_pass_2_template_strict.py -k "closed_enum or procedural_rule" -q --tb=short
```

## Verification + commit

After all 3 patches addressed:

```bash
# Full 6.4-relevant focused regression
.venv/Scripts/python.exe -m pytest \
  tests/unit/specialists/irene/test_pass_2_template_strict.py \
  tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py \
  tests/composition/test_irene_pass_2_template_composition_smoke.py \
  -q --tb=short

# Verify no regression in cycle 1 work
.venv/Scripts/python.exe -m pytest tests/unit/specialists/irene/ tests/integration/specialists/irene/ -q --tb=short

# Ruff + sandbox-AC
.venv/Scripts/python.exe -m ruff check app/specialists/irene/authoring/ tests/unit/specialists/irene/ tests/integration/specialists/irene/
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-6-4-irene-pass-2-authoring-template.md
```

Expected: all PASS; cycle 1 tests still GREEN; new cycle 2 tests GREEN.

**Themed commit:**
```
fix(slab-6.4-cycle-2): close 3 re-trace FAIL findings from second-pass review

Addresses second-pass review record 6-3-6-4-6-5-second-pass-review-2026-04-28.md
6.4 patches:
- 6.4-SP2-BH-1: JSON Schema now rejects remote .png URLs via negative-lookahead
  pattern (mirrors Pydantic field-validator runtime rejection); JSON Schema
  consumers no longer weaker than model. Closes 6.4-EH-4 re-trace FAIL.
- 6.4-SP2-EH-1: Validator-oracle alignment expanded to enumerate all 39 error
  + 11 warning enforcement points from validate-irene-pass2-handoff.py with
  per-rule expected-coverage + rationale; meta-test prevents future drift.
  Closes M-R3 / 6.4-AA-4 re-trace FAIL.
- 6.4-SP2-AA-1: ProceduralRule added to closed-enum 3-surface red-rejection
  parametrize; all 8 enums now get uniform Pydantic Literal + JSON Schema enum
  + shape-pin coverage. Closes 6.4-AA-1 closed-enum portion re-trace FAIL.

Verification: focused 6.4 suites pass; cycle 1 tests preserved; ruff clean;
sandbox-AC PASS.

Story status remains review (third-pass verification fires next).
```

Sprint-status flip: keep `migration-6-4-irene-pass-2-authoring-template: review` (do NOT flip to done from this cycle).

## Halt-and-surface triggers

HALT if:
- Approach B explicit enumeration becomes unwieldy beyond 50 entries (surface as decision_needed for Approach A pivot OR a different shape)
- Approach A validator refactor introduces unrelated behavior changes (surface; do not silently expand scope)
- New patch surfaces beyond the 3 named here
- Pydantic / JSON Schema generator interaction reveals constraint that can't propagate cleanly (e.g., negative lookahead pattern not supported by JSON Schema draft-7 or whatever version is in use — surface as decision_needed for alternative pattern)
- Cycle 1 tests regress

## What this dispatch does NOT do

- Does NOT touch 6.3 or 6.5 (clean per second-pass; operator handles closes separately)
- Does NOT flip 6.4 to done (third-pass verification-only re-trace fires next; operator runs Gate 5 dual-gate after; then formal close)
- Does NOT modify Slab 6.0/6.1/6.2 substrate (out of scope)
- Does NOT modify anti-pattern catalog (Mary harvest-gate at 6.4 close evaluates A18; not at remediation)
- Does NOT re-litigate operator-ratified party-mode BINDING riders or DN dispositions

## Closeout posture

When this commit lands:
1. Codex final report: 3 patches addressed; verification numbers; any decision_needed items surfaced (likely zero given concrete patch shape)
2. Operator authors third-pass verification-only re-trace dispatch (Acceptance Auditor only on the 3 cycle-2 patches; ~30-60 min Codex)
3. Once third-pass clears: operator runs Gate 5 dual-gate live evidence ceremony for 6.4
4. Then formal 6.4 close per discipline doc Gate 6 + Mary harvest-gate A18 disposition

Total wall-clock to 6.4 close: ~3-5 hr Codex (cycle 2 + third-pass verification) + operator Gate 5 + close edits. Achievable in this session if operator stays engaged.
