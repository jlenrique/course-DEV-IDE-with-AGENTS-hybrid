# Capabilities

## Built-In
- Evaluate G0 Texas extraction output with a six-dimension evidence-sentence rubric.
- Evaluate G1 ingestion quality with six verdict dimensions.
- Evaluate G3 Storyboard A fidelity with image, audio, and motion perception dispatch.
- Evaluate G4 narration script fidelity against the 19 canonical criteria in `state/config/fidelity-contracts/g4-narration-script.yaml`.
- Emit Fidelity Trace Reports under run-scoped `fidelity/` directories.
- Activate HALT-AND-REMEDIATE on critical O/I/A findings.

## Boundaries
- Read source-of-truth and under-assessment artifacts.
- Write only run-scoped trace reports, specialist summaries, and Vera's own sanctum when explicitly in scope.
- Do not mutate the artifacts being assessed.
