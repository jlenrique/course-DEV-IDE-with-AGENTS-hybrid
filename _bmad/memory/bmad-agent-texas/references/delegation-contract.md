# Delegation Contract: Marcus ↔ Texas

## Overview

Marcus delegates source wrangling to Texas via a structured directive. Texas returns a structured result. Marcus mediates all downstream delivery — Texas never delivers directly to Irene, Gary, Vera, or other consuming agents.

## Marcus → Texas: Wrangling Directive

```yaml
task: source_wrangling
run_id: "{RUN_ID from run-constants}"
bundle_dir: "course-content/staging/tracked/source-bundles/{run-slug}/"
course_content_dir: "course-content/courses/{course-slug}/"
sources:
  - ref_id: "src-001"
    provider: "local_file"        # local_file | notion | url | box | mcp
    locator: "path/to/source.pdf" # provider-specific address
    format: "pdf"                 # pdf | docx | md | html | notion | pptx
    role: "primary"               # primary | validation | supplementary
    description: "Human-readable description"
    known_issues: []              # operator-declared problems
    coverage_scope: "full_module" # full_module | part_N | topic_specific
  # ... additional sources
quality_gate:
  min_completeness: 0.80          # minimum completeness ratio to pass
  require_structural_fidelity: true
```

## Texas → Marcus: Wrangling Result

```yaml
status: "complete"                # complete | complete_with_warnings | blocked
materials:
  - ref_id: "src-001"
    quality_tier: 1               # 1=Full Fidelity, 2=Adequate, 3=Degraded, 4=Failed
    extraction_mode: "snapshot"   # live_ref | snapshot | rich_transform
    content_path: "extracted.md"  # relative to bundle_dir
    extractor_used: "pypdf"       # which method produced the final output
    fallbacks_tried: []           # methods attempted before the successful one
    word_count: 7514
    line_count: 786
    heading_count: 24
    quality_report:
      completeness_ratio: 0.95
      structural_fidelity: "high"
      cross_validation:
        - asset_ref_id: "src-002"
          asset_description: "Part 1 MD reference"
          sections_matched: "6/6"
          key_terms_coverage: 0.92
          verdict: "confirms extraction completeness for Part 1 scope"
      known_losses: []
      evidence:
        - "Extracted 7514 words / 786 lines / 24 headings"
        - "Expected minimum: 4800 words (completeness: 156%)"
        - "Cross-validated against Part 1 MD: 6/6 sections matched"
blocking_issues: []               # only present when status = "blocked"
  # - ref_id: "src-001"
  #   issue: "PDF is password-protected"
  #   question: "Please provide the password or an unlocked version"
recommendations: []               # advisory, non-blocking
bundle_manifest_path: "manifest.json"  # index of all produced files
```

## Bundle Directory Structure

Texas writes all output to the bundle directory:

```
{bundle_dir}/
├── manifest.json              # index for Vera provenance tracing
├── extracted.md               # primary extraction (what downstream agents consume)
├── metadata.json              # source metadata (pages, engine, timestamps)
├── extraction-report.yaml     # quality tier, evidence, cross-validation results
├── ingestion-evidence.md      # human-readable extraction evidence log
└── gates/
    └── gate-03-result.yaml    # gate sidecar for HUD (if gate integration active)
```

## Status Semantics

| Status | Meaning | Marcus Action |
|--------|---------|---------------|
| `complete` | All sources extracted at Tier 1 or 2 | Proceed with production run |
| `complete_with_warnings` | All sources extracted but some at Tier 2 with gaps | Proceed, but surface warnings to operator |
| `blocked` | One or more critical sources at Tier 3/4 after fallbacks | Halt run, present blocking_issues to operator |

## Provenance Chain

Every piece of extracted content maintains a provenance chain:
- `ref_id` links material back to the source directive
- `extractor_used` records which method produced the output
- `fallbacks_tried` records what was attempted
- `content_path` points to the actual file
- Cross-validation results link to the validation assets used

Vera can trace any downstream claim through: content → extraction-report → source manifest → original file.
